"""Heuristic metadata/content extractors over reading-order-sorted layout blocks.

These are deliberately simple, regex/font-size heuristics tuned to common
single-column and IEEE-style two-column academic PDFs. They are the
weakest, most format-specific part of the pipeline - expected to misfire
on unusual layouts (see README's "Known limitations" section) but good
enough to power the up-front "paper summary card"; the chat itself does
not depend on their accuracy since it's grounded in retrieved chunk text.
"""
import re

from app.models.domain import Citation, Metadata, Reference, Section


class TitleExtractor:
    @staticmethod
    def extract(layout_blocks) -> str:
        if not layout_blocks:
            return ""
        title_block = max(layout_blocks, key=lambda b: b.font_size)
        return title_block.text.strip()


class AuthorExtractor:
    @staticmethod
    def extract(layout_blocks, title: str) -> list[str]:
        title_index = next(
            (i for i, b in enumerate(layout_blocks) if b.text == title), -1
        )
        if title_index == -1:
            return []

        for block in layout_blocks[title_index + 1 : title_index + 4]:
            text = block.text.strip()
            if not text:
                continue
            if text.lower().startswith("abstract"):
                break

            text = (
                text.replace("Fellow, IEEE", "")
                .replace("Senior Member, IEEE", "")
                .replace("Member, IEEE", "")
                .replace(", IEEE", "")
                .replace(" and ", ", ")
            )
            authors = [
                name.strip()
                for name in text.split(",")
                if name.strip() and len(name.strip().split()) >= 2
            ]
            if authors:
                return authors
        return []


class AbstractExtractor:
    @staticmethod
    def extract(layout_blocks) -> str:
        lines, inside = [], False
        for block in layout_blocks:
            text = block.text.strip()
            if not text:
                continue

            if text.lower().startswith("abstract"):
                inside = True
                text = re.sub(r"^abstract[\s—\-:]*", "", text, flags=re.IGNORECASE).strip()
                if text:
                    lines.append(text)
                continue

            if inside:
                upper = text.upper()
                if upper.startswith("I.") or upper.startswith("1."):
                    break
                lines.append(text)
        return "\n".join(lines)


class SectionExtractor:
    """Splits blocks into numbered sections (`I. INTRO`, `1. Intro`), tracking
    each section's page span for later chunk provenance."""

    HEADING_PATTERN = re.compile(r"^(?:[IVXLC]+\.|[0-9]+\.)\s*", re.IGNORECASE)

    @classmethod
    def extract(cls, layout_blocks) -> list[Section]:
        sections: list[Section] = []
        title, content, page_start, page_end = None, [], None, None

        def flush():
            if title:
                sections.append(
                    Section(
                        title=title,
                        content="\n".join(content).strip(),
                        page_start=page_start or 0,
                        page_end=page_end or 0,
                    )
                )

        for block in layout_blocks:
            text = block.text.strip()
            if not text:
                continue

            normalized = text.upper().replace(" ", "").replace("\n", "")
            if normalized.startswith("REFERENCES"):
                flush()
                return sections

            if cls.HEADING_PATTERN.match(text):
                flush()
                title, content = text, []
                page_start = page_end = block.page_number
            elif title:
                content.append(text)
                page_end = block.page_number

        flush()
        return sections


class CitationExtractor:
    PATTERN = re.compile(r"\[(\d+)\]")

    @classmethod
    def extract(cls, sections: list[Section]) -> list[Citation]:
        citations = []
        for section in sections:
            sentences = re.split(r"(?<=[.!?])\s+", section.content)
            for sentence in sentences:
                for match in cls.PATTERN.findall(sentence):
                    citations.append(
                        Citation(
                            reference_number=int(match),
                            section_title=section.title,
                            sentence=sentence.strip(),
                        )
                    )
        return citations


class ReferenceExtractor:
    @staticmethod
    def extract(layout_blocks) -> list[Reference]:
        references, collecting = [], False
        number, text_buf = 0, ""

        for block in layout_blocks:
            text = block.text.strip()
            if not text:
                continue

            if not collecting:
                if text.upper().startswith("REFERENCES"):
                    collecting = True
                continue

            match = re.match(r"^\[(\d+)\]", text)
            if match:
                if text_buf:
                    references.append(Reference(number=number, raw_text=text_buf.strip()))
                number, text_buf = int(match.group(1)), text
            else:
                text_buf += " " + text

        if text_buf:
            references.append(Reference(number=number, raw_text=text_buf.strip()))
        return references


class MetadataExtractor:
    DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
    YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

    @classmethod
    def extract(cls, full_text: str, title: str, authors: list[str]) -> Metadata:
        metadata = Metadata(title=title, authors=authors)

        doi_match = cls.DOI_PATTERN.search(full_text)
        if doi_match:
            metadata.doi = doi_match.group()

        year_match = cls.YEAR_PATTERN.search(full_text)
        if year_match:
            metadata.year = year_match.group()

        return metadata


class DocumentStatistics:
    @staticmethod
    def analyze(paper) -> dict:
        stats: dict = {
            "author_count": len(paper.authors),
            "section_count": len(paper.sections),
            "reference_count": len(paper.references),
            "citation_count": len(paper.citations),
            "page_count": paper.page_count,
        }
        words = paper.full_text.split()
        stats["word_count"] = len(words)
        sentences = [s.strip() for s in re.split(r"[.!?]+", paper.full_text) if s.strip()]
        stats["sentence_count"] = len(sentences)
        stats["average_sentence_length"] = round(len(words) / len(sentences), 2) if sentences else 0
        return stats
