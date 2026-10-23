# PROJECT.md

## Purpose

- **Projektname:** FairShare
- **Problem:** In Wohngemeinschaften (WGs) entstehen laufend gemeinsame Ausgaben
  und Haushaltsaufgaben. Wer wem wie viel schuldet und wer welches Ämtli
  übernimmt, wird meist in Chats oder Tabellen verwaltet. Das führt zu
  Rundungsfehlern, vielen Einzelüberweisungen und ungleich verteilter Arbeit.
- **Nutzende:** Mitglieder eines gemeinsamen Haushalts (WG, Familie, Reisegruppe).
- **In Scope:** Haushalt und Mitglieder verwalten, Ausgaben erfassen und
  aufteilen (gleich, prozentual, nach Anteilen), Salden berechnen, minimale
  Ausgleichszahlungen vorschlagen und erfassen, Ämtli fair nach Aufwand
  verteilen, Belege per KI vorerfassen (Port/Adapter).
- **Out of Scope:** Echte Zahlungsabwicklung, Authentifizierung/Benutzerkonten,
  Mehrwährungsfähigkeit, Mobile App.

## Architecture

Clean Architecture, Abhängigkeiten zeigen nach innen:

`domain ← application ← interfaces ← infrastructure`

| Layer | Inhalt | Darf importieren |
|---|---|---|
| `domain` | Entities, Value Objects, reine Domänenlogik (Split, Saldo, Ausgleich, Rotation) | nur Standardbibliothek |
| `application` | Use-Case-Services, Repository-Ports, DTOs, Fehler | `domain` |
| `interfaces` | HTTP-Grenze (FastAPI-Router, Pydantic-Schemas) | `application`, `domain` |
| `infrastructure` | Konfiguration, SQLAlchemy-Modelle und Repositories, Alembic, App-Wiring, statisches UI | alle |

Die Regel wird nicht nur dokumentiert, sondern mit **import-linter** in CI
erzwungen (`lint-imports`, Verträge in `pyproject.toml`).

Entscheidungen: siehe `docs/adr/`.

- Stack: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, pytest
- Datenbank: SQLite (Entwicklung, CI), PostgreSQL (Produktion auf Render)
- Geldbeträge: Ganzzahlige Rappen (`int`), keine Floats

## Structure

```
src/app/
├── domain/            # Entities + Domänenservices (framework-frei)
├── application/       # Use Cases + Ports (Repository-Interfaces)
├── interfaces/api/    # FastAPI-Router + Schemas
├── infrastructure/    # DB, ORM, Repositories, Web-Wiring, UI
└── main.py            # Entry Point
tests/
├── unit/              # Domain + Use Cases mit In-Memory-Repositories
├── integration/       # API + SQLAlchemy gegen SQLite in-memory
└── e2e/               # HTTP gegen laufenden Docker-Container
docs/
├── specs/             # Ausführbare Use-Case-Spezifikationen
└── adr/               # Architecture Decision Records
```

## Commands

| Aktivität | Befehl |
|---|---|
| Install | `bash scripts/setup-python.sh` |
| Unit-Tests | `pytest tests/unit` |
| Integrationstests | `pytest tests/integration` |
| Alle Tests + Coverage | `pytest tests/unit tests/integration --cov` |
| Lint / Format | `ruff check . && ruff format --check .` |
| Typecheck | `mypy` |
| Architekturregeln | `lint-imports` |
| Lokal starten | `PYTHONPATH=src uvicorn app.main:app --reload` |
| Container | `docker build -t fairshare . && docker run -p 8000:8000 fairshare` |
| E2E | `BASE_URL=http://127.0.0.1:8000 pytest tests/e2e` |
| Release | `git tag vX.Y.Z && git push origin vX.Y.Z` |

## Dependencies

- Laufzeit: `requirements.txt`; Entwicklung/Tests: `requirements-dev.txt`
- Python-Version: `.python-version` (3.12)
- Konfiguration nur über Umgebungsvariablen:
  - `DATABASE_URL` (Default `sqlite:///./fairshare.db`)
- Secrets (nur in GitHub/Render, nie im Repo): `RENDER_API_KEY`, `RENDER_SERVICE_ID`
