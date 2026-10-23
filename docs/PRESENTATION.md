# Presentation – 2026-10-29 (10 min + 5 min Q&A)

Focus according to the assignment: **approach and learnings**, not the app.

| # | Min | Who | Slide | Key message / evidence |
|---|---|---|---|---|
| 1 | 0:30 | Jasin | Title + problem | Shared-flat money and chores: rounding to the cent, many transfers, unfair distribution |
| 2 | 1:00 | Jasin | Use cases + 30-s demo | UI: expense → Settle up → "Paid" → weekly plan (or GIF) |
| 3 | 1:30 | Jasin | Architecture | Layer diagram from the README; **import-linter makes the rule executable** |
| 4 | 1:00 | Jasin | ADRs | 7 ADRs; examples ADR-004 (cents) and ADR-007 (greedy instead of NP-hard) |
| 5 | 2:00 | Bajram | Coding agents | AGENTS.md as router, skills, phases per UC, TASKS log, hook; prompt → spec → red tests → green |
| 6 | 1:00 | Bajram | Tool choice | Claude Code (terminal agent, runs tests itself) vs. Copilot (inline) → both use the same AGENTS.md |
| 7 | 1:30 | Bajram | Tests + deployment | Pyramid 131/39/3, property tests, E2E against Postgres in CI, tag → GHCR → Render |
| 8 | 1:30 | both | Challenges & learnings | see below |

## Learnings (candidates, from docs/AI-LOG.md)

- **Agents need executable guardrails.** Rules in Markdown alone are not enough; only CI contracts (import-linter, mypy --strict, alembic check) keep generated code clean.
- **Spec first pays off.** Acceptance criteria became integration tests 1:1; the agent had a clear target.
- **Review agent tests.** Generated tests contained a meaningless assertion; tests are not automatically good just because they are green.
- **Domain decisions stay with humans.** Cents instead of CHF decimals, overpayment protection and the greedy algorithm were decided by us and recorded as ADRs.
- **Small PRs per use case** make agent output reviewable and the TDD trail visible.
- **CI failures as a feedback loop.** The agent read CI logs and corrected itself (empty test folder).

## Possible questions

- *Why not Java/Spring?* → ADR-002 (agent speed, test cycle, team know-how)
- *How much of the code is from the agent?* → Answer honestly; commits carry `Co-Authored-By`, the AI-LOG shows corrections.
- *Is the greedy settle-up optimal?* → No, but ≤ n − 1 is guaranteed and property-tested (ADR-007).
- *Why SQLite in CI?* → Fast; in addition, E2E against real PostgreSQL in the CI job `e2e`.
