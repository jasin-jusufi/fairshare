from datetime import date

import pytest

from app.domain.chore import Chore, plan_week, week_start_of
from app.domain.errors import ValidationError

MONDAY = date(2026, 10, 26)


def chore(id: int, effort: int) -> Chore:
    return Chore(household_id=1, name=f"C{id}", effort=effort, id=id)


@pytest.mark.parametrize("effort", [1, 5])
def test_effort_boundaries_are_accepted(effort: int) -> None:
    """Both ends of the allowed range 1–5 (the existing tests only check 0 and 6)."""
    assert Chore(household_id=1, name="Trash", effort=effort).effort == effort


def test_negative_effort_is_rejected() -> None:
    """Clearly invalid value well outside the range."""
    with pytest.raises(ValidationError):
        Chore(household_id=1, name="Trash", effort=-1)


@pytest.mark.parametrize(
    ("day", "monday"),
    [
        (date.min, date.min),
        (date.max, date(9999, 12, 27)),
        (date(2028, 2, 29), date(2028, 2, 28)),
        (date(2027, 1, 1), date(2026, 12, 28)),
    ],
    ids=["first-date-ever", "last-date-ever", "leap-day", "new-year-on-friday"],
)
def test_week_start_of_handles_calendar_edges(day: date, monday: date) -> None:
    """Calendar boundaries: the smallest and largest dates Python knows (no overflow),
    a leap day and a week that spans two years."""
    assert week_start_of(day) == monday


def test_more_members_than_chores_leaves_members_without_a_chore() -> None:
    """One chore, three members: exactly one assignment, nobody gets a chore twice."""
    result = plan_week(1, [chore(1, 3)], [10, 20, 30], {}, MONDAY)
    assert [(a.chore_id, a.member_id) for a in result] == [(1, 10)]


def test_ties_are_broken_by_lowest_member_id() -> None:
    """Equal effort and equal load: the plan must be deterministic, not random."""
    result = plan_week(1, [chore(1, 2), chore(2, 2)], [30, 10, 20], {}, MONDAY)
    assert {a.chore_id: a.member_id for a in result} == {1: 10, 2: 20}


def test_new_member_without_history_gets_the_heaviest_chore() -> None:
    """Fairness with history: someone who just moved in has done nothing yet, so they
    should take over the heaviest chore."""
    result = plan_week(1, [chore(1, 5), chore(2, 1)], [1, 2, 3], {1: 10, 2: 10}, MONDAY)
    assert {a.chore_id: a.member_id for a in result}[1] == 3


def test_history_of_former_members_is_ignored() -> None:
    """Past load of someone who is no longer in the member list must not lead to an
    assignment for that person."""
    result = plan_week(1, [chore(1, 3)], [1, 2], {99: 0, 1: 4}, MONDAY)
    assert [a.member_id for a in result] == [2]
