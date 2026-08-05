from src.retrieval.retriever import Retriever

from src.qa.context_builder import ContextBuilder

from src.qa.prompt_builder import PromptBuilder

from src.llm.gemini_client import GeminiClient


class ChatEngine:

    """
    Complete ScholarMind AI pipeline.
    """

    def __init__(
        self,
        semantic_searcher
    ):

        self.retriever = Retriever(
            semantic_searcher
        )

        self.llm = GeminiClient()

    def ask(
        self,
        question: str,
        top_k: int = 5
    ):

        chunks = self.retriever.retrieve(
            question,
            top_k
        )

        context = ContextBuilder.build(
            chunks
        )

        prompt = PromptBuilder.build(
            question,
            context
        )

        answer = self.llm.generate(
            prompt
        )

        return {

            "question": question,

            "answer": answer,

            "chunks": chunks,

            "context": context
        }