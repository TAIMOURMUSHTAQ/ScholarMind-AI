"""Chat transcript export as Markdown or PDF.

PDF export uses fpdf2 (pure Python, no native build dependency - the same
class of Windows wheel problem that pushed the vector store from ChromaDB
to FAISS ruled out heavier PDF libraries here). fpdf2's built-in core
fonts only cover Latin-1, so full Unicode support (curly quotes, en/em
dashes, non-Latin scripts, math symbols) needs an embedded TrueType font;
this bundles DejaVu Sans (`assets/fonts/`, Bitstream Vera-derived license,
the same font matplotlib ships for the identical reason) rather than
degrading unsupported characters. The Markdown export was never limited
this way.
"""
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def _speaker(role: str) -> str:
    return "You" if role == "user" else "ScholarMind AI"


def build_markdown(title: str, turns: list[dict]) -> str:
    lines = [f"# Chat transcript: {title}", "", f"_Exported {datetime.now(timezone.utc).isoformat()}_", ""]
    for turn in turns:
        lines.append(f"**{_speaker(turn['role'])}:** {turn['content']}")
        for source in turn.get("sources", []):
            label = source.get("paper_title")
            prefix = f"{label} - " if label else ""
            lines.append(
                f"> Source {source['rank']}: {prefix}{source['section_title']} "
                f"(pages {source['page_start']}-{source['page_end']})"
            )
        lines.append("")
    return "\n".join(lines)


def _register_fonts(pdf: FPDF) -> None:
    pdf.add_font("DejaVu", "", str(FONT_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_font("DejaVu", "I", str(FONT_DIR / "DejaVuSans-Oblique.ttf"))
    pdf.add_font("DejaVu", "BI", str(FONT_DIR / "DejaVuSans-BoldOblique.ttf"))


def _line(pdf: FPDF, height: float, text: str) -> None:
    """multi_cell that resets the cursor to the left margin afterwards.

    fpdf2's multi_cell defaults to leaving the cursor at the cell's right
    edge (new_x=XPos.RIGHT); with a full-width (w=0) cell that's the page's
    right margin, so the very next multi_cell call has zero width left and
    raises FPDFException. Every call here must reset back to the margin.
    """
    pdf.multi_cell(0, height, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(title: str, turns: list[dict]) -> bytes:
    pdf = FPDF()
    _register_fonts(pdf)
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 14)
    _line(pdf, 10, f"Chat transcript: {title}")
    pdf.set_font("DejaVu", "I", 8)
    _line(pdf, 5, f"Exported {datetime.now(timezone.utc).isoformat()}")
    pdf.ln(3)

    for turn in turns:
        pdf.set_font("DejaVu", "B", 11)
        _line(pdf, 7, _speaker(turn["role"]))
        pdf.set_font("DejaVu", "", 10)
        _line(pdf, 6, turn["content"])
        for source in turn.get("sources", []):
            label = source.get("paper_title")
            prefix = f"{label} - " if label else ""
            pdf.set_font("DejaVu", "I", 9)
            _line(
                pdf, 5,
                f"Source {source['rank']}: {prefix}{source['section_title']} "
                f"(pages {source['page_start']}-{source['page_end']})",
            )
        pdf.ln(3)

    return bytes(pdf.output())
