"""Semantic search across the whole library, not just one paper.

Reuses the exact same embeddings + FAISS infra as per-paper chat: embed
the query once, retrieve a handful of chunks from every ready paper's own
index, then merge and re-rank by score. Fine at personal-library scale
(tens of papers) - it doesn't need a shared index across papers.
"""
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.storage.paper_store import PaperStore

PER_PAPER_TOP_K = 3


def search_library(query: str, limit: int = 10) -> list[dict]:
    query = (query or "").strip()
    if not query:
        return []

    query_embedding = EmbeddingGenerator.embed_query(query)

    results: list[dict] = []
    for record in PaperStore.list_all():
        if record["status"] != "ready":
            continue
        matches = VectorStore.query(record["id"], query_embedding, PER_PAPER_TOP_K)
        for match in matches:
            results.append(
                {
                    "paper_id": record["id"],
                    "paper_title": record["title"] or record["filename"],
                    "section_title": match["section_title"],
                    "page_start": match["page_start"],
                    "page_end": match["page_end"],
                    "score": round(match["score"], 4),
                    "preview": match["text"][:280],
                }
            )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]
