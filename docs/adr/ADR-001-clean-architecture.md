# ADR-001: Clean Architecture mit erzwungenen Layer-Grenzen

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Die Anwendung soll Enterprise-tauglich und gut testbar sein. Die Geschäftslogik
(Aufteilen, Saldieren, Ausgleichen, Ämtli verteilen) ist der eigentliche Wert und
soll unabhängig von Web-Framework und Datenbank testbar bleiben. Coding Agents
neigen dazu, Framework-Code in die Domäne zu ziehen, wenn die Grenze nur
dokumentiert ist.

## Alternativen

1. Schichtenmodell „Router → Service → ORM-Model“ (typisches FastAPI-Tutorial)
2. Clean Architecture nur als Konvention in `AGENTS.md`
3. Clean Architecture **plus** automatische Prüfung in CI

## Entscheid

Variante 3. Vier Layer `domain ← application ← interfaces ← infrastructure`.
`import-linter` prüft in CI zwei Verträge:

- Layer-Vertrag: Kein Layer importiert einen äusseren Layer.
- Verbots-Vertrag: `domain` und `application` importieren weder FastAPI,
  Pydantic, SQLAlchemy noch Alembic.

Repositories sind Ports (`typing.Protocol`) im Application-Layer; Adapter
liegen in `infrastructure/persistence`. Die Verdrahtung erfolgt nur in
`infrastructure/web/app.py` via FastAPI `dependency_overrides`.

## Konsequenzen

- Domäne und Use Cases sind mit In-Memory-Repositories in Millisekunden testbar.
- Agenten erhalten sofortiges Feedback, wenn sie die Regel verletzen (CI rot).
- Mehr Boilerplate: ORM-Modelle und Domänen-Entities werden explizit gemappt.
