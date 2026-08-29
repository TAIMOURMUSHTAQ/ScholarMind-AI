from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.rag.discovery import ArxivImportError, download_arxiv_pdf, extract_arxiv_id, find_related_papers


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2301.12345", "2301.12345"),
        ("https://arxiv.org/abs/2301.12345", "2301.12345"),
        ("https://arxiv.org/pdf/2301.12345v2.pdf", "2301.12345v2"),
        ("hep-th/9901001", "hep-th/9901001"),
    ],
)
def test_extract_arxiv_id_from_various_formats(raw, expected):
    assert extract_arxiv_id(raw) == expected


def test_extract_arxiv_id_rejects_garbage():
    with pytest.raises(ArxivImportError):
        extract_arxiv_id("not an arxiv id at all")


@patch("app.rag.discovery.httpx.get")
def test_find_related_papers_excludes_the_same_title(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "data": [
                {"title": "My Paper", "abstract": "...", "year": 2024, "authors": [], "url": ""},
                {"title": "A Different Paper", "abstract": "...", "year": 2023, "authors": [{"name": "A"}], "url": "http://x"},
            ]
        },
        raise_for_status=lambda: None,
    )

    results = find_related_papers("My Paper")

    assert len(results) == 1
    assert results[0]["title"] == "A Different Paper"


@patch("app.rag.discovery.httpx.get", side_effect=httpx.ConnectTimeout("timed out"))
def test_find_related_papers_degrades_to_empty_list_on_network_failure(mock_get):
    assert find_related_papers("Anything") == []


def test_find_related_papers_with_blank_title_skips_network_call():
    with patch("app.rag.discovery.httpx.get") as mock_get:
        assert find_related_papers("") == []
        mock_get.assert_not_called()


@patch("app.rag.discovery.httpx.get")
def test_download_arxiv_pdf_returns_id_and_bytes(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        content=b"%PDF-1.4 fake",
        headers={"content-type": "application/pdf"},
        raise_for_status=lambda: None,
    )

    arxiv_id, content = download_arxiv_pdf("https://arxiv.org/abs/2301.12345")

    assert arxiv_id == "2301.12345"
    assert content == b"%PDF-1.4 fake"


@patch("app.rag.discovery.httpx.get")
def test_download_arxiv_pdf_rejects_non_pdf_response(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        content=b"<html>not found</html>",
        headers={"content-type": "text/html"},
        raise_for_status=lambda: None,
    )

    with pytest.raises(ArxivImportError):
        download_arxiv_pdf("2301.12345")
