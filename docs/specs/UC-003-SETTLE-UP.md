# UC-003-SETTLE-UP

## Intent
Die WG will wissen, wer wem wie viel schuldet, und mit **möglichst wenigen
Überweisungen** abrechnen. Bezahlte Ausgleichszahlungen werden erfasst, damit
die Salden wieder stimmen.

## Actors

Primary: WG-Mitglied (prüft Saldo, erfasst Zahlung)
Secondary: Empfänger:in der Zahlung

## Preconditions

- Haushalt mit Mitgliedern (UC-001), Ausgaben erfasst (UC-002).

## Flow

1. Mitglied ruft die Salden ab: Saldo = bezahlt − eigener Anteil + gesendete Ausgleiche − empfangene Ausgleiche.
2. System schlägt Ausgleichszahlungen vor (Greedy, max. n − 1 Überweisungen, ADR-007).
3. Schuldner:in überweist ausserhalb des Systems und erfasst die Zahlung.
4. System prüft die Zahlung und speichert sie; die Salden werden neu berechnet.
5. Mitglieder listen alle erfassten Ausgleichszahlungen.

## Errors

- invalid input: Betrag ≤ 0, Zahler = Empfänger → 400
- unknown member: Zahler oder Empfänger nicht im Haushalt → 400
- overpayment: Betrag übersteigt die offene Schuld des Zahlers oder das Guthaben des Empfängers → 400
- not found: Haushalt existiert nicht → 404

## Acceptance

- AC1 Given Lea zahlt 9000 `equal` für Lea/Noah/Mia, When `GET …/balances`, Then Lea +6000, Noah −3000, Mia −3000 (Summe 0).
- AC2 Given AC1, When `GET …/settle-up`, Then zwei Transfers: Noah → Lea 3000, Mia → Lea 3000.
- AC3 Given Kettenschulden (Lea zahlt für Noah 1000, Noah zahlt für Mia 1000), When settle-up, Then genau ein Transfer Mia → Lea 1000.
- AC4 Given AC1, When Noah erfasst 3000 an Lea, Then 201, Noah hat Saldo 0, settle-up enthält nur noch Mia → Lea.
- AC5 Given AC1, When Noah erfasst 3500 an Lea, Then 400 (Überzahlung).
- AC6 Given Zahler = Empfänger oder Betrag 0, When erfasst, Then 400.
- AC7 Given alle Schulden beglichen, When settle-up, Then leere Liste.
- AC8 Given erfasste Zahlungen, When `GET …/settlements`, Then alle in Erfassungsreihenfolge.

## Tests

Unit: `compute_balances`, `suggest_transfers` (Summe 0, ≤ n − 1 Transfers, Determinismus, zufällige Szenarien), `Settlement`-Invarianten, `SettlementService`
Integration: AC1–AC8 über `TestClient` + SQLite in-memory
E2E: Ausgabe → settle-up → Zahlung → Saldo 0 gegen den Container

## Design

| Layer | Komponente |
|---|---|
| domain | `Settlement` (Entity), `Transfer` (Value Object), `compute_balances()`, `suggest_transfers()`, `OverpaymentError` |
| application | `SettlementService` (`balances`, `suggest_transfers`, `record_settlement`, `list_settlements`), Port `SettlementRepository`, DTO `MemberBalance` |
| interfaces | Router `/households/{id}/balances`, `/settle-up`, `/settlements`, Schemas `BalanceOut`, `TransferOut`, `SettlementCreate`, `SettlementOut` |
| infrastructure | `SettlementModel`, `SqlAlchemySettlementRepository`, Migration |

Algorithmus-Entscheid: [ADR-007](../adr/ADR-007-settle-up-algorithm.md).
