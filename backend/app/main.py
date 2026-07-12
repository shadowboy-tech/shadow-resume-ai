# backend/app/main.py
"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.schemas import HealthResponse, ChatRequest, ChatResponse
from backend.app.rag.retrieve import retrieve_chunks
from backend.app.rag.generate import generate_answer

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


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG Chat endpoint.
    1. Embeds user question and searches Pinecone.
    2. Passes retrieved chunks to Mistral to generate a grounded answer.
    """
    # 1. Retrieve top context
    chunks = retrieve_chunks(request.question, top_k=3)
    
    # 2. Generate answer
    answer, sources = generate_answer(request.question, chunks)
    
    return ChatResponse(
        answer=answer,
        sources=sources
    )
