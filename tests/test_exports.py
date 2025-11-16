import logging

import pytest

from bible_translations.translations.kjv import KJV
from bible_translations.utils.exporter import Exporter

@pytest.mark.asyncio
async def test_export_amos():
    logging.basicConfig(level=logging.DEBUG, force=True)
    kjv = KJV()
    books = [await kjv.aget_book("amos")]
    exporter = Exporter()
    exporter.export(books)