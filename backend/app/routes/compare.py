from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse

from app.exceptions import EmptyQuestionError, GeminiRateLimitError, GeminiUnavailableError
from app.models.schemas import ChatRequest, ChatResponse, ChatTurnOut
from app.rag.conversation_memory import ConversationMemory
from app.rag.export import build_markdown, build_pdf
from app.rag.rag_pipeline import RAGPipeline, compare_key
from app.routes.chat import _sse_stream
from app.storage.paper_store import PaperStore

router = APIRouter(prefix="/api/compare", tags=["compare"])
_pipeline = RAGPipeline()


def _parse_and_validate(ids: str) -> list[str]:
    paper_ids = [pid for pid in ids.split(",") if pid]
    if len(paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least two papers to compare.")

    for paper_id in paper_ids:
        record = PaperStore.get(paper_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"No paper found with id {paper_id}.")
        if record["status"] == "processing":
            raise HTTPException(status_code=409, detail=f"'{record['title'] or record['filename']}' is still being processed.")
        if record["status"] == "failed":
            raise HTTPException(status_code=422, detail=f"'{record['filename']}' failed to process and can't be compared.")

    return paper_ids


@router.post("/{ids}/chat", response_model=ChatResponse)
def compare_chat(ids: str, body: ChatRequest):
    paper_ids = _parse_and_validate(ids)
    try:
        result = _pipeline.ask_compare(paper_ids, body.question, body.top_k)
    except EmptyQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except GeminiUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(**result)


@router.post("/{ids}/chat/stream")
def compare_chat_stream(ids: str, body: ChatRequest):
    paper_ids = _parse_and_validate(ids)
    try:
        sources, token_generator = _pipeline.ask_compare_stream(paper_ids, body.question, body.top_k)
    except EmptyQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StreamingResponse(_sse_stream(sources, token_generator), media_type="text/event-stream")


@router.get("/{ids}/chat/history", response_model=list[ChatTurnOut])
def compare_chat_history(ids: str):
    paper_ids = _parse_and_validate(ids)
    return ConversationMemory.get_turns(compare_key(paper_ids))


@router.delete("/{ids}/chat", status_code=204)
def compare_clear_chat(ids: str):
    paper_ids = _parse_and_validate(ids)
    ConversationMemory.clear(compare_key(paper_ids))


@router.get("/{ids}/chat/export")
def compare_export_chat(ids: str, format: str = Query("markdown", pattern="^(markdown|pdf)$")):
    paper_ids = _parse_and_validate(ids)
    turns = ConversationMemory.get_turns(compare_key(paper_ids))
    titles = [PaperStore.get(pid)["title"] or PaperStore.get(pid)["filename"] for pid in paper_ids]
    title = " vs ".join(titles)

    if format == "pdf":
        content = build_pdf(title, turns)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="compare-chat.pdf"'},
        )

    content = build_markdown(title, turns)
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="compare-chat.md"'},
    )
