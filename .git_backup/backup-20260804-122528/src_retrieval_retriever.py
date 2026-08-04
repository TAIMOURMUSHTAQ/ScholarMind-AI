from src.search.semantic_search import SemanticSearcher


class Retriever:
    """
    High-level retrieval interface.

    Responsibilities
    ----------------
    1. Accept a user query.
    2. Perform semantic search.
    3. Return the most relevant chunks.
    """

    def __init__(self, semantic_searcher: SemanticSearcher):
        self.semantic_searcher = semantic_searcher

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ):
        """
        Retrieve the top-k most relevant chunks.

        Returns a plain list of Chunk objects. The underlying
        semantic_searcher may return (chunk, score) tuples; this
        method normalizes that into a list of Chunk objects so
        downstream code doesn't need to unpack tuples.
        """

        results = self.semantic_searcher.search(
            query=query,
            top_k=top_k
        )

        # Normalize results: accept either [(chunk, score), ...]
        # or [chunk, ...] and return [chunk, ...].
        chunks = []
        for item in results:
            if isinstance(item, tuple) or isinstance(item, list):
                if len(item) >= 1:
                    chunks.append(item[0])
            else:
                chunks.append(item)

        return chunks

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5
    ):
        """
        Convert retrieved chunks into one context string.

        This will later be passed to the LLM.
        """

        chunks = self.retrieve(
            query,
            top_k
        )

        context = ""

        for i, chunk in enumerate(chunks, start=1):

            context += (
                f"[Chunk {i}]\n"
                f"{chunk.text}\n\n"
            )

        return context