"""
VectorStore with a safe fallback when faiss is not available.
If faiss is installed, an IndexFlatL2 is used. Otherwise the
embeddings are stored as a numpy array and a simple numpy-based
search is provided.
"""

from pathlib import Path
import numpy as np

# Try to import faiss, but don't crash if it's missing.
try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    faiss = None
    _HAS_FAISS = False


class VectorStore:
    """
    Handles storing and loading vector embeddings and provides a
    consistent search API regardless of whether faiss is available.
    """

    def __init__(self):
        self.index = None
        self._embeddings = None  # numpy array fallback

    def build(self, chunks):
        """
        Build an index (faiss if available) from chunk embeddings.
        """
        embeddings = np.array(
            [chunk.embedding for chunk in chunks],
            dtype="float32"
        )

        if embeddings.size == 0:
            raise ValueError("No embeddings provided to VectorStore.build()")

        self._embeddings = embeddings

        if _HAS_FAISS:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(embeddings)
            return self.index

        # Faiss not available: keep embeddings and use numpy for searches
        self.index = None
        return embeddings

    def save(self, folder):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        if _HAS_FAISS and self.index is not None:
            faiss.write_index(self.index, str(folder / "paper.index"))
        else:
            # Save numpy fallback
            if self._embeddings is None:
                raise ValueError("No embeddings to save")
            np.save(str(folder / "paper_embeddings.npy"), self._embeddings)

    def load(self, folder):
        folder = Path(folder)
        if _HAS_FAISS:
            idx_path = folder / "paper.index"
            if idx_path.exists():
                self.index = faiss.read_index(str(idx_path))
                return self.index

        emb_path = folder / "paper_embeddings.npy"
        if emb_path.exists():
            self._embeddings = np.load(str(emb_path))
            self.index = None
            return self._embeddings

        raise FileNotFoundError("No saved index or embeddings found in folder")

    def search(self, query_vectors, top_k=5):
        """
        Search the index with one or more query vectors.

        Parameters:
        - query_vectors: numpy array shape (n_queries, dim)
        - top_k: number of results to return

        Returns (distances, indices) where distances.shape == (n_queries, top_k)
        and indices.shape == (n_queries, top_k). For numpy fallback, indices are
        integer indices into the saved embeddings.
        """
        query_vectors = np.asarray(query_vectors, dtype="float32")

        if _HAS_FAISS and self.index is not None:
            distances, indices = self.index.search(query_vectors, top_k)
            return distances, indices

        # Numpy fallback: compute L2 distances between query and embeddings
        if self._embeddings is None:
            raise ValueError("VectorStore has no embeddings to search")

        # Efficient L2: (a-b)^2 = a^2 + b^2 - 2ab
        # query_vectors: (q, d), _embeddings: (n, d)
        q = query_vectors
        x = self._embeddings

        # compute squared L2 distances
        q_sq = np.sum(q * q, axis=1, keepdims=True)  # (q,1)
        x_sq = np.sum(x * x, axis=1)  # (n,)
        # inner product
        inner = q.dot(x.T)  # (q,n)
        # broadcast
        dists = q_sq + x_sq[np.newaxis, :] - 2.0 * inner

        # for each query, get top_k smallest distances
        indices = np.argpartition(dists, kth=min(top_k, dists.shape[1]) - 1, axis=1)[:, :top_k]

        # sort the top_k selections
        sorted_idx = np.argsort(dists[np.arange(dists.shape[0])[:, None], indices], axis=1)
        indices = indices[np.arange(indices.shape[0])[:, None], sorted_idx]

        distances = dists[np.arange(dists.shape[0])[:, None], indices]

        return distances, indices