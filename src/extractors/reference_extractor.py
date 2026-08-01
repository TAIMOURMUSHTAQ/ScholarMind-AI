import re

from src.models.reference import Reference


class ReferenceExtractor:
    """
    Extract bibliography entries from the REFERENCES section.
    """

    @staticmethod
    def extract(layout_blocks):

        references = []

        collecting = False

        reference_text = ""

        reference_number = 0

        for block in layout_blocks:

            text = block.text.strip()

            if not text:
                continue

            upper = text.upper()

            # -------------------------
            # Find References Heading
            # -------------------------
            if not collecting:

                if upper.startswith("REFERENCES"):

                    collecting = True

                continue

            # -------------------------
            # New reference starts?
            # -------------------------

            match = re.match(r"^\[(\d+)\]", text)

            if match:

                # Save previous reference

                if reference_text:

                    references.append(
                        Reference(
                            number=reference_number,
                            raw_text=reference_text.strip()
                        )
                    )

                reference_number = int(match.group(1))

                reference_text = text

            else:

                reference_text += " " + text

        # Save final reference

        if reference_text:

            references.append(
                Reference(
                    number=reference_number,
                    raw_text=reference_text.strip()
                )
            )

        return references