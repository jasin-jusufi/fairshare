# ADR-005: Teststrategie und TDD-Nachweis

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Tests sind die wichtigste Leitplanke für Code, der von Agenten generiert wird.
Die AI-SDLC-Phase DEVELOP verlangt die Reihenfolge Integrationstest →
Unit-Test → Implementierung.

## Entscheid

Testpyramide mit drei Ebenen:

| Ebene | Ziel | Technik |
|---|---|---|
| Unit | Domänenregeln, Use-Case-Logik | pytest, In-Memory-Repositories, keine Frameworks |
| Integration | Akzeptanzkriterien über HTTP + echte DB | FastAPI `TestClient`, SQLite in-memory |
| E2E | Ausgeliefertes Artefakt | `httpx` gegen den laufenden Docker-Container |

TDD wird in der Git-Historie sichtbar: pro Use Case zuerst ein Commit
`test(uc-NNN): ... (red)`, danach `feat(uc-NNN): ...` (green), dann
`refactor`. Coverage-Ziel ≥ 90 % für `domain` und `application`; CI bricht
unter 85 % Gesamt-Coverage ab.

## Konsequenzen

- Akzeptanzkriterien jeder Spezifikation sind 1:1 als Integrationstests auffindbar.
- Rote Commits existieren nur auf Feature-Branches; `main` bleibt grün.
