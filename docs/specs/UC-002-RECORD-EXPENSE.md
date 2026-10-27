# UC-002-RECORD-EXPENSE

## Intent
A member records a shared expense (e.g. groceries, internet) and specifies who
takes part and how it is split. The shares are the basis for balances and
settlements (UC-003).

## Actors

Primary: Flatmate (pays and records the expense)
Secondary: other members (participants)

## Preconditions

- The household exists (UC-001).
- Payer and participants are members of this household.

## Flow

1. The member enters payer, description, amount in cents, split method and participants.
2. The system checks memberships and input.
3. The system computes the shares:
   - `equal`: split equally
   - `percent`: by percentage (must add up to 100)
   - `shares`: by weights (e.g. 2 : 1 : 1)
4. Remaining cents are distributed using the largest remainder method; the sum of the shares equals the amount exactly (ADR-004).
5. The system stores the expense and its shares and returns them.
6. Members list the household's expenses or delete an erroneous entry.

## Errors

- invalid input: amount ≤ 0 or above 2³¹ − 1 cents (database limit), empty description, no participants, duplicate participants, weight ≤ 0, percentage sum ≠ 100 → 400
- unknown member: payer or participant does not belong to the household → 400
- wrong types: JSON booleans or strings where integers are required → 422
- not found: household or expense does not exist → 404

## Acceptance

- AC1 Given Lea, Noah, Mia, When Lea pays 10000 cents `equal` for all three, Then 201 and shares 3334/3333/3333 (sum 10000).
- AC2 Given two members, When `percent` with 70/30 on 5000, Then shares 3500/1500.
- AC3 Given three members, When `shares` with 2/1/1 on 1000, Then shares 500/250/250.
- AC4 Given `percent` with a sum of 90, When recorded, Then 400.
- AC5 Given a payer or participant from another household, When recorded, Then 400.
- AC6 Given amount 0 or an empty description, When recorded, Then 400.
- AC7 Given two expenses, When `GET /households/{id}/expenses`, Then both with their shares in recording order.
- AC8 Given an expense, When `DELETE …/expenses/{expense_id}`, Then 204 and it is no longer in the list; unknown ID → 404.

## Tests

Unit: `split_amount` (all methods, remainder distribution, sum invariant), `Expense` invariants, `ExpenseService` with in-memory repositories
Integration: AC1–AC8 via `TestClient` + SQLite in-memory
E2E: record and list an expense against the container

## Design

| Layer | Component |
|---|---|
| domain | `Expense`, `ExpenseShare` (entities), `SplitMethod`, `split_amount()` (largest remainder), `UnknownMemberError` |
| application | `ExpenseService` (`record_expense`, `list_expenses`, `delete_expense`), port `ExpenseRepository` |
| interfaces | Router `/households/{id}/expenses`, schemas `ExpenseCreate`, `ParticipantIn`, `ExpenseOut`, `ShareOut` |
| infrastructure | `ExpenseModel`, `ExpenseShareModel`, `SqlAlchemyExpenseRepository`, migration |

The API works with `amount_cents` (exact, no rounding over HTTP); only the UI
converts between CHF and cents (refinement of ADR-004).
