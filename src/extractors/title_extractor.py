from src.models.layout_block import LayoutBlock
class TitleExtractor:
    @staticmethod
    def extract(layout_blocks: list[LayoutBlock]) -> str:
        if not layout_blocks:
            return ""
        title_block = max(
            layout_blocks,
            key=lambda block: block.font_size
        )
        return title_block.text.strip()