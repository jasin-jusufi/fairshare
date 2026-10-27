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


def test_assignments_have_a_labelled_done_button(client: TestClient) -> None:
    html = client.get("/ui/").text
    assert "done-btn" in html
    assert "Done ✓" in html
    assert "missingChores" in html
