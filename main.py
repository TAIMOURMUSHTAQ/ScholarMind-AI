from src.reader.pdf_reader import PDFReader
def main():
    reader=PDFReader(
        "data/sample_pdfs/sample_confrence_paper.pdf"
    )
    
    document=reader.read()
    print("\n Metadata")
    for key, value in document.metadata.items():
          print(f"{key}: {value}")
    #Experiment
    print(document.metadata)
    print(document.pages[0])
    print(document.pages[-1].word_count)
    #Code start here
    print("="*60)
    print("ScholarMind AI")
    print("="*60)

    print(f"File Name : {document.file_name}")
    print(f"Page      :{document.page_count}")
    print(f"Words      :{document.pages[0].word_count}")

    print("\nFirst 500 Characters:\n")
    print(document.full_text[:500])


if __name__=="__main__":
        main()
