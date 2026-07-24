from dataclasses import dataclass

@dataclass
class LayoutBlock:
    text:str
    font_size:float
    x0:float
    y0:float
    x1:float
    y1:float
    block_number:int