import numpy as np

from sentence_transformers import SentenceTransformer


class SemanticSearcher:
    """
    Performs semantic search over paper chunks.
    """

    def __init__(self, vector_store, chunks):

        self.vector_store = vector_store

        self.chunks = chunks

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def search(
        self,
        query,
        top_k=5
    ):

        query_vector = self.model.encode(
            query,
            convert_to_numpy=True
        ).astype("float32")

        distances, indices = self.vector_store.index.search(
            np.array([query_vector]),
            top_k
        )

        results = []

        for score, idx in zip(
            distances[0],
            indices[0]
        ):

            if idx == -1:
                continue

            results.append(

                (
                    self.chunks[idx],
                    score
                )

            )

        return results