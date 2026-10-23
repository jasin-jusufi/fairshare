from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.errors import ValidationError
from app.domain.validation import clean_text

MAX_DESCRIPTION_LENGTH = 120


class SplitMethod(StrEnum):
    EQUAL = "equal"
    PERCENT = "percent"
    SHARES = "shares"


@dataclass
class ExpenseShare:
    member_id: int
    amount_cents: int
    id: int | None = None


def split_amount(
    amount_cents: int, method: SplitMethod, weights: dict[int, int]
) -> list[ExpenseShare]:
    """Split an amount by weights; leftover cents go to the largest remainders (ADR-004)."""
    if amount_cents <= 0:
        raise ValidationError("Amount must be positive")
    if not weights:
        raise ValidationError("At least one participant is required")
    if method is SplitMethod.EQUAL:
        weights = dict.fromkeys(weights, 1)
    if any(weight <= 0 for weight in weights.values()):
        raise ValidationError("Weights must be positive")
    total = sum(weights.values())
    if method is SplitMethod.PERCENT and total != 100:
        raise ValidationError("Percentages must sum to 100")

    amounts = {member: amount_cents * weight // total for member, weight in weights.items()}
    remainders = {member: amount_cents * weight % total for member, weight in weights.items()}
    leftover = amount_cents - sum(amounts.values())
    for member in sorted(weights, key=lambda m: -remainders[m])[:leftover]:
        amounts[member] += 1
    return [ExpenseShare(member_id=member, amount_cents=amounts[member]) for member in weights]


@dataclass
class Expense:
    household_id: int
    payer_id: int
    description: str
    amount_cents: int
    method: SplitMethod
    shares: list[ExpenseShare]
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.description = clean_text(self.description, "Description", MAX_DESCRIPTION_LENGTH)
        if self.amount_cents <= 0:
            raise ValidationError("Amount must be positive")
        if not self.shares:
            raise ValidationError("At least one participant is required")
        if len(self.participant_ids()) != len(self.shares):
            raise ValidationError("Participants must be unique")
        if any(share.amount_cents < 0 for share in self.shares):
            raise ValidationError("Shares must not be negative")
        if sum(share.amount_cents for share in self.shares) != self.amount_cents:
            raise ValidationError("Shares must sum to the expense amount")

    def participant_ids(self) -> set[int]:
        return {share.member_id for share in self.shares}
