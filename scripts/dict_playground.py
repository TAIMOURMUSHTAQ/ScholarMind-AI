import pymupdf

doc=pymupdf.open(
    r"C:\Users\Win\OneDrive\Scholor Mind AI\data\sample_pdfs\sample_confrence_paper.pdf"
)
page=doc[0]
data=page.get_text("dict")
# print(data.keys())
print(data["blocks"][0].keys())
#First Line
block = data["blocks"][0]
line = block["lines"][0]
print(line.keys())
span = line["spans"][0]
# print(span)
print(f"Text : {span['text']}")
print(f"Font : {span['font']}")
print(f"Size : {span['size']}")
print(f"Flags: {span['flags']}")
print(f"Color: {span['color']}")
print("-" * 50)