from dataclasses import dataclass

from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info


@dataclass
class Book:
    name: str
    chapters: list[Chapter]
    info: Info | None = None

