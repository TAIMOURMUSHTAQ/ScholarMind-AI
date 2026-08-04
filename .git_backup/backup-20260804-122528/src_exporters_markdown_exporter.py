from pathlib import Path


class MarkdownExporter:

    @staticmethod
    def export(paper, output_path):
        """
        Export the parsed paper to a human-readable Markdown file.
        Handles objects (Section, Reference) and gracefully falls
        back when optional fields are missing.
        """

        lines = []

        # Title
        lines.append(f"# {paper.title or 'Untitled'}\n")

        # Authors
        lines.append("## Authors\n")
        if paper.authors:
            for author in paper.authors:
                lines.append(f"- {author}")
        else:
            lines.append("Not Available")

        # Abstract
        lines.append("\n## Abstract\n")
        lines.append(paper.abstract if paper.abstract else "Not Available")

        # Sections
        lines.append("\n## Sections\n")
        if paper.sections:
            for section in paper.sections:
                title = getattr(section, 'title', 'Untitled Section')
                content = getattr(section, 'content', '')
                lines.append(f"### {title}\n")
                # include a short preview of content
                preview = content.strip()[:600]
                if preview:
                    lines.append(preview)
                lines.append("")
        else:
            lines.append("No Sections Found")

        # References
        lines.append("\n## References\n")
        if paper.references:
            for ref in paper.references:
                # Use raw_text when available, otherwise build a simple line
                raw = getattr(ref, 'raw_text', None)
                if raw:
                    lines.append(f"- {raw}")
                else:
                    authors = getattr(ref, 'authors', '')
                    title = getattr(ref, 'title', '')
                    year = getattr(ref, 'year', '')
                    lines.append(f"- {authors} — {title} ({year})")
        else:
            lines.append("No References Found")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        print(f"Markdown exported successfully: {output_path}")