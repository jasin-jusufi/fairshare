from app.application.errors import ReceiptUnreadableError
from app.application.lookup import require_household
from app.application.ports.receipt_parser import ReceiptParser
from app.application.ports.repositories import HouseholdRepository
from app.domain.errors import ValidationError
from app.domain.receipt import ReceiptSuggestion

MAX_IMAGE_BYTES = 5 * 1024 * 1024
SIGNATURES = {b"\xff\xd8\xff": "image/jpeg", b"\x89PNG\r\n\x1a\n": "image/png"}


def media_type_of(image: bytes) -> str | None:
    """Detects JPEG and PNG by their file signature, whatever the client claims."""
    return next((t for signature, t in SIGNATURES.items() if image.startswith(signature)), None)


class ReceiptService:
    def __init__(self, households: HouseholdRepository, parser: ReceiptParser) -> None:
        self._households = households
        self._parser = parser

    def suggest(self, household_id: int, image: bytes) -> ReceiptSuggestion:
        require_household(self._households, household_id)
        if len(image) > MAX_IMAGE_BYTES:
            raise ValidationError("The image must not be larger than 5 MB")
        media_type = media_type_of(image)
        if media_type is None:
            raise ValidationError("Only JPEG and PNG images are supported")
        reading = self._parser.parse(image, media_type)
        if reading.total_cents is None:
            raise ReceiptUnreadableError("No amount found on the receipt")
        try:
            return ReceiptSuggestion(reading.merchant or "", reading.total_cents)
        except ValidationError as error:
            raise ReceiptUnreadableError(f"Receipt could not be read: {error}") from error
