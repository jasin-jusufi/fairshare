import base64
import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from app.application.errors import ParserUnavailableError
from app.application.ports.receipt_parser import ReceiptReading
from app.infrastructure.receipt_parsers import OllamaReceiptParser, make_receipt_parser

IMAGE = b"\x89PNG\r\n\x1a\nfake-image"


class StubOllama:
    """Minimal stand-in for Ollama's /api/chat endpoint."""

    def __init__(self) -> None:
        self.status = 200
        self.content: Any = {"merchant": "Coop", "total_chf": 23.5}
        self.requests: list[dict[str, Any]] = []


@pytest.fixture
def ollama() -> Iterator[tuple[StubOllama, str]]:
    stub = StubOllama()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers["Content-Length"])
            stub.requests.append({"path": self.path, "body": json.loads(self.rfile.read(length))})
            content = stub.content if isinstance(stub.content, str) else json.dumps(stub.content)
            body = json.dumps({"message": {"role": "assistant", "content": content}}).encode()
            self.send_response(stub.status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: object) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield stub, f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def test_reads_merchant_and_total_in_cents(ollama: tuple[StubOllama, str]) -> None:
    stub, url = ollama
    reading = OllamaReceiptParser(url, "qwen2.5vl:7b").parse(IMAGE, "image/png")
    assert reading == ReceiptReading("Coop", 2350)


def test_sends_image_model_and_json_schema(ollama: tuple[StubOllama, str]) -> None:
    stub, url = ollama
    OllamaReceiptParser(url, "qwen2.5vl:7b").parse(IMAGE, "image/png")
    [request] = stub.requests
    body = request["body"]
    assert request["path"] == "/api/chat"
    assert body["model"] == "qwen2.5vl:7b"
    assert body["stream"] is False
    assert body["options"]["temperature"] == 0
    assert set(body["format"]["properties"]) == {"merchant", "total_chf"}
    assert body["messages"][0]["images"] == [base64.b64encode(IMAGE).decode()]


@pytest.mark.parametrize(
    ("total", "cents"), [(23.5, 2350), (0.1 + 0.2, 30), ("12.95", 1295), (7, 700)]
)
def test_converts_chf_to_cents_without_float_errors(
    ollama: tuple[StubOllama, str], total: object, cents: int
) -> None:
    stub, url = ollama
    stub.content = {"merchant": "Migros", "total_chf": total}
    assert OllamaReceiptParser(url, "m").parse(IMAGE, "image/png").total_cents == cents


@pytest.mark.parametrize(
    "content",
    [
        {"merchant": None, "total_chf": None},
        {"merchant": "Coop", "total_chf": "unknown"},
        "not json at all",
        {"unexpected": True},
    ],
)
def test_unusable_answers_become_an_empty_reading(
    ollama: tuple[StubOllama, str], content: object
) -> None:
    stub, url = ollama
    stub.content = content
    reading = OllamaReceiptParser(url, "m").parse(IMAGE, "image/png")
    assert reading.total_cents is None


def test_missing_model_is_unavailable_with_pull_hint(ollama: tuple[StubOllama, str]) -> None:
    stub, url = ollama
    stub.status = 404
    with pytest.raises(ParserUnavailableError, match="ollama pull m"):
        OllamaReceiptParser(url, "m").parse(IMAGE, "image/png")


def test_unreachable_server_is_unavailable() -> None:
    with pytest.raises(ParserUnavailableError, match="not reachable"):
        OllamaReceiptParser("http://127.0.0.1:9", "m", timeout=2).parse(IMAGE, "image/png")


def test_factory_builds_ollama_parser_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_URL", "http://ollama.local:1234/")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma3:4b")
    parser = make_receipt_parser("ollama")
    assert isinstance(parser, OllamaReceiptParser)
    assert (parser.base_url, parser.model) == ("http://ollama.local:1234", "gemma3:4b")
