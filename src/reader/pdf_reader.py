"""
PDF Reader
Reads PDF files and converts them into Document objects
"""
import fitz #PymuPdf
from src.models.document import Document
from src.models.page import Page

class PDFReader:
    """Reads a PDF file and retrurns document object
    """
    def __init__(self,pdf_path:str):
        self.pdf_path=pdf_path
    def read(self)-> Document:
        """Read a PDF File
        Returns:Document
        """
        raise NotImplementedError("Will be implemented in the next lesson")