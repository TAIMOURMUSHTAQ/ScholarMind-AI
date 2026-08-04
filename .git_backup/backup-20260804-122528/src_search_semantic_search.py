import numpy as np

from sentence_transformers import SentenceTransformer


class SemanticSearcher:
    """
    Performs semantic search over paper chunks.

    Uses the provided VectorStore.search API which may use faiss
    or a numpy fallback. Returns a list of (chunk, score) tuples.
    """

    def __init__(self, vector_store, chunks):
        self.vector_store = vector_store
        self.chunks = chunks
        # lazy-load model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search(self, query, top_k=5):
        query_vector = self.model.encode(
            query,
            convert_to_numpy=True
        ).astype("float32")

        # Use vector_store.search to abstract faiss vs numpy details
        distances, indices = self.vector_store.search(
            np.array([query_vector]),
            top_k=top_k
        )

        results = []

        # distances and indices are (1, top_k) when single query
        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            # score is a distance (L2). Keep it as-is so callers can rank/inspect
            results.append((self.chunks[int(idx)], float(score)))

        return results