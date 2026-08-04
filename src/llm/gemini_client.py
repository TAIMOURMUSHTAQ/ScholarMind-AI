import os

from dotenv import load_dotenv

# The real Gemini client is an optional integration.
# Import it lazily and provide a graceful fallback if the
# environment variable is not set or the package is missing.
try:
    import google.generativeai as genai  # type: ignore
    _HAS_GENAI = True
except Exception:
    genai = None
    _HAS_GENAI = False


class GeminiClient:
    """
    Wrapper around Gemini API. If the GEMINI_API_KEY is missing or the
    google.generativeai package is not installed, use a safe fallback
    that returns a helpful message instead of crashing.
    """

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or not _HAS_GENAI:
            # Operate in offline mode: do not raise. The generate() method
            # will return a friendly message explaining the situation.
            self._online = False
            self._api_key = api_key
            self.model = None
            return

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self._online = True
        self._api_key = api_key

    def generate(self, prompt: str) -> str:
        """
        Generate an answer from the model. If the client is offline,
        return a helpful message that includes the prompt context so the
        user still sees what would have been sent to the model.
        """
        if not self._online:
            message = (
                "Gemini LLM is not available.\n"
                "Two possible reasons:\n"
                "  1) GEMINI_API_KEY is not set in your .env file.\n"
                "  2) google.generativeai package is not installed.\n\n"
                "To enable live LLM responses, set GEMINI_API_KEY and install the"
                " google.generativeai package.\n\n"
                "Prompt that would have been sent to the model:\n\n"
                f"{prompt[:4000]}\n\n"
                "(Prompt truncated)")
            return message

        # Online mode: call the real API
        response = self.model.generate_content(prompt)
        return response.text.strip()