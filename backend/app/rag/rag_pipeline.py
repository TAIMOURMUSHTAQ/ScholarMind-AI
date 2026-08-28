from app.config import DEFAULT_TOP_K
from app.exceptions import EmptyQuestionError
from app.rag.conversation_memory import ConversationMemory
from app.rag.embeddings import EmbeddingGenerator
from app.rag.gemini_client import GeminiClient
from app.rag.vector_store import VectorStore

SYSTEM_PROMPT = """You are ScholarMind AI, a research assistant that answers questions about ONE specific paper.

Rules:
1. Answer using ONLY the "Context" passages provided with each question, plus the ongoing conversation.
2. Never invent facts, numbers, or citations that are not in the context.
3. If the answer isn't in the supplied context, say plainly: "I couldn't find this information in the paper."
4. Be concise and direct; use the paper's own terminology.
5. When useful, refer to sources by their number, e.g. "(Source 2)".
"""


def _build_context(matches: list[dict]) -> str:
    if not matches:
        return "(No relevant passages were retrieved from the paper.)"
    parts = []
    for i, match in enumerate(matches, start=1):
        parts.append(
            f"Source {i} - {match['section_title']} (pages {match['page_start']}-{match['page_end']}):\n{match['text']}"
        )
    return "\n\n".join(parts)


class RAGPipeline:
    def __init__(self):
        self.gemini = GeminiClient()

    def ask(self, paper_id: str, question: str, top_k: int = DEFAULT_TOP_K) -> dict:
        question = (question or "").strip()
        if not question:
            raise EmptyQuestionError("Please enter a question.")

        query_embedding = EmbeddingGenerator.embed_query(question)
        matches = VectorStore.query(paper_id, query_embedding, top_k)
        context = _build_context(matches)

        history = ConversationMemory.get_gemini_history(paper_id)
        message = f"Context:\n{context}\n\nQuestion: {question}"

        answer = self.gemini.chat(SYSTEM_PROMPT, history, message)

        sources = [
            {
                "rank": i,
                "section_title": m["section_title"],
                "page_start": m["page_start"],
                "page_end": m["page_end"],
                "score": round(m["score"], 4),
                "preview": m["text"][:280],
            }
            for i, m in enumerate(matches, start=1)
        ]

        ConversationMemory.append_turn(paper_id, "user", question)
        ConversationMemory.append_turn(paper_id, "assistant", answer, sources)

        return {"answer": answer, "sources": sources}
