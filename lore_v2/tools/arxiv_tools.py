import sys
sys.path.insert(0, "..")

import logging
from langchain_core.tools import tool
from services.arxiv_client import fetch_papers
from services.embeddings import embed_text
from services.qdrant_service import init_collection, upsert_point

logger = logging.getLogger(__name__)

COLLECTION = "papers"
DEFAULT_KEYWORDS = ["agentic AI", "large language models", "multi-agent systems"]
DEFAULT_CATEGORIES = ["cs.AI", "cs.LG", "cs.MA"]


@tool
def ingest_arxiv(days: int = 7, max_results: int = 20) -> list:
    """Fetch papers from arXiv, embed, and store in Qdrant. Returns list of ingested paper dicts."""
    collection = init_collection(COLLECTION)
    papers = fetch_papers(
        keywords=DEFAULT_KEYWORDS,
        max_results=max_results,
        categories=DEFAULT_CATEGORIES,
        days=days,
    )
    ingested = []
    for paper in papers:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        vector = embed_text(text)
        uid = upsert_point(collection=collection, payload=paper, vector=vector)
        paper["_id"] = uid
        ingested.append(paper)
        logger.info(f"[ingest_arxiv] {paper.get('title', '')[:70]}")
    logger.info(f"[ingest_arxiv] Total: {len(ingested)} papers")
    return ingested
