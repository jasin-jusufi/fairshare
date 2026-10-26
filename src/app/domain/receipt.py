from dataclasses import dataclass

from app.domain.errors import ValidationError
from app.domain.expense import MAX_DESCRIPTION_LENGTH
from app.domain.validation import clean_text


@dataclass
class ReceiptSuggestion:
    """Description and amount read from a receipt; pre-fills an expense, never stored."""

    description: str
    amount_cents: int

    def __post_init__(self) -> None:
        self.description = clean_text(self.description, "Description", MAX_DESCRIPTION_LENGTH)
        if self.amount_cents <= 0:
            raise ValidationError("Amount must be positive")
