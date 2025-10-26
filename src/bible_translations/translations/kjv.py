from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.verse import Verse
from bible_translations.translations.base import Translation


class KJV(Translation):
    name = "King James Version"
    abbreviation = "KJV"
    copyright = "Public Domain"

    def get_books(self) -> list[Book]:
        """
        Return all books available in the KJV translation.
        """
        pass

    def get_book(self, name: str) -> Book:
        """
        Return a single book by name.

        :param name: The name of the book you want to fetch.
        :return: A `Book` object.
        """
        pass

    def get_chapter(self, book_name: str, chapter_number: int) -> Chapter:
        """
        Fetches the specified chapter from a book.

        :param book_name: The name of the book from which the chapter needs to be fetched.
        :param chapter_number: The number of the chapter to retrieve from the book.
        :return: Returns the requested chapter as a `Chapter` object.
        """
        pass

    def get_verse(self, book_name: str, chapter_number: int, verse_number: int) -> Verse:
        """
        Fetches a specific Bible verse from the provided book, chapter, and verse number.

        :param book_name: The name of the book in the Bible.
        :param chapter_number: The number of the chapter inside the specified book.
        :param verse_number: The specific number of the verse within the chapter.
        :return: The Verse object corresponding to the specified book, chapter, and
            verse number.
        """
        pass

    def _get_selection_range(self, start_book: str, start_chapter: int, start_verse: int, end_book: str,
                             end_chapter: int, end_verse: int) -> list[Verse]:
        """
        Calculate and return the range of verses based on the given start and end positions.
        The provided positions include the book name, chapter number, and verse number
        to determine the specific selection range.

        :param start_book: The name of the starting book.
        :param start_chapter: The chapter number in the starting book.
        :param start_verse: The verse number in the starting chapter.
        :param end_book: The name of the ending book.
        :param end_chapter: The chapter number in the ending book.
        :param end_verse: The verse number in the ending chapter.
        :return: A list of `Verse` objects corresponding to the specified range of verses.
        """
        pass
