from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.arxiv_client import fetch_papers_async
from services.github_client import search_repos
from services.embeddings import embed_text
from services.qdrant_service import init_collection, upsert_point
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

COLLECTION = "papers"


class IngestRequest(BaseModel):
    keywords: list[str] = Field(..., min_length=1, example=["agentic AI", "multi-agent systems"])
    sources: list[str] = Field(default=["arxiv", "github"])
    max_results: int = Field(default=10, ge=1, le=50)
    # arxiv options
    arxiv_categories: list[str] | None = Field(default=None, example=["cs.AI", "cs.LG"])
    days: int | None = Field(default=None, ge=1, le=365, description="Only papers/repos from last N days")


class IngestResponse(BaseModel):
    ingested: int
    collection: str
    sources_breakdown: dict[str, int]
    ids: list[str]


async def _ingest_items(items: list[dict], collection: str) -> list[str]:
    ids = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('abstract', '')}"
        vector = embed_text(text)
        uid = upsert_point(collection=collection, payload=item, vector=vector)
        ids.append(uid)
        logger.info(f"Ingested: {item.get('title', '')[:70]} [{item.get('source')}]")
    return ids


@router.post("/", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    collection = init_collection(COLLECTION)
    all_items: list[dict] = []
    breakdown: dict[str, int] = {}

    if "arxiv" in req.sources:
        papers = await fetch_papers_async(
            keywords=req.keywords,
            max_results=req.max_results,
            categories=req.arxiv_categories,
            days=req.days,
        )
        all_items.extend(papers)
        breakdown["arxiv"] = len(papers)
        logger.info(f"Fetched {len(papers)} papers from arxiv")

    if "github" in req.sources:
        repos = await search_repos(req.keywords, req.max_results)
        all_items.extend(repos)
        breakdown["github"] = len(repos)
        logger.info(f"Fetched {len(repos)} repos from github")

    if not all_items:
        raise HTTPException(status_code=404, detail="No results found for the given keywords/filters")

    ids = await _ingest_items(all_items, collection)
    return IngestResponse(ingested=len(ids), collection=collection, sources_breakdown=breakdown, ids=ids)


@router.post("/single")
async def ingest_single(item: dict):
    """Ingest a single arbitrary document."""
    collection = init_collection(COLLECTION)
    text = f"{item.get('title', '')} {item.get('abstract', item.get('content', ''))}"
    vector = embed_text(text)
    uid = upsert_point(collection=collection, payload=item, vector=vector)
    return {"id": uid, "collection": collection}
