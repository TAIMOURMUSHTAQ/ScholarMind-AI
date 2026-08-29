from fastapi.testclient import TestClient

from app.main import app
from app.storage import paper_store as paper_store_module

client = TestClient(app)


def test_upload_sanitizes_path_traversal_filename(tmp_path, monkeypatch):
    # Isolate storage: without this the route writes straight into the
    # real backend/data/papers.json and UPLOADS_DIR, leaving permanent
    # ghost paper records behind in the dev database on every test run.
    monkeypatch.setattr(paper_store_module, "PAPER_STORE_PATH", tmp_path / "papers.json")
    monkeypatch.setattr("app.routes.papers.UPLOADS_DIR", tmp_path)
    # Ingestion itself isn't under test here - avoid running the real
    # PDF/embedding pipeline against a fake body.
    monkeypatch.setattr("app.routes.papers.ingest_paper", lambda *a, **k: None)

    response = client.post(
        "/api/papers/upload",
        files={"file": ("../../evil.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["filename"] == "evil.pdf"  # traversal segments stripped

    written = list(tmp_path.glob(f"{data['id']}_*"))
    assert len(written) == 1
    assert written[0].parent.resolve() == tmp_path.resolve()
