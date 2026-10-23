from fastapi.testclient import TestClient


def test_docs_page_is_custom_fairshare_reference(client: TestClient) -> None:
    r = client.get("/docs")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "FairShare API" in r.text
    assert "/openapi.json" in r.text


def test_swagger_ui_remains_available(client: TestClient) -> None:
    r = client.get("/swagger")
    assert r.status_code == 200
    assert "swagger-ui" in r.text.lower()


def test_openapi_is_documented_for_humans(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    tags = {t["name"]: t for t in spec["tags"]}
    assert set(tags) == {"Haushalte", "Ausgaben", "Abrechnen", "Ämtli", "Betrieb"}
    assert all(t["description"] for t in tags.values())
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            assert operation.get("summary"), f"{method.upper()} {path} has no summary"
            assert operation.get("description"), f"{method.upper()} {path} has no description"
            assert operation["tags"][0] in tags


def test_error_responses_are_documented(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    create_expense = spec["paths"]["/households/{household_id}/expenses"]["post"]
    assert {"400", "404"} <= set(create_expense["responses"])
    assert "ErrorOut" in spec["components"]["schemas"]


def test_request_schemas_carry_examples(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()["components"]["schemas"]["ExpenseCreate"]
    assert schema["properties"]["amount_cents"]["examples"] == [9000]
