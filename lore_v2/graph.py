import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send
from state import LoreState
from supervisor import supervisor, route
from agents.researcher import researcher_agent
from agents.analyzer import analyzer_agent
from agents.fact_checker import fact_checker_agent
from agents.trend_detector import trend_detector_agent
from agents.publisher import publisher_agent

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")


def _placeholder(name: str, fill: dict | None = None):
    """Placeholder node that logs and returns only the fields it owns.
    Returning a partial dict avoids concurrent-write conflicts on shared state fields
    when two nodes are dispatched in parallel via Send."""
    def fn(state: LoreState) -> dict:
        logging.info(f"[{name}] placeholder")
        return fill or {}
    fn.__name__ = name
    return fn


def build_graph(interrupt_before_publish: bool = True):
    b = StateGraph(LoreState)
    b.add_node("supervisor",     supervisor)
    b.add_node("researcher",     researcher_agent)
    b.add_node("analyzer",       analyzer_agent)
    b.add_node("fact_checker",   fact_checker_agent)
    b.add_node("trend_detector", trend_detector_agent)
    b.add_node("publisher",      publisher_agent)
    b.set_entry_point("supervisor")
    # route() returns Send list for parallel, string for single nodes, "end" for END
    b.add_conditional_edges("supervisor", route)
    for node in ["researcher", "analyzer", "fact_checker", "trend_detector", "publisher"]:
        b.add_edge(node, "supervisor")
    interrupt = ["publisher"] if interrupt_before_publish else []
    return b.compile(checkpointer=MemorySaver(), interrupt_before=interrupt)


if __name__ == "__main__":
    graph  = build_graph(interrupt_before_publish=False)
    config = {"configurable": {"thread_id": "test-skeleton"}}
    state0 = {
        "query": "agentic AI", "days": 7, "max_results": 20,
        "next": "", "iteration": 0,
        "papers_ingested": None, "synthesis": None,
        "contradictions": None, "trends": None,
        "publish_report": None, "error": None, "agent_errors": {}
    }
    result = graph.invoke(state0, config)
    print("Final next:", result["next"])
    print("Iterations:", result["iteration"])
