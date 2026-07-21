#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books/borrow-delay-repeat/directors-cut"
SOURCE = BOOK / "borrow-delay-repeat-directors-cut.docx"
PREMIUM = BOOK / "premium-edition"
EBOOK = PREMIUM / "ebook"
DIGITAL = PREMIUM / "digital"
BUILD = PREMIUM / ".epub-build"
EPUB = EBOOK / "borrow-delay-repeat-directors-cut-premium.epub"
COVER = EBOOK / "borrow-delay-repeat-directors-cut-cover.jpg"
SELECTED_COVER = EBOOK / "borrow-delay-repeat-directors-cut-cover-v3.png"
PDF_SOURCE = BOOK / "borrow-delay-repeat-directors-cut.pdf"
PDF = DIGITAL / "borrow-delay-repeat-directors-cut-premium.pdf"

TITLE = "Borrow. Delay. Repeat."
SUBTITLE = "A Very Unserious Guide to Not Giving Money Back"
EDITION = "Director’s Cut"
AUTHOR = "Sabino Pereira"
IDENTIFIER = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/borrow-delay-repeat-directors-cut"))


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def make_cover() -> None:
    EBOOK.mkdir(parents=True, exist_ok=True)
    if SELECTED_COVER.exists():
        with Image.open(SELECTED_COVER) as selected:
            selected.convert("RGB").save(COVER, "JPEG", quality=95, optimize=True, progressive=True)
        return
    w, h = 1600, 2560
    im = Image.new("RGB", (w, h), "#f4eee2")
    d = ImageDraw.Draw(im)
    impact = "/System/Library/Fonts/Supplemental/Impact.ttf"
    georgia = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    georgia_bold = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
    courier = "/System/Library/Fonts/Courier New Bold.ttf"
    ink, red, muted = "#181715", "#9e2226", "#6b625a"
    d.rectangle((92, 92, w - 92, h - 92), outline=ink, width=7)
    d.rectangle((132, 132, w - 132, h - 132), outline=red, width=3)
    d.text((185, 190), AUTHOR.upper(), font=ImageFont.truetype(georgia_bold, 48), fill=ink)
    y = 550
    for line in ("BORROW.", "DELAY.", "REPEAT."):
        d.text((185, y), line, font=ImageFont.truetype(impact, 210), fill=ink)
        y += 245
    d.line((185, 1335, 1415, 1335), fill=red, width=12)
    d.text((190, 1390), EDITION.upper(), font=ImageFont.truetype(courier, 55), fill=red)
    subtitle_font = ImageFont.truetype(georgia, 56)
    d.text((190, 1575), "A VERY UNSERIOUS GUIDE", font=subtitle_font, fill=ink)
    d.text((190, 1648), "TO NOT GIVING MONEY BACK", font=subtitle_font, fill=ink)
    d.rectangle((190, 1950, 1410, 2220), fill="#ebe1d2", outline=ink, width=4)
    receipt = ImageFont.truetype(courier, 42)
    d.text((240, 2005), "AMOUNT DUE: TRUST", font=receipt, fill=ink)
    d.text((240, 2070), "STATUS: STILL PENDING", font=receipt, fill=ink)
    d.text((240, 2135), "DUE DATE: TOMORROW", font=receipt, fill=red)
    d.text((190, 2340), "THE MONEY WAS TEMPORARY. THE AWKWARDNESS IS FOREVER.", font=ImageFont.truetype(courier, 31), fill=muted)
    im.save(COVER, "JPEG", quality=94, optimize=True, progressive=True)


def sections():
    doc = Document(SOURCE)
    result, current = [], None
    skip_cover = True
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        style = p.style.name if p.style else "Normal"
        if skip_cover:
            if text == "A Note Before the Excuses":
                skip_cover = False
            else:
                continue
        if style == "Heading 1":
            current = {"title": text, "items": []}
            result.append(current)
        elif current:
            current["items"].append((style, text))
    return result


def xhtml(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><title>{html.escape(title)}</title><link rel="stylesheet" href="styles.css" type="text/css"/></head>
<body>{body}</body></html>'''


def render_section(section, index: int) -> str:
    body = [f'<section epub:type="chapter" class="chapter" id="chapter-{index}">', f'<p class="chapter-no">RECEIPT {index:02d}</p>', f'<h1>{html.escape(section["title"])}</h1>']
    for style, text in section["items"]:
        safe = html.escape(text).replace("\n", "<br/>")
        if style == "Heading 2":
            body.append(f"<h2>{safe}</h2>")
        elif style == "Receipt":
            body.append(f'<div class="receipt">{safe}</div>')
        elif text.upper().startswith("DIRECTOR’S COMMENTARY") or text.upper().startswith("TERMS AND CONDITIONS"):
            label, _, rest = text.partition("\n")
            body.append(f'<aside><strong>{html.escape(label)}</strong><br/>{html.escape(rest)}</aside>')
        else:
            cls = ' class="short"' if len(text) < 42 else ""
            body.append(f"<p{cls}>{safe}</p>")
    body.append("</section>")
    return xhtml(section["title"], "\n".join(body))


def build() -> None:
    make_cover()
    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "META-INF").mkdir(parents=True)
    (BUILD / "OEBPS/images").mkdir(parents=True)
    write(BUILD / "mimetype", "application/epub+zip")
    write(BUILD / "META-INF/container.xml", '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''')
    shutil.copyfile(COVER, BUILD / "OEBPS/images/cover.jpg")
    css = '''body{font-family:Georgia,serif;color:#181715;line-height:1.55;margin:0 7%;} .chapter{break-before:page;} h1{font-size:1.75em;line-height:1.15;margin:.2em 0 1em;} h2{font-family:Arial,sans-serif;color:#9e2226;font-size:1.05em;margin:1.5em 0 .55em;} p{margin:0 0 .82em;} .chapter-no{font-family:monospace;color:#9e2226;font-size:.72em;letter-spacing:.12em;margin-top:2em;} .short{text-align:center;font-style:italic;} aside{background:#f4eee2;border-left:.35em solid #9e2226;margin:1.2em 0;padding:.9em 1em;} aside strong{font-family:Arial,sans-serif;color:#9e2226;font-size:.8em;letter-spacing:.08em;} .receipt{background:#ebe1d2;border:1px solid #6b625a;font-family:monospace;font-size:.88em;margin:1.3em 0;padding:1em;white-space:normal;} .cover{text-align:center;margin:0;padding:0;} .cover img{max-width:100%;height:auto;} nav ol{line-height:1.8;}'''
    write(BUILD / "OEBPS/styles.css", css)
    write(BUILD / "OEBPS/cover.xhtml", xhtml("Cover", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Cover of Borrow. Delay. Repeat. — Director’s Cut"/></section>'))
    data = sections()
    for i, section in enumerate(data, 1):
        write(BUILD / f"OEBPS/chapter-{i:02d}.xhtml", render_section(section, i))
    nav_items = "".join(f'<li><a href="chapter-{i:02d}.xhtml">{html.escape(s["title"])}</a></li>' for i, s in enumerate(data, 1))
    write(BUILD / "OEBPS/nav.xhtml", xhtml("Contents", f'<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{nav_items}</ol></nav>'))
    manifest = "".join(f'<item id="c{i}" href="chapter-{i:02d}.xhtml" media-type="application/xhtml+xml"/>' for i in range(1, len(data)+1))
    spine = "".join(f'<itemref idref="c{i}"/>' for i in range(1, len(data)+1))
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{IDENTIFIER}</dc:identifier><dc:title>{TITLE} — {EDITION}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>en</dc:language><dc:description>{SUBTITLE}. Premium Director’s Cut edition.</dc:description><dc:publisher>Sabino Pereira</dc:publisher><meta property="dcterms:modified">{modified}</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="styles.css" media-type="text/css"/><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/><item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>{manifest}</manifest><spine><itemref idref="cover" linear="no"/>{spine}</spine></package>'''
    write(BUILD / "OEBPS/content.opf", opf)
    if EPUB.exists(): EPUB.unlink()
    with zipfile.ZipFile(EPUB, "w") as z:
        z.write(BUILD / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for p in sorted(BUILD.rglob("*")):
            if p.is_file() and p.name != "mimetype":
                z.write(p, p.relative_to(BUILD), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(BUILD)
    DIGITAL.mkdir(parents=True, exist_ok=True)
    if PDF_SOURCE.exists(): shutil.copyfile(PDF_SOURCE, PDF)
    print(EPUB)
    print(COVER)
    print(PDF)


if __name__ == "__main__":
    build()
