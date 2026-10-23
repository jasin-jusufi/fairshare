# AI-LOG.md — Einsatz von Coding Agents

Kurzes Protokoll, wie wir Coding Agents eingesetzt haben: Prompt, Ergebnis und
was wir als Menschen korrigieren oder entscheiden mussten. Grundlage für die
Präsentation (Lessons Learned).

## Tools

| Tool | Einsatz | Warum |
|---|---|---|
| Claude Code (Opus) | Hauptagent im Terminal: Phasen 0–5, TDD, Refactoring, Workflows | Liest `AGENTS.md` via `CLAUDE.md`, nutzt die AI-SDLC-Skills in `.claude/skills`, kann Tests selbst ausführen |
| GitHub Copilot | Inline-Vervollständigung und Chat in VS Code / Codespaces | Liest `.github/copilot-instructions.md` → `AGENTS.md`, Skills in `.agents/skills` |

## Einträge

| Datum | Wer | Phase / UC | Prompt (gekürzt) | Ergebnis | Menschliche Korrektur / Entscheid |
|---|---|---|---|---|---|
| 2026-10-23 | Jasin | 0 | „Analysiere BAIssue und die Bewertungskriterien, schlage Use Case und Plan vor“ | Rubric-Mapping, drei Use-Case-Ideen | Use Case FairShare gewählt |
| 2026-10-23 | Jasin | 0 | „Execute phase 0 of AI-SDLC for FairShare (Python/FastAPI, Render)“ | Template übernommen, Skills verlinkt, Struktur, Tooling | Klarstellung durch uns: BAIssue ist nur Referenz für Struktur und Prozess, Domäne ist eigen |
