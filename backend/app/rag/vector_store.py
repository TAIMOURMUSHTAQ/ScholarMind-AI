"""FAISS-backed vector store, one index + metadata sidecar per paper.

Originally built on ChromaDB, but `chroma-hnswlib` (Chroma's local HNSW
backend) ships no prebuilt wheel for Python 3.13 on Windows and requires
the MSVC C++ Build Tools to compile from source, which this environment
doesn't have. `faiss-cpu` does publish a matching `cp313-win_amd64` wheel
and is a proven quantity here - the original prototype already used it
successfully on this exact machine. Same "free, local, file-based, no
server" bar as Chroma, just a different backend.

This also fixes the original prototype's bug where `vector_store.save()`
only persisted the raw FAISS index, leaving the reader to assume the
*same* in-memory chunk list, in the *same* order, was still around to
zip back up with search results - silently wrong the moment a process
restarted with a different chunk ordering. Here the index and its
per-vector metadata (chunk text, section, pages) are always written
together in `index_chunks` and always read back together in `query`, so
there's no implicit external dependency to get out of sync.
"""
import json

import faiss
import numpy as np

from app.config import VECTOR_STORE_DIR
from app.models.domain import Chunk


def _index_path(paper_id: str):
    return VECTOR_STORE_DIR / f"{paper_id}.index"


def _meta_path(paper_id: str):
    return VECTOR_STORE_DIR / f"{paper_id}.meta.json"


class VectorStore:
    @staticmethod
    def index_chunks(paper_id: str, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return

        vectors = np.array(embeddings, dtype="float32")
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, str(_index_path(paper_id)))

        metadata = [
            {
                "text": chunk.text,
                "section_title": chunk.section_title,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
            }
            for chunk in chunks
        ]
        _meta_path(paper_id).write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def query(paper_id: str, query_embedding: list[float], top_k: int) -> list[dict]:
        index_path, meta_path = _index_path(paper_id), _meta_path(paper_id)
        if not index_path.exists() or not meta_path.exists():
            return []

        index = faiss.read_index(str(index_path))
        if index.ntotal == 0:
            return []
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))

        query_vector = np.array([query_embedding], dtype="float32")
        distances, indices = index.search(query_vector, min(top_k, index.ntotal))

        matches = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            meta = metadata[idx]
            matches.append(
                {
                    "text": meta["text"],
                    "section_title": meta["section_title"],
                    "page_start": meta["page_start"],
                    "page_end": meta["page_end"],
                    # L2 distance -> an intuitive 0-1-ish relevance score (higher = better).
                    "score": 1.0 / (1.0 + float(distance)),
                }
            )
        return matches

    @staticmethod
    def delete_paper(paper_id: str) -> None:
        _index_path(paper_id).unlink(missing_ok=True)
        _meta_path(paper_id).unlink(missing_ok=True)
