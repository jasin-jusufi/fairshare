from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.web.app import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(database_url="sqlite:///:memory:", create_schema=True)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def household(client: TestClient) -> dict:
    return client.post("/households", json={"name": "WG Basel"}).json()


@pytest.fixture
def members(client: TestClient, household: dict) -> dict[str, int]:
    ids = {}
    for name in ("Lea", "Noah", "Mia"):
        r = client.post(f"/households/{household['id']}/members", json={"name": name})
        ids[name] = r.json()["id"]
    return ids
