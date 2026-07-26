import json
from pathlib import Path
class JSONExporter:
    @staticmethod
    def export(paper, output_path):
        output_path = Path(output_path)
        # Create output folder if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content
                }
                for section in paper.sections
            ]
        }
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )