from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient

from app.application.ports.receipt_parser import ReceiptReading
from app.infrastructure.web.app import create_app
from app.interfaces.api import dependencies

PNG = b"\x89PNG\r\n\x1a\n" + bytes(32)
JPEG = b"\xff\xd8\xff\xe0" + bytes(32)
PDF = b"%PDF-1.7\n" + bytes(32)
FIVE_MB = 5 * 1024 * 1024


class NoAmountParser:
    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        return ReceiptReading(merchant="Migros", total_cents=None)


@pytest.fixture(autouse=True)
def receipt_parser_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RECEIPT_PARSER", raising=False)


@pytest.fixture
def demo(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("RECEIPT_PARSER", "fake")
    with TestClient(create_app(database_url="sqlite:///:memory:", create_schema=True)) as c:
        yield c


def new_household(client: TestClient) -> int:
    return int(client.post("/households", json={"name": "Flat Basel"}).json()["id"])


def scan(
    client: TestClient,
    household_id: int,
    content: bytes,
    filename: str = "receipt.png",
    media_type: str = "image/png",
) -> httpx.Response:
    return client.post(
        f"/households/{household_id}/receipts", files={"file": (filename, content, media_type)}
    )


@pytest.mark.parametrize(
    ("content", "filename", "media_type"),
    [(PNG, "receipt.png", "image/png"), (JPEG, "receipt.jpg", "image/jpeg")],
)
def test_ac1_fake_parser_suggests_description_and_amount(
    demo: TestClient, content: bytes, filename: str, media_type: str
) -> None:
    r = scan(demo, new_household(demo), content, filename, media_type)
    assert r.status_code == 200
    assert r.json() == {"description": "Migros", "amount_cents": 2350}


@pytest.mark.parametrize(
    ("content", "media_type"),
    [
        (PDF, "application/pdf"),
        (PDF, "image/png"),
        (b"", "image/png"),
        (PNG + bytes(FIVE_MB), "image/png"),
    ],
    ids=["pdf", "pdf-sent-as-png", "empty", "larger-than-5-mb"],
)
def test_ac2_only_jpeg_and_png_up_to_5_mb(
    demo: TestClient, content: bytes, media_type: str
) -> None:
    assert scan(demo, new_household(demo), content, "receipt", media_type).status_code == 400


def test_ac2_image_of_exactly_5_mb_is_accepted(demo: TestClient) -> None:
    image = PNG + bytes(FIVE_MB - len(PNG))
    assert scan(demo, new_household(demo), image).status_code == 200


def test_ac3_receipt_without_amount_is_unreadable(client: TestClient, household: dict) -> None:
    client.app.dependency_overrides[dependencies.receipt_parser] = NoAmountParser
    r = scan(client, household["id"], PNG)
    assert r.status_code == 422
    assert r.json() == {"detail": "No amount found on the receipt"}


def test_ac4_scanning_is_switched_off_by_default(client: TestClient, household: dict) -> None:
    r = scan(client, household["id"], PNG)
    assert r.status_code == 503
    assert "RECEIPT_PARSER" in r.json()["detail"]


def test_ac5_a_suggestion_records_no_expense(demo: TestClient) -> None:
    household_id = new_household(demo)
    assert scan(demo, household_id, PNG).status_code == 200
    assert demo.get(f"/households/{household_id}/expenses").json() == []


def test_ac6_unknown_household(demo: TestClient) -> None:
    assert scan(demo, 999, PNG).status_code == 404


def test_upload_without_file_is_rejected(demo: TestClient) -> None:
    assert demo.post(f"/households/{new_household(demo)}/receipts").status_code == 422


def test_unknown_receipt_parser_stops_the_app(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RECEIPT_PARSER", "gpt")
    with pytest.raises(ValueError, match="RECEIPT_PARSER"):
        create_app(database_url="sqlite:///:memory:", create_schema=True)


def test_receipt_endpoint_is_documented(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    operation = spec["paths"]["/households/{household_id}/receipts"]["post"]
    assert operation["tags"] == ["Receipts"]
    assert {"400", "404", "422", "503"} <= set(operation["responses"])
    assert "multipart/form-data" in operation["requestBody"]["content"]
