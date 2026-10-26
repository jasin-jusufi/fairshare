import pytest
from fastapi.testclient import TestClient


def expense_body(members: dict[str, int], **overrides: object) -> dict:
    body: dict = {
        "payer_id": members["Lea"],
        "description": "Migros",
        "amount_cents": 3000,
        "method": "equal",
        "participants": [{"member_id": m} for m in members.values()],
    }
    body.update(overrides)
    return body


@pytest.mark.parametrize(
    "body",
    [{"name": 123}, {"name": None}, {"name": ["Flat"]}, {}, ["Flat"]],
    ids=["number", "null", "list", "missing", "body-is-list"],
)
def test_household_with_wrong_types_is_rejected_with_422(client: TestClient, body: object) -> None:
    """Wrong data types never reach the domain: the API answers 422 with a field error."""
    assert client.post("/households", json=body).status_code == 422


def test_malformed_json_is_rejected_with_422(client: TestClient) -> None:
    """A body that is not valid JSON at all must be a client error, not a crash."""
    r = client.post(
        "/households", content="{name: Flat", headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 422


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount_cents": "abc"},
        {"amount_cents": 12.5},
        {"amount_cents": None},
        {"amount_cents": [3000]},
        {"description": 42},
        {"method": "EQUAL"},
        {"method": "split"},
        {"participants": "Lea"},
        {"participants": [{"member_id": "Lea"}]},
    ],
    ids=[
        "amount-text",
        "amount-fraction-of-a-cent",
        "amount-null",
        "amount-list",
        "description-number",
        "method-uppercase",
        "method-unknown",
        "participants-text",
        "participant-id-text",
    ],
)
def test_expense_with_wrong_types_is_rejected_with_422(
    client: TestClient, household: dict, members: dict, overrides: dict
) -> None:
    """Every field of an expense with a wrong type; 12.5 cents is a valid number but not
    a whole cent, so it must be rejected too (ADR-004: money is integer cents)."""
    r = client.post(
        f"/households/{household['id']}/expenses", json=expense_body(members, **overrides)
    )
    assert r.status_code == 422


@pytest.mark.parametrize("field", ["payer_id", "description", "amount_cents", "participants"])
def test_expense_without_required_field_is_rejected_with_422(
    client: TestClient, household: dict, members: dict, field: str
) -> None:
    """Each required field left out on its own."""
    body = expense_body(members)
    del body[field]
    assert client.post(f"/households/{household['id']}/expenses", json=body).status_code == 422


@pytest.mark.parametrize("effort", ["five", 2.5, None], ids=["text", "fraction", "null"])
def test_chore_with_wrong_effort_type_is_rejected_with_422(
    client: TestClient, household: dict, effort: object
) -> None:
    """Effort must be a whole number; text, fractions and null are type errors."""
    r = client.post(f"/households/{household['id']}/chores", json={"name": "X", "effort": effort})
    assert r.status_code == 422


@pytest.mark.parametrize(
    "week", ["2026-02-30", "26.10.2026", ""], ids=["impossible-date", "swiss-format", "empty"]
)
def test_week_plan_with_invalid_date_is_rejected_with_422(
    client: TestClient, household: dict, week: str
) -> None:
    """Only ISO dates (YYYY-MM-DD) that exist in the calendar are accepted."""
    r = client.post(f"/households/{household['id']}/chore-plans", json={"week_start": week})
    assert r.status_code == 422


@pytest.mark.parametrize("path", ["/households/abc", "/households/1.5/expenses"])
def test_non_numeric_ids_in_the_url_are_rejected_with_422(client: TestClient, path: str) -> None:
    """IDs in the path are integers; anything else is a client error."""
    assert client.get(path).status_code == 422


@pytest.mark.parametrize("field", ["amount_cents", "payer_id"])
def test_boolean_is_not_accepted_as_a_number_in_expenses(
    client: TestClient, household: dict, members: dict, field: str
) -> None:
    """JSON `true` is not a number. Today it is silently turned into 1: an expense of
    1 cent, or member 1 as payer, although the client never sent that."""
    r = client.post(
        f"/households/{household['id']}/expenses", json=expense_body(members, **{field: True})
    )
    assert r.status_code == 422


def test_boolean_is_not_accepted_as_chore_effort(client: TestClient, household: dict) -> None:
    """Same root cause for chores: `true` becomes effort 1."""
    r = client.post(f"/households/{household['id']}/chores", json={"name": "X", "effort": True})
    assert r.status_code == 422
