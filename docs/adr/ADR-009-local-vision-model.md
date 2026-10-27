# ADR-009: Local vision model via Ollama for receipt scanning

- **Status:** accepted
- **Date:** 2026-10-26

## Context

ADR-008 put receipt parsing behind the `ReceiptParser` port and shipped a fake
adapter. The fake returns the same suggestion for every photo, which is fine for
tests but does not show real AI in the live demo. A cloud LLM needs an API key,
a paid account and sends receipt photos to a third party.

## Alternatives

1. Cloud vision LLM (Anthropic, OpenAI): best accuracy, but key, cost and data
   leaving the device.
2. Local OCR (Tesseract) plus rules: no model, but a system dependency and poor
   results on crumpled, angled receipts.
3. Local vision LLM via Ollama: free, offline, no key; slower and only on a
   machine that runs Ollama.

## Decision

Option 3. `OllamaReceiptParser` in infrastructure calls Ollama's `/api/chat`
with the image (base64), `temperature 0` and a JSON schema as `format`, asking
for `merchant` and `total_chf`. CHF are converted to cents with `Decimal`, so no
float rounding reaches the domain. Only the standard library is used (`urllib`),
no new dependency. `RECEIPT_PARSER=ollama` selects it; `OLLAMA_URL` and
`OLLAMA_MODEL` (default `qwen2.5vl:7b`) configure it. Connection errors and a
missing model raise `ParserUnavailableError` (503) with a hint; an answer the
model cannot fill becomes an empty reading, which the service already turns
into 422.

## Consequences

- Real AI in the demo without secrets; receipt photos never leave the laptop.
- CI and Render keep using `none`/`fake`: no model download in pipelines.
- The adapter is tested against a stub HTTP server, so tests stay offline.
- The first request after starting Ollama loads the model and can take
  10–30 s; warm it up before presenting.
- Swapping in a cloud model later is another adapter, as ADR-008 intended
  (done in ADR-010).
