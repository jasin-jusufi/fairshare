from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from app.domain.errors import ConflictError, ValidationError
from app.domain.validation import clean_text

MIN_EFFORT, MAX_EFFORT = 1, 5


def week_start_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


@dataclass
class Chore:
    household_id: int
    name: str
    effort: int
    id: int | None = None

    def __post_init__(self) -> None:
        self.name = clean_text(self.name, "Chore name", 80)
        if not MIN_EFFORT <= self.effort <= MAX_EFFORT:
            raise ValidationError(f"Effort must be between {MIN_EFFORT} and {MAX_EFFORT}")


@dataclass
class ChoreAssignment:
    household_id: int
    chore_id: int
    chore_name: str
    member_id: int
    effort: int
    week_start: date
    completed_at: datetime | None = None
    id: int | None = None

    def complete(self) -> None:
        if self.completed_at is not None:
            raise ConflictError("Assignment is already completed")
        self.completed_at = datetime.now(UTC)


def plan_week(
    household_id: int,
    chores: Sequence[Chore],
    member_ids: Sequence[int],
    past_load: dict[int, int],
    day: date,
) -> list[ChoreAssignment]:
    """Longest-processing-time heuristic: heaviest chore to the least loaded member."""
    if not chores:
        raise ValidationError("There are no chores to plan")
    if not member_ids:
        raise ValidationError("There are no members to assign chores to")
    load = {member: past_load.get(member, 0) for member in member_ids}
    week = week_start_of(day)
    assignments = []
    for chore in sorted(chores, key=lambda c: (-c.effort, c.id or 0)):
        assert chore.id is not None
        member = min(load, key=lambda m: (load[m], m))
        load[member] += chore.effort
        assignments.append(
            ChoreAssignment(household_id, chore.id, chore.name, member, chore.effort, week)
        )
    return assignments


@dataclass(frozen=True)
class WeekPlan:
    week_start: date
    assignments: list[ChoreAssignment] = field(default_factory=list)
