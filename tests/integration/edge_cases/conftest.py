from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.web.app import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Overrides the integration client: a crash comes back as an HTTP 500 response
    instead of an exception, so edge-case tests can assert that no input causes a 500."""
    app = create_app(database_url="sqlite:///:memory:", create_schema=True)
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
