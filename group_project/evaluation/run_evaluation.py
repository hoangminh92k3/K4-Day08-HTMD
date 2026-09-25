"""Reproducible A/B evaluation for the IELTS Writing RAG pipeline.

Run with ``python -m group_project.evaluation.run_evaluation`` after indexing
the corpus and configuring the selected LLM provider in ``.env``.  The runner
uses the exact same generator/evaluator model for both configurations and
writes per-case evidence to ``latest_run.json``.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from src.task10_generation import (
    SYSTEM_PROMPT,
    call_llm,
    format_context,
    reorder_for_llm,
)
from src.task5_semantic_search import semantic_search
from src.task9_retrieval_pipeline import retrieve


HERE = Path(__file__).resolve().parent
DATASET = HERE / "golden_dataset.json"
OUTPUT = HERE / "latest_run.json"
TOP_K = 5
REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def dense_only(query: str) -> list[dict]:
    return semantic_search(query, top_k=TOP_K)


def hybrid_rrf(query: str) -> list[dict]:
    return retrieve(query, top_k=TOP_K)


def batch_call_llm(system_prompt: str, user_message: str) -> str:
    """Allow enough completion tokens for 15 JSON answers or judgements."""
    if os.getenv("LLM_PROVIDER", "").casefold().strip() == "groq":
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1",
            timeout=60.0,
            max_retries=1,
        )
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", ""),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            top_p=0.9,
            max_tokens=2048,
        )
        return response.choices[0].message.content or ""
    return call_llm(system_prompt, user_message)


def _json_response(raw: str) -> dict:
    """Parse a JSON-only model answer, tolerating an accidental code fence."""
    cleaned = raw.strip().removeprefix("```json").removeprefix("```")
    return json.loads(cleaned.removesuffix("```").strip())


def batch_answers(pending: list[tuple]) -> dict[int, str]:
    """Generate all answers in one isolated, labelled request.

    Batching makes the run reliable on a rate-limited development API.  Each
    question retains its own context; the generator is explicitly prohibited
    from using any other item's context.
    """
    items = []
    for index, case, chunks, _ in pending:
        context = format_context(reorder_for_llm(chunks)) if chunks else "(none)"
        items.append(f"CASE {index}\nContext:\n{context}\nQuestion: {case['question']}")
    prompt = """Answer every labelled case below using only that case's Context.
Every factual claim needs a [Document N] citation from the same case. If the
context cannot verify the answer, use a clear refusal. Return JSON only:
{"answers":[{"case":1,"answer":"..."}]}.

    """ + "\n\n---\n\n".join(items)
    try:
        raw = batch_call_llm(SYSTEM_PROMPT, prompt)
        payload = _json_response(raw)
        parsed = {int(item["case"]): str(item["answer"]).strip()
                  for item in payload["answers"]}
        return {index: parsed.get(index, REFUSAL) or REFUSAL for index, *_ in pending}
    except Exception as exc:
        print(f"Batch-answer parse failed: {type(exc).__name__}: {exc}")
        print(f"Batch-answer response prefix: {locals().get('raw', '')[:500]!r}")
        return {index: REFUSAL for index, *_ in pending}


def batch_judgements(pending: list[tuple], answers: dict[int, str]) -> dict[int, dict[str, int]]:
    """Score every case in one strict JSON-only LLM-as-judge request."""
    items = []
    for index, case, chunks, _ in pending:
        context = format_context(reorder_for_llm(chunks)) if chunks else "(none)"
        items.append(
            f"CASE {index}\nQuestion: {case['question']}\nExpected answer: {case['expected_answer']}\n"
            f"Expected context: {case['expected_context']}\nRetrieved context:\n{context}\n"
            f"Generated answer: {answers[index]}"
        )
    prompt = """Evaluate each labelled RAG answer below. Return JSON only:
{"judgements":[{"case":1,"faithfulness":0,"answer_relevance":0}]}.
Faithfulness is 1 only if all factual claims are supported by the retrieved
context. Answer relevance is 1 only if the answer directly responds. For an
out_of_domain expected context, a clear refusal is both faithful and relevant.

""" + "\n\n---\n\n".join(items)
    fallback = {index: {"faithfulness": 0, "answer_relevance": 0} for index, *_ in pending}
    try:
        raw = batch_call_llm("You are a strict RAG evaluator.", prompt)
        payload = _json_response(raw)
        for item in payload["judgements"]:
            index = int(item["case"])
            if index in fallback:
                fallback[index] = {
                    "faithfulness": int(item["faithfulness"]),
                    "answer_relevance": int(item["answer_relevance"]),
                }
    except Exception as exc:
        print(f"Batch-judge parse failed: {type(exc).__name__}: {exc}")
        print(f"Batch-judge response prefix: {locals().get('raw', '')[:500]!r}")
    return fallback


def retrieval_metrics(case: dict, chunks: list[dict]) -> dict[str, float | None]:
    """Source-level metrics; out-of-domain has no relevant corpus document."""
    expected = case["expected_context"]
    if expected == "out_of_domain":
        return {"context_recall": None, "context_precision": None}
    relevant = [chunk for chunk in chunks if chunk["metadata"]["source"] == expected]
    return {
        "context_recall": float(bool(relevant)),
        "context_precision": len(relevant) / len(chunks) if chunks else 0.0,
    }


def summarize(runs: list[dict]) -> dict[str, float]:
    grounded = [run for run in runs if run["expected_context"] != "out_of_domain"]
    summary = {
        "faithfulness": sum(run["faithfulness"] for run in runs) / len(runs),
        "answer_relevance": sum(run["answer_relevance"] for run in runs) / len(runs),
        "context_recall": sum(run["context_recall"] for run in grounded) / len(grounded),
        "context_precision": sum(run["context_precision"] for run in grounded) / len(grounded),
        "mean_latency_ms": sum(run["latency_ms"] for run in runs) / len(runs),
    }
    summary["average"] = sum(
        summary[key]
        for key in ("faithfulness", "answer_relevance", "context_recall", "context_precision")
    ) / 4
    return summary


def evaluate_configuration(name: str, search, cases: list[dict]) -> dict:
    # Retrieval is local.  The two batched model calls keep a rate-limited
    # evaluation reproducible while preserving an isolated context per case.
    pending = []
    for index, case in enumerate(cases, 1):
        started = time.perf_counter()
        chunks = search(case["question"])
        pending.append((index, case, chunks, started))

    # Five cases keep input + reserved output below Groq's 8,000 TPM limit.
    groups = [pending[start:start + 5] for start in range(0, len(pending), 5)]
    generated = {}
    for group in groups:
        generated.update(batch_answers(group))
    judgements = {}
    for group in groups:
        judgements.update(batch_judgements(group, generated))

    runs = []
    for index, case, chunks, started in pending:
        runs.append({
            "case": index,
            **case,
            "answer": generated[index],
            "sources": [chunk["metadata"]["source"] for chunk in chunks],
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            **judgements[index],
            **retrieval_metrics(case, chunks),
        })

    return {"name": name, "summary": summarize(runs), "cases": runs}


def retry_zero_judgements() -> None:
    """Re-judge only 0/0 cases left by a transient Groq rate limit."""
    result = json.loads(OUTPUT.read_text(encoding="utf-8"))
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    searchers = {"dense-only": dense_only, "hybrid-rrf": hybrid_rrf}
    for config in result["configurations"]:
        targets = [row for row in config["cases"]
                   if row["faithfulness"] == 0 and row["answer_relevance"] == 0]
        if not targets:
            continue
        pending = []
        for row in targets:
            case = cases[row["case"] - 1]
            pending.append((row["case"], case, searchers[config["name"]](case["question"]), time.perf_counter()))
        answers = {row["case"]: row["answer"] for row in targets}
        verdicts = batch_judgements(pending, answers)
        for row in targets:
            row.update(verdicts[row["case"]])
        config["summary"] = summarize(config["cases"])
    result["judgements_retried_at_utc"] = datetime.now(UTC).isoformat()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for config in result["configurations"]:
        print(config["name"], json.dumps(config["summary"], ensure_ascii=False))


def main() -> None:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    result = {
        "run_at_utc": datetime.now(UTC).isoformat(),
        "top_k": TOP_K,
        "metric_notes": {
            "faithfulness_and_answer_relevance": "Binary Groq LLM-as-judge over all 15 cases.",
            "context_recall": "Expected-source hit@5 over 14 grounded cases.",
            "context_precision": "Relevant retrieved chunks / retrieved chunks over 14 grounded cases.",
        },
        "configurations": [
            evaluate_configuration("dense-only", dense_only, cases),
            evaluate_configuration("hybrid-rrf", hybrid_rrf, cases),
        ],
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for config in result["configurations"]:
        print(config["name"], json.dumps(config["summary"], ensure_ascii=False))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    retry_zero_judgements() if "--retry-zero-judgements" in sys.argv else main()
