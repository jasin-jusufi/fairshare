import pytest
from fastapi.testclient import TestClient

CHORES = [("Bathroom", 5), ("Kitchen", 3), ("Trash", 1), ("Vacuuming", 3)]


@pytest.fixture
def chores(client: TestClient, household: dict, members: dict) -> dict[str, int]:
    ids = {}
    for name, effort in CHORES:
        r = client.post(
            f"/households/{household['id']}/chores", json={"name": name, "effort": effort}
        )
        ids[name] = r.json()["id"]
    return ids


def plan(client: TestClient, household_id: int, week: str) -> tuple[int, dict]:
    r = client.post(f"/households/{household_id}/chore-plans", json={"week_start": week})
    return r.status_code, r.json()


def by_chore(client: TestClient, plan_body: dict, members: dict) -> dict[str, str]:
    names = {v: k for k, v in members.items()}
    return {a["chore_name"]: names[a["member_id"]] for a in plan_body["assignments"]}


def test_ac1_add_chore(client: TestClient, household: dict) -> None:
    r = client.post(f"/households/{household['id']}/chores", json={"name": "Bathroom", "effort": 5})
    assert r.status_code == 201
    body = r.json()
    assert isinstance(body["id"], int)
    assert (body["name"], body["effort"]) == ("Bathroom", 5)
    assert client.get(f"/households/{household['id']}/chores").json() == [body]


@pytest.mark.parametrize("effort", [0, 6])
def test_ac2_effort_must_be_between_1_and_5(
    client: TestClient, household: dict, effort: int
) -> None:
    r = client.post(f"/households/{household['id']}/chores", json={"name": "X", "effort": effort})
    assert r.status_code == 400


@pytest.mark.usefixtures("chores")
def test_ac3_heaviest_chore_goes_to_least_loaded_member(
    client: TestClient, household: dict, members: dict
) -> None:
    status, body = plan(client, household["id"], "2026-10-26")
    assert status == 201
    assert by_chore(client, body, members) == {
        "Bathroom": "Lea",
        "Kitchen": "Noah",
        "Vacuuming": "Mia",
        "Trash": "Noah",
    }


@pytest.mark.usefixtures("chores")
def test_ac4_history_balances_load_over_weeks(
    client: TestClient, household: dict, members: dict
) -> None:
    plan(client, household["id"], "2026-10-26")
    plan(client, household["id"], "2026-11-02")
    load = client.get(f"/households/{household['id']}/chore-load").json()
    assert {entry["effort_points"] for entry in load} == {8}


@pytest.mark.usefixtures("chores")
def test_ac5_week_cannot_be_planned_twice(client: TestClient, household: dict) -> None:
    assert plan(client, household["id"], "2026-10-26")[0] == 201
    assert plan(client, household["id"], "2026-10-28")[0] == 409


@pytest.mark.usefixtures("chores")
def test_ac6_any_date_is_normalised_to_monday(client: TestClient, household: dict) -> None:
    status, body = plan(client, household["id"], "2026-10-29")
    assert status == 201
    assert body["week_start"] == "2026-10-26"
    r = client.get(f"/households/{household['id']}/chore-plans/2026-10-26")
    assert r.status_code == 200
    assert len(r.json()["assignments"]) == len(CHORES)


@pytest.mark.usefixtures("chores")
def test_ac7_complete_assignment(client: TestClient, household: dict) -> None:
    _, body = plan(client, household["id"], "2026-10-26")
    assignment_id = body["assignments"][0]["id"]
    url = f"/households/{household['id']}/assignments/{assignment_id}/complete"
    r = client.post(url)
    assert r.status_code == 200
    assert r.json()["completed_at"] is not None
    assert client.post(url).status_code == 409
    assert client.post(f"/households/{household['id']}/assignments/999/complete").status_code == 404


@pytest.mark.usefixtures("members")
def test_ac8_nothing_to_plan(client: TestClient, household: dict) -> None:
    assert plan(client, household["id"], "2026-10-26")[0] == 400


@pytest.mark.usefixtures("chores")
def test_ac9_chore_load_per_member(client: TestClient, household: dict) -> None:
    plan(client, household["id"], "2026-10-26")
    load = client.get(f"/households/{household['id']}/chore-load").json()
    assert [(e["name"], e["effort_points"]) for e in load] == [("Lea", 5), ("Noah", 4), ("Mia", 3)]


def test_unknown_household(client: TestClient) -> None:
    assert client.get("/households/999/chores").status_code == 404
    assert client.get("/households/999/chore-load").status_code == 404
