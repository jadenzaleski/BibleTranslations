from dataclasses import dataclass
from typing import TYPE_CHECKING

from bible_translations.models.chapter import Chapter

if TYPE_CHECKING:
    from bible_translations.translations.base import Translation


@dataclass
class Book:
    name: str
    chapters: list[Chapter]
    translation: "Translation"
