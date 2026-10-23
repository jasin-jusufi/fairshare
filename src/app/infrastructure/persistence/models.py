from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class HouseholdModel(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3), default="CHF")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    members: Mapped[list["MemberModel"]] = relationship(
        back_populates="household", order_by="MemberModel.id", cascade="all, delete-orphan"
    )


class MemberModel(Base):
    __tablename__ = "members"
    __table_args__ = (UniqueConstraint("household_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    household: Mapped[HouseholdModel] = relationship(back_populates="members")


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    payer_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    description: Mapped[str] = mapped_column(String(120))
    amount_cents: Mapped[int] = mapped_column(Integer)
    method: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    shares: Mapped[list["ExpenseShareModel"]] = relationship(
        order_by="ExpenseShareModel.id", cascade="all, delete-orphan"
    )


class ExpenseShareModel(Base):
    __tablename__ = "expense_shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)


class SettlementModel(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    from_member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    to_member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    amount_cents: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChoreModel(Base):
    __tablename__ = "chores"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    effort: Mapped[int] = mapped_column(Integer)


class ChoreAssignmentModel(Base):
    __tablename__ = "chore_assignments"
    __table_args__ = (UniqueConstraint("chore_id", "week_start"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    chore_id: Mapped[int] = mapped_column(ForeignKey("chores.id"))
    chore_name: Mapped[str] = mapped_column(String(80))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    effort: Mapped[int] = mapped_column(Integer)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
