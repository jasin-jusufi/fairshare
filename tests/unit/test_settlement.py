import random

import pytest

from app.domain.errors import ValidationError
from app.domain.expense import MAX_AMOUNT_CENTS, Expense, ExpenseShare, SplitMethod
from app.domain.settlement import Settlement, Transfer, compute_balances, suggest_transfers


def expense(payer: int, shares: dict[int, int]) -> Expense:
    return Expense(
        household_id=1,
        payer_id=payer,
        description="x",
        amount_cents=sum(shares.values()),
        method=SplitMethod.SHARES,
        shares=[ExpenseShare(m, a) for m, a in shares.items()],
    )


def test_balances_from_expenses() -> None:
    balances = compute_balances([1, 2, 3], [expense(1, {1: 300, 2: 300, 3: 300})], [])
    assert balances == {1: 600, 2: -300, 3: -300}


def test_balances_include_members_without_activity() -> None:
    assert compute_balances([1, 2], [], []) == {1: 0, 2: 0}


def test_settlement_moves_balance() -> None:
    settlement = Settlement(household_id=1, from_member_id=2, to_member_id=1, amount_cents=300)
    balances = compute_balances([1, 2], [expense(1, {1: 300, 2: 300})], [settlement])
    assert balances == {1: 0, 2: 0}


def test_suggest_transfers_matches_largest_debt_with_largest_credit() -> None:
    transfers = suggest_transfers({1: 600, 2: -100, 3: -500})
    assert transfers == [Transfer(3, 1, 500), Transfer(2, 1, 100)]


def test_suggest_transfers_is_empty_when_balanced() -> None:
    assert suggest_transfers({1: 0, 2: 0}) == []


def test_suggest_transfers_rejects_unbalanced_input() -> None:
    with pytest.raises(ValueError):
        suggest_transfers({1: 100, 2: -50})


def test_ties_are_resolved_by_member_id() -> None:
    assert suggest_transfers({3: -100, 2: -100, 1: 200}) == [
        Transfer(2, 1, 100),
        Transfer(3, 1, 100),
    ]


@pytest.mark.parametrize("seed", range(25))
def test_random_households_settle_with_at_most_n_minus_one_transfers(seed: int) -> None:
    rng = random.Random(seed)
    members = list(range(1, rng.randint(2, 8) + 1))
    balances = {m: rng.randint(-10_000, 10_000) for m in members[:-1]}
    balances[members[-1]] = -sum(balances.values())

    transfers = suggest_transfers(balances)

    assert len(transfers) <= len(members) - 1
    remaining = dict(balances)
    for t in transfers:
        assert t.amount_cents > 0
        remaining[t.from_member_id] += t.amount_cents
        remaining[t.to_member_id] -= t.amount_cents
    assert set(remaining.values()) == {0}


@pytest.mark.parametrize(
    ("frm", "to", "amount"),
    [(1, 1, 100), (1, 2, 0), (1, 2, -1)],
)
def test_settlement_invariants(frm: int, to: int, amount: int) -> None:
    with pytest.raises(ValidationError):
        Settlement(household_id=1, from_member_id=frm, to_member_id=to, amount_cents=amount)


def test_settlement_amount_has_an_upper_limit() -> None:
    with pytest.raises(ValidationError):
        Settlement(
            household_id=1, from_member_id=1, to_member_id=2, amount_cents=MAX_AMOUNT_CENTS + 1
        )
