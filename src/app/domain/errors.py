class DomainError(Exception):
    """Base class for violated business rules."""


class ValidationError(DomainError):
    pass


class ConflictError(DomainError):
    """The request conflicts with the current state."""


class DuplicateMemberError(ConflictError):
    pass


class UnknownMemberError(ValidationError):
    pass


class OverpaymentError(DomainError):
    pass
