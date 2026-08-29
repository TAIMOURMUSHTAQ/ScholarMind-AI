"""Pydantic request/response models for the FastAPI layer."""
from typing import Literal, Optional
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
    tags: list[str] = []


class InsightCard(BaseModel):
    problem: str = ""
    method: str = ""
    key_results: list[str] = []
    limitations: list[str] = []
    contributions: list[str] = []


class FigureOut(BaseModel):
    id: str
    page: int
    caption: str = ""


class PaperDetail(PaperSummary):
    """Full summary card shown on the paper page."""
    abstract: str = ""
    metadata: MetadataOut = MetadataOut()
    statistics: dict = {}
    section_titles: list[str] = []
    insight_card: Optional[InsightCard] = None
    insight_status: str = "pending"  # "pending" | "ready" | "unavailable"
    figures: list[FigureOut] = []


class FigureQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class FigureAnswerResponse(BaseModel):
    answer: str


ReadingLevel = Literal["default", "eli5", "expert"]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=15)
    reading_level: ReadingLevel = "default"


class RenamePaperRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)


class RelatedPaper(BaseModel):
    title: str
    abstract: str = ""
    year: Optional[int] = None
    authors: list[str] = []
    url: str = ""


class ImportArxivRequest(BaseModel):
    arxiv_id: str = Field(..., min_length=3, max_length=200)


class LibrarySearchResult(BaseModel):
    paper_id: str
    paper_title: str
    section_title: str
    page_start: int
    page_end: int
    score: float
    preview: str


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
    followups: list[str] = []


class ErrorResponse(BaseModel):
    detail: str
