from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.errors import NotFoundError
from app.domain.errors import DomainError, DuplicateMemberError

STATUS_BY_ERROR: list[tuple[type[Exception], int]] = [
    (NotFoundError, 404),
    (DuplicateMemberError, 409),
    (DomainError, 400),
]


def register_error_handlers(app: FastAPI) -> None:
    for error_type, status in STATUS_BY_ERROR:

        def handler(_: Request, exc: Exception, status: int = status) -> JSONResponse:
            return JSONResponse(status_code=status, content={"detail": str(exc)})

        app.add_exception_handler(error_type, handler)
