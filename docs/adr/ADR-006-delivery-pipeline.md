# ADR-006: Delivery pipeline: GitHub Actions, GHCR and Render

- **Status:** accepted
- **Date:** 2026-10-23

## Context

CI, a release workflow, a Docker image and cloud deployment with PostgreSQL are
required. Deployment should be traceable and reproducible.

## Alternatives

1. Render builds directly from the Git repository (auto-deploy)
2. Fly.io / Railway
3. The image is built, tested and published to GHCR in GitHub Actions; Render deploys exactly this image

## Decision

Option 3, analogous to the reference project:

- **CI** (`ci.yml`, every push/PR): lint, format, type check, architecture rules, unit and integration tests with coverage, migration check, Docker build with E2E smoke test.
- **Release** (`release.yml`, tag `v*`): build image, E2E against the container, push to `ghcr.io`, GitHub Release with notes.
- **CD** (`cd.yml`, manual): Render deploys the latest GHCR image, followed by a smoke test against `/health`.

## Consequences

- Tested artifact = deployed artifact.
- Render secrets (`RENDER_API_KEY`, `RENDER_SERVICE_ID`) are stored only in GitHub.
- Deployment is deliberately manual (human approval, see `AGENTS.md`).
