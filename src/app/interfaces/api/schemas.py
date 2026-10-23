from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.expense import SplitMethod


class OutModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorOut(BaseModel):
    detail: str = Field(
        description="Menschlich lesbare Fehlermeldung", examples=["Household 7 not found"]
    )


class HouseholdCreate(BaseModel):
    name: str = Field(description="Name des Haushalts, 1–80 Zeichen", examples=["WG Basel"])


class MemberCreate(BaseModel):
    name: str = Field(
        description="Name, 1–80 Zeichen, eindeutig im Haushalt (ohne Gross-/Kleinschreibung)",
        examples=["Lea"],
    )


class MemberOut(OutModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Lea"])


class HouseholdOut(OutModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["WG Basel"])
    currency: str = Field(description="Immer CHF", examples=["CHF"])
    created_at: datetime
    members: list[MemberOut]


class ParticipantIn(BaseModel):
    member_id: int = Field(description="Beteiligtes Mitglied", examples=[1])
    weight: int = Field(
        default=1,
        description="Prozent (Methode `percent`, Summe 100) oder Gewicht (Methode `shares`); "
        "bei `equal` ignoriert",
        examples=[1],
    )


class ExpenseCreate(BaseModel):
    payer_id: int = Field(description="Mitglied, das bezahlt hat", examples=[1])
    description: str = Field(description="1–120 Zeichen", examples=["Migros Wocheneinkauf"])
    amount_cents: int = Field(description="Betrag in Rappen, > 0", examples=[9000])
    method: SplitMethod = Field(default=SplitMethod.EQUAL, description="Aufteilungsart")
    participants: list[ParticipantIn] = Field(
        description="Beteiligte, mindestens eine:r, keine Duplikate",
        examples=[[{"member_id": 1}, {"member_id": 2}, {"member_id": 3}]],
    )


class ShareOut(OutModel):
    member_id: int = Field(examples=[2])
    amount_cents: int = Field(description="Anteil in Rappen", examples=[3000])


class ExpenseOut(OutModel):
    id: int = Field(examples=[1])
    household_id: int = Field(examples=[1])
    payer_id: int = Field(examples=[1])
    description: str = Field(examples=["Migros Wocheneinkauf"])
    amount_cents: int = Field(examples=[9000])
    method: SplitMethod
    created_at: datetime
    shares: list[ShareOut] = Field(description="Summe entspricht immer exakt `amount_cents`")


class BalanceOut(OutModel):
    member_id: int = Field(examples=[1])
    name: str = Field(examples=["Lea"])
    balance_cents: int = Field(
        description="Positiv: bekommt Geld. Negativ: schuldet Geld.", examples=[6000]
    )


class TransferOut(BaseModel):
    from_member_id: int = Field(examples=[2])
    from_name: str = Field(examples=["Noah"])
    to_member_id: int = Field(examples=[1])
    to_name: str = Field(examples=["Lea"])
    amount_cents: int = Field(examples=[3000])


class SettlementCreate(BaseModel):
    from_member_id: int = Field(description="Wer überweist (Schuldner:in)", examples=[2])
    to_member_id: int = Field(description="Wer empfängt (Gläubiger:in)", examples=[1])
    amount_cents: int = Field(
        description="Rappen, > 0 und höchstens die offene Schuld", examples=[3000]
    )


class SettlementOut(OutModel):
    id: int = Field(examples=[1])
    from_member_id: int = Field(examples=[2])
    to_member_id: int = Field(examples=[1])
    amount_cents: int = Field(examples=[3000])
    created_at: datetime


class ChoreCreate(BaseModel):
    name: str = Field(description="1–80 Zeichen", examples=["Bad putzen"])
    effort: int = Field(description="Aufwand 1 (leicht) bis 5 (schwer)", examples=[5])


class ChoreOut(OutModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Bad putzen"])
    effort: int = Field(examples=[5])


class WeekPlanCreate(BaseModel):
    week_start: date = Field(
        description="Beliebiges Datum der Woche; wird auf den Montag normalisiert",
        examples=["2026-10-26"],
    )


class AssignmentOut(OutModel):
    id: int = Field(examples=[1])
    chore_id: int = Field(examples=[1])
    chore_name: str = Field(examples=["Bad putzen"])
    member_id: int = Field(examples=[1])
    effort: int = Field(description="Aufwand-Snapshot zum Planungszeitpunkt", examples=[5])
    week_start: date = Field(examples=["2026-10-26"])
    completed_at: datetime | None = Field(description="`null`, solange nicht erledigt")


class WeekPlanOut(OutModel):
    week_start: date = Field(examples=["2026-10-26"])
    assignments: list[AssignmentOut]


class MemberLoadOut(OutModel):
    member_id: int = Field(examples=[1])
    name: str = Field(examples=["Lea"])
    effort_points: int = Field(description="Summe aller zugeteilten Aufwandpunkte", examples=[8])
