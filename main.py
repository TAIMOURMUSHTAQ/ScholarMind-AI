import pymupdf
import pymupdf4llm
doc = pymupdf.open("User_Guide NUS Summer Internship.pdf")
#Extract text from pdf only
# for page in doc:
#     print(page.get_text())

#Meta Deta Extraction
# page = doc[0]

# blocks = page.get_text("dict")["blocks"]
# for block in blocks:
#     if block["type"] == 0:  # text block
#         for line in block["lines"]:
#             for span in line["spans"]:
#                 print(f"{span['text']!r}  font={span['font']}  size={span['size']:.1f}")

#Renders Tables in PDF
# page = doc[0] 
# tables = page.find_tables()
# for table in tables:
#     print(table.to_markdown())

#     # or get as Pandas DataFrame
#     df = table.to_pandas()

#Render a page to image
# page = doc[0]

# pixmap = page.get_pixmap(dpi=150)
# pixmap.save("page_0.png")

#Convert Markdown to Pdf
# md_doc = pymupdf.open("example.md")
# md_doc.save("example.pdf")

#Convert to Markdown for LLMs
md = pymupdf4llm.to_markdown("report.pdf")
# Pass directly to your LLM or vector store
print(md)

#Annotate(Find underline, highlights etc) and Redact (It does not delete anything yet.It only marks an area that should be deleted later.Think of it like placing a sticky note saying:DELETE THIS LATER)
page = doc[0]
# Add a highlight annotation
rect = pymupdf.Rect(72, 100, 400, 120)
page.add_highlight_annot(rect)
# Add a redaction and apply it
page.add_redact_annot(rect)
page.apply_redactions()
doc.save("contract_redacted.pdf")

#Merge Pdfs
merger = pymupdf.open()
for path in ["part1.pdf", "part2.pdf", "part3.pdf"]:
    merger.insert_pdf(pymupdf.open(path))
merger.save("merged.pdf")

