# backend/ingestion/chunk.py
"""
Splits parsed text into overlapping chunks for embedding.

Why overlap? If a key fact sits right at a chunk boundary, overlap ensures
it appears in full in at least one chunk. 200-char overlap is ~50 tokens —
enough to capture a sentence fragment without bloating the index.

Chunk size of ~1500 chars ≈ 375 tokens, which fits comfortably in the
embedding model's 512-token context window while keeping chunks dense enough
to be useful for retrieval.
"""

from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 1500,   # chars (~375 tokens)
    overlap: int = 200,       # chars (~50 tokens)
) -> List[str]:
    """
    Split text into overlapping chunks by character count.

    Simple character-based splitting is used intentionally over token-based
    splitting — it's model-agnostic, fast, and good enough for knowledge
    base docs that are mostly continuous prose.
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        # If we're not at the end, try to break at a paragraph or sentence boundary
        # so we don't split mid-word or mid-sentence
        if end < text_len:
            # Prefer paragraph break
            para_break = text.rfind("\n\n", start, end)
            if para_break > start + chunk_size // 2:
                end = para_break + 2  # include the newlines
            else:
                # Fall back to sentence break (period + space)
                sent_break = text.rfind(". ", start, end)
                if sent_break > start + chunk_size // 2:
                    end = sent_break + 2  # include ". "

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward by chunk_size minus overlap
        start = end - overlap if end < text_len else text_len

    return chunks


def chunk_documents(documents: List[Dict[str, str]], **kwargs) -> List[Dict[str, str]]:
    """
    Chunk a list of {source, text} dicts (from parse_all) into
    a flat list of {source, text, chunk_index} dicts.

    Preserves source attribution so each vector knows which file it came from.
    """
    chunks = []
    for doc in documents:
        doc_chunks = chunk_text(doc["text"], **kwargs)
        for i, chunk_text_str in enumerate(doc_chunks):
            chunks.append({
                "source": doc["source"],
                "text": chunk_text_str,
                "chunk_index": i,
            })
    return chunks


# ── Quick test ──
if __name__ == "__main__":
    sample = "A" * 3000 + "\n\n" + "B" * 2000
    chunks = chunk_text(sample, chunk_size=1500, overlap=200)
    print(f"Input: {len(sample)} chars → {len(chunks)} chunks")
    for i, c in enumerate(chunks):
        print(f"  Chunk {i}: {len(c)} chars, starts with '{c[:20]}...'")
