from app.application.expense_service import ExpenseService
from app.application.household_service import HouseholdService
from app.application.settlement_service import SettlementService

PROVIDED_BY_INFRASTRUCTURE = "Provided by infrastructure via dependency_overrides"


def household_service() -> HouseholdService:
    raise NotImplementedError(PROVIDED_BY_INFRASTRUCTURE)


def expense_service() -> ExpenseService:
    raise NotImplementedError(PROVIDED_BY_INFRASTRUCTURE)


def settlement_service() -> SettlementService:
    raise NotImplementedError(PROVIDED_BY_INFRASTRUCTURE)
