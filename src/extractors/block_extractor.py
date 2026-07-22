import pymupdf
class BlockExtractor:
    """Extract text blocks from a PDF Page"""
    @staticmethod
    def extract(page):
        return page.get_text("blocks")