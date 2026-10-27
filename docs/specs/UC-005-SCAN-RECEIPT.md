# UC-005-SCAN-RECEIPT

> Owner: **Bajram** (fake/none adapters), Jasin (Ollama and Claude adapters) · Status: implemented

## Intent
Instead of typing in the amount and description, a member uploads a photo of
the receipt. The app suggests a description and amount; the member
confirms and records the expense as in UC-002.

## Actors

Primary: Flatmate
Secondary: receipt parser behind the port `ReceiptParser`, selected with `RECEIPT_PARSER`

## Preconditions

- The household exists (UC-001).
- The setting `RECEIPT_PARSER` selects the parser:
  - `none` (default): receipt scanning is switched off → 503
  - `fake` (tests/fallback): returns the fixed suggestion "Migros", 2350 cents for every image
  - `ollama` (live demo): a local vision model via Ollama on the presenter's laptop
    (`OLLAMA_URL`, default `http://localhost:11434`; `OLLAMA_MODEL`, default `qwen2.5vl:7b`).
    No cloud service, no key, the image never leaves the machine (ADR-009).
  - `claude` (live demo, best accuracy): Claude via the Anthropic API
    (`ANTHROPIC_API_KEY` from the environment or `.env`; `CLAUDE_MODEL`, default
    `claude-opus-5-5`; `CLAUDE_MAX_SCANS`, default 30 per server process). Budget
    for the demo: USD 2 (ADR-010).

## Flow

1. The member uploads an image (`POST /households/{id}/receipts`, multipart field `file`, JPEG/PNG, ≤ 5 MB).
2. The application service checks the image and calls the port `ReceiptParser.parse(image, media_type)`.
3. The parser returns the merchant and the total in cents, or nothing if it cannot read them.
4. The service validates the suggestion (amount > 0, description 1–120 characters) and returns it. **Nothing is stored.**
5. The UI pre-fills the UC-002 form; the member checks it and records the expense.

## Errors

- invalid input: not a JPEG/PNG image (checked by content, not by file name) or larger than 5 MB → 400
- unreadable: the parser finds no amount or no usable description → 422
- unavailable: `RECEIPT_PARSER=none`, Ollama not running or model not pulled, Claude key missing or invalid, scan limit reached → 503
- not found: household does not exist → 404

## Acceptance

- AC1 Given `RECEIPT_PARSER=fake`, When a JPEG or PNG is uploaded, Then 200 with `description = "Migros"`, `amount_cents = 2350`.
- AC2 Given a PDF instead of an image, or an image larger than 5 MB, When uploaded, Then 400.
- AC3 Given the parser finds no amount, When uploaded, Then 422.
- AC4 Given `RECEIPT_PARSER` is not set (`none`), When uploaded, Then 503.
- AC5 Given a suggestion, Then **no** new expense exists afterwards.
- AC6 Given an unknown household, When uploaded, Then 404.
- AC7 Given `RECEIPT_PARSER=ollama` and a running model, When a receipt photo is uploaded, Then the merchant and the total (in cents) read by the model are suggested.
- AC8 Given `RECEIPT_PARSER=ollama` but Ollama is not reachable or the model is missing, When uploaded, Then 503 with a hint how to start or pull it.
- AC9 Given `RECEIPT_PARSER=claude` and a valid key, When a receipt photo is uploaded, Then the merchant and the total (in cents) read by Claude are suggested.
- AC10 Given `RECEIPT_PARSER=claude` but no or an invalid key, or `CLAUDE_MAX_SCANS` scans already made, When uploaded, Then 503 with a hint, and no API call is made once the limit is reached.

## Tests

Unit: `ReceiptSuggestion` validation; `ReceiptService` with a stub parser (image checks, unreadable result, parser unavailable)
Integration: AC1–AC6; the parser is replaced via `dependency_overrides` where needed
E2E: the container runs without `RECEIPT_PARSER` → 503 (no external API, so it can run in CI)
Unit (adapter): `OllamaReceiptParser` against a local stub HTTP server (request format, CHF → cents, nulls, malformed answers, unreachable server, missing model)
Unit (adapter): `ClaudeReceiptParser` against a stub of the Messages API (request: model, image, schema, effort; CHF → cents; refusal; missing key; auth/connection errors; scan limit)
Manual: with `RECEIPT_PARSER=ollama` and a real receipt photo, "Scan receipt" in the UI pre-fills the expense form (sample: `docs/assets/demo-receipt.png` → "COOP", 2395 cents)

## Design

| Layer | Component |
|---|---|
| domain | `ReceiptSuggestion` (value object: description 1–120 characters, `amount_cents` > 0) |
| application | Port `ReceiptParser` (`Protocol`, returns `ReceiptReading`); `ReceiptService` (household check, JPEG/PNG by file signature, ≤ 5 MB → 400, builds the suggestion); `ReceiptUnreadableError` (422), `ParserUnavailableError` (503) |
| interfaces | `POST /households/{id}/receipts` (`UploadFile`), schema `ReceiptSuggestionOut`, tag `Receipts`, error mapping 422/503, dependencies `receipt_service` and `receipt_parser` |
| infrastructure | `FakeReceiptParser`, `UnavailableReceiptParser`, `OllamaReceiptParser` (ADR-009), `ClaudeReceiptParser` (ADR-010, `anthropic` SDK); `create_app` selects one from `RECEIPT_PARSER`, an unknown value stops the app at startup |

Nothing is stored, so there is no migration. New dependency `python-multipart`
(FastAPI needs it for uploads). Why a port with a fake adapter instead of a
real LLM → ADR-008.
