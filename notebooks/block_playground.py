import pymupdf

from src.extractors.block_extractor import BlockExtractor

doc=pymupdf.open(
    "data/sample_pdfs/sample_conference_paper.pdf"
)
page=doc[0]
blocks=BlockExtractor.extract(page)
print(f"Number of blocks: {len(blocks)}")
print()
for block in blocks:
    print(block)
    print("-" * 80)