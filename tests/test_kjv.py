import logging

import pytest

from bible_translations.exceptions import BookNotFoundError, ChapterNotFoundError, VerseNotFoundError
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
async def test_aget_verse_amos_9_8():
    logging.basicConfig(level=logging.DEBUG, force=True)
    kjv = KJV()
    verse = await kjv.aget_verse(book_name="Amos", chapter_number=9, verse_number=8)
    # https://www.biblegateway.com/passage/?search=Amos%209%3A8&version=KJV
    # Testing this to make sure we handle the small-caps calss properly.
    assert (
        "Behold, the eyes of the Lord God are upon the sinful kingdom, and I will destroy it from off the face of the"
        " earth; saving that I will not utterly destroy the house of Jacob, saith the Lord." == verse.text
    )
    assert verse.number == 8


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
    assert len(chapter.verses) == 51  # There are 51 verses
    assert chapter.verses[0].number == 1  # Verse 1 hase number 1
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
    assert book.chapters[0].verses[0].number == 1  # Make sure we have the first verse
    assert len(book.chapters) == 21  # Make sure there are 21 chapters
    assert book.chapters[-1].number == 21


@pytest.mark.asyncio
async def test_aget_book_invalid_book():
    kjv = KJV()
    with pytest.raises(BookNotFoundError):
        await kjv.aget_book(name="Johnny")


@pytest.mark.asyncio
async def test_aget_books():
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


@pytest.mark.asyncio
async def test_aget_selection_matthew():
    kjv = KJV()
    selection = await kjv.aget_selection(
        start_book="Matthew", start_chapter=1, start_verse=1, end_book="Matthew", end_chapter=1, end_verse=7
    )
    assert len(selection) == 1
    assert len(selection[0].chapters) == 1
    assert len(selection[0].chapters[0].verses) == 7
    assert selection[0].chapters[0].verses[0].number == 1
    assert selection[0].chapters[0].verses[-1].number == 7
    assert selection[0].chapters[0].verses[0].text == (
        "The book of the generation of Jesus Christ, the son of David, the son of Abraham."
    )


@pytest.mark.asyncio
async def test_aget_selection_mode_ref():
    kjv = KJV()
    selection = await kjv.aget_selection(start_ref="John 1:2", end_ref="John 3:4")
    assert len(selection) == 1
    assert len(selection[0].chapters) == 3
    assert len(selection[0].chapters[0].verses) == 50  # 51 - 1
    assert len(selection[0].chapters[1].verses) == 25
    assert len(selection[0].chapters[2].verses) == 4
    assert selection[0].chapters[2].verses[3].text == (
        "Nicodemus saith unto him, How can a man be born when he is old?"
        " can he enter the second time into his mother's womb,"
        " and be born?"
    )


@pytest.mark.asyncio
async def test_aget_selection_mode_ref_multi_book():
    kjv = KJV()
    selection = await kjv.aget_selection(start_ref="John 1:2", end_ref="Romans 3:4")
    assert len(selection) == 3
    assert len(selection[0].chapters) == 21
    assert len(selection[0].chapters[0].verses) == 50  # 51 - 1
    assert len(selection[1].chapters) == 28
    assert len(selection[2].chapters) == 3
    assert len(selection[2].chapters[2].verses) == 4
    assert selection[2].chapters[2].verses[3].text == (
        "God forbid: yea, let God be true, but every man a liar; as it"
        " is written, That thou mightest be justified in thy sayings,"
        " and mightest overcome when thou art judged."
    )


@pytest.mark.asyncio
async def test_aget_selection_invalid_mode_ref():
    kjv = KJV()
    with pytest.raises(ValueError):
        await kjv.aget_selection(start_ref="John 1:2", end_ref="Genesis 3:4")

    with pytest.raises(ValueError):
        await kjv.aget_selection(start_ref="John 1-2", end_ref="Genesis -3:4")


@pytest.mark.asyncio
async def test_aget_selection_invalid():
    kjv = KJV()
    with pytest.raises(ValueError):
        await kjv.aget_selection(
            start_book="Matthew", start_chapter=1, start_verse=1, end_book="Genesis", end_chapter=1, end_verse=7
        )
