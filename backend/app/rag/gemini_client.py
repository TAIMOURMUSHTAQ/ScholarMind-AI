"""Gemini chat client with retry/backoff for the free tier's rate limits.

Free-tier Gemini (whatever GEMINI_MODEL points at, e.g. `gemini-3.6-flash`)
enforces per-minute request quotas. Any real usage will eventually hit a
429. Rather than let that bubble up as an opaque 500, we retry a handful
of times with exponential backoff and only then surface a clear,
actionable error to the API layer.
"""
import json
import time

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError, ResourceExhausted, ServiceUnavailable

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.exceptions import GeminiRateLimitError, GeminiUnavailableError
from app.logger import logger

_RETRYABLE = (ResourceExhausted, ServiceUnavailable)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiClient:
    def __init__(self, model_name: str = GEMINI_MODEL):
        self.model_name = model_name
        self.available = bool(GEMINI_API_KEY)

    def chat(
        self,
        system_prompt: str,
        history: list[dict],
        message: str,
        max_retries: int = 3,
        base_delay_seconds: float = 2.0,
    ) -> str:
        """Send `message` in a chat session seeded with `history`.

        `history` is a list of {"role": "user"|"model", "parts": [text]}.
        """
        if not self.available:
            raise GeminiUnavailableError(
                "GEMINI_API_KEY is not configured. Add it to backend/.env to enable chat "
                "(get a free key at https://aistudio.google.com/apikey)."
            )

        model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(message)
                return (response.text or "").strip()
            except _RETRYABLE as exc:
                last_error = exc
                if attempt < max_retries:
                    delay = base_delay_seconds * (2**attempt)
                    logger.warning(
                        "Gemini call rate-limited/unavailable (attempt %s/%s); retrying in %.1fs",
                        attempt + 1, max_retries, delay,
                    )
                    time.sleep(delay)
            except GoogleAPICallError as exc:
                raise GeminiUnavailableError(f"Gemini API error: {exc}") from exc
            except Exception as exc:
                raise GeminiUnavailableError(f"Unexpected error calling Gemini: {exc}") from exc

        raise GeminiRateLimitError(
            "Gemini's free-tier rate limit was hit and retries were exhausted. "
            "Please wait a minute and try again."
        ) from last_error

    def generate_json(
        self,
        system_prompt: str,
        message: str,
        max_retries: int = 2,
        base_delay_seconds: float = 2.0,
    ):
        """One-shot, non-chat call constrained to JSON output.

        Used for best-effort enrichment (insight cards, tags, follow-up
        suggestions) - callers are expected to treat any exception here as
        "enrichment unavailable" rather than a hard failure, since none of
        it blocks the core chat feature.
        """
        if not self.available:
            raise GeminiUnavailableError("GEMINI_API_KEY is not configured.")

        model = genai.GenerativeModel(
            self.model_name,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json"),
        )

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(message)
                return json.loads(response.text)
            except _RETRYABLE as exc:
                last_error = exc
                if attempt < max_retries:
                    time.sleep(base_delay_seconds * (2**attempt))
            except (GoogleAPICallError, json.JSONDecodeError) as exc:
                raise GeminiUnavailableError(f"Gemini JSON generation failed: {exc}") from exc
            except Exception as exc:
                raise GeminiUnavailableError(f"Unexpected error calling Gemini: {exc}") from exc

        raise GeminiRateLimitError("Gemini's free-tier rate limit was hit and retries were exhausted.") from last_error

    def generate_with_image(
        self,
        system_prompt: str,
        message: str,
        image_bytes: bytes,
        mime_type: str,
        max_retries: int = 3,
        base_delay_seconds: float = 2.0,
    ) -> str:
        """One-shot multimodal call: text + a single inline image."""
        if not self.available:
            raise GeminiUnavailableError(
                "GEMINI_API_KEY is not configured. Add it to backend/.env to enable chat "
                "(get a free key at https://aistudio.google.com/apikey)."
            )

        model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)
        parts = [message, {"mime_type": mime_type, "data": image_bytes}]

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(parts)
                return (response.text or "").strip()
            except _RETRYABLE as exc:
                last_error = exc
                if attempt < max_retries:
                    time.sleep(base_delay_seconds * (2**attempt))
            except GoogleAPICallError as exc:
                raise GeminiUnavailableError(f"Gemini API error: {exc}") from exc
            except Exception as exc:
                raise GeminiUnavailableError(f"Unexpected error calling Gemini: {exc}") from exc

        raise GeminiRateLimitError(
            "Gemini's free-tier rate limit was hit and retries were exhausted. Please wait a minute and try again."
        ) from last_error

    def chat_stream(
        self,
        system_prompt: str,
        history: list[dict],
        message: str,
        max_retries: int = 3,
        base_delay_seconds: float = 2.0,
    ):
        """Like `chat`, but yields text deltas as they arrive.

        Retry/backoff only applies before the first token of an attempt is
        yielded (the common failure mode: a 429 on the initial request).
        Once a token has been sent to the caller it can't be un-sent, so a
        retryable error after that point does NOT restart the stream from
        scratch (which would duplicate/garble what the client already
        rendered) - it raises instead, and the caller keeps whatever
        partial answer streamed in.
        """
        if not self.available:
            raise GeminiUnavailableError(
                "GEMINI_API_KEY is not configured. Add it to backend/.env to enable chat "
                "(get a free key at https://aistudio.google.com/apikey)."
            )

        model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            yielded_any = False
            try:
                chat_session = model.start_chat(history=history)
                response_stream = chat_session.send_message(message, stream=True)
                for chunk in response_stream:
                    if chunk.text:
                        yielded_any = True
                        yield chunk.text
                return
            except _RETRYABLE as exc:
                last_error = exc
                if yielded_any:
                    raise GeminiUnavailableError(
                        "The connection to Gemini dropped partway through the response. "
                        "What generated so far is kept; please ask again to continue."
                    ) from exc
                if attempt < max_retries:
                    delay = base_delay_seconds * (2**attempt)
                    logger.warning(
                        "Gemini stream rate-limited/unavailable before any output (attempt %s/%s); retrying in %.1fs",
                        attempt + 1, max_retries, delay,
                    )
                    time.sleep(delay)
            except GoogleAPICallError as exc:
                if yielded_any:
                    raise GeminiUnavailableError(
                        f"Gemini API error partway through the response: {exc}. "
                        "What generated so far is kept; please ask again to continue."
                    ) from exc
                raise GeminiUnavailableError(f"Gemini API error: {exc}") from exc
            except Exception as exc:
                if yielded_any:
                    raise GeminiUnavailableError(
                        f"Unexpected error partway through the response: {exc}. "
                        "What generated so far is kept; please ask again to continue."
                    ) from exc
                raise GeminiUnavailableError(f"Unexpected error calling Gemini: {exc}") from exc

        raise GeminiRateLimitError(
            "Gemini's free-tier rate limit was hit and retries were exhausted. "
            "Please wait a minute and try again."
        ) from last_error
