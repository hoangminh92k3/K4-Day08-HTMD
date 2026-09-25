"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
PAGEINDEX_API_URL = os.getenv("PAGEINDEX_API_URL", "").rstrip("/")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = Path(__file__).parent.parent / "pageindex_doc_ids.json"
REQUEST_TIMEOUT = float(os.getenv("PAGEINDEX_TIMEOUT", "30"))


def _load_cache() -> dict[str, str]:
    if not CACHE_PATH.is_file():
        return {}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY or not PAGEINDEX_API_URL:
        return

    import requests

    cache = _load_cache()
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        source = path.relative_to(STANDARDIZED_DIR).as_posix()
        if source in cache:
            continue
        with path.open("rb") as document:
            response = requests.post(
                f"{PAGEINDEX_API_URL}/documents",
                headers={"Authorization": f"Bearer {PAGEINDEX_API_KEY}"},
                files={"file": (path.name, document, "text/markdown")},
                timeout=REQUEST_TIMEOUT,
            )
        response.raise_for_status()
        payload = response.json()
        document_id = payload.get("document_id") or payload.get("id")
        if not isinstance(document_id, str) or not document_id:
            raise ValueError(f"PageIndex upload response has no document ID for {source}")
        cache[source] = document_id
        _save_cache(cache)


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query.strip() or top_k <= 0 or not PAGEINDEX_API_KEY or not PAGEINDEX_API_URL:
        return []

    import requests

    try:
        upload_documents()
        cache = _load_cache()
        response = requests.post(
            f"{PAGEINDEX_API_URL}/search",
            headers={"Authorization": f"Bearer {PAGEINDEX_API_KEY}"},
            json={"query": query, "document_ids": list(cache.values()), "top_k": top_k},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
    except (OSError, ValueError, requests.RequestException):
        return []

    nodes = payload.get("results", payload.get("nodes", []))
    if not isinstance(nodes, list):
        return []

    results = []
    for rank, node in enumerate(nodes[:top_k], 1):
        if not isinstance(node, dict):
            continue
        content = node.get("content") or node.get("text") or node.get("markdown")
        if not isinstance(content, str) or not content.strip():
            continue
        source = node.get("source") or node.get("document") or "pageindex"
        results.append({
            "id": str(node.get("id") or f"pageindex-{rank}"),
            "content": content,
            "score": float(node.get("score", 1.0 / rank)),
            "metadata": {
                "source": str(source),
                "title": str(node.get("title") or source),
                "doc_type": "legal" if "legal" in str(source).split("/") else "news",
                "url": node.get("url"),
                "chunk_index": int(node.get("chunk_index", rank - 1)),
            },
            "retrieval_method": "pageindex",
        })
    return sorted(results, key=lambda item: item["score"], reverse=True)


if __name__ == "__main__":
    upload_documents()
