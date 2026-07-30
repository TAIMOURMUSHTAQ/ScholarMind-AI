from src.models.layout_block import LayoutBlock


class LayoutAnalyzer:
    @staticmethod
    def extract(page):
        data = page.get_text("dict")

        layout_blocks = []

        for block_no, block in enumerate(data.get("blocks", [])):

            # Skip non-text blocks
            if block.get("type") != 0:
                continue

            text_parts = []
            max_font = 0

            for line in block.get("lines", []):

                for span in line.get("spans", []):

                    text_parts.append(span["text"])
                    max_font = max(max_font, span["size"])

            text = " ".join(text_parts).strip()

            if not text:
                continue

            x0, y0, x1, y1 = block["bbox"]

            layout_blocks.append(
                LayoutBlock(
                    text=text,
                    font_size=max_font,
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    block_number=block_no,
                )
            )

        layout_blocks.sort(key=lambda block: (block.y0, block.x0))

        return layout_blocks