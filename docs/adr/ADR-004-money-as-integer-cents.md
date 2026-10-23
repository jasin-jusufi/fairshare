# ADR-004: Money as integer cents

- **Status:** accepted
- **Date:** 2026-10-23

## Context

Splitting expenses produces remainders (CHF 100 / 3). Floats lead to rounding
errors; the sum of the shares must equal the amount exactly, otherwise
balances never add up to zero.

## Alternatives

1. `float`
2. `decimal.Decimal` with rounding
3. `int` in cents, remainder distributed using the largest remainder method

## Decision

Option 3. All amounts are `int` in cents (`amount_cents`). When splitting,
leftover cents are distributed deterministically to the participants with the
largest fractional part (ties are broken by order).

## Consequences

- The invariant "sum of shares = amount" can be checked exactly and is tested.
- The API works with `amount_cents`; only the UI converts between CHF and cents.
- Single-currency system (CHF) — multi-currency is out of scope.
