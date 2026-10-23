from app.domain.errors import ValidationError


def clean_text(value: str, label: str, max_length: int) -> str:
    text = value.strip()
    if not text:
        raise ValidationError(f"{label} must not be empty")
    if len(text) > max_length:
        raise ValidationError(f"{label} must be at most {max_length} characters")
    return text
