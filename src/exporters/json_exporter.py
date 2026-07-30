import json
from pathlib import Path


class JSONExporter:

    @staticmethod
    def export(paper, output_path):
        """
        Export a parsed paper into JSON format.
        """

        output_path = Path(output_path)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {

            # -----------------------------------
            # Parser Information
            # -----------------------------------
            "parser": {
                "name": "ScholarMind Parser",
                "version": "1.0",
                "engine": "PyMuPDF"
            },

            # -----------------------------------
            # Metadata
            # -----------------------------------
            "metadata": {
                "doi": paper.metadata.doi,
                "year": paper.metadata.year,
                "venue": paper.metadata.venue,
                "keywords": paper.metadata.keywords
            },

            # -----------------------------------
            # Basic Information
            # -----------------------------------
            "title": paper.title,

            "authors": paper.authors,

            "abstract": paper.abstract,

            # -----------------------------------
            # Sections
            # -----------------------------------
            "sections": [
                {
                    "title": section.title,
                    "content": section.content
                }
                for section in paper.sections
            ],

            # -----------------------------------
            # Citations
            # -----------------------------------
            "citations": [
                {
                    "reference_number": citation.reference_number,
                    "section": citation.section_title,
                    "sentence": citation.sentence
                }
                for citation in paper.citations
            ],

            # -----------------------------------
            # References
            # -----------------------------------
            "references": [
                {
                    "number": reference.number,
                    "raw_text": reference.raw_text,
                    "authors": reference.authors,
                    "title": reference.title,
                    "year": reference.year,
                    "venue": reference.venue,
                    "doi": reference.doi
                }
                for reference in paper.references
            ]
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"JSON exported successfully: {output_path}")