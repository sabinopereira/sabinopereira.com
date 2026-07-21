#!/usr/bin/env python3
"""Rebuild Bad Girl Gospel as premium prose editions.

Narrative chapters are reflowed into literary paragraphs. Opening manifestos,
closings, epigraph-like passages, and deliberate lists retain their lineation.
"""

from __future__ import annotations

import html
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageBreak, PageTemplate, Paragraph, Spacer


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPTS = ROOT / "manuscripts"
DIRECT = ROOT / "direct-sale"
SITE = "sabinopereira.com"
AUTHOR = "Sabino Pereira"
PAGE_W, PAGE_H = 6 * inch, 9 * inch
INK = colors.HexColor("#22191c")
WINE = colors.HexColor("#6f2434")
ROSE = colors.HexColor("#b87682")
CREAM = colors.HexColor("#fbf5ed")
MUTED = colors.HexColor("#74686a")


@dataclass
class Book:
    slug: str
    title: str
    subtitle: str
    source: Path
    cover: Path


@dataclass
class Section:
    heading: str
    subtitle: str
    blocks: list[list[str]]
    verse: bool = False


BOOKS = [
    Book("selah", "Bad Girl Gospel: The Story of Selah", "A Confession About the Cost of Freedom", MANUSCRIPTS / "selah-source.epub", DIRECT / "selah/bad-girl-gospel-the-story-of-selah-digital-cover.jpg"),
    Book("diana", "Bad Girl Gospel: The Story of Diana", "A Confession About Marriage", MANUSCRIPTS / "diana.md", DIRECT / "diana/bad-girl-gospel-the-story-of-diana-digital-cover.jpg"),
    Book("noa", "Bad Girl Gospel: The Story of Noa", "A Confession About the Name She Had to Survive", MANUSCRIPTS / "noa.md", DIRECT / "noa/bad-girl-gospel-the-story-of-noa-digital-cover.jpg"),
    Book("naomi", "Bad Girl Gospel: The Story of Naomi", "A Confession About Money, Hunger, and the Woman They Called Heartless", MANUSCRIPTS / "naomi.md", DIRECT / "naomi/bad-girl-gospel-the-story-of-naomi-digital-cover.jpg"),
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("  ", " ")).strip()


def markup(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)


def is_verse_section(heading: str) -> bool:
    key = heading.lower()
    return "manifesto" in key or key == "closing"


def markdown_sections(path: Path) -> list[Section]:
    text = path.read_text(encoding="utf-8")
    parts = [p.strip() for p in text.split("\n---\n") if p.strip()]
    sections: list[Section] = []
    for part in parts[1:]:  # title page is generated separately
        lines = part.splitlines()
        heading = next((x[3:].strip() for x in lines if x.startswith("## ")), "")
        subtitle = next((x[4:].strip() for x in lines if x.startswith("### ")), "")
        body = [x.rstrip() for x in lines if not x.startswith(("# ", "## ", "### "))]
        blocks, current = [], []
        for line in body + [""]:
            if line.strip():
                current.append(line.strip().rstrip("  "))
            elif current:
                blocks.append(current)
                current = []
        sections.append(Section(heading, subtitle, blocks, is_verse_section(heading)))
    return sections


def epub_sections(path: Path) -> list[Section]:
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.startswith("OEBPS/text/") and n.endswith(".xhtml")]
        names = [n for n in names if not n.endswith(("cover.xhtml", "title.xhtml", "about-the-author.xhtml"))]
        order = [n for n in names if "fiction-note" in n or "opening-manifesto" in n]
        order += sorted([n for n in names if "/chapter-" in n], key=lambda n: int(re.search(r"chapter-(\d+)", n).group(1)))
        order += [n for n in names if "afterword" in n]
        sections = []
        for name in order:
            root = ET.fromstring(z.read(name))
            ns = {"x": "http://www.w3.org/1999/xhtml"}
            headings = [clean("".join(h.itertext())) for h in root.findall(".//x:h1", ns) + root.findall(".//x:h2", ns)]
            heading = headings[0] if headings else Path(name).stem.replace("-", " ").title()
            subtitle = headings[1] if len(headings) > 1 else ""
            blocks = []
            for p in root.findall(".//x:p", ns):
                lines = [clean(x) for x in "".join(p.itertext()).splitlines() if clean(x)]
                if lines:
                    blocks.append(lines)
            sections.append(Section(heading, subtitle, blocks, is_verse_section(heading) or "afterword" in name))
        return sections


def looks_like_heading(text: str) -> bool:
    words = text.split()
    return 0 < len(words) <= 7 and not re.search(r"[.!?;:,\"”]$", text) and all(w[:1].isupper() or w.lower() in {"a", "and", "of", "the", "to", "in", "with", "without"} for w in words)


def reflow(blocks: list[list[str]]) -> list[tuple[str, bool]]:
    """Return (text, preserve_lines) blocks for a prose section."""
    units = [clean(" ".join(lines)) for lines in blocks if clean(" ".join(lines))]
    out: list[tuple[str, bool]] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            out.append((" ".join(buffer), False))
            buffer.clear()

    for unit in units:
        # Dialogue, internal headings, and refrain-like lists remain distinct.
        special = unit.startswith(("“", '"', "—")) or looks_like_heading(unit)
        if special:
            flush()
            out.append((unit, False))
            continue
        candidate = " ".join(buffer + [unit])
        if buffer and (len(candidate) > 620 or len(buffer) >= 5):
            flush()
        buffer.append(unit)
    flush()
    return out


def section_content(section: Section) -> list[tuple[str, bool]]:
    if section.verse:
        return [("<br/>".join(markup(clean(line)) for line in block if clean(line)), True) for block in section.blocks]
    return [(markup(text), keep) for text, keep in reflow(section.blocks)]


def register_fonts() -> None:
    folder = Path("/System/Library/Fonts/Supplemental")
    for name, filename in {"Georgia": "Georgia.ttf", "Georgia-Bold": "Georgia Bold.ttf", "Georgia-Italic": "Georgia Italic.ttf"}.items():
        pdfmetrics.registerFont(TTFont(name, str(folder / filename)))


class Cover(Flowable):
    def __init__(self, path: Path):
        super().__init__(); self.path = str(path); self.width = PAGE_W; self.height = PAGE_H
    def wrap(self, aw, ah): return PAGE_W, PAGE_H
    def draw(self): self.canv.drawImage(self.path, 0, 0, PAGE_W, PAGE_H, preserveAspectRatio=False, mask="auto")


def frame_page(canvas, doc) -> None:
    canvas.saveState(); canvas.setFillColor(CREAM); canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setStrokeColor(ROSE); canvas.setLineWidth(.45); canvas.line(.68*inch, PAGE_H-.5*inch, PAGE_W-.68*inch, PAGE_H-.5*inch)
    canvas.setFillColor(MUTED); canvas.setFont("Georgia", 7.4); canvas.drawString(.68*inch, .39*inch, doc.title)
    canvas.drawRightString(PAGE_W-.68*inch, .39*inch, str(doc.page)); canvas.restoreState()


def blank_page(canvas, doc) -> None:
    canvas.saveState(); canvas.setFillColor(CREAM); canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0); canvas.restoreState()


def pdf_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("Title", parent=base["Title"], fontName="Georgia-Bold", fontSize=25, leading=31, textColor=WINE, alignment=TA_CENTER, spaceAfter=15),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName="Georgia-Italic", fontSize=12.4, leading=18, textColor=ROSE, alignment=TA_CENTER),
        "author": ParagraphStyle("Author", parent=base["Normal"], fontName="Georgia-Bold", fontSize=11.5, textColor=INK, alignment=TA_CENTER, spaceBefore=24),
        "heading": ParagraphStyle("Heading", parent=base["Heading1"], fontName="Georgia-Bold", fontSize=19.5, leading=24, textColor=WINE, alignment=TA_CENTER, spaceAfter=8),
        "subheading": ParagraphStyle("Subheading", parent=base["Normal"], fontName="Georgia-Italic", fontSize=11.5, leading=16, textColor=ROSE, alignment=TA_CENTER, spaceAfter=25),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Georgia", fontSize=10.45, leading=16.1, textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=16, spaceAfter=8),
        "first": ParagraphStyle("First", parent=base["Normal"], fontName="Georgia", fontSize=10.45, leading=16.1, textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=0, spaceAfter=8),
        "verse": ParagraphStyle("Verse", parent=base["Normal"], fontName="Georgia", fontSize=10.35, leading=16.2, textColor=INK, alignment=TA_LEFT, leftIndent=16, rightIndent=10, spaceAfter=13),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Georgia", fontSize=8.8, leading=13.5, textColor=MUTED, spaceAfter=9),
    }


def build_pdf(book: Book, sections: list[Section]) -> Path:
    register_fonts(); styles = pdf_styles(); folder = DIRECT / book.slug
    out = folder / f"bad-girl-gospel-the-story-of-{book.slug}-premium-ebook.pdf"
    doc = BaseDocTemplate(str(out), pagesize=(PAGE_W, PAGE_H), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0, title=book.title, author=AUTHOR)
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, 0, 0, 0, 0, id="cover")
    body_frame = Frame(.68*inch, .61*inch, PAGE_W-1.36*inch, PAGE_H-1.19*inch, 0, 0, .2*inch, .1*inch, id="body")
    doc.addPageTemplates([PageTemplate(id="Cover", frames=[cover_frame], onPage=blank_page, autoNextPageTemplate="Body"), PageTemplate(id="Body", frames=[body_frame], onPage=frame_page)])
    story = [Cover(book.cover), PageBreak(), Spacer(1, 1.15*inch), Paragraph(book.title, styles["title"]), Paragraph(book.subtitle, styles["subtitle"]), Paragraph(AUTHOR, styles["author"]), PageBreak(), Spacer(1, .6*inch), Paragraph("Copyright", styles["heading"]), Paragraph("Copyright © 2026 Sabino Pereira. All rights reserved.", styles["small"]), Paragraph("No part of this publication may be reproduced, stored, distributed, or transmitted in any form or by any means without prior written permission, except for brief quotations used in reviews.", styles["small"]), Paragraph("This is a work of fiction. Names, characters, places, institutions, and incidents are products of the author's imagination or are used fictitiously.", styles["small"]), Paragraph("Premium digital edition, 2026", styles["small"]), PageBreak()]
    for section in sections:
        story += [Spacer(1, .5*inch), Paragraph(html.escape(section.heading), styles["heading"])]
        if section.subtitle: story.append(Paragraph(html.escape(section.subtitle), styles["subheading"]))
        else: story.append(Spacer(1, 12))
        first = True
        for content, verse in section_content(section):
            if not content: continue
            story.append(Paragraph(content, styles["verse"] if verse else styles["first"] if first else styles["body"]))
            first = False
        story.append(PageBreak())
    story += [Spacer(1, 1*inch), Paragraph("About the Author", styles["heading"]), Paragraph("Sabino Pereira creates fiction, reflective books, music, and work about behavior, healing, discernment, faith, and modern life.", styles["first"]), Paragraph(f'<link href="https://{SITE}" color="#6f2434">{SITE}</link>', styles["subtitle"])]
    doc.build(story)
    return out


def xhtml(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" href="styles.css"/></head><body>{body}</body></html>'''


def build_epub(book: Book, sections: list[Section]) -> Path:
    folder = DIRECT / book.slug; build = ROOT / "build" / book.slug
    if build.exists(): shutil.rmtree(build)
    (build / "META-INF").mkdir(parents=True); (build / "OEBPS/images").mkdir(parents=True)
    (build / "mimetype").write_text("application/epub+zip", encoding="utf-8")
    (build / "META-INF/container.xml").write_text('<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>', encoding="utf-8")
    shutil.copyfile(book.cover, build / "OEBPS/images/cover.jpg")
    css = 'body{font-family:Georgia,serif;color:#22191c;line-height:1.58;margin:0 7%;}h1{text-align:center;color:#6f2434;margin:2.3em 0 .5em;}h2{text-align:center;color:#9b5866;font-size:1.05em;font-style:italic;margin:0 0 2em;}p{margin:.55em 0;text-indent:1.2em;text-align:justify;}p.first,p.verse,p.front{text-indent:0;}p.verse{text-align:left;margin:.8em 5%;}.cover{text-align:center;margin:0}.cover img{max-width:100%;}.author{text-align:center;font-weight:bold}.site{text-align:center;color:#6f2434}.chapter{break-before:page;}'
    (build / "OEBPS/styles.css").write_text(css, encoding="utf-8")
    (build / "OEBPS/cover.xhtml").write_text(xhtml("Cover", f'<div class="cover"><img src="images/cover.jpg" alt="Cover of {html.escape(book.title)}"/></div>'), encoding="utf-8")
    (build / "OEBPS/title.xhtml").write_text(xhtml("Title", f'<h1>{html.escape(book.title)}</h1><h2>{html.escape(book.subtitle)}</h2><p class="author">{AUTHOR}</p>'), encoding="utf-8")
    files = ["cover.xhtml", "title.xhtml"]
    nav_items = []
    for i, section in enumerate(sections, 1):
        paras=[]
        for j,(content,verse) in enumerate(section_content(section)):
            cls = "verse" if verse else "first" if j == 0 else ""
            paras.append(f'<p class="{cls}">{content}</p>')
        name=f"section-{i:02d}.xhtml"; files.append(name); nav_items.append(f'<li><a href="{name}">{html.escape(section.heading)}</a></li>')
        (build/f"OEBPS/{name}").write_text(xhtml(section.heading, f'<section class="chapter"><h1>{html.escape(section.heading)}</h1>{f"<h2>{html.escape(section.subtitle)}</h2>" if section.subtitle else ""}{"".join(paras)}</section>'), encoding="utf-8")
    (build/"OEBPS/nav.xhtml").write_text(xhtml("Contents", f'<nav epub:type="toc"><h1>Contents</h1><ol>{"".join(nav_items)}</ol></nav>'), encoding="utf-8"); files.append("nav.xhtml")
    manifest=['<item id="cover-img" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>','<item id="css" href="styles.css" media-type="text/css"/>']; spine=[]
    for i,name in enumerate(files):
        prop=' properties="nav"' if name=="nav.xhtml" else ''
        manifest.append(f'<item id="p{i}" href="{name}" media-type="application/xhtml+xml"{prop}/>'); spine.append(f'<itemref idref="p{i}"/>')
    ident=uuid.uuid5(uuid.NAMESPACE_URL, f"https://{SITE}/bad-girl-gospel/{book.slug}/premium-prose")
    opf=f'''<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">urn:uuid:{ident}</dc:identifier><dc:title>{html.escape(book.title)}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>en</dc:language><meta property="dcterms:modified">2026-07-20T00:00:00Z</meta></metadata><manifest>{''.join(manifest)}</manifest><spine>{''.join(spine)}</spine></package>'''
    (build/"OEBPS/content.opf").write_text(opf, encoding="utf-8")
    out=folder/f"bad-girl-gospel-the-story-of-{book.slug}-premium-ebook.epub"
    with zipfile.ZipFile(out,"w") as z:
        z.write(build/"mimetype","mimetype",compress_type=zipfile.ZIP_STORED)
        for path in sorted(build.rglob("*")):
            if path.is_file() and path.name!="mimetype": z.write(path,path.relative_to(build).as_posix(),compress_type=zipfile.ZIP_DEFLATED)
    return out


def main() -> None:
    for book in BOOKS:
        sections = epub_sections(book.source) if book.source.suffix == ".epub" else markdown_sections(book.source)
        print(f"{book.slug}: {len(sections)} sections")
        print(build_pdf(book, sections)); print(build_epub(book, sections))


if __name__ == "__main__": main()
