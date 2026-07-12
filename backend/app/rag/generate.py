# backend/app/rag/generate.py
"""
Generation module — calls Mistral API to generate a grounded answer based on retrieved chunks.
"""

from typing import List, Dict, Any, Tuple
from mistralai.client import Mistral
from backend.app.config import settings

_client = None

def get_mistral_client() -> Mistral:
    """Lazy-load the Mistral client."""
    global _client
    if _client is None:
        _client = Mistral(api_key=settings.MISTRAL_API_KEY)
    return _client


SYSTEM_PROMPT = """You are Shadow, a helpful and professional AI assistant embedded on Muhammad's portfolio website.
Your job is to answer questions about Muhammad for recruiters and potential collaborators.

CRITICAL RULES:
1. ONLY answer using the provided CONTEXT. Do not use outside knowledge.
2. If the answer is not in the CONTEXT, gracefully say you don't know and tell them to contact Muhammad directly.
3. Speak ABOUT Muhammad in the third person (e.g., "Muhammad built...", not "I built...").
4. Keep answers concise, professional, and directly to the point.
"""


def generate_answer(question: str, chunks: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    """
    Generate an answer using Mistral, grounded in the provided chunks.
    Returns a tuple of (answer_text, list_of_unique_sources).
    """
    if not chunks:
        return "I don't have enough context to answer that. You can contact Muhammad directly at inuwamuhammad930@gmail.com.", []

    # Build context string from chunks
    context_text = "\n\n---\n\n".join(
        f"Source: {c['source']}\n{c['text']}" for c in chunks
    )

    prompt = f"""CONTEXT:
{context_text}

USER QUESTION: {question}

Remember the rules: use ONLY the context above, and speak about Muhammad in the third person."""

    client = get_mistral_client()
    
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,  # Low temperature for factual RAG
    )

    answer = response.choices[0].message.content
    
    # Deduplicate sources while preserving order (roughly)
    sources = []
    for c in chunks:
        if c["source"] not in sources:
            sources.append(c["source"])

    return answer, sources
