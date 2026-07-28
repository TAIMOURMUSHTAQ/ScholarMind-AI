import re
from src.models.reference import Reference
class ReferenceExtractor:
    @staticmethod
    def extract(layout_blocks):
        references = []
        inside_reference = False
        current_reference = None
        for block in layout_blocks:
            text = block.text.strip()
            # Detect beginning of bibliography
            if text.upper().startswith("REFERENCES"):
                inside_reference = True
                continue
            if not inside_reference:
                continue
            # Match [1], [2], ...
            match = re.match(r"^\[(\d+)\]\s*(.*)", text)
            if match:
                if current_reference is not None:
                    references.append(current_reference)
                current_reference = Reference(
                    number=int(match.group(1)),
                    raw_text=match.group(2)
                )
            elif current_reference is not None:

                current_reference.raw_text += " " + text
        if current_reference is not None:
            references.append(current_reference)
        return references