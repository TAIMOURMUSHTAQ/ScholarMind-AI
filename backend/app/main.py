from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import CORS_ORIGINS
from app.exceptions import InvalidPDFError, PaperNotFoundError, ScannedPDFError, ScholarMindError
from app.logger import logger
from app.routes import chat, papers

app = FastAPI(
    title="ScholarMind AI",
    description="Upload a research paper, get a structured summary, and chat with it - grounded in retrieval, not hallucination.",
    version="2.0.0",
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
