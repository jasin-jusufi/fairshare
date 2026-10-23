import pytest

from app.application.errors import NotFoundError
from app.application.expense_service import ExpenseService, Participant
from app.application.settlement_service import SettlementService
from app.domain.errors import OverpaymentError, UnknownMemberError
from app.domain.expense import SplitMethod
from app.domain.household import Household
from app.domain.settlement import Transfer

from .fakes import (
    InMemoryExpenseRepository,
    InMemoryHouseholdRepository,
    InMemorySettlementRepository,
)


@pytest.fixture
def service() -> SettlementService:
    households = InMemoryHouseholdRepository()
    household = households.add(Household(name="WG"))
    for name in ("Lea", "Noah"):
        household.add_member(name)
    households.save(household)
    expenses = InMemoryExpenseRepository()
    ExpenseService(households, expenses).record_expense(
        1, 1, "Migros", 1000, SplitMethod.EQUAL, [Participant(1), Participant(2)]
    )
    return SettlementService(households, expenses, InMemorySettlementRepository())


def test_balances_include_names(service: SettlementService) -> None:
    assert [(b.name, b.balance_cents) for b in service.balances(1)] == [
        ("Lea", 500),
        ("Noah", -500),
    ]


def test_suggest_transfers(service: SettlementService) -> None:
    assert service.suggest_transfers(1) == [Transfer(2, 1, 500)]


def test_record_settlement_clears_debt(service: SettlementService) -> None:
    settlement = service.record_settlement(1, 2, 1, 500)
    assert settlement.id is not None
    assert service.suggest_transfers(1) == []
    assert service.list_settlements(1) == [settlement]


def test_overpayment_is_rejected(service: SettlementService) -> None:
    with pytest.raises(OverpaymentError):
        service.record_settlement(1, 2, 1, 501)


def test_creditor_cannot_pay(service: SettlementService) -> None:
    with pytest.raises(OverpaymentError):
        service.record_settlement(1, 1, 2, 100)


def test_members_must_belong_to_household(service: SettlementService) -> None:
    with pytest.raises(UnknownMemberError):
        service.record_settlement(1, 2, 99, 100)


def test_unknown_household(service: SettlementService) -> None:
    with pytest.raises(NotFoundError):
        service.balances(9)
