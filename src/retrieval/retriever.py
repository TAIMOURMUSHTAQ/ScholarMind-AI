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

        Parameters
        ----------
        query : str
            User query.

        top_k : int
            Number of chunks to return.

        Returns
        -------
        list
            Ranked Chunk objects.
        """

        return self.semantic_searcher.search(
            query=query,
            top_k=top_k
        )

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