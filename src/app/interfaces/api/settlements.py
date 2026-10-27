from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.settlement_service import MemberBalance, SettlementService
from app.domain.settlement import Settlement
from app.interfaces.api.dependencies import settlement_service
from app.interfaces.api.openapi import INVALID, NOT_FOUND
from app.interfaces.api.params import Id
from app.interfaces.api.schemas import BalanceOut, SettlementCreate, SettlementOut, TransferOut

router = APIRouter(prefix="/households/{household_id}", tags=["Settle-up"])
Service = Annotated[SettlementService, Depends(settlement_service)]


@router.get(
    "/balances", response_model=list[BalanceOut], summary="Get balances", responses=NOT_FOUND
)
def balances(household_id: Id, service: Service) -> list[MemberBalance]:
    """Balance per member: paid − own shares + settlements sent − settlements received.
    All balances always add up to 0."""
    return service.balances(household_id)


@router.get(
    "/settle-up",
    response_model=list[TransferOut],
    summary="Suggest settle-up",
    responses=NOT_FOUND,
)
def settle_up(household_id: Id, service: Service) -> list[TransferOut]:
    """Suggests transfers that bring every balance to 0. Greedy: largest debt against
    largest credit, at most n − 1 transfers (ADR-007)."""
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
    summary="Record settlement",
    responses={**INVALID, **NOT_FOUND},
)
def record_settlement(household_id: Id, payload: SettlementCreate, service: Service) -> Settlement:
    """Records a transfer made outside the app. The amount may exceed neither the
    payer's open debt nor the recipient's credit."""
    return service.record_settlement(
        household_id, payload.from_member_id, payload.to_member_id, payload.amount_cents
    )


@router.get(
    "/settlements",
    response_model=list[SettlementOut],
    summary="List settlements",
    responses=NOT_FOUND,
)
def list_settlements(household_id: Id, service: Service) -> list[Settlement]:
    """All recorded settlements in the order they were recorded."""
    return service.list_settlements(household_id)
