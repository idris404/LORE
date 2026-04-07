import sys
sys.path.insert(0, "..")

import asyncio
import logging
from state import LoreState
from services.notion_client import create_paper, create_synthese, create_tendance

logger = logging.getLogger(__name__)

MAX_PAPERS_TO_PUBLISH = 5


async def _publish(state: LoreState) -> dict:
    papers = state.get("papers_ingested") or []
    synthesis = state.get("synthesis") or {}
    trends = state.get("trends") or []
    report: dict = {"papers": 0, "synthesis": False, "trends": 0, "errors": []}

    # publish top papers
    real_papers = [p for p in papers if isinstance(p, dict) and p.get("title")]
    for paper in real_papers[:MAX_PAPERS_TO_PUBLISH]:
        try:
            await create_paper(paper)
            report["papers"] += 1
        except Exception as e:
            logger.warning(f"[Publisher] create_paper failed: {e}")
            report["errors"].append(f"paper:{e}")

    # publish synthesis
    if synthesis.get("synthesis"):
        try:
            await create_synthese(synthesis)
            report["synthesis"] = True
        except Exception as e:
            logger.warning(f"[Publisher] create_synthese failed: {e}")
            report["errors"].append(f"synthesis:{e}")

    # publish trends
    real_trends = [t for t in trends if isinstance(t, dict) and t.get("keyword", "").startswith("__") is False]
    for trend in real_trends[:10]:
        try:
            await create_tendance({"concept": trend["keyword"], "count": trend["count"], "growth_score": 0.0})
            report["trends"] += 1
        except Exception as e:
            logger.warning(f"[Publisher] create_tendance failed: {e}")
            report["errors"].append(f"trend:{e}")

    logger.info(f"[Publisher] papers={report['papers']} synthesis={report['synthesis']} trends={report['trends']}")
    return report


def publisher_agent(state: LoreState) -> dict:
    try:
        report = asyncio.run(_publish(state))
        return {"publish_report": report}
    except Exception as e:
        logger.error(f"[Publisher] error: {e}")
        existing = state.get("agent_errors") or {}
        return {
            "publish_report": {"error": str(e)},
            "agent_errors": {**existing, "publisher": str(e)},
        }
