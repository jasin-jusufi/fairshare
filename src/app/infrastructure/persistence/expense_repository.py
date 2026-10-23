from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.expense import Expense, ExpenseShare, SplitMethod
from app.infrastructure.persistence.mapping import as_utc
from app.infrastructure.persistence.models import ExpenseModel, ExpenseShareModel


def to_domain(model: ExpenseModel) -> Expense:
    return Expense(
        id=model.id,
        household_id=model.household_id,
        payer_id=model.payer_id,
        description=model.description,
        amount_cents=model.amount_cents,
        method=SplitMethod(model.method),
        created_at=as_utc(model.created_at),
        shares=[
            ExpenseShare(id=s.id, member_id=s.member_id, amount_cents=s.amount_cents)
            for s in model.shares
        ],
    )


class SqlAlchemyExpenseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, expense: Expense) -> Expense:
        model = ExpenseModel(
            household_id=expense.household_id,
            payer_id=expense.payer_id,
            description=expense.description,
            amount_cents=expense.amount_cents,
            method=expense.method.value,
            created_at=expense.created_at,
            shares=[
                ExpenseShareModel(member_id=s.member_id, amount_cents=s.amount_cents)
                for s in expense.shares
            ],
        )
        self._session.add(model)
        self._session.commit()
        return to_domain(model)

    def get(self, expense_id: int) -> Expense | None:
        model = self._session.get(ExpenseModel, expense_id)
        return to_domain(model) if model else None

    def list_by_household(self, household_id: int) -> list[Expense]:
        query = (
            select(ExpenseModel)
            .where(ExpenseModel.household_id == household_id)
            .order_by(ExpenseModel.id)
        )
        return [to_domain(m) for m in self._session.scalars(query)]

    def delete(self, expense_id: int) -> None:
        self._session.delete(self._session.get_one(ExpenseModel, expense_id))
        self._session.commit()
