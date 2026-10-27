from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.application.expense_service import ExpenseService, Participant
from app.domain.expense import Expense
from app.interfaces.api.dependencies import expense_service
from app.interfaces.api.openapi import INVALID, NOT_FOUND
from app.interfaces.api.params import Id
from app.interfaces.api.schemas import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/households/{household_id}/expenses", tags=["Expenses"])
Service = Annotated[ExpenseService, Depends(expense_service)]


@router.post(
    "",
    response_model=ExpenseOut,
    status_code=201,
    summary="Record expense",
    responses={**INVALID, **NOT_FOUND},
)
def record_expense(household_id: Id, payload: ExpenseCreate, service: Service) -> Expense:
    """Records an expense and calculates each participant's share.

    - `equal`: split evenly, `weight` is ignored
    - `percent`: `weight` is a percentage and all weights must add up to 100
    - `shares`: `weight` is a ratio, e.g. 2 : 1 : 1

    Leftover cents go to the participants with the largest fractional part
    (largest remainder). The shares always add up exactly to the amount.
    """
    return service.record_expense(
        household_id,
        payload.payer_id,
        payload.description,
        payload.amount_cents,
        payload.method,
        [Participant(p.member_id, p.weight) for p in payload.participants],
    )


@router.get("", response_model=list[ExpenseOut], summary="List expenses", responses=NOT_FOUND)
def list_expenses(household_id: Id, service: Service) -> list[Expense]:
    """All expenses of the household in the order they were recorded, including shares."""
    return service.list_expenses(household_id)


@router.put(
    "/{expense_id}",
    response_model=ExpenseOut,
    summary="Correct expense",
    responses={**INVALID, **NOT_FOUND},
)
def update_expense(
    household_id: Id, expense_id: Id, payload: ExpenseCreate, service: Service
) -> Expense:
    """Replaces payer, description, amount, split method and participants of an
    expense. The shares are recomputed with the same rules as when recording; the
    expense keeps its ID and recording time. Balances and settle-up suggestions
    follow immediately, also when settlements were already recorded.
    """
    return service.update_expense(
        household_id,
        expense_id,
        payload.payer_id,
        payload.description,
        payload.amount_cents,
        payload.method,
        [Participant(p.member_id, p.weight) for p in payload.participants],
    )


@router.delete("/{expense_id}", status_code=204, summary="Delete expense", responses=NOT_FOUND)
def delete_expense(household_id: Id, expense_id: Id, service: Service) -> Response:
    """Deletes an expense recorded by mistake. Balances are recalculated immediately."""
    service.delete_expense(household_id, expense_id)
    return Response(status_code=204)
