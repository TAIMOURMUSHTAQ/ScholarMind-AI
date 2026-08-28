"""Per-paper conversation memory, persisted to a small JSON file per paper.

This is what makes chat feel like a conversation instead of single-shot
Q&A: each turn's history is replayed back to Gemini as chat history so
follow-up questions ("what dataset did *they* use for *that*?") resolve
correctly.
"""
import json
import threading

from app.config import CONVERSATIONS_DIR, MAX_HISTORY_TURNS

_lock = threading.Lock()


def _path(paper_id: str):
    return CONVERSATIONS_DIR / f"{paper_id}.json"


class ConversationMemory:
    @staticmethod
    def get_turns(paper_id: str) -> list[dict]:
        """Full turn list for display: [{role, content, sources}]."""
        path = _path(paper_id)
        if not path.exists():
            return []
        with _lock:
            return json.loads(path.read_text(encoding="utf-8"))

    @classmethod
    def append_turn(cls, paper_id: str, role: str, content: str, sources: list[dict] | None = None) -> None:
        turns = cls.get_turns(paper_id)
        turns.append({"role": role, "content": content, "sources": sources or []})
        with _lock:
            _path(paper_id).write_text(json.dumps(turns, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def get_gemini_history(cls, paper_id: str) -> list[dict]:
        """Recent turns formatted for `GenerativeModel.start_chat(history=...)`."""
        turns = cls.get_turns(paper_id)[-(MAX_HISTORY_TURNS * 2) :]
        role_map = {"user": "user", "assistant": "model"}
        return [
            {"role": role_map[t["role"]], "parts": [t["content"]]}
            for t in turns
            if t["role"] in role_map
        ]

    @staticmethod
    def clear(paper_id: str) -> None:
        path = _path(paper_id)
        if path.exists():
            path.unlink()
