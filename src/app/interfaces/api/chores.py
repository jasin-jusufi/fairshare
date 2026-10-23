from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.chore_service import ChoreService, MemberLoad
from app.domain.chore import Chore, ChoreAssignment, WeekPlan, week_start_of
from app.interfaces.api.dependencies import chore_service
from app.interfaces.api.schemas import (
    AssignmentOut,
    ChoreCreate,
    ChoreOut,
    MemberLoadOut,
    WeekPlanCreate,
    WeekPlanOut,
)

router = APIRouter(prefix="/households/{household_id}", tags=["chores"])
Service = Annotated[ChoreService, Depends(chore_service)]


@router.post("/chores", response_model=ChoreOut, status_code=201)
def add_chore(household_id: int, payload: ChoreCreate, service: Service) -> Chore:
    return service.add_chore(household_id, payload.name, payload.effort)


@router.get("/chores", response_model=list[ChoreOut])
def list_chores(household_id: int, service: Service) -> list[Chore]:
    return service.list_chores(household_id)


@router.post("/chore-plans", response_model=WeekPlanOut, status_code=201)
def plan_week(household_id: int, payload: WeekPlanCreate, service: Service) -> WeekPlan:
    assignments = service.plan_week(household_id, payload.week_start)
    return WeekPlan(week_start_of(payload.week_start), assignments)


@router.get("/chore-plans/{week_start}", response_model=WeekPlanOut)
def week_plan(household_id: int, week_start: date, service: Service) -> WeekPlan:
    return WeekPlan(week_start_of(week_start), service.week_plan(household_id, week_start))


@router.post("/assignments/{assignment_id}/complete", response_model=AssignmentOut)
def complete_assignment(household_id: int, assignment_id: int, service: Service) -> ChoreAssignment:
    return service.complete_assignment(household_id, assignment_id)


@router.get("/chore-load", response_model=list[MemberLoadOut])
def chore_load(household_id: int, service: Service) -> list[MemberLoad]:
    return service.load_by_member(household_id)
