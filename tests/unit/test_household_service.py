import pytest

from app.application.errors import NotFoundError
from app.application.household_service import HouseholdService
from app.domain.errors import DuplicateMemberError

from .fakes import InMemoryHouseholdRepository


@pytest.fixture
def service() -> HouseholdService:
    return HouseholdService(InMemoryHouseholdRepository())


def test_create_household_assigns_id(service: HouseholdService) -> None:
    household = service.create_household("Flat Basel")
    assert household.id == 1
    assert service.get_household(1).name == "Flat Basel"


def test_add_member_persists_member(service: HouseholdService) -> None:
    household = service.create_household("Flat")
    member = service.add_member(household.id or 0, "Lea")
    assert member.id is not None
    assert [m.name for m in service.get_household(household.id or 0).members] == ["Lea"]


def test_add_duplicate_member_is_rejected(service: HouseholdService) -> None:
    household = service.create_household("Flat")
    service.add_member(household.id or 0, "Lea")
    with pytest.raises(DuplicateMemberError):
        service.add_member(household.id or 0, "lea")


def test_unknown_household_raises_not_found(service: HouseholdService) -> None:
    with pytest.raises(NotFoundError):
        service.get_household(42)
    with pytest.raises(NotFoundError):
        service.add_member(42, "Lea")


def test_list_households(service: HouseholdService) -> None:
    service.create_household("A")
    service.create_household("B")
    assert [h.name for h in service.list_households()] == ["A", "B"]
