"""Structure-aware chunking.

Chunks respect section boundaries (never mixing two sections into one chunk)
and, within a section, split on sentence boundaries rather than blind
fixed-size word cuts. A sliding overlap keeps context from being severed
right at a chunk edge, which matters for retrieval quality on paragraphs
that span the boundary.
"""
import re
import uuid

from app.config import CHUNK_OVERLAP_WORDS, CHUNK_SIZE_WORDS
from app.models.domain import Chunk, Section

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


class ChunkGenerator:
    @staticmethod
    def generate(paper_id: str, sections: list[Section]) -> list[Chunk]:
        chunks: list[Chunk] = []

        for section in sections:
            sentences = _split_sentences(section.content)
            if not sentences:
                continue

            current: list[str] = []
            current_words = 0

            def flush():
                if not current:
                    return
                text = " ".join(current)
                chunks.append(
                    Chunk(
                        id=str(uuid.uuid4()),
                        paper_id=paper_id,
                        section_title=section.title,
                        text=text,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        word_count=len(text.split()),
                    )
                )

            for sentence in sentences:
                sentence_words = len(sentence.split())

                if current_words + sentence_words > CHUNK_SIZE_WORDS and current:
                    flush()
                    # Carry trailing sentences forward as overlap context.
                    overlap: list[str] = []
                    overlap_words = 0
                    for prev in reversed(current):
                        prev_words = len(prev.split())
                        if overlap_words + prev_words > CHUNK_OVERLAP_WORDS:
                            break
                        overlap.insert(0, prev)
                        overlap_words += prev_words
                    current = overlap
                    current_words = overlap_words

                current.append(sentence)
                current_words += sentence_words

            flush()

        return chunks
