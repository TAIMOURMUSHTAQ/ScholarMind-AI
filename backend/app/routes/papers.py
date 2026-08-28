import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from app.config import MAX_UPLOAD_MB, UPLOADS_DIR
from app.ingestion import delete_paper_files, ingest_paper
from app.models.schemas import PaperDetail, PaperSummary, RenamePaperRequest
from app.rag.conversation_memory import ConversationMemory
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
    )


@router.post("/upload", response_model=PaperSummary, status_code=202)
async def upload_paper(background_tasks: BackgroundTasks, file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds the {MAX_UPLOAD_MB}MB upload limit.")

    paper_id = str(uuid.uuid4())
    dest = UPLOADS_DIR / f"{paper_id}_{file.filename}"
    dest.write_bytes(contents)

    record = PaperStore.create_placeholder(paper_id, file.filename)
    background_tasks.add_task(ingest_paper, paper_id, dest)

    return _to_summary(record)


@router.get("", response_model=list[PaperSummary])
def list_papers():
    return [_to_summary(r) for r in PaperStore.list_all()]


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
    )


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
