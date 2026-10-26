from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.expense import SplitMethod


class OutModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorOut(BaseModel):
    detail: str = Field(
        description="Human-readable error message", examples=["Household 7 not found"]
    )


class HouseholdCreate(BaseModel):
    name: str = Field(description="Household name, 1–80 characters", examples=["Flat Basel"])


class MemberCreate(BaseModel):
    name: str = Field(
        description="Name, 1–80 characters, unique within the household (case-insensitive)",
        examples=["Lea"],
    )


class MemberOut(OutModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Lea"])


class HouseholdOut(OutModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Flat Basel"])
    currency: str = Field(description="Always CHF", examples=["CHF"])
    created_at: datetime
    members: list[MemberOut]


class ParticipantIn(BaseModel):
    member_id: int = Field(description="Participating member", examples=[1])
    weight: int = Field(
        default=1,
        description="Percentage (method `percent`, total 100) or ratio (method `shares`); "
        "ignored for `equal`",
        examples=[1],
    )


class ExpenseCreate(BaseModel):
    payer_id: int = Field(description="Member who paid", examples=[1])
    description: str = Field(description="1–120 characters", examples=["Weekly groceries"])
    amount_cents: int = Field(description="Amount in cents (Rappen), > 0", examples=[9000])
    method: SplitMethod = Field(default=SplitMethod.EQUAL, description="Split method")
    participants: list[ParticipantIn] = Field(
        description="Participants, at least one, no duplicates",
        examples=[[{"member_id": 1}, {"member_id": 2}, {"member_id": 3}]],
    )


class ShareOut(OutModel):
    member_id: int = Field(examples=[2])
    amount_cents: int = Field(description="Share in cents", examples=[3000])


class ExpenseOut(OutModel):
    id: int = Field(examples=[1])
    household_id: int = Field(examples=[1])
    payer_id: int = Field(examples=[1])
    description: str = Field(examples=["Weekly groceries"])
    amount_cents: int = Field(examples=[9000])
    method: SplitMethod
    created_at: datetime
    shares: list[ShareOut] = Field(description="Always adds up exactly to `amount_cents`")


class BalanceOut(OutModel):
    member_id: int = Field(examples=[1])
    name: str = Field(examples=["Lea"])
    balance_cents: int = Field(
        description="Positive: is owed money. Negative: owes money.", examples=[6000]
    )


class TransferOut(BaseModel):
    from_member_id: int = Field(examples=[2])
    from_name: str = Field(examples=["Noah"])
    to_member_id: int = Field(examples=[1])
    to_name: str = Field(examples=["Lea"])
    amount_cents: int = Field(examples=[3000])


class SettlementCreate(BaseModel):
    from_member_id: int = Field(description="Who pays (debtor)", examples=[2])
    to_member_id: int = Field(description="Who receives (creditor)", examples=[1])
    amount_cents: int = Field(description="Cents, > 0 and at most the open debt", examples=[3000])


class SettlementOut(OutModel):
    id: int = Field(examples=[1])
    from_member_id: int = Field(examples=[2])
    to_member_id: int = Field(examples=[1])
    amount_cents: int = Field(examples=[3000])
    created_at: datetime


class ChoreCreate(BaseModel):
    name: str = Field(description="1–80 characters", examples=["Bathroom"])
    effort: int = Field(description="Effort from 1 (light) to 5 (heavy)", examples=[5])


class ChoreOut(OutModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Bathroom"])
    effort: int = Field(examples=[5])


class WeekPlanCreate(BaseModel):
    week_start: date = Field(
        description="Any date in the week; normalised to its Monday",
        examples=["2026-10-26"],
    )


class AssignmentOut(OutModel):
    id: int = Field(examples=[1])
    chore_id: int = Field(examples=[1])
    chore_name: str = Field(examples=["Bathroom"])
    member_id: int = Field(examples=[1])
    effort: int = Field(description="Effort snapshot taken at planning time", examples=[5])
    week_start: date = Field(examples=["2026-10-26"])
    completed_at: datetime | None = Field(description="`null` until completed")


class WeekPlanOut(OutModel):
    week_start: date = Field(examples=["2026-10-26"])
    assignments: list[AssignmentOut]


class ReceiptSuggestionOut(OutModel):
    description: str = Field(
        description="Suggested description, 1–120 characters", examples=["Migros"]
    )
    amount_cents: int = Field(description="Suggested amount in cents (Rappen)", examples=[2350])


class MemberLoadOut(OutModel):
    member_id: int = Field(examples=[1])
    name: str = Field(examples=["Lea"])
    effort_points: int = Field(description="Sum of all assigned effort points", examples=[8])
