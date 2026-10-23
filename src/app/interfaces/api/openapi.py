from typing import Any

from app.interfaces.api.schemas import ErrorOut

TAGS: list[dict[str, Any]] = [
    {
        "name": "Haushalte",
        "description": "Haushalt anlegen und Mitglieder verwalten (UC-001). "
        "Alle anderen Ressourcen hängen an einem Haushalt.",
    },
    {
        "name": "Ausgaben",
        "description": "Gemeinsame Ausgaben erfassen und aufteilen (UC-002): gleich, prozentual "
        "oder nach Anteilen. Restrappen werden nach Largest-Remainder verteilt.",
    },
    {
        "name": "Abrechnen",
        "description": "Salden, Ausgleichsvorschläge mit höchstens n − 1 Überweisungen und "
        "erfasste Zahlungen (UC-003).",
    },
    {
        "name": "Ämtli",
        "description": "Ämtli mit Aufwand 1–5 und faire Wochenplanung nach bisheriger Last "
        "(UC-004).",
    },
    {"name": "Betrieb", "description": "Health-Check für Container, Render und Smoke-Tests."},
]

Responses = dict[int | str, dict[str, Any]]


def error(status: int, description: str) -> Responses:
    return {status: {"model": ErrorOut, "description": description}}


NOT_FOUND = error(404, "Haushalt oder Ressource existiert nicht")
INVALID = error(400, "Verletzte Geschäftsregel, z. B. leerer Name oder ungültiger Betrag")
CONFLICT = error(409, "Widerspruch zum aktuellen Zustand, z. B. Duplikat")
