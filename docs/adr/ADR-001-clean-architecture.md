# ADR-001: Clean Architecture with enforced layer boundaries

- **Status:** accepted
- **Date:** 2026-10-23

## Context

The application should be enterprise-ready and easy to test. The business
logic (splitting, computing balances, settling up, rotating chores) is the
actual value and must remain testable independently of the web framework and
the database. Coding agents tend to pull framework code into the domain when
the boundary is only documented.

## Alternatives

1. Layered model "router → service → ORM model" (typical FastAPI tutorial)
2. Clean Architecture only as a convention in `AGENTS.md`
3. Clean Architecture **plus** automated checks in CI

## Decision

Option 3. Four layers `domain ← application ← interfaces ← infrastructure`.
`import-linter` checks two contracts in CI:

- Layers contract: no layer imports an outer layer.
- Forbidden contract: `domain` and `application` import neither FastAPI,
  Pydantic, SQLAlchemy nor Alembic.

Repositories are ports (`typing.Protocol`) in the application layer; adapters
live in `infrastructure/persistence`. Wiring happens only in
`infrastructure/web/app.py` via FastAPI `dependency_overrides`.

## Consequences

- Domain and use cases can be tested in milliseconds with in-memory repositories.
- Agents get immediate feedback when they violate the rule (CI red).
- More boilerplate: ORM models and domain entities are mapped explicitly.
