"""Connects the library to the outside world: related-paper lookup via the
free Semantic Scholar Graph API, and importing a paper directly from arXiv
by id/URL instead of requiring a local file.

Both are best-effort against a third-party service: network failures,
timeouts, or rate limits degrade to an empty result (related papers) or a
clear user-facing error (arXiv import), never a crash.
"""
import re

import httpx

from app.exceptions import ScholarMindError
from app.logger import logger

SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}.pdf"
REQUEST_TIMEOUT_SECONDS = 10

# e.g. "2301.12345", "2301.12345v2", "hep-th/9901001"
_ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5}(v\d+)?|[a-z-]+/\d{7}(v\d+)?)", re.IGNORECASE)


class ArxivImportError(ScholarMindError):
    pass


def find_related_papers(title: str, limit: int = 5) -> list[dict]:
    """Best-effort: returns [] on any failure rather than raising, since
    this is a nice-to-have panel, not core functionality."""
    title = (title or "").strip()
    if not title:
        return []

    try:
        response = httpx.get(
            SEMANTIC_SCHOLAR_SEARCH_URL,
            params={
                "query": title,
                "limit": limit,
                "fields": "title,abstract,year,authors,url,externalIds",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        papers = response.json().get("data", [])
    except Exception:
        logger.warning("Semantic Scholar lookup failed for title %r", title, exc_info=True)
        return []

    results = []
    for paper in papers:
        # Skip the paper matching itself back (same title, common when the
        # uploaded paper is itself indexed on Semantic Scholar).
        if paper.get("title", "").strip().lower() == title.lower():
            continue
        results.append(
            {
                "title": paper.get("title") or "Untitled",
                "abstract": (paper.get("abstract") or "")[:400],
                "year": paper.get("year"),
                "authors": [a.get("name", "") for a in (paper.get("authors") or [])][:5],
                "url": paper.get("url") or "",
            }
        )
    return results


def extract_arxiv_id(id_or_url: str) -> str:
    """Pulls a bare arXiv id out of either a bare id or any arxiv.org URL
    shape, never trusting a user-supplied host - the download always goes
    to the fixed arxiv.org PDF endpoint we build ourselves, so a malicious
    "URL" can't redirect the fetch anywhere else (no SSRF via this field)."""
    match = _ARXIV_ID_PATTERN.search(id_or_url or "")
    if not match:
        raise ArxivImportError(f"Couldn't find a valid arXiv id in '{id_or_url}'.")
    return match.group(1)


def download_arxiv_pdf(id_or_url: str) -> tuple[str, bytes]:
    """Returns (arxiv_id, pdf_bytes)."""
    arxiv_id = extract_arxiv_id(id_or_url)
    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)

    try:
        response = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ArxivImportError(f"arXiv returned an error for '{arxiv_id}' (is the id correct?): {exc}") from exc
    except Exception as exc:
        raise ArxivImportError(f"Could not reach arXiv to download '{arxiv_id}': {exc}") from exc

    if not response.content or response.headers.get("content-type", "").split(";")[0] != "application/pdf":
        raise ArxivImportError(f"arXiv did not return a PDF for '{arxiv_id}'.")

    return arxiv_id, response.content
