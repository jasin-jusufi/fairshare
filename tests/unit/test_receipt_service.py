import pytest

from app.application.errors import NotFoundError, ParserUnavailableError, ReceiptUnreadableError
from app.application.ports.receipt_parser import ReceiptReading
from app.application.receipt_service import MAX_IMAGE_BYTES, ReceiptService
from app.domain.errors import ValidationError
from app.domain.household import Household
from app.domain.receipt import ReceiptSuggestion

from .fakes import InMemoryHouseholdRepository, StubReceiptParser

PNG = b"\x89PNG\r\n\x1a\n" + bytes(8)
JPEG = b"\xff\xd8\xff" + bytes(8)
MIGROS = ReceiptReading("Migros", 2350)


def make(
    result: ReceiptReading | Exception = MIGROS,
) -> tuple[ReceiptService, StubReceiptParser]:
    households = InMemoryHouseholdRepository()
    households.add(Household(name="Flat"))
    parser = StubReceiptParser(result)
    return ReceiptService(households, parser), parser


@pytest.mark.parametrize(("image", "media_type"), [(PNG, "image/png"), (JPEG, "image/jpeg")])
def test_suggestion_comes_from_the_parser(image: bytes, media_type: str) -> None:
    service, parser = make()
    assert service.suggest(1, image) == ReceiptSuggestion("Migros", 2350)
    assert parser.calls == [(image, media_type)]


def test_unknown_household_is_not_parsed() -> None:
    service, parser = make()
    with pytest.raises(NotFoundError):
        service.suggest(2, PNG)
    assert parser.calls == []


@pytest.mark.parametrize(
    "image", [b"", b"%PDF-1.7", b"GIF89a", PNG[:4]], ids=["empty", "pdf", "gif", "cut-off-png"]
)
def test_only_jpeg_and_png_are_parsed(image: bytes) -> None:
    service, parser = make()
    with pytest.raises(ValidationError):
        service.suggest(1, image)
    assert parser.calls == []


def test_images_up_to_5_mb_are_accepted() -> None:
    service, _ = make()
    image = PNG + bytes(MAX_IMAGE_BYTES - len(PNG))
    assert MAX_IMAGE_BYTES == 5 * 1024 * 1024
    assert service.suggest(1, image).amount_cents == 2350
    with pytest.raises(ValidationError):
        service.suggest(1, image + b"\x00")


@pytest.mark.parametrize(
    "reading",
    [
        ReceiptReading("Migros", None),
        ReceiptReading(None, 2350),
        ReceiptReading("  ", 2350),
        ReceiptReading("x" * 121, 2350),
        ReceiptReading("Migros", 0),
    ],
    ids=["no-amount", "no-merchant", "blank-merchant", "merchant-too-long", "zero-amount"],
)
def test_unusable_readings_are_unreadable(reading: ReceiptReading) -> None:
    service, _ = make(reading)
    with pytest.raises(ReceiptUnreadableError):
        service.suggest(1, PNG)


def test_unavailable_parser_is_passed_on() -> None:
    service, _ = make(ParserUnavailableError("switched off"))
    with pytest.raises(ParserUnavailableError):
        service.suggest(1, PNG)
