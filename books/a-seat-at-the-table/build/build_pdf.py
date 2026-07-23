from pathlib import Path
from html import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT.parents[1] / "output" / "pdf" / "a-seat-at-the-table"
OUT = OUT_DIR / "A Seat at the Table - Premium Edition.pdf"
COVER = ROOT / "assets" / "a-seat-at-the-table-cover-premium.png"
CHAPTERS = [ROOT / "source" / f"chapter-{n:02d}-complete.md" for n in range(1, 13)]
EPILOGUE = ROOT / "source" / "epilogue-complete.md"

CHAPTER_TITLES = [
    "The Table", "The First Course", "The Appetite", "The Ace", "The Queen", "The King",
    "The Man in the Apron", "The Nameless Chair", "The Blue Envelope",
    "The Woman on the Stairs", "Losing on Purpose", "The Door",
]

PAGE_W, PAGE_H = 6.25 * inch, 10 * inch
BURGUNDY = colors.HexColor("#5A1F27")
GOLD = colors.HexColor("#A77A35")
INK = colors.HexColor("#171513")
MUTED = colors.HexColor("#514941")
HAIRLINE = colors.HexColor("#DED7CF")

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("Georgia", str(FONT_DIR / "Georgia.ttf")))
pdfmetrics.registerFont(TTFont("Georgia-Italic", str(FONT_DIR / "Georgia Italic.ttf")))
pdfmetrics.registerFont(TTFont("Georgia-Bold", str(FONT_DIR / "Georgia Bold.ttf")))
pdfmetrics.registerFontFamily(
    "Georgia", normal="Georgia", bold="Georgia-Bold",
    italic="Georgia-Italic", boldItalic="Georgia-Bold"
)


class FullPageCover(Flowable):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = str(image_path)
        self.width = PAGE_W
        self.height = PAGE_H

    def wrap(self, avail_width, avail_height):
        return 0, 0

    def draw(self):
        pass


class PremiumDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
            id="main",
        )
        self.addPageTemplates(PageTemplate(id="premium", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.drawImage(
                str(COVER), 0, 0, width=PAGE_W, height=PAGE_H,
                preserveAspectRatio=False, mask="auto",
            )
            canvas.restoreState()
            return
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        if doc.page >= 7:
            canvas.setFont("Georgia", 8)
            canvas.setFillColor(colors.HexColor("#7A716A"))
            canvas.drawCentredString(PAGE_W / 2, 0.42 * inch, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "ChapterTitle":
            text = getattr(flowable, "toc_label", flowable.getPlainText())
            key = f"chapter-{self.seq.nextf('chapter')}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=0, closed=False)
            self.notify("TOCEntry", (0, text, self.page, key))


def clean_markdown(text):
    return text.replace("**", "").replace("*", "").strip()


def prose_blocks(text):
    blocks, buffer = [], []
    chars = 0

    def flush():
        nonlocal buffer, chars
        if buffer:
            blocks.append(("narrative", " ".join(buffer)))
            buffer, chars = [], 0

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "---":
            flush()
            blocks.append(("divider", "•"))
            continue
        marked = (line.startswith("**") and line.endswith("**")) or (
            line.startswith("*") and line.endswith("*")
        )
        plain = clean_markdown(line)
        if line.startswith("“") or line.startswith('"'):
            flush()
            blocks.append(("dialogue", plain))
            continue
        if marked:
            flush()
            blocks.append(("display", plain))
            continue
        buffer.append(plain)
        chars += len(plain)
        if len(buffer) >= 4 or chars >= 420 or plain.endswith(":"):
            flush()
    flush()
    return blocks


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="BookBody", fontName="Georgia", fontSize=10.6, leading=15.5,
    textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=15,
    spaceAfter=5.5, splitLongWords=False, allowWidows=0, allowOrphans=0,
))
styles.add(ParagraphStyle(
    name="Dialogue", parent=styles["BookBody"], firstLineIndent=0,
    alignment=TA_LEFT, spaceAfter=5.2,
))
styles.add(ParagraphStyle(
    name="Display", parent=styles["BookBody"], firstLineIndent=0,
    alignment=TA_CENTER, fontSize=9.7, leading=14.5, textColor=BURGUNDY,
    leftIndent=22, rightIndent=22, spaceBefore=8, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="ChapterTitle", fontName="Georgia", fontSize=20, leading=26,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="ChapterSubtitle", fontName="Georgia-Italic", fontSize=12,
    leading=17, textColor=MUTED, alignment=TA_CENTER, spaceAfter=14,
))
styles.add(ParagraphStyle(
    name="FrontTitle", fontName="Georgia", fontSize=26, leading=32,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=14,
))
styles.add(ParagraphStyle(
    name="FrontHeading", fontName="Georgia", fontSize=18, leading=23,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=18,
))
styles.add(ParagraphStyle(
    name="FrontBody", fontName="Georgia", fontSize=10.2, leading=15,
    textColor=INK, alignment=TA_LEFT, spaceAfter=9,
))
styles.add(ParagraphStyle(
    name="Centered", parent=styles["FrontBody"], alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="Epigraph", parent=styles["Centered"], fontName="Georgia-Italic",
    fontSize=12, leading=18, leftIndent=28, rightIndent=28,
))
styles.add(ParagraphStyle(
    name="TOCHeading", fontName="Georgia", fontSize=20, leading=25,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=20,
))


def add_chapter_opener(story, label, subtitle):
    story.append(PageBreak())
    story.append(Spacer(1, 2.72 * inch))
    story.append(Paragraph("•", ParagraphStyle(
        "Ornament", fontName="Georgia", fontSize=8, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=10,
    )))
    heading = Paragraph(escape(label), styles["ChapterTitle"])
    heading.toc_label = f"{label} - {subtitle}"
    story.append(heading)
    story.append(Paragraph(escape(subtitle), styles["ChapterSubtitle"]))
    story.append(Table([[""]], colWidths=[0.78 * inch], rowHeights=[0.5], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GOLD),
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, GOLD),
    ])))
    story.append(PageBreak())


def add_book_text(story, source):
    first = True
    for kind, text in prose_blocks(source.read_text(encoding="utf-8")):
        if kind == "divider":
            story.append(Spacer(1, 9))
            story.append(Paragraph("•", ParagraphStyle(
                "SceneBreak", fontName="Georgia", fontSize=7, textColor=GOLD,
                alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
            )))
            story.append(Spacer(1, 9))
            first = False
            continue
        style = styles["BookBody"]
        if kind == "dialogue":
            style = styles["Dialogue"]
        elif kind == "display":
            style = styles["Display"]
        p = Paragraph(escape(text), style)
        if first and kind == "narrative":
            p.style = ParagraphStyle("OpeningParagraph", parent=styles["BookBody"], firstLineIndent=0)
        story.append(p)
        first = False


def build_story():
    story = [FullPageCover(COVER), PageBreak()]

    story += [
        Spacer(1, 3.25 * inch),
        Paragraph("A SEAT AT THE TABLE", styles["FrontTitle"]),
        Paragraph("SABINO PEREIRA", ParagraphStyle(
            "Author", fontName="Georgia", fontSize=12, leading=16,
            textColor=GOLD, alignment=TA_CENTER, spaceBefore=4,
        )),
        PageBreak(),
        Spacer(1, 0.7 * inch),
        Paragraph("Copyright", styles["FrontHeading"]),
        Paragraph("<i>A Seat at the Table</i>", styles["FrontBody"]),
        Paragraph("Copyright © 2026 Sabino Pereira", styles["FrontBody"]),
        Paragraph("All rights reserved.", styles["FrontBody"]),
        Paragraph("No part of this publication may be reproduced, stored, or transmitted in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without the author's prior written permission, except for brief quotations used in reviews or critical articles.", styles["FrontBody"]),
        Paragraph("This is a work of fiction. Names, characters, organizations, events, and places are either products of the author's imagination or used fictitiously. Any resemblance to actual persons, living or dead, or to actual events is purely coincidental.", styles["FrontBody"]),
        Paragraph("Premium English edition<br/>First digital edition, 2026", styles["FrontBody"]),
        PageBreak(),
        Spacer(1, 3.05 * inch),
        Paragraph("For everyone who has ever mistaken a seat at the table for a place in the world.", styles["Centered"]),
        PageBreak(),
        Spacer(1, 2.9 * inch),
        Paragraph("Some people spend their entire lives earning a seat without ever asking who had to stand up.", styles["Epigraph"]),
        PageBreak(),
        Spacer(1, 0.55 * inch),
        Paragraph("Contents", styles["TOCHeading"]),
    ]

    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle(
        "TOCLevel1", fontName="Georgia", fontSize=10.2, leading=17,
        leftIndent=0, firstLineIndent=0, textColor=INK,
        spaceBefore=2, spaceAfter=2,
    )]
    story += [toc, PageBreak(), Spacer(1, 0.7 * inch), Paragraph("A Note to the Reader", styles["FrontHeading"])]
    note = [
        "We all believe we know who we are.",
        "Until a choice forces us to discover whom we are willing to sacrifice.",
        "This story begins with a dinner.",
        "Around the table sit people accustomed to power, success, and control. Each believes they know the truth about their own life. Each carries a secret they would rather leave buried.",
        "Over the course of the evening, the cards will be dealt.",
        "Not to decide who wins.",
        "But to reveal who each of them has always been.",
        "Welcome to <i>A Seat at the Table</i>.",
    ]
    story.extend(Paragraph(p, styles["FrontBody"]) for p in note)

    for n, source in enumerate(CHAPTERS, 1):
        add_chapter_opener(story, f"CHAPTER {n}", CHAPTER_TITLES[n - 1])
        add_book_text(story, source)

    add_chapter_opener(story, "EPILOGUE", "When No One Is Watching")
    add_book_text(story, EPILOGUE)
    return story


OUT_DIR.mkdir(parents=True, exist_ok=True)
doc = PremiumDocTemplate(
    str(OUT), pagesize=portrait((PAGE_W, PAGE_H)),
    leftMargin=0.74 * inch, rightMargin=0.74 * inch,
    topMargin=0.78 * inch, bottomMargin=0.72 * inch,
    title="A Seat at the Table", author="Sabino Pereira",
    subject="Premium English edition",
)
doc.multiBuild(build_story())
print(OUT)
