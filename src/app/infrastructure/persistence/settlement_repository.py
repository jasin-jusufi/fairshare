from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.settlement import Settlement
from app.infrastructure.persistence.mapping import as_utc
from app.infrastructure.persistence.models import SettlementModel


def to_domain(model: SettlementModel) -> Settlement:
    return Settlement(
        id=model.id,
        household_id=model.household_id,
        from_member_id=model.from_member_id,
        to_member_id=model.to_member_id,
        amount_cents=model.amount_cents,
        created_at=as_utc(model.created_at),
    )


class SqlAlchemySettlementRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, settlement: Settlement) -> Settlement:
        model = SettlementModel(
            household_id=settlement.household_id,
            from_member_id=settlement.from_member_id,
            to_member_id=settlement.to_member_id,
            amount_cents=settlement.amount_cents,
            created_at=settlement.created_at,
        )
        self._session.add(model)
        self._session.commit()
        return to_domain(model)

    def list_by_household(self, household_id: int) -> list[Settlement]:
        query = (
            select(SettlementModel)
            .where(SettlementModel.household_id == household_id)
            .order_by(SettlementModel.id)
        )
        return [to_domain(m) for m in self._session.scalars(query)]
