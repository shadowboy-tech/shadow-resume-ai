# backend/app/rag/embed.py
"""
Embedding module — calls Mistral's mistral-embed API.

Switched from sentence-transformers (local PyTorch, ~400 MB RAM)
to the Mistral Embeddings API to keep the Render container under 512 MB.

Model: mistral-embed
Output dimension: 1024
"""

from typing import List
from mistralai.client import Mistral
from backend.app.config import settings

# Lazily initialised Mistral client
_client: Mistral | None = None


def _get_client() -> Mistral:
    global _client
    if _client is None:
        _client = Mistral(api_key=settings.MISTRAL_API_KEY)
    return _client


def embed_texts(texts: List[str], model_name: str = "mistral-embed") -> List[List[float]]:
    """
    Embed a batch of texts via the Mistral Embeddings API.

    Returns plain Python lists (Pinecone-compatible format).
    """
    client = _get_client()
    response = client.embeddings.create(model=model_name, inputs=texts)
    return [item.embedding for item in response.data]


def embed_query(query: str, model_name: str = "mistral-embed") -> List[float]:
    """Embed a single query string. Convenience wrapper over embed_texts."""
    return embed_texts([query], model_name)[0]
