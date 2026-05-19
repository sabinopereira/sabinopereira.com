#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

from generate_borrow_ebook_pdf import (
    BOOK_DIR,
    COVER_JPG,
    LineIllustration,
    create_cover,
    para,
    parse_sections,
    read_docx_paragraphs,
    SOURCE_DOCX,
)


PAPERBACK_DIR = BOOK_DIR / "paperback"
INTERIOR_PDF = PAPERBACK_DIR / "borrow-delay-repeat-paperback-miolo-kdp.pdf"
COVER_PDF = PAPERBACK_DIR / "borrow-delay-repeat-paperback-capa-kdp.pdf"
METADATA_JSON = BOOK_DIR / "kdp-metadata.json"

TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    for name, path in {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
        "Impact": font_dir / "Impact.ttf",
    }.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def draw_page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFont("Georgia", 9)
    canv.setFillColor(colors.HexColor("#555555"))
    canv.drawCentredString(TRIM_W / 2, 0.42 * inch, str(doc.page))
    canv.restoreState()


def add_blank_page(pdf_path: Path) -> None:
    blank_path = pdf_path.with_suffix(".blank.pdf")
    c = canvas.Canvas(str(blank_path), pagesize=(TRIM_W, TRIM_H))
    c.showPage()
    c.save()

    reader = PdfReader(str(pdf_path))
    blank = PdfReader(str(blank_path)).pages[0]
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_page(blank)
    with pdf_path.open("wb") as handle:
        writer.write(handle)
    blank_path.unlink(missing_ok=True)


def build_interior() -> int:
    title, subtitle, sections = parse_sections(read_docx_paragraphs(SOURCE_DOCX))
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BookTitle", fontName="Impact", fontSize=38, leading=40, alignment=TA_CENTER, textColor=colors.HexColor("#111111")))
    styles.add(ParagraphStyle("BookSubtitle", fontName="Georgia-Italic", fontSize=13, leading=19, alignment=TA_CENTER, textColor=colors.HexColor("#333333")))
    styles.add(ParagraphStyle("Author", fontName="Georgia", fontSize=11, leading=15, alignment=TA_CENTER, spaceBefore=32))
    styles.add(ParagraphStyle("SectionTitle", fontName="Impact", fontSize=25, leading=28, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle("PartTitle", fontName="Georgia-Bold", fontSize=13, leading=18, alignment=TA_CENTER, spaceBefore=10, spaceAfter=14))
    styles.add(ParagraphStyle("BodyBook", fontName="Georgia", fontSize=11.4, leading=17.2, spaceAfter=7.2))
    styles.add(ParagraphStyle("ShortLine", fontName="Georgia-Italic", fontSize=12, leading=18, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle("Toc", fontName="Georgia", fontSize=12, leading=21, spaceAfter=3))
    styles.add(ParagraphStyle("Small", fontName="Georgia", fontSize=9.5, leading=14, alignment=TA_LEFT, textColor=colors.HexColor("#333333")))
    styles.add(ParagraphStyle("EndNote", fontName="Georgia-Italic", fontSize=11, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#333333")))

    doc = BaseDocTemplate(
        str(INTERIOR_PDF),
        pagesize=(TRIM_W, TRIM_H),
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
        title=f"{title} - Paperback Interior",
        author="Sabino Pereira",
    )
    odd = Frame(0.68 * inch, 0.72 * inch, TRIM_W - 1.22 * inch, TRIM_H - 1.42 * inch, id="odd")
    even = Frame(0.54 * inch, 0.72 * inch, TRIM_W - 1.22 * inch, TRIM_H - 1.42 * inch, id="even")
    doc.addPageTemplates(
        [
            PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
            PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
        ]
    )

    story: list = [
        Spacer(1, 2.0 * inch),
        Paragraph("BORROW.<br/>DELAY.<br/>REPEAT.", styles["BookTitle"]),
        Spacer(1, 0.18 * inch),
        para(subtitle, styles["BookSubtitle"]),
        para("Sabino Pereira", styles["Author"]),
        PageBreak(),
        Spacer(1, 2.05 * inch),
        para(title, styles["BookSubtitle"]),
        Spacer(1, 0.28 * inch),
        para("Copyright © 2026 Sabino Pereira. All rights reserved.", styles["Small"]),
        para("This book is satire. It is not financial, legal, or relationship advice.", styles["Small"]),
        Spacer(1, 0.26 * inch),
        para("First paperback edition.", styles["Small"]),
        PageBreak(),
        para("Contents", styles["SectionTitle"]),
    ]
    for section in sections:
        story.append(para(section.title, styles["Toc"]))
    story.append(PageBreak())

    illustration_map = {
        "Chapter 1 - Ask Nicely": "ask",
        "Chapter 2 - Promise Tomorrow": "tomorrow",
        "Chapter 3 - Strategic Disappearance": "disappear",
        "Chapter 4 - Image Control": "image",
        "Chapter 5 - The Follow-up Defense": "defense",
        "Chapter 6 - The Reset": "reset",
    }
    for section in sections:
        story.append(KeepTogether([para(section.title, styles["SectionTitle"])]))
        if section.title in illustration_map:
            story.append(Spacer(1, 0.04 * inch))
            story.append(LineIllustration(illustration_map[section.title], width=4.25 * inch, height=1.55 * inch))
            story.append(Spacer(1, 0.14 * inch))
        for text in section.paragraphs:
            if text == "Part 1 - The Basics":
                story.append(para(text, styles["PartTitle"]))
            elif len(text) <= 34 and not text.endswith(".") and section.kind == "chapter":
                story.append(para(text, styles["ShortLine"]))
            else:
                story.append(para(text, styles["BodyBook"]))
        story.append(PageBreak())

    story.extend([
        Spacer(1, 3.1 * inch),
        para(title, styles["EndNote"]),
        para("End of book.", styles["EndNote"]),
    ])
    doc.build(story)

    page_count = len(PdfReader(str(INTERIOR_PDF)).pages)
    while page_count < 24 or page_count % 2:
        add_blank_page(INTERIOR_PDF)
        page_count += 1
    return page_count


def draw_wrapped_text(canv: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float, color) -> float:
    canv.setFont(font, size)
    canv.setFillColor(color)
    words = text.split()
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if canv.stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            canv.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        canv.drawString(x, y, line)
        y -= leading
    return y


def build_cover(page_count: int) -> dict[str, float]:
    if not COVER_JPG.exists():
        create_cover(COVER_JPG)

    spine = page_count * WHITE_PAPER_SPINE_PER_PAGE
    cover_w = BLEED + TRIM_W + spine + TRIM_W + BLEED
    cover_h = TRIM_H + 2 * BLEED
    back_x = BLEED
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine

    c = canvas.Canvas(str(COVER_PDF), pagesize=(cover_w, cover_h))
    c.setTitle("Borrow. Delay. Repeat. - Paperback Cover")
    c.setAuthor("Sabino Pereira")
    c.setFillColor(colors.HexColor("#111111"))
    c.rect(0, 0, cover_w, cover_h, stroke=0, fill=1)

    c.drawImage(str(COVER_JPG), front_x, 0, width=TRIM_W + BLEED, height=cover_h, preserveAspectRatio=False, mask="auto")

    safe_x = back_x + 0.46 * inch
    y = cover_h - 0.88 * inch
    c.setFont("Impact", 24)
    c.setFillColor(colors.white)
    c.drawString(safe_x, y, "BORROW. DELAY. REPEAT.")
    y -= 0.34 * inch
    c.setStrokeColor(colors.HexColor("#b01f1f"))
    c.setLineWidth(3)
    c.line(safe_x, y, safe_x + 1.7 * inch, y)
    y -= 0.38 * inch

    blurb = (
        "A short satirical guide to the fine art of borrowing money, delaying repayment, "
        "protecting your image, and acting surprised when people remember."
    )
    y = draw_wrapped_text(c, blurb, safe_x, y, TRIM_W - 0.95 * inch, "Georgia", 12.2, 18, colors.HexColor("#eeeeee"))
    y -= 0.22 * inch
    quote = "Not advice. Not a strategy. Definitely not a confession."
    y = draw_wrapped_text(c, quote, safe_x, y, TRIM_W - 1.05 * inch, "Georgia-Italic", 13, 20, colors.white)
    y -= 0.28 * inch
    c.setFont("Georgia", 10)
    c.setFillColor(colors.HexColor("#cfcfcf"))
    c.drawString(safe_x, y, "Sabino Pereira")

    barcode_w = 2.0 * inch
    barcode_h = 1.2 * inch
    c.setFillColor(colors.white)
    c.rect(back_x + TRIM_W - barcode_w - 0.35 * inch, 0.42 * inch, barcode_w, barcode_h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Georgia", 6.5)
    c.drawCentredString(back_x + TRIM_W - barcode_w / 2 - 0.35 * inch, 0.96 * inch, "Barcode KDP")

    if page_count > 79:
        c.saveState()
        c.translate(spine_x + spine / 2, cover_h / 2)
        c.rotate(90)
        c.setFont("Impact", max(6, min(11, spine * 0.42)))
        c.setFillColor(colors.white)
        c.drawCentredString(0, -spine * 0.18, "BORROW. DELAY. REPEAT.")
        c.setFont("Georgia", max(4.5, min(7.2, spine * 0.26)))
        c.drawCentredString(0, spine * 0.26, "SABINO PEREIRA")
        c.restoreState()

    c.showPage()
    c.save()
    return {
        "page_count": page_count,
        "trim_width_in": TRIM_W / inch,
        "trim_height_in": TRIM_H / inch,
        "bleed_in": BLEED / inch,
        "spine_width_in": spine / inch,
        "cover_width_in": cover_w / inch,
        "cover_height_in": cover_h / inch,
    }


def write_metadata(specs: dict[str, float]) -> None:
    metadata = {
        "title": "Borrow. Delay. Repeat.",
        "author": "Sabino Pereira",
        "language": "English",
        "format": "Paperback and Kindle eBook",
        "kdp_setup": {
            "trim_size": "6 x 9 in",
            "interior": "Black & white",
            "paper": "White paper",
            "interior_bleed": "No bleed",
            "cover_finish": "Matte recommended",
            "reading_direction": "Left to Right",
        },
        "files": {
            "paperback_interior_pdf": "paperback/borrow-delay-repeat-paperback-miolo-kdp.pdf",
            "paperback_cover_pdf": "paperback/borrow-delay-repeat-paperback-capa-kdp.pdf",
            "ebook_epub": "ebook/borrow-delay-repeat-kindle-ebook.epub",
            "ebook_cover_jpg": "ebook/borrow-delay-repeat-ebook-cover.jpg",
        },
        "print_specs": specs,
    }
    METADATA_JSON.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    register_fonts()
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    page_count = build_interior()
    specs = build_cover(page_count)
    write_metadata(specs)
    print(json.dumps(specs, indent=2))


if __name__ == "__main__":
    main()
