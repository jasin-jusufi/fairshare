# UC-005-SCAN-RECEIPT

> Owner: **Bajram** · Status: spezifiziert, Umsetzung offen

## Intent
Statt Betrag und Beschreibung abzutippen, lädt ein Mitglied ein Foto des
Kassenbons hoch. Ein KI-Modell schlägt Beschreibung und Betrag vor; das
Mitglied bestätigt und erfasst die Ausgabe wie in UC-002.

## Actors

Primary: WG-Mitglied
Secondary: Externes Vision-LLM (über Port `ReceiptParser`)

## Preconditions

- Haushalt existiert (UC-001).
- Für Produktion: `ANTHROPIC_API_KEY` ist gesetzt (nur als Secret, nie im Repo).

## Flow

1. Mitglied lädt ein Bild hoch (`POST /households/{id}/receipts`, JPEG/PNG, ≤ 5 MB).
2. Application-Service ruft den Port `ReceiptParser.parse(image_bytes, media_type)` auf.
3. Adapter (Infrastruktur) fragt das LLM nach strukturiertem JSON `{merchant, total_cents, date}`.
4. Service validiert den Vorschlag (Betrag > 0, Beschreibung 1–120 Zeichen) und gibt ihn zurück. **Es wird nichts gespeichert.**
5. UI füllt das Formular von UC-002 vor; das Mitglied bestätigt.

## Errors

- invalid input: falscher Dateityp oder zu gross → 400
- unreadable: Modell findet keinen Betrag → 422
- unavailable: kein API-Key oder LLM nicht erreichbar → 503
- not found: Haushalt existiert nicht → 404

## Acceptance

- AC1 Given Fake-Parser liefert „Migros, 2350“, When Bild hochgeladen, Then 200 mit `description = "Migros"`, `amount_cents = 2350`.
- AC2 Given PDF statt Bild, When hochgeladen, Then 400.
- AC3 Given Parser findet keinen Betrag, When hochgeladen, Then 422.
- AC4 Given kein API-Key konfiguriert, When hochgeladen, Then 503.
- AC5 Given Vorschlag, Then es existiert danach **keine** neue Ausgabe.

## Tests

Unit: `ReceiptService` mit `FakeReceiptParser`, Validierung des Vorschlags
Integration: AC1–AC5 mit Fake-Adapter über `dependency_overrides`
E2E: nicht im CI (externe API); manueller Test dokumentieren

## Design

| Layer | Komponente |
|---|---|
| domain | `ReceiptSuggestion` (Value Object, Validierung) |
| application | `ReceiptService`, Port `ReceiptParser` (`Protocol`), `ReceiptUnreadableError`, `ParserUnavailableError` |
| interfaces | Router `POST /households/{id}/receipts` (`UploadFile`), Schema `ReceiptSuggestionOut` |
| infrastructure | `AnthropicReceiptParser` (Anthropic SDK, Vision), Auswahl per Env in `create_app`; Fallback ohne Key → 503 |

Neue Abhängigkeiten (`anthropic`, `python-multipart`) und die Wahl des Modells
→ ADR-008. Der Port sorgt dafür, dass Domain und Application das LLM nicht kennen
und alle Tests ohne Netzwerk laufen.
