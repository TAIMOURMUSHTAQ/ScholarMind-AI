from dataclasses import dataclass


@dataclass
class Reference:

    number: int = 0

    raw_text: str = ""

    authors: str = ""

    title: str = ""

    venue: str = ""

    year: str = ""

    doi: str = ""