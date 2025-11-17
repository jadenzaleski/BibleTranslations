from dataclasses import dataclass


@dataclass
class Info:
    translation: str
    abbreviation: str
    language: str
    copyright: str | None = None
    url: str | None = None
    fetch_date: str | None = None
