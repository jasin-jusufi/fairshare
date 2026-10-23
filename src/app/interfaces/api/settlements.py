from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.settlement_service import MemberBalance, SettlementService
from app.domain.settlement import Settlement
from app.interfaces.api.dependencies import settlement_service
from app.interfaces.api.schemas import BalanceOut, SettlementCreate, SettlementOut, TransferOut

router = APIRouter(prefix="/households/{household_id}", tags=["settle-up"])
Service = Annotated[SettlementService, Depends(settlement_service)]


@router.get("/balances", response_model=list[BalanceOut])
def balances(household_id: int, service: Service) -> list[MemberBalance]:
    return service.balances(household_id)


@router.get("/settle-up", response_model=list[TransferOut])
def settle_up(household_id: int, service: Service) -> list[TransferOut]:
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


@router.post("/settlements", response_model=SettlementOut, status_code=201)
def record_settlement(household_id: int, payload: SettlementCreate, service: Service) -> Settlement:
    return service.record_settlement(
        household_id, payload.from_member_id, payload.to_member_id, payload.amount_cents
    )


@router.get("/settlements", response_model=list[SettlementOut])
def list_settlements(household_id: int, service: Service) -> list[Settlement]:
    return service.list_settlements(household_id)
