from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.synthesis import synthesize_topic
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SynthesisRequest(BaseModel):
    query: str = Field(..., example="How does RAG improve LLM factual accuracy?")
    top_k: int = Field(default=8, ge=1, le=30)
    collection: str = Field(default="papers")


class SourceRef(BaseModel):
    rank: int
    title: str | None
    url: str | None
    source: str | None
    score: float


class SynthesisResponse(BaseModel):
    query: str
    synthesis: str
    sources: list[SourceRef]


@router.post("/", response_model=SynthesisResponse)
async def synthesize(req: SynthesisRequest):
    result = await synthesize_topic(query=req.query, collection=req.collection, top_k=req.top_k)
    if not result.get("sources"):
        raise HTTPException(status_code=404, detail="No relevant documents found. Try ingesting first.")
    return SynthesisResponse(
        query=result["query"],
        synthesis=result["synthesis"],
        sources=[SourceRef(**s) for s in result["sources"]],
    )
