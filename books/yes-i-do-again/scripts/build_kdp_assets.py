#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
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
MANUSCRIPT = ROOT / "manuscript/yes-i-do-again.md"
SOURCE_COVER = ROOT / "cover/yes-i-do-again-english-cover.png"
EBOOK_DIR = ROOT / "amazon-kdp/english/ebook"
PAPERBACK_DIR = ROOT / "amazon-kdp/english/paperback"
METADATA_DIR = ROOT / "amazon-kdp/english/metadata"
BUILD_DIR = ROOT / "build/kdp"

EPUB_PATH = EBOOK_DIR / "yes-i-do-again-kindle.epub"
EBOOK_COVER = EBOOK_DIR / "yes-i-do-again-ebook-cover.jpg"
INTERIOR_PDF = PAPERBACK_DIR / "yes-i-do-again-paperback-interior.pdf"
COVER_PDF = PAPERBACK_DIR / "yes-i-do-again-paperback-cover.pdf"
METADATA_JSON = METADATA_DIR / "kdp-metadata.json"
METADATA_MD = METADATA_DIR / "kdp-listing-copy.md"

TITLE = "Yes, I Do... Again."
AUTHOR = "Sabino Pereira"
TAGLINE = "Knowing everything you know now, would you still choose the same person?"
LANGUAGE = "en-US"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/yes-i-do-again"))

TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch


@dataclass
class Section:
    title: str
    paragraphs: list[str]
    kind: str = "chapter"


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    fonts = {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
    }
    for name, path in fonts.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def parse_manuscript() -> list[Section]:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    sections: list[Section] = []
    current: Section | None = None
    buffer: list[str] = []

    def flush_paragraph() -> None:
        nonlocal buffer
        if current is not None and buffer:
            current.paragraphs.append(" ".join(line.strip() for line in buffer).strip())
            buffer = []

    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            flush_paragraph()
            heading = line[3:].strip()
            current = Section(heading, [], "epilogue" if heading.lower().startswith("epilogue") else "chapter")
            sections.append(current)
        elif line.startswith("# "):
            continue
        elif not line:
            flush_paragraph()
        elif current is not None:
            buffer.append(line)
    flush_paragraph()
    if not sections:
        raise RuntimeError("No chapters found in manuscript")
    return sections


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)
    return escaped


def epub_xhtml(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
{body}
</body>
</html>
'''


def make_ebook_cover() -> None:
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE_COVER) as src:
        image = src.convert("RGB")
        target_ratio = 1600 / 2560
        source_ratio = image.width / image.height
        if source_ratio > target_ratio:
            new_w = round(image.height * target_ratio)
            left = (image.width - new_w) // 2
            image = image.crop((left, 0, left + new_w, image.height))
        elif source_ratio < target_ratio:
            new_h = round(image.width / target_ratio)
            top = (image.height - new_h) // 2
            image = image.crop((0, top, image.width, top + new_h))
        image = image.resize((1600, 2560), Image.Resampling.LANCZOS)
        image.save(EBOOK_COVER, "JPEG", quality=95, optimize=True, progressive=True, dpi=(300, 300))


def build_epub(sections: list[Section]) -> None:
    make_ebook_cover()
    build = BUILD_DIR / "epub"
    if build.exists():
        shutil.rmtree(build)
    (build / "META-INF").mkdir(parents=True)
    (build / "OEBPS/images").mkdir(parents=True)
    (build / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (build / "META-INF/container.xml").write_text(
        '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>\n''',
        encoding="utf-8",
    )
    css = '''body { color: #171717; font-family: serif; line-height: 1.55; margin: 0 6%; }
p { margin: 0; text-indent: 1.25em; }
p.first, p.dialogue, p.message { text-indent: 0; }
p.message { font-style: italic; margin: 0.55em 1.2em; }
h1 { font-size: 1.55em; line-height: 1.2; margin: 1.8em 0 1.4em; text-align: center; }
.chapter { break-before: page; page-break-before: always; }
.cover { margin: 0; padding: 0; text-align: center; }
.cover img { height: auto; max-height: 100%; max-width: 100%; }
nav ol { line-height: 1.8; }
'''
    (build / "OEBPS/styles.css").write_text(css, encoding="utf-8")
    shutil.copyfile(EBOOK_COVER, build / "OEBPS/images/cover.jpg")
    (build / "OEBPS/cover.xhtml").write_text(
        epub_xhtml("Cover", f'<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Cover of {html.escape(TITLE)}"/></section>'),
        encoding="utf-8",
    )

    for index, section in enumerate(sections, 1):
        body = [f'<section class="chapter" epub:type="{section.kind}" id="section-{index:02d}">', f"<h1>{html.escape(section.title)}</h1>"]
        for p_index, paragraph in enumerate(section.paragraphs):
            stripped = paragraph.lstrip()
            cls = "first" if p_index == 0 else ""
            if paragraph.startswith("*") and paragraph.endswith("*"):
                cls = "message"
            elif stripped.startswith(("“", '"')):
                cls = "dialogue"
            body.append(f'<p class="{cls}">{inline_markup(paragraph)}</p>')
        body.append("</section>")
        (build / f"OEBPS/section-{index:02d}.xhtml").write_text(epub_xhtml(section.title, "\n".join(body)), encoding="utf-8")

    nav_items = "\n".join(
        f'      <li><a href="section-{i:02d}.xhtml">{html.escape(section.title)}</a></li>'
        for i, section in enumerate(sections, 1)
    )
    nav_body = f'''<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>\n{nav_items}\n</ol></nav>
<nav epub:type="landmarks" hidden="hidden"><ol>
<li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
<li><a epub:type="bodymatter" href="section-01.xhtml">Beginning</a></li>
</ol></nav>'''
    (build / "OEBPS/nav.xhtml").write_text(epub_xhtml("Contents", nav_body), encoding="utf-8")

    manifest_sections = "\n".join(
        f'    <item id="section-{i:02d}" href="section-{i:02d}.xhtml" media-type="application/xhtml+xml"/>'
        for i in range(1, len(sections) + 1)
    )
    spine_sections = "\n".join(f'    <itemref idref="section-{i:02d}"/>' for i in range(1, len(sections) + 1))
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{LANGUAGE}">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="bookid">{BOOK_ID}</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title>
  <dc:creator>{html.escape(AUTHOR)}</dc:creator><dc:language>{LANGUAGE}</dc:language>
  <dc:publisher>{html.escape(AUTHOR)}</dc:publisher><dc:description>{html.escape(TAGLINE)}</dc:description>
  <meta property="dcterms:modified">{modified}</meta><meta name="cover" content="cover-image"/>
</metadata>
<manifest>
  <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  <item id="style" href="styles.css" media-type="text/css"/>
  <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
  <item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
{manifest_sections}
</manifest>
<spine><itemref idref="cover" linear="no"/>{spine_sections}</spine>
</package>\n'''
    (build / "OEBPS/content.opf").write_text(opf, encoding="utf-8")

    EPUB_PATH.unlink(missing_ok=True)
    with zipfile.ZipFile(EPUB_PATH, "w") as archive:
        archive.write(build / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(build.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                archive.write(path, path.relative_to(build).as_posix(), compress_type=zipfile.ZIP_DEFLATED)


def draw_page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFillColor(colors.HexColor("#555555"))
    canv.setFont("Georgia", 9)
    outer_x = TRIM_W - 0.58 * inch if doc.page % 2 else 0.58 * inch
    canv.drawCentredString(outer_x, 0.42 * inch, str(doc.page))
    canv.restoreState()


def reportlab_text(text: str) -> str:
    return inline_markup(text).replace("—", "&mdash;")


def add_blank_page(pdf_path: Path) -> None:
    blank_path = BUILD_DIR / "blank.pdf"
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


def build_interior(sections: list[Section]) -> int:
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitlePage", fontName="Georgia", fontSize=28, leading=34, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Tagline", fontName="Georgia-Italic", fontSize=11, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#555555")))
    styles.add(ParagraphStyle("Author", fontName="Georgia", fontSize=12, leading=16, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Chapter", fontName="Georgia", fontSize=18, leading=23, alignment=TA_CENTER, spaceAfter=26))
    styles.add(ParagraphStyle("Body", fontName="Georgia", fontSize=10.8, leading=15.4, alignment=TA_JUSTIFY, firstLineIndent=16, spaceAfter=0, allowWidows=0, allowOrphans=0))
    styles.add(ParagraphStyle("First", parent=styles["Body"], firstLineIndent=0))
    styles.add(ParagraphStyle("Message", parent=styles["Body"], fontName="Georgia-Italic", firstLineIndent=0, leftIndent=18, rightIndent=18, spaceBefore=4, spaceAfter=4))
    styles.add(ParagraphStyle("Copyright", fontName="Georgia", fontSize=9, leading=14, alignment=TA_LEFT, textColor=colors.HexColor("#444444")))

    doc = BaseDocTemplate(str(INTERIOR_PDF), pagesize=(TRIM_W, TRIM_H), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0, title=TITLE, author=AUTHOR)
    odd = Frame(0.78 * inch, 0.68 * inch, TRIM_W - 1.43 * inch, TRIM_H - 1.36 * inch, id="odd")
    even = Frame(0.65 * inch, 0.68 * inch, TRIM_W - 1.43 * inch, TRIM_H - 1.36 * inch, id="even")
    doc.addPageTemplates([
        PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
        PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
    ])

    story = [
        Spacer(1, 2.05 * inch), Paragraph(TITLE.upper(), styles["TitlePage"]), Spacer(1, 0.25 * inch),
        Paragraph(TAGLINE, styles["Tagline"]), Spacer(1, 1.6 * inch), Paragraph(AUTHOR.upper(), styles["Author"]), PageBreak(),
        Spacer(1, 1.75 * inch), Paragraph(f"Copyright © 2026 {AUTHOR}", styles["Copyright"]), Spacer(1, 0.16 * inch),
        Paragraph("All rights reserved.", styles["Copyright"]), Spacer(1, 0.2 * inch),
        Paragraph("This is a work of fiction. Names, characters, places, and incidents are products of the author’s imagination or are used fictitiously.", styles["Copyright"]),
        Spacer(1, 0.2 * inch), Paragraph("First English edition.", styles["Copyright"]), PageBreak(),
    ]
    for section in sections:
        story.extend([Spacer(1, 1.15 * inch), Paragraph(reportlab_text(section.title), styles["Chapter"])])
        for idx, paragraph in enumerate(section.paragraphs):
            if paragraph.startswith("*") and paragraph.endswith("*"):
                style = styles["Message"]
            elif idx == 0:
                style = styles["First"]
            else:
                style = styles["Body"]
            story.append(Paragraph(reportlab_text(paragraph), style))
        story.append(PageBreak())
    story.extend([Spacer(1, 3.2 * inch), Paragraph("END", styles["Tagline"])])
    doc.build(story)
    page_count = len(PdfReader(str(INTERIOR_PDF)).pages)
    while page_count < 24 or page_count % 2:
        add_blank_page(INTERIOR_PDF)
        page_count += 1
    return page_count


def wrapped_lines(canv: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or canv.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_print_cover(page_count: int) -> dict[str, float | int | str]:
    spine = page_count * WHITE_PAPER_SPINE_PER_PAGE
    width = BLEED + TRIM_W + spine + TRIM_W + BLEED
    height = TRIM_H + 2 * BLEED
    back_x = BLEED
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine

    c = canvas.Canvas(str(COVER_PDF), pagesize=(width, height))
    c.setTitle(f"{TITLE} - Paperback Cover")
    c.setAuthor(AUTHOR)
    c.setFillColor(colors.HexColor("#1b252c"))
    c.rect(0, 0, width, height, stroke=0, fill=1)

    with Image.open(SOURCE_COVER) as src:
        rgb = src.convert("RGB").resize((1838, 2775), Image.Resampling.LANCZOS)
        print_front = BUILD_DIR / "print-front.jpg"
        print_front.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(print_front, "JPEG", quality=96, optimize=True, dpi=(300, 300))
    c.drawImage(str(print_front), front_x, 0, width=TRIM_W + BLEED, height=height, preserveAspectRatio=False, mask="auto")

    c.setFillColor(colors.HexColor("#d9e1e4"))
    c.setFont("Georgia", 20)
    c.drawString(back_x + 0.55 * inch, height - 0.8 * inch, "WOULD YOU SAY YES AGAIN?")
    c.setStrokeColor(colors.HexColor("#9ab3bc"))
    c.setLineWidth(1.2)
    c.line(back_x + 0.55 * inch, height - 0.98 * inch, back_x + 2.8 * inch, height - 0.98 * inch)

    blurb = (
        "Ten years into their marriage, Tomás and Leonor have built a life that works: a home, a son, shared routines, and a silence neither knows how to name. Then the Renewal Program asks them to choose again. Renew. Renegotiate. Separate. End. As the deadline approaches, every kindness begins to look like a campaign, every sacrifice becomes evidence, and the possibility of another life starts to feel dangerously real."
    )
    y = height - 1.42 * inch
    c.setFillColor(colors.HexColor("#f2f1ec"))
    for line in wrapped_lines(c, blurb, "Georgia", 11.2, TRIM_W - 1.1 * inch):
        c.setFont("Georgia", 11.2)
        c.drawString(back_x + 0.55 * inch, y, line)
        y -= 0.19 * inch

    y -= 0.2 * inch
    c.setFont("Georgia-Italic", 11)
    c.setFillColor(colors.HexColor("#b8cbd2"))
    for line in wrapped_lines(c, TAGLINE, "Georgia-Italic", 11, TRIM_W - 1.2 * inch):
        c.drawString(back_x + 0.55 * inch, y, line)
        y -= 0.19 * inch

    c.setFont("Georgia", 10)
    c.setFillColor(colors.HexColor("#f2f1ec"))
    c.drawString(back_x + 0.55 * inch, 0.62 * inch, AUTHOR.upper())

    barcode_w, barcode_h = 2.0 * inch, 1.2 * inch
    c.setFillColor(colors.white)
    c.rect(back_x + TRIM_W - barcode_w - 0.35 * inch, 0.42 * inch, barcode_w, barcode_h, stroke=0, fill=1)

    if page_count >= 79:
        c.saveState()
        c.translate(spine_x + spine / 2, height / 2)
        c.rotate(90)
        c.setFillColor(colors.HexColor("#f2f1ec"))
        c.setFont("Georgia", min(10, max(6, spine * 0.35)))
        c.drawCentredString(0, 0, f"{TITLE.upper()}   •   {AUTHOR.upper()}")
        c.restoreState()

    c.showPage()
    c.save()
    return {
        "page_count": page_count,
        "trim_size": "6 x 9 in",
        "paper": "White paper",
        "interior": "Black & white, no bleed",
        "cover_finish": "Matte recommended",
        "spine_width_in": round(spine / inch, 6),
        "cover_width_in": round(width / inch, 6),
        "cover_height_in": round(height / inch, 6),
    }


def write_metadata(specs: dict[str, float | int | str]) -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "title": TITLE,
        "subtitle": "",
        "author": AUTHOR,
        "language": "English",
        "edition": "First English edition",
        "description": (
            "Ten years into their marriage, Tomás and Leonor have built a life that works—but they no longer know whether they are still choosing it. In a society where couples must periodically renew, renegotiate, or end their relationships, their ten-year Identity Review forces every quiet resentment, hidden sacrifice, temptation, and unrealized future into the open. Yes, I Do... Again. is an intimate speculative novel about love after passion, the comfort of routine, and the courage required to choose consciously."
        ),
        "keywords": [
            "marriage fiction", "relationship novel", "speculative romance", "second chance marriage",
            "domestic fiction", "love after passion", "emotional infidelity"
        ],
        "suggested_categories": [
            "FICTION / Family Life / Marriage & Divorce",
            "FICTION / Romance / Later in Life",
            "FICTION / Science Fiction / Social Science Fiction",
        ],
        "audience": "Adult",
        "territories": "Worldwide rights, if owned by the author",
        "files": {
            "ebook_epub": "../ebook/yes-i-do-again-kindle.epub",
            "ebook_cover": "../ebook/yes-i-do-again-ebook-cover.jpg",
            "paperback_interior": "../paperback/yes-i-do-again-paperback-interior.pdf",
            "paperback_cover": "../paperback/yes-i-do-again-paperback-cover.pdf",
        },
        "print_specs": specs,
    }
    METADATA_JSON.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    copy = f'''# KDP Listing Copy — {TITLE}

## Title

{TITLE}

## Author

{AUTHOR}

## Book description

{metadata["description"]}

## Keywords

''' + "\n".join(f"- {item}" for item in metadata["keywords"]) + "\n\n## Suggested categories\n\n" + "\n".join(f"- {item}" for item in metadata["suggested_categories"]) + f'''\n\n## Paperback setup

- Trim: 6 × 9 inches
- Interior: black and white, white paper, no bleed
- Cover finish: matte recommended
- Reading direction: left to right
- Final page count: {specs["page_count"]}
'''
    METADATA_MD.write_text(copy, encoding="utf-8")


def main() -> None:
    register_fonts()
    sections = parse_manuscript()
    build_epub(sections)
    page_count = build_interior(sections)
    specs = build_print_cover(page_count)
    write_metadata(specs)
    print(json.dumps(specs, indent=2))


if __name__ == "__main__":
    main()
