from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.errors import DuplicateMemberError, ValidationError

MAX_NAME_LENGTH = 80


def clean_name(value: str, label: str) -> str:
    name = value.strip()
    if not name:
        raise ValidationError(f"{label} must not be empty")
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(f"{label} must be at most {MAX_NAME_LENGTH} characters")
    return name


@dataclass
class Member:
    name: str
    household_id: int | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        self.name = clean_name(self.name, "Member name")


@dataclass
class Household:
    name: str
    currency: str = "CHF"
    members: list[Member] = field(default_factory=list)
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.name = clean_name(self.name, "Household name")

    def add_member(self, name: str) -> Member:
        member = Member(name=name, household_id=self.id)
        if any(m.name.casefold() == member.name.casefold() for m in self.members):
            raise DuplicateMemberError(f"Member '{member.name}' already exists")
        self.members.append(member)
        return member

    def has_member(self, member_id: int) -> bool:
        return any(m.id == member_id for m in self.members)

    def member_ids(self) -> set[int]:
        return {m.id for m in self.members if m.id is not None}
