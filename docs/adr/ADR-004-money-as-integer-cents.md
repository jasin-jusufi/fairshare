# ADR-004: Geldbeträge als ganzzahlige Rappen

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Beim Aufteilen von Ausgaben entstehen Restbeträge (CHF 100 / 3). Floats führen
zu Rundungsfehlern; die Summe der Anteile muss exakt dem Betrag entsprechen,
sonst stimmen Salden nie auf null.

## Alternativen

1. `float`
2. `decimal.Decimal` mit Rundung
3. `int` in Rappen, Restverteilung nach Largest-Remainder-Verfahren

## Entscheid

Variante 3. Alle Beträge sind `int` in Rappen (`amount_cents`). Beim Splitten
werden übrig bleibende Rappen deterministisch an die Teilnehmenden mit dem
grössten Bruchteil verteilt (bei Gleichstand nach Reihenfolge).

## Konsequenzen

- Invariante „Summe der Anteile = Betrag“ ist exakt prüfbar und getestet.
- API und UI rechnen CHF ↔ Rappen an der Grenze um.
- Einwährungssystem (CHF) — Mehrwährung ist Out of Scope.
