# UC-005-SCAN-RECEIPT

> Owner: **Bajram** · Status: specified, no API key (fake parser for the demo)

## Intent
Instead of typing in the amount and description, a member uploads a photo of
the receipt. The app suggests a description and amount; the member
confirms and records the expense as in UC-002.

## Actors

Primary: Flatmate
Secondary: receipt parser behind the port `ReceiptParser`, selected with `RECEIPT_PARSER`

## Preconditions

- The household exists (UC-001).
- No API key is used. The setting `RECEIPT_PARSER` selects the parser:
  - `none` (default): receipt scanning is switched off → 503
  - `fake` (demo): returns the fixed suggestion "Migros", 2350 cents for every image
- A real vision-LLM adapter (e.g. Claude) is out of scope for now.

## Flow

1. The member uploads an image (`POST /households/{id}/receipts`, multipart field `file`, JPEG/PNG, ≤ 5 MB).
2. The application service checks the image and calls the port `ReceiptParser.parse(image, media_type)`.
3. The parser returns the merchant and the total in cents, or nothing if it cannot read them.
4. The service validates the suggestion (amount > 0, description 1–120 characters) and returns it. **Nothing is stored.**
5. The UI pre-fills the UC-002 form; the member checks it and records the expense.

## Errors

- invalid input: not a JPEG/PNG image (checked by content, not by file name) or larger than 5 MB → 400
- unreadable: the parser finds no amount or no usable description → 422
- unavailable: `RECEIPT_PARSER=none` → 503
- not found: household does not exist → 404

## Acceptance

- AC1 Given `RECEIPT_PARSER=fake`, When a JPEG or PNG is uploaded, Then 200 with `description = "Migros"`, `amount_cents = 2350`.
- AC2 Given a PDF instead of an image, or an image larger than 5 MB, When uploaded, Then 400.
- AC3 Given the parser finds no amount, When uploaded, Then 422.
- AC4 Given `RECEIPT_PARSER` is not set (`none`), When uploaded, Then 503.
- AC5 Given a suggestion, Then **no** new expense exists afterwards.
- AC6 Given an unknown household, When uploaded, Then 404.

## Tests

Unit: `ReceiptSuggestion` validation; `ReceiptService` with a stub parser (image checks, unreadable result, parser unavailable)
Integration: AC1–AC6; the parser is replaced via `dependency_overrides` where needed
E2E: the container runs without `RECEIPT_PARSER` → 503 (no external API, so it can run in CI)
Manual: with `RECEIPT_PARSER=fake`, "Scan receipt" in the UI pre-fills the expense form

## Design

| Layer | Component |
|---|---|
| domain | `ReceiptSuggestion` (value object: description 1–120 characters, `amount_cents` > 0) |
| application | Port `ReceiptParser` (`Protocol`, returns `ReceiptReading`); `ReceiptService` (household check, JPEG/PNG by file signature, ≤ 5 MB → 400, builds the suggestion); `ReceiptUnreadableError` (422), `ParserUnavailableError` (503) |
| interfaces | `POST /households/{id}/receipts` (`UploadFile`), schema `ReceiptSuggestionOut`, tag `Receipts`, error mapping 422/503, dependencies `receipt_service` and `receipt_parser` |
| infrastructure | `FakeReceiptParser`, `UnavailableReceiptParser`; `create_app` selects one from `RECEIPT_PARSER`, an unknown value stops the app at startup |

Nothing is stored, so there is no migration. New dependency `python-multipart`
(FastAPI needs it for uploads). Why a port with a fake adapter instead of a
real LLM → ADR-008.
