# Báo cáo kết quả RAG

## Phạm vi và bằng chứng

Báo cáo này chỉ ghi nhận các phần đã có trong repository hoặc đã được chạy trong
terminal của project. Báo cáo không tự tạo ra điểm đánh giá chất lượng khi chưa có
lần chạy evaluation tương ứng.

| Hạng mục | Bằng chứng đã có |
| --- | --- |
| Corpus | 3 tài liệu legal/policy và 6 bài news đã được chuẩn hóa thành Markdown trong `data/standardized/` |
| Golden dataset | 15 case trong `group_project/evaluation/golden_dataset.json`; mỗi case có question, expected answer và expected context |
| Dense retrieval | Task 4 index Markdown chuẩn hóa vào Chroma với cosine similarity và `BAAI/bge-m3` |
| Lexical retrieval | Task 6 xây dựng BM25L từ cùng tập chunk trong Chroma |
| Hybrid retrieval | Task 7 gộp kết quả dense và BM25 bằng Reciprocal Rank Fusion (RRF) |
| Pipeline run | `python -m src.task9_retrieval_pipeline` đã chạy thành công và trả về ba SearchResult có method `hybrid` |
| PageIndex fallback | Code tích hợp đã có nhưng chưa cấu hình hay chạy PageIndex API thật |
| Sinh câu trả lời | Task 10 hỗ trợ sinh câu trả lời kèm citation, nhưng chưa có lần chạy LLM nào được ghi nhận |

## Cấu hình retrieval

Luồng retrieval đã hoàn thành gồm dense cosine search và BM25L, sau đó được gộp một
lần bằng RRF. Task 9 dùng cosine score gốc cao nhất của dense search để quyết định có
thử PageIndex fallback hay không; không dùng RRF score cho quyết định này. Cấu hình
mặc định là `top_k=5`, với fallback threshold là `0.3`.

## Lần chạy đã quan sát

Task 9 dùng truy vấn mặc định `test query` và in ra ba kết quả có
`retrieval_method: hybrid`. Kết quả này xác nhận Task 4 index, semantic search, BM25
và RRF có thể chạy cùng nhau trong môi trường local. Điểm RRF được in ra xấp xỉ
`0.016`; đây là điểm gộp theo thứ hạng, không phải cosine similarity score.

Các đoạn được retrieve gồm cả một đoạn phù hợp về IELTS Writing Task 1 và một số đoạn
chứa menu/navigation của website. Đây là hạn chế quan sát được ở dữ liệu news crawl,
không phải kết quả đánh giá chất lượng answer generation.

## Overall scores

Chưa có phép đo faithfulness, answer relevance, context recall, context precision,
latency hoặc cost. Những chỉ số này đòi hỏi phải chạy 15 golden case qua generator và
evaluator, việc đó chưa có bằng chứng đã thực hiện.

| Chỉ số | Giá trị đã ghi nhận | Diễn giải |
| --- | --- | --- |
| Độ đầy đủ của golden dataset | 15/15 case có mặt | Cấu trúc dataset đã hoàn chỉnh |
| Smoke test retrieval pipeline | Đạt | Hybrid retrieval đã trả về kết quả |
| Faithfulness | Chưa đo | Cần answer được sinh và evaluator |
| Answer relevance | Chưa đo | Cần answer được sinh và evaluator |
| Context recall / precision | Chưa đo | Cần đánh giá kết quả retrieval theo từng case |
| Latency / cost | Chưa đo | Cần provider run có đo thời gian và chi phí |

## A/B comparison

Chưa có lần chạy A/B giữa dense-only và hybrid/PageIndex với cùng golden dataset,
generator và evaluator. Vì vậy chưa thể kết luận cấu hình nào tốt hơn. Bằng chứng hiện
có chỉ cho thấy hybrid retrieval đã chạy thành công trong Task 9.

## Worst performers

Chưa có dữ liệu theo từng câu hỏi để xác định các case hoạt động kém nhất. Vấn đề duy
nhất đã quan sát là một số chunk news giữ lại navigation và footer, nên có thể xuất hiện
ở vị trí cao với những truy vấn rộng.

## Recommendations

Các mục sau là việc cần làm tiếp được rút ra từ bằng chứng hiện có, không phải công
việc mới đã hoàn thành:

1. Lọc menu, footer và nội dung lặp trong news trước khi chạy lại standardization và index.
2. Chạy 15 golden case cho dense-only và hybrid, lưu kết quả từng case trước khi báo cáo metric.
3. Chỉ cấu hình PageIndex khi có PageIndex API key và endpoint hợp lệ; nếu không, giữ graceful fallback sang hybrid.
4. Cấu hình một LLM provider và chạy Task 10 trước khi đánh giá faithfulness hoặc citation quality.

## Cách tái lập

Chạy smoke test retrieval:

```powershell
python -m src.task9_retrieval_pipeline
```

Chạy acceptance tests:

```powershell
pytest -q
```
