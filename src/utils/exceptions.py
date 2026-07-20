"""
Custom Exceptions for ScholarMind AI
"""


class ScholarMindError(Exception):
    """Base exception for the project."""
    pass


class InvalidPDFError(ScholarMindError):
    """Raised when the PDF cannot be opened."""
    pass


class FileNotFoundErrorSM(ScholarMindError):
    """Raised when the file path does not exist."""
    pass