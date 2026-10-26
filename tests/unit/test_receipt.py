import pytest

from app.domain.errors import ValidationError
from app.domain.receipt import ReceiptSuggestion


def test_suggestion_trims_description() -> None:
    assert ReceiptSuggestion(description=" Migros ", amount_cents=2350) == ReceiptSuggestion(
        description="Migros", amount_cents=2350
    )


def test_description_of_120_characters_is_allowed() -> None:
    assert len(ReceiptSuggestion(description="x" * 120, amount_cents=1).description) == 120


@pytest.mark.parametrize(
    ("description", "amount"),
    [("", 100), ("   ", 100), ("x" * 121, 100), ("Migros", 0), ("Migros", -1)],
)
def test_suggestion_invariants(description: str, amount: int) -> None:
    with pytest.raises(ValidationError):
        ReceiptSuggestion(description=description, amount_cents=amount)
