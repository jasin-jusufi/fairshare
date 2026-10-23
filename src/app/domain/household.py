from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.errors import DuplicateMemberError
from app.domain.validation import clean_text

MAX_NAME_LENGTH = 80


@dataclass
class Member:
    name: str
    household_id: int | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        self.name = clean_text(self.name, "Member name", MAX_NAME_LENGTH)


@dataclass
class Household:
    name: str
    currency: str = "CHF"
    members: list[Member] = field(default_factory=list)
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.name = clean_text(self.name, "Household name", MAX_NAME_LENGTH)

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
