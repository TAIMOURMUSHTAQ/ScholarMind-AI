import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import CORS_ORIGINS, UPLOADS_DIR
from app.exceptions import InvalidPDFError, PaperNotFoundError, ScannedPDFError, ScholarMindError
from app.ingestion import ingest_paper
from app.logger import logger
from app.routes import chat, compare, figures, papers
from app.storage.paper_store import PaperStore


def resume_interrupted_ingestions() -> None:
    """A paper can be left stuck in "processing" forever if the server
    process dies mid-ingestion (a crash, or - in dev - the --reload
    autoreloader killing the worker while a BackgroundTask is running).
    The uploaded PDF is still on disk, so on every boot we just re-run
    ingestion for anything still marked "processing" rather than leaving
    it silently stuck."""
    stuck = [r for r in PaperStore.list_all() if r["status"] == "processing"]
    for record in stuck:
        pdf_path = UPLOADS_DIR / f"{record['id']}_{record['filename']}"
        if pdf_path.exists():
            logger.warning("Resuming interrupted ingestion for paper %s", record["id"])
            threading.Thread(target=ingest_paper, args=(record["id"], pdf_path), daemon=True).start()
        else:
            logger.warning("Paper %s stuck in processing but its file is missing; marking failed", record["id"])
            PaperStore.mark_failed(record["id"], "Processing was interrupted and the uploaded file could not be found.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    resume_interrupted_ingestions()
    yield


app = FastAPI(
    title="ScholarMind AI",
    description="Upload a research paper, get a structured summary, and chat with it - grounded in retrieval, not hallucination.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(compare.router)
app.include_router(figures.router)


@app.exception_handler(InvalidPDFError)
async def invalid_pdf_handler(request, exc: InvalidPDFError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ScannedPDFError)
async def scanned_pdf_handler(request, exc: ScannedPDFError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(PaperNotFoundError)
async def paper_not_found_handler(request, exc: PaperNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ScholarMindError)
async def scholarmind_error_handler(request, exc: ScholarMindError):
    logger.exception("Unhandled ScholarMindError")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
