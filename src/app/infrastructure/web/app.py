from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session

from app.application.expense_service import ExpenseService
from app.application.household_service import HouseholdService
from app.application.settlement_service import SettlementService
from app.infrastructure import config
from app.infrastructure.database import create_schema as create_db_schema
from app.infrastructure.database import make_engine, make_session_factory
from app.infrastructure.persistence.expense_repository import SqlAlchemyExpenseRepository
from app.infrastructure.persistence.household_repository import SqlAlchemyHouseholdRepository
from app.infrastructure.persistence.settlement_repository import SqlAlchemySettlementRepository
from app.interfaces.api import dependencies, expenses, households, settlements
from app.interfaces.api.errors import register_error_handlers


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


def create_app(database_url: str | None = None, create_schema: bool | None = None) -> FastAPI:
    url = database_url or config.database_url()
    engine = make_engine(url)
    if create_schema if create_schema is not None else url.startswith("sqlite"):
        create_db_schema(engine)

    app = FastAPI(
        title=config.API_TITLE, version=config.API_VERSION, description=config.API_DESCRIPTION
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

    app.dependency_overrides[dependencies.household_service] = household_service
    app.dependency_overrides[dependencies.expense_service] = expense_service
    app.dependency_overrides[dependencies.settlement_service] = settlement_service
    app.include_router(households.router)
    app.include_router(expenses.router)
    app.include_router(settlements.router)
    register_error_handlers(app)

    @app.get("/health", tags=["ops"])
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app
