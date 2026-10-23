from copy import deepcopy

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
