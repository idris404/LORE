import sys
import json
import logging
from dotenv import load_dotenv
load_dotenv("../.env")

from graph import build_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _print_synthesis(state: dict) -> None:
    synthesis = state.get("synthesis") or {}
    print("\n" + "=" * 60)
    print("SYNTHESIS PREVIEW")
    print("=" * 60)
    print(f"Query : {synthesis.get('query', 'N/A')}")
    print(f"Sources: {len(synthesis.get('sources', []))}")
    text = synthesis.get("synthesis", "No synthesis available.")
    print("\n" + text[:1200] + ("..." if len(text) > 1200 else ""))

    contradictions = state.get("contradictions") or []
    if contradictions:
        print(f"\nContradictions detected: {len(contradictions)}")
        for c in contradictions[:3]:
            sev = c.get("severity", "?").upper()
            print(f"  [{sev}] {c.get('claim', '')[:80]}")

    trends = state.get("trends") or []
    real_trends = [t for t in trends if isinstance(t, dict) and not t.get("keyword", "").startswith("__")]
    if real_trends:
        print(f"\nTop trends: {', '.join(t['keyword'] for t in real_trends[:5])}")

    print("=" * 60)


def run(query: str = "agentic AI", days: int = 7, max_results: int = 20) -> None:
    graph = build_graph(interrupt_before_publish=True)
    config = {"configurable": {"thread_id": f"lore-{query[:20].replace(' ', '-')}"}}
    initial_state = {
        "query": query,
        "days": days,
        "max_results": max_results,
        "next": "",
        "iteration": 0,
        "papers_ingested": None,
        "synthesis": None,
        "contradictions": None,
        "trends": None,
        "publish_report": None,
        "error": None,
        "agent_errors": {},
    }

    logger.info(f"Starting LORE pipeline — query='{query}' days={days} max_results={max_results}")

    # Run until interrupt (before publisher)
    for chunk in graph.stream(initial_state, config, stream_mode="values"):
        pass  # stream to advance state; logs come from agents

    # Check current state at interrupt
    state = graph.get_state(config).values
    _print_synthesis(state)

    # Human-in-the-loop
    print("\nPublish to Notion? [y/N] ", end="", flush=True)
    answer = input().strip().lower()

    if answer == "y":
        logger.info("Resuming graph → publisher")
        result = graph.invoke(None, config)
        report = result.get("publish_report") or {}
        print(f"\nPublished — papers: {report.get('papers', 0)}, "
              f"synthesis: {report.get('synthesis', False)}, "
              f"trends: {report.get('trends', 0)}")
        errors = report.get("errors") or []
        if errors:
            print(f"Partial errors: {errors[:5]}")
    else:
        logger.info("Publish cancelled by user")
        print("Cancelled. Nothing pushed to Notion.")

    agent_errors = state.get("agent_errors") or {}
    if agent_errors:
        print(f"\nAgent errors during run: {json.dumps(agent_errors, indent=2)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LORE — Language-based Open Research Engine")
    parser.add_argument("--query", default="agentic AI")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--max-results", type=int, default=20)
    args = parser.parse_args()
    run(query=args.query, days=args.days, max_results=args.max_results)
