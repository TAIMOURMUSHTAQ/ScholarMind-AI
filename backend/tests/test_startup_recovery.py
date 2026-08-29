from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.storage import paper_store as paper_store_module
from app.storage.paper_store import PaperStore


def test_resumes_ingestion_for_papers_stuck_processing_with_file_present(tmp_path, monkeypatch):
    monkeypatch.setattr(paper_store_module, "PAPER_STORE_PATH", tmp_path / "papers.json")
    monkeypatch.setattr("app.main.UPLOADS_DIR", tmp_path)

    PaperStore.create_placeholder("stuck-1", "paper.pdf")
    (tmp_path / "stuck-1_paper.pdf").write_bytes(b"%PDF-1.4 fake")

    with patch("app.main.ingest_paper") as mock_ingest, patch("app.main.threading.Thread") as mock_thread:
        with TestClient(app):
            pass
        mock_thread.assert_called_once()
        args = mock_thread.call_args.kwargs["args"]
        assert args[0] == "stuck-1"


def test_marks_failed_when_stuck_and_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(paper_store_module, "PAPER_STORE_PATH", tmp_path / "papers.json")
    monkeypatch.setattr("app.main.UPLOADS_DIR", tmp_path)

    PaperStore.create_placeholder("stuck-2", "missing.pdf")
    # no file written to disk for this one

    with TestClient(app):
        pass

    record = PaperStore.get("stuck-2")
    assert record["status"] == "failed"
