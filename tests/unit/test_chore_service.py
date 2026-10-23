from datetime import date

import pytest

from app.application.chore_service import ChoreService
from app.application.errors import NotFoundError
from app.domain.errors import ConflictError
from app.domain.household import Household

from .fakes import (
    InMemoryChoreAssignmentRepository,
    InMemoryChoreRepository,
    InMemoryHouseholdRepository,
)

MONDAY = date(2026, 10, 26)


@pytest.fixture
def service() -> ChoreService:
    households = InMemoryHouseholdRepository()
    household = households.add(Household(name="WG"))
    for name in ("Lea", "Noah"):
        household.add_member(name)
    households.save(household)
    return ChoreService(households, InMemoryChoreRepository(), InMemoryChoreAssignmentRepository())


def test_add_and_list_chores(service: ChoreService) -> None:
    chore = service.add_chore(1, "Bad", 5)
    assert chore.id is not None
    assert service.list_chores(1) == [chore]


def test_plan_week_and_read_plan(service: ChoreService) -> None:
    service.add_chore(1, "Bad", 5)
    service.add_chore(1, "Müll", 1)
    planned = service.plan_week(1, date(2026, 10, 28))
    assert [a.member_id for a in planned] == [1, 2]
    assert service.week_plan(1, MONDAY) == planned


def test_plan_week_twice_conflicts(service: ChoreService) -> None:
    service.add_chore(1, "Bad", 5)
    service.plan_week(1, MONDAY)
    with pytest.raises(ConflictError):
        service.plan_week(1, MONDAY)


def test_complete_assignment(service: ChoreService) -> None:
    service.add_chore(1, "Bad", 5)
    [assignment] = service.plan_week(1, MONDAY)
    done = service.complete_assignment(1, assignment.id or 0)
    assert done.completed_at is not None
    with pytest.raises(NotFoundError):
        service.complete_assignment(1, 999)


def test_load_by_member(service: ChoreService) -> None:
    service.add_chore(1, "Bad", 5)
    service.plan_week(1, MONDAY)
    assert [(m.name, m.effort_points) for m in service.load_by_member(1)] == [
        ("Lea", 5),
        ("Noah", 0),
    ]


def test_unknown_household(service: ChoreService) -> None:
    with pytest.raises(NotFoundError):
        service.list_chores(9)
