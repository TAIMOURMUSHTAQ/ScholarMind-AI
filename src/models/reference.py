from dataclasses import dataclass
@dataclass
class Reference:
    """
    Represents one bibliography reference
    """
    number:int
    raw_text:str

    authors:list[str] | None=None
    title:str=""
    year:str="" 
    venue:str=""
    doi:str=""