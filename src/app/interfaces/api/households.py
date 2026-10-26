from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.household_service import HouseholdService
from app.domain.household import Household, Member
from app.interfaces.api.dependencies import household_service
from app.interfaces.api.openapi import CONFLICT, INVALID, NOT_FOUND
from app.interfaces.api.params import Id
from app.interfaces.api.schemas import HouseholdCreate, HouseholdOut, MemberCreate, MemberOut

router = APIRouter(prefix="/households", tags=["Households"])
Service = Annotated[HouseholdService, Depends(household_service)]


@router.post(
    "", response_model=HouseholdOut, status_code=201, summary="Create household", responses=INVALID
)
def create_household(payload: HouseholdCreate, service: Service) -> Household:
    """Creates a new household in CHF. The name is trimmed."""
    return service.create_household(payload.name)


@router.get("", response_model=list[HouseholdOut], summary="List households")
def list_households(service: Service) -> list[Household]:
    """All households in creation order, each with its members."""
    return service.list_households()


@router.get(
    "/{household_id}", response_model=HouseholdOut, summary="Get household", responses=NOT_FOUND
)
def get_household(household_id: Id, service: Service) -> Household:
    """A single household with all its members."""
    return service.get_household(household_id)


@router.post(
    "/{household_id}/members",
    response_model=MemberOut,
    status_code=201,
    summary="Add member",
    responses={**INVALID, **NOT_FOUND, **CONFLICT},
)
def add_member(household_id: Id, payload: MemberCreate, service: Service) -> Member:
    """Adds a member. Names are unique per household, ignoring case
    (`Lea` and `lea` → 409)."""
    return service.add_member(household_id, payload.name)
