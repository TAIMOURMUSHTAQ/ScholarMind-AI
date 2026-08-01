# import pymupdf
# from src.models.paper import Paper
# from src.layout.layout_analyzer import LayoutAnalyzer
# from src.extractors.title_extractor import TitleExtractor
# from src.extractors.author_extractor import AuthorExtractor
# from src.extractors.abstract_extractor import AbstractExtractor
# from src.extractors.section_extractor import SectionExtractor
# from src.extractors.reference_extractor import ReferenceExtractor
# from src.layout.reading_order import ReadingOrderAnalyzer
# from src.extractors.citation_extractor import CitationExtractor
# from src.extractors.metadata_extractor import MetadataExtractor
# class PaperParser:
#     def parse(self, pdf_path):
#         doc = pymupdf.open(pdf_path)
#         first_page = doc[0]
#         layout_blocks = LayoutAnalyzer.extract(first_page)
#         #
#         # print("\n===== LAYOUT BLOCKS =====")
#         # for i, block in enumerate(layout_blocks):
#         #     print(f"\nBLOCK {i}")
#         #     print("-" * 40)
#         #     print(block.text)
#         #     print("Font:", block.font_size)
#         #     print("Y:", block.y0)
#         # #
#         #Arrange blocks into the correct reading order
#         layout_blocks=ReadingOrderAnalyzer.sort(layout_blocks)
#         paper = Paper()
#         paper.title = TitleExtractor.extract(layout_blocks)
#         paper.authors = AuthorExtractor.extract(
#             layout_blocks,
#             paper.title
#         )
#         paper.abstract = AbstractExtractor.extract(
#             layout_blocks
#         )
#         paper.sections=SectionExtractor.extract(
#             layout_blocks
#         )
#         paper.citations=CitationExtractor.extract(
#             paper.sections
#         )
#         paper.references = ReferenceExtractor.extract(
#             layout_blocks
#         )
#         paper.metadata=MetadataExtractor.extract(
#             doc,
#             paper
#         )
#         doc.close()
#         return paper








from pathlib import Path
import pymupdf
from src.models.paper import Paper
from src.layout.layout_analyzer import LayoutAnalyzer
from src.layout.reading_order import ReadingOrderAnalyzer
from src.extractors.title_extractor import TitleExtractor
from src.extractors.author_extractor import AuthorExtractor
from src.extractors.abstract_extractor import AbstractExtractor
from src.extractors.section_extractor import SectionExtractor
from src.extractors.citation_extractor import CitationExtractor
from src.extractors.reference_extractor import ReferenceExtractor
from src.extractors.metadata_extractor import MetadataExtractor
from src.analyzers.document_statistics import DocumentStatistics
from src.chunking.chunk_generator import ChunkGenerator

class PaperParser:
    """
    Main parser responsible for converting a PDF
    into a structured Paper object.
    """
    def parse(self, pdf_path):
        """
        Parse a PDF file and return a populated Paper object.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )
        doc = pymupdf.open(pdf_path)
        try:
            # Store blocks from every page
            layout_blocks = []

            # Iterate through every page
            for page in doc:

                page_blocks = LayoutAnalyzer.extract(page)

                page_blocks = ReadingOrderAnalyzer.sort(
                    page_blocks
                )

                layout_blocks.extend(
                    page_blocks
                )
            # -----------------------------------
            # Create Paper Object
            # -----------------------------------
            paper = Paper()
            # -----------------------------------
            # Basic Information
            # -----------------------------------
            paper.title = TitleExtractor.extract(
                layout_blocks
            )
            paper.authors = AuthorExtractor.extract(
                layout_blocks,
                paper.title
            )
            paper.abstract = AbstractExtractor.extract(
                layout_blocks
            )
            # -----------------------------------
            # Content Extraction
            # -----------------------------------
            paper.sections = SectionExtractor.extract(
                layout_blocks
            )
            paper.citations = CitationExtractor.extract(
                paper.sections
            )
            paper.references = ReferenceExtractor.extract(
                layout_blocks
            )
            # -----------------------------------
            # Metadata
            # -----------------------------------
            paper.metadata = MetadataExtractor.extract(
                doc,
                paper
            )
            paper.statistics = DocumentStatistics.analyze(
                paper
            )
            paper.chunks=ChunkGenerator.generate(
                paper.sections
            )
            print("\n===== CHUNKS =====")

            for chunk in paper.chunks:

                    print("-" * 40)

                    print("Chunk ID :", chunk.id)

                    print("Title    :", chunk.title)

                    print("Words    :", chunk.word_count)

                    print("Preview  :", chunk.text[:100])

                    print()
            return paper
    
        finally:
            doc.close()