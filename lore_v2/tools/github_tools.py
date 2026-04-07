import sys
sys.path.insert(0, "..")

import asyncio
import logging
from langchain_core.tools import tool
from services.github_client import search_repos
from services.embeddings import embed_text
from services.qdrant_service import init_collection, upsert_point

logger = logging.getLogger(__name__)

COLLECTION = "papers"
DEFAULT_KEYWORDS = ["agentic AI", "LLM", "multi-agent"]


@tool
def ingest_github(max_results: int = 10) -> list:
    """Fetch trending AI repos from GitHub, embed, and store in Qdrant. Returns list of ingested repo dicts."""
    collection = init_collection(COLLECTION)
    repos = asyncio.run(search_repos(DEFAULT_KEYWORDS, max_results=max_results))
    ingested = []
    for repo in repos:
        text = f"{repo.get('title', '')} {repo.get('abstract', '')}"
        vector = embed_text(text)
        uid = upsert_point(collection=collection, payload=repo, vector=vector)
        repo["_id"] = uid
        ingested.append(repo)
        logger.info(f"[ingest_github] {repo.get('title', '')[:70]}")
    logger.info(f"[ingest_github] Total: {len(ingested)} repos")
    return ingested
