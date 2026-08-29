"""Extracts embedded raster figures/charts from a PDF, with a lightweight
caption heuristic (first "Figure N" / "Table N" text block on the same
page). This is a page-level association, not a precise spatial match
between an image and its caption - acceptable for a "browse the figures"
panel, and callers should treat captions as best-effort labels.
"""
import re
from pathlib import Path

MIN_DIMENSION_PX = 120  # filters out small icons/logos/decorative rules
CAPTION_PATTERN = re.compile(r"^(figure|fig\.?|table)\s*\d+", re.IGNORECASE)


class FigureExtractor:
    @staticmethod
    def extract(doc, output_dir: Path) -> list[dict]:
        output_dir.mkdir(parents=True, exist_ok=True)
        figures: list[dict] = []
        index = 0

        for page_number in range(doc.page_count):
            page = doc[page_number]
            caption = FigureExtractor._first_caption_on_page(page)

            for image_info in page.get_images(full=True):
                xref = image_info[0]
                try:
                    base_image = doc.extract_image(xref)
                except Exception:
                    continue

                width, height = base_image.get("width", 0), base_image.get("height", 0)
                if width < MIN_DIMENSION_PX or height < MIN_DIMENSION_PX:
                    continue

                ext = base_image.get("ext", "png")
                figure_id = str(index)
                (output_dir / f"{figure_id}.{ext}").write_bytes(base_image["image"])

                figures.append({"id": figure_id, "page": page_number, "ext": ext, "caption": caption})
                index += 1

        return figures

    @staticmethod
    def _first_caption_on_page(page) -> str:
        for block in page.get_text("blocks"):
            text = block[4].strip()
            if CAPTION_PATTERN.match(text):
                return text.split("\n")[0][:200]
        return ""
