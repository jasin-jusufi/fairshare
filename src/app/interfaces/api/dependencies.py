from app.application.expense_service import ExpenseService
from app.application.household_service import HouseholdService

PROVIDED_BY_INFRASTRUCTURE = "Provided by infrastructure via dependency_overrides"


def household_service() -> HouseholdService:
    raise NotImplementedError(PROVIDED_BY_INFRASTRUCTURE)


def expense_service() -> ExpenseService:
    raise NotImplementedError(PROVIDED_BY_INFRASTRUCTURE)
