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
