import asyncio
from abc import ABC, abstractmethod

from bible_translations.constants import DEFAULT_BOOK_CHAPTER_COUNTS
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.verse import Verse


def _run_async(coro):
    """
    Safely run an async coroutine in both sync and async contexts.

    - If no event loop is running, it creates one.
    - If called within an existing loop, schedules a new task.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.create_task(coro)


class Translation(ABC):
    """
    Base class for all Bible translations.
    Implementations should define async methods; sync wrappers are provided for convenience.
    """

    name: str
    abbreviation: str
    copyright: str
    language: str = "English"
    books: list[str] = list(DEFAULT_BOOK_CHAPTER_COUNTS.keys())
    book_chapter_counts: dict[str, int] = DEFAULT_BOOK_CHAPTER_COUNTS

    # ---------- Retrieval methods ----------

    @abstractmethod
    async def aget_books(self) -> list[Book]:
        """
        Asynchronously return all books available in this translation.

        :returns: list[Book]: A list of all `Book` objects for the translation.
        """
        raise NotImplementedError

    def get_books(self) -> list[Book]:
        """
        Synchronously return all books available in this translation.

        :returns: list[Book]: A list of all `Book` objects for the translation.
        """
        return _run_async(self.aget_books())

    @abstractmethod
    async def aget_book(self, name: str) -> Book:
        """
        Asynchronously return a single book by name.

        :param name: The book name (e.g., "Genesis", "John").
        :returns: Book: The corresponding `Book` object containing all chapters and verses.
        """
        raise NotImplementedError

    def get_book(self, name: str) -> Book:
        """
        Synchronously return a single book by name.

        :param name: The book name (e.g., "Genesis", "John").
        :returns: Book: The corresponding `Book` object containing all chapters and verses.
        """
        return _run_async(self.aget_book(name))

    @abstractmethod
    async def aget_chapter(self, book_name: str, chapter_number: int) -> Chapter:
        """
        Asynchronously return a single chapter by book name and chapter number.

        :param book_name: Name of the book (e.g., "John").
        :param chapter_number: Chapter number to retrieve.
        :returns: Chapter: The `Chapter` object, including its verses.
        """
        raise NotImplementedError

    def get_chapter(self, book_name: str, chapter_number: int) -> Chapter:
        """
        Synchronously return a single chapter by book name and chapter number.

        :param book_name: Name of the book (e.g., "John").
        :param chapter_number: Chapter number to retrieve.
        :returns: Chapter: The `Chapter` object, including its verses.
        """
        return _run_async(self.aget_chapter(book_name, chapter_number))

    @abstractmethod
    async def aget_verse(self, book_name: str, chapter_number: int, verse_number: int) -> Verse:
        """
        Asynchronously return a single verse by book, chapter, and verse number.

        :param book_name: Name of the book.
        :param chapter_number: Chapter number.
        :param verse_number: Verse number.
        :returns: Verse: The requested `Verse` object, linked to its chapter, book, and translation.
        """
        raise NotImplementedError

    async def get_verse(self, book_name: str, chapter_number: int, verse_number: int) -> Verse:
        """
        Synchronously return a single verse by book, chapter, and verse number.

        :param book_name: Name of the book.
        :param chapter_number: Chapter number.
        :param verse_number: Verse number.
        :returns: Verse: The requested `Verse` object, linked to its chapter, book, and translation.
        """
        return _run_async(self.aget_verse(book_name, chapter_number, verse_number))

    # ---------- Selection retrieval ----------

    async def aget_selection(
        self,
        start_ref: str | None = None,
        end_ref: str | None = None,
        *,
        start_book: str | None = None,
        start_chapter: int | None = None,
        start_verse: int | None = None,
        end_book: str | None = None,
        end_chapter: int | None = None,
        end_verse: int | None = None,
    ) -> list[Verse]:
        """
        Asynchronously return a continuous selection of verses between two points.

        Can be called with string references or explicit numeric arguments:

            await aget_selection("John 3:16", "John 5:1")

            await aget_selection(
                start_book="John", start_chapter=3, start_verse=16,
                end_book="John", end_chapter=5, end_verse=1)

        :param start_ref: Optional string reference for the start (e.g., "John 3:16").
        :param end_ref: Optional string reference for the end (e.g., "John 5:1").
        :param start_book: Start book name if using numeric mode.
        :param start_chapter: Start chapter number.
        :param start_verse: Start verse number.
        :param end_book: End book name if using numeric mode.
        :param end_chapter: End chapter number.
        :param end_verse: End verse number.
        :returns: list[Verse]: A list of `Verse` objects covering the inclusive range.
        """
        if start_ref and end_ref:
            start_book, start_chapter, start_verse = self._parse_ref(start_ref)
            end_book, end_chapter, end_verse = self._parse_ref(end_ref)

        return self._aget_selection_range(start_book, start_chapter, start_verse, end_book, end_chapter, end_verse)

    async def get_selection(
        self,
        start_ref: str | None = None,
        end_ref: str | None = None,
        *,
        start_book: str | None = None,
        start_chapter: int | None = None,
        start_verse: int | None = None,
        end_book: str | None = None,
        end_chapter: int | None = None,
        end_verse: int | None = None,
    ) -> list[Verse]:
        """
        Synchronously return a continuous selection of verses between two points.

        Can be called with string references or explicit numeric arguments:

            get_selection("John 3:16", "John 5:1")

            get_selection(
                start_book="John", start_chapter=3, start_verse=16,
                end_book="John", end_chapter=5, end_verse=1)

        :param start_ref: Optional string reference for the start (e.g., "John 3:16").
        :param end_ref: Optional string reference for the end (e.g., "John 5:1").
        :param start_book: Start book name if using numeric mode.
        :param start_chapter: Start chapter number.
        :param start_verse: Start verse number.
        :param end_book: End book name if using numeric mode.
        :param end_chapter: End chapter number.
        :param end_verse: End verse number.
        :returns: list[Verse]: A list of `Verse` objects covering the inclusive range.
        """
        if start_ref and end_ref:
            start_book, start_chapter, start_verse = self._parse_ref(start_ref)
            end_book, end_chapter, end_verse = self._parse_ref(end_ref)

        return _run_async(
            self._aget_selection_range(start_book, start_chapter, start_verse, end_book, end_chapter, end_verse)
        )

    @abstractmethod
    def _aget_selection_range(
        self,
        start_book: str,
        start_chapter: int,
        start_verse: int,
        end_book: str,
        end_chapter: int,
        end_verse: int,
    ) -> list[Verse]:
        """
        Asynchronously retrieve a continuous list of verses between two reference points.

        This method must be implemented by subclasses to define
        how verses are loaded or generated internally.

        :param start_book: Name of the starting book.
        :param start_chapter: Starting chapter number.
        :param start_verse: Starting verse number.
        :param end_book: Name of the ending book.
        :param end_chapter: Ending chapter number.
        :param end_verse: Ending verse number.
        :returns: list[Verse]: Ordered list of all `Verse` objects in the range.
        """
        raise NotImplementedError

    @staticmethod
    def _parse_ref(self, ref: str) -> tuple[str, int, int]:
        """
        Parse a string reference into components.

        Example:
            "John 3:16" → ("John", 3, 16)

        Args:
            ref (str): Reference string formatted as "Book Chapter:Verse".

        Returns:
            tuple[str, int, int]: (book_name, chapter_number, verse_number)
        """
        book, rest = ref.split(" ", 1)
        chapter, verse = rest.split(":")
        return book, int(chapter), int(verse)
