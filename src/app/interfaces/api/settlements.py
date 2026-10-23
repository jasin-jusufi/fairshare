from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.settlement_service import MemberBalance, SettlementService
from app.domain.settlement import Settlement
from app.interfaces.api.dependencies import settlement_service
from app.interfaces.api.openapi import INVALID, NOT_FOUND
from app.interfaces.api.schemas import BalanceOut, SettlementCreate, SettlementOut, TransferOut

router = APIRouter(prefix="/households/{household_id}", tags=["Abrechnen"])
Service = Annotated[SettlementService, Depends(settlement_service)]


@router.get(
    "/balances", response_model=list[BalanceOut], summary="Salden abrufen", responses=NOT_FOUND
)
def balances(household_id: int, service: Service) -> list[MemberBalance]:
    """Saldo pro Mitglied: bezahlt − eigene Anteile + gesendete − empfangene Zahlungen.
    Die Summe aller Salden ist immer 0."""
    return service.balances(household_id)


@router.get(
    "/settle-up",
    response_model=list[TransferOut],
    summary="Ausgleich vorschlagen",
    responses=NOT_FOUND,
)
def settle_up(household_id: int, service: Service) -> list[TransferOut]:
    """Schlägt Überweisungen vor, die alle Salden auf 0 bringen. Greedy: grösste Schuld
    gegen grösstes Guthaben, höchstens n − 1 Überweisungen (ADR-007)."""
    names = {b.member_id: b.name for b in service.balances(household_id)}
    return [
        TransferOut(
            from_member_id=t.from_member_id,
            from_name=names[t.from_member_id],
            to_member_id=t.to_member_id,
            to_name=names[t.to_member_id],
            amount_cents=t.amount_cents,
        )
        for t in service.suggest_transfers(household_id)
    ]


@router.post(
    "/settlements",
    response_model=SettlementOut,
    status_code=201,
    summary="Zahlung erfassen",
    responses={**INVALID, **NOT_FOUND},
)
def record_settlement(household_id: int, payload: SettlementCreate, service: Service) -> Settlement:
    """Erfasst eine ausserhalb der App getätigte Überweisung. Der Betrag darf weder die
    offene Schuld des Zahlers noch das Guthaben des Empfängers übersteigen."""
    return service.record_settlement(
        household_id, payload.from_member_id, payload.to_member_id, payload.amount_cents
    )


@router.get(
    "/settlements",
    response_model=list[SettlementOut],
    summary="Zahlungen auflisten",
    responses=NOT_FOUND,
)
def list_settlements(household_id: int, service: Service) -> list[Settlement]:
    """Alle erfassten Ausgleichszahlungen in Erfassungsreihenfolge."""
    return service.list_settlements(household_id)
