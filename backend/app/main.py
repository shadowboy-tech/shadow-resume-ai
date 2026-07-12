# backend/app/main.py
"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.schemas import HealthResponse

app = FastAPI(
    title="Shadow API",
    description="RAG-powered chatbot for Muhammad's portfolio",
    version="1.0.0",
)

# ── CORS Middleware ──
# Very permissive in dev, will be tightened in M6
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint."""
    return HealthResponse(status="ok")
