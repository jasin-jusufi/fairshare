import pytest

from app.domain.errors import DuplicateMemberError, ValidationError
from app.domain.household import Household, Member


@pytest.mark.parametrize(
    ("name", "valid"),
    [("A", True), ("x" * 80, True), ("x" * 81, False), ("  " + "x" * 80 + "  ", True)],
    ids=["1-char", "80-chars", "81-chars", "80-chars-plus-spaces"],
)
def test_name_length_boundaries(name: str, valid: bool) -> None:
    """Boundary values of the 1–80 rule; surrounding spaces are trimmed before counting,
    so 80 characters with padding are still valid."""
    if valid:
        assert Member(name=name).name == name.strip()
    else:
        with pytest.raises(ValidationError):
            Member(name=name)


@pytest.mark.parametrize(
    "name", ["\t\n", " ", "　"], ids=["tab-newline", "nbsp", "ideographic-space"]
)
def test_unicode_whitespace_only_names_are_rejected(name: str) -> None:
    """Empty input in disguise: tabs, non-breaking and full-width spaces count as blank."""
    with pytest.raises(ValidationError):
        Household(name=name)


def test_umlauts_and_emoji_are_kept_unchanged() -> None:
    """Valid non-ASCII input must survive trimming unchanged (no encoding damage)."""
    assert Member(name=" Zoë 🏠 ").name == "Zoë 🏠"


def test_duplicate_check_uses_full_unicode_case_folding() -> None:
    """`casefold` (not just `lower`) treats German ß like ss, so STRAUß equals Strauss."""
    household = Household(name="Flat")
    household.add_member("Strauss")
    with pytest.raises(DuplicateMemberError):
        household.add_member("STRAUß")


@pytest.mark.parametrize(
    "name", ["​", "\x00", "Lea\x00"], ids=["zero-width-space", "nul", "nul-inside"]
)
def test_invisible_and_control_characters_are_rejected(name: str) -> None:
    """A zero-width space looks empty in the UI, and NUL cannot be stored in PostgreSQL
    text columns, so both should fail validation like a blank name."""
    with pytest.raises(ValidationError):
        Member(name=name)


def test_composed_and_decomposed_names_are_duplicates() -> None:
    """'José' can be typed as one character é (NFC) or e + combining accent (NFD, e.g. on
    macOS). Both look identical, so the second one should be rejected as a duplicate."""
    household = Household(name="Flat")
    household.add_member("José")
    with pytest.raises(DuplicateMemberError):
        household.add_member("José")
