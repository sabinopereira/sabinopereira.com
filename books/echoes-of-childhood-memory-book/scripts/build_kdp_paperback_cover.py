#!/usr/bin/env python3
"""Build the KDP paperback wrap cover for 64-page premium colour stock."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / "assets" / "cover" / "echoes-of-childhood-memory-book-cover-print-1850x2775.jpg"
OUTPUT = ROOT / "amazon-kdp" / "paperback" / "cover" / "echoes-of-childhood-paperback-cover-kdp.pdf"

TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
PAGE_COUNT = 62
SPINE_IN = PAGE_COUNT * 0.002347
SPINE = SPINE_IN * inch
FULL_W = BLEED + TRIM_W + SPINE + TRIM_W + BLEED
FULL_H = BLEED + TRIM_H + BLEED

PAPER = HexColor("#F0E2C9")
INK = HexColor("#182331")
SEPIA = HexColor("#8E6237")
GOLD = HexColor("#B68142")
DARK = HexColor("#1B140F")

pdfmetrics.registerFont(TTFont("Georgia", "/System/Library/Fonts/Supplemental/Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Italic", "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"))


def draw_fitted_paragraph(c, text, style, x, y_top, width, height):
    paragraph = Paragraph(text, style)
    _, used_h = paragraph.wrap(width, height)
    paragraph.drawOn(c, x, y_top - used_h)
    return used_h


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(FULL_W, FULL_H), pageCompression=1)
    c.setTitle("Echoes of Childhood - Paperback Cover")
    c.setAuthor("Sabino Pereira")

    # Continuous parchment base across back, spine and front bleed.
    c.setFillColor(PAPER)
    c.rect(0, 0, FULL_W, FULL_H, fill=1, stroke=0)

    # Back cover: warm vignette and restrained memory-box geometry.
    back_x = BLEED
    back_y = BLEED
    c.setFillColor(DARK)
    c.rect(0, 0, BLEED + TRIM_W + SPINE, FULL_H, fill=1, stroke=0)
    c.setFillColor(HexColor("#2B2118"))
    c.circle(1.05 * inch, 7.95 * inch, 1.55 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#352719"))
    c.circle(5.4 * inch, 1.1 * inch, 1.85 * inch, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#75522F"))
    c.setLineWidth(0.6)
    for offset in (0.52, 0.66, 0.8):
        c.rect(back_x + offset * inch, back_y + offset * inch,
               TRIM_W - 2 * offset * inch, TRIM_H - 2 * offset * inch,
               fill=0, stroke=1)

    quote_style = ParagraphStyle(
        "Quote", fontName="Georgia-Italic", fontSize=20, leading=26,
        textColor=PAPER, alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "Body", fontName="Georgia", fontSize=10.1, leading=15.2,
        textColor=HexColor("#E6D6BC"), alignment=TA_LEFT,
    )
    credit_style = ParagraphStyle(
        "Credit", fontName="Georgia-Bold", fontSize=8.3, leading=12,
        textColor=GOLD, alignment=TA_LEFT,
    )

    safe_x = back_x + 0.62 * inch
    text_w = 4.62 * inch
    y = FULL_H - 0.85 * inch
    y -= draw_fitted_paragraph(
        c,
        "We didn&rsquo;t know we were making memories.<br/>We thought we were simply living.",
        quote_style, safe_x, y, text_w, 1.2 * inch,
    )
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(safe_x, y - 0.2 * inch, safe_x + 0.9 * inch, y - 0.2 * inch)
    y -= 0.55 * inch
    blurb = (
        "Childhood rarely announces the moments that will stay with us. A Saturday morning. "
        "A favourite toy. The sound of friends outside. A hand reaching for ours before we knew "
        "how much safety mattered.<br/><br/>"
        "<i>Echoes of Childhood</i> is an invitation to return to those ordinary moments and "
        "discover why they became extraordinary with time. Across twelve reflective chapters, "
        "Sabino Pereira explores wonder, friendship, growing up, gratitude and the people who "
        "made the world feel like home.<br/><br/>"
        "Created as a visual companion to the cinematic instrumental album by Reira Bin, this is "
        "not a story about one childhood. It is a quiet space in which to remember your own."
    )
    y -= draw_fitted_paragraph(c, blurb, body_style, safe_x, y, text_w, 4.2 * inch)
    y -= 0.38 * inch
    draw_fitted_paragraph(
        c, "WRITTEN BY SABINO PEREIRA<br/>MUSIC BY RB / REIRA BIN",
        credit_style, safe_x, y, text_w, 0.5 * inch,
    )

    # Quiet object marks, kept away from the automatic barcode zone.
    c.setStrokeColor(HexColor("#A67A43"))
    c.setLineWidth(1.2)
    c.circle(back_x + 0.9 * inch, back_y + 0.72 * inch, 0.12 * inch, fill=0, stroke=1)
    c.line(back_x + 1.02 * inch, back_y + 0.72 * inch,
           back_x + 1.46 * inch, back_y + 0.72 * inch)

    # Automatic KDP barcode reserve: lower-right of the back cover.
    barcode_w = 2.0 * inch
    barcode_h = 1.2 * inch
    barcode_x = back_x + TRIM_W - barcode_w - 0.25 * inch
    barcode_y = back_y + 0.25 * inch
    c.setFillColor(PAPER)
    c.roundRect(barcode_x, barcode_y, barcode_w, barcode_h, 3, fill=1, stroke=0)

    # Narrow spine: colour only. KDP rejects spine text below 79 pages.
    spine_x = BLEED + TRIM_W
    c.setFillColor(HexColor("#17120E"))
    c.rect(spine_x, 0, SPINE, FULL_H, fill=1, stroke=0)

    # Front cover extends through the right bleed.
    front_x = BLEED + TRIM_W + SPINE
    c.drawImage(
        ImageReader(str(FRONT)), front_x, 0,
        width=TRIM_W + BLEED, height=FULL_H,
        preserveAspectRatio=False, mask="auto",
    )

    c.showPage()
    c.save()
    print(OUTPUT)
    print(f"spine={SPINE_IN:.6f}in full_cover={FULL_W/inch:.6f}x{FULL_H/inch:.2f}in")


if __name__ == "__main__":
    main()
