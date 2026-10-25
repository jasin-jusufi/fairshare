import random

from fastapi.testclient import TestClient

from tests.integration.helpers import pay


def balances(client: TestClient, household_id: int) -> dict[str, int]:
    return {
        b["name"]: b["balance_cents"]
        for b in client.get(f"/households/{household_id}/balances").json()
    }


def random_percentages(rng: random.Random, count: int) -> list[int]:
    cuts = sorted(rng.sample(range(1, 100), count - 1))
    return [b - a for a, b in zip([0, *cuts], [*cuts, 100], strict=True)]


def test_recording_every_suggested_transfer_settles_everyone(
    client: TestClient, household: dict
) -> None:
    """End-to-end property: 40 random expenses with all three split methods, then every
    suggested transfer is recorded. The overpayment check must never block a transfer the
    app itself suggested, and afterwards every balance must be exactly 0."""
    rng = random.Random(7)
    hid = household["id"]
    ids = [
        client.post(f"/households/{hid}/members", json={"name": f"Member {i}"}).json()["id"]
        for i in range(6)
    ]
    for _ in range(40):
        people = rng.sample(ids, rng.randint(1, len(ids)))
        method = rng.choice(["equal", "percent", "shares"])
        weights = (
            random_percentages(rng, len(people))
            if method == "percent"
            else [rng.randint(1, 5) for _ in people]
        )
        r = client.post(
            f"/households/{hid}/expenses",
            json={
                "payer_id": rng.choice(ids),
                "description": "Random",
                "amount_cents": rng.randint(1, 50_000),
                "method": method,
                "participants": [
                    {"member_id": m, "weight": w} for m, w in zip(people, weights, strict=True)
                ],
            },
        )
        assert r.status_code == 201, r.text
        assert sum(balances(client, hid).values()) == 0

    transfers = client.get(f"/households/{hid}/settle-up").json()
    assert len(transfers) <= len(ids) - 1
    for t in transfers:
        body = {k: t[k] for k in ("from_member_id", "to_member_id", "amount_cents")}
        assert client.post(f"/households/{hid}/settlements", json=body).status_code == 201

    assert set(balances(client, hid).values()) == {0}
    assert client.get(f"/households/{hid}/settle-up").json() == []


def test_deleting_an_already_settled_expense_reverses_the_debt(
    client: TestClient, household: dict, members: dict
) -> None:
    """Edge case of 'delete expense': Noah already paid Lea back, then the expense is
    deleted as a mistake. Now Lea owes Noah the money, and settle-up must say so."""
    hid = household["id"]
    expense = pay(client, hid, members["Lea"], 9000, list(members.values()))
    client.post(
        f"/households/{hid}/settlements",
        json={
            "from_member_id": members["Noah"],
            "to_member_id": members["Lea"],
            "amount_cents": 3000,
        },
    )

    assert client.delete(f"/households/{hid}/expenses/{expense['id']}").status_code == 204

    assert balances(client, hid) == {"Lea": -3000, "Noah": 3000, "Mia": 0}
    [transfer] = client.get(f"/households/{hid}/settle-up").json()
    assert (transfer["from_name"], transfer["to_name"], transfer["amount_cents"]) == (
        "Lea",
        "Noah",
        3000,
    )
