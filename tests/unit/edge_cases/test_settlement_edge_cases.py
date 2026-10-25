import random

from app.domain.expense import Expense, ExpenseShare, SplitMethod
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


def test_empty_household_has_no_balances_and_no_transfers() -> None:
    """Empty input: no members, no expenses. Must not crash and must suggest nothing."""
    assert compute_balances([], [], []) == {}
    assert suggest_transfers({}) == []


def test_paying_only_for_yourself_creates_no_debt() -> None:
    """A member who is payer and only participant owes nobody anything."""
    balances = compute_balances([1, 2], [expense(1, {1: 500})], [])
    assert balances == {1: 0, 2: 0}
    assert suggest_transfers(balances) == []


def test_one_cent_debt_is_still_settled() -> None:
    """Smallest possible debt must not be rounded away."""
    assert suggest_transfers({1: 1, 2: -1}) == [Transfer(2, 1, 1)]


def test_suggest_transfers_does_not_modify_the_input() -> None:
    """No side effects: the caller's balances dict must be unchanged afterwards."""
    balances = {1: 600, 2: -100, 3: -500}
    suggest_transfers(balances)
    assert balances == {1: 600, 2: -100, 3: -500}


def test_fifty_members_settle_with_at_most_49_positive_transfers() -> None:
    """Large household (the existing property test stops at 8 members): the n − 1 bound
    from ADR-007 must still hold and no transfer may be 0 or negative."""
    rng = random.Random(50)
    balances = {m: rng.randint(-50_000, 50_000) for m in range(1, 50)}
    balances[50] = -sum(balances.values())

    transfers = suggest_transfers(balances)

    assert len(transfers) <= 49
    assert all(t.amount_cents > 0 for t in transfers)


def test_balances_always_add_up_to_zero() -> None:
    """Core invariant of UC-003 over 200 random expenses and settlements: money is only
    moved between members, never created or lost."""
    rng = random.Random(3)
    members = [1, 2, 3, 4, 5]
    expenses = []
    for _ in range(200):
        participants = rng.sample(members, rng.randint(1, 5))
        expenses.append(
            expense(rng.choice(members), {m: rng.randint(0, 9999) for m in participants})
        )
    settlements = [
        Settlement(1, frm, to, rng.randint(1, 5000))
        for frm, to in (rng.sample(members, 2) for _ in range(50))
    ]
    assert sum(compute_balances(members, expenses, settlements).values()) == 0
