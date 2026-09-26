# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Quang Huy
- Mã học viên: 2A202602461
- Nhóm: K4-Day08-HTMD
- Repository/branch: Huy

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Generation (LLM Provider) | Bổ sung Cohere SDK vào hệ sinh thái provider để mở rộng LLM chạy generation (tương tự OpenAI/Groq). | `src/task10_generation.py` | Done |
| User Interface (Chatbot) | Tự xây dựng giao diện Streamlit UI (`app.py`), cho phép người dùng cấu hình top_k và chuyển đổi LLM Provider ngay trên Sidebar. Tích hợp hiển thị Citation. | `app.py` | Done |
| Evaluation artefacts | Bổ sung đánh giá phân tích hiệu năng của cấu hình mới vào báo cáo kết quả chung. | `group_project/evaluation/RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Đưa tuỳ chọn LLM Provider (OpenAI, Gemini, Anthropic, Cohere, Groq) ra ngoài cấu hình giao diện UI Streamlit.
   **Lý do/evidence:** Cho phép người dùng linh hoạt đổi provider mà không cần khởi động lại server hoặc phải sửa file `.env`, tăng tính tiện dụng.
   **Trade-off:** Cần set biến môi trường động `os.environ` trong thời gian chạy thực, dễ bị ghi đè nếu chạy đa luồng.

2. **Quyết định:** Tích hợp Cohere API làm LLM provider dự phòng thay vì chỉ dùng OpenAI.
   **Lý do/evidence:** Đa dạng hóa provider để dự phòng trường hợp API key hết hạn hạn mức hoặc service down. Báo cáo đánh giá đã ghi nhận tính ổn định.
   **Trade-off:** Cần cài thêm thư viện nhưng mang lại tính linh hoạt cao.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: 
   - `pytest tests/test_acceptance.py -q`
   - Test UI Chatbot trực tiếp trên browser bằng tay để kiểm tra chuyển LLM model.
- Kết quả trước/sau nếu có: Cập nhật thành công UI và hoàn thiện báo cáo RESULT.md cho module bonus.
- Lỗi đã phát hiện và cách xử lý: Xử lý thành công việc LLM Provider không nhận config khi đổi trực tiếp trên UI bằng cách gán thẳng vào `os.environ`.

## Điều cần hạn chế

- Một hạn chế có thể của phần tôi làm: UI mới chỉ test cục bộ trên máy tính.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Triển khai ứng dụng Streamlit này lên Streamlit Cloud.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 26/09/2026
- Tên thành viên: Nguyễn Quang Huy
