from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReceiptReading:
    """What a parser recognised on a receipt; `None` where it found nothing."""

    merchant: str | None
    total_cents: int | None


class ReceiptParser(Protocol):
    def parse(self, image: bytes, media_type: str) -> ReceiptReading: ...
