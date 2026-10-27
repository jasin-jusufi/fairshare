# PROJECT.md

## Purpose

- **Project name:** FairShare
- **Problem:** Shared flats constantly generate shared expenses and household
  tasks. Who owes whom how much, and who takes on which chore, is usually
  tracked in group chats or spreadsheets. This leads to rounding errors, many
  individual transfers and an unequal distribution of work.
- **Users:** Members of a shared household (shared flat, family, travel group).
- **In scope:** Manage households and members, record and split expenses
  (equally, by percentage, by shares), compute balances, suggest and record
  minimal settle-up transfers, distribute chores fairly by effort, pre-fill
  receipts using AI (port/adapter).
- **Out of scope:** Real payment processing, authentication/user accounts,
  multi-currency support, mobile app.

## Architecture

Clean Architecture, dependencies point inwards:

`domain ← application ← interfaces ← infrastructure`

| Layer | Contents | May import |
|---|---|---|
| `domain` | Entities, value objects, pure domain logic (split, balance, settle-up, rotation) | standard library only |
| `application` | Use case services, repository ports, DTOs, errors | `domain` |
| `interfaces` | HTTP boundary (FastAPI routers, Pydantic schemas) | `application`, `domain` |
| `infrastructure` | Configuration, SQLAlchemy models and repositories, Alembic, app wiring, static UI | all |

The rule is not just documented but enforced in CI with **import-linter**
(`lint-imports`, contracts in `pyproject.toml`).

Decisions: see `docs/adr/`.

- Stack: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, pytest
- Database: SQLite (development, CI), PostgreSQL (production on Render)
- Money amounts: integer cents (`int`), no floats

## API

| Resource (OpenAPI tag) | Endpoints | UC |
|---|---|---|
| Households | `POST/GET /households`, `GET /households/{id}`, `POST /households/{id}/members` | 001 |
| Expenses | `POST/GET /households/{id}/expenses`, `DELETE …/expenses/{expense_id}` | 002 |
| Settle-up | `GET …/balances`, `GET …/settle-up`, `POST/GET …/settlements` | 003 |
| Chores | `POST/GET …/chores`, `POST …/chore-plans`, `GET …/chore-plans/{week}`, `POST …/assignments/{id}/complete`, `GET …/chore-load` | 004 |
| Receipts | `POST …/receipts` (suggestion only, nothing is stored) | 005 |
| Operations | `GET /health`, `/docs` (API reference), `/swagger`, `/openapi.json`, `/ui/` (web UI) | — |

## Structure

```
src/app/
├── domain/            # Entities + domain services (framework-free)
├── application/       # Use cases + ports (repository interfaces)
├── interfaces/api/    # FastAPI routers + schemas
├── infrastructure/    # DB, ORM, repositories, web wiring, UI
└── main.py            # Entry point
tests/
├── unit/              # Domain + use cases with in-memory repositories
├── integration/       # API + SQLAlchemy against SQLite in-memory
└── e2e/               # HTTP against the running Docker container
migrations/            # Alembic migrations (production schema)
scripts/               # Setup, deploy, smoke test, agent hooks
docs/
├── specs/             # Executable use case specifications
└── adr/               # Architecture Decision Records
```

## Commands

| Activity | Command |
|---|---|
| Install | `bash scripts/setup-python.sh` |
| Unit tests | `pytest tests/unit` |
| Integration tests | `pytest tests/integration` |
| All tests + coverage | `pytest tests/unit tests/integration --cov` |
| Lint / format | `ruff check . && ruff format --check .` |
| Type check | `mypy` |
| Architecture rules | `lint-imports` |
| Run locally | `PYTHONPATH=src uvicorn app.main:app --reload` |
| Container | `docker build -t fairshare . && docker run -p 8000:8000 fairshare` |
| E2E | `BASE_URL=http://127.0.0.1:8000 pytest tests/e2e` |
| Release | `git tag vX.Y.Z && git push origin vX.Y.Z` |

## Dependencies

- Runtime: `requirements.txt`; development/tests: `requirements-dev.txt`
- Python version: `.python-version` (3.12)
- Configuration via environment variables only:
  - `DATABASE_URL` (default `sqlite:///./fairshare.db`)
  - `RECEIPT_PARSER`: `none` (default, receipt scanning answers 503), `fake`, `ollama` or `claude`
  - `OLLAMA_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default `qwen2.5vl:7b`)
  - `ANTHROPIC_API_KEY` (only for `claude`, from the environment or the git-ignored `.env`),
    `CLAUDE_MODEL` (default `claude-sonnet-5-5`), `CLAUDE_MAX_SCANS` (default 30)
    (see ADR-008 to ADR-010)
- Secrets (only in GitHub/Render, never in the repo): `RENDER_API_KEY`, `RENDER_SERVICE_ID`
