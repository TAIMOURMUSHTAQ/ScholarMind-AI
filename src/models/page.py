"""
Page Model
Represents a single page inside a PDF Document
"""
from dataclasses import dataclass,field
from typing import Any

@dataclass
class Page:
    """
    Stores information about one PDF's Page
    This class only stores data
    """
    page_number:int
    text:str
    word_count:int
    character_count:int
    metadata:dict[str,Any]=field(default_factory=dict)
    images_count=0
    tables_count=0