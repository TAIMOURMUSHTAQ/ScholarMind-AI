"""Local sentence-transformers embeddings.

Why local instead of Gemini's embedding endpoint: embeddings are generated
per-chunk at *upload* time (potentially dozens per paper) and again per
*question* at chat time. Running that through a free-tier API would burn
the same quota budget the chat completions need, and hit rate limits fast
on anything but a toy paper. `all-MiniLM-L6-v2` is small (~80MB), fast on
CPU, runs fully offline, and its 384-dim vectors are more than adequate for
single-paper / small-library semantic search.
"""
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL


class EmbeddingGenerator:
    _model: SentenceTransformer | None = None

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            cls._model = SentenceTransformer(EMBEDDING_MODEL)
        return cls._model

    @classmethod
    def embed_texts(cls, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = cls._get_model()
        vectors = model.encode(texts, convert_to_numpy=True, batch_size=32, show_progress_bar=False)
        return vectors.tolist()

    @classmethod
    def embed_query(cls, text: str) -> list[float]:
        return cls._get_model().encode(text, convert_to_numpy=True).tolist()
