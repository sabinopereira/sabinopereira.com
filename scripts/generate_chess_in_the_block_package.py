#!/usr/bin/env python3
from __future__ import annotations

import html
import json
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
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "books/xadrez-no-comando/chess-in-the-block-manuscript-clean.md"
SOURCE_BRIEF = ROOT / "books/xadrez-no-comando/chess-in-the-block-cover-brief.md"
FRONT_COVER = ROOT / "books/chess-in-the-block/cover/chess-in-the-block-cover-alt-5-rook.png"
OUT_DIR = ROOT / "books/chess-in-the-block"
PAPERBACK_DIR = OUT_DIR / "paperback"
EBOOK_DIR = OUT_DIR / "ebook"
PREVIEWS_DIR = OUT_DIR / "previews"
EPUB_BUILD_DIR = OUT_DIR / "ebook-build"

TITLE = "Chess in the Block"
AUTHOR = "Sabino Pereira"
SUBTITLE = "Survival, silence, pressure, love, loss, and learning how to move without losing yourself."
DESCRIPTION = (
    "Chess in the Block is a reflective book about survival, silence, pressure, love, loss, class, family, and maturity. "
    "Using chess as a metaphor for life on the block, each piece becomes a way to understand the invisible strategies people use to survive without losing themselves."
)

TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch


@dataclass
class Chapter:
    title: str
    paragraphs: list[str]


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    fonts = {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
        "Impact": font_dir / "Impact.ttf",
    }
    for name, path in fonts.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def read_clean_manuscript() -> list[Chapter]:
    text = SOURCE_MD.read_text(encoding="utf-8")
    chapters: list[Chapter] = []
    current_title: str | None = None
    current_lines: list[str] = []
    skip_sections = {"Subtitle", "Table of Contents"}

    def flush() -> None:
        nonlocal current_title, current_lines
        if not current_title or current_title in skip_sections:
            current_title = None
            current_lines = []
            return
        paragraphs = [p.strip() for p in "\n".join(current_lines).split("\n\n") if p.strip()]
        chapters.append(Chapter(current_title, paragraphs))
        current_title = None
        current_lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_lines = []
        elif current_title:
            current_lines.append(line)
    flush()
    return chapters


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    safe = html.escape(text).replace("\n", "<br/>")
    safe = safe.replace("&lt;br/&gt;", "<br/>")
    return Paragraph(safe, style)


def draw_page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFont("Georgia", 9)
    canv.setFillColor(colors.HexColor("#555555"))
    canv.drawCentredString(TRIM_W / 2, 0.42 * inch, str(doc.page))
    canv.restoreState()


def build_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "BookTitle",
            fontName="Impact",
            fontSize=42,
            leading=44,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            "SubtitleBook",
            fontName="Georgia-Italic",
            fontSize=12.5,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Author",
            fontName="Georgia",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceBefore=34,
        )
    )
    styles.add(
        ParagraphStyle(
            "ChapterTitle",
            fontName="Impact",
            fontSize=25,
            leading=28,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#111111"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodyBook",
            fontName="Georgia",
            fontSize=11.15,
            leading=16.4,
            spaceAfter=7.0,
            textColor=colors.HexColor("#151515"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Toc",
            fontName="Georgia",
            fontSize=11.4,
            leading=19,
            textColor=colors.HexColor("#151515"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Copyright",
            fontName="Georgia",
            fontSize=10.8,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#151515"),
            spaceAfter=8,
        )
    )
    return styles


def build_interior(chapters: list[Chapter], output_pdf: Path) -> int:
    styles = build_styles()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output_pdf),
        pagesize=(TRIM_W, TRIM_H),
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
        title=f"{TITLE} - Paperback Interior",
        author=AUTHOR,
    )
    odd = Frame(0.64 * inch, 0.72 * inch, TRIM_W - 1.18 * inch, TRIM_H - 1.42 * inch, id="odd")
    even = Frame(0.54 * inch, 0.72 * inch, TRIM_W - 1.18 * inch, TRIM_H - 1.42 * inch, id="even")
    doc.addPageTemplates(
        [
            PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
            PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
        ]
    )

    story: list = [NextPageTemplate("Even")]
    story.extend(
        [
            Spacer(1, 2.1 * inch),
            paragraph("CHESS<br/>IN THE<br/>BLOCK", styles["BookTitle"]),
            Spacer(1, 0.15 * inch),
            paragraph(SUBTITLE, styles["SubtitleBook"]),
            paragraph(AUTHOR, styles["Author"]),
            PageBreak(),
            Spacer(1, 2.0 * inch),
            paragraph(TITLE, styles["SubtitleBook"]),
            Spacer(1, 0.25 * inch),
            paragraph(f"Copyright (c) 2026 {AUTHOR}. All rights reserved.", styles["Copyright"]),
            paragraph("No part of this book may be reproduced without permission from the author, except for brief quotations used for review or commentary.", styles["Copyright"]),
            Spacer(1, 0.3 * inch),
            paragraph("First English-language edition.", styles["Copyright"]),
            PageBreak(),
            paragraph("Table of Contents", styles["ChapterTitle"]),
        ]
    )
    for chapter in chapters:
        story.append(paragraph(chapter.title, styles["Toc"]))
    story.append(PageBreak())

    for chapter in chapters:
        story.extend([paragraph(chapter.title, styles["ChapterTitle"]), Spacer(1, 4)])
        for text in chapter.paragraphs:
            story.append(paragraph(text, styles["BodyBook"]))
        story.append(PageBreak())

    story.extend([Spacer(1, 3.25 * inch), paragraph(TITLE, styles["SubtitleBook"])])
    doc.build(story)

    reader = PdfReader(str(output_pdf))
    page_count = len(reader.pages)
    if page_count % 2:
        blank_path = output_pdf.with_suffix(".blank.pdf")
        blank = canvas.Canvas(str(blank_path), pagesize=(TRIM_W, TRIM_H))
        blank.showPage()
        blank.save()
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_page(PdfReader(str(blank_path)).pages[0])
        with output_pdf.open("wb") as handle:
            writer.write(handle)
        blank_path.unlink()
        page_count += 1
    return page_count


def draw_wrapped_text(
    canv: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font_name: str,
    size: float,
    leading: float,
    color=colors.white,
) -> float:
    canv.setFillColor(color)
    canv.setFont(font_name, size)
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if canv.stringWidth(candidate, font_name, size) <= width:
            line = candidate
        else:
            canv.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        canv.drawString(x, y, line)
        y -= leading
    return y


def make_ebook_cover() -> Path:
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    out = EBOOK_DIR / "chess-in-the-block-ebook-cover.jpg"
    Image.open(FRONT_COVER).convert("RGB").resize((1600, 2560), Image.Resampling.LANCZOS).save(
        out, "JPEG", quality=95, optimize=True
    )
    return out


def build_cover(page_count: int, output_pdf: Path, preview_png: Path) -> dict[str, float]:
    if not FRONT_COVER.exists():
        raise SystemExit(f"Missing selected cover image: {FRONT_COVER}")

    spine = page_count * WHITE_PAPER_SPINE_PER_PAGE
    cover_w = BLEED + TRIM_W + spine + TRIM_W + BLEED
    cover_h = TRIM_H + 2 * BLEED
    back_x = BLEED
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_pdf), pagesize=(cover_w, cover_h))
    c.setTitle(f"{TITLE} - Paperback Cover")
    c.setAuthor(AUTHOR)
    c.setFillColor(colors.black)
    c.rect(0, 0, cover_w, cover_h, stroke=0, fill=1)

    # Back cover.
    safe_x = back_x + 0.42 * inch
    y = cover_h - 0.82 * inch
    c.setFont("Impact", 25)
    c.setFillColor(colors.HexColor("#d69b46"))
    c.drawString(safe_x, y, "CHESS IN THE BLOCK")
    y -= 0.34 * inch
    c.setStrokeColor(colors.HexColor("#d69b46"))
    c.setLineWidth(1.2)
    c.line(safe_x, y, safe_x + 1.35 * inch, y)
    y -= 0.36 * inch
    blurb = (
        "Some people are born into the game protected. Others begin the match already backed against a wall. "
        "Chess in the Block uses chess to speak about survival, silence, pressure, family, love, loss, class, and maturity."
    )
    y = draw_wrapped_text(c, blurb, safe_x, y, TRIM_W - 0.9 * inch, "Georgia", 12.0, 18, colors.HexColor("#eeeeee"))
    y -= 0.20 * inch
    quote = "Big moves don't need noise."
    y = draw_wrapped_text(c, quote, safe_x, y, TRIM_W - 1.05 * inch, "Georgia-Italic", 13.2, 20, colors.white)
    y -= 0.24 * inch
    c.setFont("Georgia", 10.5)
    c.setFillColor(colors.HexColor("#d69b46"))
    c.drawString(safe_x, y, AUTHOR)

    barcode_w = 2.0 * inch
    barcode_h = 1.2 * inch
    c.setFillColor(colors.white)
    c.rect(back_x + TRIM_W - barcode_w - 0.35 * inch, 0.42 * inch, barcode_w, barcode_h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Georgia", 6.5)
    c.drawCentredString(back_x + TRIM_W - barcode_w / 2 - 0.35 * inch, 0.96 * inch, "Barcode KDP")

    # Spine.
    if page_count > 79:
        c.saveState()
        c.setFillColor(colors.HexColor("#050505"))
        c.rect(spine_x, 0, spine, cover_h, stroke=0, fill=1)
        c.translate(spine_x + spine / 2, cover_h / 2)
        c.rotate(90)
        c.setFont("Impact", max(7, min(12, spine * 0.43)))
        c.setFillColor(colors.HexColor("#d69b46"))
        c.drawCentredString(0, -spine * 0.18, "CHESS IN THE BLOCK")
        c.setFont("Georgia", max(4.7, min(7.4, spine * 0.26)))
        c.setFillColor(colors.white)
        c.drawCentredString(0, spine * 0.28, AUTHOR.upper())
        c.restoreState()

    # Front cover.
    c.drawImage(
        str(FRONT_COVER),
        front_x,
        0,
        width=TRIM_W + BLEED,
        height=cover_h,
        preserveAspectRatio=False,
        mask="auto",
    )
    c.showPage()
    c.save()

    make_cover_preview(preview_png, cover_w, cover_h, spine)
    return {
        "page_count": page_count,
        "trim_width_in": TRIM_W / inch,
        "trim_height_in": TRIM_H / inch,
        "bleed_in": BLEED / inch,
        "spine_width_in": spine / inch,
        "cover_width_in": cover_w / inch,
        "cover_height_in": cover_h / inch,
    }


def make_cover_preview(preview_png: Path, cover_w_pt: float, cover_h_pt: float, spine_pt: float) -> None:
    scale = 110
    w = round(cover_w_pt / inch * scale)
    h = round(cover_h_pt / inch * scale)
    im = Image.new("RGB", (w, h), "black")
    draw = ImageDraw.Draw(im)
    bleed_px = round((BLEED / inch) * scale)
    trim_w_px = round((TRIM_W / inch) * scale)
    spine_px = max(1, round((spine_pt / inch) * scale))
    spine_x = bleed_px + trim_w_px
    front_x = spine_x + spine_px

    front = Image.open(FRONT_COVER).convert("RGB").resize((trim_w_px + bleed_px, h), Image.Resampling.LANCZOS)
    im.paste(front, (front_x, 0))

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 34)
        body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 16)
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 12)
    except OSError:
        title_font = body_font = small_font = ImageFont.load_default()

    x = bleed_px + round(0.42 * scale)
    y = round(0.72 * scale)
    draw.text((x, y), "CHESS IN THE BLOCK", fill=(214, 155, 70), font=title_font)
    y += round(0.65 * scale)
    for line in [
        "Some people are born into the game protected.",
        "Others begin the match already backed",
        "against a wall.",
        "",
        "Big moves don't need noise.",
    ]:
        draw.text((x, y), line, fill=(232, 232, 232), font=body_font)
        y += round(0.26 * scale)
    draw.text((x, y + 14), AUTHOR, fill=(214, 155, 70), font=small_font)
    draw.rectangle(
        [
            bleed_px + trim_w_px - round(2.35 * scale),
            h - round(1.65 * scale),
            bleed_px + trim_w_px - round(0.35 * scale),
            h - round(0.45 * scale),
        ],
        fill="white",
    )
    draw.rectangle([spine_x, 0, spine_x + spine_px, h], fill=(7, 7, 7))
    draw.rectangle([bleed_px, bleed_px, w - bleed_px, h - bleed_px], outline=(180, 180, 180), width=2)
    preview_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(preview_png)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def chapter_filename(index: int) -> str:
    return f"chapter-{index:02d}.xhtml"


def xhtml_page(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
{body}
</body>
</html>
'''


def build_epub_chapter(chapter: Chapter, index: int) -> str:
    body = [f'<section epub:type="chapter" id="chapter-{index:02d}">', f"<h1>{html.escape(chapter.title)}</h1>"]
    for text in chapter.paragraphs:
        body.append(f"<p>{html.escape(text)}</p>")
    body.append("</section>")
    return xhtml_page(chapter.title, "\n".join(body))


def build_epub_nav(chapters: list[Chapter]) -> str:
    items = "\n".join(
        f'      <li><a href="{chapter_filename(i)}">{html.escape(chapter.title)}</a></li>'
        for i, chapter in enumerate(chapters, 1)
    )
    body = f'''  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
{items}
    </ol>
  </nav>
  <nav epub:type="landmarks" hidden="hidden">
    <h2>Guide</h2>
    <ol>
      <li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
      <li><a epub:type="toc" href="nav.xhtml">Table of Contents</a></li>
      <li><a epub:type="bodymatter" href="chapter-01.xhtml">Start</a></li>
    </ol>
  </nav>'''
    return xhtml_page("Table of Contents", body)


def build_ncx(chapters: list[Chapter]) -> str:
    nav_points = []
    for i, chapter in enumerate(chapters, 1):
        nav_points.append(
            f'''    <navPoint id="navPoint-{i}" playOrder="{i}">
      <navLabel><text>{html.escape(chapter.title)}</text></navLabel>
      <content src="{chapter_filename(i)}"/>
    </navPoint>'''
        )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'https://sabinopereira.com/chess-in-the-block')}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{html.escape(TITLE)}</text></docTitle>
  <docAuthor><text>{html.escape(AUTHOR)}</text></docAuthor>
  <navMap>
{chr(10).join(nav_points)}
  </navMap>
</ncx>
'''


def build_opf(chapters: list[Chapter]) -> str:
    book_id = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/chess-in-the-block"))
    manifest_chapters = "\n".join(
        f'    <item id="chapter-{i:02d}" href="{chapter_filename(i)}" media-type="application/xhtml+xml"/>'
        for i, _ in enumerate(chapters, 1)
    )
    spine_chapters = "\n".join(f'    <itemref idref="chapter-{i:02d}"/>' for i, _ in enumerate(chapters, 1))
    return f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{book_id}</dc:identifier>
    <dc:title>{html.escape(TITLE)}</dc:title>
    <dc:creator>{html.escape(AUTHOR)}</dc:creator>
    <dc:language>en</dc:language>
    <dc:publisher>{html.escape(AUTHOR)}</dc:publisher>
    <dc:description>{html.escape(DESCRIPTION)}</dc:description>
    <meta name="cover" content="cover-image"/>
    <meta property="dcterms:modified">2026-05-22T12:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="style" href="styles.css" media-type="text/css"/>
    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
    <item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
{manifest_chapters}
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover" linear="no"/>
{spine_chapters}
  </spine>
</package>
'''


def build_epub(chapters: list[Chapter]) -> Path:
    if EPUB_BUILD_DIR.exists():
        shutil.rmtree(EPUB_BUILD_DIR)
    (EPUB_BUILD_DIR / "META-INF").mkdir(parents=True)
    (EPUB_BUILD_DIR / "OEBPS/images").mkdir(parents=True)
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)

    cover_jpg = make_ebook_cover()
    epub_path = EBOOK_DIR / "chess-in-the-block-kindle-ebook.epub"
    write(EPUB_BUILD_DIR / "mimetype", "application/epub+zip")
    write(
        EPUB_BUILD_DIR / "META-INF/container.xml",
        '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
''',
    )
    write(
        EPUB_BUILD_DIR / "OEBPS/styles.css",
        """body {
  color: #151515;
  font-family: Georgia, serif;
  line-height: 1.55;
  margin: 0 6%;
}
h1 {
  font-family: Georgia, serif;
  font-size: 1.65em;
  line-height: 1.15;
  margin: 1.1em 0 0.8em;
}
p {
  margin: 0 0 0.85em;
}
.cover {
  margin: 0;
  padding: 0;
  text-align: center;
}
.cover img {
  height: auto;
  max-width: 100%;
}
nav ol {
  line-height: 1.8;
}
""",
    )
    write(EPUB_BUILD_DIR / "OEBPS/nav.xhtml", build_epub_nav(chapters))
    write(EPUB_BUILD_DIR / "OEBPS/toc.ncx", build_ncx(chapters))
    write(EPUB_BUILD_DIR / "OEBPS/content.opf", build_opf(chapters))
    write(
        EPUB_BUILD_DIR / "OEBPS/cover.xhtml",
        xhtml_page("Cover", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Cover of Chess in the Block"/></section>'),
    )
    for i, chapter in enumerate(chapters, 1):
        write(EPUB_BUILD_DIR / "OEBPS" / chapter_filename(i), build_epub_chapter(chapter, i))
    shutil.copyfile(cover_jpg, EPUB_BUILD_DIR / "OEBPS/images/cover.jpg")

    if epub_path.exists():
        epub_path.unlink()
    with zipfile.ZipFile(epub_path, "w") as zf:
        zf.write(EPUB_BUILD_DIR / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for file in sorted(EPUB_BUILD_DIR.rglob("*")):
            if file.is_file() and file.name != "mimetype":
                zf.write(file, file.relative_to(EPUB_BUILD_DIR), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(EPUB_BUILD_DIR)
    return epub_path


def write_metadata(specs: dict[str, float]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "title": TITLE,
        "author": AUTHOR,
        "language": "English",
        "format": "Paperback and Kindle eBook",
        "kdp_setup": {
            "trim_size": "6 x 9 in",
            "interior": "Black and white",
            "paper": "White paper",
            "bleed": "No bleed for interior",
            "cover_finish": "Matte recommended",
            "reading_direction": "Left to Right",
        },
        "files": {
            "paperback_interior_pdf": "paperback/chess-in-the-block-paperback-interior-kdp.pdf",
            "paperback_cover_pdf": "paperback/chess-in-the-block-paperback-cover-kdp.pdf",
            "ebook_epub": "ebook/chess-in-the-block-kindle-ebook.epub",
            "ebook_cover_jpg": "ebook/chess-in-the-block-ebook-cover.jpg",
            "cover_preview_png": "previews/chess-in-the-block-paperback-spread-preview.png",
        },
        "description_en": DESCRIPTION,
        "keywords_suggested": [
            "chess metaphor",
            "urban life",
            "survival",
            "emotional growth",
            "personal essays",
            "resilience",
            "family",
            "masculinity",
            "social class",
            "self reflection",
        ],
        "categories_suggested": [
            "Literary Collections / Essays",
            "Self-Help / Personal Growth / General",
            "Biography & Autobiography / Personal Memoirs",
            "Social Science / Sociology / Urban",
        ],
        "print_specs": specs,
    }
    (OUT_DIR / "kdp-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    readme = f"""# Chess in the Block - Amazon KDP Package

Files prepared for Amazon KDP paperback and Kindle/eBook upload.

## Upload Files

- Paperback interior/manuscript: `paperback/chess-in-the-block-paperback-interior-kdp.pdf`
- Paperback cover: `paperback/chess-in-the-block-paperback-cover-kdp.pdf`
- Kindle/eBook manuscript: `ebook/chess-in-the-block-kindle-ebook.epub`
- Kindle/eBook cover: `ebook/chess-in-the-block-ebook-cover.jpg`
- Visual previews: `previews/`
- Metadata helper: `kdp-metadata.json`
- Cover direction: `chess-in-the-block-cover-brief.md`

## KDP Setup

- Trim size: 6 x 9 in
- Interior: Black and white
- Paper: White
- Interior bleed: No bleed
- Cover bleed: 0.125 in
- Cover finish: Matte recommended
- Reading direction: Left to Right

## Generated Dimensions

- Interior page count: {int(specs["page_count"])}
- Spine width: {specs["spine_width_in"]:.4f} in
- Full cover width: {specs["cover_width_in"]:.4f} in
- Full cover height: {specs["cover_height_in"]:.4f} in

## Before Publishing

1. Paperback: upload `paperback/chess-in-the-block-paperback-interior-kdp.pdf` and `paperback/chess-in-the-block-paperback-cover-kdp.pdf`.
2. Kindle/eBook: upload `ebook/chess-in-the-block-kindle-ebook.epub` and `ebook/chess-in-the-block-ebook-cover.jpg`.
3. Open KDP's online previewer and check every flagged page/screen.
4. Order a paperback proof copy before enabling live sales.
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")
    if SOURCE_BRIEF.exists():
        (OUT_DIR / "chess-in-the-block-cover-brief.md").write_text(SOURCE_BRIEF.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    register_fonts()
    chapters = read_clean_manuscript()
    if len(chapters) != 10:
        raise SystemExit(f"Expected 10 chapters, found {len(chapters)}")
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    interior_pdf = PAPERBACK_DIR / "chess-in-the-block-paperback-interior-kdp.pdf"
    cover_pdf = PAPERBACK_DIR / "chess-in-the-block-paperback-cover-kdp.pdf"
    cover_preview = PREVIEWS_DIR / "chess-in-the-block-paperback-spread-preview.png"
    page_count = build_interior(chapters, interior_pdf)
    specs = build_cover(page_count, cover_pdf, cover_preview)
    epub_path = build_epub(chapters)
    write_metadata(specs)
    print(json.dumps({"page_count": page_count, "cover_pdf": str(cover_pdf), "interior_pdf": str(interior_pdf), "epub": str(epub_path)}, indent=2))


if __name__ == "__main__":
    main()
