from src.extractors.title_extractor import TitleExtractor

def test_creation():
    extractor=TitleExtractor()
    assert extractor is not None