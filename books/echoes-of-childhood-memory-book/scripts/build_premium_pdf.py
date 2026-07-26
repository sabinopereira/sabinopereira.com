#!/usr/bin/env python3
from pathlib import Path
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Flowable
)

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "echoes-of-childhood-final-manuscript.md"
COVER = ROOT / "assets" / "cover" / "echoes-of-childhood-memory-book-cover-prototype-1800x2700.png"
CH1_IMAGE = ROOT / "assets" / "illustrations" / "01-before-the-world-got-loud-style-proof.png"
OUTPUT = ROOT / "output" / "echoes-of-childhood-memory-book-premium-prototype.pdf"

PAGE_W, PAGE_H = 6 * inch, 9 * inch
IVORY = HexColor("#F3E8D0")
NAVY = HexColor("#111B2D")
SEPIA = HexColor("#9B7345")
GOLD = HexColor("#B18A4A")
CHARCOAL = HexColor("#292722")

pdfmetrics.registerFont(TTFont("Georgia", "/System/Library/Fonts/Supplemental/Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Italic", "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-BoldItalic", "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf"))
pdfmetrics.registerFontFamily(
    "Georgia", normal="Georgia", bold="Georgia-Bold",
    italic="Georgia-Italic", boldItalic="Georgia-BoldItalic"
)


class MemoryBookDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=(PAGE_W, PAGE_H),
            leftMargin=0.82 * inch,
            rightMargin=0.72 * inch,
            topMargin=0.72 * inch,
            bottomMargin=0.68 * inch,
            title="Echoes of Childhood - A Memory Book",
            author="Sabino Pereira",
            subject="Premium prototype",
        )
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            PAGE_W - self.leftMargin - self.rightMargin,
            PAGE_H - self.topMargin - self.bottomMargin,
            id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
        )
        self.addPageTemplates([PageTemplate(id="book", frames=frame, onPage=draw_page)])


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(IVORY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if doc.page > 4:
        canvas.setFillColor(GOLD)
        canvas.setFont("Georgia", 8)
        canvas.drawCentredString(PAGE_W / 2, 0.32 * inch, str(doc.page))
    canvas.restoreState()


class FullPageImage(Flowable):
    def __init__(self, path):
        super().__init__()
        self.path = str(path)

    def wrap(self, avail_width, avail_height):
        return 0, 0

    def drawOn(self, canvas, x, y, _sW=0):
        canvas.drawImage(
            ImageReader(self.path), 0, 0, width=PAGE_W, height=PAGE_H,
            preserveAspectRatio=False, mask="auto"
        )


def full_page_image(path):
    return FullPageImage(path)


def split_sections(text):
    matches = list(re.finditer(r"(?m)^# (.+)$", text))
    sections = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[start:end].strip()))
    return sections


def clean_inline(text):
    text = text.strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = text.replace(" — ", " - ")
    return text


styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body", fontName="Georgia", fontSize=10.3, leading=15.1,
    textColor=CHARCOAL, alignment=TA_LEFT, spaceAfter=8.5,
    firstLineIndent=0, allowWidows=0, allowOrphans=0,
)
BODY_FIRST = ParagraphStyle("BodyFirst", parent=BODY, firstLineIndent=0)
SMALL_CAP = ParagraphStyle(
    "SmallCap", fontName="Georgia", fontSize=8, leading=10,
    textColor=GOLD, alignment=TA_CENTER, spaceAfter=10,
)
TITLE = ParagraphStyle(
    "Title", fontName="Georgia", fontSize=30, leading=33,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=12,
)
CHAPTER_NO = ParagraphStyle(
    "ChapterNo", fontName="Georgia", fontSize=9, leading=12,
    textColor=GOLD, alignment=TA_CENTER, spaceAfter=18,
)
CHAPTER_TITLE = ParagraphStyle(
    "ChapterTitle", fontName="Georgia", fontSize=25, leading=29,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=14,
)
SUBTITLE = ParagraphStyle(
    "Subtitle", fontName="Georgia-Italic", fontSize=11, leading=15,
    textColor=SEPIA, alignment=TA_CENTER, spaceAfter=16,
)
FRAGMENT = ParagraphStyle(
    "Fragment", fontName="Georgia-Italic", fontSize=12, leading=18,
    textColor=NAVY, alignment=TA_CENTER, leftIndent=20, rightIndent=20,
    spaceBefore=12, spaceAfter=18,
)
SECTION_TITLE = ParagraphStyle(
    "SectionTitle", fontName="Georgia", fontSize=24, leading=29,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=22,
)
FINAL = ParagraphStyle(
    "Final", fontName="Georgia-Bold", fontSize=17, leading=25,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=16,
)
FINAL_ITALIC = ParagraphStyle(
    "FinalItalic", fontName="Georgia-Italic", fontSize=13, leading=20,
    textColor=SEPIA, alignment=TA_CENTER,
)
CONTENTS = ParagraphStyle(
    "Contents", fontName="Georgia", fontSize=9.5, leading=16,
    textColor=CHARCOAL, alignment=TA_LEFT, leftIndent=12,
)


def paragraphs_from_body(body):
    body = re.sub(r"(?m)^## .+$", "", body)
    body = re.sub(r"(?m)^### Memory Fragment$", "", body)
    body = re.sub(r"(?m)^> .+$", "", body)
    body = re.sub(r"(?m)^\*.+\*$", "", body)
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
    return [b for b in blocks if b != "---"]


def chapter_meta(name, body):
    title_match = re.search(r"(?m)^## (.+)$", body)
    subtitle_match = re.search(r"(?m)^\*(.+)\*$", body)
    fragment_match = re.search(r"(?m)^> [“\"](.+?)[”\"]$", body)
    return (
        title_match.group(1).strip() if title_match else name,
        subtitle_match.group(1).strip() if subtitle_match else "",
        fragment_match.group(1).strip() if fragment_match else "",
    )


def add_prose(story, blocks):
    for block in blocks:
        if block.startswith("**") and block.endswith("**"):
            story.append(Paragraph(clean_inline(block), ParagraphStyle(
                "Signature", parent=BODY, alignment=TA_RIGHT, spaceBefore=16
            )))
        else:
            story.append(Paragraph(clean_inline(block), BODY_FIRST))


def build():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    sections = split_sections(text)
    story = []

    story.append(full_page_image(COVER))
    story.append(PageBreak())
    story.extend([Spacer(1, 2.0 * inch), Paragraph("ECHOES OF CHILDHOOD", TITLE),
                  Paragraph("A MEMORY BOOK", SMALL_CAP), Spacer(1, 0.45 * inch),
                  Paragraph("Music by RB", SUBTITLE), Paragraph("Written by Sabino Pereira", SUBTITLE),
                  PageBreak()])

    for name, body in sections:
        if name == "ECHOES OF CHILDHOOD":
            continue
        if name == "Contents":
            story.extend([Spacer(1, 0.55 * inch), Paragraph("Contents", SECTION_TITLE)])
            for line in [x.strip() for x in body.splitlines() if x.strip() and x.strip() != "---"]:
                story.append(Paragraph(clean_inline(line), CONTENTS))
            story.append(PageBreak())
            continue
        if name in {"Introduction", "Before You Begin", "Acknowledgements"}:
            story.extend([Spacer(1, 0.65 * inch), Paragraph(name, SECTION_TITLE)])
            add_prose(story, paragraphs_from_body(body))
            story.append(PageBreak())
            continue
        if name == "Final Page":
            story.extend([Spacer(1, 2.65 * inch),
                          Paragraph("One day, someone will remember today.", FINAL),
                          Paragraph("Make it a beautiful memory.", FINAL_ITALIC)])
            continue
        if name.startswith("Chapter") or name == "Epilogue":
            title, subtitle, fragment = chapter_meta(name, body)
            if name == "Chapter One" and CH1_IMAGE.exists():
                story.append(full_page_image(CH1_IMAGE))
                story.append(PageBreak())
            story.extend([
                Spacer(1, 1.45 * inch),
                Paragraph(name.upper(), CHAPTER_NO),
                Paragraph(clean_inline(title), CHAPTER_TITLE),
                Paragraph(clean_inline(subtitle), SUBTITLE),
                Spacer(1, 0.3 * inch),
                Paragraph("MEMORY FRAGMENT", SMALL_CAP),
                Paragraph("“" + fragment + "”", FRAGMENT),
                PageBreak(),
            ])
            add_prose(story, paragraphs_from_body(body))
            story.append(PageBreak())

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = MemoryBookDoc(str(OUTPUT))
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
