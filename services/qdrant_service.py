from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from services.embeddings import get_dim
import os, uuid

client = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)

def init_collection(name: str = "papers") -> str:
    existing = [c.name for c in client.get_collections().collections]
    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=get_dim(), distance=Distance.COSINE)
        )
    return name

def upsert_point(collection: str, payload: dict, vector: list[float]) -> str:
    uid = str(uuid.uuid5(uuid.NAMESPACE_URL, payload.get("url", str(uuid.uuid4()))))
    client.upsert(collection_name=collection,
                  points=[PointStruct(id=uid, vector=vector, payload=payload)])
    return uid


def search_similar(collection: str, query_text: str, top_k: int = 10, source_filter: str | None = None):
    from services.embeddings import embed_text
    vector = embed_text(query_text)
    query_filter = None
    if source_filter:
        query_filter = Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=source_filter))]
        )
    return client.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    )


def delete_point(collection: str, point_id: str) -> None:
    from qdrant_client.models import PointIdsList
    client.delete(collection_name=collection, points_selector=PointIdsList(points=[point_id]))