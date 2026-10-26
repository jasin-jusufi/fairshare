# ADR-008: Receipt parsing behind a port, fake adapter instead of a real LLM

- **Status:** accepted
- **Date:** 2026-10-26

## Context

UC-005 suggests a description and an amount from a photo of a receipt. The
first version of the spec called a vision LLM (Anthropic SDK) directly. That
needs an API key as a secret, a paid account and network access, also in CI.
None of this is available for the course demo, and tests must stay offline and
deterministic. A real model should still be pluggable later without touching
the rest of the app.

## Alternatives

1. Call the LLM SDK directly in the service: simple, but couples the
   application layer to an SDK and needs a key and network in every test.
2. Port `ReceiptParser` plus a real LLM adapter now: clean, but needs a key,
   costs per call and network access in CI.
3. Port `ReceiptParser` plus a fake adapter for the demo and an "unavailable"
   adapter as the default; the real adapter later.
4. Local OCR (e.g. Tesseract): system dependency in the Docker image and poor
   accuracy on receipts.

## Decision

Option 3. `application/ports` defines `ReceiptParser.parse(image, media_type)`,
which returns a `ReceiptReading` (merchant, total in cents, each optional).
Infrastructure provides `FakeReceiptParser` (always "Migros", 2350 cents) and
`UnavailableReceiptParser` (raises `ParserUnavailableError` → 503). The
setting `RECEIPT_PARSER` (`none` by default, `fake`) selects the adapter in
`create_app`; an unknown value stops the app at startup. Checking the image
and validating the suggestion stay in application and domain, so they apply
to every adapter.

## Consequences

- No API key, no secrets, no network: all tests run offline.
- The default `none` keeps production honest: the feature answers 503 instead
  of inventing data. `fake` is for demos only, it returns the same suggestion
  for every image.
- A real adapter is one new class in infrastructure plus one new value for
  `RECEIPT_PARSER`. It needs its own ADR for model choice, key handling and
  cost.
- New runtime dependency `python-multipart` for uploads. No database change.
