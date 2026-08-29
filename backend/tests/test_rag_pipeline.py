from unittest.mock import patch

import pytest

from app.exceptions import EmptyQuestionError, GeminiUnavailableError
from app.rag.conversation_memory import ConversationMemory
from app.rag.rag_pipeline import RAGPipeline, compare_key


def test_compare_key_is_order_independent():
    assert compare_key(["b", "a"]) == compare_key(["a", "b"])
    assert compare_key(["a", "b"]) == "compare_a_b"


@pytest.fixture(autouse=True)
def clean_conversation(tmp_path, monkeypatch):
    monkeypatch.setattr("app.rag.conversation_memory.CONVERSATIONS_DIR", tmp_path)
    yield


@pytest.fixture(autouse=True)
def no_real_followup_calls(monkeypatch):
    """Follow-up suggestions are a separate best-effort Gemini call - mock
    them everywhere by default so tests that only care about the answer
    itself don't silently hit the real API."""
    monkeypatch.setattr("app.rag.rag_pipeline.RAGPipeline.suggest_followups", staticmethod(lambda q, a: []))
    yield


def test_ask_raises_on_empty_question():
    pipeline = RAGPipeline()
    with pytest.raises(EmptyQuestionError):
        pipeline.ask("paper-1", "   ")


@patch("app.rag.rag_pipeline.VectorStore.query")
@patch("app.rag.rag_pipeline.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.rag_pipeline.GeminiClient.chat")
def test_ask_grounds_answer_in_retrieved_chunks(mock_chat, mock_embed, mock_query):
    mock_query.return_value = [
        {"text": "The dataset used was ImageNet.", "section_title": "Experiments", "page_start": 3, "page_end": 3, "score": 0.9}
    ]
    mock_chat.return_value = "The paper uses ImageNet (Source 1)."

    result = RAGPipeline().ask("paper-1", "What dataset did they use?", top_k=3)

    assert result["answer"] == "The paper uses ImageNet (Source 1)."
    assert result["sources"][0]["section_title"] == "Experiments"

    # Gemini must have been called with the retrieved passage in context, not
    # left to hallucinate.
    _, kwargs = mock_chat.call_args
    called_message = mock_chat.call_args.args[2]
    assert "ImageNet" in called_message


@patch("app.rag.rag_pipeline.VectorStore.query", return_value=[])
@patch("app.rag.rag_pipeline.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.rag_pipeline.GeminiClient.chat")
def test_ask_with_no_matches_still_calls_gemini_with_empty_context_notice(mock_chat, mock_embed, mock_query):
    mock_chat.return_value = "I couldn't find this information in the paper."

    result = RAGPipeline().ask("paper-1", "Unrelated question?", top_k=3)

    assert result["sources"] == []
    called_message = mock_chat.call_args.args[2]
    assert "No relevant passages" in called_message


@patch("app.rag.rag_pipeline.VectorStore.query", return_value=[])
@patch("app.rag.rag_pipeline.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.rag_pipeline.GeminiClient.chat_stream")
def test_ask_stream_persists_partial_answer_when_stream_errors_mid_way(mock_chat_stream, mock_embed, mock_query):
    def failing_stream(*args, **kwargs):
        yield "Partial "
        yield "answer."
        raise GeminiUnavailableError("dropped partway")

    mock_chat_stream.return_value = failing_stream()

    sources, token_generator = RAGPipeline().ask_stream("paper-1", "What dataset?", top_k=3)

    received = []
    with pytest.raises(GeminiUnavailableError):
        for delta in token_generator:
            received.append(delta)

    assert "".join(received) == "Partial answer."

    turns = ConversationMemory.get_turns("paper-1")
    assert turns[-1]["role"] == "assistant"
    assert turns[-1]["content"] == "Partial answer."


@patch("app.rag.rag_pipeline.VectorStore.query", return_value=[])
@patch("app.rag.rag_pipeline.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.rag_pipeline.GeminiClient.chat", return_value="answer")
def test_eli5_reading_level_adds_style_instruction(mock_chat, mock_embed, mock_query):
    RAGPipeline().ask("paper-1", "Explain this", top_k=3, reading_level="eli5")

    system_prompt = mock_chat.call_args.args[0]
    assert "curious beginner" in system_prompt


@patch("app.rag.rag_pipeline.VectorStore.query", return_value=[])
@patch("app.rag.rag_pipeline.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.rag_pipeline.GeminiClient.chat", return_value="answer")
def test_default_reading_level_adds_no_extra_instruction(mock_chat, mock_embed, mock_query):
    RAGPipeline().ask("paper-1", "Explain this", top_k=3)

    system_prompt = mock_chat.call_args.args[0]
    assert system_prompt.strip() == "You are ScholarMind AI, a research assistant that answers questions about ONE specific paper.\n\nRules:\n1. Answer using ONLY the \"Context\" passages provided with each question, plus the ongoing conversation.\n2. Never invent facts, numbers, or citations that are not in the context.\n3. If the answer isn't in the supplied context, say plainly: \"I couldn't find this information in the paper.\"\n4. Be concise and direct; use the paper's own terminology.\n5. When useful, refer to sources by their number, e.g. \"(Source 2)\".".strip()


@patch("app.rag.rag_pipeline.RAGPipeline.suggest_followups", return_value=["What about X?", "How does Y compare?"])
@patch("app.rag.rag_pipeline.VectorStore.query", return_value=[])
@patch("app.rag.rag_pipeline.EmbeddingGenerator.embed_query", return_value=[0.1, 0.2, 0.3])
@patch("app.rag.rag_pipeline.GeminiClient.chat", return_value="answer")
def test_ask_includes_suggested_followups(mock_chat, mock_embed, mock_query, mock_followups):
    result = RAGPipeline().ask("paper-1", "Explain this", top_k=3)
    assert result["followups"] == ["What about X?", "How does Y compare?"]
