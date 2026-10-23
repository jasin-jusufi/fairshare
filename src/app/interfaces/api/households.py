from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.household_service import HouseholdService
from app.domain.household import Household, Member
from app.interfaces.api.dependencies import household_service
from app.interfaces.api.schemas import HouseholdCreate, HouseholdOut, MemberCreate, MemberOut

router = APIRouter(prefix="/households", tags=["households"])
Service = Annotated[HouseholdService, Depends(household_service)]


@router.post("", response_model=HouseholdOut, status_code=201)
def create_household(payload: HouseholdCreate, service: Service) -> Household:
    return service.create_household(payload.name)


@router.get("", response_model=list[HouseholdOut])
def list_households(service: Service) -> list[Household]:
    return service.list_households()


@router.get("/{household_id}", response_model=HouseholdOut)
def get_household(household_id: int, service: Service) -> Household:
    return service.get_household(household_id)


@router.post("/{household_id}/members", response_model=MemberOut, status_code=201)
def add_member(household_id: int, payload: MemberCreate, service: Service) -> Member:
    return service.add_member(household_id, payload.name)
