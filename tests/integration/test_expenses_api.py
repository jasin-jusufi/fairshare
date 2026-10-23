from fastapi.testclient import TestClient


def expense(payer: int, amount: int, method: str, participants: list, desc: str = "Migros") -> dict:
    return {
        "payer_id": payer,
        "description": desc,
        "amount_cents": amount,
        "method": method,
        "participants": participants,
    }


def shares_of(body: dict) -> list[int]:
    return [s["amount_cents"] for s in body["shares"]]


def test_ac1_equal_split_distributes_remainder(
    client: TestClient, household: dict, members: dict
) -> None:
    participants = [{"member_id": m} for m in members.values()]
    r = client.post(
        f"/households/{household['id']}/expenses",
        json=expense(members["Lea"], 10000, "equal", participants),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["payer_id"] == members["Lea"]
    assert body["method"] == "equal"
    assert shares_of(body) == [3334, 3333, 3333]
    assert sum(shares_of(body)) == 10000


def test_ac2_percent_split(client: TestClient, household: dict, members: dict) -> None:
    participants = [
        {"member_id": members["Lea"], "weight": 70},
        {"member_id": members["Noah"], "weight": 30},
    ]
    r = client.post(
        f"/households/{household['id']}/expenses",
        json=expense(members["Noah"], 5000, "percent", participants),
    )
    assert r.status_code == 201
    assert shares_of(r.json()) == [3500, 1500]


def test_ac3_weighted_split(client: TestClient, household: dict, members: dict) -> None:
    participants = [
        {"member_id": members["Lea"], "weight": 2},
        {"member_id": members["Noah"], "weight": 1},
        {"member_id": members["Mia"], "weight": 1},
    ]
    r = client.post(
        f"/households/{household['id']}/expenses",
        json=expense(members["Mia"], 1000, "shares", participants),
    )
    assert r.status_code == 201
    assert shares_of(r.json()) == [500, 250, 250]


def test_ac4_percent_must_sum_to_100(client: TestClient, household: dict, members: dict) -> None:
    participants = [
        {"member_id": members["Lea"], "weight": 60},
        {"member_id": members["Noah"], "weight": 30},
    ]
    r = client.post(
        f"/households/{household['id']}/expenses",
        json=expense(members["Lea"], 1000, "percent", participants),
    )
    assert r.status_code == 400


def test_ac5_members_must_belong_to_household(
    client: TestClient, household: dict, members: dict
) -> None:
    other = client.post("/households", json={"name": "Other Flat"}).json()
    stranger = client.post(f"/households/{other['id']}/members", json={"name": "Max"}).json()
    url = f"/households/{household['id']}/expenses"
    as_payer = expense(stranger["id"], 1000, "equal", [{"member_id": members["Lea"]}])
    as_participant = expense(members["Lea"], 1000, "equal", [{"member_id": stranger["id"]}])
    assert client.post(url, json=as_payer).status_code == 400
    assert client.post(url, json=as_participant).status_code == 400


def test_ac6_amount_and_description_are_validated(
    client: TestClient, household: dict, members: dict
) -> None:
    url = f"/households/{household['id']}/expenses"
    participants = [{"member_id": members["Lea"]}]
    zero = expense(members["Lea"], 0, "equal", participants)
    blank = expense(members["Lea"], 100, "equal", participants, desc=" ")
    assert client.post(url, json=zero).status_code == 400
    assert client.post(url, json=blank).status_code == 400


def test_ac7_list_expenses(client: TestClient, household: dict, members: dict) -> None:
    url = f"/households/{household['id']}/expenses"
    participants = [{"member_id": m} for m in members.values()]
    client.post(url, json=expense(members["Lea"], 3000, "equal", participants, desc="Migros"))
    client.post(url, json=expense(members["Noah"], 6000, "equal", participants, desc="Internet"))
    body = client.get(url).json()
    assert [e["description"] for e in body] == ["Migros", "Internet"]
    assert shares_of(body[1]) == [2000, 2000, 2000]


def test_ac8_delete_expense(client: TestClient, household: dict, members: dict) -> None:
    url = f"/households/{household['id']}/expenses"
    created = client.post(
        url, json=expense(members["Lea"], 3000, "equal", [{"member_id": members["Lea"]}])
    ).json()
    assert client.delete(f"{url}/{created['id']}").status_code == 204
    assert client.get(url).json() == []
    assert client.delete(f"{url}/{created['id']}").status_code == 404


def test_expenses_of_unknown_household(client: TestClient) -> None:
    assert client.get("/households/999/expenses").status_code == 404
