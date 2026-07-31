from dataclasses import dataclass, field
from src.models.section import Section
from src.models.reference import Reference
from src.models.citation import Citation
from src.models.metadata import Metadata
@dataclass
class Paper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    full_text: str = ""
    sections: list[Section] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    citations:list[Citation]=field(default_factory=list)
    metadata:Metadata=field(default_factory=Metadata)
    