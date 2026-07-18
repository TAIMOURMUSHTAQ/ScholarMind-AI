Project Architecture
📁 ScholarMind-AI

    📁 src

        📁 models

            📄 document.py

            📄 page.py

        📁 reader

            📄 pdf_reader.py

            📄 metadata.py

            📄 exporter.py

        📁 utils

            📄 logger.py

            📄 exceptions.py

    📁 tests

        📄 test_pdf_reader.py

    📁 docs

        📄 architecture_v1.md

    📁 data

        📁 sample_pdfs

        📁 outputs

    📁 notebooks

    📄 README.md

    📄 requirements.txt

    📄 .gitignore

    📄 main.py


    # ScholarMind AI - Architecture Version 1

## Project Goal

ScholarMind AI is an intelligent research assistant that helps researchers analyze academic documents.
The first module focuses on building a reliable PDF processing pipeline that extracts and structures information from documents.

---

# Architecture Overview

PDF File

    |
    |
    v

PDFReader

    |
    |
    v

Document Object

    |
    |
    +----------------+
    |                |
    v                v

Metadata        Future AI Modules

                |
                |
                +--> Summarizer
                +--> Keyword Extractor
                +--> Citation Analysis
                +--> Chat with Paper


---

# Design Questions

## 1. Why shouldn't we return only text instead of a Document object?

Returning only text limits the application because a research paper contains much more information than text.

A document also contains:

- title
- author
- metadata
- page information
- file information
- future AI analysis results

A Document object allows different modules to access the same structured information without repeatedly processing the PDF.

---

## 2. Which design is easier to extend: String or Document object?

A Document object is easier to extend.

If we use a string, adding new information requires changing the whole system.

For example:

Later we may need:

- DOI
- publication date
- sections
- citations
- references

With a Document object, we can add new fields without changing every module.

---

## 3. Should AI modules receive text or Document?

AI modules should receive the Document object.

Examples:

Summarizer(document)

KeywordExtractor(document)

CitationAnalyzer(document)

Because the Document object provides context and allows future improvements.

---

# Responsibility of Document Class

The Document class only stores information about a PDF document.

It does not:

- read PDFs
- clean text
- summarize content
- perform AI tasks
- export files

Those responsibilities belong to separate modules.