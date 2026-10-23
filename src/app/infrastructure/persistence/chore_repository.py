from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.chore import Chore, ChoreAssignment
from app.infrastructure.persistence.mapping import as_utc
from app.infrastructure.persistence.models import ChoreAssignmentModel, ChoreModel


class SqlAlchemyChoreRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, chore: Chore) -> Chore:
        model = ChoreModel(household_id=chore.household_id, name=chore.name, effort=chore.effort)
        self._session.add(model)
        self._session.commit()
        chore.id = model.id
        return chore

    def list_by_household(self, household_id: int) -> list[Chore]:
        query = (
            select(ChoreModel)
            .where(ChoreModel.household_id == household_id)
            .order_by(ChoreModel.id)
        )
        return [
            Chore(id=m.id, household_id=m.household_id, name=m.name, effort=m.effort)
            for m in self._session.scalars(query)
        ]


def to_domain(model: ChoreAssignmentModel) -> ChoreAssignment:
    return ChoreAssignment(
        id=model.id,
        household_id=model.household_id,
        chore_id=model.chore_id,
        chore_name=model.chore_name,
        member_id=model.member_id,
        effort=model.effort,
        week_start=model.week_start,
        completed_at=as_utc(model.completed_at) if model.completed_at else None,
    )


class SqlAlchemyChoreAssignmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_all(self, assignments: list[ChoreAssignment]) -> list[ChoreAssignment]:
        models = [
            ChoreAssignmentModel(
                household_id=a.household_id,
                chore_id=a.chore_id,
                chore_name=a.chore_name,
                member_id=a.member_id,
                effort=a.effort,
                week_start=a.week_start,
            )
            for a in assignments
        ]
        self._session.add_all(models)
        self._session.commit()
        return [to_domain(m) for m in models]

    def get(self, assignment_id: int) -> ChoreAssignment | None:
        model = self._session.get(ChoreAssignmentModel, assignment_id)
        return to_domain(model) if model else None

    def list_by_household(
        self, household_id: int, week_start: date | None = None
    ) -> list[ChoreAssignment]:
        query = select(ChoreAssignmentModel).where(
            ChoreAssignmentModel.household_id == household_id
        )
        if week_start is not None:
            query = query.where(ChoreAssignmentModel.week_start == week_start)
        return [
            to_domain(m) for m in self._session.scalars(query.order_by(ChoreAssignmentModel.id))
        ]

    def save(self, assignment: ChoreAssignment) -> ChoreAssignment:
        model = self._session.get_one(ChoreAssignmentModel, assignment.id)
        model.completed_at = assignment.completed_at
        self._session.commit()
        return assignment
