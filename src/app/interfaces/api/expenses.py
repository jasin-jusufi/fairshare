from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.application.expense_service import ExpenseService, Participant
from app.domain.expense import Expense
from app.interfaces.api.dependencies import expense_service
from app.interfaces.api.schemas import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/households/{household_id}/expenses", tags=["expenses"])
Service = Annotated[ExpenseService, Depends(expense_service)]


@router.post("", response_model=ExpenseOut, status_code=201)
def record_expense(household_id: int, payload: ExpenseCreate, service: Service) -> Expense:
    return service.record_expense(
        household_id,
        payload.payer_id,
        payload.description,
        payload.amount_cents,
        payload.method,
        [Participant(p.member_id, p.weight) for p in payload.participants],
    )


@router.get("", response_model=list[ExpenseOut])
def list_expenses(household_id: int, service: Service) -> list[Expense]:
    return service.list_expenses(household_id)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(household_id: int, expense_id: int, service: Service) -> Response:
    service.delete_expense(household_id, expense_id)
    return Response(status_code=204)
