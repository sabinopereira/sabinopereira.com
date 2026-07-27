#!/usr/bin/env python3
"""Build the 6 x 9 in KDP premium-colour paperback interior with bleed."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from reportlab.lib.pagesizes import inch


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = ROOT / "scripts" / "build_premium_pdf.py"
OUTPUT = ROOT / "amazon-kdp" / "paperback" / "interior" / "echoes-of-childhood-paperback-interior-kdp.pdf"


def load_builder():
    spec = spec_from_file_location("memory_book_builder", SOURCE_SCRIPT)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    builder = load_builder()

    def draw_print_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(builder.IVORY)
        canvas.rect(0, 0, builder.PAGE_W, builder.PAGE_H, fill=1, stroke=0)
        if doc.page > 4:
            canvas.setFillColor(builder.GOLD)
            canvas.setFont("Georgia", 8)
            # KDP bleed pages need all live type at least 0.5 in from
            # the PDF edge at the foot; 0.58 in clears the safety line.
            canvas.drawCentredString(builder.PAGE_W / 2, 0.58 * inch, str(doc.page))
        canvas.restoreState()

    # KDP full-bleed page size for a 6 x 9 inch trim.
    builder.PAGE_W = 6.125 * inch
    builder.PAGE_H = 9.25 * inch
    builder.draw_page = draw_print_page
    builder.OUTPUT = OUTPUT
    builder.COVER = ROOT / "assets" / "cover" / "echoes-of-childhood-memory-book-cover-print-1850x2775.jpg"
    builder.CHAPTER_IMAGES = {
        name: ROOT / "assets" / "illustrations-print-jpeg" / (path.stem + ".jpg")
        for name, path in builder.CHAPTER_IMAGES.items()
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    builder.build()


if __name__ == "__main__":
    main()
