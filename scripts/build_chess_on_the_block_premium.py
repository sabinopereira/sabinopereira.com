#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "books/chess-in-the-block/chess-on-the-block-directors-cut.md"
COVER = ROOT / "books/chess-in-the-block/cover/chess-on-the-block-directors-cut-cover-v3.png"
PDF_OUT = ROOT / "output/pdf/chess-on-the-block-directors-cut-premium.pdf"
PREMIUM_DIR = ROOT / "books/chess-in-the-block/premium"
EPUB_OUT = PREMIUM_DIR / "chess-on-the-block-directors-cut.epub"
COVER_JPG = PREMIUM_DIR / "chess-on-the-block-directors-cut-cover.jpg"
PACKAGE_OUT = PREMIUM_DIR / "chess-on-the-block-directors-cut-fourthwall.zip"

TITLE = "Chess on the Block"
EDITION = "Director's Cut"
AUTHOR = "Sabino Pereira"
SUBTITLE = "Survival, family, pressure—and learning how to move without losing yourself."
DESCRIPTION = (
    "A reflective urban book about survival, family, pressure, silence, love, loss, "
    "and the moves people learn to make without losing themselves."
)

PAGE_W = 6 * inch
PAGE_H = 9 * inch
GOLD = colors.HexColor("#B9863E")
INK = colors.HexColor("#171512")
WARM_GRAY = colors.HexColor("#6A6257")
PAPER = colors.HexColor("#F4EFE5")


@dataclass
class Chapter:
    title: str
    paragraphs: list[str]


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    candidates = {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
        "Impact": font_dir / "Impact.ttf",
    }
    for name, path in candidates.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def parse_manuscript() -> tuple[list[str], list[Chapter]]:
    text = SOURCE.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    lines: list[str] = []

    def flush() -> None:
        nonlocal current, lines
        if current is not None:
            sections[current] = [p.strip() for p in "\n".join(lines).split("\n\n") if p.strip()]
        current, lines = None, []

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            current = line[3:].strip()
        elif current is not None:
            lines.append(line)
    flush()

    author_note = sections.get("Author's Note", [])
    excluded = {"Subtitle", "Author's Note", "Table of Contents"}
    chapters = [Chapter(title, paras) for title, paras in sections.items() if title not in excluded]
    if len(chapters) != 10:
        raise SystemExit(f"Expected 10 chapters, found {len(chapters)}")
    return author_note, chapters


def styles() -> dict[str, ParagraphStyle]:
    sheet = getSampleStyleSheet()
    result = {
        "title": ParagraphStyle(
            "PremiumTitle", parent=sheet["Title"], fontName="Impact", fontSize=37,
            leading=40, alignment=TA_CENTER, textColor=INK, spaceAfter=15,
        ),
        "edition": ParagraphStyle(
            "Edition", fontName="Georgia-Bold", fontSize=10, leading=14,
            alignment=TA_CENTER, textColor=GOLD, tracking=1.5, spaceAfter=20,
        ),
        "subtitle": ParagraphStyle(
            "PremiumSubtitle", fontName="Georgia-Italic", fontSize=12.2, leading=18,
            alignment=TA_CENTER, textColor=WARM_GRAY, spaceAfter=28,
        ),
        "author": ParagraphStyle(
            "PremiumAuthor", fontName="Georgia-Bold", fontSize=12, leading=16,
            alignment=TA_CENTER, textColor=INK,
        ),
        "h1": ParagraphStyle(
            "PremiumH1", fontName="Impact", fontSize=28, leading=31,
            alignment=TA_LEFT, textColor=INK, spaceAfter=14,
        ),
        "kicker": ParagraphStyle(
            "Kicker", fontName="Georgia-Bold", fontSize=9.5, leading=13,
            alignment=TA_LEFT, textColor=GOLD, spaceAfter=9,
        ),
        "body": ParagraphStyle(
            "PremiumBody", fontName="Georgia", fontSize=10.85, leading=16.6,
            alignment=TA_JUSTIFY, textColor=INK, spaceAfter=10,
            allowWidows=0, allowOrphans=0,
        ),
        "beat": ParagraphStyle(
            "SpokenBeat", fontName="Georgia-Italic", fontSize=12.2, leading=18,
            alignment=TA_CENTER, textColor=INK, leftIndent=25, rightIndent=25,
            spaceBefore=7, spaceAfter=12,
        ),
        "toc": ParagraphStyle(
            "PremiumToc", fontName="Georgia", fontSize=11, leading=17,
            textColor=INK, spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "PremiumSmall", fontName="Georgia", fontSize=8.4, leading=13,
            alignment=TA_CENTER, textColor=WARM_GRAY, spaceAfter=7,
        ),
        "note": ParagraphStyle(
            "PremiumNote", fontName="Georgia", fontSize=11, leading=17,
            alignment=TA_LEFT, textColor=INK, spaceAfter=11,
        ),
        "chapter_number": ParagraphStyle(
            "ChapterNumber", fontName="Georgia-Bold", fontSize=10, leading=14,
            alignment=TA_LEFT, textColor=GOLD, spaceAfter=13,
        ),
        "chapter_title": ParagraphStyle(
            "ChapterTitle", fontName="Impact", fontSize=31, leading=35,
            alignment=TA_LEFT, textColor=INK, spaceAfter=18,
        ),
    }
    return result


BEATS = {
    "Others are not.", "But it was.", "This book is about that.",
    "Not chess as a game.", "Chess as a language.",
    "This book is not about beating everybody.", "It is about not losing yourself.",
    "One step at a time.", "One square.", "Then another.",
    "Not impressed by.", "Safe with.", "But real.", "And sometimes, necessary.",
    "not how to escape,", "but how to arrive.", "You can protect the silence.",
    "Or you can protect the truth.", "They are not.", "The rook goes back.",
    "Ask anyway.", "Ask again later.", "Good.", "Some humility is medicine.",
    "That counts.", "Some pain is just pain.", "Some chairs stay empty.",
    "No lesson fills them.", "Not innocent.", "Not naive.", "Human.",
    "Even here.", "Especially here.", "On another board.",
}


def esc(text: str) -> str:
    return html.escape(text).replace("—", "&mdash;")


def draw_body_page(canv, doc) -> None:
    canv.saveState()
    canv.setFillColor(PAPER)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if doc.page > 4:
        canv.setStrokeColor(colors.HexColor("#D7C9B4"))
        canv.setLineWidth(0.45)
        canv.line(0.72 * inch, PAGE_H - 0.52 * inch, PAGE_W - 0.72 * inch, PAGE_H - 0.52 * inch)
        canv.setFont("Georgia", 8)
        canv.setFillColor(WARM_GRAY)
        canv.drawString(0.72 * inch, PAGE_H - 0.42 * inch, TITLE.upper())
        canv.drawRightString(PAGE_W - 0.72 * inch, 0.42 * inch, str(doc.page - 1))
    canv.restoreState()


def draw_chapter_page(canv, doc) -> None:
    canv.saveState()
    canv.setFillColor(PAPER)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setFillColor(colors.HexColor("#13110F"))
    canv.rect(0, PAGE_H - 1.08 * inch, PAGE_W, 1.08 * inch, fill=1, stroke=0)
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(1.1)
    canv.line(0.72 * inch, 1.05 * inch, 2.0 * inch, 1.05 * inch)
    canv.restoreState()


def build_pdf(author_note: list[str], chapters: list[Chapter]) -> None:
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    PREMIUM_DIR.mkdir(parents=True, exist_ok=True)
    s = styles()
    doc = BaseDocTemplate(
        str(PDF_OUT), pagesize=(PAGE_W, PAGE_H), leftMargin=0, rightMargin=0,
        topMargin=0, bottomMargin=0, title=f"{TITLE} — {EDITION}", author=AUTHOR,
        subject=DESCRIPTION,
    )
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0, id="cover")
    body_frame = Frame(0.72 * inch, 0.68 * inch, PAGE_W - 1.44 * inch, PAGE_H - 1.30 * inch,
                       leftPadding=0, rightPadding=0, topPadding=0.12 * inch,
                       bottomPadding=0.05 * inch, id="body")
    chapter_frame = Frame(0.72 * inch, 1.05 * inch, PAGE_W - 1.44 * inch, PAGE_H - 2.0 * inch,
                          leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                          id="chapter")
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame]),
        PageTemplate(id="Body", frames=[body_frame], onPage=draw_body_page),
        PageTemplate(id="Chapter", frames=[chapter_frame], onPage=draw_chapter_page),
    ])

    story = [Image(str(COVER), width=PAGE_W, height=PAGE_H), NextPageTemplate("Body"), PageBreak()]
    story.extend([
        Spacer(1, 1.35 * inch),
        Paragraph(TITLE.upper(), s["title"]),
        Paragraph(EDITION.upper(), s["edition"]),
        Paragraph(esc(SUBTITLE), s["subtitle"]),
        Paragraph(AUTHOR.upper(), s["author"]),
        PageBreak(),
        Spacer(1, 1.35 * inch),
        Paragraph("Copyright © 2026 Sabino Pereira", s["small"]),
        Paragraph("All rights reserved.", s["small"]),
        Spacer(1, 0.22 * inch),
        Paragraph(
            "No part of this publication may be reproduced, distributed, or transmitted in any form without prior written permission from the author, except for brief quotations used in reviews or commentary.",
            s["small"],
        ),
        Spacer(1, 0.24 * inch),
        Paragraph("Premium digital edition · Director's Cut", s["small"]),
        PageBreak(),
        Paragraph("AUTHOR'S NOTE", s["kicker"]),
        Paragraph("Before the First Move", s["h1"]),
    ])
    for para in author_note:
        story.append(Paragraph(esc(para), s["note"]))
    story.extend([PageBreak(), Paragraph("CONTENTS", s["kicker"]), Paragraph("The Board", s["h1"])])
    for index, chapter in enumerate(chapters, 1):
        story.append(Paragraph(f'<a href="#chapter-{index}">{index:02d}  ·  {esc(chapter.title)}</a>', s["toc"]))

    for index, chapter in enumerate(chapters, 1):
        story.extend([
            NextPageTemplate("Chapter"), PageBreak(), Spacer(1, 1.55 * inch),
            Paragraph(f'<a name="chapter-{index}"/>CHAPTER {index:02d}', s["chapter_number"]),
            Paragraph(esc(chapter.title), s["chapter_title"]),
            Spacer(1, 0.12 * inch),
            Paragraph("A MOVE ON THE BOARD", s["kicker"]),
            NextPageTemplate("Body"), PageBreak(),
        ])
        for para in chapter.paragraphs:
            style = s["beat"] if para in BEATS else s["body"]
            story.append(Paragraph(esc(para), style))

    story.extend([
        NextPageTemplate("Chapter"), PageBreak(), Spacer(1, 2.05 * inch),
        Paragraph("THE BOARD CHANGES.", s["chapter_title"]),
        Paragraph("THE NEXT MOVE IS YOURS.", s["chapter_number"]),
    ])
    doc.build(story)
    shutil.copy2(PDF_OUT, PREMIUM_DIR / PDF_OUT.name)


def xhtml(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><title>{html.escape(title)}</title><link rel="stylesheet" href="styles.css" type="text/css"/></head>
<body>{body}</body></html>'''


def build_epub(author_note: list[str], chapters: list[Chapter]) -> None:
    PREMIUM_DIR.mkdir(parents=True, exist_ok=True)
    build = PREMIUM_DIR / ".epub-build"
    if build.exists():
        shutil.rmtree(build)
    (build / "META-INF").mkdir(parents=True)
    (build / "OEBPS/images").mkdir(parents=True)
    PILImage.open(COVER).convert("RGB").resize((1600, 2560), PILImage.Resampling.LANCZOS).save(
        COVER_JPG, "JPEG", quality=94, optimize=True
    )
    (build / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (build / "META-INF/container.xml").write_text(
        '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',
        encoding="utf-8",
    )
    css = '''body{font-family:Georgia,serif;line-height:1.58;margin:0 7%;color:#171512;background:#f8f3e9}h1{font-size:1.75em;line-height:1.15;margin:1.3em 0 .8em}h2{color:#9b6d2c;font-size:.82em;letter-spacing:.14em;text-transform:uppercase;margin-top:2em}p{margin:0 0 .9em}.beat{font-style:italic;text-align:center;margin:1.25em 7%}.cover{margin:0;text-align:center}.cover img{width:100%;height:auto}.author-note{font-style:italic}nav ol{line-height:1.8;padding-left:1.25em}a{color:#6f4b1d;text-decoration:none}'''
    (build / "OEBPS/styles.css").write_text(css, encoding="utf-8")
    shutil.copy2(COVER_JPG, build / "OEBPS/images/cover.jpg")
    (build / "OEBPS/cover.xhtml").write_text(
        xhtml("Cover", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Cover of Chess on the Block — Director’s Cut"/></section>'),
        encoding="utf-8",
    )
    note_body = '<section epub:type="preface"><h2>Author’s Note</h2><h1>Before the First Move</h1>' + "".join(
        f'<p class="author-note">{html.escape(p)}</p>' for p in author_note
    ) + "</section>"
    (build / "OEBPS/author-note.xhtml").write_text(xhtml("Author's Note", note_body), encoding="utf-8")
    for i, chapter in enumerate(chapters, 1):
        paragraphs = "".join(
            f'<p class="{"beat" if p in BEATS else "body"}">{html.escape(p)}</p>' for p in chapter.paragraphs
        )
        body = f'<section epub:type="chapter" id="chapter-{i}"><h2>Chapter {i:02d}</h2><h1>{html.escape(chapter.title)}</h1>{paragraphs}</section>'
        (build / f"OEBPS/chapter-{i:02d}.xhtml").write_text(xhtml(chapter.title, body), encoding="utf-8")

    nav_items = ['<li><a href="author-note.xhtml">Author’s Note</a></li>'] + [
        f'<li><a href="chapter-{i:02d}.xhtml">{html.escape(c.title)}</a></li>' for i, c in enumerate(chapters, 1)
    ]
    nav = f'<nav epub:type="toc"><h1>Contents</h1><ol>{"".join(nav_items)}</ol></nav>'
    (build / "OEBPS/nav.xhtml").write_text(xhtml("Contents", nav), encoding="utf-8")
    uid = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'https://sabinopereira.com/chess-on-the-block-directors-cut')}"
    manifest = "".join(
        f'<item id="c{i}" href="chapter-{i:02d}.xhtml" media-type="application/xhtml+xml"/>' for i in range(1, len(chapters) + 1)
    )
    spine = "".join(f'<itemref idref="c{i}"/>' for i in range(1, len(chapters) + 1))
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{uid}</dc:identifier><dc:title>{TITLE} — {EDITION}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>en</dc:language><dc:description>{html.escape(DESCRIPTION)}</dc:description><meta property="dcterms:modified">2026-07-19T00:00:00Z</meta></metadata>
<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="style" href="styles.css" media-type="text/css"/><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/><item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/><item id="note" href="author-note.xhtml" media-type="application/xhtml+xml"/>{manifest}</manifest>
<spine><itemref idref="cover" linear="no"/><itemref idref="note"/>{spine}</spine></package>'''
    (build / "OEBPS/content.opf").write_text(opf, encoding="utf-8")
    if EPUB_OUT.exists():
        EPUB_OUT.unlink()
    with zipfile.ZipFile(EPUB_OUT, "w") as zf:
        zf.write(build / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(build.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                zf.write(path, path.relative_to(build), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(build)


def build_package() -> None:
    readme = PREMIUM_DIR / "READ-ME-FIRST.txt"
    readme.write_text(
        f"{TITLE} — {EDITION}\n\nPremium digital edition by {AUTHOR}.\n\nIncluded:\n- Premium PDF (fixed layout)\n- EPUB (reflowable ebook)\n- High-resolution cover JPG\n",
        encoding="utf-8",
    )
    if PACKAGE_OUT.exists():
        PACKAGE_OUT.unlink()
    with zipfile.ZipFile(PACKAGE_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in [PREMIUM_DIR / PDF_OUT.name, EPUB_OUT, COVER_JPG, readme]:
            zf.write(path, path.name)


def main() -> None:
    register_fonts()
    author_note, chapters = parse_manuscript()
    build_pdf(author_note, chapters)
    build_epub(author_note, chapters)
    build_package()
    print(PDF_OUT)
    print(EPUB_OUT)
    print(PACKAGE_OUT)


if __name__ == "__main__":
    main()
