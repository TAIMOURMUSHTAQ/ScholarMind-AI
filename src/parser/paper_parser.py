import pymupdf
from src.models.paper import Paper
from src.extractors.title_extractor import TitleExtractor
from src.extractors.author_extractor import AuthorExtractor
class PaperParser:
    def parse(self, pdf_path):
        # Open PDF
        doc = pymupdf.open(pdf_path)
        # First page
        first_page = doc[0]
        # Create Paper object
        paper = Paper()
        # Extract title
        paper.title = TitleExtractor.extract(first_page)
        paper.authors=AuthorExtractor.extract(
            first_page,
            paper.title
        )
        # Close document
        doc.close()
        return paper