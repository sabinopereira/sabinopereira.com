#!/usr/bin/env python3
"""Build Amazon KDP paperback interiors and full-wrap covers for the series."""

from __future__ import annotations

import html
import json
import runpy
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paperback"
MODULE = runpy.run_path(str(Path(__file__).with_name("build-prose-premium-editions.py")))
BOOKS = MODULE["BOOKS"]
markdown_sections = MODULE["markdown_sections"]
epub_sections = MODULE["epub_sections"]
section_content = MODULE["section_content"]

AUTHOR = "Sabino Pereira"
TRIM_W, TRIM_H = 6 * inch, 9 * inch
BLEED = 0.125 * inch
GROUNDWOOD_SPINE_PER_PAGE = 0.00235 * inch
INK = colors.HexColor("#22191c")
WINE = colors.HexColor("#6f2434")
ROSE = colors.HexColor("#b87682")
MUTED = colors.HexColor("#74686a")

BLURBS = {
    "selah": "Selah was taught that goodness meant obedience, silence, and sacrifice. But when the life she built begins to feel like a cage, she must decide whether freedom is betrayal - or the first honest thing she has ever chosen.",
    "diana": "Diana knows how to look devoted while quietly disappearing. A marriage, a reputation, and a carefully managed life force her to confront the difference between being chosen and being free.",
    "noa": "Noa has survived by answering to the names other people gave her. To reclaim her own voice, she must face the cost of belonging, ambition, and the identity she built to stay safe.",
    "naomi": "Naomi learned early that money could mean food, safety, dignity, and escape. Called heartless for refusing dependence, she must discover whether security can protect her without turning her into stone.",
}


class EmbeddedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("initialFontName", "Georgia")
        super().__init__(*args, **kwargs)


def register_fonts() -> None:
    folder = Path("/System/Library/Fonts/Supplemental")
    for name, filename in {
        # ReportLab emits an initial Helvetica text-state command in Platypus
        # documents. Register it to an embedded font so KDP sees no base-14
        # font dependency, even though that initial command draws no text.
        "Helvetica": "Georgia.ttf",
        "Georgia": "Georgia.ttf",
        "Georgia-Bold": "Georgia Bold.ttf",
        "Georgia-Italic": "Georgia Italic.ttf",
    }.items():
        pdfmetrics.registerFont(TTFont(name, str(folder / filename)))


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("Title", parent=base["Title"], fontName="Georgia-Bold", fontSize=24, leading=30, textColor=WINE, alignment=TA_CENTER, spaceAfter=16),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName="Georgia-Italic", fontSize=12, leading=18, textColor=ROSE, alignment=TA_CENTER),
        "author": ParagraphStyle("Author", parent=base["Normal"], fontName="Georgia-Bold", fontSize=11, textColor=INK, alignment=TA_CENTER, spaceBefore=26),
        "heading": ParagraphStyle("Heading", parent=base["Heading1"], fontName="Georgia-Bold", fontSize=19, leading=24, textColor=WINE, alignment=TA_CENTER, spaceAfter=8),
        "subheading": ParagraphStyle("Subheading", parent=base["Normal"], fontName="Georgia-Italic", fontSize=11, leading=16, textColor=ROSE, alignment=TA_CENTER, spaceAfter=24),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Georgia", fontSize=10.5, leading=15.8, textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=16, spaceAfter=7.5),
        "first": ParagraphStyle("First", parent=base["Normal"], fontName="Georgia", fontSize=10.5, leading=15.8, textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=0, spaceAfter=7.5),
        "verse": ParagraphStyle("Verse", parent=base["Normal"], fontName="Georgia", fontSize=10.4, leading=16, textColor=INK, leftIndent=14, rightIndent=8, spaceAfter=12),
        "internal": ParagraphStyle("Internal", parent=base["Heading3"], fontName="Georgia-Bold", fontSize=11.2, leading=15, textColor=WINE, alignment=TA_LEFT, spaceBefore=14, spaceAfter=7),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Georgia", fontSize=8.8, leading=13.5, textColor=MUTED, spaceAfter=9),
    }


def page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFillColor(MUTED)
    canv.setFont("Georgia", 8)
    x = 0.68 * inch if doc.page % 2 == 0 else TRIM_W - 0.68 * inch
    draw = canv.drawString if doc.page % 2 == 0 else canv.drawRightString
    draw(x, 0.42 * inch, str(doc.page))
    canv.restoreState()


def build_interior(book, sections, output: Path) -> int:
    st = styles()
    doc = BaseDocTemplate(str(output), pagesize=(TRIM_W, TRIM_H), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0, title=book.title, author=AUTHOR)
    odd = Frame(0.72 * inch, 0.68 * inch, TRIM_W - 1.34 * inch, TRIM_H - 1.34 * inch, id="odd")
    even = Frame(0.62 * inch, 0.68 * inch, TRIM_W - 1.34 * inch, TRIM_H - 1.34 * inch, id="even")
    doc.addPageTemplates([
        PageTemplate(id="Odd", frames=[odd], onPage=page_number, autoNextPageTemplate="Even"),
        PageTemplate(id="Even", frames=[even], onPage=page_number, autoNextPageTemplate="Odd"),
    ])
    story = [
        Spacer(1, 1.65 * inch), Paragraph(book.title, st["title"]), Paragraph(book.subtitle, st["subtitle"]), Paragraph(AUTHOR, st["author"]), PageBreak(),
        Spacer(1, 1.05 * inch), Paragraph("Copyright", st["heading"]),
        Paragraph("Copyright © 2026 Sabino Pereira. All rights reserved.", st["small"]),
        Paragraph("No part of this publication may be reproduced, stored, distributed, or transmitted in any form or by any means without prior written permission, except for brief quotations used in reviews.", st["small"]),
        Paragraph("This is a work of fiction. Names, characters, places, institutions, and incidents are products of the author's imagination or are used fictitiously.", st["small"]),
        Paragraph("First paperback edition, 2026", st["small"]), PageBreak(),
    ]
    for section in sections:
        story.extend([Spacer(1, 0.55 * inch), Paragraph(html.escape(section.heading), st["heading"])])
        story.append(Paragraph(html.escape(section.subtitle), st["subheading"]) if section.subtitle else Spacer(1, 12))
        first = True
        for content, kind in section_content(section):
            if content:
                story.append(Paragraph(content, st["verse"] if kind == "verse" else st["internal"] if kind == "internal" else st["first"] if first else st["body"]))
                if kind == "internal":
                    # Keep short internal headings visually separate even when
                    # they land close to a page break or a tightly filled line.
                    story.append(Spacer(1, 3))
                if kind == "prose":
                    first = False
        story.append(PageBreak())
    story.extend([Spacer(1, 1.1 * inch), Paragraph("About the Author", st["heading"]), Paragraph("Sabino Pereira creates fiction, reflective books, music, and work about behavior, healing, discernment, faith, and modern life.", st["first"]), Paragraph("sabinopereira.com", st["subtitle"])])
    doc.build(story, canvasmaker=EmbeddedCanvas)
    reader = PdfReader(str(output))
    if len(reader.pages) % 2:
        blank_path = output.with_suffix(".blank.pdf")
        blank = EmbeddedCanvas(str(blank_path), pagesize=(TRIM_W, TRIM_H)); blank.showPage(); blank.save()
        writer = PdfWriter()
        for page in reader.pages: writer.add_page(page)
        writer.add_page(PdfReader(str(blank_path)).pages[0])
        with output.open("wb") as handle: writer.write(handle)
        blank_path.unlink()
    return len(PdfReader(str(output)).pages)


def draw_wrapped(c: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float) -> float:
    c.setFont(font, size)
    words, line = text.split(), ""
    for word in words + [None]:
        candidate = f"{line} {word}".strip() if word else ""
        if word and c.stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            if line: c.drawString(x, y, line); y -= leading
            line = word or ""
    return y


def build_cover(book, pages: int, output: Path) -> dict[str, float]:
    spine = pages * GROUNDWOOD_SPINE_PER_PAGE
    width = 2 * BLEED + 2 * TRIM_W + spine
    height = TRIM_H + 2 * BLEED
    back_x, spine_x, front_x = BLEED, BLEED + TRIM_W, BLEED + TRIM_W + spine
    c = EmbeddedCanvas(str(output), pagesize=(width, height), pageCompression=1)
    c.setTitle(f"{book.title} - KDP Paperback Cover"); c.setAuthor(AUTHOR)
    c.setFillColor(colors.HexColor("#21171a")); c.rect(0, 0, width, height, fill=1, stroke=0)
    if book.slug == "diana":
        # Diana's original front artwork contains text close to the outer edge.
        # Frame the complete artwork inside the 0.375 in KDP safe zone instead
        # of cropping it, then redraw the author name clearly for QA/OCR.
        safe_front_w = TRIM_W - 0.75 * inch
        safe_front_h = safe_front_w * 1.5
        safe_front_x = front_x + 0.375 * inch
        safe_front_y = BLEED + (TRIM_H - safe_front_h) / 2
        c.drawImage(str(book.cover), safe_front_x, safe_front_y, width=safe_front_w, height=safe_front_h, preserveAspectRatio=False, mask="auto")
        author_band_y = safe_front_y
        c.setFillColor(colors.HexColor("#21171a"))
        c.rect(safe_front_x, author_band_y, safe_front_w, 0.78 * inch, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#fbf5ed"))
        c.setFont("Georgia-Bold", 11)
        c.drawCentredString(safe_front_x + safe_front_w / 2, author_band_y + 0.30 * inch, AUTHOR)
    else:
        c.drawImage(str(book.cover), front_x, 0, width=TRIM_W + BLEED, height=height, preserveAspectRatio=False, mask="auto")
    safe_x = back_x + 0.48 * inch
    y = height - 0.88 * inch
    c.setFillColor(colors.HexColor("#fbf5ed")); c.setFont("Georgia-Bold", 20)
    y = draw_wrapped(c, book.title, safe_x, y, TRIM_W - 0.96 * inch, "Georgia-Bold", 20, 25)
    y -= 0.25 * inch
    c.setStrokeColor(ROSE); c.setLineWidth(1); c.line(safe_x, y, safe_x + 1.3 * inch, y); y -= 0.38 * inch
    c.setFillColor(colors.HexColor("#eee5dd")); y = draw_wrapped(c, BLURBS[book.slug], safe_x, y, TRIM_W - 0.96 * inch, "Georgia", 11.2, 17)
    y -= 0.25 * inch
    c.setFillColor(ROSE)
    draw_wrapped(c, book.subtitle, safe_x, y, TRIM_W - 0.96 * inch, "Georgia-Italic", 9.5, 14)
    c.setFillColor(colors.white); c.rect(back_x + TRIM_W - 2.35 * inch, 0.42 * inch, 2 * inch, 1.2 * inch, fill=1, stroke=0)
    # KDP requires clear space on both sides of spine text. The two shortest
    # volumes are too narrow for safe 7 pt lettering, so their spines stay clean.
    if spine / inch >= 0.23:
        c.saveState(); c.translate(spine_x + spine / 2, height / 2); c.rotate(90)
        c.setFillColor(colors.HexColor("#fbf5ed")); c.setFont("Georgia-Bold", 7); c.drawCentredString(0, -2, book.title)
        c.restoreState()
    c.showPage(); c.save()
    return {"pages": pages, "trim_width_in": 6, "trim_height_in": 9, "paper": "groundwood", "interior_bleed": False, "cover_bleed_in": 0.125, "spine_width_in": spine / inch, "cover_width_in": width / inch, "cover_height_in": height / inch}


def main() -> None:
    register_fonts(); summary = {}
    for book in BOOKS:
        sections = epub_sections(book.source) if book.source.suffix == ".epub" else markdown_sections(book.source)
        folder = OUT / book.slug; folder.mkdir(parents=True, exist_ok=True)
        interior = folder / f"bad-girl-gospel-{book.slug}-paperback-interior-kdp.pdf"
        cover = folder / f"bad-girl-gospel-{book.slug}-paperback-cover-kdp.pdf"
        pages = build_interior(book, sections, interior)
        summary[book.slug] = build_cover(book, pages, cover)
        (folder / "kdp-specs.json").write_text(json.dumps(summary[book.slug], indent=2) + "\n", encoding="utf-8")
        (folder / "README.txt").write_text(
            f"""{book.title.upper()} - AMAZON KDP PAPERBACK

Upload interior: {interior.name}
Upload cover: {cover.name}

KDP settings
- Trim size: 6 x 9 in
- Interior: black and white
- Paper: groundwood
- Interior bleed: no bleed
- Cover bleed: included (0.125 in)
- Page count: {pages}
- Reading direction: left to right
- Cover finish: matte recommended

Review the files in KDP Print Previewer before publishing.
""",
            encoding="utf-8",
        )
        print(book.slug, json.dumps(summary[book.slug]))
    (OUT / "kdp-paperback-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
