"""Environment-driven configuration. No secrets hardcoded — see .env.example."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BACKEND_ROOT = Path(__file__).resolve().parent.parent

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

CHUNK_SIZE_WORDS = int(os.getenv("CHUNK_SIZE_WORDS", "220"))
CHUNK_OVERLAP_WORDS = int(os.getenv("CHUNK_OVERLAP_WORDS", "40"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "6"))

MIN_CHARS_PER_PAGE = float(os.getenv("MIN_CHARS_PER_PAGE", "20"))
"""Below this average, a PDF is treated as scanned/image-only (no extractable text)."""

DATA_DIR = Path(os.getenv("DATA_DIR", str(BACKEND_ROOT / "data")))
UPLOADS_DIR = DATA_DIR / "uploads"
CONVERSATIONS_DIR = DATA_DIR / "conversations"
PAPER_STORE_PATH = DATA_DIR / "papers.json"
VECTOR_STORE_DIR = Path(os.getenv("VECTOR_STORE_DIR", str(BACKEND_ROOT / "vector_store_data")))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "30"))

for directory in (DATA_DIR, UPLOADS_DIR, CONVERSATIONS_DIR, VECTOR_STORE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
