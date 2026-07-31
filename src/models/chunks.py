from dataclasses import dataclass


@dataclass
class Chunk:
    """
    One semantic chunk from a research paper.
    """

    id: int

    title: str

    text: str

    page_start: int

    page_end: int

    word_count: int