# UC-004-ROTATE-CHORES

## Intent
Chores (cleaning the bathroom, kitchen, trash …) should be distributed **fairly
by effort**, not just in turn. Whoever had a lot of effort in past weeks gets
less this week.

## Actors

Primary: Flatmate (maintains chores, plans the week, ticks off completed chores)
Secondary: other members (receive assignments)

## Preconditions

- Household with at least one member (UC-001).

## Flow

1. A member records chores with a name and effort (1–5 points).
2. A member plans a week (any date → Monday of that week).
3. The system assigns each chore exactly once: the most demanding one first, to the member with the lowest total load so far (history up to and including this week, later weeks are ignored); ties → lower member ID (LPT heuristic).
4. Members see the weekly plan and tick off completed chores with a clearly labelled "Done" button.
5. Chores added after a week was planned can be planned into that week later: only the
   chores missing from the week are assigned, by the same rule and counting the load
   already assigned; existing assignments stay unchanged (feedback from the live
   deployment, 2026-10-27).
6. Members see the cumulative load per person (fairness overview).

## Errors

- invalid input: empty name, effort outside 1–5 → 400
- nothing to plan: no chores or no members → 400
- conflict: week already planned and no chore missing from it, assignment already completed → 409
- not found: household or assignment does not exist → 404

## Acceptance

- AC1 Given a household, When `POST …/chores {"name": "Bathroom", "effort": 5}`, Then 201 with `id`, `name`, `effort`.
- AC2 Given effort 0 or 6, When recorded, Then 400.
- AC3 Given Lea, Noah, Mia and chores Bathroom 5, Kitchen 3, Trash 1, Vacuuming 3, When the week is planned, Then Bathroom → Lea, Kitchen → Noah, Vacuuming → Mia, Trash → Noah.
- AC4 Given AC3, When the following week is planned, Then after two weeks every member has exactly 8 points.
- AC5 Given a planned week and no new chores, When the same week is planned again, Then 409.
- AC6 Given the date Thursday 2026-10-29, When planned, Then `week_start = 2026-10-26`.
- AC7 Given an assignment, When `POST …/assignments/{id}/complete`, Then 200 with `completed_at`; again → 409; unknown ID → 404.
- AC8 Given no chores, When a week is planned, Then 400.
- AC9 Given planned weeks, When `GET …/chore-load`, Then points per member.
- AC10 Given Lea and Noah and a week planned with Bathroom 5 (→ Lea), When Kitchen 3 is added and the same week is planned again, Then 201 with only Kitchen → Noah, and the week now holds both assignments with Bathroom unchanged.
- AC11 Given the web UI, Then each assignment shows a labelled "Done" button (afterwards "Done ✓"), and "Plan fairly" is offered again while chores are missing from the week.

## Tests

Unit: `week_start_of`, `plan_week` (order, ties, history, fairness over many weeks), `Chore`/`ChoreAssignment` invariants, `ChoreService`
Integration: AC1–AC11 via `TestClient` + SQLite in-memory
E2E: create chores and plan a week against the container

## Design

| Layer | Component |
|---|---|
| domain | `Chore`, `ChoreAssignment` (entities), `week_start_of()`, `plan_week()`, `ConflictError` as the base for 409 errors |
| application | `ChoreService` (`add_chore`, `list_chores`, `plan_week`, `week_plan`, `complete_assignment`, `load_by_member`), ports `ChoreRepository`, `ChoreAssignmentRepository` |
| interfaces | Router `/households/{id}/chores`, `/chore-plans`, `/assignments/{id}/complete`, `/chore-load` |
| infrastructure | `ChoreModel`, `ChoreAssignmentModel` (unique: chore + week), repositories, migration |

The assignment stores the effort as a snapshot so that later changes to the
chore do not distort the fairness history.
