from dataclasses import dataclass


@dataclass
class Verse:
    number: int
    text: str
    heading: str | None = None
    superscription: str | None = None
    footnotes: list[str] | None = None
