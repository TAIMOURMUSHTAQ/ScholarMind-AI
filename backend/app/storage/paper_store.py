"""JSON-file-backed registry of uploaded papers.

Deliberately not a database: this project has no auth/multi-user need yet
and a single JSON file keeps the "no infra" bar the brief asks for. If
multi-user support is added later, this is the seam to swap for SQLite.
"""
import json
import threading
from datetime import datetime, timezone

from app.config import PAPER_STORE_PATH

_lock = threading.Lock()


def _read_all() -> dict:
    if not PAPER_STORE_PATH.exists():
        return {}
    with _lock:
        return json.loads(PAPER_STORE_PATH.read_text(encoding="utf-8") or "{}")


def _write_all(data: dict) -> None:
    with _lock:
        PAPER_STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class PaperStore:
    @staticmethod
    def create_placeholder(paper_id: str, filename: str) -> dict:
        record = {
            "id": paper_id,
            "filename": filename,
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "status": "processing",
            "error_message": None,
            "title": "",
            "authors": [],
            "abstract": "",
            "metadata": {"doi": "", "year": "", "venue": "", "keywords": []},
            "statistics": {},
            "section_titles": [],
            "num_pages": 0,
            "num_chunks": 0,
            "tags": [],
            "insight_card": None,
            "insight_status": "pending",  # "pending" | "ready" | "unavailable"
            "related_papers": None,  # cached on first /related request
            "figures": [],
        }
        data = _read_all()
        data[paper_id] = record
        _write_all(data)
        return record

    @staticmethod
    def mark_ready(paper_id: str, paper, num_chunks: int) -> None:
        data = _read_all()
        record = data[paper_id]
        record.update(
            status="ready",
            title=paper.title or "Untitled",
            authors=paper.authors,
            abstract=paper.abstract,
            metadata={
                "doi": paper.metadata.doi,
                "year": paper.metadata.year,
                "venue": paper.metadata.venue,
                "keywords": paper.metadata.keywords,
            },
            statistics=paper.statistics,
            section_titles=[s.title for s in paper.sections],
            num_pages=paper.page_count,
            num_chunks=num_chunks,
        )
        data[paper_id] = record
        _write_all(data)

    @staticmethod
    def mark_failed(paper_id: str, error_message: str) -> None:
        data = _read_all()
        if paper_id in data:
            data[paper_id]["status"] = "failed"
            data[paper_id]["error_message"] = error_message
            _write_all(data)

    @staticmethod
    def get(paper_id: str) -> dict | None:
        return _read_all().get(paper_id)

    @staticmethod
    def list_all() -> list[dict]:
        return sorted(_read_all().values(), key=lambda r: r["upload_time"], reverse=True)

    @staticmethod
    def delete(paper_id: str) -> None:
        data = _read_all()
        data.pop(paper_id, None)
        _write_all(data)

    @staticmethod
    def rename(paper_id: str, new_title: str) -> dict | None:
        data = _read_all()
        record = data.get(paper_id)
        if record is None:
            return None
        record["title"] = new_title
        # Related-paper lookups are cached under the old title (often a
        # garbage title extraction misfired on, which is exactly why the
        # user is renaming) - drop the cache so the next view re-searches
        # under the corrected title instead of returning stale results.
        record["related_papers"] = None
        data[paper_id] = record
        _write_all(data)
        return record

    @staticmethod
    def set_insight_card(paper_id: str, card: dict | None) -> None:
        data = _read_all()
        if paper_id in data:
            data[paper_id]["insight_card"] = card
            data[paper_id]["insight_status"] = "ready" if card else "unavailable"
            _write_all(data)

    @staticmethod
    def set_tags(paper_id: str, tags: list[str]) -> None:
        data = _read_all()
        if paper_id in data:
            data[paper_id]["tags"] = tags
            _write_all(data)

    @staticmethod
    def set_related_papers(paper_id: str, related: list[dict]) -> None:
        data = _read_all()
        if paper_id in data:
            data[paper_id]["related_papers"] = related
            _write_all(data)

    @staticmethod
    def set_figures(paper_id: str, figures: list[dict]) -> None:
        data = _read_all()
        if paper_id in data:
            data[paper_id]["figures"] = figures
            _write_all(data)

    @staticmethod
    def all_tags() -> list[str]:
        seen = set()
        for record in _read_all().values():
            seen.update(record.get("tags", []))
        return sorted(seen)
