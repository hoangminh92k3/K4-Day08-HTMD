# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Quang Huy
- Mã học viên: 2A202602461
- Nhóm: K4-Day08-HTMD
- Repository/branch: Huy

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Quản lý Git & Tích hợp | Phụ trách rà soát nhánh `main` và đối chiếu với nhánh `duc`. Hỗ trợ chuẩn bị kịch bản tích hợp và cấu hình báo cáo cá nhân trước khi nộp. | Nhánh `Huy` | Done |
| Quality Assurance (QA) & Testing | Chạy bộ kiểm thử tự động (`pytest` acceptance/contracts), rà soát lỗi logic trước khi đóng gói sản phẩm. Đảm bảo pipeline End-to-End hoạt động ổn định đạt 100% tests passed. | Logs hệ thống kiểm thử nội bộ | Done |
| Chuẩn bị Kịch bản Demo | Rà soát cấu trúc thư mục, đối chiếu Grading Rubric, chuẩn bị danh sách các câu hỏi test In-domain và Out-domain để chuẩn bị demo tính năng Fallback của chatbot. | Nhánh `Huy` | Done |

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Không merge trực tiếp từ `Huy` sang `main` mà đẩy riêng lên nhánh cá nhân để trưởng nhóm dễ dàng theo dõi và review phần báo cáo cá nhân.
   **Lý do/evidence:** Hạn chế rủi ro xảy ra merge conflict với file `RESULT.md` và `app.py` đang được bạn Đức (`duc`) và trưởng nhóm hoàn thiện trên nhánh chính.
   **Trade-off:** Cần thêm một thao tác Pull Request (PR) cuối cùng từ trưởng nhóm để gộp tất cả file MD vào `main`.

2. **Quyết định:** Áp dụng quy trình "Code Freeze" trên nhánh cá nhân.
   **Lý do/evidence:** Để đảm bảo "Toàn bộ test chạy đạt trên bản commit nộp" (tiêu chí README), tôi phụ trách kiểm tra CI/CD (local pytest) sau khi pull code, và không thay đổi logic Python cốt lõi ở phút chót.
   **Trade-off:** Tập trung hoàn thiện tài liệu thay vì cố gắng thêm feature mới rủi ro cao.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: 
   - `pytest tests/test_acceptance.py -q`
   - `pytest tests/test_contracts.py -q`
- Kết quả trước/sau nếu có: Xác nhận hệ thống đạt 20/20 test cases pass.
- Lỗi đã phát hiện và cách xử lý: Phát hiện conflict tiềm ẩn ở các file báo cáo kết quả, xử lý bằng cách bám sát phân chia nhánh (Branching strategy) theo đúng phân công của nhóm.

## Điều cần hạn chế

- Một hạn chế có thể của phần tôi làm: Tích hợp báo cáo hoàn toàn thủ công.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Thiết lập GitHub Actions để tự động chạy `pytest` mỗi khi có người push code.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 26/09/2026
- Tên thành viên: Nguyễn Quang Huy
