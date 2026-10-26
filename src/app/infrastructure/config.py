import os

from dotenv import load_dotenv

load_dotenv()

API_TITLE = "FairShare API"
API_VERSION = "0.1.0"
API_DESCRIPTION = "Shared household expenses, fair settle-up and chore rotation"


def normalize_database_url(url: str) -> str:
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


def database_url() -> str:
    return normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./fairshare.db"))


def receipt_parser_mode() -> str:
    return os.getenv("RECEIPT_PARSER", "none").strip().lower() or "none"


def ollama_url() -> str:
    return os.getenv("OLLAMA_URL", "http://localhost:11434").strip().rstrip("/")


def ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "qwen2.5vl:7b").strip()
