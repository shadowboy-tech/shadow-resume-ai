# backend/app/rag/retrieve.py
"""
Queries Pinecone for the most relevant knowledge base chunks.
"""

from typing import List, Dict, Any
from pinecone import Pinecone
from backend.app.config import settings
from backend.app.rag.embed import embed_query

# Cache the Pinecone client to avoid reconnecting on every query
_pc = None
_index = None


def get_pinecone_index():
    """Lazy-load the Pinecone index connection."""
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        _index = _pc.Index(settings.PINECONE_INDEX_NAME)
    return _index


def retrieve_chunks(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embed the user's question, search Pinecone, and return the top_k
    matching chunks along with their source filenames.
    """
    # 1. Embed the question using the exact same model used for ingestion
    query_vector = embed_query(question, settings.EMBEDDING_MODEL_NAME)

    # 2. Query Pinecone
    index = get_pinecone_index()
    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,  # Crucial: we need the text and source back!
    )

    # 3. Format the results
    results = []
    for match in response.matches:
        results.append({
            "score": match.score,
            "text": match.metadata.get("text", ""),
            "source": match.metadata.get("source", "unknown"),
        })

    return results
