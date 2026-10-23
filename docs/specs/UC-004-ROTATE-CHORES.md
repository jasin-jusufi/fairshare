# UC-004-ROTATE-CHORES

## Intent
Ämtli (Bad putzen, Küche, Abfall …) sollen **fair nach Aufwand** verteilt
werden, nicht nur der Reihe nach. Wer in vergangenen Wochen viel Aufwand
hatte, bekommt diese Woche weniger.

## Actors

Primary: WG-Mitglied (pflegt Ämtli, plant Woche, hakt erledigte Ämtli ab)
Secondary: übrige Mitglieder (erhalten Zuteilungen)

## Preconditions

- Haushalt mit mindestens einem Mitglied (UC-001).

## Flow

1. Mitglied erfasst Ämtli mit Name und Aufwand (1–5 Punkte).
2. Mitglied plant eine Woche (beliebiges Datum → Montag dieser Woche).
3. System verteilt jedes Ämtli genau einmal: das aufwändigste zuerst an das Mitglied mit der bisher kleinsten Gesamtlast (Historie + bereits in dieser Woche zugeteilt), Gleichstand → kleinere Mitglied-ID (LPT-Heuristik).
4. Mitglieder sehen den Wochenplan und haken erledigte Ämtli ab.
5. Mitglieder sehen die kumulierte Last pro Person (Fairness-Übersicht).

## Errors

- invalid input: leerer Name, Aufwand ausserhalb 1–5 → 400
- nothing to plan: keine Ämtli oder keine Mitglieder → 400
- conflict: Woche bereits geplant, Zuteilung bereits erledigt → 409
- not found: Haushalt oder Zuteilung existiert nicht → 404

## Acceptance

- AC1 Given Haushalt, When `POST …/chores {"name": "Bad", "effort": 5}`, Then 201 mit `id`, `name`, `effort`.
- AC2 Given Aufwand 0 oder 6, When erfasst, Then 400.
- AC3 Given Lea, Noah, Mia und Ämtli Bad 5, Küche 3, Müll 1, Staubsaugen 3, When Woche geplant, Then Bad → Lea, Küche → Noah, Staubsaugen → Mia, Müll → Noah.
- AC4 Given AC3, When die Folgewoche geplant wird, Then hat nach zwei Wochen jedes Mitglied genau 8 Punkte.
- AC5 Given geplante Woche, When dieselbe Woche erneut geplant wird, Then 409.
- AC6 Given Datum Donnerstag 2026-10-29, When geplant, Then `week_start = 2026-10-26`.
- AC7 Given Zuteilung, When `POST …/assignments/{id}/complete`, Then 200 mit `completed_at`; erneut → 409; unbekannte ID → 404.
- AC8 Given keine Ämtli, When Woche geplant, Then 400.
- AC9 Given geplante Wochen, When `GET …/chore-load`, Then Punkte pro Mitglied.

## Tests

Unit: `week_start_of`, `plan_week` (Reihenfolge, Gleichstand, Historie, Fairness über viele Wochen), `Chore`-/`ChoreAssignment`-Invarianten, `ChoreService`
Integration: AC1–AC9 über `TestClient` + SQLite in-memory
E2E: Ämtli anlegen und Woche planen gegen den Container

## Design

| Layer | Komponente |
|---|---|
| domain | `Chore`, `ChoreAssignment` (Entities), `week_start_of()`, `plan_week()`, `ConflictError` als Basis für 409-Fehler |
| application | `ChoreService` (`add_chore`, `list_chores`, `plan_week`, `week_plan`, `complete_assignment`, `load_by_member`), Ports `ChoreRepository`, `ChoreAssignmentRepository` |
| interfaces | Router `/households/{id}/chores`, `/chore-plans`, `/assignments/{id}/complete`, `/chore-load` |
| infrastructure | `ChoreModel`, `ChoreAssignmentModel` (Unique: Ämtli + Woche), Repositories, Migration |

Die Zuteilung speichert den Aufwand als Snapshot, damit spätere Änderungen am
Ämtli die Fairness-Historie nicht verfälschen.
