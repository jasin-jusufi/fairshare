import pytest

from app.infrastructure.config import database_url, normalize_database_url, receipt_parser_mode


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("sqlite:///./x.db", "sqlite:///./x.db"),
    ],
)
def test_normalize_database_url(url: str, expected: str) -> None:
    assert normalize_database_url(url) == expected


def test_database_url_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://render/db")
    assert database_url() == "postgresql+psycopg://render/db"
    monkeypatch.delenv("DATABASE_URL")
    assert database_url() == "sqlite:///./fairshare.db"


def test_receipt_parser_mode_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RECEIPT_PARSER", raising=False)
    assert receipt_parser_mode() == "none"
    monkeypatch.setenv("RECEIPT_PARSER", " Fake ")
    assert receipt_parser_mode() == "fake"
