from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.storage import paper_store as paper_store_module
from app.storage.paper_store import PaperStore

client = TestClient(app)


def _isolated_paper(tmp_path, monkeypatch):
    monkeypatch.setattr(paper_store_module, "PAPER_STORE_PATH", tmp_path / "papers.json")
    PaperStore.create_placeholder("paper-1", "paper.pdf")
    data = paper_store_module._read_all()
    data["paper-1"]["title"] = "My Paper"
    data["paper-1"]["status"] = "ready"
    paper_store_module._write_all(data)


@patch("app.routes.papers.find_related_papers", return_value=[{"title": "A Related Paper", "abstract": "", "year": 2020, "authors": [], "url": ""}])
def test_related_papers_are_cached_after_a_successful_lookup(mock_find, tmp_path, monkeypatch):
    _isolated_paper(tmp_path, monkeypatch)

    first = client.get("/api/papers/paper-1/related")
    second = client.get("/api/papers/paper-1/related")

    assert first.json() == second.json()
    assert mock_find.call_count == 1  # second call served from cache


@patch("app.routes.papers.find_related_papers", return_value=[])
def test_empty_related_result_is_not_cached_so_it_retries(mock_find, tmp_path, monkeypatch):
    _isolated_paper(tmp_path, monkeypatch)

    client.get("/api/papers/paper-1/related")
    client.get("/api/papers/paper-1/related")

    assert mock_find.call_count == 2  # not cached - retried both times
