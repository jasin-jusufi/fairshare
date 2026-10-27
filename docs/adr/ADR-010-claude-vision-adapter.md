# ADR-010: Claude as an optional cloud adapter for receipt scanning

- **Status:** accepted
- **Date:** 2026-10-27

## Context

ADR-009 added a local model for the live demo. It needs a laptop with
Ollama and a 6 GB model, and it is noticeably weaker on crumpled or angled
receipts. The team now has an Anthropic API key with a hard limit of USD 2 for
the demo. ADR-008 kept the door open for a cloud adapter behind the same port.

## Alternatives

1. Stay with Ollama only: free and offline, but weaker and machine-bound.
2. Claude via raw HTTP (`urllib`, like the Ollama adapter): no new dependency,
   but we would re-implement retries, error types and request shapes.
3. Claude via the official `anthropic` SDK with structured outputs: one new
   dependency, typed errors, the JSON answer is guaranteed to match the schema.

## Decision

Option 3. `ClaudeReceiptParser` in infrastructure sends the image (base64)
and the shared prompt to `claude-sonnet-5-5` with `output_config.format` set to
the same JSON schema as the Ollama adapter (`merchant`, `total_chf`) and
effort `low`. `RECEIPT_PARSER=claude` selects it; `ANTHROPIC_API_KEY` comes
from the environment or the git-ignored `.env`, never from the repository.

Cost control for the USD 2 budget:

- `CLAUDE_MAX_SCANS` (default 30) caps API calls per server process; after
  that the adapter answers 503 without calling the API.
- `max_tokens` is 2048 and effort `low`; measured cost per scan is recorded in
  the UC-005 spec.
- Sonnet instead of Opus: on the sample receipt both read the same result,
  Sonnet at half the price and faster. `CLAUDE_MODEL` can switch back.
- A spend limit is also set in the Anthropic Console as the hard stop.
- CI, the E2E test and Render never use this adapter: tests run against a
  stub server, so the pipeline needs no key and costs nothing.

Missing or invalid key, network errors and API errors raise
`ParserUnavailableError` (503) with a hint. A refusal or an unusable answer
becomes an empty reading (422), as with the other adapters.

## Consequences

- Better accuracy in the demo, at a few cents per scan; Ollama stays as the
  free offline fallback and `fake` as the last resort.
- Receipt photos are sent to Anthropic when `claude` is selected; the default
  stays `none`.
- New runtime dependency `anthropic`.
- The scan counter lives in memory: a restart resets it, which is acceptable
  for a demo but not a billing control (the Console limit is).
