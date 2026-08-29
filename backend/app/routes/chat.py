import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse

from app.exceptions import EmptyQuestionError, GeminiRateLimitError, GeminiUnavailableError
from app.models.schemas import ChatRequest, ChatResponse, ChatTurnOut
from app.rag.conversation_memory import ConversationMemory
from app.rag.export import build_markdown, build_pdf
from app.rag.rag_pipeline import RAGPipeline
from app.storage.paper_store import PaperStore

router = APIRouter(prefix="/api/papers", tags=["chat"])
_pipeline = RAGPipeline()


def _require_ready_paper(paper_id: str) -> dict:
    record = PaperStore.get(paper_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No paper found with that id.")
    if record["status"] == "processing":
        raise HTTPException(status_code=409, detail="This paper is still being processed. Try again shortly.")
    if record["status"] == "failed":
        raise HTTPException(
            status_code=422,
            detail=f"This paper failed to process: {record.get('error_message', 'unknown error')}",
        )
    return record


def _sse_stream(sources: list[dict], token_generator, question: str):
    yield f"event: sources\ndata: {json.dumps(sources)}\n\n"
    chunks: list[str] = []
    try:
        for delta in token_generator:
            chunks.append(delta)
            yield f"event: delta\ndata: {json.dumps({'text': delta})}\n\n"
        followups = RAGPipeline.suggest_followups(question, "".join(chunks))
        yield f"event: followups\ndata: {json.dumps(followups)}\n\n"
        yield "event: done\ndata: {}\n\n"
    except (GeminiRateLimitError, GeminiUnavailableError) as exc:
        yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"


@router.post("/{paper_id}/chat", response_model=ChatResponse)
def chat_with_paper(paper_id: str, body: ChatRequest):
    _require_ready_paper(paper_id)
    try:
        result = _pipeline.ask(paper_id, body.question, body.top_k, body.reading_level)
    except EmptyQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except GeminiUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(**result)


@router.post("/{paper_id}/chat/stream")
def chat_with_paper_stream(paper_id: str, body: ChatRequest):
    _require_ready_paper(paper_id)
    try:
        sources, token_generator = _pipeline.ask_stream(paper_id, body.question, body.top_k, body.reading_level)
    except EmptyQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StreamingResponse(_sse_stream(sources, token_generator, body.question), media_type="text/event-stream")


@router.get("/{paper_id}/chat/history", response_model=list[ChatTurnOut])
def get_chat_history(paper_id: str):
    _require_ready_paper(paper_id)
    return ConversationMemory.get_turns(paper_id)


@router.delete("/{paper_id}/chat", status_code=204)
def clear_chat_history(paper_id: str):
    _require_ready_paper(paper_id)
    ConversationMemory.clear(paper_id)


@router.get("/{paper_id}/chat/export")
def export_chat(paper_id: str, format: str = Query("markdown", pattern="^(markdown|pdf)$")):
    record = _require_ready_paper(paper_id)
    turns = ConversationMemory.get_turns(paper_id)
    title = record["title"] or record["filename"]

    if format == "pdf":
        content = build_pdf(title, turns)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{paper_id}-chat.pdf"'},
        )

    content = build_markdown(title, turns)
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{paper_id}-chat.md"'},
    )
