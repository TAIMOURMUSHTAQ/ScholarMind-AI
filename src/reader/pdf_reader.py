"""
PDF Reader
Reads PDF files and converts them into Document objects
"""
import fitz #PymuPdf
import os
from src.models.document import Document
from src.models.page import Page
#Exceptions and loggers defined
from src.utils.logger import logger
from src.utils.exceptions import (
    InvalidPDFError,
    FileNotFoundErrorSM,
)
class PDFReader:
    """Reads a PDF file and retrurns document object
    """
    def __init__(self,pdf_path:str):
        self.pdf_path=pdf_path
    def read(self)-> Document:
        """Read a PDF File
        Returns:Document
        """
        doc = None
        try:
            if not os.path.exists(self.pdf_path):
                raise FileNotFoundErrorSM(
                    f"File not found: {self.pdf_path}"
                )
            logger.info("Opening PDF...")
            doc = fitz.open(self.pdf_path)
            pages = []
            full_text = ""

            for page_number, page in enumerate(doc, start=1):
                text = page.get_text()
                page_obj = Page(
                    page_number=page_number,
                    text=text,
                    word_count=len(text.split()),
                    character_count=len(text)
                )
                pages.append(page_obj)
                full_text += text + "\n"

            document = Document(
                file_name=os.path.basename(self.pdf_path),
                file_path=self.pdf_path,
                page_count=doc.page_count,
                metadata=doc.metadata,
                pages=pages,
                full_text=full_text
            )
            return document
        except Exception as e:
            raise InvalidPDFError(str(e))
        finally:
            if doc is not None:
                doc.close()