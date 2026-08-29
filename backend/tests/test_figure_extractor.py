import pymupdf

from app.pdf.figure_extractor import FigureExtractor


def _make_pdf_with_image_and_caption(path, image_bytes: bytes):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_image(pymupdf.Rect(50, 50, 250, 250), stream=image_bytes)
    page.insert_text((50, 270), "Figure 1: A synthetic test image.")
    doc.save(path)
    doc.close()


def _make_png_bytes(width=200, height=200):
    doc = pymupdf.open()
    page = doc.new_page(width=width, height=height)
    page.draw_rect(page.rect, color=(0, 0, 0), fill=(0.5, 0.5, 0.9))
    pix = page.get_pixmap()
    png_bytes = pix.tobytes("png")
    doc.close()
    return png_bytes


def test_extracts_figure_with_caption(tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    _make_pdf_with_image_and_caption(pdf_path, _make_png_bytes())

    doc = pymupdf.open(pdf_path)
    try:
        figures = FigureExtractor.extract(doc, tmp_path / "figures")
    finally:
        doc.close()

    assert len(figures) == 1
    assert figures[0]["page"] == 0
    assert figures[0]["caption"].lower().startswith("figure 1")
    assert (tmp_path / "figures" / f"{figures[0]['id']}.{figures[0]['ext']}").exists()


def test_skips_small_images(tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_image(pymupdf.Rect(50, 50, 60, 60), stream=_make_png_bytes(width=20, height=20))
    doc.save(pdf_path)
    doc.close()

    doc = pymupdf.open(pdf_path)
    try:
        figures = FigureExtractor.extract(doc, tmp_path / "figures")
    finally:
        doc.close()

    assert figures == []
