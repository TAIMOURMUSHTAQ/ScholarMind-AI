from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import ResourceExhausted

from app.exceptions import GeminiUnavailableError
from app.rag.gemini_client import GeminiClient


@patch("app.rag.gemini_client.GEMINI_API_KEY", "fake-key")
@patch("app.rag.gemini_client.genai.GenerativeModel")
def test_generate_json_parses_response_text(mock_model_cls):
    response = MagicMock()
    response.text = '{"foo": "bar"}'
    model = MagicMock()
    model.generate_content.return_value = response
    mock_model_cls.return_value = model

    result = GeminiClient().generate_json("sys", "message")

    assert result == {"foo": "bar"}


@patch("app.rag.gemini_client.GEMINI_API_KEY", "fake-key")
@patch("app.rag.gemini_client.genai.GenerativeModel")
def test_generate_json_raises_on_invalid_json(mock_model_cls):
    response = MagicMock()
    response.text = "not json"
    model = MagicMock()
    model.generate_content.return_value = response
    mock_model_cls.return_value = model

    with pytest.raises(GeminiUnavailableError):
        GeminiClient().generate_json("sys", "message")


@patch("app.rag.gemini_client.GEMINI_API_KEY", "fake-key")
@patch("app.rag.gemini_client.genai.GenerativeModel")
def test_generate_json_retries_on_rate_limit(mock_model_cls):
    response = MagicMock()
    response.text = "[1, 2, 3]"
    model = MagicMock()
    model.generate_content.side_effect = [ResourceExhausted("busy"), response]
    mock_model_cls.return_value = model

    with patch("time.sleep"):
        result = GeminiClient().generate_json("sys", "message", max_retries=1, base_delay_seconds=0)

    assert result == [1, 2, 3]
    assert model.generate_content.call_count == 2
