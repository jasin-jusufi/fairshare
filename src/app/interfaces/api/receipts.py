from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.application.receipt_service import MAX_IMAGE_BYTES, ReceiptService
from app.domain.receipt import ReceiptSuggestion
from app.interfaces.api.dependencies import receipt_scanning_mode, receipt_service
from app.interfaces.api.openapi import INVALID, NOT_FOUND, UNAVAILABLE, UNREADABLE
from app.interfaces.api.params import Id
from app.interfaces.api.schemas import ReceiptScanningOut, ReceiptSuggestionOut

router = APIRouter(prefix="/households/{household_id}/receipts", tags=["Receipts"])
status_router = APIRouter(tags=["Receipts"])
Service = Annotated[ReceiptService, Depends(receipt_service)]
Image = Annotated[UploadFile, File(description="Photo of the receipt: JPEG or PNG, at most 5 MB")]


@router.post(
    "",
    response_model=ReceiptSuggestionOut,
    summary="Scan receipt",
    responses={**INVALID, **NOT_FOUND, **UNREADABLE, **UNAVAILABLE},
)
def scan_receipt(household_id: Id, file: Image, service: Service) -> ReceiptSuggestion:
    """Suggests a description and an amount from a photo of a receipt. **Nothing is
    stored**: the client pre-fills the expense form and records the expense with
    `POST /households/{household_id}/expenses` once the member has checked it.

    `RECEIPT_PARSER` selects the parser: `none` (default) answers 503, `fake`
    returns the demo suggestion "Migros", 2350 cents for every image (ADR-008),
    `ollama` uses a local vision model (ADR-009) and `claude` the Anthropic API
    (ADR-010)."""
    return service.suggest(household_id, file.file.read(MAX_IMAGE_BYTES + 1))


@status_router.get(
    "/receipt-scanning", response_model=ReceiptScanningOut, summary="Receipt scanning status"
)
def scanning_status(mode: Annotated[str, Depends(receipt_scanning_mode)]) -> ReceiptScanningOut:
    """Tells clients whether receipt scanning is available on this server, so the UI
    can explain it before anyone uploads a photo. Uploads nothing and calls no model."""
    return ReceiptScanningOut(enabled=mode != "none", mode=mode)
