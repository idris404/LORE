import sys
sys.path.insert(0, "..")

import asyncio
import json
import logging
from state import LoreState
from services.llm import complete

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a scientific fact-checker. Given a research synthesis and a list of paper titles, "
    "identify claims that may contradict each other or lack consensus. "
    "Return a JSON array of objects with keys: "
    "\"claim\" (the contested statement), \"counter\" (the opposing view), "
    "\"severity\" (\"low\", \"medium\", or \"high\"). "
    "Return at most 5 contradictions. If none found, return []."
)


async def _check(synthesis: dict, papers: list) -> list:
    summary = synthesis.get("synthesis", "")[:1500]
    titles = [p.get("title", "") for p in papers if isinstance(p, dict)][:15]
    user = (
        f"Synthesis:\n{summary}\n\n"
        f"Papers covered:\n" + "\n".join(f"- {t}" for t in titles)
    )
    raw = await complete(SYSTEM_PROMPT, user)
    # extract JSON array from response
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        return []
    return json.loads(raw[start:end])


def fact_checker_agent(state: LoreState) -> dict:
    synthesis = state.get("synthesis") or {}
    papers = state.get("papers_ingested") or []
    try:
        contradictions = asyncio.run(_check(synthesis, papers))
        logger.info(f"[FactChecker] {len(contradictions)} contradictions found")
        return {"contradictions": contradictions if contradictions else []}
    except Exception as e:
        logger.error(f"[FactChecker] error: {e}")
        existing = state.get("agent_errors") or {}
        return {
            "contradictions": [],
            "agent_errors": {**existing, "fact_checker": str(e)},
        }
