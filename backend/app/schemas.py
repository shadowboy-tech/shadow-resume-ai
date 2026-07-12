# backend/app/schemas.py
"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List


class HealthResponse(BaseModel):
    status: str = Field(default="ok")


class ChatRequest(BaseModel):
    question: str = Field(..., example="What backend frameworks does Muhammad use?")


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
