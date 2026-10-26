import pytest
from fastapi.testclient import TestClient

from tests.integration.helpers import pay
from tests.known_bugs import AMOUNT_OVERFLOW, ID_OVERFLOW

POSTGRES_INTEGER_MAX = 2**31 - 1
SQLITE_INTEGER_MAX = 2**63 - 1


def record(client: TestClient, household_id: int, payer: int, amount: int, **extra: object) -> int:
    body = {"payer_id": payer, "description": "x", "amount_cents": amount, **extra}
    body.setdefault("participants", [{"member_id": payer}])
    return client.post(f"/households/{household_id}/expenses", json=body).status_code


@pytest.mark.parametrize(("length", "status"), [(80, 201), (81, 400)])
def test_member_name_length_boundary(
    client: TestClient, household: dict, length: int, status: int
) -> None:
    """Boundary value analysis over HTTP: last valid and first invalid length."""
    r = client.post(f"/households/{household['id']}/members", json={"name": "x" * length})
    assert r.status_code == status


@pytest.mark.parametrize(("length", "status"), [(120, 201), (121, 400)])
def test_description_length_boundary(
    client: TestClient, household: dict, members: dict, length: int, status: int
) -> None:
    """Same for the expense description (1–120 characters)."""
    lea = members["Lea"]
    assert record(client, household["id"], lea, 100, description="d" * length) == status


def test_one_cent_expense_for_three_people(
    client: TestClient, household: dict, members: dict
) -> None:
    """Smallest amount over HTTP: 201, shares 1/0/0, and balances still add up to 0."""
    expense = pay(client, household["id"], members["Lea"], 1, list(members.values()))
    assert [s["amount_cents"] for s in expense["shares"]] == [1, 0, 0]
    balances = client.get(f"/households/{household['id']}/balances").json()
    assert sum(b["balance_cents"] for b in balances) == 0


def test_settlement_of_exactly_the_open_debt_is_allowed_one_cent_more_is_not(
    client: TestClient, household: dict, members: dict
) -> None:
    """Overpayment rule at its boundary: Noah owes Lea 3000 cents."""
    pay(client, household["id"], members["Lea"], 6000, [members["Lea"], members["Noah"]])
    url = f"/households/{household['id']}/settlements"
    body = {"from_member_id": members["Noah"], "to_member_id": members["Lea"]}
    assert client.post(url, json={**body, "amount_cents": 3001}).status_code == 400
    assert client.post(url, json={**body, "amount_cents": 3000}).status_code == 201


def test_amount_at_the_postgres_integer_limit_is_accepted(
    client: TestClient, household: dict, members: dict
) -> None:
    """Largest amount that fits every supported database (CHF 21'474'836.47)."""
    assert record(client, household["id"], members["Lea"], POSTGRES_INTEGER_MAX) == 201


@pytest.mark.parametrize("household_id", [0, -1])
def test_zero_and_negative_ids_are_not_found(client: TestClient, household_id: int) -> None:
    """IDs start at 1; 0 and negative IDs simply do not exist."""
    assert client.get(f"/households/{household_id}").status_code == 404


def test_expense_cannot_be_deleted_through_another_household(
    client: TestClient, household: dict, members: dict
) -> None:
    """Data isolation: knowing an expense ID is not enough, it has to belong to the
    household in the URL. The expense must still exist afterwards."""
    expense = pay(client, household["id"], members["Lea"], 3000, [members["Lea"]])
    other = client.post("/households", json={"name": "Other Flat"}).json()
    r = client.delete(f"/households/{other['id']}/expenses/{expense['id']}")
    assert r.status_code == 404
    assert len(client.get(f"/households/{household['id']}/expenses").json()) == 1


@pytest.mark.usefixtures("members")
def test_assignment_cannot_be_completed_through_another_household(
    client: TestClient, household: dict
) -> None:
    """Data isolation for chores, same idea as for expenses."""
    hid = household["id"]
    client.post(f"/households/{hid}/chores", json={"name": "Trash", "effort": 1})
    plan = client.post(f"/households/{hid}/chore-plans", json={"week_start": "2026-10-26"}).json()
    other = client.post("/households", json={"name": "Other Flat"}).json()
    aid = plan["assignments"][0]["id"]
    assert client.post(f"/households/{other['id']}/assignments/{aid}/complete").status_code == 404
    week = client.get(f"/households/{hid}/chore-plans/2026-10-26").json()
    assert week["assignments"][0]["completed_at"] is None


@AMOUNT_OVERFLOW
@pytest.mark.parametrize(
    "amount",
    [POSTGRES_INTEGER_MAX + 1, SQLITE_INTEGER_MAX + 1],
    ids=["above-postgres-integer", "above-sqlite-integer"],
)
def test_amount_beyond_the_database_range_is_rejected(
    client: TestClient, household: dict, members: dict, amount: int
) -> None:
    """Amounts have no upper limit. Above 2^63 − 1 SQLite crashes with HTTP 500; above
    2^31 − 1 the `Integer` column overflows in production (PostgreSQL). Expected: 400/422."""
    assert record(client, household["id"], members["Lea"], amount) in (400, 422)


@ID_OVERFLOW
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/households/{big}"),
        ("get", "/households/{big}/balances"),
        ("delete", "/households/{hid}/expenses/{big}"),
        ("post", "/households/{hid}/assignments/{big}/complete"),
    ],
)
def test_ids_beyond_64_bit_are_not_found_instead_of_crashing(
    client: TestClient, household: dict, method: str, path: str
) -> None:
    """An absurdly large ID is just an ID that does not exist: expected 404 (or 422),
    actual HTTP 500 because the database driver cannot convert the number."""
    url = path.format(big=SQLITE_INTEGER_MAX + 1, hid=household["id"])
    assert client.request(method, url).status_code in (404, 422)


@pytest.mark.parametrize("name", ["​", "Lea\x00"], ids=["zero-width-space", "nul-inside"])
def test_member_names_with_invisible_characters_are_rejected(
    client: TestClient, household: dict, name: str
) -> None:
    """HTTP view of BUG-4: today both names are stored with 201."""
    r = client.post(f"/households/{household['id']}/members", json={"name": name})
    assert r.status_code == 400
