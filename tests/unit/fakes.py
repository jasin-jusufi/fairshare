from copy import deepcopy

from app.domain.settlement import Settlement

from app.domain.expense import Expense
from app.domain.household import Household


class InMemoryHouseholdRepository:
    def __init__(self) -> None:
        self._items: dict[int, Household] = {}
        self._next_member_id = 1

    def add(self, household: Household) -> Household:
        household.id = len(self._items) + 1
        return self.save(household)

    def get(self, household_id: int) -> Household | None:
        stored = self._items.get(household_id)
        return deepcopy(stored) if stored else None

    def list(self) -> list[Household]:
        return [deepcopy(h) for h in self._items.values()]

    def save(self, household: Household) -> Household:
        assert household.id is not None
        for member in household.members:
            if member.id is None:
                member.id = self._next_member_id
                self._next_member_id += 1
            member.household_id = household.id
        self._items[household.id] = deepcopy(household)
        return household


class InMemoryExpenseRepository:
    def __init__(self) -> None:
        self._items: dict[int, Expense] = {}
        self._next_id = 1

    def add(self, expense: Expense) -> Expense:
        expense.id = self._next_id
        self._next_id += 1
        self._items[expense.id] = deepcopy(expense)
        return expense

    def get(self, expense_id: int) -> Expense | None:
        stored = self._items.get(expense_id)
        return deepcopy(stored) if stored else None

    def list_by_household(self, household_id: int) -> list[Expense]:
        return [deepcopy(e) for e in self._items.values() if e.household_id == household_id]

    def delete(self, expense_id: int) -> None:
        del self._items[expense_id]


class InMemorySettlementRepository:
    def __init__(self) -> None:
        self._items: list[Settlement] = []

    def add(self, settlement: Settlement) -> Settlement:
        settlement.id = len(self._items) + 1
        self._items.append(deepcopy(settlement))
        return settlement

    def list_by_household(self, household_id: int) -> list[Settlement]:
        return [deepcopy(s) for s in self._items if s.household_id == household_id]
