"""End-to-end journey against a running container (set BASE_URL)."""

import os
from collections.abc import Iterator

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL")

pytestmark = pytest.mark.skipif(not BASE_URL, reason="BASE_URL not set")


@pytest.fixture(scope="module")
def http() -> Iterator[httpx.Client]:
    with httpx.Client(base_url=BASE_URL or "", timeout=10) as client:
        yield client


def test_health(http: httpx.Client) -> None:
    r = http.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_ui_and_openapi_are_served(http: httpx.Client) -> None:
    assert http.get("/docs").status_code == 200
    assert http.get("/openapi.json").json()["info"]["title"] == "FairShare API"


def test_household_journey(http: httpx.Client) -> None:
    household = http.post("/households", json={"name": "E2E Flat"}).json()
    base = f"/households/{household['id']}"
    lea, noah = (
        http.post(f"{base}/members", json={"name": name}).json()["id"] for name in ("Lea", "Noah")
    )

    r = http.post(
        f"{base}/expenses",
        json={
            "payer_id": lea,
            "description": "Migros",
            "amount_cents": 5000,
            "method": "equal",
            "participants": [{"member_id": lea}, {"member_id": noah}],
        },
    )
    assert r.status_code == 201

    transfers = http.get(f"{base}/settle-up").json()
    assert [(t["from_member_id"], t["to_member_id"], t["amount_cents"]) for t in transfers] == [
        (noah, lea, 2500)
    ]

    r = http.post(
        f"{base}/settlements",
        json={"from_member_id": noah, "to_member_id": lea, "amount_cents": 2500},
    )
    assert r.status_code == 201
    assert http.get(f"{base}/settle-up").json() == []

    http.post(f"{base}/chores", json={"name": "Bathroom", "effort": 5})
    http.post(f"{base}/chores", json={"name": "Trash", "effort": 1})
    plan = http.post(f"{base}/chore-plans", json={"week_start": "2026-10-26"})
    assert plan.status_code == 201
    assert {a["member_id"] for a in plan.json()["assignments"]} == {lea, noah}


def test_receipt_scanning_is_off_by_default(http: httpx.Client) -> None:
    household = http.post("/households", json={"name": "E2E Receipts"}).json()
    png = b"\x89PNG\r\n\x1a\n" + bytes(16)
    r = http.post(
        f"/households/{household['id']}/receipts", files={"file": ("receipt.png", png, "image/png")}
    )
    assert r.status_code == 503
