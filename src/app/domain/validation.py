import unicodedata

from app.domain.errors import ValidationError

INVISIBLE = "​‌‍⁠﻿"


def clean_text(value: str, label: str, max_length: int) -> str:
    text = unicodedata.normalize("NFC", value).strip()
    if not text.strip(INVISIBLE).strip():
        raise ValidationError(f"{label} must not be empty")
    if any(unicodedata.category(char) == "Cc" for char in text):
        raise ValidationError(f"{label} must not contain control characters")
    if len(text) > max_length:
        raise ValidationError(f"{label} must be at most {max_length} characters")
    return text
