from dataclasses import dataclass

from app.application.lookup import require_household
from app.application.ports.repositories import (
    ExpenseRepository,
    HouseholdRepository,
    SettlementRepository,
)
from app.domain.errors import OverpaymentError, UnknownMemberError
from app.domain.household import Household
from app.domain.settlement import Settlement, Transfer, compute_balances, suggest_transfers


@dataclass(frozen=True)
class MemberBalance:
    member_id: int
    name: str
    balance_cents: int


class SettlementService:
    def __init__(
        self,
        households: HouseholdRepository,
        expenses: ExpenseRepository,
        settlements: SettlementRepository,
    ) -> None:
        self._households = households
        self._expenses = expenses
        self._settlements = settlements

    def balances(self, household_id: int) -> list[MemberBalance]:
        household = require_household(self._households, household_id)
        balances = self._balances(household)
        return [
            MemberBalance(member.id, member.name, balances[member.id])
            for member in household.members
            if member.id is not None
        ]

    def suggest_transfers(self, household_id: int) -> list[Transfer]:
        household = require_household(self._households, household_id)
        return suggest_transfers(self._balances(household))

    def record_settlement(
        self, household_id: int, from_member_id: int, to_member_id: int, amount_cents: int
    ) -> Settlement:
        household = require_household(self._households, household_id)
        unknown = {from_member_id, to_member_id} - household.member_ids()
        if unknown:
            raise UnknownMemberError(f"Not members of this household: {sorted(unknown)}")
        settlement = Settlement(household_id, from_member_id, to_member_id, amount_cents)
        balances = self._balances(household)
        if amount_cents > -balances[from_member_id] or amount_cents > balances[to_member_id]:
            raise OverpaymentError("Settlement exceeds the open debt between these members")
        return self._settlements.add(settlement)

    def list_settlements(self, household_id: int) -> list[Settlement]:
        require_household(self._households, household_id)
        return self._settlements.list_by_household(household_id)

    def _balances(self, household: Household) -> dict[int, int]:
        assert household.id is not None
        return compute_balances(
            household.member_ids(),
            self._expenses.list_by_household(household.id),
            self._settlements.list_by_household(household.id),
        )
