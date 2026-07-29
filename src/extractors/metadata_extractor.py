import re
from src.models.metadata import Metadata
class MetadataExtractor:
    @staticmethod
    def extract(document,paper):
        metadata=Metadata()
        metadata.title=paper.title
        metadata.authors=paper.authors
        #Todo
        #Extract DOI
        doi_pattern=r"10\.\d{4,9}/[-._;()/:A-Z0-9]+"
        match=re.search(
            doi_pattern,
            document.full_text,
            flags=re.IGNORECASE
        )
        if match:
            metadata.doi=match.group()
        #Extract Year
        year_pattern=r"\b(19|20)\d{2}\b"
        years=re.findall(year_pattern,document.full_text)
        #Extract Keywords
        # Extract Venue
        return metadata