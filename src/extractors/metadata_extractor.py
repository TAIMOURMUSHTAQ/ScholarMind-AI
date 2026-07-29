import re
from src.models.metadata import Metadata


class MetadataExtractor:

    @staticmethod
    def extract(doc, paper):

        metadata = Metadata()

        metadata.title = paper.title
        metadata.authors = paper.authors

        # Build full text from all pages
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        # ---------------- DOI ----------------

        doi_pattern = r"10\.\d{4,9}/[-._;()/:A-Z0-9]+"

        match = re.search(
            doi_pattern,
            full_text,
            flags=re.IGNORECASE
        )

        if match:
            metadata.doi = match.group()

        # ---------------- YEAR ----------------

        years = re.findall(
            r"\b(?:19|20)\d{2}\b",
            full_text
        )

        if years:
            metadata.year = years[0]

        return metadata