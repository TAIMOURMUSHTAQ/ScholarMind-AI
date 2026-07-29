# from src.reader.pdf_reader import PDFReader
# def main():
#     reader=PDFReader(
#         "data/sample_pdfs/sample_confrence_paper.pdf"
#     )
    
#     document=reader.read()
#     #For explicit metadata
#     print("\n Metadata")
#     for key, value in document.metadata.items():
#           print(f"{key}: {value}")
#     #For statistics
#     print("\n Page Statistics")
#     for page in document.pages:
#           print(
#                 page.page_number,
#                 page.word_count,
#                 page.character_count
#           )
#     #Experiment
#     print(document.metadata)
#     print(document.pages[0])
#     print(document.pages[-1].word_count)
#     #Code start here
#     print("="*60)
#     print("ScholarMind AI")
#     print("="*60)

#     print(f"File Name : {document.file_name}")
#     print(f"Page      :{document.page_count}")
#     print(f"Words      :{document.pages[0].word_count}")

#     print("\nFirst 500 Characters:\n")
#     print(document.full_text[:500])


# if __name__=="__main__":
#         main()


from src.parser.paper_parser import PaperParser
from pathlib import Path
from src.exporters.json_exporter import JSONExporter
def main():
    parser = PaperParser()
    # paper = parser.parse(
    #     r"data\sample_pdfs\sample_conference_paper.pdf"
    # )
    

    PROJECT_ROOT = Path(__file__).resolve().parent

    PDF_PATH = (
        PROJECT_ROOT
        / "data"
        / "sample_pdfs"
        / "sample_conference_paper.pdf"
    )

    paper = parser.parse(str(PDF_PATH))
    print("=" * 60)
    print("ScholarMind AI")
    print("=" * 60)
    print("\nTITLE")
    print("-" * 60)
    print(paper.title)
    print("\nAUTHORS")
    print("-" * 60)
    for author in paper.authors:
        print(author)
    print("\nABSTRACT")
    print("-" * 60)
    print(paper.abstract)
    print("\n\nSECTIONS")
    print("-"*60)
    for section in paper.sections:
        print(section.title)
        # print(section.content[:150])
        print()
        print(section.content[:150])
    print("\nCITATIONS")
    print("-" * 60)

    if not paper.citations:

        print("No citations found.")

    else:

        for citation in paper.citations:

            print(
                f"[{citation.reference_number}] "
                f"{citation.section_title}"
            )

            print(citation.sentence)
        print()    
    print("\nREFERENCES")
    print("-"*60)
    for reference in paper.references:
        print(f"[{reference.number}]")
        print(reference.text)
        print()
    print("\nMETADATA")
    print("-" * 60)
    print("DOI:", paper.metadata.doi)
    print("Year:", paper.metadata.year)
    print("Venue:", paper.metadata.venue)
    print("Keywords:", paper.metadata.keywords)
    JSONExporter.export(
        paper,
        "output/paper.json"
    )
    print("\nJSON exported successfully.")
if __name__ == "__main__":
    main()