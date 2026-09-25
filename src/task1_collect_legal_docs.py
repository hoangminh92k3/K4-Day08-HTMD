"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Kiểm tra các tài liệu PDF/DOCX đã được tải thủ công."""
    documents = [
        path
        for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".pdf", ".docx"}
    ]

    if len(documents) < 3:
        raise RuntimeError(
            f"Expected at least 3 PDF/DOCX files in {DATA_DIR}, "
            f"found {len(documents)}"
        )

    print(f"Found {len(documents)} legal documents:")
    for document in sorted(documents):
        print(f"- {document.name}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
