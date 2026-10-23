from app.application.lookup import require_household
from app.application.ports.repositories import HouseholdRepository
from app.domain.household import Household, Member


class HouseholdService:
    def __init__(self, households: HouseholdRepository) -> None:
        self._households = households

    def create_household(self, name: str) -> Household:
        return self._households.add(Household(name=name))

    def list_households(self) -> list[Household]:
        return self._households.list()

    def get_household(self, household_id: int) -> Household:
        return require_household(self._households, household_id)

    def add_member(self, household_id: int, name: str) -> Member:
        household = self.get_household(household_id)
        member = household.add_member(name)
        self._households.save(household)
        return member
