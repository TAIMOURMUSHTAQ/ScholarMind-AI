import json

class JSONExporter:
    @staticmethod
    def export(paper,output_path):
        data={
            "title":paper.title,
            "authors":paper.authors,
            "abstract":paper.abstract,
            "sections":[
                {
                    "title":section.title,
                    "content":section.content
                }
                for section in paper.sections
            ]
        }
        with open (output_path,"w",encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )