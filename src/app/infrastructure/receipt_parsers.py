from collections.abc import Callable

from app.application.errors import ParserUnavailableError
from app.application.ports.receipt_parser import ReceiptParser, ReceiptReading


class FakeReceiptParser:
    """Demo adapter without a model: the same suggestion for every image (ADR-008)."""

    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        return ReceiptReading(merchant="Migros", total_cents=2350)


class UnavailableReceiptParser:
    """Default adapter: receipt scanning is switched off."""

    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        raise ParserUnavailableError(
            "Receipt scanning is switched off. Set RECEIPT_PARSER=fake for the demo."
        )


PARSERS: dict[str, Callable[[], ReceiptParser]] = {
    "fake": FakeReceiptParser,
    "none": UnavailableReceiptParser,
}


def make_receipt_parser(mode: str) -> ReceiptParser:
    if mode not in PARSERS:
        raise ValueError(f"Unknown RECEIPT_PARSER '{mode}', expected one of: {', '.join(PARSERS)}")
    return PARSERS[mode]()
