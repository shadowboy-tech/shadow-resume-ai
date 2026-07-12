# backend/app/rag/embed.py
"""
Embedding module — wraps sentence-transformers for both ingestion and query.

The model is loaded once (lazily) and reused. Using a module-level cache
instead of re-loading on every request because:
1. The model is ~80MB — loading it takes a couple seconds
2. It's stateless, so sharing it across requests is safe
3. sentence-transformers handles batching internally
"""

from typing import List
from sentence_transformers import SentenceTransformer

# Lazy-loaded model cache
_model: SentenceTransformer | None = None


def get_model(model_name: str) -> SentenceTransformer:
    """Load the embedding model once, cache it for reuse."""
    global _model
    if _model is None:
        print(f"[embed] Loading model: {model_name}")
        _model = SentenceTransformer(model_name)
        print(f"[embed] Model loaded (dimension: {_model.get_sentence_embedding_dimension()})")
    return _model


def embed_texts(texts: List[str], model_name: str) -> List[List[float]]:
    """
    Embed a batch of texts into vectors.

    Returns plain Python lists (not numpy) because Pinecone expects that format.
    """
    model = get_model(model_name)
    embeddings = model.encode(texts, show_progress_bar=len(texts) > 10)
    return embeddings.tolist()


def embed_query(query: str, model_name: str) -> List[float]:
    """Embed a single query string. Convenience wrapper over embed_texts."""
    return embed_texts([query], model_name)[0]
