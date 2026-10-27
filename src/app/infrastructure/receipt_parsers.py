import base64
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from app.application.errors import ParserUnavailableError
from app.application.ports.receipt_parser import ReceiptParser, ReceiptReading
from app.infrastructure import config


class FakeReceiptParser:
    """Demo adapter without a model: the same suggestion for every image (ADR-008)."""

    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        return ReceiptReading(merchant="Migros", total_cents=2350)


class UnavailableReceiptParser:
    """Default adapter: receipt scanning is switched off."""

    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        raise ParserUnavailableError(
            "Receipt scanning is switched off. Set RECEIPT_PARSER=ollama (local model) or fake."
        )


PROMPT = (
    "This is a photo of a shopping receipt. Return the name of the store or merchant and "
    "the final total amount paid in CHF (the line labelled TOTAL, Total, Summe or Betrag). "
    "Use null for anything you cannot read."
)
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "merchant": {"type": ["string", "null"]},
        "total_chf": {"type": ["number", "null"]},
    },
    "required": ["merchant", "total_chf"],
}


def to_cents(total_chf: object) -> int | None:
    if isinstance(total_chf, bool) or not isinstance(total_chf, int | float | str):
        return None
    try:
        chf = Decimal(str(total_chf).strip())
    except InvalidOperation:
        return None
    if not chf.is_finite():
        return None
    return int((chf * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


class OllamaReceiptParser:
    """Local vision model via Ollama: no key, the image never leaves the machine (ADR-009)."""

    def __init__(self, base_url: str, model: str, timeout: float = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        payload = {
            "model": self.model,
            "stream": False,
            "format": ANSWER_SCHEMA,
            "options": {"temperature": 0},
            "messages": [
                {"role": "user", "content": PROMPT, "images": [base64.b64encode(image).decode()]}
            ],
        }
        answer = self._chat(payload)
        merchant = answer.get("merchant")
        return ReceiptReading(
            merchant=merchant.strip() or None if isinstance(merchant, str) else None,
            total_cents=to_cents(answer.get("total_chf")),
        )

    def _chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read())
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise ParserUnavailableError(
                    f"Model '{self.model}' is not available. Run `ollama pull {self.model}`."
                ) from error
            raise ParserUnavailableError(f"Ollama answered with HTTP {error.code}") from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise ParserUnavailableError(
                f"Ollama is not reachable at {self.base_url}. Start it with `ollama serve`."
            ) from error
        try:
            answer = json.loads(body["message"]["content"])
        except (KeyError, TypeError, ValueError):
            return {}
        return answer if isinstance(answer, dict) else {}


def ollama_from_settings() -> OllamaReceiptParser:
    return OllamaReceiptParser(config.ollama_url(), config.ollama_model())


PARSERS: dict[str, Callable[[], ReceiptParser]] = {
    "fake": FakeReceiptParser,
    "none": UnavailableReceiptParser,
    "ollama": ollama_from_settings,
}


def make_receipt_parser(mode: str) -> ReceiptParser:
    if mode not in PARSERS:
        raise ValueError(f"Unknown RECEIPT_PARSER '{mode}', expected one of: {', '.join(PARSERS)}")
    return PARSERS[mode]()
