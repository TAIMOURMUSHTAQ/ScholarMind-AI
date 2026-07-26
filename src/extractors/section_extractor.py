import re
from src.models.section import Section
from src.models.layout_block import LayoutBlock

class SectionExtractor:
    @staticmethod
    def extract(layout_blocks:list[LayoutBlock])
        sections=[]
        current_title=None
        current_content=[]
        pattern=re.compile(r"^[IVXLC]+\.")
        for block in layout_blocks:
            text=block.text.strip()
            if not text:
                continue
            if pattern.match(text):
                if current_title:
                    sections.appedn(
                        Section(
                            title=current_title,
                            content="\n".join(current_content)
                        )
                    )
                current_title=text
                current_content=[]
            else:
                if current_title:
                    current_content.append(text)
            if current_title:
                sections.append(
                    Section(
                        title=current_title,
                        content="\n".join(current_content)
                    )
                )
            return sections