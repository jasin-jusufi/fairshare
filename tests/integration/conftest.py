from collections.abc import Iterator

import pytest
from app.infrastructure.web.app import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(database_url="sqlite:///:memory:", create_schema=True)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def household(client: TestClient) -> dict:
    return client.post("/households", json={"name": "WG Basel"}).json()
