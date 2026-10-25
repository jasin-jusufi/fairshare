import random

import pytest

from app.domain.errors import ValidationError
from app.domain.expense import SplitMethod, split_amount


def amounts(shares: list) -> list[int]:
    return [s.amount_cents for s in shares]


def test_one_cent_among_three_goes_to_the_first_participant() -> None:
    """Smallest possible amount: one cent cannot be split, so exactly one person gets it
    and the others get 0. Nothing may be lost or created."""
    assert amounts(split_amount(1, SplitMethod.EQUAL, {1: 1, 2: 1, 3: 1})) == [1, 0, 0]


@pytest.mark.parametrize(
    ("method", "weight"),
    [(SplitMethod.EQUAL, 1), (SplitMethod.PERCENT, 100), (SplitMethod.SHARES, 7)],
)
def test_single_participant_pays_the_full_amount(method: SplitMethod, weight: int) -> None:
    """Lower bound for participants: whatever the method, one person carries 100 %."""
    assert amounts(split_amount(999, method, {1: weight})) == [999]


@pytest.mark.parametrize("amount", [0, -1])
@pytest.mark.parametrize("method", list(SplitMethod))
def test_zero_and_negative_amounts_are_rejected(amount: int, method: SplitMethod) -> None:
    """Boundary just below the smallest valid amount (1 cent), for every method."""
    with pytest.raises(ValidationError):
        split_amount(amount, method, {1: 100})


@pytest.mark.parametrize(
    ("weights", "valid"),
    [
        ({1: 99, 2: 1}, True),
        ({1: 50, 2: 49}, False),
        ({1: 50, 2: 51}, False),
        ({1: 150, 2: -50}, False),
    ],
    ids=["exactly-100", "99", "101", "negative-but-sums-to-100"],
)
def test_percentages_must_be_positive_and_add_up_to_exactly_100(
    weights: dict[int, int], valid: bool
) -> None:
    """Boundary 99 / 100 / 101 %, and a trick case that sums to 100 with a negative value."""
    if valid:
        assert sum(amounts(split_amount(1000, SplitMethod.PERCENT, weights))) == 1000
    else:
        with pytest.raises(ValidationError):
            split_amount(1000, SplitMethod.PERCENT, weights)


def test_equal_split_ignores_zero_and_negative_weights() -> None:
    """For `equal` the weight is documented as ignored, so invalid weights must not
    cause an error there (they would for `shares`)."""
    assert amounts(split_amount(100, SplitMethod.EQUAL, {1: 0, 2: -5})) == [50, 50]


def test_very_large_amounts_and_weights_are_split_exactly() -> None:
    """Python ints have no overflow; the split must stay exact even far beyond 64 bit."""
    shares = split_amount(10**20 + 1, SplitMethod.SHARES, {1: 10**12, 2: 1, 3: 1})
    assert sum(amounts(shares)) == 10**20 + 1


def test_remainder_goes_to_the_participant_listed_first_not_lowest_id() -> None:
    """Tie-break documentation: with equal remainders the order of the participant list
    decides who pays the extra cent, not the member ID."""
    assert amounts(split_amount(100, SplitMethod.EQUAL, {3: 1, 1: 1, 2: 1})) == [34, 33, 33]


@pytest.mark.parametrize("seed", range(30))
def test_every_share_is_within_one_cent_of_the_exact_value(seed: int) -> None:
    """Property test with random amounts and weights: largest remainder never moves a share
    by a full cent or more away from the mathematically exact share, and the sum is exact."""
    rng = random.Random(seed)
    weights = {m: rng.randint(1, 50) for m in range(1, rng.randint(2, 9))}
    amount = rng.randint(1, 1_000_000)
    total = sum(weights.values())

    shares = split_amount(amount, SplitMethod.SHARES, weights)

    assert sum(amounts(shares)) == amount
    for share in shares:
        assert abs(share.amount_cents * total - amount * weights[share.member_id]) < total


@pytest.mark.parametrize("seed", range(30))
def test_equal_shares_differ_by_at_most_one_cent(seed: int) -> None:
    """Fairness of `equal`: nobody pays more than one cent more than anyone else."""
    rng = random.Random(seed)
    participants = dict.fromkeys(range(1, rng.randint(2, 12)), 1)
    shares = amounts(split_amount(rng.randint(1, 100_000), SplitMethod.EQUAL, participants))
    assert max(shares) - min(shares) <= 1
