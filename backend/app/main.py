# backend/app/main.py
"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.app.config import settings
from backend.app.schemas import HealthResponse, ChatRequest, ChatResponse
from backend.app.rag.retrieve import retrieve_chunks
from backend.app.rag.generate import generate_answer

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Shadow API",
    description="RAG-powered chatbot for Muhammad's portfolio",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler to prevent stack traces from leaking."""
    print(f"ERROR: {exc}") # In prod, use standard logger
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
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


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(body: ChatRequest, request: Request):
    """
    RAG Chat endpoint.
    1. Embeds user question and searches Pinecone.
    2. Passes retrieved chunks to Mistral to generate a grounded answer.
    """
    # 1. Retrieve top context
    chunks = retrieve_chunks(body.question, top_k=3)
    
    # 2. Generate answer
    answer, sources = generate_answer(body.question, chunks)
    
    return ChatResponse(
        answer=answer,
        sources=sources
    )
