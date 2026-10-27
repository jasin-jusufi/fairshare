from collections import Counter
from dataclasses import dataclass
from datetime import date

from app.application.errors import NotFoundError
from app.application.lookup import require_household
from app.application.ports.repositories import (
    ChoreAssignmentRepository,
    ChoreRepository,
    HouseholdRepository,
)
from app.domain.chore import Chore, ChoreAssignment, plan_week, week_start_of
from app.domain.errors import ConflictError


@dataclass(frozen=True)
class MemberLoad:
    member_id: int
    name: str
    effort_points: int


class ChoreService:
    def __init__(
        self,
        households: HouseholdRepository,
        chores: ChoreRepository,
        assignments: ChoreAssignmentRepository,
    ) -> None:
        self._households = households
        self._chores = chores
        self._assignments = assignments

    def add_chore(self, household_id: int, name: str, effort: int) -> Chore:
        require_household(self._households, household_id)
        return self._chores.add(Chore(household_id=household_id, name=name, effort=effort))

    def list_chores(self, household_id: int) -> list[Chore]:
        require_household(self._households, household_id)
        return self._chores.list_by_household(household_id)

    def plan_week(self, household_id: int, day: date) -> list[ChoreAssignment]:
        """Plans the chores still missing from the week; an untouched week gets all of them."""
        household = require_household(self._households, household_id)
        week = week_start_of(day)
        planned = {a.chore_id for a in self._assignments.list_by_household(household_id, week)}
        missing = [c for c in self._chores.list_by_household(household_id) if c.id not in planned]
        if planned and not missing:
            raise ConflictError(f"Week starting {week.isoformat()} is already planned")
        assignments = plan_week(
            household_id,
            missing,
            sorted(household.member_ids()),
            self._past_load(household_id, until=week),
            week,
        )
        return self._assignments.add_all(assignments)

    def week_plan(self, household_id: int, day: date) -> list[ChoreAssignment]:
        require_household(self._households, household_id)
        return self._assignments.list_by_household(household_id, week_start_of(day))

    def complete_assignment(self, household_id: int, assignment_id: int) -> ChoreAssignment:
        assignment = self._assignments.get(assignment_id)
        if assignment is None or assignment.household_id != household_id:
            raise NotFoundError(f"Assignment {assignment_id} not found")
        assignment.complete()
        return self._assignments.save(assignment)

    def load_by_member(self, household_id: int) -> list[MemberLoad]:
        household = require_household(self._households, household_id)
        load = self._past_load(household_id)
        return [
            MemberLoad(member.id, member.name, load.get(member.id, 0))
            for member in household.members
            if member.id is not None
        ]

    def _past_load(self, household_id: int, until: date | None = None) -> dict[int, int]:
        load: Counter[int] = Counter()
        for assignment in self._assignments.list_by_household(household_id):
            if until is None or assignment.week_start <= until:
                load[assignment.member_id] += assignment.effort
        return dict(load)
