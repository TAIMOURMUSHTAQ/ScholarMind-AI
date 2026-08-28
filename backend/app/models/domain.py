"""Plain dataclasses representing a parsed paper and its parts.

Kept separate from `schemas.py` (the Pydantic API layer) so the parsing
pipeline has no dependency on FastAPI/Pydantic.
"""
from dataclasses import dataclass, field


@dataclass
class LayoutBlock:
    """One text block extracted from a PDF page, with font/position info."""
    text: str
    font_size: float
    x0: float
    y0: float
    x1: float
    y1: float
    block_number: int
    page_number: int = 0


@dataclass
class Section:
    """One logical section of a paper (e.g. 'II. METHODOLOGY')."""
    title: str
    content: str
    page_start: int = 0
    page_end: int = 0


@dataclass
class Citation:
    reference_number: int
    section_title: str
    sentence: str


@dataclass
class Reference:
    number: int = 0
    raw_text: str = ""


@dataclass
class Metadata:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    venue: str = ""
    doi: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class Chunk:
    """One retrieval-unit of text, scoped to a paper."""
    id: str
    paper_id: str
    section_title: str
    text: str
    page_start: int
    page_end: int
    word_count: int


@dataclass
class Paper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    full_text: str = ""
    page_count: int = 0
    statistics: dict = field(default_factory=dict)
    sections: list[Section] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    metadata: Metadata = field(default_factory=Metadata)
    chunks: list[Chunk] = field(default_factory=list)
