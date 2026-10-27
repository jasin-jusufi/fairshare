import pytest

from app.application.errors import ParserUnavailableError
from app.application.ports.receipt_parser import ReceiptReading
from app.infrastructure.receipt_parsers import (
    FakeReceiptParser,
    UnavailableReceiptParser,
    make_receipt_parser,
)


def test_fake_parser_returns_the_demo_reading_for_any_image() -> None:
    assert FakeReceiptParser().parse(b"anything", "image/png") == ReceiptReading("Migros", 2350)


def test_unavailable_parser_explains_how_to_switch_it_on() -> None:
    with pytest.raises(ParserUnavailableError, match="RECEIPT_PARSER"):
        UnavailableReceiptParser().parse(b"", "image/png")


@pytest.mark.parametrize(
    ("mode", "parser_type"), [("fake", FakeReceiptParser), ("none", UnavailableReceiptParser)]
)
def test_make_receipt_parser(mode: str, parser_type: type) -> None:
    assert isinstance(make_receipt_parser(mode), parser_type)


def test_unknown_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="RECEIPT_PARSER"):
        make_receipt_parser("gpt")
