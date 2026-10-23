# ADR-007: Greedy-Algorithmus für Ausgleichszahlungen

- **Status:** akzeptiert
- **Datum:** 2026-10-23

## Kontext

Aus den Salden sollen Überweisungen abgeleitet werden. Naiv überweist jede
Person pro Ausgabe an die zahlende Person (viele kleine Zahlungen). Die
minimale Anzahl Überweisungen zu finden ist NP-schwer (Partitionsproblem).
Haushalte haben typischerweise 2–8 Mitglieder.

## Alternativen

1. Pro Ausgabe und Person eine Überweisung (einfach, aber bis zu O(Ausgaben × n))
2. Exakte Optimierung über Teilmengen-Suche (exponentiell)
3. Greedy: grösste Schuld gegen grösstes Guthaben verrechnen, wiederholen

## Entscheid

Variante 3. Jeder Schritt gleicht mindestens eine Person vollständig aus,
daher entstehen höchstens n − 1 Überweisungen. Gleichstände werden nach
Mitglied-ID aufgelöst, damit das Ergebnis deterministisch und testbar ist.
Der Algorithmus ist eine reine Funktion im Domain-Layer.

## Konsequenzen

- Laufzeit O(n²), für Haushaltsgrössen vernachlässigbar.
- Nicht immer global minimal, aber garantiert ≤ n − 1 und in Tests als
  Eigenschaft geprüft (Summe 0, Obergrenze, alle Salden danach 0).
- Ausgleichszahlungen dürfen offene Schulden nicht übersteigen, damit keine
  neuen Schulden durch Tippfehler entstehen.
