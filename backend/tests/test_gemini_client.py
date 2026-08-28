from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import ResourceExhausted

from app.exceptions import GeminiUnavailableError
from app.rag.gemini_client import GeminiClient


def _chunk(text: str):
    chunk = MagicMock()
    chunk.text = text
    return chunk


@patch("app.rag.gemini_client.GEMINI_API_KEY", "fake-key")
@patch("app.rag.gemini_client.genai.GenerativeModel")
def test_chat_stream_retries_before_any_output_is_sent(mock_model_cls):
    session_fail = MagicMock()
    session_fail.send_message.side_effect = ResourceExhausted("rate limited")
    session_ok = MagicMock()
    session_ok.send_message.return_value = [_chunk("Hello"), _chunk(" world")]

    model = MagicMock()
    model.start_chat.side_effect = [session_fail, session_ok]
    mock_model_cls.return_value = model

    with patch("time.sleep"):
        result = "".join(GeminiClient().chat_stream("sys", [], "hi", max_retries=1, base_delay_seconds=0))

    assert result == "Hello world"
    assert model.start_chat.call_count == 2


@patch("app.rag.gemini_client.GEMINI_API_KEY", "fake-key")
@patch("app.rag.gemini_client.genai.GenerativeModel")
def test_chat_stream_does_not_retry_once_output_has_started(mock_model_cls):
    """A dropped connection mid-stream must not silently restart the
    generation - that would duplicate/garble what the client already
    rendered. It should raise, preserving what already streamed."""

    def failing_stream():
        yield _chunk("Hello")
        raise ResourceExhausted("dropped mid-stream")

    session = MagicMock()
    session.send_message.return_value = failing_stream()
    model = MagicMock()
    model.start_chat.return_value = session
    mock_model_cls.return_value = model

    received = []
    with pytest.raises(GeminiUnavailableError, match="dropped partway"):
        for delta in GeminiClient().chat_stream("sys", [], "hi", max_retries=3, base_delay_seconds=0):
            received.append(delta)

    assert received == ["Hello"]
    assert model.start_chat.call_count == 1
