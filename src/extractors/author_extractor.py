from src.models.layout_block import LayoutBlock
class AuthorExtractor:

    @staticmethod
    def extract(layout_blocks: list[LayoutBlock], title: str):
        title_index = -1
        # Locate title
        for i, block in enumerate(layout_blocks):
            if block.text == title:
                title_index = i
                break
        if title_index == -1:
            return []
        # Search only the next few blocks
        for block in layout_blocks[title_index + 1:title_index + 4]:
            text = block.text.strip()
            if not text:
                continue
            # Stop if we already reached Abstract
            if text.lower().startswith("abstract"):
                break
            # Clean common academic titles
            text = (
                text.replace("Fellow, IEEE", "")
                    .replace("Senior Member, IEEE", "")
                    .replace("Member, IEEE", "")
                    .replace(", IEEE", "")
                    .replace(" and ", ", ")
            )
            authors = []
            for name in text.split(","):
                name = name.strip()
                if not name:
                    continue
                # Skip obvious non-author lines
                if len(name.split()) < 2:
                    continue
                authors.append(name)
            if authors:
                return authors
        return []