"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


import re
import unicodedata

from .contracts import validate_document
from .task4_chunking_indexing import get_collection


# Optional explicit corpus for offline tests. None reads the live Task 5 collection.
CORPUS: list[dict] | None = None


def _tokenize(text: str) -> list[str]:
    """Normalize Unicode/case while retaining accents and complete document codes."""
    text = unicodedata.normalize("NFC", text).casefold()
    return re.findall(r"\w+(?:[-/]\w+)*", text)


def _load_corpus() -> list[dict]:
    # Reload on each search so reindexing cannot leave an outdated BM25 cache.
    response = get_collection().get(include=["documents", "metadatas"])
    corpus = []
    for item_id, content, metadata in zip(
        response["ids"], response["documents"], response["metadatas"],
    ):
        metadata = dict(metadata)
        metadata["url"] = metadata.get("url") or None
        corpus.append({"id": item_id, "content": content, "metadata": metadata})
    return corpus


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25L

    for item in corpus:
        validate_document(item, require_chunk=True)
    tokenized = [_tokenize(item["content"]) for item in corpus]
    if not any(tokenized):
        return None
    # BM25L retains positive match scores even for one- or two-chunk corpora.
    return BM25L(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    tokens = _tokenize(query)
    if top_k <= 0 or not tokens:
        return []
    source = _load_corpus() if CORPUS is None else CORPUS
    # Duplicate IDs must not inflate document frequency or appear in the output.
    corpus = list({item["id"]: item for item in source}.values())
    bm25 = build_bm25_index(corpus)
    if bm25 is None:
        return []
    scores = bm25.get_scores(tokens)
    results = [
        {
            "id": item["id"], "content": item["content"],
            "score": float(score), "metadata": dict(item["metadata"]),
            "retrieval_method": "bm25",
        }
        for item, score in zip(corpus, scores) if score > 0
    ]
    return sorted(results, key=lambda item: (-item["score"], item["id"]))[:top_k]


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
