# UC-002-RECORD-EXPENSE

## Intent
Ein Mitglied erfasst eine gemeinsame Ausgabe (z. B. Einkauf, Internet) und
legt fest, wer daran beteiligt ist und wie sie aufgeteilt wird. Die Anteile
sind die Grundlage für Salden und Ausgleichszahlungen (UC-003).

## Actors

Primary: WG-Mitglied (zahlt und erfasst)
Secondary: übrige Mitglieder (Beteiligte)

## Preconditions

- Haushalt existiert (UC-001).
- Zahler und Beteiligte sind Mitglieder dieses Haushalts.

## Flow

1. Mitglied gibt Zahler, Beschreibung, Betrag in Rappen, Aufteilungsart und Beteiligte an.
2. System prüft Mitgliedschaften und Eingaben.
3. System berechnet die Anteile:
   - `equal`: gleich verteilt
   - `percent`: nach Prozent (Summe muss 100 sein)
   - `shares`: nach Gewichten (z. B. 2 : 1 : 1)
4. Restrappen werden nach Largest-Remainder verteilt, die Summe der Anteile entspricht exakt dem Betrag (ADR-004).
5. System speichert Ausgabe und Anteile und gibt sie zurück.
6. Mitglieder listen die Ausgaben des Haushalts oder löschen eine Fehlerfassung.

## Errors

- invalid input: Betrag ≤ 0, leere Beschreibung, keine Beteiligten, doppelte Beteiligte, Gewicht ≤ 0, Prozentsumme ≠ 100 → 400
- unknown member: Zahler oder Beteiligte:r gehört nicht zum Haushalt → 400
- not found: Haushalt oder Ausgabe existiert nicht → 404

## Acceptance

- AC1 Given Lea, Noah, Mia, When Lea zahlt 10000 Rappen `equal` für alle drei, Then 201 und Anteile 3334/3333/3333 (Summe 10000).
- AC2 Given zwei Mitglieder, When `percent` mit 70/30 auf 5000, Then Anteile 3500/1500.
- AC3 Given drei Mitglieder, When `shares` mit 2/1/1 auf 1000, Then Anteile 500/250/250.
- AC4 Given `percent` mit Summe 90, When erfasst, Then 400.
- AC5 Given Zahler oder Beteiligte:r aus anderem Haushalt, When erfasst, Then 400.
- AC6 Given Betrag 0 oder leere Beschreibung, When erfasst, Then 400.
- AC7 Given zwei Ausgaben, When `GET /households/{id}/expenses`, Then beide mit Anteilen in Erfassungsreihenfolge.
- AC8 Given eine Ausgabe, When `DELETE …/expenses/{expense_id}`, Then 204 und sie fehlt in der Liste; unbekannte ID → 404.

## Tests

Unit: `split_amount` (alle Methoden, Restverteilung, Summeninvariante), `Expense`-Invarianten, `ExpenseService` mit In-Memory-Repositories
Integration: AC1–AC8 über `TestClient` + SQLite in-memory
E2E: Ausgabe erfassen und auflisten gegen den Container

## Design

| Layer | Komponente |
|---|---|
| domain | `Expense`, `ExpenseShare` (Entities), `SplitMethod`, `split_amount()` (Largest-Remainder), `UnknownMemberError` |
| application | `ExpenseService` (`record_expense`, `list_expenses`, `delete_expense`), Port `ExpenseRepository` |
| interfaces | Router `/households/{id}/expenses`, Schemas `ExpenseCreate`, `ParticipantIn`, `ExpenseOut`, `ShareOut` |
| infrastructure | `ExpenseModel`, `ExpenseShareModel`, `SqlAlchemyExpenseRepository`, Migration |

Die API arbeitet mit `amount_cents` (exakt, keine Rundung über HTTP); die
Umrechnung CHF ↔ Rappen macht nur das UI (Präzisierung zu ADR-004).
