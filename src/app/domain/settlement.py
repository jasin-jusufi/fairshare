from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.errors import ValidationError
from app.domain.expense import Expense


@dataclass
class Settlement:
    household_id: int
    from_member_id: int
    to_member_id: int
    amount_cents: int
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.from_member_id == self.to_member_id:
            raise ValidationError("A member cannot pay themselves")
        if self.amount_cents <= 0:
            raise ValidationError("Amount must be positive")


@dataclass(frozen=True)
class Transfer:
    from_member_id: int
    to_member_id: int
    amount_cents: int


def compute_balances(
    member_ids: Iterable[int], expenses: Iterable[Expense], settlements: Iterable[Settlement]
) -> dict[int, int]:
    """Positive balance: the member is owed money. Negative: the member owes money."""
    balances = dict.fromkeys(member_ids, 0)
    for expense in expenses:
        balances[expense.payer_id] += expense.amount_cents
        for share in expense.shares:
            balances[share.member_id] -= share.amount_cents
    for settlement in settlements:
        balances[settlement.from_member_id] += settlement.amount_cents
        balances[settlement.to_member_id] -= settlement.amount_cents
    return balances


def suggest_transfers(balances: dict[int, int]) -> list[Transfer]:
    """Greedy settle-up: largest debt pays largest credit, at most n-1 transfers (ADR-007)."""
    if sum(balances.values()) != 0:
        raise ValueError("Balances must sum to zero")
    remaining = dict(balances)
    transfers: list[Transfer] = []
    while debtors := [m for m, b in remaining.items() if b < 0]:
        creditors = [m for m, b in remaining.items() if b > 0]
        debtor = min(debtors, key=lambda m: (remaining[m], m))
        creditor = min(creditors, key=lambda m: (-remaining[m], m))
        amount = min(-remaining[debtor], remaining[creditor])
        transfers.append(Transfer(debtor, creditor, amount))
        remaining[debtor] += amount
        remaining[creditor] -= amount
    return transfers
