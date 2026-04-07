import sys
sys.path.insert(0, "..")

import asyncio
import logging
from state import LoreState
from services.synthesis import synthesize_topic

logger = logging.getLogger(__name__)


def analyzer_agent(state: LoreState) -> dict:
    query = state.get("query", "agentic AI")
    try:
        result = asyncio.run(synthesize_topic(query=query, top_k=8))
        logger.info(f"[Analyzer] synthesis done — {len(result.get('sources', []))} sources")
        return {"synthesis": result}
    except Exception as e:
        logger.error(f"[Analyzer] error: {e}")
        existing = state.get("agent_errors") or {}
        return {
            "synthesis": {"query": query, "synthesis": f"Error: {e}", "sources": []},
            "agent_errors": {**existing, "analyzer": str(e)},
        }
