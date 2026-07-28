from dataclasses import dataclass

@dataclass
class Citation:
    """
    Represents an in-text citation
    """
    reference_number:int
    section_title:str
    sentence:str