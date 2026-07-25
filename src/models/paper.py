from dataclasses import dataclass, field

@dataclass
class Paper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    sections: list = field(default_factory=list)
    references: list = field(default_factory=list)