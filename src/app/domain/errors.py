class DomainError(Exception):
    """Base class for violated business rules."""


class ValidationError(DomainError):
    pass


class DuplicateMemberError(DomainError):
    pass


class UnknownMemberError(ValidationError):
    pass
