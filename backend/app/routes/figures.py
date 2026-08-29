from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import FIGURES_DIR
from app.exceptions import EmptyQuestionError, GeminiRateLimitError, GeminiUnavailableError
from app.models.schemas import FigureAnswerResponse, FigureQuestionRequest
from app.rag.rag_pipeline import RAGPipeline
from app.storage.paper_store import PaperStore

router = APIRouter(prefix="/api/papers", tags=["figures"])
_pipeline = RAGPipeline()

_MIME_BY_EXT = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}


def _find_figure(paper_id: str, figure_id: str) -> dict:
    record = PaperStore.get(paper_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No paper found with that id.")

    figure = next((f for f in record.get("figures", []) if f["id"] == figure_id), None)
    if figure is None:
        raise HTTPException(status_code=404, detail="No figure found with that id.")
    return figure


@router.get("/{paper_id}/figures/{figure_id}")
def get_figure_image(paper_id: str, figure_id: str):
    figure = _find_figure(paper_id, figure_id)
    path = FIGURES_DIR / paper_id / f"{figure_id}.{figure['ext']}"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Figure image file is missing.")
    return FileResponse(path, media_type=_MIME_BY_EXT.get(figure["ext"], "application/octet-stream"))


@router.post("/{paper_id}/figures/{figure_id}/ask", response_model=FigureAnswerResponse)
def ask_about_figure(paper_id: str, figure_id: str, body: FigureQuestionRequest):
    figure = _find_figure(paper_id, figure_id)
    path = FIGURES_DIR / paper_id / f"{figure_id}.{figure['ext']}"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Figure image file is missing.")

    mime_type = _MIME_BY_EXT.get(figure["ext"], "image/png")
    try:
        answer = _pipeline.ask_about_figure(figure.get("caption", ""), path.read_bytes(), mime_type, body.question)
    except EmptyQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except GeminiUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return FigureAnswerResponse(answer=answer)
