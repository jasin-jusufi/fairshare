from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_ac1_create_household(client: TestClient) -> None:
    r = client.post("/households", json={"name": "Flat Basel"})
    assert r.status_code == 201
    body = r.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Flat Basel"
    assert body["currency"] == "CHF"
    assert body["members"] == []


def test_ac2_add_member(client: TestClient, household: dict) -> None:
    r = client.post(f"/households/{household['id']}/members", json={"name": "Lea"})
    assert r.status_code == 201
    body = r.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Lea"


def test_ac3_duplicate_member_name_is_rejected(client: TestClient, household: dict) -> None:
    client.post(f"/households/{household['id']}/members", json={"name": "Lea"})
    r = client.post(f"/households/{household['id']}/members", json={"name": "lea"})
    assert r.status_code == 409


def test_ac4_blank_names_are_rejected(client: TestClient, household: dict) -> None:
    assert client.post("/households", json={"name": "   "}).status_code == 400
    r = client.post(f"/households/{household['id']}/members", json={"name": ""})
    assert r.status_code == 400


def test_ac5_unknown_household(client: TestClient) -> None:
    assert client.get("/households/999").status_code == 404
    assert client.post("/households/999/members", json={"name": "Lea"}).status_code == 404


def test_ac6_list_households_in_creation_order(client: TestClient) -> None:
    client.post("/households", json={"name": "Flat Basel"})
    client.post("/households", json={"name": "Flat Olten"})
    names = [h["name"] for h in client.get("/households").json()]
    assert names == ["Flat Basel", "Flat Olten"]


def test_ac7_get_household_with_members(client: TestClient, household: dict) -> None:
    for name in ("Lea", "Noah"):
        client.post(f"/households/{household['id']}/members", json={"name": name})
    r = client.get(f"/households/{household['id']}")
    assert r.status_code == 200
    assert [m["name"] for m in r.json()["members"]] == ["Lea", "Noah"]
