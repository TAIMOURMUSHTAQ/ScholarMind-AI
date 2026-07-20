from src.reader.pdf_reader import PDFReader

def test_reader_creation():

    reader=PDFReader(
        "data/sample_pdfs/sample_conference_paper.pdf"
    )
    assert reader.pdf_path.endswith(".pdf")