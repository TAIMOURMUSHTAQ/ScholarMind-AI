"""Upload -> parse -> chunk -> embed -> index, one call per uploaded PDF."""
from pathlib import Path

from app.config import UPLOADS_DIR
from app.logger import logger
from app.pdf.pdf_processor import PDFProcessor
from app.rag.chunking import ChunkGenerator
from app.rag.embeddings import EmbeddingGenerator
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


def delete_paper_files(paper_id: str, filename: str) -> None:
    VectorStore.delete_paper(paper_id)
    upload_path = UPLOADS_DIR / f"{paper_id}_{filename}"
    if upload_path.exists():
        upload_path.unlink()
