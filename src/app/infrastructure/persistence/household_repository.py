from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.household import Household, Member
from app.infrastructure.persistence.mapping import as_utc
from app.infrastructure.persistence.models import HouseholdModel, MemberModel


def to_domain(model: HouseholdModel) -> Household:
    return Household(
        id=model.id,
        name=model.name,
        currency=model.currency,
        created_at=as_utc(model.created_at),
        members=[Member(id=m.id, household_id=m.household_id, name=m.name) for m in model.members],
    )


class SqlAlchemyHouseholdRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, household: Household) -> Household:
        model = HouseholdModel(
            name=household.name, currency=household.currency, created_at=household.created_at
        )
        self._session.add(model)
        self._session.flush()
        household.id = model.id
        return self.save(household)

    def get(self, household_id: int) -> Household | None:
        model = self._session.get(HouseholdModel, household_id)
        return to_domain(model) if model else None

    def list(self) -> list[Household]:
        models = self._session.scalars(select(HouseholdModel).order_by(HouseholdModel.id))
        return [to_domain(m) for m in models]

    def save(self, household: Household) -> Household:
        model = self._session.get_one(HouseholdModel, household.id)
        model.name = household.name
        new_members = [m for m in household.members if m.id is None]
        for member in new_members:
            member_model = MemberModel(name=member.name)
            model.members.append(member_model)
            self._session.flush()
            member.id = member_model.id
            member.household_id = model.id
        self._session.commit()
        return household
