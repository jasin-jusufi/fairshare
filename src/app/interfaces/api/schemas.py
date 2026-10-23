from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domain.expense import SplitMethod


class OutModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HouseholdCreate(BaseModel):
    name: str


class MemberCreate(BaseModel):
    name: str


class MemberOut(OutModel):
    id: int
    name: str


class HouseholdOut(OutModel):
    id: int
    name: str
    currency: str
    created_at: datetime
    members: list[MemberOut]


class ParticipantIn(BaseModel):
    member_id: int
    weight: int = 1


class ExpenseCreate(BaseModel):
    payer_id: int
    description: str
    amount_cents: int
    method: SplitMethod = SplitMethod.EQUAL
    participants: list[ParticipantIn]


class ShareOut(OutModel):
    member_id: int
    amount_cents: int


class ExpenseOut(OutModel):
    id: int
    household_id: int
    payer_id: int
    description: str
    amount_cents: int
    method: SplitMethod
    created_at: datetime
    shares: list[ShareOut]


class BalanceOut(OutModel):
    member_id: int
    name: str
    balance_cents: int


class TransferOut(BaseModel):
    from_member_id: int
    from_name: str
    to_member_id: int
    to_name: str
    amount_cents: int


class SettlementCreate(BaseModel):
    from_member_id: int
    to_member_id: int
    amount_cents: int


class SettlementOut(OutModel):
    id: int
    from_member_id: int
    to_member_id: int
    amount_cents: int
    created_at: datetime


class ChoreCreate(BaseModel):
    name: str
    effort: int


class ChoreOut(OutModel):
    id: int
    name: str
    effort: int


class WeekPlanCreate(BaseModel):
    week_start: date


class AssignmentOut(OutModel):
    id: int
    chore_id: int
    chore_name: str
    member_id: int
    effort: int
    week_start: date
    completed_at: datetime | None


class WeekPlanOut(OutModel):
    week_start: date
    assignments: list[AssignmentOut]


class MemberLoadOut(OutModel):
    member_id: int
    name: str
    effort_points: int
