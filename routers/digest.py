import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.arxiv_client import fetch_papers_async
from services.github_client import search_repos
from services.embeddings import embed_text
from services.qdrant_service import init_collection, upsert_point, search_similar
from services.synthesis import synthesize_topic
from services.trends import compute_trends
from services.notion_client import create_paper, create_synthese, create_tendance

logger = logging.getLogger(__name__)
router = APIRouter()

COLLECTION = "papers"
DIGEST_KEYWORDS = ["agentic AI", "multi-agent systems", "LLM tool use", "autonomous agents"]
ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.MA"]


class DigestRequest(BaseModel):
    keywords: list[str] = Field(default=DIGEST_KEYWORDS)
    arxiv_categories: list[str] = Field(default=ARXIV_CATEGORIES)
    days: int = Field(default=7, ge=1, le=30)
    max_results: int = Field(default=50, ge=1, le=50)
    top_papers: int = Field(default=10, description="How many top papers to push to Notion")
    top_trends: int = Field(default=10, description="How many top trends to push to Notion")
    synthesis_query: str = Field(default="latest trends in agentic AI and LLM tool use")
    dry_run: bool = Field(default=False, description="Skip Notion writes, return what would be sent")


class DigestResponse(BaseModel):
    papers_ingested: int
    papers_created: int
    synthese_created: bool
    tendances_created: int
    synthesis_preview: str
    dry_run: bool


async def _ingest_items(items: list[dict], collection: str) -> list[str]:
    ids = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('abstract', '')}"
        vector = embed_text(text)
        uid = upsert_point(collection=collection, payload=item, vector=vector)
        ids.append(uid)
    return ids


@router.post("/run", response_model=DigestResponse)
async def run_digest(req: DigestRequest = DigestRequest()):
    collection = init_collection(COLLECTION)
    breakdown: dict[str, int] = {}

    # ── 1. Ingest arxiv ──────────────────────────────────────────────────────
    logger.info("Digest step 1/5: ingest arxiv")
    try:
        papers = await fetch_papers_async(
            keywords=req.keywords,
            max_results=req.max_results,
            categories=req.arxiv_categories,
            days=req.days,
        )
        breakdown["arxiv"] = len(papers)
        logger.info(f"  arxiv: {len(papers)} papers fetched")
    except Exception as e:
        logger.warning(f"  arxiv fetch failed: {e} — continuing with existing collection")
        papers = []
        breakdown["arxiv"] = 0

    # ── 2. Ingest github ─────────────────────────────────────────────────────
    logger.info("Digest step 2/5: ingest github")
    try:
        repos = await search_repos(req.keywords, max_results=10)
        breakdown["github"] = len(repos)
        logger.info(f"  github: {len(repos)} repos fetched")
    except Exception as e:
        logger.warning(f"  github fetch failed: {e} — continuing")
        repos = []
        breakdown["github"] = 0

    all_items = papers + repos
    if all_items:
        await _ingest_items(all_items, collection)
    papers_ingested = len(all_items)

    # ── 3. Synthesize ─────────────────────────────────────────────────────────
    logger.info("Digest step 3/5: synthesize")
    synthesis_result = await synthesize_topic(
        query=req.synthesis_query,
        collection=collection,
        top_k=req.top_papers,
    )

    # ── 4. Trends ─────────────────────────────────────────────────────────────
    logger.info("Digest step 4/5: compute trends")
    trends_data = compute_trends(collection=collection, top_n=req.top_trends)

    # ── 5. Push to Notion ─────────────────────────────────────────────────────
    logger.info("Digest step 5/5: push to Notion")

    # Top papers by semantic score from the synthesis sources
    top_sources = synthesis_result.get("sources", [])[:req.top_papers]
    papers_created = 0
    synthese_created = False
    tendances_created = 0

    if req.dry_run:
        logger.info("  dry_run=True — skipping Notion writes")
        papers_created = len(top_sources)
        synthese_created = True
        tendances_created = min(len(trends_data.get("top_keywords", [])), req.top_trends)
    else:
        # Push top papers
        for src in top_sources:
            try:
                await create_paper({
                    "title": src.get("title"),
                    "abstract": "",  # already chunked in qdrant; avoid re-fetching
                    "url": src.get("url"),
                    "source": src.get("source"),
                    "score": src.get("score"),
                })
                papers_created += 1
            except Exception as e:
                logger.error(f"  Notion paper create failed for '{src.get('title')}': {e}")

        # Push synthesis
        try:
            await create_synthese(synthesis_result)
            synthese_created = True
        except Exception as e:
            logger.error(f"  Notion synthese create failed: {e}")

        # Push top trends (keywords)
        for kw, count in trends_data.get("top_keywords", [])[:req.top_trends]:
            try:
                await create_tendance({"concept": kw, "count": count, "growth_score": 0.0})
                tendances_created += 1
            except Exception as e:
                logger.error(f"  Notion tendance create failed for '{kw}': {e}")

    logger.info(
        f"Digest complete: {papers_ingested} ingested, "
        f"{papers_created} papers pushed, synthese={synthese_created}, "
        f"{tendances_created} trends pushed"
    )

    return DigestResponse(
        papers_ingested=papers_ingested,
        papers_created=papers_created,
        synthese_created=synthese_created,
        tendances_created=tendances_created,
        synthesis_preview=synthesis_result.get("synthesis", "")[:500],
        dry_run=req.dry_run,
    )
