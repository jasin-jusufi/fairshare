from typing import Any

from app.interfaces.api.schemas import ErrorOut

TAGS: list[dict[str, Any]] = [
    {
        "name": "Households",
        "description": "Create households and manage members (UC-001). "
        "Every other resource belongs to a household.",
    },
    {
        "name": "Expenses",
        "description": "Record shared expenses and split them (UC-002): equally, by percent "
        "or by shares. Leftover cents are distributed by largest remainder.",
    },
    {
        "name": "Settle-up",
        "description": "Balances, settle-up suggestions with at most n − 1 transfers and "
        "recorded settlements (UC-003).",
    },
    {
        "name": "Chores",
        "description": "Chores with effort 1–5 and fair weekly planning based on past load "
        "(UC-004).",
    },
    {"name": "Operations", "description": "Health check for containers, Render and smoke tests."},
]

Responses = dict[int | str, dict[str, Any]]


def error(status: int, description: str) -> Responses:
    return {status: {"model": ErrorOut, "description": description}}


NOT_FOUND = error(404, "Household or resource does not exist")
INVALID = error(400, "Business rule violated, e.g. empty name or invalid amount")
CONFLICT = error(409, "Conflicts with the current state, e.g. a duplicate")
