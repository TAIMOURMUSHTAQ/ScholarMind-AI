from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.storage import paper_store as paper_store_module
from app.storage.paper_store import PaperStore

client = TestClient(app)


def _setup_paper_with_figure(tmp_path, monkeypatch):
    monkeypatch.setattr(paper_store_module, "PAPER_STORE_PATH", tmp_path / "papers.json")
    monkeypatch.setattr("app.routes.figures.FIGURES_DIR", tmp_path)

    PaperStore.create_placeholder("paper-1", "paper.pdf")
    PaperStore.set_figures("paper-1", [{"id": "0", "page": 0, "ext": "png", "caption": "Figure 1: test"}])

    figure_dir = tmp_path / "paper-1"
    figure_dir.mkdir()
    (figure_dir / "0.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")


def test_get_figure_image_returns_file(tmp_path, monkeypatch):
    _setup_paper_with_figure(tmp_path, monkeypatch)

    response = client.get("/api/papers/paper-1/figures/0")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_get_unknown_figure_returns_404(tmp_path, monkeypatch):
    _setup_paper_with_figure(tmp_path, monkeypatch)

    response = client.get("/api/papers/paper-1/figures/does-not-exist")

    assert response.status_code == 404


@patch("app.routes.figures.RAGPipeline.ask_about_figure", return_value="It shows a bar chart.")
def test_ask_about_figure_returns_answer(mock_ask, tmp_path, monkeypatch):
    _setup_paper_with_figure(tmp_path, monkeypatch)

    response = client.post("/api/papers/paper-1/figures/0/ask", json={"question": "What does this show?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "It shows a bar chart."
