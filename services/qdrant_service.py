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