import base64
import json
import threading
import urllib.error
import urllib.request
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

import anthropic
from anthropic.types import MessageParam, OutputConfigParam

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
            "Receipt scanning is switched off. Set RECEIPT_PARSER=claude, ollama or fake."
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
    "additionalProperties": False,
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
        return reading_from(self._chat(payload))

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
            content = body["message"]["content"]
        except (KeyError, TypeError):
            return {}
        return json_object(content) if isinstance(content, str) else {}


def reading_from(answer: dict[str, Any]) -> ReceiptReading:
    merchant = answer.get("merchant")
    return ReceiptReading(
        merchant=merchant.strip() or None if isinstance(merchant, str) else None,
        total_cents=to_cents(answer.get("total_chf")),
    )


def json_object(text: str) -> dict[str, Any]:
    try:
        answer = json.loads(text)
    except ValueError:
        return {}
    return answer if isinstance(answer, dict) else {}


OUTPUT: OutputConfigParam = {
    "effort": "low",
    "format": {"type": "json_schema", "schema": ANSWER_SCHEMA},
}


class ClaudeReceiptParser:
    """Claude via the Anthropic API, capped at `max_scans` calls per process (ADR-010)."""

    def __init__(
        self,
        api_key: str | None,
        model: str,
        max_scans: int,
        base_url: str | None = None,
        max_retries: int = 2,
    ) -> None:
        self.model = model
        self.max_scans = max_scans
        self.scans = 0
        self._lock = threading.Lock()
        self._client = (
            anthropic.Anthropic(
                api_key=api_key, base_url=base_url, max_retries=max_retries, timeout=60
            )
            if api_key
            else None
        )

    def parse(self, image: bytes, media_type: str) -> ReceiptReading:
        if self._client is None:
            raise ParserUnavailableError(
                "No Anthropic API key. Set ANTHROPIC_API_KEY in the environment or in .env."
            )
        with self._lock:
            if self.scans >= self.max_scans:
                raise ParserUnavailableError(
                    f"Demo limit of {self.max_scans} scans reached (CLAUDE_MAX_SCANS)."
                )
            self.scans += 1
        message: MessageParam = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png" if media_type == "image/png" else "image/jpeg",
                        "data": base64.b64encode(image).decode(),
                    },
                },
                {"type": "text", "text": PROMPT},
            ],
        }
        try:
            response = self._client.messages.create(
                model=self.model, max_tokens=2048, output_config=OUTPUT, messages=[message]
            )
        except anthropic.AuthenticationError as error:
            raise ParserUnavailableError(
                "The Anthropic API key was rejected. Check ANTHROPIC_API_KEY."
            ) from error
        except anthropic.APIStatusError as error:
            raise ParserUnavailableError(
                f"Claude answered with HTTP {error.status_code}"
            ) from error
        except anthropic.APIConnectionError as error:
            raise ParserUnavailableError("The Anthropic API is not reachable.") from error
        if response.stop_reason != "end_turn":
            return ReceiptReading(None, None)
        text = next((block.text for block in response.content if block.type == "text"), "")
        return reading_from(json_object(text))


def claude_from_settings() -> ClaudeReceiptParser:
    return ClaudeReceiptParser(
        config.anthropic_api_key(), config.claude_model(), config.claude_max_scans()
    )


def ollama_from_settings() -> OllamaReceiptParser:
    return OllamaReceiptParser(config.ollama_url(), config.ollama_model())


PARSERS: dict[str, Callable[[], ReceiptParser]] = {
    "claude": claude_from_settings,
    "fake": FakeReceiptParser,
    "none": UnavailableReceiptParser,
    "ollama": ollama_from_settings,
}


def make_receipt_parser(mode: str) -> ReceiptParser:
    if mode not in PARSERS:
        raise ValueError(f"Unknown RECEIPT_PARSER '{mode}', expected one of: {', '.join(PARSERS)}")
    return PARSERS[mode]()
