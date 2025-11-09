import asyncio
from contextlib import nullcontext

from bible_translations.exceptions import BookNotFoundError, ChapterNotFoundError, VerseNotFoundError
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.verse import Verse
from bible_translations.translations.base import Translation
from bible_translations.utils.fetch.bible_gateway import BibleGatewayClient
from bible_translations.utils.logger import logger


class BibleGatewayTranslation(Translation):
    """
    Generic Translation implementation backed by BibleGateway scraping.

    This class centralizes the scraping routines used by multiple translations on
    BibleGateway so that adding new translations only requires defining a
    lightweight subclass with metadata (name, abbreviation, copyright).

    Usage example:
        class KJV(BibleGatewayTranslation):
            name = "King James Version"
            abbreviation = "KJV"
            copyright = "Public Domain"

    Notes on resource usage:
    - Methods that trigger multiple downstream requests (aget_books, _aget_selection_range)
      create a single BibleGatewayClient session and pass it down, preventing the creation of
      too many sessions.
    - Leaf calls (aget_chapter, aget_verse) accept an optional client; if none is provided,
      they create a short-lived session for just that call.

    Customization hooks:
    - Override _get_container_selector() if a specific translation renders differently on BibleGateway.
    - Override _normalize_book_name() if you need special book-name aliases.
    - Set max_concurrency to limit concurrent requests per high-level call.
    """

    # Optional cap for concurrency per high-level operation (None = no explicit cap)
    max_concurrency: int | None = None

    def _get_container_selector(self) -> str:
        """
        Return the CSS selector for the chapter container for this translation.

        Default maps to BibleGateway's structure, e.g.: div.version-KJV.result-text-style-normal.text-html
        """
        return f"div.version-{self.abbreviation}.result-text-style-normal.text-html"

    def _normalize_book_name(self, name: str) -> str:
        """
        Map an input book name (any casing) to the canonical name from self.books.
        :param name: The book name (e.g., "Genesis", "John").

        :returns: str: The canonical book name.
        :raises BookNotFoundError: if the provided name is not recognized.
        """
        mapping = {k.lower(): k for k in self.books}
        lower = name.lower()
        if lower not in mapping:
            raise BookNotFoundError(f"Book not found: {name}")
        return mapping[lower]

    def _maybe_normalize_book_name(self, name: str) -> str:
        """Best-effort normalization that falls back to the original name if not recognized."""
        try:
            return self._normalize_book_name(name)
        except BookNotFoundError:
            return name

    @staticmethod
    async def _with_sem(sem: asyncio.Semaphore, coro_func, *args, **kwargs):
        async with sem:
            return await coro_func(*args, **kwargs)

    async def aget_books(self) -> list[Book]:
        """
        Asynchronously return all books available in this translation by fetching
        each book concurrently using a single shared HTTP session.

        :returns: list[Book]: A list of all `Book` objects for the translation.
        """
        async with BibleGatewayClient() as client:
            names = list(self.books)
            sem = asyncio.Semaphore(self.max_concurrency) if self.max_concurrency else None

            async def run(name_: str):
                if sem:
                    return await self._with_sem(sem, self.aget_book, name_, client)
                return await self.aget_book(name_, client)

            tasks = [asyncio.create_task(run(name)) for name in names]
            for i, (name, task) in enumerate(zip(names, tasks), 1):
                task.add_done_callback(
                    lambda x, book=name, idx=i: logger.debug(f"[{idx}] Completed fetching book: {book}")
                )

            results = await asyncio.gather(*tasks)
            results_by_book = dict(zip(names, results))
            sorted_results = [results_by_book[name] for name in names]
            return sorted_results

    async def aget_book(self, name: str, client: BibleGatewayClient | None = None) -> Book:
        """
        Asynchronously return a single book by name.

        A single client is propagated downstream to avoid opening multiple sessions.

        :param name: The book name (e.g., "Genesis", "John").
        :param client: Optional shared `BibleGatewayClient` to reuse.
        :returns: Book: The corresponding `Book` object containing all chapters and verses.
        :raises BookNotFoundError: If the book name is not recognized for this translation.
        """
        # Normalize to canonical book name (strict) to accept different casing
        canonical_name = self._normalize_book_name(name)

        chapter_count = self.book_chapter_counts[canonical_name]

        # Prepare concurrent chapter fetch tasks, reusing session if provided
        async def run(i: int, cl: BibleGatewayClient):
            return await self.aget_chapter(canonical_name, i, cl)

        sem = asyncio.Semaphore(self.max_concurrency) if self.max_concurrency else None

        client_to_use = client or BibleGatewayClient()
        async with client_to_use if client is None else nullcontext() as session_client:
            client_for_tasks = session_client if client is None else client
            tasks = [
                asyncio.create_task(
                    self._with_sem(sem, run, i, client_for_tasks) if sem else run(i, client_for_tasks)
                )
                for i in range(1, chapter_count + 1)
            ]
            results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x.number)
        return Book(name=canonical_name, chapters=results)

    async def aget_chapter(
        self, book_name: str, chapter_number: int, client: BibleGatewayClient | None = None
    ) -> Chapter:
        """
        Asynchronously return a chapter by book name and chapter number, scraped from BibleGateway.

        :param book_name: Name of the book (e.g., "John").
        :param chapter_number: Chapter number to retrieve.
        :param client: Optional shared `BibleGatewayClient` to reuse.
        :returns: Chapter: The `Chapter` object, including its verses.
        :raises ChapterNotFoundError: If the chapter cannot be found on BibleGateway.
        """
        canonical_book = self._maybe_normalize_book_name(book_name)
        query = f"{canonical_book}+{chapter_number}&version={self.abbreviation}"
        logger.debug(f"Query: {query}")

        if client is None:
            async with BibleGatewayClient() as new_client:
                soup = await new_client.fetch(query)
        else:
            soup = await client.fetch(query)

        # Resolve the appropriate container selector and locate content
        container_selector = self._get_container_selector()
        container = soup.select_one(container_selector)
        if not container:
            raise ChapterNotFoundError(f"Chapter not found: {book_name} {chapter_number}")

        verses: list[Verse] = []
        for verse in container.select("p"):
            # Remove the chapter number if it's there
            extra_content = verse.select(".chapternum")
            if extra_content:
                for element in extra_content:
                    element.decompose()

            if verse.select_one("sup.versenum"):
                verse_number = int(verse.select_one("sup.versenum").get_text(strip=True))
                verse.select_one("sup.versenum").decompose()
            else:
                verse_number = 1

            verse_text = verse.get_text(strip=True)
            verses.append(Verse(number=verse_number, text=verse_text))

        return Chapter(number=chapter_number, verses=verses)

    async def aget_verse(
        self, book_name: str, chapter_number: int, verse_number: int, client: BibleGatewayClient | None = None
    ) -> Verse:
        """
        Asynchronously return a single verse by book, chapter, and verse number.

        :param book_name: Name of the book.
        :param chapter_number: Chapter number.
        :param verse_number: Verse number.
        :param client: Optional shared `BibleGatewayClient` to reuse.
        :returns: Verse: The requested `Verse` object.
        :raises VerseNotFoundError: If the verse cannot be located on BibleGateway.
        """
        canonical_book = self._maybe_normalize_book_name(book_name)
        query = f"{canonical_book}+{chapter_number}:{verse_number}&version={self.abbreviation}"
        logger.debug(f"Query: {query}")

        if client is None:
            async with BibleGatewayClient() as new_client:
                soup = await new_client.fetch(query)
        else:
            soup = await client.fetch(query)

        verse_span = soup.select_one(f"span.{canonical_book}-{chapter_number}-{verse_number}")
        if not verse_span:
            raise VerseNotFoundError(f"Verse not found: {book_name} {chapter_number}:{verse_number}")

        # Remove any nested content like chapter/verse numbers
        extra_content = verse_span.select(".chapternum, .versenum")
        if extra_content:
            for element in extra_content:
                element.decompose()

        verse_text = verse_span.get_text(strip=True)
        return Verse(number=verse_number, text=verse_text)

    async def _aget_selection_range(
        self, start_book: str, start_chapter: int, start_verse: int, end_book: str, end_chapter: int, end_verse: int
    ) -> list[Book]:
        """
        Asynchronously retrieve a continuous list of verses between two reference points
        using a single shared HTTP session for efficiency.

        :param start_book: Name of the starting book.
        :param start_chapter: Starting chapter number.
        :param start_verse: Starting verse number.
        :param end_book: Name of the ending book.
        :param end_chapter: Ending chapter number.
        :param end_verse: Ending verse number.
        :returns: list[Book]: Ordered list of `Book` objects restricted to the range.
        :raises BookNotFoundError: If either provided book name is invalid.
        :raises ValueError: If the end reference is before the start reference in canonical order.
        """
        async with BibleGatewayClient() as client:
            # Normalize casing to canonical names
            start_book_c = self._normalize_book_name(start_book)
            end_book_c = self._normalize_book_name(end_book)

            if end_book_c != start_book_c and self.books.index(end_book_c) < self.books.index(start_book_c):
                raise ValueError(
                    f"End book must be the same as or after the start book: {start_book} -> {end_book}"
                )

            required_books_list = self.books[self.books.index(start_book_c) : self.books.index(end_book_c) + 1]
            logger.debug(f"Required books: {required_books_list}")

            sem = asyncio.Semaphore(self.max_concurrency) if self.max_concurrency else None

            async def run(book_name: str):
                if sem:
                    return await self._with_sem(sem, self.aget_book, book_name, client)
                return await self.aget_book(book_name, client)

            tasks = [asyncio.create_task(run(book)) for book in required_books_list]
            fetched_books = await asyncio.gather(*tasks)

            # Trim verses/chapters at the boundaries
            if start_book_c == end_book_c:
                book = fetched_books[0]
                trimmed_chapters: list[Chapter] = []
                for c in book.chapters[start_chapter - 1 : end_chapter]:
                    new_verses: list[Verse] = []
                    for v in c.verses:
                        if c.number == start_chapter and v.number < start_verse:
                            continue
                        if c.number == end_chapter and v.number > end_verse:
                            continue
                        new_verses.append(v)
                    trimmed_chapters.append(Chapter(number=c.number, verses=new_verses))
                fetched_books[0] = Book(name=book.name, chapters=trimmed_chapters)
            else:
                # Trim start book
                start_book_obj = fetched_books[0]
                start_book_obj.chapters = [
                    Chapter(number=c.number, verses=[v for v in c.verses if v.number >= start_verse])
                    for c in start_book_obj.chapters[start_chapter - 1 :]
                ]

                # Trim end book
                end_book_obj = fetched_books[-1]
                end_book_obj.chapters = [
                    Chapter(number=c.number, verses=[v for v in c.verses if v.number <= end_verse])
                    for c in end_book_obj.chapters[: end_chapter]
                ]

            return fetched_books
