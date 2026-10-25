# Test protocol – edge-case suite

| | |
|---|---|
| **Date** | 2026-10-25 |
| **Tester** | Bajram Kurto Elezi (testing role), assisted by Claude Code |
| **Branch / base** | `test/edge-case-tests`, based on `main` @ `491ab82` |
| **Environment** | Windows 11, Python 3.12.10, pytest 9.1.1, FastAPI 0.162.0, Pydantic 2.14.1, SQLAlchemy 2.1.6, SQLite in-memory |
| **Command** | `pytest tests/unit tests/integration --cov -rx` |

## Summary

| | Test cases | Passed | Failed (bug, marked `xfail`) |
|---|---|---|---|
| Existing suite (acceptance criteria) | 175 | 175 | 0 |
| **New edge-case suite** | **158** | **143** | **15** |
| Total | 333 | 318 | 15 |

Coverage: 99.76 % (gate 90 %). `ruff`, `mypy --strict` and `lint-imports` pass.
The 15 failing cases trace back to **5 bugs** (BUG-1 … BUG-5, see [Findings](#findings)).
They are marked as strict `xfail` in `tests/known_bugs.py`, so CI stays green until
they are fixed. Parametrized tests are one row each; the count is in brackets.

## Test cases

### Unit tests – expense split (`tests/unit/edge_cases/test_split_edge_cases.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| U-01 One cent among three | 1 cent, `equal`, 3 participants | Shares `[1, 0, 0]` | `[1, 0, 0]` | ✅ Pass |
| U-02 Single participant pays everything (3) | 999 cents, one participant: `equal`, `percent` 100, `shares` 7 | `[999]` | `[999]` | ✅ Pass |
| U-03 Zero and negative amount (6) | 0 and −1 cents × 3 methods | `ValidationError` | `ValidationError` | ✅ Pass |
| U-04 Percent boundary (4) | 99 + 1, 50 + 49, 50 + 51, 150 + (−50) | Only 99 + 1 valid | As expected | ✅ Pass |
| U-05 `equal` ignores invalid weights | 100 cents, weights 0 and −5 | `[50, 50]` | `[50, 50]` | ✅ Pass |
| U-06 Very large numbers | 10²⁰ + 1 cents, weights 10¹² : 1 : 1 | Sum exactly 10²⁰ + 1 | Exact | ✅ Pass |
| U-07 Remainder order | 100 cents `equal`, participants listed 3, 1, 2 | Member 3 (listed first) gets 34 | `[34, 33, 33]` | ✅ Pass |
| U-08 Property: within one cent of exact value (30) | Random 1–1,000,000 cents, 1–8 participants, weights 1–50 | \|share − exact share\| < 1 cent, sum exact | Holds for all 30 seeds | ✅ Pass |
| U-09 Property: `equal` is fair (30) | Random amount, 1–11 participants | max − min ≤ 1 cent | Holds for all 30 seeds | ✅ Pass |

### Unit tests – names (`tests/unit/edge_cases/test_text_edge_cases.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| U-10 Name length (4) | `A`, 80 × `x`, 81 × `x`, 80 × `x` with spaces around | 1–80 valid after trimming, 81 invalid | As expected | ✅ Pass |
| U-11 Only Unicode whitespace (3) | Tab + newline, U+00A0, U+3000 | `ValidationError` | `ValidationError` | ✅ Pass |
| U-12 Umlauts and emoji | `" Zoë 🏠 "` | `"Zoë 🏠"` | `"Zoë 🏠"` | ✅ Pass |
| U-13 ß is a duplicate of ss | `Strauss`, then `STRAUß` | `DuplicateMemberError` | `DuplicateMemberError` | ✅ Pass |
| U-14 Invisible and control characters (3) | U+200B, `\x00`, `Lea\x00` | `ValidationError` | Accepted | ❌ Fail – BUG-4 |
| U-15 Same name in NFC and NFD | `José` (é), then `José` (e + U+0301) | `DuplicateMemberError` | Accepted as a second member | ❌ Fail – BUG-5 |

### Unit tests – settle-up (`tests/unit/edge_cases/test_settlement_edge_cases.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| U-16 Empty household | No members, no expenses | Balances `{}`, transfers `[]` | `{}`, `[]` | ✅ Pass |
| U-17 Paying only for yourself | Lea pays 500 for Lea | All balances 0, no transfer | As expected | ✅ Pass |
| U-18 One-cent debt | Balances +1 / −1 | One transfer of 1 cent | As expected | ✅ Pass |
| U-19 No side effects | `{1: 600, 2: −100, 3: −500}` | Input unchanged after the call | Unchanged | ✅ Pass |
| U-20 50 members | Random balances, 50 members | ≤ 49 transfers, all > 0 | As expected | ✅ Pass |
| U-21 Balances sum to 0 | 200 random expenses, 50 settlements | Sum of balances = 0 | 0 | ✅ Pass |

### Unit tests – chores (`tests/unit/edge_cases/test_chore_edge_cases.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| U-22 Effort 1 and 5 (2) | Effort 1, effort 5 | Accepted | Accepted | ✅ Pass |
| U-23 Negative effort | Effort −1 | `ValidationError` | `ValidationError` | ✅ Pass |
| U-24 Calendar edges (4) | 0001-01-01, 9999-12-31, 2028-02-29, 2027-01-01 | Monday 0001-01-01, 9999-12-27, 2028-02-28, 2026-12-28 | As expected | ✅ Pass |
| U-25 More members than chores | 1 chore, members 10, 20, 30 | One assignment, to member 10 | As expected | ✅ Pass |
| U-26 Ties | 2 chores with effort 2, members 30, 10, 20 | Chore 1 → 10, chore 2 → 20 | As expected | ✅ Pass |
| U-27 New member | Load 10 / 10 / 0, chores with effort 5 and 1 | Effort 5 goes to the new member | As expected | ✅ Pass |
| U-28 Former members | Past load for member 99, who left | Member 99 gets nothing | As expected | ✅ Pass |

### Integration tests – wrong data types (`tests/integration/edge_cases/test_input_types_api.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| I-01 Household with wrong types (5) | `name` = 123 / null / `["Flat"]`, `name` missing, body is a list | 422 | 422 | ✅ Pass |
| I-02 Malformed JSON | `{name: Flat` | 422 | 422 | ✅ Pass |
| I-03 Expense with wrong types (9) | `amount_cents` = `"abc"` / 12.5 / null / `[3000]`, `description` = 42, `method` = `"EQUAL"` / `"split"`, `participants` = `"Lea"` / `[{"member_id": "Lea"}]` | 422 | 422 | ✅ Pass |
| I-04 Required field missing (4) | Without `payer_id` / `description` / `amount_cents` / `participants` | 422 | 422 | ✅ Pass |
| I-05 Effort with wrong type (3) | `"five"`, 2.5, null | 422 | 422 | ✅ Pass |
| I-06 Invalid date (3) | `2026-02-30`, `26.10.2026`, `""` | 422 | 422 | ✅ Pass |
| I-07 Non-numeric ID in the URL (2) | `/households/abc`, `/households/1.5/expenses` | 422 | 422 | ✅ Pass |
| I-08 Boolean as a number in an expense (2) | `amount_cents: true`, `payer_id: true` | 422 | 201: 1-cent expense / member 1 as payer | ❌ Fail – BUG-3 |
| I-09 Boolean as effort | `effort: true` | 422 | 201 with effort 1 | ❌ Fail – BUG-3 |

### Integration tests – limits and isolation (`tests/integration/edge_cases/test_limits_api.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| I-10 Member name 80 / 81 characters (2) | 80 × `x`, 81 × `x` | 201 / 400 | 201 / 400 | ✅ Pass |
| I-11 Description 120 / 121 characters (2) | 120 × `d`, 121 × `d` | 201 / 400 | 201 / 400 | ✅ Pass |
| I-12 1-cent expense for three | 1 cent, 3 participants | 201, shares 1 / 0 / 0, balances sum to 0 | As expected | ✅ Pass |
| I-13 Settlement boundary | Open debt 3000; settle 3001, then 3000 | 400, then 201 | 400, 201 | ✅ Pass |
| I-14 Largest safe amount | 2,147,483,647 cents (PostgreSQL `INTEGER` max) | 201 | 201 | ✅ Pass |
| I-15 IDs 0 and −1 (2) | `GET /households/0`, `/households/-1` | 404 | 404 | ✅ Pass |
| I-16 Delete expense via another household | `DELETE /households/{other}/expenses/{id}` | 404, expense still exists | As expected | ✅ Pass |
| I-17 Complete chore via another household | `POST /households/{other}/assignments/{id}/complete` | 404, still not completed | As expected | ✅ Pass |
| I-18 Amount beyond the database range (2) | 2³¹ and 2⁶³ cents | 400 or 422 | 2³¹: 201 on SQLite (integer overflow on PostgreSQL, see BUG-1); 2⁶³: **500** | ❌ Fail – BUG-1 |
| I-19 IDs beyond 64 bit (4) | 2⁶³ as household, expense or assignment ID on 4 endpoints | 404 or 422 | **500** | ❌ Fail – BUG-2 |
| I-20 Invisible names over HTTP (2) | U+200B, `Lea\x00` | 400 | 201 | ❌ Fail – BUG-4 |

### Integration tests – consistency (`tests/integration/edge_cases/test_consistency_api.py`)

| Test case | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| I-21 Random month fully settled | 6 members, 40 random expenses (all 3 methods), then every suggested transfer recorded | Balances sum to 0 after each step; ≤ 5 transfers, all accepted (201); afterwards all balances 0 and no suggestions | As expected | ✅ Pass |
| I-22 Delete an already settled expense | Lea pays 9000 for 3, Noah settles 3000, expense deleted | Lea −3000, Noah +3000, Mia 0; suggestion Lea → Noah 3000 | As expected | ✅ Pass |

## Findings

The application code was **not changed**. Each finding below can be filed as a GitHub
issue; the matching test turns red once the fix is in and its `xfail` marker must then
be removed from `tests/known_bugs.py`.

| ID | Severity | Where | Problem | Suggested fix |
|---|---|---|---|---|
| BUG-1 | Medium | `domain/expense.py`, `interfaces/api/schemas.py`, `infrastructure/persistence/models.py` | `amount_cents` is only checked for `> 0`, there is no upper limit. The column is `Integer`: 64 bit in SQLite, **32 bit in PostgreSQL** (max CHF 21,474,836.47). 2⁶³ cents gives HTTP 500 (verified on SQLite). Above 2³¹ − 1, PostgreSQL rejects the insert with "integer out of range" → HTTP 500 in production (derived from the column type; not run locally because Docker was not running). A typo with a few extra zeros is enough. | Add a domain constant, e.g. `MAX_AMOUNT_CENTS`, check it in `Expense.__post_init__` (→ 400) and document it with `Field(le=…)` in the schema and in UC-002. Alternatively `BigInteger` + migration, but a business limit is still advisable. |
| BUG-2 | Low | `interfaces/api/*.py` (path parameters), repositories (`session.get`) | IDs in the URL are unbounded `int`. From 2⁶³ upward, SQLite raises `OverflowError` → HTTP 500 instead of 404 on every endpoint with an ID (verified on SQLite; PostgreSQL probably answers 404, not verified). | Shared type `Id = Annotated[int, Path(ge=1, le=2**63 - 1)]` for all path IDs (→ 422), or catch `OverflowError` in the repositories and return `None` (→ 404). |
| BUG-3 | Medium | `interfaces/api/schemas.py` (all input models) | Pydantic runs in lax mode: JSON `true` becomes the integer 1. `"amount_cents": true` records a 1-cent expense, `"payer_id": true` makes member 1 the payer, `"effort": true` gives effort 1, without any error. Lax mode also turns `"9000"` into 9000 and `90.0` into 90. | `model_config = ConfigDict(strict=True)` on the input models (or `StrictInt` fields). In JSON mode, strict still accepts ISO date strings and enum values. Then decide as a team whether numeric strings should stay allowed. |
| BUG-4 | Low–Medium | `domain/validation.py` (`clean_text`) | `strip()` only removes whitespace. A name made of a zero-width space (U+200B) is accepted and shows up as an empty name in the UI. NUL (`\x00`) is accepted too, but PostgreSQL cannot store NUL in text columns → HTTP 500 in production (not verified locally). | Reject control characters (Unicode category `Cc`), and treat a name made only of whitespace and invisible format characters (U+200B, U+200C, U+200D, U+2060, U+FEFF) as empty. Do not reject all `Cf` characters: U+200D is needed for emoji such as 👨‍👩‍👧. |
| BUG-5 | Low | `domain/validation.py`, `domain/household.py` (`add_member`) | The duplicate check compares `casefold()` without Unicode normalization. `José` typed as é (NFC) and as e + combining accent (NFD, common on macOS) count as two different members although they look identical. | `unicodedata.normalize("NFC", text)` in `clean_text` before trimming and checking the length. |

### Observations (no bug, team decision)

- Chore names are not unique: two chores called "Kitchen" can be created. UC-004 does not require uniqueness.
- The domain layer does not check types itself (`Member(name=None)` raises `AttributeError`, not `ValidationError`). That is fine because Pydantic validates at the API boundary and `mypy --strict` checks the code.
- Type errors return **422** (Pydantic), rule violations return **400** (domain). That is consistent and documented, but clients have to handle both codes.
- The README listed 39 integration tests; 44 were actually collected before this suite was added. The numbers are now updated.

### Not covered

- E2E tests against PostgreSQL (`tests/e2e`) were not run, because the Docker daemon was not running. That is why the PostgreSQL parts of BUG-1 and BUG-4 are derived from the code and still need a check against PostgreSQL.
- UC-005 (scan receipt) is only specified, there is no code to test yet.
- The web UI (`/ui`) is not covered by automated tests.
