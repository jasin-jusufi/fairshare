from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.chore_service import ChoreService, MemberLoad
from app.domain.chore import Chore, ChoreAssignment, WeekPlan, week_start_of
from app.interfaces.api.dependencies import chore_service
from app.interfaces.api.openapi import CONFLICT, INVALID, NOT_FOUND
from app.interfaces.api.schemas import (
    AssignmentOut,
    ChoreCreate,
    ChoreOut,
    MemberLoadOut,
    WeekPlanCreate,
    WeekPlanOut,
)

router = APIRouter(prefix="/households/{household_id}", tags=["Ämtli"])
Service = Annotated[ChoreService, Depends(chore_service)]


@router.post(
    "/chores",
    response_model=ChoreOut,
    status_code=201,
    summary="Ämtli anlegen",
    responses={**INVALID, **NOT_FOUND},
)
def add_chore(household_id: int, payload: ChoreCreate, service: Service) -> Chore:
    """Legt ein Ämtli mit Aufwand 1–5 an. Der Aufwand steuert die faire Verteilung."""
    return service.add_chore(household_id, payload.name, payload.effort)


@router.get(
    "/chores", response_model=list[ChoreOut], summary="Ämtli auflisten", responses=NOT_FOUND
)
def list_chores(household_id: int, service: Service) -> list[Chore]:
    """Alle Ämtli des Haushalts."""
    return service.list_chores(household_id)


@router.post(
    "/chore-plans",
    response_model=WeekPlanOut,
    status_code=201,
    summary="Woche fair planen",
    responses={**INVALID, **NOT_FOUND, **CONFLICT},
)
def plan_week(household_id: int, payload: WeekPlanCreate, service: Service) -> WeekPlan:
    """Verteilt jedes Ämtli genau einmal: das aufwändigste zuerst an das Mitglied mit der
    kleinsten bisherigen Last (inkl. früherer Wochen). Jede Woche ist nur einmal planbar."""
    assignments = service.plan_week(household_id, payload.week_start)
    return WeekPlan(week_start_of(payload.week_start), assignments)


@router.get(
    "/chore-plans/{week_start}",
    response_model=WeekPlanOut,
    summary="Wochenplan abrufen",
    responses=NOT_FOUND,
)
def week_plan(household_id: int, week_start: date, service: Service) -> WeekPlan:
    """Zuteilungen der Woche, die das angegebene Datum enthält. Leer, wenn noch nicht geplant."""
    return WeekPlan(week_start_of(week_start), service.week_plan(household_id, week_start))


@router.post(
    "/assignments/{assignment_id}/complete",
    response_model=AssignmentOut,
    summary="Zuteilung abhaken",
    responses={**NOT_FOUND, **CONFLICT},
)
def complete_assignment(household_id: int, assignment_id: int, service: Service) -> ChoreAssignment:
    """Markiert eine Zuteilung als erledigt. Ein zweites Abhaken ergibt 409."""
    return service.complete_assignment(household_id, assignment_id)


@router.get(
    "/chore-load",
    response_model=list[MemberLoadOut],
    summary="Last pro Mitglied",
    responses=NOT_FOUND,
)
def chore_load(household_id: int, service: Service) -> list[MemberLoad]:
    """Summe der Aufwandpunkte pro Mitglied über alle geplanten Wochen."""
    return service.load_by_member(household_id)
