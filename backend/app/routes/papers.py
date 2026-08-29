import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from app.config import MAX_UPLOAD_MB, UPLOADS_DIR
from app.ingestion import delete_paper_files, ingest_paper
from app.models.schemas import (
    ImportArxivRequest,
    LibrarySearchResult,
    PaperDetail,
    PaperSummary,
    RelatedPaper,
    RenamePaperRequest,
)
from app.rag.conversation_memory import ConversationMemory
from app.rag.discovery import ArxivImportError, download_arxiv_pdf, find_related_papers
from app.rag.library_search import search_library
from app.storage.paper_store import PaperStore

router = APIRouter(prefix="/api/papers", tags=["papers"])

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def _to_summary(record: dict) -> PaperSummary:
    return PaperSummary(
        id=record["id"],
        filename=record["filename"],
        title=record.get("title") or record["filename"],
        authors=record.get("authors", []),
        upload_time=record["upload_time"],
        status=record["status"],
        error_message=record.get("error_message"),
        num_pages=record.get("num_pages", 0),
        num_chunks=record.get("num_chunks", 0),
        tags=record.get("tags", []),
    )


def _save_and_queue_ingestion(background_tasks: BackgroundTasks, filename: str, contents: bytes) -> PaperSummary:
    paper_id = str(uuid.uuid4())
    # Path(...).name strips any directory components a malicious client could
    # smuggle in the filename (e.g. "../../evil.pdf") - without it this would
    # be a path-traversal write primitive outside UPLOADS_DIR.
    safe_filename = Path(filename).name
    dest = UPLOADS_DIR / f"{paper_id}_{safe_filename}"
    dest.write_bytes(contents)

    record = PaperStore.create_placeholder(paper_id, safe_filename)
    background_tasks.add_task(ingest_paper, paper_id, dest)

    return _to_summary(record)


@router.post("/upload", response_model=PaperSummary, status_code=202)
async def upload_paper(background_tasks: BackgroundTasks, file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds the {MAX_UPLOAD_MB}MB upload limit.")

    return _save_and_queue_ingestion(background_tasks, file.filename, contents)


@router.post("/import-arxiv", response_model=PaperSummary, status_code=202)
def import_from_arxiv(background_tasks: BackgroundTasks, body: ImportArxivRequest):
    try:
        arxiv_id, contents = download_arxiv_pdf(body.arxiv_id)
    except ArxivImportError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"arXiv paper exceeds the {MAX_UPLOAD_MB}MB limit.")

    return _save_and_queue_ingestion(background_tasks, f"arxiv-{arxiv_id}.pdf", contents)


@router.get("", response_model=list[PaperSummary])
def list_papers():
    return [_to_summary(r) for r in PaperStore.list_all()]


@router.get("/search", response_model=list[LibrarySearchResult])
def search_papers(q: str):
    """Registered before /{paper_id} - otherwise FastAPI would try to match
    "search" itself as a paper_id path parameter."""
    return search_library(q)


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: str):
    record = PaperStore.get(paper_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No paper found with that id.")

    summary = _to_summary(record)
    return PaperDetail(
        **summary.model_dump(),
        abstract=record.get("abstract", ""),
        metadata=record.get("metadata", {}),
        statistics=record.get("statistics", {}),
        section_titles=record.get("section_titles", []),
        insight_card=record.get("insight_card"),
        insight_status=record.get("insight_status", "pending"),
        figures=record.get("figures", []),
    )


@router.get("/{paper_id}/related", response_model=list[RelatedPaper])
def get_related_papers(paper_id: str):
    record = PaperStore.get(paper_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No paper found with that id.")

    if record.get("related_papers"):
        return record["related_papers"]

    related = find_related_papers(record.get("title") or record["filename"])
    # Only cache a non-empty result: an empty list here is indistinguishable
    # between "genuinely no related papers" and "Semantic Scholar was
    # rate-limited/unreachable" (find_related_papers degrades to [] either
    # way). Caching the latter would wrongly hide related papers forever
    # once the transient failure clears - better to just retry next visit.
    if related:
        PaperStore.set_related_papers(paper_id, related)
    return related


@router.patch("/{paper_id}", response_model=PaperSummary)
def rename_paper(paper_id: str, body: RenamePaperRequest):
    record = PaperStore.rename(paper_id, body.title.strip())
    if record is None:
        raise HTTPException(status_code=404, detail="No paper found with that id.")
    return _to_summary(record)


@router.delete("/{paper_id}", status_code=204)
def delete_paper(paper_id: str):
    record = PaperStore.get(paper_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No paper found with that id.")

    delete_paper_files(paper_id, record["filename"])
    ConversationMemory.clear(paper_id)
    PaperStore.delete(paper_id)
