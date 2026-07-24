from src.models.layout_block import LayoutBlock

class LayoutAnalyzer:

    @staticmethod
    def extract(page):
        data=page.get_text("dict")
        layout_blocks=[]
        for block_no, block in enumerate(data["blocks"]):
            if block["type"]!=0:
                continue
            text=""
            max_font=0
            for line in block["lines"]:
                for span in line["spans"]:
                    text+=span["text"]+" "
                    max_font=max(max_font,span["size"])
                text=text.strip()
                if not text:
                    continue
                x0,y0,x1,y1=block["bbox"]
                layout_blocks.append(
                    LayoutBlock(
                        text=text,
                        font_size=max_font,
                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,
                        block_number=block_no
                    )
                )
            return layout_blocks