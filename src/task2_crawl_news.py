"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from crawl4ai import AsyncWebCrawler


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    # TODO: Thêm ít nhất 5 public URL.
    "https://ielts.org/news-and-insights/ielts-writing-band-descriptors-and-key-assessment-criteria",
    "https://ielts.org/news-and-insights/ielts-writing-task-2-how-to-understand-ielts-question-prompts",
    "https://ielts.org/news-and-insights/how-to-write-a-semi-formal-letter-for-ielts-general-training-writing-task-1",
    "https://ielts.org/news-and-insights/preparing-learners-for-task-1-on-the-ielts-academic-writing-test",
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-ielts-writing-band-descriptors",
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-ielts-writing-task-2-discussion-essay",
]


async def crawl_article(url: str) -> dict:
    """Crawl one public article and return the required JSON fields."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

    if not result.success:
        error_message = getattr(result, "error_message", "unknown crawl error")
        raise RuntimeError(f"Crawl failed for {url}: {error_message}")

    metadata = result.metadata or {}
    title = metadata.get("title") or metadata.get("og:title") or "Unknown"
    content_markdown = result.markdown or ""

    if not content_markdown.strip():
        raise ValueError(f"Crawl returned empty content for {url}")

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": content_markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
