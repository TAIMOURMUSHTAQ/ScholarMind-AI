from dataclasses import dataclass, field
from src.models.section import Section

@dataclass
class Paper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    references: list[str] = field(default_factory=list)