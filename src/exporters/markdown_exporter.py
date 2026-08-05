from pathlib import Path


class MarkdownExporter:

    @staticmethod
    def export(paper, output_path):

        lines = []

        # ----------------------------
        # Title
        # ----------------------------
        lines.append(f"# {paper.title}\n")

        # ----------------------------
        # Authors
        # ----------------------------
        lines.append("## Authors\n")

        if paper.authors:
            for author in paper.authors:
                lines.append(f"- {author}")
        else:
            lines.append("Not Available")

        # ----------------------------
        # Abstract
        # ----------------------------
        lines.append("\n## Abstract\n")

        lines.append(
            paper.abstract if paper.abstract else "Not Available"
        )

        # ----------------------------
        # Sections
        # ----------------------------
        lines.append("\n## Sections\n")

        if paper.sections:

            for section in paper.sections:

                lines.append(f"### {section.title}")
                lines.append(section.content)

        else:

            lines.append("No Sections Found")

        # ----------------------------
        # References
        # ----------------------------
        lines.append("\n## References\n")

        if paper.references:

            for ref in paper.references:

                lines.append(f"- [{ref.number}] {ref.raw_text}")

        else:

            lines.append("No References Found")

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(output_path, "w", encoding="utf-8") as file:

            file.write("\n".join(lines))

        print("Markdown exported successfully.")