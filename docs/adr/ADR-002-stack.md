# ADR-002: Python 3.12, FastAPI und SQLAlchemy 2

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Zwei Personen, eine Woche bis zur Präsentation. Der Stack muss von Coding
Agents gut beherrscht werden, schnelle Tests erlauben und dem Referenzprojekt
BAIssue nahe sein, damit Architekturvergleiche möglich sind.

## Alternativen

1. Java / Spring Boot + JPA: sehr „enterprise“, aber langsamer Build/Test-Zyklus
2. TypeScript / NestJS + Prisma: gute Typen, aber zweites Ökosystem fürs Team
3. Python / FastAPI + SQLAlchemy 2: schlank, OpenAPI automatisch, bekanntes Team-Know-how

## Entscheid

Variante 3. Zusätzlich `mypy --strict`, `ruff` und `import-linter`, um die
fehlende Compile-Time-Sicherheit von Python auszugleichen.

## Konsequenzen

- Swagger-UI unter `/docs` gratis, gut für Demo und E2E-Tests.
- Strenge Typprüfung kostet anfangs Zeit, fängt aber Agent-Fehler früh ab.
