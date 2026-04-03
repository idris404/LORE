import os
import httpx
from datetime import date, datetime

NOTION_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

PAPERS_DB = os.getenv("NOTION_PAPERS_DB", "")
SYNTHESES_DB = os.getenv("NOTION_SYNTHESES_DB", "")
TRENDS_DB = os.getenv("NOTION_TRENDS_DB", "")


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.getenv('NOTION_TOKEN', '')}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _rich_text_blocks(text: str, max_per_block: int = 2000) -> list[dict]:
    """Split long text into multiple rich_text objects (Notion limit: 2000 chars each)."""
    chunks = [text[i:i + max_per_block] for i in range(0, len(text), max_per_block)]
    return [{"type": "text", "text": {"content": chunk}} for chunk in chunks]


async def create_paper(payload: dict) -> dict:
    """Create a page in NOTION_PAPERS_DB for a single paper/repo."""
    title = (payload.get("title") or "Untitled")[:200]
    abstract = (payload.get("abstract") or "")[:2000]
    url = payload.get("url") or ""
    source = payload.get("source") or "unknown"
    score = payload.get("score")

    # Categories: list for arxiv papers, None/missing for github repos
    raw_categories = payload.get("categories") or []
    categories_str = ", ".join(raw_categories) if raw_categories else ""

    # Published: already an ISO 8601 string from arxiv ("2026-03-28T00:00:00+00:00")
    # Notion date expects "YYYY-MM-DD" for date-only fields
    published_raw = payload.get("published") or ""
    published_date = published_raw[:10] if published_raw else ""  # trim to YYYY-MM-DD

    properties: dict = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Abstract": {"rich_text": [{"text": {"content": abstract}}]},
        "Source": {"select": {"name": source}},
    }
    if url:
        properties["URL"] = {"url": url}
    if score is not None:
        properties["Score"] = {"number": round(float(score), 4)}
    if categories_str:
        properties["Categories"] = {"rich_text": [{"text": {"content": categories_str}}]}
    if published_date:
        properties["Published"] = {"date": {"start": published_date}}

    body = {
        "parent": {"database_id": PAPERS_DB},
        "properties": properties,
    }
    async with httpx.AsyncClient(headers=_headers(), timeout=20) as client:
        r = await client.post(f"{NOTION_BASE}/pages", json=body)
        r.raise_for_status()
        return r.json()


async def create_synthese(data: dict) -> dict:
    """Create a synthesis page in NOTION_SYNTHESES_DB."""
    today = date.today()
    week = today.isocalendar()
    title = f"Synthèse Semaine {week.year}-W{week.week:02d}"

    summary = data.get("synthesis") or data.get("summary") or ""
    # Extract themes from synthesis text (first 5 words of bullet points) or from data
    raw_themes = data.get("themes") or []
    if not raw_themes and "synthesis" in data:
        # Auto-extract: look for **Bold** patterns as theme titles
        import re
        raw_themes = re.findall(r"\*\*([^*]{3,40})\*\*", data["synthesis"])[:5]

    theme_options = [{"name": t[:100]} for t in raw_themes if t.strip()]

    properties: dict = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Date": {"date": {"start": today.isoformat()}},
        "Summary": {"rich_text": _rich_text_blocks(summary[:2000])},
    }
    if theme_options:
        properties["Themes"] = {"multi_select": theme_options}

    body = {
        "parent": {"database_id": SYNTHESES_DB},
        "properties": properties,
    }
    async with httpx.AsyncClient(headers=_headers(), timeout=20) as client:
        r = await client.post(f"{NOTION_BASE}/pages", json=body)
        r.raise_for_status()
        return r.json()


async def create_tendance(trend: dict) -> dict:
    """Create a trend page in NOTION_TRENDS_DB."""
    concept = str(trend.get("concept") or trend.get("keyword") or "unknown")[:200]
    count = trend.get("count") or 0
    growth_score = trend.get("growth_score") or trend.get("score") or 0.0

    properties: dict = {
        "Concept": {"title": [{"text": {"content": concept}}]},
        "Count": {"number": int(count)},
        "GrowthScore": {"number": round(float(growth_score), 4)},
    }
    body = {
        "parent": {"database_id": TRENDS_DB},
        "properties": properties,
    }
    async with httpx.AsyncClient(headers=_headers(), timeout=20) as client:
        r = await client.post(f"{NOTION_BASE}/pages", json=body)
        r.raise_for_status()
        return r.json()
