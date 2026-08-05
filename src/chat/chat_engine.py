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
        semantic_searcher,
        paper=None
    ):

        self.retriever = Retriever(
            semantic_searcher
        )

        self.llm = GeminiClient()
        self.paper = paper

    def _paper_fact_answer(self, question: str):
        if self.paper is None:
            return None

        lowered = question.lower()

        if "title" in lowered:
            return self.paper.title or "I couldn't find this information in the paper."

        if "author" in lowered or "who wrote" in lowered:
            if self.paper.authors:
                return ", ".join(self.paper.authors)
            return "I couldn't find this information in the paper."

        if "abstract" in lowered or "summary" in lowered:
            return self.paper.abstract or "I couldn't find this information in the paper."

        if "doi" in lowered:
            doi = getattr(self.paper.metadata, "doi", "")
            return doi or "I couldn't find this information in the paper."

        if "year" in lowered or "published" in lowered:
            year = getattr(self.paper.metadata, "year", "")
            return str(year) if year else "I couldn't find this information in the paper."

        if "venue" in lowered or "conference" in lowered or "journal" in lowered:
            venue = getattr(self.paper.metadata, "venue", "")
            return venue or "I couldn't find this information in the paper."

        if "keyword" in lowered:
            keywords = getattr(self.paper.metadata, "keywords", [])
            if keywords:
                return ", ".join(keywords)
            return "I couldn't find this information in the paper."

        if "reference" in lowered or "references" in lowered:
            if self.paper.references:
                return f"The paper contains {len(self.paper.references)} references."
            return "I couldn't find this information in the paper."

        if "citation" in lowered or "citations" in lowered:
            if self.paper.citations:
                return f"The paper contains {len(self.paper.citations)} citations."
            return "I couldn't find this information in the paper."

        return None

    def _fallback_answer(self, question: str, ranked_chunks):

        fact_answer = self._paper_fact_answer(question)
        if fact_answer:
            return fact_answer

        if not ranked_chunks:
            return "I couldn't find this information in the paper."

        highlights = []
        for index, (chunk, score) in enumerate(ranked_chunks[:3], start=1):
            snippet = chunk.text[:220].strip().replace("\n", " ")
            highlights.append(
                f"Source {index} ({chunk.title}) [{score:.3f}]: {snippet}"
            )

        return (
            f"I couldn't generate a model answer for: {question}\n\n"
            + "\n".join(highlights)
        )

    def ask(
        self,
        question: str,
        top_k: int = 5
    ):

        ranked_chunks = self.retriever.retrieve_ranked(
            question,
            top_k
        )

        chunks = [chunk for chunk, _score in ranked_chunks]

        context = ContextBuilder.build(
            chunks
        )

        prompt = PromptBuilder.build(
            question,
            context
        )

        try:
            answer = self.llm.generate(
                prompt
            )
        except Exception:
            answer = self._fallback_answer(
                question,
                ranked_chunks
            )

        return {

            "question": question,

            "answer": answer,

            "chunks": chunks,

            "sources": [
                {
                    "rank": index,
                    "title": chunk.title,
                    "score": score,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "preview": chunk.text[:220]
                }
                for index, (chunk, score) in enumerate(ranked_chunks, start=1)
            ],

            "context": context
        }