import base64
import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from app.application.errors import ParserUnavailableError
from app.application.ports.receipt_parser import ReceiptReading
from app.infrastructure.receipt_parsers import ClaudeReceiptParser, make_receipt_parser

IMAGE = b"\xff\xd8\xfffake-jpeg"
MODEL = "claude-opus-5-5"


class StubMessagesApi:
    """Minimal stand-in for the Anthropic Messages API (POST /v1/messages)."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.status = 200
        self.text = json.dumps({"merchant": "Coop", "total_chf": 23.95})
        self.stop_reason = "end_turn"
        self.requests: list[dict[str, Any]] = []

    def answer(self) -> dict[str, Any]:
        if self.status != 200:
            kind = "authentication_error" if self.status == 401 else "api_error"
            return {"type": "error", "error": {"type": kind, "message": "stub error"}}
        return {
            "id": "msg_stub",
            "type": "message",
            "role": "assistant",
            "model": MODEL,
            "content": [{"type": "text", "text": self.text}],
            "stop_reason": self.stop_reason,
            "stop_sequence": None,
            "usage": {"input_tokens": 1500, "output_tokens": 40},
        }


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[StubMessagesApi, str]]:
    stub = StubMessagesApi()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers["Content-Length"])
            stub.requests.append(
                {
                    "path": self.path,
                    "api_key": self.headers.get("x-api-key"),
                    "body": json.loads(self.rfile.read(length)),
                }
            )
            body = json.dumps(stub.answer()).encode()
            self.send_response(stub.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: object) -> None:
            pass

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield stub, f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def claude(server: tuple[StubMessagesApi, str]) -> tuple[StubMessagesApi, str]:
    stub, url = server
    stub.reset()
    return stub, url


def parser(url: str, api_key: str | None = "test-key", max_scans: int = 30) -> ClaudeReceiptParser:
    return ClaudeReceiptParser(api_key, MODEL, max_scans, base_url=url, max_retries=0)


def test_reads_merchant_and_total_in_cents(claude: tuple[StubMessagesApi, str]) -> None:
    _, url = claude
    assert parser(url).parse(IMAGE, "image/jpeg") == ReceiptReading("Coop", 2395)


def test_sends_image_model_schema_and_low_effort(claude: tuple[StubMessagesApi, str]) -> None:
    stub, url = claude
    parser(url).parse(IMAGE, "image/jpeg")
    [request] = stub.requests
    body = request["body"]
    assert request["path"] == "/v1/messages"
    assert request["api_key"] == "test-key"
    assert body["model"] == MODEL
    assert body["max_tokens"] == 2048
    assert body["output_config"]["effort"] == "low"
    schema = body["output_config"]["format"]["schema"]
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert set(schema["properties"]) == {"merchant", "total_chf"}
    assert schema["additionalProperties"] is False
    image, text = body["messages"][0]["content"]
    assert image["source"] == {
        "type": "base64",
        "media_type": "image/jpeg",
        "data": base64.b64encode(IMAGE).decode(),
    }
    assert "receipt" in text["text"]


@pytest.mark.parametrize(
    ("text", "stop_reason"),
    [
        ("not json", "end_turn"),
        ('["a list"]', "end_turn"),
        ('{"merchant": "Coop", "total_chf": 23.95}', "refusal"),
        ('{"merchant": "  ", "total_chf": null}', "end_turn"),
    ],
)
def test_unusable_answers_become_an_empty_reading(
    claude: tuple[StubMessagesApi, str], text: str, stop_reason: str
) -> None:
    stub, url = claude
    stub.text, stub.stop_reason = text, stop_reason
    assert parser(url).parse(IMAGE, "image/png") == ReceiptReading(None, None)


def test_missing_key_is_unavailable_without_calling_the_api(
    claude: tuple[StubMessagesApi, str],
) -> None:
    stub, url = claude
    with pytest.raises(ParserUnavailableError, match="ANTHROPIC_API_KEY"):
        parser(url, api_key=None).parse(IMAGE, "image/png")
    assert stub.requests == []


def test_rejected_key_is_unavailable(claude: tuple[StubMessagesApi, str]) -> None:
    stub, url = claude
    stub.status = 401
    with pytest.raises(ParserUnavailableError, match="key"):
        parser(url).parse(IMAGE, "image/png")


def test_api_error_is_unavailable(claude: tuple[StubMessagesApi, str]) -> None:
    stub, url = claude
    stub.status = 500
    with pytest.raises(ParserUnavailableError, match="HTTP 500"):
        parser(url).parse(IMAGE, "image/png")


def test_unreachable_api_is_unavailable() -> None:
    with pytest.raises(ParserUnavailableError, match="not reachable"):
        parser("http://127.0.0.1:9").parse(IMAGE, "image/png")


def test_scan_limit_stops_api_calls(claude: tuple[StubMessagesApi, str]) -> None:
    stub, url = claude
    limited = parser(url, max_scans=2)
    limited.parse(IMAGE, "image/png")
    limited.parse(IMAGE, "image/png")
    with pytest.raises(ParserUnavailableError, match="CLAUDE_MAX_SCANS"):
        limited.parse(IMAGE, "image/png")
    assert len(stub.requests) == 2


def test_factory_reads_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    monkeypatch.setenv("CLAUDE_MODEL", "claude-haiku-5-5")
    monkeypatch.setenv("CLAUDE_MAX_SCANS", "5")
    created = make_receipt_parser("claude")
    assert isinstance(created, ClaudeReceiptParser)
    assert created.model == "claude-haiku-5-5"
    assert created.max_scans == 5


def test_factory_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("ANTHROPIC_API_KEY", "CLAUDE_MODEL", "CLAUDE_MAX_SCANS"):
        monkeypatch.delenv(name, raising=False)
    created = make_receipt_parser("claude")
    assert isinstance(created, ClaudeReceiptParser)
    assert created.model == "claude-opus-5-5"
    assert created.max_scans == 30
