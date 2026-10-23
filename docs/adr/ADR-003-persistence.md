# ADR-003: SQLite für Entwicklung/CI, PostgreSQL in Produktion, Alembic-Migrationen

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Gefordert ist eine relationale Datenbank mit ORM. Lokale Entwicklung und CI
sollen ohne Datenbankserver laufen; Produktion braucht eine persistente,
verwaltete Datenbank.

## Alternativen

1. Überall PostgreSQL (Docker Compose lokal, Service-Container in CI)
2. SQLite überall, auch in Produktion
3. SQLite lokal/CI, PostgreSQL in Produktion, Schema via Alembic

## Entscheid

Variante 3. `DATABASE_URL` wählt die Datenbank. `postgres://`-URLs von Render
werden auf `postgresql+psycopg://` normalisiert. Das Schema wird in Produktion
über Alembic-Migrationen erstellt (`alembic upgrade head` beim Container-Start),
in Tests über `metadata.create_all`. CI prüft mit `alembic check`, dass
Migrationen und ORM-Modelle übereinstimmen.

## Konsequenzen

- Schnelle Tests ohne Infrastruktur.
- Nur portables SQL verwenden (keine Postgres-spezifischen Typen).
- Schemaänderungen brauchen immer eine Migration, sonst wird CI rot.
