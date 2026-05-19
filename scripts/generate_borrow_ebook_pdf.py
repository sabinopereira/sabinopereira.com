#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image as RLImage,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "books/borrow-delay-repeat"
SOURCE_DOCX = BOOK_DIR / "source/borrow-delay-repeat-source.docx"
OUT_DIR = BOOK_DIR / "ebook"
PREVIEW_DIR = BOOK_DIR / "previews"
COVER_JPG = OUT_DIR / "borrow-delay-repeat-ebook-cover.jpg"
OUTPUT_PDF = OUT_DIR / "borrow-delay-repeat-ebook.pdf"

PAGE_W = 6 * inch
PAGE_H = 9 * inch


@dataclass
class Section:
    title: str
    kind: str
    paragraphs: list[str]


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


def read_docx_paragraphs(path: Path) -> list[str]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", ns):
        text = "".join((node.text or "") for node in para.findall(".//w:t", ns)).strip()
        if text:
            paragraphs.append(re.sub(r"\s+", " ", text))
    return paragraphs


def clean_heading(text: str) -> str:
    return text.replace("—", "-").strip()


def parse_sections(paragraphs: list[str]) -> tuple[str, str, list[Section]]:
    title = paragraphs[0]
    subtitle = paragraphs[1]
    markers = []
    for idx, text in enumerate(paragraphs):
        if text in {"Disclaimer", "Intro"} or text.startswith("Chapter "):
            markers.append((idx, text))

    sections: list[Section] = []
    for marker_index, (start, raw_title) in enumerate(markers):
        end = markers[marker_index + 1][0] if marker_index + 1 < len(markers) else len(paragraphs)
        title_text = raw_title
        body = paragraphs[start + 1 : end]

        if raw_title.startswith("Chapter 3"):
            title_text = "Chapter 3 - Strategic Disappearance"
            extra = raw_title.replace("Chapter 3 — Strategic Disappearance", "").strip()
            if extra:
                body.insert(0, extra)
        elif raw_title.startswith("Chapter 5"):
            title_text = "Chapter 5 - The Follow-up Defense"
            extra = raw_title.replace("Chapter 5 — The Follow-up Defense", "").strip()
            if extra:
                body.insert(0, extra)
        else:
            title_text = clean_heading(title_text)

        split_body: list[str] = []
        for para in body:
            if " Part 1 — The Basics" in para:
                left, right = para.split(" Part 1 — The Basics", 1)
                if left.strip():
                    split_body.append(left.strip())
                split_body.append("Part 1 - The Basics")
                if right.strip():
                    split_body.append(right.strip())
            elif para == title:
                continue
            else:
                split_body.append(para)

        kind = "front" if title_text in {"Disclaimer", "Intro"} else "chapter"
        sections.append(Section(title_text, kind, split_body))
    return title, subtitle, sections


def fit_font(text: str, font_path: str, max_width: int, start_size: int, min_size: int) -> ImageFont.FreeTypeFont:
    canvas = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for size in range(start_size, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size)
        left, top, right, bottom = canvas.textbbox((0, 0), text, font=font)
        if right - left <= max_width:
            return font
    return ImageFont.truetype(font_path, min_size)


def create_cover(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 2560
    im = Image.new("RGB", (width, height), "#f1efe8")
    draw = ImageDraw.Draw(im)
    impact = "/System/Library/Fonts/Supplemental/Impact.ttf"
    georgia = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    georgia_bold = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
    georgia_italic = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"

    black = "#111111"
    ink = "#252525"
    grey = "#6b6b62"
    red = "#b01f1f"

    draw.rectangle([90, 90, width - 90, height - 90], outline=black, width=8)
    draw.rectangle([120, 120, width - 120, height - 120], outline=black, width=2)

    author_font = ImageFont.truetype(georgia_bold, 48)
    draw.text((140, 165), "SABINO PEREIRA", font=author_font, fill=black)

    title_font = fit_font("BORROW.", impact, width - 260, 255, 140)
    title_font_2 = fit_font("DELAY.", impact, width - 260, 255, 140)
    title_font_3 = fit_font("REPEAT.", impact, width - 260, 255, 140)
    y = 365
    for word, font in [("BORROW.", title_font), ("DELAY.", title_font_2), ("REPEAT.", title_font_3)]:
        draw.text((140, y), word, font=font, fill=black)
        y += int(font.size * 0.83)
    draw.rectangle([145, y + 18, 710, y + 34], fill=red)

    subtitle_font = ImageFont.truetype(georgia_italic, 58)
    sub_y = y + 115
    draw.text((145, sub_y), "A very unserious guide", font=subtitle_font, fill=ink)
    draw.text((145, sub_y + 76), "to not giving money back.", font=subtitle_font, fill=ink)

    # Simple monochrome satirical illustration: an IOU note quietly running away.
    note_x, note_y = 430, 1470
    draw.rounded_rectangle([note_x, note_y, note_x + 710, note_y + 430], radius=30, fill="#fffdf6", outline=black, width=7)
    draw.line([note_x + 45, note_y + 105, note_x + 665, note_y + 105], fill=grey, width=4)
    draw.line([note_x + 45, note_y + 185, note_x + 560, note_y + 185], fill=grey, width=4)
    draw.line([note_x + 45, note_y + 265, note_x + 610, note_y + 265], fill=grey, width=4)
    iou_font = ImageFont.truetype(impact, 108)
    draw.text((note_x + 64, note_y + 42), "IOU", font=iou_font, fill=black)
    draw.arc([note_x + 500, note_y + 285, note_x + 650, note_y + 385], 205, 340, fill=black, width=8)
    draw.line([note_x + 170, note_y + 430, note_x + 110, note_y + 540], fill=black, width=10)
    draw.line([note_x + 545, note_y + 430, note_x + 615, note_y + 540], fill=black, width=10)
    draw.line([note_x + 98, note_y + 540, note_x + 215, note_y + 540], fill=black, width=10)
    draw.line([note_x + 600, note_y + 540, note_x + 720, note_y + 540], fill=black, width=10)
    draw.arc([260, 1880, 1200, 2290], 190, 350, fill="#9a9487", width=5)

    kicker_font = ImageFont.truetype(georgia, 38)
    draw.text((145, height - 225), "SATIRE / SHORT READ", font=kicker_font, fill=grey)
    im.save(path, "JPEG", quality=95, optimize=True)


class LineIllustration(Flowable):
    def __init__(self, kind: str, width: float = 4.2 * inch, height: float = 1.65 * inch):
        super().__init__()
        self.kind = kind
        self.width = width
        self.height = height

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        c.saveState()
        c.setStrokeColor(colors.HexColor("#111111"))
        c.setFillColor(colors.white)
        c.setLineWidth(2)
        if self.kind == "ask":
            c.roundRect(w * 0.13, h * 0.25, w * 0.74, h * 0.42, 8, stroke=1, fill=0)
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(w * 0.5, h * 0.43, "Hey... this is awkward")
            c.line(w * 0.30, h * 0.15, w * 0.70, h * 0.15)
        elif self.kind == "tomorrow":
            c.rect(w * 0.24, h * 0.16, w * 0.52, h * 0.62, stroke=1, fill=0)
            c.line(w * 0.24, h * 0.63, w * 0.76, h * 0.63)
            c.setFont("Impact", 30)
            c.drawCentredString(w * 0.5, h * 0.33, "TOMORROW")
        elif self.kind == "disappear":
            c.roundRect(w * 0.32, h * 0.15, w * 0.36, h * 0.70, 12, stroke=1, fill=0)
            c.setFont("Georgia-Italic", 13)
            c.drawCentredString(w * 0.5, h * 0.52, "seen")
            c.setFont("Georgia-Bold", 20)
            c.drawCentredString(w * 0.5, h * 0.32, "...")
        elif self.kind == "image":
            c.circle(w * 0.5, h * 0.5, h * 0.26, stroke=1, fill=0)
            c.arc(w * 0.32, h * 0.10, w * 0.68, h * 0.52, 0, 180)
            c.line(w * 0.24, h * 0.75, w * 0.76, h * 0.75)
            c.setFont("Georgia", 12)
            c.drawCentredString(w * 0.5, h * 0.03, "public image, private delay")
        elif self.kind == "defense":
            c.roundRect(w * 0.30, h * 0.18, w * 0.40, h * 0.62, 18, stroke=1, fill=0)
            c.setFont("Impact", 44)
            c.drawCentredString(w * 0.5, h * 0.34, "?")
        else:
            c.circle(w * 0.5, h * 0.5, h * 0.30, stroke=1, fill=0)
            c.setFont("Impact", 24)
            c.drawCentredString(w * 0.5, h * 0.43, "RESET")
            c.arc(w * 0.30, h * 0.28, w * 0.70, h * 0.72, 25, 315)
        c.restoreState()


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(html.escape(text), style)


def draw_page_number(canv, doc) -> None:
    if doc.page <= 2:
        return
    canv.saveState()
    canv.setFont("Georgia", 9)
    canv.setFillColor(colors.HexColor("#555555"))
    canv.drawCentredString(PAGE_W / 2, 0.38 * inch, str(doc.page))
    canv.restoreState()


def build_pdf(title: str, subtitle: str, sections: list[Section]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    create_cover(COVER_JPG)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BookTitle", fontName="Impact", fontSize=37, leading=39, alignment=TA_CENTER, textColor=colors.HexColor("#111111")))
    styles.add(ParagraphStyle("BookSubtitle", fontName="Georgia-Italic", fontSize=14, leading=20, alignment=TA_CENTER, textColor=colors.HexColor("#333333")))
    styles.add(ParagraphStyle("Author", fontName="Georgia", fontSize=11, leading=14, alignment=TA_CENTER, spaceBefore=28))
    styles.add(ParagraphStyle("SectionTitle", fontName="Impact", fontSize=25, leading=28, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle("PartTitle", fontName="Georgia-Bold", fontSize=13, leading=18, alignment=TA_CENTER, spaceBefore=10, spaceAfter=14))
    styles.add(ParagraphStyle("BodyBook", fontName="Georgia", fontSize=11.6, leading=17.4, spaceAfter=7.5))
    styles.add(ParagraphStyle("ShortLine", fontName="Georgia-Italic", fontSize=12.2, leading=18, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle("Toc", fontName="Georgia", fontSize=12, leading=21, spaceAfter=3))
    styles.add(ParagraphStyle("Note", fontName="Georgia-Italic", fontSize=10.5, leading=15, alignment=TA_CENTER, textColor=colors.HexColor("#444444")))

    doc = BaseDocTemplate(str(OUTPUT_PDF), pagesize=(PAGE_W, PAGE_H), title=title, author="Sabino Pereira")
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
    frame = Frame(0.62 * inch, 0.7 * inch, PAGE_W - 1.24 * inch, PAGE_H - 1.4 * inch, id="main")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame]),
        PageTemplate(id="book", frames=[frame], onPage=draw_page_number),
    ])

    story: list = [
        RLImage(str(COVER_JPG), width=PAGE_W, height=PAGE_H),
        NextPageTemplate("book"),
        PageBreak(),
        Spacer(1, 2.1 * inch),
        para(title.upper(), styles["BookTitle"]),
        Spacer(1, 0.18 * inch),
        para(subtitle, styles["BookSubtitle"]),
        para("Sabino Pereira", styles["Author"]),
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
        story.append(para(section.title, styles["SectionTitle"]))
        if section.title in illustration_map:
            story.append(Spacer(1, 0.08 * inch))
            story.append(LineIllustration(illustration_map[section.title]))
            story.append(Spacer(1, 0.18 * inch))
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
        para("Borrow. Delay. Repeat.", styles["BookSubtitle"]),
        para("End of book.", styles["Note"]),
    ])
    doc.build(story)


def main() -> None:
    register_fonts()
    paragraphs = read_docx_paragraphs(SOURCE_DOCX)
    title, subtitle, sections = parse_sections(paragraphs)
    build_pdf(title, subtitle, sections)
    print(OUTPUT_PDF)
    print(COVER_JPG)


if __name__ == "__main__":
    main()
