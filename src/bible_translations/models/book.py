from dataclasses import dataclass

from bible_translations.models.chapter import Chapter


@dataclass
class Book:
    name: str
    chapters: list[Chapter]
