import pytest
from app.domain.expense import Expense, ExpenseShare, SplitMethod

from app.domain.errors import ValidationError


def make(**overrides: object) -> Expense:
    values: dict = {
        "household_id": 1,
        "payer_id": 1,
        "description": " Migros ",
        "amount_cents": 1000,
        "method": SplitMethod.EQUAL,
        "shares": [ExpenseShare(member_id=1, amount_cents=500), ExpenseShare(2, 500)],
    }
    values.update(overrides)
    return Expense(**values)


def test_valid_expense_trims_description() -> None:
    assert make().description == "Migros"


def test_participant_ids() -> None:
    assert make().participant_ids() == {1, 2}


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount_cents": 0},
        {"amount_cents": -5},
        {"description": "  "},
        {"description": "x" * 121},
        {"shares": []},
        {"shares": [ExpenseShare(1, 400), ExpenseShare(2, 500)]},
        {"shares": [ExpenseShare(1, 500), ExpenseShare(1, 500)]},
        {"shares": [ExpenseShare(1, 1100), ExpenseShare(2, -100)]},
    ],
)
def test_invariants(overrides: dict) -> None:
    with pytest.raises(ValidationError):
        make(**overrides)
