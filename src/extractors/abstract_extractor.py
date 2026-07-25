from src.models.layout_block import LayoutBlock


class AbstractExtractor:

    @staticmethod
    def extract(layout_blocks: list[LayoutBlock]) -> str:

        abstract_lines = []

        inside_abstract = False

        for block in layout_blocks:

            text = block.text.strip()

            if not text:
                continue

            # Beginning of abstract
            if text.lower().startswith("abstract"):

                inside_abstract = True

                # Remove heading
                text = (
                    text.replace("Abstract—", "")
                        .replace("Abstract-", "")
                        .replace("Abstract:", "")
                        .replace("Abstract", "")
                        .strip()
                )

                if text:
                    abstract_lines.append(text)

                continue

            if inside_abstract:

                upper = text.upper()

                # IEEE section heading
                if upper.startswith("I.") or upper.startswith("1."):

                    break

                abstract_lines.append(text)

        return "\n".join(abstract_lines)