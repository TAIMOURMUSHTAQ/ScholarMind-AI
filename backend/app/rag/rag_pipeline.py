from app.config import DEFAULT_TOP_K
from app.exceptions import EmptyQuestionError
from app.rag.conversation_memory import ConversationMemory
from app.rag.embeddings import EmbeddingGenerator
from app.rag.gemini_client import GeminiClient
from app.rag.vector_store import VectorStore
from app.storage.paper_store import PaperStore

SYSTEM_PROMPT = """You are ScholarMind AI, a research assistant that answers questions about ONE specific paper.

Rules:
1. Answer using ONLY the "Context" passages provided with each question, plus the ongoing conversation.
2. Never invent facts, numbers, or citations that are not in the context.
3. If the answer isn't in the supplied context, say plainly: "I couldn't find this information in the paper."
4. Be concise and direct; use the paper's own terminology.
5. When useful, refer to sources by their number, e.g. "(Source 2)".
"""

COMPARE_SYSTEM_PROMPT = """You are ScholarMind AI, a research assistant comparing MULTIPLE papers.

Rules:
1. Answer using ONLY the "Context" passages provided, each labeled with which paper it came from.
2. Never invent facts, numbers, or citations that are not in the context.
3. If a paper's context doesn't cover something, say so explicitly for that paper rather than guessing.
4. When comparing, structure the answer around the papers being compared and name them explicitly.
5. Refer to sources by their number, e.g. "(Source 2)".
"""


def compare_key(paper_ids: list[str]) -> str:
    """Deterministic conversation-memory key for a set of papers, order-independent."""
    return "compare_" + "_".join(sorted(paper_ids))


def _build_context(matches: list[dict]) -> str:
    if not matches:
        return "(No relevant passages were retrieved from the paper.)"
    parts = []
    for i, match in enumerate(matches, start=1):
        parts.append(
            f"Source {i} - {match['section_title']} (pages {match['page_start']}-{match['page_end']}):\n{match['text']}"
        )
    return "\n\n".join(parts)


def _build_compare_context(matches: list[dict]) -> str:
    if not matches:
        return "(No relevant passages were retrieved from any of the selected papers.)"
    parts = []
    for i, match in enumerate(matches, start=1):
        parts.append(
            f"Source {i} - Paper: {match['paper_title']} - {match['section_title']} "
            f"(pages {match['page_start']}-{match['page_end']}):\n{match['text']}"
        )
    return "\n\n".join(parts)


def _stream_and_persist(gemini: GeminiClient, system_prompt: str, history: list[dict], message: str, memory_key: str, sources: list[dict]):
    """Yield deltas from Gemini, persisting whatever accumulated even if the
    stream errors partway through (see GeminiClient.chat_stream) - so a
    dropped connection doesn't silently discard an otherwise-good partial
    answer from the paper's conversation history."""
    chunks: list[str] = []
    try:
        for delta in gemini.chat_stream(system_prompt, history, message):
            chunks.append(delta)
            yield delta
    finally:
        if chunks:
            ConversationMemory.append_turn(memory_key, "assistant", "".join(chunks), sources)


def _to_sources(matches: list[dict]) -> list[dict]:
    return [
        {
            "rank": i,
            "section_title": m["section_title"],
            "page_start": m["page_start"],
            "page_end": m["page_end"],
            "score": round(m["score"], 4),
            "preview": m["text"][:280],
            **({"paper_title": m["paper_title"]} if "paper_title" in m else {}),
        }
        for i, m in enumerate(matches, start=1)
    ]


class RAGPipeline:
    def __init__(self):
        self.gemini = GeminiClient()

    # ---------------------------------------------------------------- single paper

    def _prepare(self, paper_id: str, question: str, top_k: int):
        question = (question or "").strip()
        if not question:
            raise EmptyQuestionError("Please enter a question.")

        query_embedding = EmbeddingGenerator.embed_query(question)
        matches = VectorStore.query(paper_id, query_embedding, top_k)
        context = _build_context(matches)
        history = ConversationMemory.get_gemini_history(paper_id)
        message = f"Context:\n{context}\n\nQuestion: {question}"
        return question, matches, history, message

    def ask(self, paper_id: str, question: str, top_k: int = DEFAULT_TOP_K) -> dict:
        question, matches, history, message = self._prepare(paper_id, question, top_k)

        answer = self.gemini.chat(SYSTEM_PROMPT, history, message)
        sources = _to_sources(matches)

        ConversationMemory.append_turn(paper_id, "user", question)
        ConversationMemory.append_turn(paper_id, "assistant", answer, sources)

        return {"answer": answer, "sources": sources}

    def ask_stream(self, paper_id: str, question: str, top_k: int = DEFAULT_TOP_K):
        """Returns (sources, token_generator). Sources are ready immediately
        (retrieval already happened); the generator lazily calls Gemini and
        persists the full answer to conversation memory once exhausted."""
        question, matches, history, message = self._prepare(paper_id, question, top_k)
        sources = _to_sources(matches)

        ConversationMemory.append_turn(paper_id, "user", question)
        token_generator = _stream_and_persist(self.gemini, SYSTEM_PROMPT, history, message, paper_id, sources)
        return sources, token_generator

    # ---------------------------------------------------------------- multi-paper compare

    def _prepare_compare(self, paper_ids: list[str], question: str, top_k: int):
        question = (question or "").strip()
        if not question:
            raise EmptyQuestionError("Please enter a question.")

        query_embedding = EmbeddingGenerator.embed_query(question)
        per_paper_top_k = max(2, top_k // max(1, len(paper_ids)))

        all_matches: list[dict] = []
        for paper_id in paper_ids:
            record = PaperStore.get(paper_id)
            title = record["title"] if record else paper_id
            matches = VectorStore.query(paper_id, query_embedding, per_paper_top_k)
            for match in matches:
                match["paper_title"] = title
            all_matches.extend(matches)

        context = _build_compare_context(all_matches)
        key = compare_key(paper_ids)
        history = ConversationMemory.get_gemini_history(key)
        message = f"Context (spanning {len(paper_ids)} papers):\n{context}\n\nQuestion: {question}"
        return question, all_matches, history, message, key

    def ask_compare(self, paper_ids: list[str], question: str, top_k: int = DEFAULT_TOP_K) -> dict:
        question, matches, history, message, key = self._prepare_compare(paper_ids, question, top_k)

        answer = self.gemini.chat(COMPARE_SYSTEM_PROMPT, history, message)
        sources = _to_sources(matches)

        ConversationMemory.append_turn(key, "user", question)
        ConversationMemory.append_turn(key, "assistant", answer, sources)

        return {"answer": answer, "sources": sources}

    def ask_compare_stream(self, paper_ids: list[str], question: str, top_k: int = DEFAULT_TOP_K):
        question, matches, history, message, key = self._prepare_compare(paper_ids, question, top_k)
        sources = _to_sources(matches)

        ConversationMemory.append_turn(key, "user", question)
        token_generator = _stream_and_persist(self.gemini, COMPARE_SYSTEM_PROMPT, history, message, key, sources)
        return sources, token_generator
