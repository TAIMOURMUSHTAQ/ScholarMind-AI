"""Upload -> parse -> chunk -> embed -> index, one call per uploaded PDF."""
import shutil
from pathlib import Path

import pymupdf

from app.config import FIGURES_DIR, UPLOADS_DIR
from app.logger import logger
from app.pdf.figure_extractor import FigureExtractor
from app.pdf.pdf_processor import PDFProcessor
from app.rag.chunking import ChunkGenerator
from app.rag.embeddings import EmbeddingGenerator
from app.rag.enrichment import generate_insight_card, generate_tags
from app.rag.vector_store import VectorStore
from app.storage.paper_store import PaperStore

_processor = PDFProcessor()


def ingest_paper(paper_id: str, pdf_path: Path) -> None:
    try:
        paper = _processor.parse(pdf_path)

        chunks = ChunkGenerator.generate(paper_id, paper.sections)
        if chunks:
            embeddings = EmbeddingGenerator.embed_texts([c.text for c in chunks])
            VectorStore.index_chunks(paper_id, chunks, embeddings)
        else:
            logger.warning("Paper %s produced no chunks; chat will have no context.", paper_id)

        PaperStore.mark_ready(paper_id, paper, num_chunks=len(chunks))
        logger.info("Paper %s ingested successfully (%d chunks).", paper_id, len(chunks))
    except Exception as exc:
        logger.exception("Ingestion failed for paper %s", paper_id)
        PaperStore.mark_failed(paper_id, str(exc))
        return

    _extract_figures(paper_id, pdf_path)
    _enrich_paper(paper_id, paper)


def _extract_figures(paper_id: str, pdf_path: Path) -> None:
    """Best-effort: figures are a bonus panel, never block "ready" status."""
    try:
        doc = pymupdf.open(pdf_path)
        try:
            figures = FigureExtractor.extract(doc, FIGURES_DIR / paper_id)
        finally:
            doc.close()
        PaperStore.set_figures(paper_id, figures)
    except Exception:
        logger.warning("Figure extraction failed for paper %s", paper_id, exc_info=True)


def _enrich_paper(paper_id: str, paper) -> None:
    """Best-effort: an insight card and topic tags. Failure here never
    affects the paper's "ready" status - chat works regardless."""
    try:
        card = generate_insight_card(paper.title, paper.abstract, paper.full_text)
        PaperStore.set_insight_card(paper_id, card)
    except Exception:
        logger.warning("Insight card generation failed for paper %s", paper_id, exc_info=True)
        PaperStore.set_insight_card(paper_id, None)

    try:
        tags = generate_tags(paper.title, paper.abstract)
        PaperStore.set_tags(paper_id, tags)
    except Exception:
        logger.warning("Tag generation failed for paper %s", paper_id, exc_info=True)


def delete_paper_files(paper_id: str, filename: str) -> None:
    VectorStore.delete_paper(paper_id)
    upload_path = UPLOADS_DIR / f"{paper_id}_{filename}"
    if upload_path.exists():
        upload_path.unlink()
    shutil.rmtree(FIGURES_DIR / paper_id, ignore_errors=True)
