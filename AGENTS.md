# AGENTS.md — AI-SDLC Router

Repository state lives in:

docs/TASKS.md

Maintain `docs/TASKS.md`: PHASE = selected phase; STATUS = ready, in-progress,
done or blocked. Set in-progress on entry, done only after the phase output is
verified, or blocked with a reason. Keep PHASE on completion; an explicitly
selected next phase starts as ready. Changes to this router require human review.

---

Phases may be **skipped or repeated**.

Typical iteration:

SPECIFY → DESIGN → DEVELOP → VALIDATE  
VALIDATE → SPECIFY (iteration)  
DEPLOY → SPECIFY (feedback)

---

## Fast Track

- Small corrections only; no feature, API, data, security, dependency or architecture changes.
- Record scope, reason, acceptance and checks in the existing UC or `docs/TASKS.md`.
- Shorten SPECIFY; skip DESIGN with a reason. Scope grows → regular flow.
- Keep required CI and review. Release/deployment still require authorization.

## Collaboration

- Human-approved decisions → ADR; current architecture → `docs/PROJECT.md`.
- Durable rules + ADR links → `AGENTS.md`, with human approval/review.
- Update related files together; preserve decision history and reconcile parallel changes.

## Context Load Order

1. docs/TASKS.md  
2. docs/PROJECT.md  
3. docs/specs/UC-[NNN]-[NAME].md (or the eligible Fast Track task entry)

---

## Phase → Skill

0 → skills/ai-sdlc-0-bootstrap  
1 → skills/ai-sdlc-1-specify  
2 → skills/ai-sdlc-2-design  
3 → skills/ai-sdlc-3-develop  
4 → skills/ai-sdlc-4-validate  
5 → skills/ai-sdlc-5-deploy  

---

## Commands

Use the project-specific install, test, run and release commands documented in
`docs/PROJECT.md`. Do not assume a language, framework or deployment platform
before the project context has been completed.

---

## Rules

- Use the language of the current user prompt for communication. All
  repository artifacts (docs, specs, ADRs, UI texts, API descriptions,
  commits, pull requests) are written in **English**, regardless of the
  prompt language (team decision, see Project Rules).
- Update existing artifacts; create only what is missing.
- Keep artifacts **minimal**.
- Avoid unnecessary comments in code.
- Follow **TDD** (tests before code).
- Respect **Clean Architecture**  
  domain ← application ← interfaces ← infrastructure
- Prefer **small vertical slices** (one UC end-to-end).
- Read the [canonical AI-SDLC documentation](https://docs.aisl.science/learning-and-resources/ai-sdlc)
  when terminology or lifecycle responsibilities are unclear.

If requirements or architecture are unclear → ask the user.

---

## Project Rules (FairShare)

Human-approved durable rules derived from the ADRs in `docs/adr/`:

- Project language is English for every artifact, including user-facing UI
  and OpenAPI texts (team decision 2026-10-23).
- Layer boundaries are enforced by `lint-imports`; never weaken a contract to
  make a change pass ([ADR-001](docs/adr/ADR-001-clean-architecture.md)).
- Domain and application code must not import FastAPI, Pydantic, SQLAlchemy or
  Alembic; repositories are `Protocol` ports in `application/ports`.
- Money is always `int` cents; split remainders use largest remainder
  ([ADR-004](docs/adr/ADR-004-money-as-integer-cents.md)).
- Every schema change needs an Alembic migration
  ([ADR-003](docs/adr/ADR-003-persistence.md)).
- TDD trail: commit failing tests first (`test(uc-NNN): ... (red)`), then the
  implementation (`feat(uc-NNN): ...`) ([ADR-005](docs/adr/ADR-005-testing-strategy.md)).
- One branch and pull request per use case; CI must be green before merge.
- Before finishing a phase run: `ruff check . && ruff format --check . && mypy && lint-imports && pytest tests/unit tests/integration`.
- Log notable agent sessions (prompt, result, human correction) in `docs/AI-LOG.md`.
- Deployment and releases only after explicit human approval.
