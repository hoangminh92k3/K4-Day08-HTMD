# RAG evaluation results

> Status: completed. Per-case evidence is stored in `group_project/evaluation/latest_run.json` and can be regenerated with `python -m group_project.evaluation.run_evaluation`.

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-26 (Asia/Bangkok); evaluator retry completed at 2026-09-25T17:33:19Z |
| Corpus | 3 legal PDFs and 6 IELTS Writing articles standardized to Markdown (599 indexed chunks) |
| Golden dataset | 15 cases: 14 grounded questions and 1 out-of-domain safe-refusal case |
| Generator / evaluator | Groq `openai/gpt-oss-20b`; the same model, system prompt, `temperature=0.3`, and `top_p=0.9` for both A and B |
| Embedding | `BAAI/bge-m3`, normalized cosine similarity in ChromaDB |
| Retrieval | `top_k=5`; Config A dense only; Config B dense + BM25L + RRF (`k=60`) |
| Fallback / calibration | Dense threshold `0.30`; smoke check: in-domain score `0.6753`, visa out-of-domain score `0.4859`. Both exceed the threshold, so PageIndex did not trigger; it was also not configured. Threshold calibration remains a known limitation. |

Metric definitions: faithfulness and answer relevance are binary Groq LLM-as-judge scores over all 15 cases. Context recall is expected-source hit@5; context precision is relevant retrieved chunks / retrieved chunks. The two context metrics exclude the single out-of-domain case because it has no relevant corpus document.

The Groq development tier limits this model to 8,000 TPM. The runner therefore evaluates five isolated cases per request; this preserves each case's own context while keeping each request below the provider limit.

## Configurations

- **Config A — dense-only:** BGE cosine retrieval only.
- **Config B — hybrid + RRF:** the same dense results plus BM25L, fused once by RRF with `k=60`.

Only the retrieval strategy changes between configurations.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.933 | 0.933 | +0.000 |
| Answer relevance | 1.000 | 0.933 | -0.067 |
| Context recall | 0.929 | 1.000 | +0.071 |
| Context precision | 0.471 | 0.400 | -0.071 |
| **Average** | **0.833** | **0.817** | **-0.017** |

## A/B comparison

- **Cấu hình tốt hơn theo average:** Config A (dense-only), 0.833 so với 0.817.
- **Evidence:** Hybrid tìm được expected source cho đủ 14/14 câu grounded, trong khi dense bỏ sót case 13. Tuy vậy, RRF đưa thêm chunk không liên quan vào top-5 (precision giảm 0.071) và case 11 bị judge đánh giá không faithful/relevant, khiến average giảm 0.017.
- **Latency/cost:** Không kết luận latency từ run này. Groq rate-limit đã làm wall-clock time phụ thuộc vào thời điểm batch và retry; hai config dùng cùng model, prompt, `top_k`, số case và cùng số lượt batch LLM nên chi phí model dự kiến tương đương.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | Khi đọc đề Task 2, cần kiểm tra điều gì để tránh bỏ sót yêu cầu? | Hybrid + RRF | 0 | 0 | 1.000 | 0.200 | generation | Expected source có mặt ở rank 3, nhưng answer không kèm citation và không nêu đầy đủ checklist theo golden answer. |
| 2 | Khi đọc đề Task 2, cần kiểm tra điều gì để tránh bỏ sót yêu cầu? | Dense-only | 0 | 1 | 1.000 | 0.400 | generation | Answer trả lời đúng hướng nhưng citation trỏ tới chunk không chứng minh đầy đủ các ý cần kiểm tra. |
| 3 | Trong opinion essay, thí sinh cần thể hiện điều gì? | Dense-only | 1 | 1 | 0.000 | 0.000 | retrieval / dataset | Dense chỉ trả các chunk `article_06`; answer vẫn được judge chấp nhận, cho thấy golden expected source `article_02` quá đặc hiệu hoặc corpus bị chồng chéo nội dung. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Validate `[Document N]` citations and re-prompt/refuse when a response has none. | Hybrid case 11 had the expected source but generated no citation and failed both answer metrics. | Raise faithfulness and traceability. | Re-run case 11; every claim must map to a returned source. |
| 2 | Tune RRF input depth or deduplicate chunks from the same document before fusion. | Hybrid recall reached 1.000 but precision fell from 0.471 to 0.400. | Retain recall while reducing distractor chunks. | Compare precision@5 and answer metrics on the same golden set. |
| 3 | Review golden case 13 and record every acceptable supporting source. | `article_06` supported a faithful answer although the golden entry required `article_02`. | Make retrieval metrics reflect valid corpus evidence rather than one arbitrarily chosen document. | Have a reviewer approve allowed-source IDs, then re-run A/B. |

## Bonus experiments

No bonus experiment was run. The next candidate is document-level deduplication before RRF; it should be claimed only if a second A/B run improves the metrics above.
