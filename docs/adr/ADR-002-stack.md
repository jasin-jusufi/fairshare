# ADR-002: Python 3.12, FastAPI and SQLAlchemy 2

- **Status:** accepted
- **Date:** 2026-10-23

## Context

Two people, one week until the presentation. The stack must be handled well by
coding agents, allow fast tests and be close to the reference project BAIssue
so that architecture comparisons are possible.

## Alternatives

1. Java / Spring Boot + JPA: very "enterprise", but slow build/test cycle
2. TypeScript / NestJS + Prisma: good types, but a second ecosystem for the team
3. Python / FastAPI + SQLAlchemy 2: lean, automatic OpenAPI, existing team know-how

## Decision

Option 3. In addition, `mypy --strict`, `ruff` and `import-linter` compensate
for Python's lack of compile-time safety.

## Consequences

- Swagger UI at `/docs` for free, useful for the demo and E2E tests.
- Strict type checking costs time at first but catches agent mistakes early.

> **Update 2026-10-23:** Swagger UI moved to `/swagger`; `/docs` now serves a custom API reference generated from the same OpenAPI document. The decision itself is unchanged.
