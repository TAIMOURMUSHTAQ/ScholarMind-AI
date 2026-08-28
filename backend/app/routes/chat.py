from fastapi import APIRouter, HTTPException

from app.exceptions import EmptyQuestionError, GeminiRateLimitError, GeminiUnavailableError
from app.models.schemas import ChatRequest, ChatResponse, ChatTurnOut
from app.rag.conversation_memory import ConversationMemory
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


@router.post("/{paper_id}/chat", response_model=ChatResponse)
def chat_with_paper(paper_id: str, body: ChatRequest):
    _require_ready_paper(paper_id)
    try:
        result = _pipeline.ask(paper_id, body.question, body.top_k)
    except EmptyQuestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except GeminiUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(**result)


@router.get("/{paper_id}/chat/history", response_model=list[ChatTurnOut])
def get_chat_history(paper_id: str):
    _require_ready_paper(paper_id)
    return ConversationMemory.get_turns(paper_id)


@router.delete("/{paper_id}/chat", status_code=204)
def clear_chat_history(paper_id: str):
    _require_ready_paper(paper_id)
    ConversationMemory.clear(paper_id)
