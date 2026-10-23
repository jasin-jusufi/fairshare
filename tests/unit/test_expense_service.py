import pytest
from app.application.expense_service import ExpenseService, Participant
from app.domain.expense import SplitMethod

from app.application.errors import NotFoundError
from app.domain.errors import UnknownMemberError
from app.domain.household import Household

from .fakes import InMemoryExpenseRepository, InMemoryHouseholdRepository


@pytest.fixture
def households() -> InMemoryHouseholdRepository:
    repo = InMemoryHouseholdRepository()
    household = repo.add(Household(name="WG"))
    for name in ("Lea", "Noah"):
        household.add_member(name)
    repo.save(household)
    return repo


@pytest.fixture
def service(households: InMemoryHouseholdRepository) -> ExpenseService:
    return ExpenseService(households, InMemoryExpenseRepository())


def test_record_expense_splits_and_persists(service: ExpenseService) -> None:
    expense = service.record_expense(
        1, 1, "Migros", 1001, SplitMethod.EQUAL, [Participant(1), Participant(2)]
    )
    assert expense.id is not None
    assert [s.amount_cents for s in expense.shares] == [501, 500]
    assert service.list_expenses(1) == [expense]


def test_payer_must_be_member(service: ExpenseService) -> None:
    with pytest.raises(UnknownMemberError):
        service.record_expense(1, 99, "Migros", 100, SplitMethod.EQUAL, [Participant(1)])


def test_participants_must_be_members(service: ExpenseService) -> None:
    with pytest.raises(UnknownMemberError):
        service.record_expense(1, 1, "Migros", 100, SplitMethod.EQUAL, [Participant(99)])


def test_unknown_household(service: ExpenseService) -> None:
    with pytest.raises(NotFoundError):
        service.record_expense(9, 1, "Migros", 100, SplitMethod.EQUAL, [Participant(1)])
    with pytest.raises(NotFoundError):
        service.list_expenses(9)


def test_delete_expense(service: ExpenseService) -> None:
    expense = service.record_expense(1, 1, "Migros", 100, SplitMethod.EQUAL, [Participant(1)])
    service.delete_expense(1, expense.id or 0)
    assert service.list_expenses(1) == []
    with pytest.raises(NotFoundError):
        service.delete_expense(1, expense.id or 0)
