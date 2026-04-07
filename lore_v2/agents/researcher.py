import sys
sys.path.insert(0, "..")

import logging
from state import LoreState
from tools.arxiv_tools import ingest_arxiv
from tools.github_tools import ingest_github

logger = logging.getLogger(__name__)


def researcher_agent(state: LoreState) -> dict:
    days = state.get("days", 7)
    max_results = state.get("max_results", 20)
    papers = []
    errors = {}

    try:
        arxiv_papers = ingest_arxiv.invoke({"days": days, "max_results": max_results})
        papers.extend(arxiv_papers)
        logger.info(f"[Researcher] arXiv: {len(arxiv_papers)} papers")
    except Exception as e:
        logger.error(f"[Researcher] arXiv error: {e}")
        errors["arxiv"] = str(e)

    try:
        github_repos = ingest_github.invoke({"max_results": max(1, max_results // 2)})
        papers.extend(github_repos)
        logger.info(f"[Researcher] GitHub: {len(github_repos)} repos")
    except Exception as e:
        logger.error(f"[Researcher] GitHub error: {e}")
        errors["github"] = str(e)

    logger.info(f"[Researcher] Total: {len(papers)} items")

    result: dict = {"papers_ingested": papers if papers else ["__no_results__"]}
    if errors:
        existing = state.get("agent_errors") or {}
        result["agent_errors"] = {**existing, **errors}
    return result
