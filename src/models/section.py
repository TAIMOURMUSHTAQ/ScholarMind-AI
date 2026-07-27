from dataclasses import dataclass
@dataclass
class Section:
    """
    Represents one logical section of a research paper.
    """
    title:str
    content:str