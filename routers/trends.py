from fastapi import APIRouter, Query
from pydantic import BaseModel
from services.trends import compute_trends
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TrendsResponse(BaseModel):
    total: int
    top_keywords: list[list]
    top_categories: list[list]
    sources: dict
    recent_titles: list[dict]


@router.get("/", response_model=TrendsResponse)
async def trends(
    collection: str = Query(default="papers"),
    top_n: int = Query(default=20, ge=5, le=100),
):
    data = compute_trends(collection=collection, top_n=top_n)
    return TrendsResponse(**data)
