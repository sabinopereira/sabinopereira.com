#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/yes-i-do-again.md"
COVER = ROOT / "cover/yes-i-do-again-english-cover.png"
OUT = ROOT / "direct-sale/english"
BUILD = ROOT / "build/direct-sale"
PDF_PATH = OUT / "yes-i-do-again-premium-ebook.pdf"
EPUB_PATH = OUT / "yes-i-do-again-premium-ebook.epub"
COVER_JPG = OUT / "yes-i-do-again-digital-cover.jpg"
README_PATH = OUT / "README.txt"

TITLE = "Yes, I Do... Again."
AUTHOR = "Sabino Pereira"
TAGLINE = "Knowing everything you know now, would you still choose the same person?"
SITE = "sabinopereira.com"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/books/yes-i-do-again/direct-sale"))

PAGE_W, PAGE_H = 6 * inch, 9 * inch
NAVY = colors.HexColor("#10293C")
DEEP_NAVY = colors.HexColor("#081B2A")
COPPER = colors.HexColor("#C28B57")
CREAM = colors.HexColor("#F7F2E8")
INK = colors.HexColor("#1D252B")
MUTED = colors.HexColor("#6D7478")


@dataclass
class Section:
    title: str
    paragraphs: list[str]
    kind: str


def parse_manuscript() -> list[Section]:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    sections: list[Section] = []
    current: Section | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if current and buffer:
            current.paragraphs.append(" ".join(x.strip() for x in buffer).strip())
        buffer = []

    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            flush()
            title = line[3:].strip()
            current = Section(title, [], "epilogue" if title.lower().startswith("epilogue") else "chapter")
            sections.append(current)
        elif line.startswith("# "):
            continue
        elif not line:
            flush()
        elif current:
            buffer.append(line)
    flush()
    return sections


def register_fonts() -> None:
    folder = Path("/System/Library/Fonts/Supplemental")
    for name, filename in {
        "Georgia": "Georgia.ttf",
        "Georgia-Bold": "Georgia Bold.ttf",
        "Georgia-Italic": "Georgia Italic.ttf",
    }.items():
        path = folder / filename
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def prepare_cover() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with Image.open(COVER) as src:
        image = src.convert("RGB")
        ratio = 1600 / 2560
        current = image.width / image.height
        if current > ratio:
            width = round(image.height * ratio)
            x = (image.width - width) // 2
            image = image.crop((x, 0, x + width, image.height))
        elif current < ratio:
            height = round(image.width / ratio)
            y = (image.height - height) // 2
            image = image.crop((0, y, image.width, y + height))
        image.resize((1600, 2560), Image.Resampling.LANCZOS).save(
            COVER_JPG, "JPEG", quality=96, optimize=True, progressive=True, dpi=(300, 300)
        )


class CoverPage(Flowable):
    def __init__(self, path: Path):
        super().__init__()
        self.path = str(path)
        self.width = PAGE_W
        self.height = PAGE_H

    def wrap(self, avail_width, avail_height):
        return PAGE_W, PAGE_H

    def draw(self):
        self.canv.drawImage(self.path, 0, 0, PAGE_W, PAGE_H, preserveAspectRatio=False, mask="auto")


class PremiumDocTemplate(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "ChapterTitle":
            text = flowable.getPlainText()
            key = getattr(flowable, "_bookmarkName", None)
            if key:
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=0, closed=False)
                self.notify("TOCEntry", (0, text, self.page, key))


def styles():
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle("PremiumTitle", parent=base["Title"], fontName="Georgia-Bold", fontSize=30, leading=35, textColor=NAVY, alignment=TA_CENTER, spaceAfter=18),
        "Tagline": ParagraphStyle("Tagline", parent=base["Normal"], fontName="Georgia-Italic", fontSize=13, leading=19, textColor=COPPER, alignment=TA_CENTER),
        "Author": ParagraphStyle("Author", parent=base["Normal"], fontName="Georgia-Bold", fontSize=12, leading=15, textColor=NAVY, alignment=TA_CENTER, spaceBefore=26),
        "FrontHeading": ParagraphStyle("FrontHeading", parent=base["Heading1"], fontName="Georgia-Bold", fontSize=23, leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=22),
        "FrontBody": ParagraphStyle("FrontBody", parent=base["Normal"], fontName="Georgia", fontSize=10.8, leading=17, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=11),
        "Copyright": ParagraphStyle("Copyright", parent=base["Normal"], fontName="Georgia", fontSize=8.8, leading=13.5, textColor=MUTED, alignment=TA_LEFT, spaceAfter=10),
        "ChapterTitle": ParagraphStyle("ChapterTitle", parent=base["Heading1"], fontName="Georgia-Bold", fontSize=22, leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=28),
        "First": ParagraphStyle("First", parent=base["Normal"], fontName="Georgia", fontSize=10.7, leading=16.6, textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=0, spaceAfter=0),
        "Body": ParagraphStyle("Body", parent=base["Normal"], fontName="Georgia", fontSize=10.7, leading=16.6, textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=17, spaceAfter=0),
        "Message": ParagraphStyle("Message", parent=base["Normal"], fontName="Georgia-Italic", fontSize=10.3, leading=16, textColor=NAVY, leftIndent=22, rightIndent=18, spaceBefore=5, spaceAfter=5),
        "About": ParagraphStyle("About", parent=base["Normal"], fontName="Georgia", fontSize=11, leading=18, textColor=INK, alignment=TA_LEFT, spaceAfter=12),
        "Site": ParagraphStyle("Site", parent=base["Normal"], fontName="Georgia-Bold", fontSize=11, leading=16, textColor=COPPER, alignment=TA_CENTER, spaceBefore=18),
    }


def markup(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)


def draw_frame(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setStrokeColor(COPPER)
    canvas.setLineWidth(0.45)
    canvas.line(0.72 * inch, PAGE_H - 0.52 * inch, PAGE_W - 0.72 * inch, PAGE_H - 0.52 * inch)
    canvas.setFont("Georgia", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.72 * inch, 0.42 * inch, TITLE)
    canvas.drawRightString(PAGE_W - 0.72 * inch, 0.42 * inch, str(doc.page))
    canvas.restoreState()


def draw_cover_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DEEP_NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.restoreState()


def rule() -> Flowable:
    class Rule(Flowable):
        def wrap(self, aw, ah): return aw, 18
        def draw(self):
            self.canv.setStrokeColor(COPPER)
            self.canv.setLineWidth(1)
            self.canv.line(self.width * 0.34, 9, self.width * 0.66, 9)
    return Rule()


def build_pdf(sections: list[Section]) -> None:
    register_fonts()
    s = styles()
    doc = PremiumDocTemplate(str(PDF_PATH), pagesize=(PAGE_W, PAGE_H), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0, title=TITLE, author=AUTHOR, subject=TAGLINE)
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
    body_frame = Frame(0.72 * inch, 0.65 * inch, PAGE_W - 1.44 * inch, PAGE_H - 1.25 * inch, leftPadding=0, rightPadding=0, topPadding=0.22 * inch, bottomPadding=0.1 * inch, id="body")
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover_background, autoNextPageTemplate="Body"),
        PageTemplate(id="Body", frames=[body_frame], onPage=draw_frame),
    ])

    story = [CoverPage(COVER_JPG), PageBreak()]
    story.extend([
        Spacer(1, 0.9 * inch),
        Paragraph(TITLE, s["Title"]), rule(), Spacer(1, 15),
        Paragraph(TAGLINE, s["Tagline"]),
        Paragraph(AUTHOR, s["Author"]),
        PageBreak(),
        Spacer(1, 0.5 * inch),
        Paragraph("Copyright", s["FrontHeading"]), rule(), Spacer(1, 20),
        Paragraph("Copyright © 2026 Sabino Pereira. All rights reserved.", s["Copyright"]),
        Paragraph("No part of this publication may be reproduced, stored, distributed, or transmitted in any form or by any means without prior written permission from the copyright holder, except for brief quotations used in reviews.", s["Copyright"]),
        Paragraph("This is a work of fiction. Names, characters, places, institutions, and incidents are products of the author’s imagination or are used fictitiously. Any resemblance to actual persons or events is coincidental.", s["Copyright"]),
        Paragraph("Digital edition, 2026", s["Copyright"]),
        Paragraph(SITE, s["Site"]),
        PageBreak(),
        Spacer(1, 0.35 * inch),
        Paragraph("About This Book", s["FrontHeading"]), rule(), Spacer(1, 18),
        Paragraph("Every ten years, couples must choose what they still want to be to one another.", s["FrontBody"]),
        Paragraph("Tomás and Leonor have built a home, raised a son, and learned how to keep a life running. What they have not learned is whether remaining together is still an act of love—or merely the path of least resistance.", s["FrontBody"]),
        Paragraph("When their Identity Review arrives, the system offers five choices: renew, renegotiate, remain a family without romance, separate, or end. The decision forces them to confront desire, sacrifice, temptation, money, parenthood, and the uncomfortable possibility that two people can love each other while no longer choosing the same life.", s["FrontBody"]),
        PageBreak(),
        Spacer(1, 0.25 * inch),
        Paragraph("Contents", s["FrontHeading"]), rule(), Spacer(1, 12),
    ])
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("TOC", fontName="Georgia", fontSize=11, leading=19, textColor=NAVY, leftIndent=6, rightIndent=6, firstLineIndent=0, spaceBefore=3)]
    story.extend([toc, PageBreak()])

    for idx, section in enumerate(sections, 1):
        story.append(Spacer(1, 0.72 * inch))
        heading = Paragraph(markup(section.title), s["ChapterTitle"])
        heading._bookmarkName = f"section-{idx:02d}"
        story.extend([heading, rule(), Spacer(1, 17)])
        for pidx, paragraph in enumerate(section.paragraphs):
            is_message = paragraph.startswith("*") and paragraph.endswith("*")
            style = s["Message"] if is_message else s["First"] if pidx == 0 else s["Body"]
            story.append(Paragraph(markup(paragraph), style))
        story.append(PageBreak())

    story.extend([
        Spacer(1, 0.8 * inch),
        Paragraph("About the Author", s["FrontHeading"]), rule(), Spacer(1, 22),
        Paragraph("Sabino Pereira creates fiction, reflective books, music, and work about behavior, healing, discernment, faith, and modern life.", s["About"]),
        Paragraph("Discover more books and creative work at:", s["About"]),
        Paragraph(f'<link href="https://{SITE}" color="#C28B57">{SITE}</link>', s["Site"]),
        Spacer(1, 0.8 * inch),
        Paragraph("Thank you for reading.", s["Tagline"]),
    ])
    doc.multiBuild(story)


def epub_page(title: str, body: str, body_class: str = "") -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" href="styles.css" type="text/css"/></head>
<body class="{body_class}">{body}</body></html>'''


def build_epub(sections: list[Section]) -> None:
    root = BUILD / "epub"
    if root.exists(): shutil.rmtree(root)
    (root / "META-INF").mkdir(parents=True)
    (root / "OEBPS/images").mkdir(parents=True)
    (root / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (root / "META-INF/container.xml").write_text('''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''', encoding="utf-8")
    shutil.copyfile(COVER_JPG, root / "OEBPS/images/cover.jpg")
    css = '''
body{font-family:serif;color:#1d252b;line-height:1.58;margin:0 6%;}
body.cover{margin:0;text-align:center;} .cover img{max-width:100%;height:auto;}
h1{color:#10293c;font-size:1.65em;line-height:1.25;text-align:center;margin:2.2em 0 1.7em;}
h2{color:#10293c;font-size:1.25em;text-align:center;margin:2em 0 1em;}
.accent{color:#9c693d;text-align:center;font-style:italic;margin:1.4em 6%;}
.author{text-align:center;font-weight:bold;color:#10293c;margin-top:2.2em;}
.front{text-indent:0;margin:.8em 0;} .copyright{font-size:.88em;color:#5f676c;text-indent:0;margin:.7em 0;}
p{margin:0;text-indent:1.25em;} p.first{margin-top:0;text-indent:0;} p.message{font-style:italic;text-indent:0;margin:.6em 1.2em;color:#10293c;}
.chapter{break-before:page;page-break-before:always;} nav ol{line-height:1.9;} nav a{color:#10293c;text-decoration:none;}
.rule{width:28%;border:0;border-top:1px solid #c28b57;margin:1em auto 1.5em;}
.site{text-align:center;font-weight:bold;color:#9c693d;}
'''
    (root / "OEBPS/styles.css").write_text(css, encoding="utf-8")
    (root / "OEBPS/cover.xhtml").write_text(epub_page("Cover", f'<section epub:type="cover"><img src="images/cover.jpg" alt="Cover of {html.escape(TITLE)}"/></section>', "cover"), encoding="utf-8")
    title_body = f'<section epub:type="titlepage"><h1>{html.escape(TITLE)}</h1><hr class="rule"/><p class="accent">{html.escape(TAGLINE)}</p><p class="author">{html.escape(AUTHOR)}</p></section>'
    (root / "OEBPS/title.xhtml").write_text(epub_page("Title Page", title_body), encoding="utf-8")
    copyright_body = f'<section epub:type="copyright-page"><h1>Copyright</h1><hr class="rule"/><p class="copyright">Copyright © 2026 Sabino Pereira. All rights reserved.</p><p class="copyright">No part of this publication may be reproduced, stored, distributed, or transmitted in any form or by any means without prior written permission from the copyright holder, except for brief quotations used in reviews.</p><p class="copyright">This is a work of fiction. Names, characters, places, institutions, and incidents are products of the author’s imagination or are used fictitiously. Any resemblance to actual persons or events is coincidental.</p><p class="copyright">Digital edition, 2026</p><p class="site">{SITE}</p></section>'
    (root / "OEBPS/copyright.xhtml").write_text(epub_page("Copyright", copyright_body), encoding="utf-8")
    about_body = '<section><h1>About This Book</h1><hr class="rule"/><p class="front">Every ten years, couples must choose what they still want to be to one another.</p><p class="front">Tomás and Leonor have built a home, raised a son, and learned how to keep a life running. What they have not learned is whether remaining together is still an act of love—or merely the path of least resistance.</p><p class="front">When their Identity Review arrives, the system offers five choices: renew, renegotiate, remain a family without romance, separate, or end. The decision forces them to confront desire, sacrifice, temptation, money, parenthood, and the uncomfortable possibility that two people can love each other while no longer choosing the same life.</p></section>'
    (root / "OEBPS/about-book.xhtml").write_text(epub_page("About This Book", about_body), encoding="utf-8")

    for idx, section in enumerate(sections, 1):
        paras = []
        for pidx, p in enumerate(section.paragraphs):
            cls = "message" if p.startswith("*") and p.endswith("*") else "first" if pidx == 0 else ""
            paras.append(f'<p class="{cls}">{markup(p)}</p>')
        body = f'<section class="chapter" epub:type="{section.kind}" id="section-{idx:02d}"><h1>{html.escape(section.title)}</h1><hr class="rule"/>{"".join(paras)}</section>'
        (root / f"OEBPS/section-{idx:02d}.xhtml").write_text(epub_page(section.title, body), encoding="utf-8")

    author_body = f'<section><h1>About the Author</h1><hr class="rule"/><p class="front">Sabino Pereira creates fiction, reflective books, music, and work about behavior, healing, discernment, faith, and modern life.</p><p class="front">Discover more books and creative work at:</p><p class="site"><a href="https://{SITE}">{SITE}</a></p><p class="accent">Thank you for reading.</p></section>'
    (root / "OEBPS/about-author.xhtml").write_text(epub_page("About the Author", author_body), encoding="utf-8")

    nav_items = ''.join(f'<li><a href="section-{i:02d}.xhtml">{html.escape(s.title)}</a></li>' for i, s in enumerate(sections, 1))
    nav = f'<nav epub:type="toc" id="toc"><h1>Contents</h1><ol><li><a href="about-book.xhtml">About This Book</a></li>{nav_items}<li><a href="about-author.xhtml">About the Author</a></li></ol></nav>'
    (root / "OEBPS/nav.xhtml").write_text(epub_page("Contents", nav), encoding="utf-8")

    files = ["cover.xhtml", "title.xhtml", "copyright.xhtml", "about-book.xhtml", "nav.xhtml"] + [f"section-{i:02d}.xhtml" for i in range(1, len(sections)+1)] + ["about-author.xhtml"]
    manifest = ['<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>', '<item id="css" href="styles.css" media-type="text/css"/>']
    spine = []
    for idx, name in enumerate(files):
        props = ' properties="nav"' if name == "nav.xhtml" else ""
        manifest.append(f'<item id="item-{idx}" href="{name}" media-type="application/xhtml+xml"{props}/>')
        spine.append(f'<itemref idref="item-{idx}"/>')
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="en-US"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">{BOOK_ID}</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title><dc:creator>{html.escape(AUTHOR)}</dc:creator><dc:language>en-US</dc:language><dc:publisher>{html.escape(AUTHOR)}</dc:publisher><dc:description>{html.escape(TAGLINE)}</dc:description><meta property="dcterms:modified">2026-07-19T00:00:00Z</meta></metadata><manifest>{''.join(manifest)}</manifest><spine>{''.join(spine)}</spine></package>'''
    (root / "OEBPS/content.opf").write_text(opf, encoding="utf-8")
    with zipfile.ZipFile(EPUB_PATH, "w") as z:
        z.write(root / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                z.write(path, path.relative_to(root).as_posix(), compress_type=zipfile.ZIP_DEFLATED)


def write_readme() -> None:
    README_PATH.write_text(f'''YES, I DO... AGAIN. — PREMIUM DIGITAL EDITION

Included files
--------------
1. yes-i-do-again-premium-ebook.epub
   Reflowable edition for Apple Books, Kobo, Google Play Books, tablets,
   phones, and compatible e-readers. Includes a navigable table of contents.

2. yes-i-do-again-premium-ebook.pdf
   Designed fixed-layout edition for direct reading on tablets and computers.
   Includes a visual table of contents, PDF bookmarks, page numbers, and links.

3. yes-i-do-again-digital-cover.jpg
   High-resolution sales cover (1600 x 2560 px).

Title: {TITLE}
Author: {AUTHOR}
Language: English (US)
Website: https://{SITE}

Copyright © 2026 Sabino Pereira. All rights reserved.
''', encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    prepare_cover()
    sections = parse_manuscript()
    build_pdf(sections)
    build_epub(sections)
    write_readme()
    print(f"Created {PDF_PATH}")
    print(f"Created {EPUB_PATH}")
    print(f"Created {COVER_JPG}")
    print(f"Created {README_PATH}")


if __name__ == "__main__":
    main()
