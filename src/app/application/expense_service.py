from dataclasses import dataclass

from app.application.errors import NotFoundError
from app.application.lookup import require_household
from app.application.ports.repositories import ExpenseRepository, HouseholdRepository
from app.domain.errors import UnknownMemberError, ValidationError
from app.domain.expense import Expense, SplitMethod, split_amount


@dataclass(frozen=True)
class Participant:
    member_id: int
    weight: int = 1


class ExpenseService:
    def __init__(self, households: HouseholdRepository, expenses: ExpenseRepository) -> None:
        self._households = households
        self._expenses = expenses

    def record_expense(
        self,
        household_id: int,
        payer_id: int,
        description: str,
        amount_cents: int,
        method: SplitMethod,
        participants: list[Participant],
    ) -> Expense:
        household = require_household(self._households, household_id)
        member_ids = [p.member_id for p in participants]
        if len(set(member_ids)) != len(member_ids):
            raise ValidationError("Participants must be unique")
        unknown = ({payer_id} | set(member_ids)) - household.member_ids()
        if unknown:
            raise UnknownMemberError(f"Not members of this household: {sorted(unknown)}")
        shares = split_amount(amount_cents, method, {p.member_id: p.weight for p in participants})
        expense = Expense(
            household_id=household_id,
            payer_id=payer_id,
            description=description,
            amount_cents=amount_cents,
            method=method,
            shares=shares,
        )
        return self._expenses.add(expense)

    def list_expenses(self, household_id: int) -> list[Expense]:
        require_household(self._households, household_id)
        return self._expenses.list_by_household(household_id)

    def delete_expense(self, household_id: int, expense_id: int) -> None:
        expense = self._expenses.get(expense_id)
        if expense is None or expense.household_id != household_id:
            raise NotFoundError(f"Expense {expense_id} not found")
        self._expenses.delete(expense_id)
