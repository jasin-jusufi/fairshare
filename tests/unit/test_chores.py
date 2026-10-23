import random
from datetime import date

import pytest
from app.domain.chore import Chore, ChoreAssignment, plan_week, week_start_of

from app.domain.errors import ConflictError, ValidationError


def chore(id: int, effort: int) -> Chore:
    return Chore(household_id=1, name=f"C{id}", effort=effort, id=id)


def assigned(assignments: list[ChoreAssignment]) -> dict[int, int]:
    return {a.chore_id: a.member_id for a in assignments}


@pytest.mark.parametrize(
    ("day", "monday"),
    [
        (date(2026, 10, 26), date(2026, 10, 26)),
        (date(2026, 10, 29), date(2026, 10, 26)),
        (date(2026, 11, 1), date(2026, 10, 26)),
    ],
)
def test_week_start_of(day: date, monday: date) -> None:
    assert week_start_of(day) == monday


def test_heaviest_chore_first_to_least_loaded() -> None:
    chores = [chore(1, 1), chore(2, 5), chore(3, 3)]
    result = plan_week(1, chores, [10, 20], {}, date(2026, 10, 26))
    assert assigned(result) == {2: 10, 3: 20, 1: 20}


def test_history_is_taken_into_account() -> None:
    result = plan_week(1, [chore(1, 3)], [10, 20], {10: 9, 20: 2}, date(2026, 10, 26))
    assert assigned(result) == {1: 20}


def test_assignments_snapshot_effort_and_week() -> None:
    [a] = plan_week(1, [chore(1, 4)], [10], {}, date(2026, 10, 28))
    assert (a.effort, a.week_start, a.completed_at) == (4, date(2026, 10, 26), None)


def test_requires_chores_and_members() -> None:
    with pytest.raises(ValidationError):
        plan_week(1, [], [10], {}, date(2026, 10, 26))
    with pytest.raises(ValidationError):
        plan_week(1, [chore(1, 1)], [], {}, date(2026, 10, 26))


@pytest.mark.parametrize("seed", range(10))
def test_long_run_fairness(seed: int) -> None:
    rng = random.Random(seed)
    chores = [chore(i, rng.randint(1, 5)) for i in range(1, rng.randint(3, 8))]
    members = list(range(1, rng.randint(2, 5) + 1))
    load = dict.fromkeys(members, 0)
    for week in range(12):
        for a in plan_week(1, chores, members, load, date(2026, 1, 5)):
            load[a.member_id] += a.effort
        assert week >= 0
    assert max(load.values()) - min(load.values()) <= max(c.effort for c in chores)


@pytest.mark.parametrize(("name", "effort"), [("", 3), ("Bad", 0), ("Bad", 6)])
def test_chore_invariants(name: str, effort: int) -> None:
    with pytest.raises(ValidationError):
        Chore(household_id=1, name=name, effort=effort)


def test_complete_once() -> None:
    [a] = plan_week(1, [chore(1, 2)], [10], {}, date(2026, 10, 26))
    a.complete()
    assert a.completed_at is not None
    with pytest.raises(ConflictError):
        a.complete()
