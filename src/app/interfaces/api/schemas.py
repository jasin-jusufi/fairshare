from datetime import datetime

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
