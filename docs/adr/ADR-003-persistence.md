# ADR-003: SQLite for development/CI, PostgreSQL in production, Alembic migrations

- **Status:** accepted
- **Date:** 2026-10-23

## Context

A relational database with an ORM is required. Local development and CI should
run without a database server; production needs a persistent, managed
database.

## Alternatives

1. PostgreSQL everywhere (Docker Compose locally, service container in CI)
2. SQLite everywhere, including production
3. SQLite locally/in CI, PostgreSQL in production, schema via Alembic

## Decision

Option 3. `DATABASE_URL` selects the database. `postgres://` URLs from Render
are normalized to `postgresql+psycopg://`. In production the schema is created
via Alembic migrations (`alembic upgrade head` on container start), in tests via
`metadata.create_all`. CI uses `alembic check` to verify that migrations and
ORM models match.

## Consequences

- Fast tests without infrastructure.
- Use portable SQL only (no Postgres-specific types).
- Schema changes always require a migration, otherwise CI turns red.
