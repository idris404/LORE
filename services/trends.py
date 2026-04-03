from collections import Counter
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
import os
from datetime import datetime, timedelta

client = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333)),
)


def _scroll_all(collection: str, with_payload: bool = True) -> list:
    records, offset = [], None
    while True:
        batch, offset = client.scroll(
            collection_name=collection,
            limit=100,
            offset=offset,
            with_payload=with_payload,
            with_vectors=False,
        )
        records.extend(batch)
        if offset is None:
            break
    return records


def compute_trends(collection: str = "papers", top_n: int = 20) -> dict:
    records = _scroll_all(collection)
    if not records:
        return {"total": 0, "top_keywords": [], "top_categories": [], "sources": {}, "recent_titles": []}

    keyword_counter: Counter = Counter()
    category_counter: Counter = Counter()
    source_counter: Counter = Counter()
    recent: list[dict] = []
    cutoff = datetime.utcnow() - timedelta(days=30)

    for rec in records:
        p = rec.payload or {}
        # keywords from title words (simple heuristic)
        title_words = [w.lower() for w in p.get("title", "").split() if len(w) > 4]
        keyword_counter.update(title_words)
        # arxiv categories
        for cat in p.get("categories", []):
            category_counter[cat] += 1
        # source
        source_counter[p.get("source", "unknown")] += 1
        # recent papers
        pub = p.get("published")
        if pub:
            try:
                if datetime.fromisoformat(pub[:19]) >= cutoff:
                    recent.append({"title": p.get("title"), "published": pub, "url": p.get("url")})
            except ValueError:
                pass

    recent.sort(key=lambda x: x.get("published", ""), reverse=True)

    return {
        "total": len(records),
        "top_keywords": keyword_counter.most_common(top_n),
        "top_categories": category_counter.most_common(top_n),
        "sources": dict(source_counter),
        "recent_titles": recent[:10],
    }
