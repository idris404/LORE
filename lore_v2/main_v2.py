import sys
sys.path.insert(0, "..")

import uuid
import logging
from dotenv import load_dotenv
load_dotenv("../.env")

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from graph import build_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app   = FastAPI(title="LORE v2 — LangGraph")
graph = build_graph(interrupt_before_publish=False)


@app.post("/run")
async def run_graph(query: str = "agentic AI", days: int = 7, max_results: int = 30):
    config = {"configurable": {"thread_id": f"n8n-{uuid.uuid4().hex[:8]}"}}
    state0 = {
        "query": query, "days": days, "max_results": max_results,
        "next": "", "iteration": 0,
        "papers_ingested": None, "synthesis": None, "contradictions": None,
        "trends": None, "publish_report": None, "error": None, "agent_errors": {}
    }
    result = await run_in_threadpool(graph.invoke, state0, config)
    return {
        "papers_ingested":  len(result.get("papers_ingested") or []),
        "synthesis_ok":     bool(result.get("synthesis")),
        "contradictions":   len(result.get("contradictions") or []),
        "trends":           len(result.get("trends") or []),
        "publish_report":   result.get("publish_report"),
        "agent_errors":     result.get("agent_errors"),
    }
