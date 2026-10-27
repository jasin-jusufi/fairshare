from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.chore_service import ChoreService, MemberLoad
from app.domain.chore import Chore, ChoreAssignment, WeekPlan, week_start_of
from app.interfaces.api.dependencies import chore_service
from app.interfaces.api.openapi import CONFLICT, INVALID, NOT_FOUND
from app.interfaces.api.params import Id
from app.interfaces.api.schemas import (
    AssignmentOut,
    ChoreCreate,
    ChoreOut,
    MemberLoadOut,
    WeekPlanCreate,
    WeekPlanOut,
)

router = APIRouter(prefix="/households/{household_id}", tags=["Chores"])
Service = Annotated[ChoreService, Depends(chore_service)]


@router.post(
    "/chores",
    response_model=ChoreOut,
    status_code=201,
    summary="Create chore",
    responses={**INVALID, **NOT_FOUND},
)
def add_chore(household_id: Id, payload: ChoreCreate, service: Service) -> Chore:
    """Creates a chore with effort 1–5. Effort drives the fair distribution."""
    return service.add_chore(household_id, payload.name, payload.effort)


@router.get("/chores", response_model=list[ChoreOut], summary="List chores", responses=NOT_FOUND)
def list_chores(household_id: Id, service: Service) -> list[Chore]:
    """All chores of the household."""
    return service.list_chores(household_id)


@router.post(
    "/chore-plans",
    response_model=WeekPlanOut,
    status_code=201,
    summary="Plan week fairly",
    responses={**INVALID, **NOT_FOUND, **CONFLICT},
)
def plan_week(household_id: Id, payload: WeekPlanCreate, service: Service) -> WeekPlan:
    """Assigns every chore exactly once: the heaviest first, to the member with the
    lowest load so far (including previous weeks). Each week can be planned only once."""
    assignments = service.plan_week(household_id, payload.week_start)
    return WeekPlan(week_start_of(payload.week_start), assignments)


@router.get(
    "/chore-plans/{week_start}",
    response_model=WeekPlanOut,
    summary="Get week plan",
    responses=NOT_FOUND,
)
def week_plan(household_id: Id, week_start: date, service: Service) -> WeekPlan:
    """Assignments of the week containing the given date. Empty if not planned yet."""
    return WeekPlan(week_start_of(week_start), service.week_plan(household_id, week_start))


@router.post(
    "/assignments/{assignment_id}/complete",
    response_model=AssignmentOut,
    summary="Complete assignment",
    responses={**NOT_FOUND, **CONFLICT},
)
def complete_assignment(household_id: Id, assignment_id: Id, service: Service) -> ChoreAssignment:
    """Marks an assignment as done. Completing it again returns 409."""
    return service.complete_assignment(household_id, assignment_id)


@router.get(
    "/chore-load",
    response_model=list[MemberLoadOut],
    summary="Load per member",
    responses=NOT_FOUND,
)
def chore_load(household_id: Id, service: Service) -> list[MemberLoad]:
    """Total effort points per member across all planned weeks."""
    return service.load_by_member(household_id)
