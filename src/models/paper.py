from dataclasses import dataclass, field
from src.models.section import Section
from src.models.reference import Reference

@dataclass
class Paper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)