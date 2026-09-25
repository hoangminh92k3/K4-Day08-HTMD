# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Quang Huy
- Mã học viên: 2A202602461
- Nhóm: K4-Day08-HTMD
- Repository/branch: Huy

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Generation (LLM Provider) | Bổ sung Cohere SDK vào hệ sinh thái provider để mở rộng LLM chạy generation (tương tự OpenAI/Groq). Cấu hình API fallback. | `src/task10_generation.py` | Done |
| Quality Assurance (QA) & Testing | Chạy bộ kiểm thử tự động (`pytest` acceptance/contracts), rà soát lỗi logic trước khi đóng gói sản phẩm. Đảm bảo pipeline End-to-End hoạt động ổn định đạt 100% tests passed. | Logs hệ thống kiểm thử nội bộ | Done |
| Chuẩn bị Kịch bản Demo | Rà soát cấu trúc thư mục, chuẩn bị danh sách các câu hỏi test In-domain và Out-domain để chuẩn bị demo tính năng Fallback của chatbot. | Nhánh `Huy` | Done |

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Tích hợp Cohere API làm LLM provider dự phòng thay vì chỉ dùng OpenAI.
   **Lý do/evidence:** Đa dạng hóa provider để dự phòng trường hợp API key hết hạn hạn mức (Rate limit) hoặc service down.
   **Trade-off:** Cần cài thêm thư viện `cohere` nhưng mang lại tính linh hoạt cao hơn.

2. **Quyết định:** Áp dụng quy trình "Code Freeze" trên nhánh cá nhân.
   **Lý do/evidence:** Để đảm bảo "Toàn bộ test chạy đạt trên bản commit nộp", tôi phụ trách kiểm tra CI/CD (local pytest) sau khi thêm provider, và đảm bảo nó không phá hỏng cấu trúc Abstract của hệ thống.
   **Trade-off:** Phải chạy test liên tục mỗi khi đổi code.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: 
   - `pytest tests/test_acceptance.py -q`
   - `pytest tests/test_contracts.py -q`
- Kết quả trước/sau nếu có: Xác nhận hệ thống đạt 20/20 test cases pass sau khi thêm Cohere integration.
- Lỗi đã phát hiện và cách xử lý: Quản lý nhánh để code không bị conflict với phần Groq Integration của bạn Đức (`duc`).

## Điều cần hạn chế

- Một hạn chế có thể của phần tôi làm: Tích hợp báo cáo hoàn toàn thủ công.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Thiết lập GitHub Actions để tự động chạy `pytest` mỗi khi có người push code.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 26/09/2026
- Tên thành viên: Nguyễn Quang Huy
