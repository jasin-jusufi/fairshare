# UC-001-SETUP-HOUSEHOLD

## Intent
Eine WG legt einen gemeinsamen Haushalt an und erfasst ihre Mitglieder. Ohne
Haushalt und Mitglieder können keine Ausgaben geteilt und keine Ämtli verteilt
werden.

## Actors

Primary: WG-Mitglied (legt Haushalt an, fügt Mitglieder hinzu)
Secondary: —

## Preconditions

- Keine. Für „Mitglied hinzufügen“ muss der Haushalt existieren.

## Flow

1. Mitglied erstellt einen Haushalt mit Namen (Währung CHF).
2. System speichert den Haushalt und gibt ihn mit ID zurück.
3. Mitglied fügt weitere Mitglieder mit Namen hinzu.
4. System prüft die Eindeutigkeit des Namens im Haushalt und speichert.
5. Mitglied ruft den Haushalt mit allen Mitgliedern ab oder listet alle Haushalte.

## Errors

- invalid input: Haushaltsname oder Mitgliedername leer / nur Leerzeichen / länger als 80 Zeichen → 400
- duplicate: Mitgliedername existiert im Haushalt bereits (Gross-/Kleinschreibung egal) → 409
- not found: Haushalt existiert nicht → 404

## Acceptance

- AC1 Given kein Haushalt, When `POST /households {"name": "WG Basel"}`, Then 201 mit `id`, `name`, `currency = "CHF"`, `members = []`.
- AC2 Given Haushalt, When `POST /households/{id}/members {"name": "Lea"}`, Then 201 mit Mitglied-`id` und `name`.
- AC3 Given Mitglied „Lea“, When Mitglied „lea“ hinzugefügt wird, Then 409.
- AC4 Given leerer Name, When Haushalt oder Mitglied erstellt wird, Then 400.
- AC5 Given unbekannte Haushalt-ID, When abgerufen oder Mitglied hinzugefügt wird, Then 404.
- AC6 Given zwei Haushalte, When `GET /households`, Then beide in Erstellungsreihenfolge.
- AC7 Given Haushalt mit Mitgliedern, When `GET /households/{id}`, Then alle Mitglieder enthalten.

## Tests

Unit: Namensvalidierung (`Household`, `Member`), Duplikatprüfung, `HouseholdService` mit In-Memory-Repository
Integration: AC1–AC7 über `TestClient` + SQLite in-memory
E2E: Haushalt anlegen und Mitglied hinzufügen gegen den Container

## Design

| Layer | Komponente |
|---|---|
| domain | `Household`, `Member` (Entities), `ValidationError`, `DuplicateMemberError` |
| application | `HouseholdService` (`create_household`, `add_member`, `get_household`, `list_households`), Port `HouseholdRepository`, `NotFoundError` |
| interfaces | Router `/households`, Schemas `HouseholdCreate`, `MemberCreate`, `HouseholdOut`, `MemberOut`, Fehler-Mapping 400/404/409 |
| infrastructure | `HouseholdModel`, `MemberModel`, `SqlAlchemyHouseholdRepository`, Alembic-Migration, Wiring in `create_app` |
