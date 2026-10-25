# TASKS.md

PHASE: 4
STATUS: done

(0=Bootstrap | 1=Specify | 2=Design | 3=Develop | 4=Validate | 5=Deploy)

## Current Use Case

docs/specs/UC-004-ROTATE-CHORES.md

## Backlog

- docs/specs/UC-005-SCAN-RECEIPT.md — Owner: Bajram (Phase 2 → 3, ADR-008)
- UI E2E with Playwright (Owner: Bajram)
- Phase 5: set up Render deployment and run `cd.yml` (Jasin + Bajram)

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
