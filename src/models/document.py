# """
# Document Model

# This module defines the Document class used throughout ScholarMind AI.

# Author: Taimour Mushtaq
# Project: ScholarMind AI
# """

# from dataclasses import dataclass, field
# from typing import Any


# @dataclass
# class Document:
#     """
#     Represents a PDF document after it has been read.

#     This class only stores information.
#     It does NOT read PDFs, clean text, or perform AI tasks.
#     """

#     # ---------- File Information ----------
#     file_name: str
#     file_path: str

#     # ---------- Document Statistics ----------
#     page_count: int

#     # ---------- Metadata ----------
#     metadata: dict[str, Any] = field(default_factory=dict)

#     # ---------- Content ----------
#     pages: list = field(default_factory=list)
#     full_text: str = ""




"""
Document Model

Represents a processed PDF document inside ScholarMind AI.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """
    Stores information extracted from a PDF file.
    """

    file_name: str
    file_path: str
    page_count: int

    metadata: dict[str, Any] = field(default_factory=dict)

    pages: list = field(default_factory=list)

    full_text: str = ""
#Example
# doc = Document(
#     file_name="Pdf_Tables.pdf",
#     file_path="data/sample_pdfs",
#     page_count=5
# )
# doc = Document(
#     file_name="sample_conference_paper.pdf",
#     file_path="data/sample_pdfs/sample_conference_paper.pdf",
#     page_count=5
# )
# print(doc)

# #Real Pipeline
# import PDFReader
# reader = PDFReader("sample_conference_paper.pdf")
# document = reader.read()



