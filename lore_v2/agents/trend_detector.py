import sys
sys.path.insert(0, "..")

import logging
from state import LoreState
from services.trends import compute_trends

logger = logging.getLogger(__name__)


def trend_detector_agent(state: LoreState) -> dict:
    try:
        raw = compute_trends(collection="papers", top_n=20)
        trends = [
            {"keyword": kw, "count": count}
            for kw, count in raw.get("top_keywords", [])[:10]
        ]
        # pad with categories if keywords sparse
        if len(trends) < 3:
            for cat, count in raw.get("top_categories", [])[:5]:
                trends.append({"keyword": cat, "count": count})
        logger.info(f"[TrendDetector] {len(trends)} trends — total docs: {raw.get('total', 0)}")
        return {"trends": trends if trends else [{"keyword": "__no_data__", "count": 0}]}
    except Exception as e:
        logger.error(f"[TrendDetector] error: {e}")
        existing = state.get("agent_errors") or {}
        return {
            "trends": [{"keyword": "__error__", "count": 0}],
            "agent_errors": {**existing, "trend_detector": str(e)},
        }
