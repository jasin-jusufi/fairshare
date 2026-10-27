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


def test_expense_form_offers_receipt_scan(client: TestClient) -> None:
    html = client.get("/ui/").text
    assert 'id="receipt-scan"' in html
    assert 'accept="image/jpeg,image/png"' in html
    assert "/receipts" in html


def test_expenses_can_be_corrected_in_the_ui(client: TestClient) -> None:
    html = client.get("/ui/").text
    assert 'id="expense-submit"' in html
    assert 'id="expense-cancel"' in html
    assert "Save changes" in html
    assert 'method: "PUT"' in html


def test_edit_form_uses_the_stored_weights(client: TestClient) -> None:
    assert "share.weight" in client.get("/ui/").text
