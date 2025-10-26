from abc import ABC, abstractmethod

from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.verse import Verse


class Translation(ABC):
    """
    Abstract base class defining the standard interface for all Bible translations.

    Every concrete translation implementation (e.g., KJV, ESV)
    must inherit from this class and implement the abstract retrieval methods.
    """

    name: str
    abbreviation: str
    copyright: str
    language: str = "English"
    books: list[str] = [
        "Genesis",
        "Exodus",
        "Leviticus",
        "Numbers",
        "Deuteronomy",
        "Joshua",
        "Judges",
        "Ruth",
        "1 Samuel",
        "2 Samuel",
        "1 Kings",
        "2 Kings",
        "1 Chronicles",
        "2 Chronicles",
        "Ezra",
        "Nehemiah",
        "Esther",
        "Job",
        "Psalms",
        "Proverbs",
        "Ecclesiastes",
        "Song of Solomon",
        "Isaiah",
        "Jeremiah",
        "Lamentations",
        "Ezekiel",
        "Daniel",
        "Hosea",
        "Joel",
        "Amos",
        "Obadiah",
        "Jonah",
        "Micah",
        "Nahum",
        "Habakkuk",
        "Zephaniah",
        "Haggai",
        "Zechariah",
        "Malachi",
        # New Testament
        "Matthew",
        "Mark",
        "Luke",
        "John",
        "Acts",
        "Romans",
        "1 Corinthians",
        "2 Corinthians",
        "Galatians",
        "Ephesians",
        "Philippians",
        "Colossians",
        "1 Thessalonians",
        "2 Thessalonians",
        "1 Timothy",
        "2 Timothy",
        "Titus",
        "Philemon",
        "Hebrews",
        "James",
        "1 Peter",
        "2 Peter",
        "1 John",
        "2 John",
        "3 John",
        "Jude",
        "Revelation",
    ]

    # ---------- Retrieval methods ----------

    @abstractmethod
    def get_books(self) -> list[Book]:
        """
        Return all books available in this translation.

        Returns:
            list[Book]: A list of all `Book` objects for the translation.
        """
        raise NotImplementedError

    @abstractmethod
    def get_book(self, name: str) -> Book:
        """
        Return a single book by name.

        Args:
            name (str): The book name (e.g., "Genesis", "John").

        Returns:
            Book: The corresponding `Book` object containing all chapters and verses.
        """
        raise NotImplementedError

    @abstractmethod
    def get_chapter(self, book_name: str, chapter_number: int) -> Chapter:
        """
        Return a single chapter by book name and chapter number.

        Args:
            book_name (str): Name of the book (e.g., "John").
            chapter_number (int): Chapter number to retrieve.

        Returns:
            Chapter: The `Chapter` object, including its verses.
        """
        raise NotImplementedError

    @abstractmethod
    def get_verse(self, book_name: str, chapter_number: int, verse_number: int) -> Verse:
        """
        Return a single verse by book, chapter, and verse number.

        Args:
            book_name (str): Name of the book.
            chapter_number (int): Chapter number.
            verse_number (int): Verse number.

        Returns:
            Verse: The requested `Verse` object, linked to its chapter, book, and translation.
        """
        raise NotImplementedError

    # ---------- Selection retrieval ----------

    def get_selection(
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
        Return a continuous selection of verses between two points.

        Can be called with string references:
            get_selection("John 3:16", "John 5:1")

        or with explicit numeric arguments:
            get_selection(
                start_book="John", start_chapter=3, start_verse=16,
                end_book="John", end_chapter=5, end_verse=1
            )

        Args:
            start_ref (str | None): Optional string reference for the start (e.g., "John 3:16").
            end_ref (str | None): Optional string reference for the end (e.g., "John 5:1").
            start_book (str | None): Start book name if using numeric mode.
            start_chapter (int | None): Start chapter number.
            start_verse (int | None): Start verse number.
            end_book (str | None): End book name if using numeric mode.
            end_chapter (int | None): End chapter number.
            end_verse (int | None): End verse number.

        Returns:
            list[Verse]: A list of `Verse` objects covering the inclusive range.
        """
        if start_ref and end_ref:
            start_book, start_chapter, start_verse = self._parse_ref(start_ref)
            end_book, end_chapter, end_verse = self._parse_ref(end_ref)

        return self._get_selection_range(start_book, start_chapter, start_verse, end_book, end_chapter, end_verse)

    @abstractmethod
    def _get_selection_range(
        self,
        start_book: str,
        start_chapter: int,
        start_verse: int,
        end_book: str,
        end_chapter: int,
        end_verse: int,
    ) -> list[Verse]:
        """
        Retrieve a continuous list of verses between two reference points.

        This method must be implemented by subclasses to define
        how verses are loaded or generated internally.

        Args:
            start_book (str): Name of the starting book.
            start_chapter (int): Starting chapter number.
            start_verse (int): Starting verse number.
            end_book (str): Name of the ending book.
            end_chapter (int): Ending chapter number.
            end_verse (int): Ending verse number.

        Returns:
            list[Verse]: Ordered list of all `Verse` objects in the range.
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
