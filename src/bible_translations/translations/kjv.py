from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.verse import Verse
from bible_translations.translations.base import Translation


class KJV(Translation):
    name = "King James Version"
    abbreviation = "KJV"
    copyright = "Public Domain"

    async def aget_books(self) -> list[Book]:
        pass

    async def aget_book(self, name: str) -> Book:
        pass

    async def aget_chapter(self, book_name: str, chapter_number: int) -> Chapter:
        pass

    async def aget_verse(self, book_name: str, chapter_number: int, verse_number: int) -> Verse:
        pass

    def _aget_selection_range(
        self, start_book: str, start_chapter: int, start_verse: int, end_book: str, end_chapter: int, end_verse: int
    ) -> list[Verse]:
        pass
