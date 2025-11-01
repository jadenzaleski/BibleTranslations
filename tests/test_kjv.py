import logging

import pytest

from bible_translations.exceptions import VerseNotFoundError, ChapterNotFoundError, BookNotFoundError
from bible_translations.translations.kjv import KJV


@pytest.mark.asyncio
async def test_aget_verse_john_3_16():
    kjv = KJV()
    verse = await kjv.aget_verse(book_name="John", chapter_number=3, verse_number=16)
    # https://www.biblegateway.com/passage/?search=John%203%3A16&version=KJV
    assert (
        "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not"
        " perish, but have everlasting life." == verse.text
    )
    assert verse.number == 16


@pytest.mark.asyncio
async def test_aget_verse_invalid_book():
    kjv = KJV()
    with pytest.raises(VerseNotFoundError):
        await kjv.aget_verse(book_name="FakeBook", chapter_number=1, verse_number=1)


@pytest.mark.asyncio
async def test_aget_verse_invalid_chapter():
    kjv = KJV()
    with pytest.raises(VerseNotFoundError):
        await kjv.aget_verse(book_name="John", chapter_number=50, verse_number=1)


@pytest.mark.asyncio
async def test_aget_verse_invalid_verse():
    kjv = KJV()
    with pytest.raises(VerseNotFoundError):
        await kjv.aget_verse(book_name="John", chapter_number=3, verse_number=999)


@pytest.mark.asyncio
async def test_aget_chapter_john_1():
    kjv = KJV()
    chapter = await kjv.aget_chapter(book_name="John", chapter_number=1)
    assert len(chapter.verses) == 51 # There are 51 verses
    assert chapter.verses[0].number == 1 # Verse 1 hase number 1
    assert chapter.verses[-1].number == 51  # Verse 51 have number 51
    assert chapter.verses[23].text == "And they which were sent were of the Pharisees."


@pytest.mark.asyncio
async def test_aget_chapter_invalid_chapter():
    kjv = KJV()
    with pytest.raises(ChapterNotFoundError):
        await kjv.aget_chapter(book_name="John", chapter_number=85)


@pytest.mark.asyncio
async def test_aget_chapter_invalid_book():
    kjv = KJV()
    with pytest.raises(ChapterNotFoundError):
        await kjv.aget_chapter(book_name="Johnny", chapter_number=85)

@pytest.mark.asyncio
async def test_aget_book_john():
    kjv = KJV()
    book = await kjv.aget_book(name="John")
    assert book.chapters[0].verses[0].number == 1 # Make sure we have the first verse
    assert len(book.chapters) == 21 # Make sure there are 21 chapters
    assert book.chapters[-1].number == 21


@pytest.mark.asyncio
async def test_aget_book_invalid_book():
    kjv = KJV()
    with pytest.raises(BookNotFoundError):
        await kjv.aget_book(name="Johnny")


@pytest.mark.asyncio
async def test_aget_books():
    logging.basicConfig(level=logging.DEBUG, force=True)
    kjv = KJV()
    books = await kjv.aget_books()
    assert len(books) == 66
    # Make sure the books are in order
    expected_order = list(kjv.books)
    returned_order = [b.name for b in books]
    assert returned_order == expected_order
    # Each book has chapters
    for b in books:
        assert len(b.chapters) >= 1

