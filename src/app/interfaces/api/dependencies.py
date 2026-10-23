from app.application.household_service import HouseholdService


def household_service() -> HouseholdService:
    raise NotImplementedError("Provided by infrastructure via dependency_overrides")
