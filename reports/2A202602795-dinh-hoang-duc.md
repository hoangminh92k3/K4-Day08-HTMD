# Individual contribution report

## Thông tin

- Họ và tên: Đinh Hoàng Đức
- Mã học viên: 2A202602795
- Nhóm: K4-Day08-HTMD
- Repository/branch: repository nhóm, commit nền `95c44b2` (Lab08)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
| --- | --- | --- | --- |
| Generation & chatbot | Tích hợp UI Streamlit với RAG pipeline, lưu lịch sử hội thoại và hiển thị nguồn, retrieval method, score. | `app.py`; working tree sau `95c44b2` | Done |
| Groq integration | Bổ sung Groq theo OpenAI-compatible API, cấu hình mẫu không lộ secret và ép citation `[Document N]`. | `src/task10_generation.py`, `.env.example`; working tree sau `95c44b2` | Done |
| Evaluation artefacts | Tạo golden dataset 15 case (có query ngoài domain), report đúng vị trí và chuẩn bị A/B dense-only/hybrid. | `group_project/evaluation/`; working tree sau `95c44b2` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng Groq qua OpenAI SDK với base URL riêng.
   **Lý do/evidence:** Giữ cùng interface chat-completions đang dùng cho OpenAI, chỉ thêm một provider và không làm thay đổi contract generation.
   **Trade-off:** Phụ thuộc model/provider bên ngoài; khi lỗi, pipeline trả safe refusal thay vì suy đoán.

2. **Quyết định:** Giữ dense cosine làm điều kiện fallback và RRF chỉ để fusion.
   **Lý do/evidence:** Đây là invariant trong `docs/MODULE_CONTRACTS.md` và được contract test kiểm tra.
   **Trade-off:** Cần hiệu chỉnh threshold bằng benchmark A/B thay vì suy ra từ RRF score.

## Kiểm thử và kết quả

- Test hoặc query đã dùng: contract tests, acceptance tests, 15 câu golden dataset và một query ngoài domain.
- Kết quả trước/sau: UI placeholder đã được thay bằng `generate_with_citation`; golden dataset từ 0 lên 15 cases hợp lệ.
- Lỗi đã phát hiện và cách xử lý: cấu hình ban đầu chưa hỗ trợ Groq; đã bổ sung adapter OpenAI-compatible và `.env.example`.

## Điều còn hạn chế

- Một hạn chế cụ thể: kết quả A/B cần chạy lại khi corpus, embedding model hoặc LLM model thay đổi.
- Nếu có thêm thời gian: bổ sung evaluator độc lập và lưu raw output từng case để audit metric.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Đinh Hoàng Đức
