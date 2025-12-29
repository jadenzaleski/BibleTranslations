import logging
import zipfile

import pytest

from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.translations.kjv import KJV
from bible_translations.utils.exporter import Exporter


@pytest.mark.asyncio
async def test_export_single_verse(tmp_path):
    kjv = KJV()
    verse = await kjv.aget_verse("John", 3, 16)
    chapter = Chapter(3, [verse])
    book = Book("John", [chapter], kjv.getInfo())
    exporter = Exporter(output_dir=tmp_path)

    zip_path = exporter.export([book])

    assert zip_path.exists()
    assert zip_path.suffix == ".zip"

    with zipfile.ZipFile(zip_path) as z:
        logging.basicConfig(level=logging.DEBUG, force=True)
        names = z.namelist()
        print(names)

        assert "books/john.json" in names
        assert "kjv_info.json" in names
        assert "kjv.json" in names
