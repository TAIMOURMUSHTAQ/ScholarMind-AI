import pymupdf

from app.rag.export import build_markdown, build_pdf


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
        return "".join(page.get_text() for page in doc)
    finally:
        doc.close()

TURNS = [
    {"role": "user", "content": "What dataset was used?", "sources": []},
    {
        "role": "assistant",
        "content": "The paper uses ImageNet (Source 1).",
        "sources": [
            {"rank": 1, "section_title": "Experiments", "page_start": 3, "page_end": 3, "score": 0.9, "preview": "..."}
        ],
    },
]


def test_markdown_export_includes_title_speakers_and_sources():
    markdown = build_markdown("My Paper", TURNS)

    assert "# Chat transcript: My Paper" in markdown
    assert "**You:** What dataset was used?" in markdown
    assert "**ScholarMind AI:** The paper uses ImageNet (Source 1)." in markdown
    assert "Source 1: Experiments (pages 3-3)" in markdown


def test_markdown_export_labels_sources_with_paper_title_when_comparing():
    compare_turns = [
        {
            "role": "assistant",
            "content": "Paper A uses ImageNet; Paper B uses COCO.",
            "sources": [
                {
                    "rank": 1, "section_title": "Experiments", "page_start": 3, "page_end": 3,
                    "score": 0.9, "preview": "...", "paper_title": "Paper A",
                }
            ],
        }
    ]
    markdown = build_markdown("Paper A vs Paper B", compare_turns)
    assert "Source 1: Paper A - Experiments (pages 3-3)" in markdown


def test_pdf_export_produces_nonempty_bytes():
    pdf_bytes = build_pdf("My Paper", TURNS)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100


def test_pdf_export_renders_non_latin1_characters_faithfully():
    unicode_turns = [{"role": "assistant", "content": "Uses ≥ 90% accuracy — impressive: 日本語も.", "sources": []}]
    pdf_bytes = build_pdf("My Paper", unicode_turns)

    assert pdf_bytes.startswith(b"%PDF")
    extracted = _extract_pdf_text(pdf_bytes)
    assert "≥ 90% accuracy — impressive" in extracted
