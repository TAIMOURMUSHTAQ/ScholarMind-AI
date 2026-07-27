import re
from src.models.reference import Reference
class ReferenceExtractor:
    @staticmethod
    def extract(layout_blocks):
        references = []
        inside_reference = False
        current_reference = ""
        current_number = 0

        for block in layout_blocks:
            text = block.text.strip()
            # Detect start of References section
            if text.upper().startswith("REFERENCES"):
                inside_reference = True
                continue
            if not inside_reference:
                continue
            # Match [1], [2], [3] ...
            match = re.match(r"^\[(\d+)\]\s*(.*)", text)
            if match:
                # Save previous reference
                if current_reference:
                    references.append(
                        Reference(
                            number=current_number,
                            text=current_reference.strip()
                        )
                    )
                current_number = int(match.group(1))
                current_reference = match.group(2)
            else:
                if current_reference:
                    current_reference += " " + text
        # Save last reference
        if current_reference:
            references.append(
                Reference(
                    number=current_number,
                    text=current_reference.strip()
                )
            )
        return references