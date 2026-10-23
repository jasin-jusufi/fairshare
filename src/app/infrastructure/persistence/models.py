from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
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
