# Presentation – 2026-10-29 (10 min + 5 min Q&A)

Focus according to the assignment: **approach and learnings**, not the app.

Slides: `FairShare-Presentation.pptx` (Bajram's deck, speaker notes per slide).

| # | Min | Who | Slide | Key message / evidence |
|---|---|---|---|---|
| 1 | 0:20 | Jasin | Title | Focus on approach and learnings, not features |
| 2 | 0:10 | Jasin | Agenda | Problem → architecture → agents and tools → testing and deployment → learnings |
| 3 | 0:50 | Jasin | Problem + use cases | Rounding, many transfers, unfair chores; 5 UCs, each specified before coding |
| 4 | 1:30 | Jasin | Clean Architecture | **import-linter makes the rule executable**; if the agent breaks it, the build turns red |
| 5 | 1:00 | Jasin | 10 ADRs | ADR-004 (cents), ADR-007 (greedy instead of NP-hard), ADR-008–010 (port → Ollama → Claude with a budget) |
| 6 | 1:30 | Bajram | Coding agents | AI-SDLC loop per UC, AGENTS.md router, spec first, TASKS + AI-LOG, edit hook, red → green commit trail |
| 7 | 1:00 | Bajram | Tool selection | Claude Code (terminal) + Copilot (inline), same AGENTS.md; stack chosen for fast agent feedback |
| 8 | 1:30 | Bajram | Testing | Pyramid 300 / 121 / 7 (Playwright through the UI), 99 % coverage, 158 edge-case tests found 5 bugs, all fixed |
| 9 | 1:00 | Bajram | CI, release, deployment | PR → 4 required checks → tag → GHCR → manual CD to Render → smoke test |
| 10 | 1:10 | both | Challenges and learnings | see below |
| 11 | 0:10 | Jasin | Guardrails instead of trust | Questions |

## Optional live demo (Q&A or instead of the screenshot on slide 3)

1. Start before the talk: `RECEIPT_PARSER=claude PYTHONPATH=src .venv/bin/uvicorn app.main:app`
   and scan `docs/assets/demo-receipt.png` once (checks key and network).
2. Live: household "Demo Flat" with Lea and Noah → quick add `Groceries 45.50` →
   Settle up shows Noah → Lea CHF 22.75 → "Paid" → Chores "Plan fairly" →
   Expenses "Scan receipt" → form shows "COOP", 23.95 → "Add expense".
3. Fallbacks, in this order: no network → restart with `RECEIPT_PARSER=ollama`
   (local model, warm it up first) → `RECEIPT_PARSER=fake` → screen recording.
4. Budget: about USD 0.002 per scan with `claude-sonnet-5-5`; `CLAUDE_MAX_SCANS=30`
   stops the server before the USD 2 limit could be reached.

## Learnings (from docs/AI-LOG.md)

- **Agents need executable guardrails.** Rules in Markdown alone are not enough;
  only CI contracts (import-linter, mypy --strict, alembic check) and branch
  protection keep generated code clean.
- **Spec first pays off.** Acceptance criteria became integration tests 1:1;
  the agent had a clear target.
- **Tests protect against the agent, too.** When fixing the five bugs, the agent
  first picked a CHF 1M limit and positive-only IDs; Bajram's boundary tests
  caught both. The limits now follow the tests.
- **A second AI reviews the first.** The Codex bot on our PRs found a real bug
  the fix had introduced (settle-up could suggest a transfer above the new
  limit). It was also wrong once (claimed a valid model ID did not exist) –
  a real API call settled it. AI review needs human judgement.
- **Domain and cost decisions stay with humans.** Cents instead of CHF
  decimals, greedy settle-up, USD 2 budget, Sonnet instead of Opus: decided by
  us, recorded as ADRs.
- **Ports make AI swappable.** One `ReceiptParser` port, four adapters (off,
  fake, local Ollama, Claude); CI never needs a key or a model.
- **Small PRs per use case** make agent output reviewable and the TDD trail
  visible.

## Possible questions

- *Why not Java/Spring?* → ADR-002 (agent speed, test cycle, team know-how)
- *How much of the code is from the agent?* → Most of it; commits carry
  `Co-Authored-By`, the AI-LOG shows what we corrected and decided.
- *Is the greedy settle-up optimal?* → No, but ≤ n − 1 transfers is guaranteed
  and property-tested (ADR-007).
- *What happens to receipt photos?* → Nothing is stored. `ollama` keeps them on
  the laptop; `claude` sends them to Anthropic, so it is opt-in (ADR-009/010).
- *How do you control AI cost?* → Scan limit per process, effort `low`, cheaper
  model, Console spend limit; measured cost in the UC-005 spec.
- *Why SQLite in CI?* → Fast; in addition, E2E against real PostgreSQL in the
  CI job `e2e`.
