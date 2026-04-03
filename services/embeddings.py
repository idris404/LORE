from sentence_transformers import SentenceTransformer
from functools import lru_cache
import os

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    return SentenceTransformer(name)

def embed_text(text: str) -> list[float]:
    return get_model().encode(text[:2000], show_progress_bar=False).tolist()

def get_dim() -> int:
    return get_model().get_sentence_embedding_dimension()