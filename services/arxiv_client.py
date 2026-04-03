import arxiv
import asyncio
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from utils.retry import retry_async

ARXIV_MAX_RESULTS = 10

arxiv_client = arxiv.Client(page_size=50, delay_seconds=5, num_retries=5)

# Inject User-Agent so arxiv doesn't throttle anonymous bots
_opener = urllib.request.build_opener()
_opener.addheaders = [("User-Agent", "AI-Research-Agent/1.0 (research tool; contact: research@example.com)")]
urllib.request.install_opener(_opener)


def _build_query(keywords: list[str], categories: list[str] | None = None) -> str:
    kw_part = " OR ".join(f'"{k}"' for k in keywords)
    if categories:
        cat_part = " OR ".join(f"cat:{c}" for c in categories)
        return f"({cat_part}) AND ({kw_part})"
    return kw_part


def fetch_papers(
    keywords: list[str],
    max_results: int = ARXIV_MAX_RESULTS,
    categories: list[str] | None = None,
    days: int | None = None,
) -> list[dict]:
    time.sleep(5)  # polite delay before every call to avoid 429
    query = _build_query(keywords, categories)
    fetch_n = min(max_results * 2 if days else max_results, 50)
    search = arxiv.Search(
        query=query,
        max_results=fetch_n,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days else None
    results = []
    for paper in arxiv_client.results(search):
        if cutoff and paper.published and paper.published < cutoff:
            continue
        results.append({
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "abstract": paper.summary,
            "url": paper.entry_id,
            "pdf_url": paper.pdf_url,
            "published": paper.published.isoformat() if paper.published else None,
            "categories": paper.categories,
            "source": "arxiv",
        })
        if len(results) >= max_results:
            break
    return results


@retry_async(max_attempts=2, delay=30.0)
async def fetch_papers_async(
    keywords: list[str],
    max_results: int = ARXIV_MAX_RESULTS,
    categories: list[str] | None = None,
    days: int | None = None,
) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: fetch_papers(keywords, max_results, categories, days))
