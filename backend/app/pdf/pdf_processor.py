"""Orchestrates PDF -> structured Paper, with boundary-safe error handling.

Failure modes handled explicitly (see README "Error handling"):
  - not a valid/parseable PDF        -> InvalidPDFError
  - PDF has no extractable text      -> ScannedPDFError (e.g. scanned images)
"""
from pathlib import Path

import pymupdf

from app.config import MIN_CHARS_PER_PAGE
from app.exceptions import InvalidPDFError, ScannedPDFError
from app.logger import logger
from app.models.domain import Paper
from app.pdf.extractors import (
    AbstractExtractor,
    AuthorExtractor,
    CitationExtractor,
    DocumentStatistics,
    MetadataExtractor,
    ReferenceExtractor,
    SectionExtractor,
    TitleExtractor,
)
from app.pdf.layout_analyzer import LayoutAnalyzer
from app.pdf.reading_order import ReadingOrderAnalyzer


class PDFProcessor:
    """Parses a PDF file into a structured Paper object."""

    def parse(self, pdf_path: str | Path) -> Paper:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            doc = pymupdf.open(pdf_path)
        except Exception as exc:
            raise InvalidPDFError(
                "This file could not be opened as a PDF. It may be corrupted, "
                "password-protected, or not a real PDF."
            ) from exc

        try:
            return self._parse_document(doc)
        finally:
            doc.close()

    def _parse_document(self, doc) -> Paper:
        if doc.page_count == 0:
            raise InvalidPDFError("This PDF has no pages.")

        layout_blocks = []
        full_text_parts = []

        for page in doc:
            full_text_parts.append(page.get_text("text", sort=True))
            page_blocks = LayoutAnalyzer.extract(page)
            layout_blocks.extend(ReadingOrderAnalyzer.sort(page_blocks))

        full_text = "".join(full_text_parts).strip()

        avg_chars_per_page = len(full_text) / doc.page_count
        if avg_chars_per_page < MIN_CHARS_PER_PAGE:
            raise ScannedPDFError(
                "This PDF has little or no extractable text — it looks like a "
                "scanned or image-only document. ScholarMind AI needs a text "
                "layer to work; try running it through OCR first."
            )

        paper = Paper()
        paper.full_text = full_text
        paper.page_count = doc.page_count

        paper.title = TitleExtractor.extract(layout_blocks)
        paper.authors = AuthorExtractor.extract(layout_blocks, paper.title)
        paper.abstract = AbstractExtractor.extract(layout_blocks)
        paper.sections = SectionExtractor.extract(layout_blocks)
        paper.citations = CitationExtractor.extract(paper.sections)
        paper.references = ReferenceExtractor.extract(layout_blocks)
        paper.metadata = MetadataExtractor.extract(full_text, paper.title, paper.authors)
        paper.statistics = DocumentStatistics.analyze(paper)

        if not paper.sections:
            logger.warning("No numbered sections detected; falling back to whole-document section.")
            from app.models.domain import Section

            paper.sections = [
                Section(title="Full Text", content=full_text, page_start=0, page_end=doc.page_count - 1)
            ]

        return paper
