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


# from src.parser.paper_parser import PaperParser
# from pathlib import Path
# from src.exporters.json_exporter import JSONExporter
# from src.exporters.markdown_exporter import MarkdownExporter
# def main():
#     parser = PaperParser()
#     # paper = parser.parse(
#     #     r"data\sample_pdfs\sample_conference_paper.pdf"
#     # )
    

#     PROJECT_ROOT = Path(__file__).resolve().parent

#     PDF_PATH = (
#         PROJECT_ROOT
#         / "data"
#         / "sample_pdfs"
#         / "sample_conference_paper.pdf"
#     )

#     paper = parser.parse(str(PDF_PATH))
#     print("=" * 60)
#     print("ScholarMind AI")
#     print("=" * 60)
#     print("\nTITLE")
#     print("-" * 60)
#     print(paper.title)
#     print("\nAUTHORS")
#     print("-" * 60)
#     for author in paper.authors:
#         print(author)
#     print("\nABSTRACT")
#     print("-" * 60)
#     print(paper.abstract)
#     print("\n\nSECTIONS")
#     print("-"*60)
#     for section in paper.sections:
#         print(section.title)
#         # print(section.content[:150])
#         print()
#         print(section.content[:150])
#     print("\nCITATIONS")
#     print("-" * 60)

#     if not paper.citations:

#         print("No citations found.")

#     else:

#         for citation in paper.citations:

#             print(
#                 f"[{citation.reference_number}] "
#                 f"{citation.section_title}"
#             )

#             print(citation.sentence)
#         print()    
#     print("\nREFERENCES")
#     print("-"*60)
#     for reference in paper.references:
#         print(f"[{reference.number}]")
#         print(reference.text)
#         print()
#     print("\nMETADATA")
#     print("-" * 60)
#     print("DOI:", paper.metadata.doi)
#     print("Year:", paper.metadata.year)
#     print("Venue:", paper.metadata.venue)
#     print("Keywords:", paper.metadata.keywords)
#     MarkdownExporter.export(
#     paper,
#     "output/paper.md"
#     )
#     JSONExporter.export(
#         paper,
#         "output/paper.json"
#     )
#     print("\nJSON exported successfully.")
# if __name__ == "__main__":
#     main()

import argparse
import os
from pathlib import Path

from src.parser.paper_parser import PaperParser
from src.exporters.json_exporter import JSONExporter
from src.exporters.markdown_exporter import MarkdownExporter
from src.vectorstore.vector_store import VectorStore
from src.search.semantic_search import SemanticSearcher

def main():

    parser = argparse.ArgumentParser(
        description="Parse a paper and optionally start chat."
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Start the interactive chat loop after parsing."
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ScholarMind AI")
    print("=" * 60)

    # --------------------------------------------------
    # Project Paths
    # --------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parent

    DATA_FOLDER = PROJECT_ROOT / "data" / "sample_pdfs"

    PDF_PATH = DATA_FOLDER / "sample_conference_paper.pdf"

    OUTPUT_FOLDER = PROJECT_ROOT / "output"

    # --------------------------------------------------
    # Debug Information
    # --------------------------------------------------

    print("\nProject Root:")
    print(PROJECT_ROOT)

    print("\nPDF Path:")
    print(PDF_PATH)

    print("\nPDF Exists:")
    print(PDF_PATH.exists())

    if not PDF_PATH.exists():

        print("\nFiles found inside sample_pdfs:\n")

        if DATA_FOLDER.exists():

            for file in DATA_FOLDER.iterdir():
                print(file.name)

        else:

            print("Folder does not exist:", DATA_FOLDER)

        return

    # --------------------------------------------------
    # Parse Paper
    # --------------------------------------------------

    paper_parser = PaperParser()

    paper = paper_parser.parse(PDF_PATH)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    MarkdownExporter.export(
        paper,
        OUTPUT_FOLDER / "paper.md"
    )

    JSONExporter.export(
        paper,
        OUTPUT_FOLDER / "paper.json"
    )

    searcher = None
    if paper.chunks:
        vector_db = VectorStore()
        vector_db.build(paper.chunks)
        vector_db.save("indexes")
        searcher = SemanticSearcher(
            vector_db,
            paper.chunks
        )
    else:
        print("\nNo chunks were generated, so semantic search was skipped.")

    # --------------------------------------------------
    # Display Results
    # --------------------------------------------------

    print("\nTITLE")
    print("-" * 60)
    print(paper.title)

    print("\nAUTHORS")
    print("-" * 60)

    if paper.authors:
        for author in paper.authors:
            print(author)
    else:
        print("No authors found.")

    print("\nABSTRACT")
    print("-" * 60)
    print(paper.abstract or "No abstract found.")

    print("\nSECTIONS")
    print("-" * 60)

    if paper.sections:
        for section in paper.sections:
            print(section.title)
            print(section.content[:150])
            print()
    else:
        print("No sections found.")

    print("\nCITATIONS")
    print("-" * 60)

    if paper.citations:
        for citation in paper.citations:
            print(f"[{citation.reference_number}] {citation.section_title}")
            print(citation.sentence)
            print()
    else:
        print("No citations found.")

    print("\nREFERENCES")
    print("-" * 60)

    if not paper.references:

            print("No references found.")
    else:

        for reference in paper.references:
                print(f"[{reference.number}]")
                print(reference.raw_text)
                print()

    print("\nMETADATA")
    print("-" * 60)
    print("DOI      :", paper.metadata.doi)
    print("Year     :", paper.metadata.year)
    print("Venue    :", paper.metadata.venue)
    print("Keywords :", paper.metadata.keywords)

    print("\nDOCUMENT STATISTICS")
    print("-" * 60)
    if paper.statistics:
        for key, value in paper.statistics.items():
            print(f"{key:<30} {value}")
    else:
        print("No document statistics available.")


    print()

    print("="*60)

    print("SEMANTIC SEARCH")

    print("="*60)

    if searcher is not None:
        results = searcher.search(
            "conference paper formatting",
            top_k=3
        )

        for chunk, score in results:

            print()
            print(chunk.title)
            print(score)
            print(chunk.text[:250])

    if args.chat:

        from src.chat.chat_engine import ChatEngine

        if not os.getenv("GEMINI_API_KEY"):
            print("\nChat skipped because GEMINI_API_KEY is not set.")
            return

        if searcher is None:
            print("\nChat skipped because no chunks were generated.")
            return

        chat = ChatEngine(
            semantic_searcher=searcher
        )

        print("\n" + "=" * 60)
        print("ScholarMind AI Chat")
        print("=" * 60)
        print("Type 'exit' or 'quit' to leave.\n")

        while True:

            question = input("Ask > ").strip()

            if question.lower() in ["exit", "quit"]:
                break

            try:

                result = chat.ask(question)

                print("\n" + "=" * 60)
                print("ANSWER")
                print("=" * 60)
                print(result["answer"])

            except Exception as e:

                print("\nError:", e)

    print("\nParsing completed successfully.")


if __name__ == "__main__":
    main()