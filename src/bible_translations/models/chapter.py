from dataclasses import dataclass
from typing import TYPE_CHECKING

from bible_translations.models.verse import Verse

if TYPE_CHECKING:
    from bible_translations.models.book import Book
    from bible_translations.translations.base import Translation


@dataclass
class Chapter:
    number: int
    verses: list[Verse]
    book: "Book"

    @property
    def translation(self) -> "Translation":
        return self.book.translation
