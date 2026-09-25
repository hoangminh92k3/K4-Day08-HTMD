# Báo cáo kết quả RAG

## Thông tin thực hiện

| Hạng mục | Nội dung đã có bằng chứng |
| --- | --- |
| Ngày ghi nhận | 25/09/2026 |
| Phạm vi báo cáo | Chỉ ghi nhận các task đã triển khai và lần chạy Task 9; chưa thực hiện đánh giá chất lượng bằng LLM/evaluator |
| Embedding model | `BAAI/bge-m3` |
| Corpus | 3 tài liệu legal/policy và 6 bài news đã được chuẩn hóa thành Markdown trong `data/standardized/` |
| Golden dataset | 15 case có `question`, `expected_answer`, `expected_context` |
| `top_k` mặc định | 5 trong Task 9 |
| Fallback threshold | 0.3, so sánh với cosine score gốc của dense retrieval |
| PageIndex | Đã có code fallback; chưa cấu hình API key/endpoint và chưa chạy provider thật |
| Sinh câu trả lời | Task 10 đã có code hỗ trợ OpenAI, Gemini và Anthropic; chưa có lần chạy LLM được ghi nhận |

## Các cấu hình retrieval

- **Cấu hình A — dense-only:** Task 5 truy vấn Chroma bằng cosine similarity, dùng cùng `BAAI/bge-m3` với Task 4.
- **Cấu hình B — hybrid + RRF:** Task 6 chạy BM25L trên cùng tập chunk; Task 7 gộp dense và BM25 bằng Reciprocal Rank Fusion.

Task 9 đã chạy Cấu hình B với truy vấn mẫu `test query` và trả về ba kết quả có `retrieval_method: hybrid`.

## Overall scores

Chưa có điểm faithfulness, answer relevance, context recall, context precision,
latency hay cost vì chưa chạy golden dataset qua generator và evaluator. Không đưa ra
điểm số ước đoán khi chưa có dữ liệu đo đạc.

| Chỉ số | Cấu hình A | Cấu hình B | Chênh lệch |
| --- | --- | --- | --- |
| Golden dataset hợp lệ | 15 case đã có | 15 case đã có | Không áp dụng |
| Smoke test retrieval | Chưa chạy riêng | Đã chạy thành công qua Task 9 | Không áp dụng |
| Faithfulness | Chưa đo | Chưa đo | Chưa đo |
| Answer relevance | Chưa đo | Chưa đo | Chưa đo |
| Context recall | Chưa đo | Chưa đo | Chưa đo |
| Context precision | Chưa đo | Chưa đo | Chưa đo |

## A/B comparison

- **Cấu hình tốt hơn:** Chưa thể kết luận, vì chưa có chạy A/B với cùng golden dataset, generator và evaluator.
- **Bằng chứng hiện có:** Cấu hình hybrid đã chạy end-to-end trong Task 9; RRF gộp dense và BM25 đúng một lần.
- **Latency/cost:** Chưa đo. PageIndex và LLM provider chưa được gọi trong lần chạy đã ghi nhận.

## Worst performers

Chưa có dữ liệu per-question để xếp hạng câu hỏi hoạt động kém. Quan sát duy nhất từ
lần chạy Task 9 là một số chunk news vẫn chứa menu, navigation và footer của trang web;
những đoạn này có thể xuất hiện trong kết quả của truy vấn rộng.

| Hạng mục quan sát | Giai đoạn | Nguyên nhân ghi nhận |
| --- | --- | --- |
| Chunk news chứa navigation/footer | Dữ liệu/retrieval | Nội dung crawl còn boilerplate web, chưa được lọc hoàn toàn khi chuẩn hóa |

## Recommendations

| Ưu tiên | Việc cần làm tiếp | Bằng chứng hiện có | Cách xác minh |
| ---: | --- | --- | --- |
| 1 | Lọc menu, footer và link lặp trong news trước khi re-index | Task 9 trả về một số chunk navigation-heavy | Chạy lại Task 4 và kiểm tra kết quả Task 9 |
| 2 | Chạy 15 golden case cho dense-only và hybrid | Dataset đã đủ cấu trúc nhưng chưa có metric | Lưu kết quả từng case và tính các metric |
| 3 | Cấu hình một LLM provider trước khi đánh giá câu trả lời/citation | Task 10 đã hỗ trợ provider nhưng chưa có lần chạy được ghi nhận | Chạy Task 10 với query trong golden dataset |

## Bonus experiments

Chưa có thử nghiệm bổ sung được chạy. Khi có PageIndex API key/endpoint hợp lệ, có thể
so sánh hybrid với PageIndex fallback trên cùng 15 golden case và ghi lại metric,
latency cùng các lỗi theo từng câu hỏi.
