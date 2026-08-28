import pytest

from app.storage import paper_store as paper_store_module
from app.storage.paper_store import PaperStore


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(paper_store_module, "PAPER_STORE_PATH", tmp_path / "papers.json")
    yield


def test_rename_updates_title_and_persists():
    PaperStore.create_placeholder("paper-1", "original.pdf")

    renamed = PaperStore.rename("paper-1", "A Better Title")

    assert renamed["title"] == "A Better Title"
    assert PaperStore.get("paper-1")["title"] == "A Better Title"


def test_rename_unknown_paper_returns_none():
    assert PaperStore.rename("does-not-exist", "New Title") is None
