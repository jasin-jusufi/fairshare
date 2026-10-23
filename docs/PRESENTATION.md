# Präsentation – 29.10.2026 (10 min + 5 min Fragen)

Fokus laut Auftrag: **Vorgehen und Learnings**, nicht die App.

| # | Min | Wer | Folie | Kernaussage / Beleg |
|---|---|---|---|---|
| 1 | 0:30 | Jasin | Titel + Problem | WG-Geld und Ämtli: Rappen-Rundung, viele Überweisungen, unfaire Verteilung |
| 2 | 1:00 | Jasin | Use Cases + 30-s-Demo | UI: Ausgabe → Settle-up → „Bezahlt“ → Wochenplan (oder GIF) |
| 3 | 1:30 | Jasin | Architektur | Layer-Diagramm aus dem README; **import-linter macht die Regel ausführbar** |
| 4 | 1:00 | Jasin | ADRs | 7 ADRs; Beispiel ADR-004 (Rappen) und ADR-007 (Greedy statt NP-schwer) |
| 5 | 2:00 | Bajram | Coding Agents | AGENTS.md als Router, Skills, Phasen pro UC, TASKS-Log, Hook; Prompt → Spec → rote Tests → grün |
| 6 | 1:00 | Bajram | Tool-Wahl | Claude Code (Terminal-Agent, führt Tests selbst aus) vs. Copilot (Inline) → beide über dieselbe AGENTS.md |
| 7 | 1:30 | Bajram | Tests + Deployment | Pyramide 131/39/3, Property-Tests, E2E gegen Postgres in CI, Tag → GHCR → Render |
| 8 | 1:30 | beide | Challenges & Learnings | siehe unten |

## Learnings (Kandidaten, aus docs/AI-LOG.md)

- **Agents brauchen ausführbare Leitplanken.** Regeln in Markdown allein reichen nicht; erst CI-Verträge (import-linter, mypy --strict, alembic check) halten generierten Code sauber.
- **Spec zuerst lohnt sich.** Akzeptanzkriterien wurden 1:1 zu Integrationstests; der Agent hatte ein klares Ziel.
- **Agent-Tests reviewen.** Generierte Tests enthielten eine sinnlose Assertion; Tests sind nicht automatisch gut, nur weil sie grün sind.
- **Fachentscheide bleiben beim Menschen.** Rappen statt CHF-Dezimal, Überzahlungsschutz und Greedy-Algorithmus wurden von uns entschieden und als ADR festgehalten.
- **Kleine PRs pro Use Case** machen Agent-Output überprüfbar und den TDD-Trail sichtbar.
- **CI-Fehler als Feedbackschleife.** Der Agent hat CI-Logs gelesen und selbst korrigiert (leerer Testordner).

## Mögliche Fragen

- *Warum nicht Java/Spring?* → ADR-002 (Agent-Tempo, Testzyklus, Team-Know-how)
- *Wie viel Code ist vom Agent?* → Ehrlich beantworten; Commits tragen `Co-Authored-By`, AI-LOG zeigt Korrekturen.
- *Ist der Greedy-Ausgleich optimal?* → Nein, aber ≤ n − 1 garantiert und property-getestet (ADR-007).
- *Warum SQLite in CI?* → Schnell; zusätzlich E2E gegen echtes PostgreSQL im CI-Job `e2e`.
