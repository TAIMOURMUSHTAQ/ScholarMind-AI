from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """
    Generates vector embeddings for every chunk.
    """

    _model = None

    @classmethod
    def load_model(cls):
        """
        Lazy-load the embedding model only once.
        """
        if cls._model is None:
            cls._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        return cls._model

    @classmethod
    def generate(cls, chunks):
        """
        Adds an embedding vector to every chunk.
        """

        model = cls.load_model()

        for chunk in chunks:

            chunk.embedding = model.encode(
                chunk.text,
                convert_to_numpy=True
            ).tolist()

        return chunks