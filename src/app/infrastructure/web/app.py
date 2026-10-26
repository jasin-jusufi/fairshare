from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.application.chore_service import ChoreService
from app.application.expense_service import ExpenseService
from app.application.household_service import HouseholdService
from app.application.ports.receipt_parser import ReceiptParser
from app.application.receipt_service import ReceiptService
from app.application.settlement_service import SettlementService
from app.infrastructure import config
from app.infrastructure.database import create_schema as create_db_schema
from app.infrastructure.database import make_engine, make_session_factory
from app.infrastructure.persistence.chore_repository import (
    SqlAlchemyChoreAssignmentRepository,
    SqlAlchemyChoreRepository,
)
from app.infrastructure.persistence.expense_repository import SqlAlchemyExpenseRepository
from app.infrastructure.persistence.household_repository import SqlAlchemyHouseholdRepository
from app.infrastructure.persistence.settlement_repository import SqlAlchemySettlementRepository
from app.infrastructure.receipt_parsers import make_receipt_parser
from app.interfaces.api import chores, dependencies, expenses, households, receipts, settlements
from app.interfaces.api.errors import register_error_handlers
from app.interfaces.api.openapi import TAGS

STATIC_DIR = Path(__file__).parent / "static"


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


def create_app(database_url: str | None = None, create_schema: bool | None = None) -> FastAPI:
    url = database_url or config.database_url()
    parser = make_receipt_parser(config.receipt_parser_mode())
    engine = make_engine(url)
    if create_schema if create_schema is not None else url.startswith("sqlite"):
        create_db_schema(engine)

    app = FastAPI(
        title=config.API_TITLE,
        version=config.API_VERSION,
        description=config.API_DESCRIPTION,
        openapi_tags=TAGS,
        docs_url=None,
    )
    app.state.session_factory = make_session_factory(engine)

    def household_service(session: DbSession) -> HouseholdService:
        return HouseholdService(SqlAlchemyHouseholdRepository(session))

    def expense_service(session: DbSession) -> ExpenseService:
        return ExpenseService(
            SqlAlchemyHouseholdRepository(session), SqlAlchemyExpenseRepository(session)
        )

    def settlement_service(session: DbSession) -> SettlementService:
        return SettlementService(
            SqlAlchemyHouseholdRepository(session),
            SqlAlchemyExpenseRepository(session),
            SqlAlchemySettlementRepository(session),
        )

    def chore_service(session: DbSession) -> ChoreService:
        return ChoreService(
            SqlAlchemyHouseholdRepository(session),
            SqlAlchemyChoreRepository(session),
            SqlAlchemyChoreAssignmentRepository(session),
        )

    def receipt_service(
        session: DbSession,
        receipt_parser: Annotated[ReceiptParser, Depends(dependencies.receipt_parser)],
    ) -> ReceiptService:
        return ReceiptService(SqlAlchemyHouseholdRepository(session), receipt_parser)

    app.dependency_overrides[dependencies.household_service] = household_service
    app.dependency_overrides[dependencies.expense_service] = expense_service
    app.dependency_overrides[dependencies.settlement_service] = settlement_service
    app.dependency_overrides[dependencies.chore_service] = chore_service
    app.dependency_overrides[dependencies.receipt_parser] = lambda: parser
    app.dependency_overrides[dependencies.receipt_service] = receipt_service
    app.include_router(households.router)
    app.include_router(expenses.router)
    app.include_router(settlements.router)
    app.include_router(chores.router)
    app.include_router(receipts.router)
    register_error_handlers(app)

    @app.get("/health", tags=["Operations"], summary="Health check")
    def health() -> dict[str, str]:
        """Responds with `healthy` once the app and its configuration are loaded."""
        return {"status": "healthy"}

    @app.get("/docs", include_in_schema=False)
    def api_reference() -> FileResponse:
        return FileResponse(STATIC_DIR / "docs.html")

    @app.get("/swagger", include_in_schema=False)
    def swagger() -> HTMLResponse:
        return get_swagger_ui_html(openapi_url="/openapi.json", title="FairShare API – Swagger")

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse("/ui/")

    app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")

    return app
