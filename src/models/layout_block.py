from dataclasses import dataclass
@dataclass
class LayoutBlock:
    """
    Represents one text block extracted from a PDF page.
    """
    text: str
    font_size: float
    x0: float
    y0: float
    x1: float
    y1: float
    block_number: int
    # NEW
    page_number: int = 0