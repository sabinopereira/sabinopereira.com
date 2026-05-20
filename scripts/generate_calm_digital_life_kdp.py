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
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PDF = Path("/Users/binopereira/Desktop/Quiet Power/Books/The Calm Digital Life Pause First. Avoid Scams. Protect Your Money. Stay in Control After 60 (Hard Cover).pdf")
BOOK_DIR = ROOT / "books/the-calm-digital-life"
SOURCE_DIR = BOOK_DIR / "source"
EBOOK_DIR = BOOK_DIR / "ebook"
PAPERBACK_DIR = BOOK_DIR / "paperback"
PREVIEW_DIR = BOOK_DIR / "previews"
COVER_JPG = EBOOK_DIR / "the-calm-digital-life-ebook-cover.jpg"
EPUB_PATH = EBOOK_DIR / "the-calm-digital-life-kindle-ebook.epub"
INTERIOR_PDF = PAPERBACK_DIR / "the-calm-digital-life-paperback-miolo-kdp.pdf"
COVER_PDF = PAPERBACK_DIR / "the-calm-digital-life-paperback-capa-kdp.pdf"
EXTRACTED_TEXT = SOURCE_DIR / "the-calm-digital-life-source-extracted.txt"
METADATA_JSON = BOOK_DIR / "kdp-metadata.json"

TITLE = "The Calm Digital Life"
SUBTITLE = "Pause First. Avoid Scams. Protect Your Money. Stay in Control After 60."
AUTHOR = "Sabino Pereira"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/the-calm-digital-life"))
TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch


@dataclass
class Chapter:
    title: str
    lines: list[str]


EXERCISES = {
    "Chapter 1": [
        ("My Essential Apps", ["The three apps I use most are:", "One app I want to understand better is:", "One app I can ignore for now is:"]),
        ("My Pause Rule", ["When I feel confused, I will pause and:", "The person I can ask before acting is:"]),
    ],
    "Chapter 2": [
        ("Suspicious Call Notes", ["Who called?", "What did they ask me to do?", "What emotion did I feel?", "How will I verify it safely?"]),
    ],
    "Chapter 3": [
        ("Pressure Check", ["The message or call said:", "The urgent words I noticed were:", "What can wait until tomorrow?", "My calm next step is:"]),
    ],
    "Chapter 4": [
        ("Before I Click", ["Who sent this?", "Was I expecting it?", "Can I go directly to the official website instead?", "What will I do before clicking?"]),
    ],
    "Chapter 6": [
        ("Password Plan", ["Accounts I need to protect first:", "Where I will safely store passwords:", "One password habit I will change this week:"]),
    ],
    "Chapter 8": [
        ("Privacy Review", ["Information I should avoid posting publicly:", "Apps or accounts I want to check:", "One privacy setting to review:"]),
    ],
    "Chapter 10": [
        ("Digital Confidence Checklist", ["I pause before responding to urgent messages.", "I verify money requests through another channel.", "I know who to call when unsure.", "I do not share codes or passwords."]),
    ],
    "Chapter 12": [
        ("My Financial Overview", ["Main income sources:", "Main regular expenses:", "Bank or savings accounts I use:", "Trusted person who can help me review this:"]),
    ],
    "Chapter 13": [
        ("Important Documents", ["Where my bills are kept:", "Where insurance documents are kept:", "Where bank documents are kept:", "Who knows where to find them if needed?"]),
    ],
    "Chapter 14": [
        ("Money Boundary Script", ["A phrase I can use when someone pressures me:", "A decision I will not make on the spot:", "A trusted person I can speak to first:"]),
    ],
    "Chapter 15": [
        ("Investment Safety Check", ["Who is offering this?", "What return is promised?", "What risk is being hidden?", "Who will I ask before investing?"]),
    ],
    "Chapter 16": [
        ("Simple Monthly Balance", ["Approximate income:", "Essential expenses:", "Flexible expenses:", "Small adjustment I can make calmly:"]),
    ],
    "Chapter 17": [
        ("Decision Rule", ["Before making a financial decision, I will:", "I will wait this long before saying yes:", "My trusted second opinion is:"]),
    ],
    "Chapter 19": [
        ("Memory Support Page", ["Important task to remember:", "Where I wrote it down:", "Reminder I will use:", "When I will check it again:"]),
    ],
    "Chapter 21": [
        ("My Calm Digital Plan", ["One habit I will keep:", "One risk I will watch for:", "One person I will help or ask for help:", "My rule for urgent messages:"]),
    ],
}


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


def clean_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    line = line.replace("—", "-")
    return line


def extract_source() -> list[str]:
    reader = PdfReader(str(SOURCE_PDF))
    lines: list[str] = []
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        for raw in text.splitlines():
            line = clean_line(raw)
            if not line or line == str(page_num):
                continue
            lines.append(line)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def parse_chapters(lines: list[str]) -> list[Chapter]:
    starts: list[int] = []
    for idx, line in enumerate(lines):
        if line == "Introduction" or re.fullmatch(r"Chapter \d+", line) or line == "Final Note":
            starts.append(idx)
    intro_hits = [idx for idx in starts if lines[idx] == "Introduction"]
    body_start = intro_hits[1] if len(intro_hits) > 1 else starts[0]
    starts = [idx for idx in starts if idx >= body_start]
    chapters: list[Chapter] = []
    for pos, start in enumerate(starts):
        end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
        heading = lines[start]
        body_start = start + 1
        if heading.startswith("Chapter ") and body_start < end:
            title = f"{heading}: {lines[body_start]}"
            body_start += 1
        else:
            title = heading
        body = [line for line in lines[body_start:end] if line != title]
        chapters.append(Chapter(title, body))
    return chapters


def create_cover(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = 1600, 2560
    im = Image.new("RGB", (w, h), "#f3f1e9")
    d = ImageDraw.Draw(im)
    font_dir = "/System/Library/Fonts/Supplemental"
    georgia = f"{font_dir}/Georgia.ttf"
    georgia_bold = f"{font_dir}/Georgia Bold.ttf"
    georgia_italic = f"{font_dir}/Georgia Italic.ttf"
    impact = f"{font_dir}/Impact.ttf"
    navy = "#15243a"
    blue = "#2c6f91"
    ink = "#1b1d20"
    muted = "#73706a"
    green = "#4f8a6b"
    gold = "#d9b45f"
    paper = "#fffdf6"

    d.rectangle([0, 0, w, 770], fill=navy)
    d.rectangle([0, 760, w, 790], fill=gold)
    d.rounded_rectangle([255, 880, 1345, 1885], radius=55, fill=paper, outline=navy, width=10)
    for y in [1020, 1180, 1340, 1500]:
        d.rectangle([320, y, 1280, y + 10], fill="#d8d2c4")
    for y in [1105, 1265, 1425]:
        d.ellipse([340, y, 395, y + 55], outline=green, width=8)
    d.line([354, 1132, 374, 1148], fill=green, width=8)
    d.line([374, 1148, 402, 1112], fill=green, width=8)
    d.rounded_rectangle([930, 1110, 1165, 1570], radius=38, outline=navy, width=8, fill="#eef5f6")
    d.polygon([(1048, 1230), (1130, 1275), (1115, 1405), (1048, 1470), (980, 1405), (965, 1275)], outline=blue, width=8)
    d.line([1005, 1355, 1038, 1392], fill=green, width=9)
    d.line([1038, 1392, 1098, 1315], fill=green, width=9)
    d.line([500, 1690, 930, 1690], fill=ink, width=14)
    d.polygon([(930, 1672), (1015, 1690), (930, 1708)], fill=gold, outline=ink)

    d.text((130, 115), AUTHOR.upper(), font=ImageFont.truetype(georgia_bold, 50), fill="#f3f1e9")
    d.text((130, 255), "THE CALM", font=ImageFont.truetype(impact, 150), fill="#ffffff")
    d.text((130, 405), "DIGITAL LIFE", font=ImageFont.truetype(impact, 150), fill="#ffffff")
    d.text((135, 615), "Pause first. Write it down. Stay in control.", font=ImageFont.truetype(georgia_italic, 62), fill="#d8e6eb")
    d.text((130, 2025), "A practical guide with exercises", font=ImageFont.truetype(georgia, 44), fill=ink)
    d.text((130, 2085), "for safer online decisions after 60.", font=ImageFont.truetype(georgia, 44), fill=ink)
    d.rectangle([130, 2195, 620, 2205], fill=gold)
    d.text((130, 2290), "AVOID SCAMS  /  PROTECT MONEY  /  TAKE NOTES", font=ImageFont.truetype(georgia_bold, 34), fill=muted)
    d.rectangle([80, 80, w - 80, h - 80], outline=navy, width=6)
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


def worksheet_story(title: str, prompts: list[str], styles) -> list:
    story: list = [Spacer(1, 0.2 * inch), paragraph(title, styles["WorksheetTitle"])]
    for prompt in prompts:
        story.append(paragraph(prompt, styles["Prompt"]))
        story.append(Spacer(1, 0.1 * inch))
        for _ in range(3):
            story.append(Spacer(1, 0.24 * inch))
            story.append(LineFlowable())
    return story


class LineFlowable(Flowable):
    def __init__(self):
        super().__init__()

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, 4

    def draw(self):
        canv = self.canv
        canv.saveState()
        canv.setStrokeColor(colors.HexColor("#b8b0a2"))
        canv.setLineWidth(0.7)
        canv.line(0, 0, self.width, 0)
        canv.restoreState()


def build_interior(chapters: list[Chapter]) -> int:
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitleImpact", fontName="Impact", fontSize=34, leading=37, alignment=TA_CENTER, spaceAfter=14))
    styles.add(ParagraphStyle("Subtitle", fontName="Georgia-Italic", fontSize=13.2, leading=19, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Author", fontName="Georgia", fontSize=11, leading=15, alignment=TA_CENTER, spaceBefore=28))
    styles.add(ParagraphStyle("ChapterTitle", fontName="Georgia-Bold", fontSize=20, leading=24, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle("Body", fontName="Georgia", fontSize=12.2, leading=18.2, spaceAfter=7.5))
    styles.add(ParagraphStyle("BookBullet", fontName="Georgia", fontSize=12.0, leading=17.5, leftIndent=14, firstLineIndent=-10, spaceAfter=5))
    styles.add(ParagraphStyle("Toc", fontName="Georgia", fontSize=11.2, leading=17, spaceAfter=2))
    styles.add(ParagraphStyle("SectionNote", fontName="Georgia-Italic", fontSize=11.4, leading=17, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle("WorksheetTitle", fontName="Georgia-Bold", fontSize=17, leading=22, alignment=TA_LEFT, spaceAfter=10))
    styles.add(ParagraphStyle("Prompt", fontName="Georgia-Bold", fontSize=11.6, leading=16, spaceBefore=8, spaceAfter=2))
    styles.add(ParagraphStyle("Small", fontName="Georgia", fontSize=9.5, leading=14))

    doc = BaseDocTemplate(str(INTERIOR_PDF), pagesize=(TRIM_W, TRIM_H), title=f"{TITLE} - Updated Edition", author=AUTHOR)
    odd = Frame(0.68 * inch, 0.72 * inch, TRIM_W - 1.22 * inch, TRIM_H - 1.42 * inch, id="odd")
    even = Frame(0.54 * inch, 0.72 * inch, TRIM_W - 1.22 * inch, TRIM_H - 1.42 * inch, id="even")
    doc.addPageTemplates([
        PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
        PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
    ])
    story: list = [
        Spacer(1, 2.0 * inch),
        Paragraph("THE CALM<br/>DIGITAL LIFE", styles["TitleImpact"]),
        paragraph("Pause First. Write It Down. Stay in Control.", styles["Subtitle"]),
        paragraph("A practical guide with simple exercises for safer online decisions after 60.", styles["Subtitle"]),
        paragraph(AUTHOR, styles["Author"]),
        PageBreak(),
        Spacer(1, 2.0 * inch),
        paragraph("Copyright © 2026 Sabino Pereira. All rights reserved.", styles["Small"]),
        paragraph("This book is for informational purposes only. It does not constitute financial, legal, or professional advice.", styles["Small"]),
        Spacer(1, 0.25 * inch),
        paragraph("Updated edition with practical exercises.", styles["Small"]),
        PageBreak(),
        paragraph("Contents", styles["ChapterTitle"]),
    ]
    for chapter in chapters:
        story.append(paragraph(chapter.title, styles["Toc"]))
        key = chapter.title.split(":")[0]
        if key in EXERCISES:
            story.append(paragraph("  Exercise pages", styles["Toc"]))
    story.append(PageBreak())

    for chapter in chapters:
        story.append(paragraph(chapter.title, styles["ChapterTitle"]))
        for line in chapter.lines:
            if line.startswith("•"):
                story.append(paragraph(line, styles["BookBullet"]))
            elif len(line) < 55 and not line.endswith(".") and not line.endswith("?") and not line.startswith("“"):
                story.append(paragraph(line, styles["SectionNote"]))
            else:
                story.append(paragraph(line, styles["Body"]))
        key = chapter.title.split(":")[0]
        if key in EXERCISES:
            story.append(PageBreak())
            for idx, (exercise_title, prompts) in enumerate(EXERCISES[key]):
                if idx:
                    story.append(PageBreak())
                story.extend(worksheet_story(exercise_title, prompts, styles))
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


def draw_exercise_page(c: canvas.Canvas, title: str, prompts: list[str]) -> None:
    margin_x = 0.58 * inch
    top_y = TRIM_H - 0.72 * inch
    c.setFillColor(colors.black)
    c.setFont("Georgia-Bold", 27)
    c.drawString(margin_x, top_y, title)
    y = top_y - 0.62 * inch
    for prompt in prompts:
        c.setFont("Georgia-Bold", 18)
        c.drawString(margin_x, y, prompt)
        y -= 0.55 * inch
        c.setStrokeColor(colors.HexColor("#b8b0a2"))
        c.setLineWidth(0.8)
        for _ in range(3):
            c.line(margin_x, y, TRIM_W - margin_x, y)
            y -= 0.42 * inch
        y -= 0.12 * inch
        if y < 1.0 * inch:
            break
    c.showPage()


def create_exercise_pdf(path: Path) -> int:
    c = canvas.Canvas(str(path), pagesize=(TRIM_W, TRIM_H))
    c.setTitle("The Calm Digital Life - Practical Exercise Pages")
    c.setAuthor(AUTHOR)

    c.setFont("Georgia-Bold", 28)
    c.drawCentredString(TRIM_W / 2, 5.35 * inch, "Practical Exercise Pages")
    c.setFont("Georgia-Italic", 15)
    c.drawCentredString(TRIM_W / 2, 4.85 * inch, "Use these pages to pause, write things down, and decide calmly.")
    c.showPage()

    page_count = 1
    for exercises in EXERCISES.values():
        for title, prompts in exercises:
            draw_exercise_page(c, title, prompts)
            page_count += 1
    c.save()
    return page_count


def build_interior_from_source() -> int:
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    exercise_pdf = PAPERBACK_DIR / "the-calm-digital-life-exercise-pages.tmp.pdf"
    exercise_count = create_exercise_pdf(exercise_pdf)
    writer = PdfWriter()
    source = PdfReader(str(SOURCE_PDF))
    for page in source.pages:
        writer.add_page(page)
    exercises = PdfReader(str(exercise_pdf))
    for page in exercises.pages:
        writer.add_page(page)
    with INTERIOR_PDF.open("wb") as handle:
        writer.write(handle)
    exercise_pdf.unlink(missing_ok=True)
    page_count = len(PdfReader(str(INTERIOR_PDF)).pages)
    if page_count % 2:
        add_blank_page(INTERIOR_PDF)
        page_count += 1
    return page_count


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
    c.setFillColor(colors.HexColor("#15243a"))
    c.rect(0, 0, cover_w, cover_h, stroke=0, fill=1)
    c.drawImage(str(COVER_JPG), front_x, 0, width=TRIM_W + BLEED, height=cover_h, preserveAspectRatio=False, mask="auto")

    safe_x = back_x + 0.46 * inch
    y = cover_h - 0.82 * inch
    c.setFont("Impact", 25)
    c.setFillColor(colors.white)
    c.drawString(safe_x, y, "THE CALM DIGITAL LIFE")
    y -= 0.34 * inch
    c.setStrokeColor(colors.HexColor("#d9b45f"))
    c.setLineWidth(3)
    c.line(safe_x, y, safe_x + 1.65 * inch, y)
    y -= 0.36 * inch
    blurb = (
        "A practical guide with simple exercises for safer online decisions after 60. "
        "Read the lesson, pause, write things down, and build calm habits around messages, calls, passwords, money, and pressure."
    )
    y = draw_wrapped_text(c, blurb, safe_x, y, TRIM_W - 0.95 * inch, "Georgia", 12, 18, colors.HexColor("#f1efe6"))
    y -= 0.2 * inch
    y = draw_wrapped_text(c, "Pause first. Write it down. Stay in control.", safe_x, y, TRIM_W - 1.0 * inch, "Georgia-Italic", 13, 20, colors.white)
    y -= 0.24 * inch
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
        c.setFont("Impact", max(6, min(11, spine * 0.42)))
        c.setFillColor(colors.white)
        c.drawCentredString(0, -spine * 0.18, "THE CALM DIGITAL LIFE")
        c.setFont("Georgia", max(4.5, min(7.2, spine * 0.26)))
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


def write_epub(chapters: list[Chapter]) -> None:
    build_dir = EBOOK_DIR / "ebook-build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    (build_dir / "META-INF").mkdir(parents=True)
    (build_dir / "OEBPS/images").mkdir(parents=True)

    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def xhtml_page(title: str, body: str) -> str:
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
    write(build_dir / "OEBPS/styles.css", """body{font-family:Georgia,serif;line-height:1.55;margin:0 7%;color:#151515}.chapter{break-before:page;page-break-before:always}h1{font-size:1.45em;line-height:1.18;margin:1em 0}.cover{text-align:center;margin:0}.cover img,figure img{max-width:100%;height:auto}.exercise{break-before:page;page-break-before:always;border-top:1px solid #aaa;margin-top:1.4em;padding-top:1em}p{margin:0 0 .8em}.prompt{font-weight:bold;margin-top:1em}.line{border-bottom:1px solid #aaa;height:1.6em}""")
    write(build_dir / "OEBPS/cover.xhtml", xhtml_page("Cover", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="The Calm Digital Life cover"/></section>'))
    shutil.copyfile(COVER_JPG, build_dir / "OEBPS/images/cover.jpg")
    nav_items, spine_items, manifest_items = [], [], []
    for i, chapter in enumerate(chapters, 1):
        fname = f"chapter-{i:02d}.xhtml"
        nav_items.append(f'<li><a href="{fname}">{html.escape(chapter.title)}</a></li>')
        spine_items.append(f'<itemref idref="chapter-{i:02d}"/>')
        manifest_items.append(f'<item id="chapter-{i:02d}" href="{fname}" media-type="application/xhtml+xml"/>')
        parts = [f'<section class="chapter" epub:type="chapter"><h1>{html.escape(chapter.title)}</h1>']
        for line in chapter.lines:
            parts.append(f"<p>{html.escape(line)}</p>")
        key = chapter.title.split(":")[0]
        if key in EXERCISES:
            parts.append('<section class="exercise"><h2>Exercise pages</h2>')
            for ex_title, prompts in EXERCISES[key]:
                parts.append(f"<h3>{html.escape(ex_title)}</h3>")
                for prompt in prompts:
                    parts.append(f'<p class="prompt">{html.escape(prompt)}</p><p class="line"></p><p class="line"></p>')
            parts.append("</section>")
        parts.append("</section>")
        write(build_dir / "OEBPS" / fname, xhtml_page(chapter.title, "\n".join(parts)))
    write(build_dir / "OEBPS/nav.xhtml", xhtml_page("Contents", f'<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{"".join(nav_items)}</ol></nav>'))
    write(build_dir / "OEBPS/content.opf", f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{BOOK_ID}</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>en</dc:language><dc:publisher>{AUTHOR}</dc:publisher><meta name="cover" content="cover-image"/><meta property="dcterms:modified">2026-05-19T21:00:00Z</meta></metadata>
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
        "author": AUTHOR,
        "edition": "Updated edition with practical exercises",
        "kdp_setup": {
            "trim_size": "6 x 9 in",
            "interior": "Black & white",
            "paper": "White paper",
            "interior_bleed": "No bleed",
            "cover_finish": "Matte recommended",
        },
        "files": {
            "paperback_interior_pdf": "paperback/the-calm-digital-life-paperback-miolo-kdp.pdf",
            "paperback_cover_pdf": "paperback/the-calm-digital-life-paperback-capa-kdp.pdf",
            "ebook_epub": "ebook/the-calm-digital-life-kindle-ebook.epub",
            "ebook_cover_jpg": "ebook/the-calm-digital-life-ebook-cover.jpg",
        },
        "print_specs": specs,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    register_fonts()
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    create_cover(COVER_JPG)
    chapters = parse_chapters(extract_source())
    if len(chapters) < 20:
        raise SystemExit(f"Expected full chapter set, found {len(chapters)}")
    page_count = build_interior_from_source()
    specs = build_cover_pdf(page_count)
    write_epub(chapters)
    write_metadata(specs)
    print(json.dumps(specs, indent=2))


if __name__ == "__main__":
    main()
