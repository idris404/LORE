import logging
from state import LoreState

logger = logging.getLogger(__name__)
MAX_ITER = 10


def supervisor(state: LoreState) -> LoreState:
    iteration = state.get("iteration", 0) + 1
    if iteration > MAX_ITER:
        logger.error("MAX_ITER reached")
        return {**state, "next": "end", "iteration": iteration}
    papers    = state.get("papers_ingested")
    synthesis = state.get("synthesis")
    trends    = state.get("trends")
    pub       = state.get("publish_report")
    if not papers:
        nxt = "researcher"
    elif not synthesis:
        nxt = "analyze_parallel"
    elif not trends:
        nxt = "trend_detector"
    elif not pub:
        nxt = "publisher"
    else:
        nxt = "end"
    logger.info(f"[Supervisor] iter={iteration} → {nxt}")
    return {**state, "next": nxt, "iteration": iteration}


def route(state: LoreState):
    nxt = state["next"]
    if nxt == "analyze_parallel":
        from langgraph.types import Send
        return [Send("analyzer", state), Send("fact_checker", state)]
    return nxt
