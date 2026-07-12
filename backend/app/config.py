# backend/app/config.py
"""
Central config — loads all env vars once, fails fast if anything critical is missing.

Why a dedicated config module instead of reading os.environ everywhere:
- Single source of truth for env var names
- Validates at startup, not on first request (easier to debug)
- Type-safe access throughout the app
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists (dev only — prod uses real env vars)
# Walk up to find .env in backend/ or project root
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")
load_dotenv(_backend_dir.parent / ".env")


class Settings:
    """App settings loaded from environment variables."""

    # ── Pinecone ──
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "shadow-kb")

    # ── Mistral ──
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

    # ── Embedding ──
    # Must match between ingestion and query — this is the single source of truth
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    EMBEDDING_DIMENSION: int = 384  # all-MiniLM-L6-v2 output size

    # ── CORS ──
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:5500").split(",")
        if origin.strip()
    ]

    # ── Paths ──
    KNOWLEDGE_BASE_DIR: str = os.getenv(
        "KNOWLEDGE_BASE_DIR",
        str(_backend_dir.parent / "knowledge_base"),
    )


# Singleton instance used throughout the app
settings = Settings()
