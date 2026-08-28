"""Custom exceptions raised at the pipeline layer, mapped to HTTP responses in main.py."""


class ScholarMindError(Exception):
    """Base exception for the project."""


class InvalidPDFError(ScholarMindError):
    """The uploaded file could not be opened as a PDF (corrupt/malformed/not a PDF)."""


class ScannedPDFError(ScholarMindError):
    """The PDF has no extractable text layer (likely a scanned image)."""


class PaperNotFoundError(ScholarMindError):
    """No paper exists with the given id."""


class EmptyQuestionError(ScholarMindError):
    """The user submitted an empty or whitespace-only question."""


class GeminiRateLimitError(ScholarMindError):
    """Gemini free-tier rate limit was hit even after retries."""


class GeminiUnavailableError(ScholarMindError):
    """Gemini could not be reached, or no API key is configured."""
