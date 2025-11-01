from dataclasses import dataclass

from bible_translations.models.verse import Verse


@dataclass
class Chapter:
    number: int
    verses: list[Verse]
