class VerseNotFoundError(Exception):
    """Raised when a requested verse cannot be found."""

    pass


class BookNotFoundError(Exception):
    """Raised when a requested book cannot be found."""

    pass


class ChapterNotFoundError(Exception):
    """Raised when a requested chapter cannot be found."""

    pass


class SelectionInvalidError(Exception):
    """Raised when a selection is invalid."""

    pass
