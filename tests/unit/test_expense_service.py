import pytest

from app.application.errors import NotFoundError
from app.application.expense_service import ExpenseService, Participant
from app.domain.errors import UnknownMemberError, ValidationError
from app.domain.expense import SplitMethod
from app.domain.household import Household

from .fakes import InMemoryExpenseRepository, InMemoryHouseholdRepository


@pytest.fixture
def households() -> InMemoryHouseholdRepository:
    repo = InMemoryHouseholdRepository()
    household = repo.add(Household(name="Flat"))
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


def test_participants_must_be_unique(service: ExpenseService) -> None:
    with pytest.raises(ValidationError):
        service.record_expense(
            1, 1, "Migros", 100, SplitMethod.EQUAL, [Participant(1), Participant(1)]
        )


def test_update_expense_recomputes_shares_and_keeps_identity(service: ExpenseService) -> None:
    original = service.record_expense(
        1, 1, "Migros", 5000, SplitMethod.EQUAL, [Participant(1), Participant(2)]
    )
    updated = service.update_expense(
        1,
        original.id or 0,
        2,
        "Coop",
        6000,
        SplitMethod.PERCENT,
        [Participant(1, 25), Participant(2, 75)],
    )
    assert updated.id == original.id
    assert updated.created_at == original.created_at
    assert (updated.payer_id, updated.description, updated.method) == (
        2,
        "Coop",
        SplitMethod.PERCENT,
    )
    assert [s.amount_cents for s in updated.shares] == [1500, 4500]
    assert service.list_expenses(1) == [updated]


def test_invalid_update_leaves_the_expense_unchanged(service: ExpenseService) -> None:
    original = service.record_expense(1, 1, "Migros", 5000, SplitMethod.EQUAL, [Participant(1)])
    with pytest.raises(ValidationError):
        service.update_expense(
            1, original.id or 0, 1, "Migros", 5000, SplitMethod.PERCENT, [Participant(1, 90)]
        )
    with pytest.raises(UnknownMemberError):
        service.update_expense(
            1, original.id or 0, 99, "Migros", 5000, SplitMethod.EQUAL, [Participant(1)]
        )
    assert service.list_expenses(1) == [original]


def test_update_unknown_expense_or_other_household(
    service: ExpenseService, households: InMemoryHouseholdRepository
) -> None:
    other = households.add(Household(name="Other"))
    other.add_member("Mia")
    households.save(other)
    expense = service.record_expense(1, 1, "Migros", 100, SplitMethod.EQUAL, [Participant(1)])
    with pytest.raises(NotFoundError):
        service.update_expense(1, 99, 1, "Migros", 100, SplitMethod.EQUAL, [Participant(1)])
    with pytest.raises(NotFoundError):
        service.update_expense(
            other.id or 0, expense.id or 0, 3, "Migros", 100, SplitMethod.EQUAL, [Participant(3)]
        )
