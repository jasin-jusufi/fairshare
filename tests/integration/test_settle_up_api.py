import pytest
from fastapi.testclient import TestClient

from .helpers import pay


@pytest.fixture
def lea_paid_for_all(client: TestClient, household: dict, members: dict) -> None:
    pay(client, household["id"], members["Lea"], 9000, list(members.values()))


def balances(client: TestClient, household_id: int) -> dict[str, int]:
    r = client.get(f"/households/{household_id}/balances")
    assert r.status_code == 200
    return {b["name"]: b["balance_cents"] for b in r.json()}


def transfers(client: TestClient, household_id: int) -> list[tuple[str, str, int]]:
    r = client.get(f"/households/{household_id}/settle-up")
    assert r.status_code == 200
    return [(t["from_name"], t["to_name"], t["amount_cents"]) for t in r.json()]


def settle(client: TestClient, household_id: int, frm: int, to: int, amount: int) -> int:
    r = client.post(
        f"/households/{household_id}/settlements",
        json={"from_member_id": frm, "to_member_id": to, "amount_cents": amount},
    )
    return r.status_code


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac1_balances(client: TestClient, household: dict) -> None:
    assert balances(client, household["id"]) == {"Lea": 6000, "Noah": -3000, "Mia": -3000}


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac2_suggested_transfers(client: TestClient, household: dict) -> None:
    assert transfers(client, household["id"]) == [("Noah", "Lea", 3000), ("Mia", "Lea", 3000)]


def test_ac3_chain_debts_collapse_to_one_transfer(
    client: TestClient, household: dict, members: dict
) -> None:
    pay(client, household["id"], members["Lea"], 1000, [members["Noah"]])
    pay(client, household["id"], members["Noah"], 1000, [members["Mia"]])
    assert transfers(client, household["id"]) == [("Mia", "Lea", 1000)]


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac4_record_settlement_updates_balances(
    client: TestClient, household: dict, members: dict
) -> None:
    assert settle(client, household["id"], members["Noah"], members["Lea"], 3000) == 201
    assert balances(client, household["id"])["Noah"] == 0
    assert transfers(client, household["id"]) == [("Mia", "Lea", 3000)]


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac5_overpayment_is_rejected(client: TestClient, household: dict, members: dict) -> None:
    assert settle(client, household["id"], members["Noah"], members["Lea"], 3500) == 400
    assert settle(client, household["id"], members["Lea"], members["Noah"], 100) == 400


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac6_invalid_settlements(client: TestClient, household: dict, members: dict) -> None:
    assert settle(client, household["id"], members["Noah"], members["Noah"], 100) == 400
    assert settle(client, household["id"], members["Noah"], members["Lea"], 0) == 400
    assert settle(client, household["id"], members["Noah"], 999, 100) == 400


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac7_nothing_to_settle_when_balanced(
    client: TestClient, household: dict, members: dict
) -> None:
    settle(client, household["id"], members["Noah"], members["Lea"], 3000)
    settle(client, household["id"], members["Mia"], members["Lea"], 3000)
    assert transfers(client, household["id"]) == []
    assert set(balances(client, household["id"]).values()) == {0}


@pytest.mark.usefixtures("lea_paid_for_all")
def test_ac8_list_settlements(client: TestClient, household: dict, members: dict) -> None:
    settle(client, household["id"], members["Noah"], members["Lea"], 1000)
    settle(client, household["id"], members["Mia"], members["Lea"], 2000)
    r = client.get(f"/households/{household['id']}/settlements")
    assert r.status_code == 200
    assert [s["amount_cents"] for s in r.json()] == [1000, 2000]


def test_unknown_household(client: TestClient) -> None:
    assert client.get("/households/999/balances").status_code == 404
    assert client.get("/households/999/settle-up").status_code == 404
