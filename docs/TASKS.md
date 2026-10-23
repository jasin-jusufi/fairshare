# TASKS.md

PHASE: 3
STATUS: done

(0=Bootstrap | 1=Specify | 2=Design | 3=Develop | 4=Validate | 5=Deploy)

## Current Use Case

docs/specs/UC-001-SETUP-HOUSEHOLD.md

## Backlog

- docs/specs/UC-002-RECORD-EXPENSE.md
- docs/specs/UC-003-SETTLE-UP.md
- docs/specs/UC-004-ROTATE-CHORES.md

## Working agreement

- Keep one active use case small enough to deliver vertically.
- Update this file when the lifecycle phase or active use case changes.
- Link decisions and validation evidence from the relevant project artefact.
- One branch and one pull request per use case; CI must be green before merge.

## Log

| Datum | UC | Phase | Status | Wer / Agent | Notiz |
|---|---|---|---|---|---|
| 2026-10-23 | — | 0 Bootstrap | done | Jasin + Claude Code | Template übernommen, Struktur, Tooling, PROJECT.md |
| 2026-10-23 | UC-001 | 1 Specify | done | Jasin + Claude Code | Spezifikation mit AC1–AC7 |
| 2026-10-23 | UC-001 | 2 Design | done | Jasin + Claude Code | Komponenten pro Layer, keine neue ADR nötig |
| 2026-10-23 | UC-001 | 3 Develop | done | Jasin + Claude Code | TDD: 12 Integration- + 12 Unit-Tests rot → grün, Alembic-Migration |
