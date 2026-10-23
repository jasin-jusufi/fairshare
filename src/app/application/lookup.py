from app.application.errors import NotFoundError
from app.application.ports.repositories import HouseholdRepository
from app.domain.household import Household


def require_household(households: HouseholdRepository, household_id: int) -> Household:
    household = households.get(household_id)
    if household is None:
        raise NotFoundError(f"Household {household_id} not found")
    return household
