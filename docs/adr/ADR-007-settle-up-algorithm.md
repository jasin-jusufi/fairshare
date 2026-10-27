# ADR-007: Greedy algorithm for settle-up transfers

- **Status:** accepted
- **Date:** 2026-10-23

## Context

Transfers are to be derived from the balances. Naively, every person pays the
payer back for each expense (many small payments). Finding the minimum number
of transfers is NP-hard (partition problem). Households typically have 2–8
members.

## Alternatives

1. One transfer per expense and person (simple, but up to O(expenses × n))
2. Exact optimization via subset search (exponential)
3. Greedy: match the largest debt against the largest credit, repeat

## Decision

Option 3. Each step settles at least one person completely, so there are at
most n − 1 transfers. Ties are broken by member ID so that the result is
deterministic and testable. The algorithm is a pure function in the domain
layer.

## Consequences

- Runtime O(n²), negligible for household sizes.
- Not always globally minimal, but guaranteed ≤ n − 1 and checked as a
  property in tests (sum 0, upper bound, all balances 0 afterwards).
- Settlements must not exceed outstanding debts, so that typos cannot create
  new debts.

**Update 2026-10-27:** a single settlement is capped at 2³¹ − 1 cents
(ADR-004). A suggested transfer above that cap is split into several
transfers between the same pair, so every suggestion can be recorded. The
n − 1 bound counts debtor–creditor pairs; it only differs for balances above
CHF 21 million.
