# UC-005-SCAN-RECEIPT

> Owner: **Bajram** · Status: specified, implementation pending

## Intent
Instead of typing in the amount and description, a member uploads a photo of
the receipt. An AI model suggests a description and amount; the member
confirms and records the expense as in UC-002.

## Actors

Primary: Flatmate
Secondary: external vision LLM (via port `ReceiptParser`)

## Preconditions

- The household exists (UC-001).
- For production: `ANTHROPIC_API_KEY` is set (only as a secret, never in the repo).

## Flow

1. The member uploads an image (`POST /households/{id}/receipts`, JPEG/PNG, ≤ 5 MB).
2. The application service calls the port `ReceiptParser.parse(image_bytes, media_type)`.
3. The adapter (infrastructure) asks the LLM for structured JSON `{merchant, total_cents, date}`.
4. The service validates the suggestion (amount > 0, description 1–120 characters) and returns it. **Nothing is stored.**
5. The UI pre-fills the UC-002 form; the member confirms.

## Errors

- invalid input: wrong file type or too large → 400
- unreadable: the model finds no amount → 422
- unavailable: no API key or LLM unreachable → 503
- not found: household does not exist → 404

## Acceptance

- AC1 Given the fake parser returns "Migros, 2350", When an image is uploaded, Then 200 with `description = "Migros"`, `amount_cents = 2350`.
- AC2 Given a PDF instead of an image, When uploaded, Then 400.
- AC3 Given the parser finds no amount, When uploaded, Then 422.
- AC4 Given no API key is configured, When uploaded, Then 503.
- AC5 Given a suggestion, Then **no** new expense exists afterwards.

## Tests

Unit: `ReceiptService` with `FakeReceiptParser`, validation of the suggestion
Integration: AC1–AC5 with a fake adapter via `dependency_overrides`
E2E: not in CI (external API); document a manual test

## Design

| Layer | Component |
|---|---|
| domain | `ReceiptSuggestion` (value object, validation) |
| application | `ReceiptService`, port `ReceiptParser` (`Protocol`), `ReceiptUnreadableError`, `ParserUnavailableError` |
| interfaces | Router `POST /households/{id}/receipts` (`UploadFile`), schema `ReceiptSuggestionOut` |
| infrastructure | `AnthropicReceiptParser` (Anthropic SDK, vision), selected via env in `create_app`; fallback without key → 503 |

New dependencies (`anthropic`, `python-multipart`) and the choice of model
→ ADR-008. The port ensures that domain and application know nothing about the
LLM and that all tests run without network access.
