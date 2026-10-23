from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
