from app.models.domain import Section
from app.rag.chunking import ChunkGenerator


def _section(title, word_count, page_start=1, page_end=1, prefix="word"):
    text = " ".join(f"{prefix}{i}." for i in range(word_count))
    return Section(title=title, content=text, page_start=page_start, page_end=page_end)


def test_chunks_never_cross_section_boundaries():
    sections = [_section("Intro", 50, prefix="intro"), _section("Methods", 50, prefix="method")]
    chunks = ChunkGenerator.generate("paper-1", sections)

    assert all(c.section_title in ("Intro", "Methods") for c in chunks)
    intro_chunks = [c for c in chunks if c.section_title == "Intro"]
    methods_chunks = [c for c in chunks if c.section_title == "Methods"]
    assert intro_chunks and methods_chunks
    # No Intro vocabulary should ever leak into a Methods chunk, or vice versa.
    assert "intro49." not in " ".join(c.text for c in methods_chunks).split()
    assert "method0." not in " ".join(c.text for c in intro_chunks).split()


def test_long_section_splits_into_multiple_overlapping_chunks():
    sections = [_section("Results", 600)]
    chunks = ChunkGenerator.generate("paper-1", sections)

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.word_count > 0
        assert chunk.paper_id == "paper-1"
        assert chunk.page_start == 1 and chunk.page_end == 1


def test_empty_section_produces_no_chunks():
    sections = [Section(title="Empty", content="   ", page_start=0, page_end=0)]
    assert ChunkGenerator.generate("paper-1", sections) == []


def test_chunk_ids_are_unique():
    sections = [_section("Intro", 400)]
    chunks = ChunkGenerator.generate("paper-1", sections)
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))
