"""Pydantic request/response models for the FastAPI layer."""
from typing import Optional
from pydantic import BaseModel, Field


class MetadataOut(BaseModel):
    doi: str = ""
    year: str = ""
    venue: str = ""
    keywords: list[str] = []


class PaperSummary(BaseModel):
    """Row shown in the library list."""
    id: str
    filename: str
    title: str
    authors: list[str] = []
    upload_time: str
    status: str  # "processing" | "ready" | "failed"
    error_message: Optional[str] = None
    num_pages: int = 0
    num_chunks: int = 0


class PaperDetail(PaperSummary):
    """Full summary card shown on the paper page."""
    abstract: str = ""
    metadata: MetadataOut = MetadataOut()
    statistics: dict = {}
    section_titles: list[str] = []


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=15)


class RenamePaperRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)


class SourceOut(BaseModel):
    rank: int
    section_title: str
    page_start: int
    page_end: int
    score: float
    preview: str
    paper_title: Optional[str] = None


class ChatTurnOut(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    sources: list[SourceOut] = []


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceOut] = []


class ErrorResponse(BaseModel):
    detail: str
