from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from services.qdrant_service import search_similar
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

COLLECTION = "papers"


class SearchResult(BaseModel):
    rank: int
    score: float
    title: str | None
    url: str | None
    source: str | None
    abstract: str | None
    published: str | None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Semantic search query"),
    top_k: int = Query(default=10, ge=1, le=50),
    source: str | None = Query(default=None, description="Filter by source: arxiv or github"),
):
    hits = search_similar(collection=COLLECTION, query_text=q, top_k=top_k, source_filter=source)

    results = [
        SearchResult(
            rank=i + 1,
            score=round(hit.score, 4),
            title=hit.payload.get("title"),
            url=hit.payload.get("url"),
            source=hit.payload.get("source"),
            abstract=(hit.payload.get("abstract") or "")[:300],
            published=hit.payload.get("published"),
        )
        for i, hit in enumerate(hits)
    ]

    return SearchResponse(query=q, total=len(results), results=results)
