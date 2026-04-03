from services.qdrant_service import search_similar
from services.llm import complete


async def synthesize_topic(query: str, collection: str = "papers", top_k: int = 8) -> dict:
    """Retrieve relevant papers and synthesize a research overview via LLM."""
    hits = search_similar(collection=collection, query_text=query, top_k=top_k)

    if not hits:
        return {"query": query, "synthesis": "No relevant papers found.", "sources": []}

    context_parts = []
    sources = []
    for i, hit in enumerate(hits, 1):
        p = hit.payload
        context_parts.append(
            f"[{i}] Title: {p.get('title', 'Unknown')}\n"
            f"    Source: {p.get('source', '')}\n"
            f"    Abstract: {p.get('abstract', '')[:400]}"
        )
        sources.append({
            "rank": i,
            "title": p.get("title"),
            "url": p.get("url"),
            "source": p.get("source"),
            "score": round(hit.score, 4),
        })

    context = "\n\n".join(context_parts)
    system = (
        "You are an expert AI research analyst. Given a set of papers and repositories, "
        "write a comprehensive synthesis that: identifies main themes, compares approaches, "
        "highlights state-of-the-art results, and suggests open research questions. "
        "Be concise but thorough. Cite sources by their number [1], [2], etc."
    )
    user = f"Research query: {query}\n\nSources:\n{context}"

    synthesis = await complete(system, user)
    return {"query": query, "synthesis": synthesis, "sources": sources}
