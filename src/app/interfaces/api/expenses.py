from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.application.expense_service import ExpenseService, Participant
from app.domain.expense import Expense
from app.interfaces.api.dependencies import expense_service
from app.interfaces.api.openapi import INVALID, NOT_FOUND
from app.interfaces.api.schemas import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/households/{household_id}/expenses", tags=["Ausgaben"])
Service = Annotated[ExpenseService, Depends(expense_service)]


@router.post(
    "",
    response_model=ExpenseOut,
    status_code=201,
    summary="Ausgabe erfassen",
    responses={**INVALID, **NOT_FOUND},
)
def record_expense(household_id: int, payload: ExpenseCreate, service: Service) -> Expense:
    """Erfasst eine Ausgabe und berechnet die Anteile.

    - `equal`: gleich verteilt, `weight` wird ignoriert
    - `percent`: `weight` sind Prozent und müssen zusammen 100 ergeben
    - `shares`: `weight` sind Gewichte, z. B. 2 : 1 : 1

    Übrig bleibende Rappen erhalten die Beteiligten mit dem grössten Bruchteil
    (Largest-Remainder). Die Summe der Anteile entspricht immer exakt dem Betrag.
    """
    return service.record_expense(
        household_id,
        payload.payer_id,
        payload.description,
        payload.amount_cents,
        payload.method,
        [Participant(p.member_id, p.weight) for p in payload.participants],
    )


@router.get("", response_model=list[ExpenseOut], summary="Ausgaben auflisten", responses=NOT_FOUND)
def list_expenses(household_id: int, service: Service) -> list[Expense]:
    """Alle Ausgaben des Haushalts in Erfassungsreihenfolge, inklusive Anteile."""
    return service.list_expenses(household_id)


@router.delete("/{expense_id}", status_code=204, summary="Ausgabe löschen", responses=NOT_FOUND)
def delete_expense(household_id: int, expense_id: int, service: Service) -> Response:
    """Löscht eine Fehlerfassung. Salden werden sofort neu berechnet."""
    service.delete_expense(household_id, expense_id)
    return Response(status_code=204)
