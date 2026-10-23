from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.household_service import HouseholdService
from app.domain.household import Household, Member
from app.interfaces.api.dependencies import household_service
from app.interfaces.api.openapi import CONFLICT, INVALID, NOT_FOUND
from app.interfaces.api.schemas import HouseholdCreate, HouseholdOut, MemberCreate, MemberOut

router = APIRouter(prefix="/households", tags=["Haushalte"])
Service = Annotated[HouseholdService, Depends(household_service)]


@router.post(
    "", response_model=HouseholdOut, status_code=201, summary="Haushalt anlegen", responses=INVALID
)
def create_household(payload: HouseholdCreate, service: Service) -> Household:
    """Legt einen neuen Haushalt in CHF an. Der Name wird getrimmt."""
    return service.create_household(payload.name)


@router.get("", response_model=list[HouseholdOut], summary="Haushalte auflisten")
def list_households(service: Service) -> list[Household]:
    """Alle Haushalte in Erstellungsreihenfolge, jeweils mit Mitgliedern."""
    return service.list_households()


@router.get(
    "/{household_id}", response_model=HouseholdOut, summary="Haushalt abrufen", responses=NOT_FOUND
)
def get_household(household_id: int, service: Service) -> Household:
    """Ein Haushalt mit allen Mitgliedern."""
    return service.get_household(household_id)


@router.post(
    "/{household_id}/members",
    response_model=MemberOut,
    status_code=201,
    summary="Mitglied hinzufügen",
    responses={**INVALID, **NOT_FOUND, **CONFLICT},
)
def add_member(household_id: int, payload: MemberCreate, service: Service) -> Member:
    """Fügt ein Mitglied hinzu. Namen sind pro Haushalt eindeutig, Gross-/Kleinschreibung
    wird ignoriert (`Lea` und `lea` → 409)."""
    return service.add_member(household_id, payload.name)
