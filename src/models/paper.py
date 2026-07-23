from dataclasses import dataclass,field 

@dataclass
class Paper:
    title:str=""
    authors:list[str]=field(default_factory=list)
    abstract:str=""
    keywords:list[str]=field(default_factory=list)
    sections:dict[str,str]=field(default_factory=dict)
    references:list[str]=field(default_factory=list)
    metadata:dict=field(default_factory=dict)