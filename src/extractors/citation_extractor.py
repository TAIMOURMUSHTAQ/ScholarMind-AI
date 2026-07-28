import re
from src.models.citation import Citation

class CitationExtractor:
    @staticmethod
    def extract(sections):
        citations=[]
        pattern=r"\[(\d+)\]"
        for section in sections:
            sentences=re.split(r"(?<=[.!?])\s+",section.content)
            for sentence in sentences:
                mathces=re.findall(pattern,sentence)
                for match in mathces:
                    citations.append(
                        Citation(
                            reference_number=int(match),
                            section_title=section.title,
                            sentence=sentence.strip()
                        )
                    )
        return citations