import pytest

from app.domain.errors import ValidationError
from app.domain.expense import SplitMethod, split_amount


def amounts(shares: list) -> list[int]:
    return [s.amount_cents for s in shares]


def test_equal_split_even() -> None:
    assert amounts(split_amount(900, SplitMethod.EQUAL, {1: 1, 2: 1, 3: 1})) == [300, 300, 300]


def test_equal_split_gives_remainder_to_first_participants() -> None:
    assert amounts(split_amount(1000, SplitMethod.EQUAL, {1: 1, 2: 1, 3: 1})) == [334, 333, 333]
    assert amounts(split_amount(1001, SplitMethod.EQUAL, {1: 1, 2: 1, 3: 1})) == [334, 334, 333]


def test_equal_split_ignores_weights() -> None:
    assert amounts(split_amount(100, SplitMethod.EQUAL, {1: 5, 2: 1})) == [50, 50]


def test_percent_split() -> None:
    assert amounts(split_amount(5000, SplitMethod.PERCENT, {1: 70, 2: 30})) == [3500, 1500]


def test_percent_split_uses_largest_remainder() -> None:
    shares = split_amount(1001, SplitMethod.PERCENT, {1: 33, 2: 33, 3: 34})
    assert amounts(shares) == [330, 330, 341]


def test_percent_must_sum_to_100() -> None:
    with pytest.raises(ValidationError):
        split_amount(1000, SplitMethod.PERCENT, {1: 60, 2: 30})


def test_weighted_split() -> None:
    assert amounts(split_amount(1000, SplitMethod.SHARES, {1: 2, 2: 1, 3: 1})) == [500, 250, 250]


def test_weighted_split_remainder_goes_to_largest_fraction() -> None:
    assert amounts(split_amount(100, SplitMethod.SHARES, {1: 1, 2: 2})) == [33, 67]


@pytest.mark.parametrize("weights", [{}, {1: 0}, {1: -1, 2: 2}])
def test_invalid_participants(weights: dict[int, int]) -> None:
    with pytest.raises(ValidationError):
        split_amount(1000, SplitMethod.SHARES, weights)


@pytest.mark.parametrize("amount", [1, 7, 99, 1000, 123457])
@pytest.mark.parametrize("method", list(SplitMethod))
def test_shares_always_sum_to_amount(amount: int, method: SplitMethod) -> None:
    weights = {1: 20, 2: 30, 3: 50}
    shares = split_amount(amount, method, weights)
    assert sum(amounts(shares)) == amount
    assert [s.member_id for s in shares] == [1, 2, 3]


def test_shares_remember_their_weight() -> None:
    shares = split_amount(50, SplitMethod.SHARES, {1: 1, 2: 1, 3: 98})
    assert [(s.amount_cents, s.weight) for s in shares] == [(1, 1), (0, 1), (49, 98)]
    assert {s.weight for s in split_amount(100, SplitMethod.EQUAL, {1: 7, 2: 3})} == {1}
