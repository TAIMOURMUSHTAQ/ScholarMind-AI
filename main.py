import pymupdf

doc = pymupdf.open("User_Guide NUS Summer Internship.pdf")
#Extract text from pdf only
# for page in doc:
#     print(page.get_text())

#Meta Deta Extraction
page = doc[0]

blocks = page.get_text("dict")["blocks"]
for block in blocks:
    if block["type"] == 0:  # text block
        for line in block["lines"]:
            for span in line["spans"]:
                print(f"{span['text']!r}  font={span['font']}  size={span['size']:.1f}")
    