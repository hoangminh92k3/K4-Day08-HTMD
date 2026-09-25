# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Văn Tứ
- Mã học viên: 2A202602586
- Nhóm: TMD
- Repository/branch: K4-L3B-RAG-Pipeline / tu
- Phạm vi phụ trách: Task 4, 5, 6 — chunking, indexing, semantic search và lexical search.

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 | Đọc Markdown đệ quy; giữ metadata; chia chunks; tạo ID ổn định; embedding theo batch; upsert vào ChromaDB cosine. | [task4_chunking_indexing.py](../src/task4_chunking_indexing.py) | Done phần mã và kiểm thử offline; Blocked chạy model thật |
| Task 5 | Dùng chung `embed_texts()` và collection với Task 4; đổi distance thành `score = 1 - distance`; loại ID trùng, sort giảm dần và giới hạn `top_k`. | [task5_semantic_search.py](../src/task5_semantic_search.py) | Done phần mã và kiểm thử offline; chưa đánh giá chất lượng embedding thật |
| Task 6 | Đọc cùng chunks từ ChromaDB; chuẩn hóa Unicode và chữ hoa/thường; giữ dấu, mã tài liệu; tính BM25L và trả `SearchResult` với `retrieval_method="bm25"`. | [task6_lexical_search.py](../src/task6_lexical_search.py) | Done phần mã và kiểm thử |
| Kiểm thử | Kiểm tra contract, index lặp, metadata, tìm kiếm theo mã và cập nhật corpus. | [test_task4_indexing.py](../tests/test_task4_indexing.py), [test_task6_lexical_search.py](../tests/test_task6_lexical_search.py), [test_contracts.py](../tests/test_contracts.py) | 13 test liên quan đạt |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Chia recursive với `CHUNK_SIZE=500` ký tự, `CHUNK_OVERLAP=50`; ID dạng `<đường dẫn tương đối>::chunk-<index>` và lưu bằng upsert.
   **Lý do/evidence:** Ưu tiên ngắt theo đoạn, dòng và từ; overlap giữ một phần ngữ cảnh tại ranh giới. Test xác nhận chạy lại cùng dữ liệu không tăng số bản ghi.
   **Trade-off:** Đây là cấu hình ban đầu, chưa tối ưu bằng evaluation; đoạn dài có thể bị tách. Khi tài liệu bị rút ngắn hoặc xóa, cần bổ sung dọn chunks cũ.

2. **Quyết định:** Task 4–5 dùng một encoder `BAAI/bge-m3`, 1024 chiều, batch embedding 32, Chroma cosine; Task 6 dùng BM25L trên chính corpus đã lưu.
   **Lý do/evidence:** Hàm embedding chung giữ query và document trong cùng không gian vector. BM25L cho điểm khớp dương cả với corpus nhỏ; test kiểm tra mã `123/2024/QĐ-BGDĐT` và tên riêng tiếng Việt.
   **Trade-off:** Model cần tải dependency và trọng số; Task 6 đọc lại corpus, dựng lại BM25 mỗi lần tìm kiếm để tránh dữ liệu cũ nhưng sẽ tốn thời gian khi corpus lớn.

## Kiểm thử và kết quả

- **Kết quả ngày 25/09/2026:** Hai file test Task 4/6 cùng bốn contract test về chữ ký hàm, chunking, semantic search và lexical search đạt **13/13**. Kiểm thử không gọi API hay tải model; sử dụng ChromaDB thật trong thư mục tạm và vector giả lập.
- **Dữ liệu hiện tại:** Đọc 9 Markdown (3 legal, 6 news), tạo **600 chunks / 600 ID duy nhất**. Đây là kết quả load/chunk, không phải số vector đã index bằng model thật.
- **Bằng chứng hành vi:** Upsert hai lần giữ nguyên số bản ghi; bảo toàn metadata; kết quả đúng schema, score giảm dần, không trùng ID và không vượt `top_k`; BM25 nhận nội dung mới sau upsert. Có kiểm tra truy vấn rỗng, không khớp, Unicode và corpus nhỏ.
- **Lỗi và xử lý:** Chroma không nhận metadata `None`, nên URL được lưu bằng chuỗi rỗng và khôi phục thành `None` khi truy vấn. Lệnh chạy Task 4 thật dừng ở `ModuleNotFoundError: sentence_transformers`; đã thử cài dependency nhưng tải PyTorch bị ngắt ở cả nguồn ban đầu và kho CPU chính thức, chưa khắc phục xong.

Lệnh chạy lại đúng nhóm kiểm thử trên, từ thư mục gốc với môi trường `.venv` đã kích hoạt:

```powershell
python -m pytest tests/test_task4_indexing.py tests/test_task6_lexical_search.py tests/test_contracts.py -q -k "not validator and not rrf and not reorder and not retrieve"
```

## Điều còn hạn chế

- Chưa chạy trọn pipeline bằng embedding thật, chưa có số đo chất lượng truy xuất hoặc độ trễ thực tế; kết quả test không thay thế evaluation trên bộ câu hỏi chuẩn.
- Ưu tiên tiếp theo: cài xong `sentence-transformers` khi kết nối ổn định, chạy `python -m src.task4_chunking_indexing`, kiểm tra Task 5/6 trên cùng corpus và đánh giá trước khi điều chỉnh chunk size/overlap.

## Xác nhận đóng góp

Phần việc kê khai giới hạn ở Task 4, 5, 6, được triển khai và kiểm thử với sự hỗ trợ của Codex. Bằng chứng đối chiếu là các file và kiểm thử nêu trên; việc chạy model thật còn bị chặn như đã ghi nhận.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Văn Tứ
