# backend/ingestion/ingest.py
"""
Full ingestion pipeline: parse → chunk → embed → upsert to Pinecone.

Run this whenever you update the knowledge base:
    python -m backend.ingestion.ingest

It will:
1. Parse all files in knowledge_base/ (PDF, DOCX, MD)
2. Chunk them into embedding-sized pieces with overlap
3. Embed each chunk using the configured HF model
4. Create the Pinecone index if it doesn't exist (auto-creation)
5. Clear old vectors and upsert fresh ones

This is designed to be idempotent — running it twice produces the same index.
"""

import sys
import time
from pathlib import Path

# Add project root to path so we can import from backend.app
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from pinecone import Pinecone, ServerlessSpec
from backend.app.config import settings
from backend.app.rag.embed import embed_texts
from backend.ingestion.parse import parse_all
from backend.ingestion.chunk import chunk_documents


def create_index_if_needed(pc: Pinecone) -> None:
    """
    Auto-create the Pinecone serverless index if it doesn't exist.

    Uses cosine metric + 384 dimensions to match all-MiniLM-L6-v2.
    AWS us-east-1 is the free-tier default for serverless indexes.
    """
    existing = [idx.name for idx in pc.list_indexes()]
    index_name = settings.PINECONE_INDEX_NAME

    if index_name in existing:
        print(f"[index] Index '{index_name}' already exists — skipping creation")
        return

    print(f"[index] Creating index '{index_name}' (dim={settings.EMBEDDING_DIMENSION}, metric=cosine)...")
    pc.create_index(
        name=index_name,
        dimension=settings.EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

    # Wait for the index to be ready
    print("[index] Waiting for index to be ready...")
    while not pc.describe_index(index_name).status.get("ready", False):
        time.sleep(2)
    print("[index] Index is ready!")


def run_ingestion() -> None:
    """Execute the full ingestion pipeline."""

    # ── Validate config ──
    if not settings.PINECONE_API_KEY:
        print("[ERROR] PINECONE_API_KEY is not set. Add it to backend/.env")
        sys.exit(1)

    kb_dir = settings.KNOWLEDGE_BASE_DIR
    print(f"[1/5] Parsing knowledge base at: {kb_dir}")
    documents = parse_all(kb_dir)
    if not documents:
        print("[ERROR] No documents found. Add files to knowledge_base/")
        sys.exit(1)

    # ── Chunk ──
    print(f"\n[2/5] Chunking {len(documents)} document(s)...")
    chunks = chunk_documents(documents)
    print(f"       -> {len(chunks)} chunks created")

    # ── Embed ──
    print(f"\n[3/5] Embedding {len(chunks)} chunks with {settings.EMBEDDING_MODEL_NAME}...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts, settings.EMBEDDING_MODEL_NAME)
    print(f"       -> {len(embeddings)} embeddings generated (dim={len(embeddings[0])})")

    # ── Connect to Pinecone and ensure index exists ──
    print(f"\n[4/5] Connecting to Pinecone...")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    create_index_if_needed(pc)

    index = pc.Index(settings.PINECONE_INDEX_NAME)

    # ── Clear existing vectors (idempotent re-ingestion) ──
    print(f"       Clearing existing vectors in '{settings.PINECONE_INDEX_NAME}'...")
    try:
        index.delete(delete_all=True)
        # Brief pause to let Pinecone process the delete
        time.sleep(2)
    except Exception as e:
        if "404" in str(e) or "Namespace not found" in str(e):
            print("       (Index is empty, nothing to clear)")
        else:
            raise

    # ── Upsert ──
    print(f"\n[5/5] Upserting {len(chunks)} vectors...")

    # Build upsert records: id, embedding, metadata
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{chunk['source']}_{chunk['chunk_index']}",
            "values": embedding,
            "metadata": {
                "source": chunk["source"],
                "text": chunk["text"],       # stored in metadata for retrieval
                "chunk_index": chunk["chunk_index"],
            },
        })

    # Upsert in batches of 100 (Pinecone best practice)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)
        print(f"       Upserted batch {i // batch_size + 1} ({len(batch)} vectors)")

    # Brief pause then verify
    time.sleep(3)
    stats = index.describe_index_stats()
    print(f"\n{'='*60}")
    print(f"[OK] Ingestion complete!")
    print(f"  Index: {settings.PINECONE_INDEX_NAME}")
    print(f"  Total vectors: {stats.total_vector_count}")
    print(f"  Sources: {set(c['source'] for c in chunks)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_ingestion()
