# backend/app/main.py
"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.schemas import HealthResponse, ChatRequest, ChatResponse
from backend.app.rag.retrieve import retrieve_chunks

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


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    TEMPORARY M4 IMPLEMENTATION:
    Returns the retrieved chunks directly so we can verify retrieval quality
    before hooking up the LLM generator.
    """
    chunks = retrieve_chunks(request.question, top_k=3)
    
    # Just format it roughly as a ChatResponse so the client doesn't break,
    # but put the raw chunk text in the "answer" field for debugging.
    debug_answer = "\n\n---\n\n".join(
        f"[Score: {c['score']:.2f} | {c['source']}]\n{c['text']}" 
        for c in chunks
    )
    
    return ChatResponse(
        answer=f"**RETRIEVAL DEBUG ONLY**\n\n{debug_answer}",
        sources=[c["source"] for c in chunks]
    )
