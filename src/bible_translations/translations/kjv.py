import asyncio

from bible_translations.exceptions import BookNotFoundError, ChapterNotFoundError, VerseNotFoundError
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.verse import Verse
from bible_translations.translations.base import Translation
from bible_translations.utils.fetch.bible_gateway import BibleGatewayClient
from bible_translations.utils.logger import logger


class KJV(Translation):
    name = "King James Version"
    abbreviation = "KJV"
    copyright = "Public Domain"

    async def aget_books(self) -> list[Book]:
        async with BibleGatewayClient() as client:
            tasks = [asyncio.create_task(self.aget_book(name, client)) for name in self.books]
            for i, (name, task) in enumerate(zip(self.books, tasks), 1):
                task.add_done_callback(
                    lambda x, book=name, idx=i: logger.debug(f"[{idx}] Completed fetching book: {book}")
                )

            results = await asyncio.gather(*tasks)
            results_by_book = dict(zip(self.books, results))
            sorted_results = [results_by_book[name] for name in self.books]

            return sorted_results

    async def aget_book(self, name: str, client: BibleGatewayClient | None = None) -> Book:
        if name.lower() not in {k.lower(): k for k in self.books}:
            raise BookNotFoundError(f"Book not found: {name}")
        # Use the actual chapter count for the book
        chapter_count = self.book_chapter_counts[name]

        # Handle soup based on whether a client is passed or not
        if client is None:
            async with BibleGatewayClient() as new_client:
                # Grab them all at the same time
                tasks = [
                    asyncio.create_task(self.aget_chapter(name, i, new_client)) for i in range(1, chapter_count + 1)
                ]
        else:
            # Grab them all at the same time
            tasks = [asyncio.create_task(self.aget_chapter(name, i, client)) for i in range(1, chapter_count + 1)]

        # Turn this on if you want more logs:
        # for i, task in enumerate(tasks, 1):
        #     task.add_done_callback(lambda x, chapter=i: logger.debug(f"Chapter {chapter} complete"))
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x.number)
        return Book(name=name, chapters=results)

    async def aget_chapter(
        self, book_name: str, chapter_number: int, client: BibleGatewayClient | None = None
    ) -> Chapter:
        query = f"{book_name}+{chapter_number}&version={self.abbreviation}"
        logger.debug(f"Query: {query}")

        # Handle soup based on whether a client is passed or not
        if client is None:
            async with BibleGatewayClient() as new_client:
                soup = await new_client.fetch(query)
        else:
            soup = await client.fetch(query)

        container = soup.select_one("div.version-KJV.result-text-style-normal.text-html")
        if not container:
            raise ChapterNotFoundError(f"Chapter not found: {book_name} {chapter_number}")

        verses = []
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
        # Build the query part of the URL
        query = f"{book_name}+{chapter_number}:{verse_number}&version={self.abbreviation}"
        logger.debug(f"Query: {query}")

        # Handle soup based on whether a client is passed or not
        if client is None:
            async with BibleGatewayClient() as new_client:
                soup = await new_client.fetch(query)
        else:
            soup = await client.fetch(query)

        # Grab the verse by this nifty class that BibleGateway provides
        verse_span = soup.select_one(f"span.{book_name}-{chapter_number}-{verse_number}")
        if not verse_span:
            raise VerseNotFoundError(f"Verse not found: {book_name} {chapter_number}:{verse_number}")

        # Remove any nested content
        extra_content = verse_span.select(".chapternum, .versenum")
        if extra_content:
            for element in extra_content:
                element.decompose()

        # Combine text if multiple elements
        verse_text = verse_span.get_text(strip=True)

        return Verse(number=verse_number, text=verse_text)

    async def _aget_selection_range(
        self, start_book: str, start_chapter: int, start_verse: int, end_book: str, end_chapter: int, end_verse: int
    ) -> list[Book]:
        async with BibleGatewayClient() as client:
            # Ensure start book
            if start_book not in self.books:
                raise BookNotFoundError(f"Book not found: {start_book}")
            # Ensure end book
            if end_book not in self.books:
                raise BookNotFoundError(f"Book not found: {end_book}")
            # Ensure the end book is the same as or after the start book
            if end_book != start_book and self.books.index(end_book) < self.books.index(start_book):
                raise ValueError(f"End book must be the same as or after the start book: {start_book} -> {end_book}")

            # Get a list of books between the start and end book, inclusive
            required_books_list = self.books[self.books.index(start_book) : self.books.index(end_book) + 1]
            logger.debug(f"Required books: {required_books_list}")

            tasks = [asyncio.create_task(self.aget_book(book, client)) for book in required_books_list]
            fetched_books = await asyncio.gather(*tasks)

            # Now remove the unnecessary verses and chapters in the start and end books.
            # Trim the start book
            if start_book == end_book:
                book = fetched_books[0]
                trimmed_chapters = []
                for c in book.chapters[start_chapter - 1 : end_chapter]:
                    new_verses = []

                    for v in c.verses:
                        if c.number == start_chapter and v.number < start_verse:
                            continue
                        if c.number == end_chapter and v.number > end_verse:
                            continue
                        new_verses.append(v)

                    trimmed_chapters.append(Chapter(number=c.number, verses=new_verses))
                fetched_books[0] = Book(name=book.name, chapters=trimmed_chapters)
            else:
                # Multiple books
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
                    for c in end_book_obj.chapters[:end_chapter]
                ]

            return fetched_books
