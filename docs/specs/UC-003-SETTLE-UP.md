# UC-003-SETTLE-UP

## Intent
The flatmates want to know who owes whom how much and settle up with **as few
transfers as possible**. Completed settlements are recorded so that the
balances are correct again.

## Actors

Primary: Flatmate (checks balance, records payment)
Secondary: recipient of the payment

## Preconditions

- Household with members (UC-001), expenses recorded (UC-002).

## Flow

1. A member retrieves the balances: balance = paid − own share + settlements sent − settlements received.
2. The system suggests settle-up transfers (greedy, at most n − 1 transfers, ADR-007); a transfer above the settlement limit of 2³¹ − 1 cents is split so that each one can be recorded.
3. The debtor transfers the money outside the system and records the payment.
4. The system validates and stores the payment; the balances are recalculated.
5. Members list all recorded settlements.

## Errors

- invalid input: amount ≤ 0, payer = recipient → 400
- unknown member: payer or recipient not in the household → 400
- overpayment: amount exceeds the payer's outstanding debt or the recipient's credit → 400
- not found: household does not exist → 404

## Acceptance

- AC1 Given Lea pays 9000 `equal` for Lea/Noah/Mia, When `GET …/balances`, Then Lea +6000, Noah −3000, Mia −3000 (sum 0).
- AC2 Given AC1, When `GET …/settle-up`, Then two transfers: Noah → Lea 3000, Mia → Lea 3000.
- AC3 Given chained debts (Lea pays 1000 for Noah, Noah pays 1000 for Mia), When settle-up, Then exactly one transfer Mia → Lea 1000.
- AC4 Given AC1, When Noah records 3000 to Lea, Then 201, Noah has balance 0, settle-up contains only Mia → Lea.
- AC5 Given AC1, When Noah records 3500 to Lea, Then 400 (overpayment).
- AC6 Given payer = recipient or amount 0, When recorded, Then 400.
- AC7 Given all debts settled, When settle-up, Then an empty list.
- AC8 Given recorded payments, When `GET …/settlements`, Then all in recording order.

## Tests

Unit: `compute_balances`, `suggest_transfers` (sum 0, ≤ n − 1 transfers, determinism, random scenarios), `Settlement` invariants, `SettlementService`
Integration: AC1–AC8 via `TestClient` + SQLite in-memory
E2E: expense → settle-up → payment → balance 0 against the container

## Design

| Layer | Component |
|---|---|
| domain | `Settlement` (entity), `Transfer` (value object), `compute_balances()`, `suggest_transfers()`, `OverpaymentError` |
| application | `SettlementService` (`balances`, `suggest_transfers`, `record_settlement`, `list_settlements`), port `SettlementRepository`, DTO `MemberBalance` |
| interfaces | Router `/households/{id}/balances`, `/settle-up`, `/settlements`, schemas `BalanceOut`, `TransferOut`, `SettlementCreate`, `SettlementOut` |
| infrastructure | `SettlementModel`, `SqlAlchemySettlementRepository`, migration |

Algorithm decision: [ADR-007](../adr/ADR-007-settle-up-algorithm.md).
