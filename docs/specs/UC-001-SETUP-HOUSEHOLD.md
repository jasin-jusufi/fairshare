# UC-001-SETUP-HOUSEHOLD

## Intent
A shared flat creates a shared household and adds its members. Without a
household and members, no expenses can be split and no chores can be
assigned.

## Actors

Primary: Flatmate (creates the household, adds members)
Secondary: —

## Preconditions

- None. For "add member", the household must exist.

## Flow

1. A member creates a household with a name (currency CHF).
2. The system stores the household and returns it with its ID.
3. The member adds further members by name.
4. The system checks that the name is unique within the household and stores the member.
5. The member retrieves the household with all members or lists all households.

## Errors

- invalid input: household name or member name empty / whitespace only / longer than 80 characters → 400
- duplicate: member name already exists in the household (case-insensitive) → 409
- not found: household does not exist → 404

## Acceptance

- AC1 Given no household, When `POST /households {"name": "Flat Basel"}`, Then 201 with `id`, `name`, `currency = "CHF"`, `members = []`.
- AC2 Given a household, When `POST /households/{id}/members {"name": "Lea"}`, Then 201 with the member's `id` and `name`.
- AC3 Given member "Lea", When member "lea" is added, Then 409.
- AC4 Given an empty name, When a household or member is created, Then 400.
- AC5 Given an unknown household ID, When it is retrieved or a member is added, Then 404.
- AC6 Given two households, When `GET /households`, Then both are returned in creation order.
- AC7 Given a household with members, When `GET /households/{id}`, Then all members are included.

## Tests

Unit: name validation (`Household`, `Member`), duplicate check, `HouseholdService` with in-memory repository
Integration: AC1–AC7 via `TestClient` + SQLite in-memory
E2E: create a household and add a member against the container

## Design

| Layer | Component |
|---|---|
| domain | `Household`, `Member` (entities), `ValidationError`, `DuplicateMemberError` |
| application | `HouseholdService` (`create_household`, `add_member`, `get_household`, `list_households`), port `HouseholdRepository`, `NotFoundError` |
| interfaces | Router `/households`, schemas `HouseholdCreate`, `MemberCreate`, `HouseholdOut`, `MemberOut`, error mapping 400/404/409 |
| infrastructure | `HouseholdModel`, `MemberModel`, `SqlAlchemyHouseholdRepository`, Alembic migration, wiring in `create_app` |
