import pytest

from app.domain.errors import DuplicateMemberError, ValidationError
from app.domain.household import Household, Member


def test_household_name_is_trimmed_and_defaults_to_chf() -> None:
    household = Household(name="  Flat Basel ")
    assert household.name == "Flat Basel"
    assert household.currency == "CHF"


@pytest.mark.parametrize("name", ["", "   ", "x" * 81])
def test_household_name_must_be_valid(name: str) -> None:
    with pytest.raises(ValidationError):
        Household(name=name)


@pytest.mark.parametrize("name", ["", "  ", "x" * 81])
def test_member_name_must_be_valid(name: str) -> None:
    with pytest.raises(ValidationError):
        Member(name=name)


def test_add_member_returns_member() -> None:
    household = Household(name="Flat")
    member = household.add_member("Lea")
    assert member.name == "Lea"
    assert household.members == [member]


def test_member_names_are_unique_case_insensitive() -> None:
    household = Household(name="Flat")
    household.add_member("Lea")
    with pytest.raises(DuplicateMemberError):
        household.add_member(" LEA ")


def test_has_member() -> None:
    household = Household(name="Flat", members=[Member(name="Lea", id=7)])
    assert household.has_member(7)
    assert not household.has_member(8)
