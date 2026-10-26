class NotFoundError(Exception):
    pass


class ReceiptUnreadableError(Exception):
    """The parser found no usable description and amount on the receipt."""


class ParserUnavailableError(Exception):
    """Receipt scanning is switched off or the parser cannot be reached."""
