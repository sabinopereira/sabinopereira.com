#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
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
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PDF = Path("/Users/binopereira/Desktop/Quiet Power/Books/Quiet Power Final paperback update.pdf")
BOOK_DIR = ROOT / "books/quiet-power"
SOURCE_DIR = BOOK_DIR / "source"
EBOOK_DIR = BOOK_DIR / "ebook"
PAPERBACK_DIR = BOOK_DIR / "paperback"
PREVIEW_DIR = BOOK_DIR / "previews"
COVER_JPG = EBOOK_DIR / "quiet-power-ebook-cover.jpg"
EPUB_PATH = EBOOK_DIR / "quiet-power-kindle-ebook.epub"
INTERIOR_PDF = PAPERBACK_DIR / "quiet-power-paperback-miolo-kdp.pdf"
COVER_PDF = PAPERBACK_DIR / "quiet-power-paperback-capa-kdp.pdf"
EXTRACTED_TEXT = SOURCE_DIR / "quiet-power-source-extracted.txt"
METADATA_JSON = BOOK_DIR / "kdp-metadata.json"

TITLE = "Quiet Power"
SUBTITLE = "Calm. Focused. Unshaken. Design."
AUTHOR = "Sabino Pereira"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/quiet-power"))
TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch


@dataclass
class Section:
    kind: str
    title: str
    subtitle: str
    lines: list[str]


SECTION_SPECS = [
    (5, "intro", "Introduction: The Silent Advantage", "", ["Introduction: The Silent", "Advantage"]),
    (17, "part", "PART I: CALM", "Control Before Direction", ["PART I. CALM", "Control Before Direction"]),
    (20, "chapter", "Chapter 1: Strategic Solitude", "The Withdrawal That Builds", ["Chapter 1 - Strategic Solitude", "The Withdrawal That Builds"]),
    (30, "chapter", "Chapter 2: Response Discipline", "The Controlled Interval", ["Chapter 2 - Response", "Discipline", "The Controlled Interval"]),
    (39, "chapter", "Chapter 3: The Noise Audit", "What Is Draining You", ["Chapter 3 - The Noise Audit", "What Is Draining You"]),
    (49, "chapter", "Chapter 4: Access Control", "The Perimeter of Focus", ["Chapter 4 - Access Control", "The Perimeter of Focus"]),
    (60, "chapter", "Chapter 5: Presence Over Performance", "Being Instead of Broadcasting", ["Chapter 5 - Presence Over", "Performance", "Being Instead of Broadcasting"]),
    (70, "part", "PART II: FOCUSED", "Direction Under Control", ["PART II. FOCUSED", "Direction Under Control"]),
    (72, "chapter", "Chapter 6: Focus Is a Strategic Asset", "Depth Over Noise", ["Chapter 6 - Focus Is a", "Strategic Asset", "Depth Over Noise"]),
    (82, "chapter", "Chapter 7: The Consistency Engine", "Structure Over Mood", ["Chapter 7 - The Consistency", "Engine", "Structure Over Mood"]),
    (93, "chapter", "Chapter 8: The Long Game", "Staying Beyond Applause", ["Chapter 8 - The Long Game", "Staying Beyond Applause"]),
    (104, "part", "PART III: UNSHAKEN", "Stability Under Pressure", ["PART III. UNSHAKEN", "Stability Under Pressure"]),
    (106, "chapter", "Chapter 9: Regulation Is Power", "Stability Under Pressure", ["Chapter 9 - Regulation Is", "Power", "Stability Under Pressure"]),
    (115, "chapter", "Chapter 10: Failure as Calibration", "Read the Signal, Not the Story", ["Chapter 10 - Failure as", "Calibration", "Read the Signal, Not the Story"]),
    (126, "chapter", "Chapter 11: The Identity Floor", "The Level You Do Not Fall Below", ["Chapter 11 - The Identity", "Floor", "The Level You Do Not Fall Below"]),
    (138, "part", "PART IV: DESIGN", "From Effort to Scale", ["PART IV - DESIGN", "From Effort to Scale"]),
    (141, "chapter", "Chapter 12: Leverage Decides Scale", "Architecture of Force", ["Chapter 12 - Leverage Decides", "Scale", "Architecture of Force"]),
    (152, "chapter", "Chapter 13: Building Systems", "Install Once. Execute Repeatedly.", ["Chapter 13 - Building Systems", "Install Once. Execute Repeatedly."]),
    (164, "chapter", "Chapter 14: Reputation as Infrastructure", "What You Repeatedly Reveal", ["Chapter 14 - Reputation as", "Infrastructure", "What You Repeatedly Reveal"]),
    (175, "chapter", "Chapter 15: The Long Position", "A Life Oriented Toward What Endures", ["Chapter 15 - The Long", "Position", "A Life Oriented Toward What Endures"]),
    (185, "chapter", "Chapter 16: Growth Tests Structure", "When Expansion Becomes Exposure", ["Chapter 16 - Growth Tests", "Structure", "When Expansion Becomes Exposure"]),
    (195, "manifesto", "Final Manifesto", "Quiet Power", ["Final Manifesto", "Quiet Power"]),
    (204, "practice", "The Quiet Power Standard", "Calm. Focused. Unshaken. Design.", ["The Quiet Power Standard", "Calm. Focused. Unshaken."]),
]


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    for name, file in {
        "Georgia": "Georgia.ttf",
        "Georgia-Bold": "Georgia Bold.ttf",
        "Georgia-Italic": "Georgia Italic.ttf",
        "Impact": "Impact.ttf",
    }.items():
        try:
            pdfmetrics.registerFont(TTFont(name, str(font_dir / file)))
        except Exception:
            pass


def clean_line(line: str) -> str:
    replacements = {
        "\x00": " - ",
        "→": " - ",
        "بسبب": "through ",
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "eﬀort": "effort",
        "Eﬀort": "Effort",
        "eﬃcient": "efficient",
        "deﬁne": "define",
        "deﬁned": "defined",
        "ﬁll": "fill",
        "ﬁlter": "filter",
        "ﬂoor": "floor",
        "ﬂuctuate": "fluctuate",
        "do react im not mediately": "do not react immediately",
        "stor y": "story",
    }
    line = line.strip()
    for old, new in replacements.items():
        line = line.replace(old, new)
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\s+-\s+-\s+", " - ", line)
    line = re.sub(r"\s+([.,:;!?])", r"\1", line)
    line = re.sub(r"^- ", "• ", line)
    return line.strip()


def page_lines(reader: PdfReader, page_no: int) -> list[str]:
    text = reader.pages[page_no - 1].extract_text() or ""
    lines: list[str] = []
    for raw in text.splitlines():
        line = clean_line(raw)
        if not line or line == str(page_no):
            continue
        lines.append(line)
    return lines


def is_heading_like(line: str) -> bool:
    if line.startswith("•") or re.fullmatch(r"\d+\..+", line):
        return False
    if line.endswith((".", "?", "!", ":", ";")):
        return False
    words = [word.strip("“”\"'()") for word in line.split()]
    if not words or len(words) > 7:
        return False
    titled = sum(1 for word in words if word[:1].isupper() or word.lower() in {"as", "of", "the", "to", "and", "vs"})
    return titled >= max(1, len(words) - 1)


def merge_extracted_lines(raw_lines: list[str]) -> list[str]:
    lines: list[str] = []
    for line in raw_lines:
        if lines and re.fullmatch(r"[a-z]+(?: [a-z]+)?", line) and not lines[-1].endswith((".", "?", "!", ":")):
            lines[-1] = f"{lines[-1]} {line}"
            continue
        if (
            lines
            and not lines[-1].endswith((".", "?", "!", ":", ";"))
            and not lines[-1].startswith("•")
            and not is_heading_like(lines[-1])
            and not is_heading_like(line)
            and not line.startswith("•")
            and not re.fullmatch(r"\d+\..+", line)
        ):
            lines[-1] = f"{lines[-1]} {line}"
            continue
        lines.append(line)
    return lines


def parse_sections() -> list[Section]:
    reader = PdfReader(str(SOURCE_PDF))
    sections: list[Section] = []
    extracted: list[str] = []
    for idx, spec in enumerate(SECTION_SPECS):
        start, kind, title, subtitle, skip = spec
        end = SECTION_SPECS[idx + 1][0] if idx + 1 < len(SECTION_SPECS) else len(reader.pages) + 1
        raw_lines: list[str] = []
        for page_no in range(start, end):
            raw_lines.extend(page_lines(reader, page_no))
        lines = merge_extracted_lines(raw_lines)
        for expected in skip:
            if lines and clean_line(lines[0]) == clean_line(expected):
                lines.pop(0)
        lines = [line for line in lines if line not in {title, subtitle}]
        section = Section(kind, title, subtitle, lines)
        sections.append(section)
        extracted.append(f"# {title}")
        if subtitle:
            extracted.append(f"## {subtitle}")
        extracted.extend(lines)
        extracted.append("")
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_TEXT.write_text("\n".join(extracted), encoding="utf-8")
    return sections


def create_cover(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1600, 2560
    im = Image.new("RGB", (w, h), "#101010")
    d = ImageDraw.Draw(im)
    font_dir = "/System/Library/Fonts/Supplemental"
    georgia = f"{font_dir}/Georgia.ttf"
    georgia_bold = f"{font_dir}/Georgia Bold.ttf"
    georgia_italic = f"{font_dir}/Georgia Italic.ttf"
    cream = "#f4f0e6"
    gold = "#bfa968"
    ink = "#101010"
    d.rectangle([0, 0, w, h], fill=ink)
    d.rectangle([105, 105, w - 105, h - 105], outline=cream, width=5)
    d.ellipse([520, 520, 1080, 1080], outline=cream, width=9)
    d.line([800, 330, 800, 1285], fill=cream, width=7)
    d.line([560, 800, 1040, 800], fill=cream, width=7)
    d.rectangle([0, 0, w, 250], fill=ink)
    d.text((150, 185), AUTHOR.upper(), font=ImageFont.truetype(georgia_bold, 46), fill=cream)
    for text, y in [("QUIET", 1320), ("POWER", 1510)]:
        bbox = d.textbbox((0, 0), text, font=ImageFont.truetype(georgia_bold, 178))
        d.text(((w - (bbox[2] - bbox[0])) / 2, y), text, font=ImageFont.truetype(georgia_bold, 178), fill=cream)
    line = "Calm. Focused. Unshaken. Design."
    bbox = d.textbbox((0, 0), line, font=ImageFont.truetype(georgia_italic, 54))
    d.text(((w - (bbox[2] - bbox[0])) / 2, 1775), line, font=ImageFont.truetype(georgia_italic, 54), fill=gold)
    desc = "A field guide for strength without noise."
    bbox = d.textbbox((0, 0), desc, font=ImageFont.truetype(georgia, 36))
    d.text(((w - (bbox[2] - bbox[0])) / 2, 2075), desc, font=ImageFont.truetype(georgia, 36), fill=cream)
    im.save(path, "JPEG", quality=95, optimize=True)


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(html.escape(text), style)


def draw_page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFont("Georgia", 9)
    canv.setFillColor(colors.HexColor("#555555"))
    canv.drawCentredString(TRIM_W / 2, 0.42 * inch, str(doc.page))
    canv.restoreState()


def build_interior(sections: list[Section]) -> int:
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BookTitle", fontName="Georgia-Bold", fontSize=40, leading=44, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle("BookSubtitle", fontName="Georgia-Italic", fontSize=14, leading=20, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle("BookAuthor", fontName="Georgia", fontSize=12, leading=16, alignment=TA_CENTER, spaceBefore=24))
    styles.add(ParagraphStyle("QPToc", fontName="Georgia", fontSize=10.8, leading=15, spaceAfter=1))
    styles.add(ParagraphStyle("QPPart", fontName="Georgia-Bold", fontSize=23, leading=29, alignment=TA_CENTER, spaceAfter=14))
    styles.add(ParagraphStyle("QPPartSub", fontName="Georgia-Italic", fontSize=15, leading=21, alignment=TA_CENTER, spaceAfter=22))
    styles.add(ParagraphStyle("QPPartIntroTitle", fontName="Georgia-Bold", fontSize=15.5, leading=20, alignment=TA_LEFT, spaceAfter=10))
    styles.add(ParagraphStyle("QPChapter", fontName="Georgia-Bold", fontSize=18.5, leading=23, alignment=TA_LEFT, spaceAfter=7))
    styles.add(ParagraphStyle("QPChapterSub", fontName="Georgia-Italic", fontSize=12.2, leading=17, alignment=TA_LEFT, spaceAfter=14))
    styles.add(ParagraphStyle("QPBody", fontName="Georgia", fontSize=10.8, leading=16.2, spaceAfter=5.5))
    styles.add(ParagraphStyle("QPBullet", fontName="Georgia", fontSize=10.8, leading=15.8, leftIndent=16, firstLineIndent=-10, spaceAfter=3))
    styles.add(ParagraphStyle("QPSectionHead", fontName="Georgia-Bold", fontSize=11.2, leading=16, alignment=TA_LEFT, spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle("QPPracticeTitle", fontName="Georgia-Bold", fontSize=15.4, leading=19, alignment=TA_LEFT, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle("QPSmall", fontName="Georgia", fontSize=9.4, leading=14))
    doc = BaseDocTemplate(str(INTERIOR_PDF), pagesize=(TRIM_W, TRIM_H), title=TITLE, author=AUTHOR)
    odd = Frame(0.78 * inch, 0.72 * inch, TRIM_W - 1.46 * inch, TRIM_H - 1.42 * inch, id="odd")
    even = Frame(0.68 * inch, 0.72 * inch, TRIM_W - 1.46 * inch, TRIM_H - 1.42 * inch, id="even")
    doc.addPageTemplates([
        PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
        PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
    ])
    story: list = [
        Spacer(1, 2.15 * inch),
        paragraph("QUIET POWER", styles["BookTitle"]),
        paragraph(SUBTITLE, styles["BookSubtitle"]),
        paragraph(AUTHOR, styles["BookAuthor"]),
        PageBreak(),
        Spacer(1, 2.0 * inch),
        paragraph("Copyright © 2026 Sabino Pereira. All rights reserved.", styles["QPSmall"]),
        paragraph("This book is for informational and reflective purposes only.", styles["QPSmall"]),
        PageBreak(),
        paragraph("Contents", styles["QPChapter"]),
    ]
    for section in sections:
        story.append(paragraph(section.title, styles["QPToc"]))
    story.append(PageBreak())
    for section in sections:
        if section.kind == "part":
            story.extend([Spacer(1, 3.0 * inch), paragraph(section.title, styles["QPPart"]), paragraph(section.subtitle, styles["QPPartSub"]), PageBreak()])
            story.append(Spacer(1, 0.35 * inch))
            story.append(paragraph(section.title.replace(":", " -"), styles["QPPartIntroTitle"]))
            for line in section.lines:
                story.append(paragraph(line, styles["QPBody"] if not line.startswith("-") and not line.startswith("•") else styles["QPBullet"]))
            story.append(PageBreak())
            continue
        title_style = styles["QPChapter"]
        story.append(Spacer(1, 0.36 * inch))
        story.append(paragraph(section.title, title_style))
        if section.subtitle:
            story.append(paragraph(section.subtitle, styles["QPChapterSub"]))
        if section.kind == "practice":
            pending: list[str] = []
            current_title: str | None = None
            current_lines: list[str] = []

            def flush_intro() -> None:
                nonlocal pending
                for item in pending:
                    story.append(paragraph(item, styles["QPBody"]))
                pending = []

            def flush_block() -> None:
                nonlocal current_title, current_lines
                if current_title is None:
                    return
                block = [paragraph(current_title, styles["QPPracticeTitle"])]
                block.extend(paragraph(item, styles["QPBody"]) for item in current_lines)
                story.append(KeepTogether(block))
                current_title, current_lines = None, []

            for line in section.lines:
                if re.fullmatch(r"\d+\..+", line) or line == "Closing Standard":
                    flush_intro()
                    flush_block()
                    current_title = line
                    current_lines = []
                elif current_title is None:
                    pending.append(line)
                else:
                    current_lines.append(line)
            flush_intro()
            flush_block()
            story.append(PageBreak())
            continue
        for line in section.lines:
            if line.startswith("•"):
                story.append(paragraph(line, styles["QPBullet"]))
            elif re.fullmatch(r"\d+\..+", line):
                story.append(Spacer(1, 0.08 * inch))
                story.append(paragraph(line, styles["QPPracticeTitle"]))
            elif len(line) < 44 and not line.endswith(".") and not line.endswith("?") and not line.startswith("“"):
                story.append(paragraph(line, styles["QPSectionHead"]))
            else:
                story.append(paragraph(line, styles["QPBody"]))
        story.append(PageBreak())
    doc.build(story)
    page_count = len(PdfReader(str(INTERIOR_PDF)).pages)
    if page_count % 2:
        add_blank_page(INTERIOR_PDF)
        page_count += 1
    return page_count


def add_blank_page(pdf_path: Path) -> None:
    blank_path = pdf_path.with_suffix(".blank.pdf")
    c = canvas.Canvas(str(blank_path), pagesize=(TRIM_W, TRIM_H))
    c.showPage()
    c.save()
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_page(PdfReader(str(blank_path)).pages[0])
    with pdf_path.open("wb") as handle:
        writer.write(handle)
    blank_path.unlink(missing_ok=True)


def draw_wrapped_text(canv: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float, color) -> float:
    canv.setFont(font, size)
    canv.setFillColor(color)
    line = ""
    for word in text.split():
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


def build_cover_pdf(page_count: int) -> dict[str, float]:
    spine = page_count * WHITE_PAPER_SPINE_PER_PAGE
    cover_w = BLEED + TRIM_W + spine + TRIM_W + BLEED
    cover_h = TRIM_H + 2 * BLEED
    back_x = BLEED
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine
    c = canvas.Canvas(str(COVER_PDF), pagesize=(cover_w, cover_h))
    c.setFillColor(colors.HexColor("#101010"))
    c.rect(0, 0, cover_w, cover_h, stroke=0, fill=1)
    c.drawImage(str(COVER_JPG), front_x, 0, width=TRIM_W + BLEED, height=cover_h, preserveAspectRatio=False, mask="auto")
    safe_x = back_x + 0.52 * inch
    y = cover_h - 0.82 * inch
    c.setFont("Georgia-Bold", 24)
    c.setFillColor(colors.HexColor("#f4f0e6"))
    c.drawString(safe_x, y, "QUIET POWER")
    y -= 0.35 * inch
    c.setStrokeColor(colors.HexColor("#bfa968"))
    c.setLineWidth(3)
    c.line(safe_x, y, safe_x + 1.6 * inch, y)
    y -= 0.42 * inch
    blurb = (
        "Quiet Power is a field guide for strength without noise: calm under pressure, "
        "focused in a distracted world, unshaken by reaction, and designed for long-term leverage."
    )
    y = draw_wrapped_text(c, blurb, safe_x, y, TRIM_W - 1.05 * inch, "Georgia", 12, 18, colors.HexColor("#f4f0e6"))
    y -= 0.2 * inch
    y = draw_wrapped_text(c, "Calm. Focused. Unshaken. Design.", safe_x, y, TRIM_W - 1.05 * inch, "Georgia-Italic", 13, 20, colors.HexColor("#bfa968"))
    y -= 0.28 * inch
    c.setFont("Georgia", 10)
    c.setFillColor(colors.HexColor("#d8d2c4"))
    c.drawString(safe_x, y, AUTHOR)
    barcode_w, barcode_h = 2.0 * inch, 1.2 * inch
    c.setFillColor(colors.white)
    c.rect(back_x + TRIM_W - barcode_w - 0.35 * inch, 0.42 * inch, barcode_w, barcode_h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Georgia", 6.5)
    c.drawCentredString(back_x + TRIM_W - barcode_w / 2 - 0.35 * inch, 0.96 * inch, "Barcode KDP")
    if page_count > 79:
        c.saveState()
        c.translate(spine_x + spine / 2, cover_h / 2)
        c.rotate(90)
        c.setFillColor(colors.HexColor("#f4f0e6"))
        c.setFont("Georgia-Bold", max(5, min(8, spine * 0.28)))
        c.drawCentredString(0, -spine * 0.18, "QUIET POWER")
        c.setFont("Georgia", max(4.5, min(7, spine * 0.24)))
        c.drawCentredString(0, spine * 0.26, AUTHOR.upper())
        c.restoreState()
    c.showPage()
    c.save()
    return {
        "page_count": page_count,
        "trim_width_in": 6,
        "trim_height_in": 9,
        "bleed_in": BLEED / inch,
        "spine_width_in": spine / inch,
        "cover_width_in": cover_w / inch,
        "cover_height_in": cover_h / inch,
    }


def write_epub(sections: list[Section]) -> None:
    build_dir = EBOOK_DIR / "ebook-build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    (build_dir / "META-INF").mkdir(parents=True)
    (build_dir / "OEBPS/images").mkdir(parents=True)

    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def xhtml(title: str, body: str) -> str:
        return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="styles.css"/></head>
<body>{body}</body></html>
'''

    write(build_dir / "mimetype", "application/epub+zip")
    write(build_dir / "META-INF/container.xml", '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>
''')
    write(build_dir / "OEBPS/styles.css", """body{font-family:Georgia,serif;line-height:1.58;margin:0 7%;color:#151515}.section{break-before:page;page-break-before:always}h1{font-size:1.38em;line-height:1.22;margin:2em 0 .55em}.subtitle{font-style:italic;margin-bottom:1.6em}.part-opener{break-before:page;page-break-before:always;text-align:center;margin-top:38%}.part-opener h1{text-transform:uppercase;letter-spacing:.06em}.part-intro{break-before:page;page-break-before:always}.part-intro h1{font-size:1.15em}.cover{text-align:center;margin:0}.cover img{max-width:100%;height:auto}.practice h2{font-size:1.1em;margin-top:1.4em}p{margin:0 0 .85em}""")
    write(build_dir / "OEBPS/cover.xhtml", xhtml("Cover", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Quiet Power cover"/></section>'))
    shutil.copyfile(COVER_JPG, build_dir / "OEBPS/images/cover.jpg")
    nav_items, spine_items, manifest_items = [], [], []
    for i, section in enumerate(sections, 1):
        fname = f"section-{i:02d}.xhtml"
        nav_items.append(f'<li><a href="{fname}">{html.escape(section.title)}</a></li>')
        spine_items.append(f'<itemref idref="section-{i:02d}"/>')
        manifest_items.append(f'<item id="section-{i:02d}" href="{fname}" media-type="application/xhtml+xml"/>')
        cls = "section practice" if section.kind == "practice" else "section"
        epub_type = "part" if section.kind == "part" else "chapter"
        if section.kind == "part":
            parts = [
                f'<section class="part-opener" epub:type="part"><h1>{html.escape(section.title)}</h1>',
                f'<p class="subtitle">{html.escape(section.subtitle)}</p></section>',
                f'<section class="part-intro"><h1>{html.escape(section.title.replace(":", " -"))}</h1>',
            ]
        else:
            parts = [f'<section class="{cls}" epub:type="{epub_type}"><h1>{html.escape(section.title)}</h1>']
            if section.subtitle:
                parts.append(f'<p class="subtitle">{html.escape(section.subtitle)}</p>')
        for line in section.lines:
            if re.fullmatch(r"\d+\..+", line):
                parts.append(f"<h2>{html.escape(line)}</h2>")
            else:
                parts.append(f"<p>{html.escape(line)}</p>")
        parts.append("</section>")
        write(build_dir / "OEBPS" / fname, xhtml(section.title, "\n".join(parts)))
    write(build_dir / "OEBPS/nav.xhtml", xhtml("Contents", f'<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{"".join(nav_items)}</ol></nav>'))
    write(build_dir / "OEBPS/content.opf", f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{BOOK_ID}</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>en</dc:language><dc:publisher>{AUTHOR}</dc:publisher><meta name="cover" content="cover-image"/><meta property="dcterms:modified">2026-05-20T06:30:00Z</meta></metadata>
<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="style" href="styles.css" media-type="text/css"/><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/><item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>{"".join(manifest_items)}</manifest>
<spine><itemref idref="cover" linear="no"/>{"".join(spine_items)}</spine></package>''')
    with zipfile.ZipFile(EPUB_PATH, "w") as zf:
        zf.write(build_dir / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for file in sorted(build_dir.rglob("*")):
            if file.is_file() and file.name != "mimetype":
                zf.write(file, file.relative_to(build_dir), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(build_dir)


def write_metadata(specs: dict[str, float]) -> None:
    METADATA_JSON.write_text(json.dumps({
        "title": TITLE,
        "subtitle": SUBTITLE,
        "author": AUTHOR,
        "kdp_setup": {
            "trim_size": "6 x 9 in",
            "interior": "Black & white",
            "paper": "White paper",
            "interior_bleed": "No bleed",
            "cover_finish": "Matte recommended",
        },
        "files": {
            "paperback_interior_pdf": "paperback/quiet-power-paperback-miolo-kdp.pdf",
            "paperback_cover_pdf": "paperback/quiet-power-paperback-capa-kdp.pdf",
            "ebook_epub": "ebook/quiet-power-kindle-ebook.epub",
            "ebook_cover_jpg": "ebook/quiet-power-ebook-cover.jpg",
        },
        "print_specs": specs,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    register_fonts()
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    create_cover(COVER_JPG)
    sections = parse_sections()
    page_count = build_interior(sections)
    specs = build_cover_pdf(page_count)
    write_epub(sections)
    write_metadata(specs)
    print(json.dumps(specs, indent=2))


if __name__ == "__main__":
    main()
