from pathlib import Path

import pymupdf
import pytest

from app.exceptions import InvalidPDFError, ScannedPDFError
from app.pdf.pdf_processor import PDFProcessor

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_pdfs"
SAMPLE_PAPER = SAMPLE_DIR / "sample_conference_paper.pdf"


def _make_image_only_pdf(path: Path) -> None:
    """Build a PDF with a page containing only a drawing, no text layer at all —
    a stand-in for a scanned/image-only document."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.draw_rect(page.rect, color=(0, 0, 0), fill=(0.8, 0.8, 0.8))
    doc.save(path)
    doc.close()


def test_parses_real_paper_into_structured_sections():
    if not SAMPLE_PAPER.exists():
        pytest.skip("sample paper fixture not present")

    paper = PDFProcessor().parse(SAMPLE_PAPER)

    assert paper.title
    assert paper.full_text
    assert paper.page_count > 0
    assert isinstance(paper.sections, list)


def test_detects_scanned_pdf_with_no_text_layer(tmp_path):
    image_only_pdf = tmp_path / "scanned.pdf"
    _make_image_only_pdf(image_only_pdf)

    with pytest.raises(ScannedPDFError):
        PDFProcessor().parse(image_only_pdf)


def test_missing_file_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        PDFProcessor().parse("does_not_exist.pdf")


def test_corrupt_file_raises_invalid_pdf_error(tmp_path):
    bad_file = tmp_path / "not_a_pdf.pdf"
    bad_file.write_bytes(b"this is not a pdf")

    with pytest.raises(InvalidPDFError):
        PDFProcessor().parse(bad_file)
