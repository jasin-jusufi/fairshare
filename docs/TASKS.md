# TASKS.md

PHASE: 4
STATUS: done

(0=Bootstrap | 1=Specify | 2=Design | 3=Develop | 4=Validate | 5=Deploy)

## Current Use Case

docs/specs/UC-004-ROTATE-CHORES.md

## Backlog


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
| 2026-10-23 | UC-002 | 1 Specify | done | Jasin + Claude Code | AC1–AC8, drei Aufteilungsarten |
| 2026-10-23 | UC-002 | 2 Design | done | Jasin + Claude Code | ADR-004 präzisiert: API in Rappen |
| 2026-10-23 | UC-002 | 3 Develop | done | Jasin + Claude Code | TDD: 50 neue Tests rot → grün, Refactor gemeinsamer Validierung |
| 2026-10-23 | UC-003 | 1 Specify | done | Jasin + Claude Code | AC1–AC8 inkl. Kettenschulden und Überzahlung |
| 2026-10-23 | UC-003 | 2 Design | done | Jasin + Claude Code | ADR-007 Greedy-Ausgleich |
| 2026-10-23 | UC-003 | 3 Develop | done | Jasin + Claude Code | TDD: 51 neue Tests inkl. 25 Zufallsszenarien, rot → grün |
| 2026-10-23 | UC-004 | 1 Specify | done | Jasin + Claude Code | AC1–AC9, Fairness über zwei Wochen als Akzeptanzkriterium |
| 2026-10-23 | UC-004 | 2 Design | done | Jasin + Claude Code | LPT-Heuristik, Aufwand-Snapshot, ConflictError-Hierarchie |
| 2026-10-23 | UC-004 | 3 Develop | done | Jasin + Claude Code | TDD: 38 neue Tests inkl. 12-Wochen-Fairness-Simulation, rot → grün |
| 2026-10-23 | alle | 4 Validate | done | Jasin + Claude Code | Coverage 99.8 % (Gate 90 %), Docker-Image, E2E lokal gegen SQLite und PostgreSQL 16, Release- und CD-Workflow |
| 2026-10-23 | UC-001–004 | 3 Develop | done | Jasin + Claude Code | Web-UI unter `/ui` (Test zuerst), im Browser mit Demo-Daten geprüft |
