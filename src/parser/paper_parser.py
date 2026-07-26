import pymupdf
from src.models.paper import Paper
from src.layout.layout_analyzer import LayoutAnalyzer
from src.extractors.title_extractor import TitleExtractor
from src.extractors.author_extractor import AuthorExtractor
from src.extractors.abstract_extractor import AbstractExtractor
from src.extractors.section_extractor import SectionExtractor
class PaperParser:
    def parse(self, pdf_path):
        doc = pymupdf.open(pdf_path)
        first_page = doc[0]
        layout_blocks = LayoutAnalyzer.extract(first_page)
        #
        # print("\n===== LAYOUT BLOCKS =====")
        # for i, block in enumerate(layout_blocks):
        #     print(f"\nBLOCK {i}")
        #     print("-" * 40)
        #     print(block.text)
        #     print("Font:", block.font_size)
        #     print("Y:", block.y0)
        # #
        paper = Paper()
        paper.title = TitleExtractor.extract(layout_blocks)
        paper.authors = AuthorExtractor.extract(
            layout_blocks,
            paper.title
        )
        paper.abstract = AbstractExtractor.extract(
            layout_blocks
        )
        paper.sections=SectionExtractor.extract(
            layout_blocks
        )
        doc.close()
        return paper