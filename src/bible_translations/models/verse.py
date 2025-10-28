from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bible_translations.models.book import Book
    from bible_translations.models.chapter import Chapter
    from bible_translations.translations.base import Translation


@dataclass
class Verse:
    number: int
    text: str
    heading: str | None = None
    superscription: str | None = None
    footnotes: list[str] | None = None
