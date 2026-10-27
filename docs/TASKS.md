# TASKS.md

PHASE: 5
STATUS: done

(0=Bootstrap | 1=Specify | 2=Design | 3=Develop | 4=Validate | 5=Deploy)

## Current Use Case

docs/specs/UC-005-SCAN-RECEIPT.md (Owner: Bajram)

## Backlog

- No open items

## Working agreement

- Keep one active use case small enough to deliver vertically.
- Update this file when the lifecycle phase or active use case changes.
- Link decisions and validation evidence from the relevant project artefact.
- One branch and one pull request per use case; CI must be green before merge.

## Log

| Date | UC | Phase | Status | Who / Agent | Note |
|---|---|---|---|---|---|
| 2026-10-23 | — | 0 Bootstrap | done | Jasin + Claude Code | Adopted template, structure, tooling, PROJECT.md |
| 2026-10-23 | UC-001 | 1 Specify | done | Jasin + Claude Code | Specification with AC1–AC7 |
| 2026-10-23 | UC-001 | 2 Design | done | Jasin + Claude Code | Components per layer, no new ADR needed |
| 2026-10-23 | UC-001 | 3 Develop | done | Jasin + Claude Code | TDD: 12 integration + 12 unit tests red → green, Alembic migration |
| 2026-10-23 | UC-002 | 1 Specify | done | Jasin + Claude Code | AC1–AC8, three split methods |
| 2026-10-23 | UC-002 | 2 Design | done | Jasin + Claude Code | ADR-004 refined: API in cents |
| 2026-10-23 | UC-002 | 3 Develop | done | Jasin + Claude Code | TDD: 50 new tests red → green, refactored shared validation |
| 2026-10-23 | UC-003 | 1 Specify | done | Jasin + Claude Code | AC1–AC8 including chained debts and overpayment |
| 2026-10-23 | UC-003 | 2 Design | done | Jasin + Claude Code | ADR-007 greedy settle-up |
| 2026-10-23 | UC-003 | 3 Develop | done | Jasin + Claude Code | TDD: 51 new tests including 25 random scenarios, red → green |
| 2026-10-23 | UC-004 | 1 Specify | done | Jasin + Claude Code | AC1–AC9, fairness over two weeks as an acceptance criterion |
| 2026-10-23 | UC-004 | 2 Design | done | Jasin + Claude Code | LPT heuristic, effort snapshot, ConflictError hierarchy |
| 2026-10-23 | UC-004 | 3 Develop | done | Jasin + Claude Code | TDD: 38 new tests including a 12-week fairness simulation, red → green |
| 2026-10-23 | all | 4 Validate | done | Jasin + Claude Code | Coverage 99.8 % (gate 90 %), Docker image, E2E locally against SQLite and PostgreSQL 16, release and CD workflows |
| 2026-10-23 | UC-001–004 | 3 Develop | done | Jasin + Claude Code | Web UI at `/ui` (test first), checked in the browser with demo data |
| 2026-10-23 | UI | Fast Track | done | Jasin + Claude Code | Scope: UI redesign (glass/pastel, navigation across 5 views, quick add). Reason: usability/presentation. No API, data or architecture change → DESIGN skipped. Checks: UI tests green, browser desktop 1440 px + mobile 375 px without horizontal scrolling |
| 2026-10-23 | API docs | 3 Develop | done | Jasin + Claude Code | Test first; OpenAPI with tags, summaries, descriptions, error responses, examples; custom reference at `/docs`, Swagger at `/swagger`; browser check desktop + mobile |
| 2026-10-23 | all | Fast Track | done | Jasin + Claude Code | Scope: translate every artifact to English (docs, specs, ADRs, UI, OpenAPI texts, test data). Reason: team decision, recorded in AGENTS.md. No behaviour change → DESIGN skipped. Checks: 175 tests green, UI and /docs verified, no German left (grep) |
| 2026-10-23 | — | 4 Validate | done | Jasin + Claude Code | Repository made public; branch protection on `main`: PR required, 4 required checks, strict, enforced for admins |
| 2026-10-25 | UC-001–004 | 4 Validate | done | Bajram + Claude Code | Edge-case suite: 158 tests in `tests/*/edge_cases/` (143 green, 15 strict `xfail`), 5 bugs documented in `docs/TEST-PROTOCOL.md`, application code unchanged; BUG-1, BUG-2 and BUG-4 checked against PostgreSQL 16 in Docker |
| 2026-10-26 | UC-005 | 1 Specify | done | Bajram + Claude Code | Change: no API key. `RECEIPT_PARSER` = `none` (default, 503) or `fake` (demo, fixed suggestion); real Claude adapter out of scope. AC1–AC6 (AC6: unknown household → 404) |
| 2026-10-26 | UC-005 | 2 Design | done | Bajram + Claude Code | ADR-008: `ReceiptParser` port with fake and unavailable adapters instead of a real LLM. Image checks in `ReceiptService` (framework-free, unit-testable). No persistence, no migration; new dependency `python-multipart`. PROJECT.md: API row and `RECEIPT_PARSER` |
| 2026-10-26 | UC-005 | 3 Develop | done | Bajram + Claude Code | TDD: 41 new tests red → green (AC1–AC6, 5 MB boundary, `ReceiptService`, `ReceiptSuggestion`, parsers, config). UI: "Scan receipt" pre-fills the expense form (test first); checked in the browser with `fake` and `none`, mobile 375 px without horizontal scrolling |
| 2026-10-26 | UC-005 | 4 Validate | done | Bajram + Claude Code | ruff, mypy, import-linter, `alembic check` (no drift) green; 360 passed + 15 known-bug xfails, coverage 99.79 %. Docker image built, E2E 4/4 against PostgreSQL 16 (new: receipts answer 503 by default, which also proves `python-multipart` is in the image). README: UC table, ADR-008, `RECEIPT_PARSER`, test counts |
| 2026-10-26 | BUG-1…5 | Fast Track | done | Jasin + Claude Code | Fixed the five bugs from the edge-case suite; per bug: remove `xfail` marker (red) → fix (green). 377 passed, 0 xfailed |
| 2026-10-26 | UC-005 | 1–2 Specify/Design | done | Jasin + Claude Code | Third adapter `ollama` (local vision model, no key): AC7–AC8, ADR-009 |
| 2026-10-26 | UC-005 | 3 Develop | done | Jasin + Claude Code | TDD: 13 adapter tests against a stub Ollama server (red → green); UI shows progress while reading |
| 2026-10-26 | UC-005 | 4 Validate | done | Jasin + Claude Code | Manual check with `qwen2.5vl:7b` on an Apple M5: sample receipt `docs/assets/demo-receipt.png` → "COOP", 2395 cents (correct); cold 10.9 s, warm 1.1 s; no expense stored. 390 tests green |
| 2026-10-27 | UC-005 | 1–2 Specify/Design | done | Jasin + Claude Code | Fourth adapter `claude` (USD 2 demo budget): AC9–AC10, ADR-010, new dependency `anthropic` |
| 2026-10-27 | UC-005 | 3 Develop | done | Jasin + Claude Code | TDD: 13 adapter tests against a stub Messages API (red → green); scan limit `CLAUDE_MAX_SCANS` |
| 2026-10-27 | UC-005 | 4 Validate | done | Jasin + Claude Code | Real check: sample receipt → "Coop", 2395 cents; ≈ USD 0.004 per scan with Opus; default switched to `claude-sonnet-5-5` (team decision, same result, ≈ USD 0.002, 1.7 s); limit answers 503 without API call. 404 tests green |
| 2026-10-27 | UC-003 | Fast Track | done | Jasin + Claude Code | Review finding (Codex bot, PR #15): suggested transfers above the settlement cap are split (red → green); ADR-007 update note. 378 passed |
| 2026-10-27 | UI | 4 Validate | done | Jasin + Claude Code | Playwright browser E2E (3 journeys: quick add → settle up, fair chore plan, receipt scan) in the CI `e2e` job against the container with PostgreSQL; traces uploaded on failure |
| 2026-10-27 | all | 5 Deploy | done | Jasin + Claude Code | Release v0.1.0 (tests, image, E2E incl. Playwright, GHCR, GitHub release); Render via Blueprint; `cd.yml` with v0.1.0 green, smoke test passed; live at https://fairshare-1u2q.onrender.com |
| 2026-10-27 | UC-002 | 1–4 | done | Jasin + Claude Code | Feedback from the live deployment: correct an expense afterwards. Spec AC9–AC11, no ADR (same split rules); Codex review: each share now stores its weight (migration) so an edit keeps the exact split; TDD red → green (service, API, UI); browser check: percent 70/30 loaded into the form, saved as 50/50 |
| 2026-10-27 | UC-004 | 1–4 | done | Jasin + Claude Code | Feedback from the live deployment: labelled Done button, new chores can be planned into a planned week (AC5 narrowed, AC10–AC11). No ADR (same LPT rule). TDD red → green; browser check desktop + 375 px |
