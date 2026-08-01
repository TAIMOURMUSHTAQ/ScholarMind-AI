import re

from src.models.section import Section


class SectionExtractor:
    """
    Extract numbered sections from the paper.

    Stops collecting section content when the REFERENCES
    heading is reached.
    """

    @staticmethod
    def extract(layout_blocks):

        sections = []

        current_title = None
        current_content = []

        # Matches:
        # I. INTRODUCTION
        # II. METHODS
        # 1. INTRODUCTION
        heading_pattern = re.compile(
            r"^(?:[IVXLC]+\.|[0-9]+\.)\s*",
            re.IGNORECASE
        )

        for block in layout_blocks:

            text = block.text.strip()

            if not text:
                continue

            # -------------------------
            # Normalize heading text
            # -------------------------

            normalized = (
                text.upper()
                .replace(" ", "")
                .replace("\n", "")
            )

            # -------------------------
            # Stop at REFERENCES
            # Handles:
            # REFERENCES
            # R EFERENCES
            # R E F E R E N C E S
            # -------------------------

            if normalized.startswith("REFERENCES"):

                if current_title:

                    sections.append(
                        Section(
                            title=current_title,
                            content="\n".join(current_content).strip()
                        )
                    )

                break

            # -------------------------
            # New numbered section
            # -------------------------

            if heading_pattern.match(text):

                if current_title:

                    sections.append(
                        Section(
                            title=current_title,
                            content="\n".join(current_content).strip()
                        )
                    )

                current_title = text
                current_content = []

            else:

                if current_title:

                    current_content.append(text)

        # -------------------------
        # Save last section
        # -------------------------

        if current_title:

            if (
                len(sections) == 0
                or sections[-1].title != current_title
            ):

                sections.append(
                    Section(
                        title=current_title,
                        content="\n".join(current_content).strip()
                    )
                )

        return sections