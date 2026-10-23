# ADR-006: Delivery-Pipeline: GitHub Actions, GHCR und Render

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Gefordert sind CI, Release-Workflow, Docker-Image und Cloud-Deployment mit
PostgreSQL. Das Deployment soll nachvollziehbar und reproduzierbar sein.

## Alternativen

1. Render baut direkt aus dem Git-Repository (Auto-Deploy)
2. Fly.io / Railway
3. Image wird in GitHub Actions gebaut, getestet und in GHCR veröffentlicht; Render deployt genau dieses Image

## Entscheid

Variante 3, analog zum Referenzprojekt:

- **CI** (`ci.yml`, jeder Push/PR): Lint, Format, Typecheck, Architekturregeln, Unit- und Integrationstests mit Coverage, Migrationscheck, Docker-Build mit E2E-Smoke-Test.
- **Release** (`release.yml`, Tag `v*`): Image bauen, E2E gegen Container, Push nach `ghcr.io`, GitHub Release mit Notes.
- **CD** (`cd.yml`, manuell): Render deployt das neueste GHCR-Image, danach Smoke-Test gegen `/health`.

## Konsequenzen

- Getestetes Artefakt = deploytes Artefakt.
- Render-Secrets (`RENDER_API_KEY`, `RENDER_SERVICE_ID`) liegen nur in GitHub.
- Deployment ist bewusst manuell (Freigabe durch Menschen, siehe `AGENTS.md`).
