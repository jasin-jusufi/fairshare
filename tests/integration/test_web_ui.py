from fastapi.testclient import TestClient


def test_root_redirects_to_ui(client: TestClient) -> None:
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == "/ui/"


def test_ui_is_served(client: TestClient) -> None:
    r = client.get("/ui/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "FairShare" in r.text
