from fastapi.testclient import TestClient


def pay(
    client: TestClient, household_id: int, payer: int, amount: int, participants: list[int]
) -> dict:
    r = client.post(
        f"/households/{household_id}/expenses",
        json={
            "payer_id": payer,
            "description": "Groceries",
            "amount_cents": amount,
            "method": "equal",
            "participants": [{"member_id": m} for m in participants],
        },
    )
    assert r.status_code == 201, r.text
    return r.json()
