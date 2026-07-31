#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import importlib.util
import re
import shutil
import textwrap
import uuid
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/a-journey-back-to-silence-final-manuscript.md"
SOURCE_COVER = ROOT / "assets/cover/a-journey-back-to-silence-book-cover.png"

PAPERBACK_ROOT = ROOT / "amazon-kdp/paperback"
PAPERBACK_INTERIOR = PAPERBACK_ROOT / "interior/a-journey-back-to-silence-paperback-interior-kdp.pdf"
PAPERBACK_COVER = PAPERBACK_ROOT / "cover/a-journey-back-to-silence-paperback-cover-kdp.pdf"
PAPERBACK_COVER_PREVIEW = PAPERBACK_ROOT / "cover/a-journey-back-to-silence-paperback-cover-preview.jpg"

EBOOK_ROOT = ROOT / "amazon-kdp/ebook"
EPUB = EBOOK_ROOT / "a-journey-back-to-silence-kindle.epub"
EBOOK_COVER = EBOOK_ROOT / "a-journey-back-to-silence-kindle-cover.jpg"
STAGE = ROOT / "tmp/kindle-epub"

TRIM_W = 6.0
TRIM_H = 9.0
BLEED = 0.125
CREAM_SPINE_PER_PAGE = 0.0025
PRINT_DPI = 300


def load_book_builder():
    path = ROOT / "scripts/build_book.py"
    spec = importlib.util.spec_from_file_location("silence_builder", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_paperback_interior() -> int:
    builder = load_book_builder()
    temp_pdf = ROOT / "tmp/pdfs/kdp-interior-with-cover.pdf"
    temp_pdf.parent.mkdir(parents=True, exist_ok=True)

    builder.PAPER = white
    builder.NAVY = HexColor("#111111")
    builder.OCEAN = HexColor("#444444")
    builder.MIST = HexColor("#777777")
    builder.INK = HexColor("#171717")
    builder.GOLD = HexColor("#555555")
    builder.OUTPUT_PDF = temp_pdf

    def draw_print_page(pdf_canvas, doc):
        pdf_canvas.saveState()
        pdf_canvas.setFillColor(white)
        pdf_canvas.rect(0, 0, builder.PAGE_W, builder.PAGE_H, fill=1, stroke=0)
        # The temporary document contains a cover that is removed below.
        # After removal, Before the Journey becomes printed page 1.
        if doc.page > 6:
            pdf_canvas.setStrokeColor(HexColor("#C8C8C8"))
            pdf_canvas.setLineWidth(0.35)
            pdf_canvas.line(0.78 * inch, 0.53 * inch, builder.PAGE_W - 0.70 * inch, 0.53 * inch)
            pdf_canvas.setFillColor(HexColor("#333333"))
            pdf_canvas.setFont("Georgia", 7.7)
            pdf_canvas.drawCentredString(builder.PAGE_W / 2, 0.31 * inch, str(doc.page - 6))
        pdf_canvas.restoreState()

    builder.draw_page = draw_print_page
    builder.build_pdf()

    source = PdfReader(str(temp_pdf))
    writer = PdfWriter()
    for page in source.pages[1:]:
        writer.add_page(page)
    if len(writer.pages) % 2:
        writer.add_blank_page(width=6 * inch, height=9 * inch)
    writer.add_metadata({
        "/Title": "A Journey Back to Silence",
        "/Author": "Sabino Pereira",
        "/Subject": "KDP paperback interior - 6 x 9 in, black ink, cream paper",
    })
    PAPERBACK_INTERIOR.parent.mkdir(parents=True, exist_ok=True)
    with PAPERBACK_INTERIOR.open("wb") as handle:
        writer.write(handle)
    return len(writer.pages)


def fit_cover_panel(source: Image.Image, width: int, height: int) -> Image.Image:
    ratio = max(width / source.width, height / source.height)
    resized = source.resize((round(source.width * ratio), round(source.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def font(path: str, size: int):
    return ImageFont.truetype(path, size)


def draw_centred_multiline(draw, box, text, text_font, fill, spacing=12):
    left, top, right, bottom = box
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(paragraph, width=44))
    heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line or " ", font=text_font)
        heights.append(bbox[3] - bbox[1])
    total = sum(heights) + spacing * (len(lines) - 1)
    y = top + max(0, (bottom - top - total) / 2)
    for line, height in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=text_font)
        x = left + (right - left - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=text_font, fill=fill)
        y += height + spacing


def build_paperback_cover(page_count: int):
    spine_in = page_count * CREAM_SPINE_PER_PAGE
    full_w_in = BLEED + TRIM_W + spine_in + TRIM_W + BLEED
    full_h_in = BLEED + TRIM_H + BLEED
    full_w = round(full_w_in * PRINT_DPI)
    full_h = round(full_h_in * PRINT_DPI)
    panel_w = round((TRIM_W + BLEED) * PRINT_DPI)
    spine_w = round(spine_in * PRINT_DPI)

    source = Image.open(SOURCE_COVER).convert("RGB")
    front = fit_cover_panel(source, panel_w, full_h)

    # The original front artwork places the dedication over a textured part of
    # the watercolour. Give it a quiet, high-contrast reading panel so the
    # printed text remains legible after KDP's compression and ink gain.
    front_rgba = front.convert("RGBA")
    front_overlay = Image.new("RGBA", front_rgba.size, (0, 0, 0, 0))
    front_overlay_draw = ImageDraw.Draw(front_overlay)
    dedication_box = (
        round(1.30 * PRINT_DPI),
        round(7.48 * PRINT_DPI),
        panel_w - round(1.30 * PRINT_DPI),
        round(8.78 * PRINT_DPI),
    )
    front_overlay_draw.rounded_rectangle(
        dedication_box,
        radius=round(0.08 * PRINT_DPI),
        fill=(246, 241, 233, 255),
    )
    front = Image.alpha_composite(front_rgba, front_overlay).convert("RGB")

    # Back cover uses the same watercolour language without repeating the title art.
    # Sample only the text-free landscape band. This prevents the faint title
    # from being mistaken by KDP's automated checks for unreadable cover text.
    back_source = source.crop(
        (0, round(source.height * 0.50), source.width, round(source.height * 0.76))
    )
    back = fit_cover_panel(back_source, panel_w, full_h).filter(ImageFilter.GaussianBlur(radius=20))
    wash = Image.new("RGBA", back.size, (244, 238, 228, 232))
    back = Image.alpha_composite(back.convert("RGBA"), wash).convert("RGB")

    wrap = Image.new("RGB", (full_w, full_h), "#EEE7DC")
    wrap.paste(back, (0, 0))
    front_x = panel_w + spine_w
    wrap.paste(front, (front_x, 0))

    draw = ImageDraw.Draw(wrap)
    navy = "#142A39"
    muted = "#435E6A"
    georgia = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    georgia_bold = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
    georgia_italic = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"

    safe = round(0.38 * PRINT_DPI)
    back_right = panel_w - safe
    draw.text((safe, round(0.75 * PRINT_DPI)), "A QUIET BOOK FOR A LOUD WORLD", font=font(georgia_bold, 36), fill=navy)
    draw.line((safe, round(1.18 * PRINT_DPI), back_right, round(1.18 * PRINT_DPI)), fill="#8095A0", width=2)

    blurb = (
        "In a world that never stops speaking, silence can feel unfamiliar.\n\n"
        "A Journey Back to Silence is a reflective companion for anyone who has felt overwhelmed by urgency, expectation, or the quiet exhaustion of always being available.\n\n"
        "Across eight passages inspired by the companion album by Reira Bin, Sabino Pereira explores attention, memory, waiting, control, and the courage to hear yourself again.\n\n"
        "This is not a book about escaping life. It is an invitation to return to it with less noise inside you."
    )
    body_font = font(georgia, 31)
    y = round(1.48 * PRINT_DPI)
    for paragraph in blurb.split("\n\n"):
        lines = textwrap.wrap(paragraph, width=48)
        for line in lines:
            draw.text((safe, y), line, font=body_font, fill=navy)
            y += 43
        y += 31

    quote = "“The world will be loud again.\nYou do not have to lose yourself inside it.”"
    draw_centred_multiline(
        draw,
        (safe, round(6.45 * PRINT_DPI), back_right, round(7.55 * PRINT_DPI)),
        quote,
        font(georgia_italic, 31), navy, spacing=12,
    )
    draw.text((safe, round(8.28 * PRINT_DPI)), "SABINO PEREIRA", font=font(georgia_bold, 30), fill=navy)

    # Redraw the front dedication over the contrast panel. The source image's
    # original lettering remains underneath but is fully obscured by the wash.
    front_left = front_x
    dedication = (
        "For those who are tired.\n"
        "May this journey remind you\n"
        "that silence is not emptiness.\n"
        "Sometimes, it is where we\n"
        "finally find ourselves."
    )
    draw_centred_multiline(
        draw,
        (
            front_left + dedication_box[0],
            dedication_box[1] + round(0.08 * PRINT_DPI),
            front_left + dedication_box[2],
            dedication_box[3] - round(0.08 * PRINT_DPI),
        ),
        dedication,
        font(georgia_italic, 31),
        navy,
        spacing=10,
    )

    # Leave a clean barcode zone on the lower-right area of the back cover.
    barcode_w = round(2.0 * PRINT_DPI)
    barcode_h = round(1.2 * PRINT_DPI)
    bx = panel_w - safe - barcode_w
    by = full_h - safe - barcode_h
    draw.rounded_rectangle((bx, by, bx + barcode_w, by + barcode_h), radius=8, fill="#FAF8F3")

    PAPERBACK_COVER.parent.mkdir(parents=True, exist_ok=True)
    wrap.save(PAPERBACK_COVER_PREVIEW, "JPEG", quality=94, subsampling=0, dpi=(PRINT_DPI, PRINT_DPI))
    c = canvas.Canvas(str(PAPERBACK_COVER), pagesize=(full_w_in * inch, full_h_in * inch))
    c.setTitle("A Journey Back to Silence - KDP Paperback Cover")
    c.setAuthor("Sabino Pereira")
    c.drawImage(ImageReader(wrap), 0, 0, width=full_w_in * inch, height=full_h_in * inch, preserveAspectRatio=False)
    c.showPage()
    c.save()


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def split_sections(markdown: str):
    matches = list(re.finditer(r"(?m)^# (.+)$", markdown))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        result.append((match.group(1).strip(), markdown[match.end():end].strip()))
    return result


def inline(text: str):
    value = html.escape(text.strip(), quote=False)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*(.+?)\*", r"<em>\1</em>", value)
    return value


def opening_small_caps(text: str):
    words = text.split()
    if len(words) < 3:
        return inline(text)
    return f'<span class="opening">{inline(" ".join(words[:3]))}</span> {inline(" ".join(words[3:]))}'


def markdown_html(text: str, passage=False):
    result = []
    paragraph = []
    current_subhead = ""
    opening_pending = False

    def flush():
        nonlocal opening_pending
        if not paragraph:
            return
        value = " ".join(paragraph)
        content = opening_small_caps(value) if opening_pending else inline(value)
        result.append(f"<p>{content}</p>")
        paragraph.clear()
        opening_pending = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line == "---":
            flush()
            continue
        if line.startswith("### "):
            flush()
            current_subhead = line[4:].strip()
            opening_pending = passage and current_subhead == "The Arrival"
            result.append(f"<h2>{inline(current_subhead)}</h2>")
        elif line.startswith("## "):
            flush()
            result.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("> "):
            flush()
            result.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        else:
            paragraph.append(line)
    flush()
    return "\n".join(result)


def xhtml(title: str, body: str, body_class=""):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="styles.css"/></head>
<body class="{body_class}">{body}</body></html>'''


def build_epub():
    markdown = MANUSCRIPT.read_text(encoding="utf-8")
    sections = [
        (name, body) for name, body in split_sections(markdown)
        if name not in {"A JOURNEY BACK TO SILENCE", "Contents"}
    ]
    if STAGE.exists():
        shutil.rmtree(STAGE)
    (STAGE / "META-INF").mkdir(parents=True)
    (STAGE / "OEBPS/images").mkdir(parents=True)
    EBOOK_ROOT.mkdir(parents=True, exist_ok=True)

    with Image.open(SOURCE_COVER) as image:
        image = image.convert("RGB").resize((1600, 2400), Image.Resampling.LANCZOS)
        image.save(EBOOK_COVER, "JPEG", quality=94, optimize=True, progressive=True)
    shutil.copyfile(EBOOK_COVER, STAGE / "OEBPS/images/cover.jpg")

    write(STAGE / "mimetype", "application/epub+zip")
    write(STAGE / "META-INF/container.xml", '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles></container>''')

    css = '''@charset "UTF-8";
body { margin: 0 5%; }
p { margin: 0 0 1em; }
h1, h2 { text-align: left; font-weight: normal; }
h1 { font-size: 1.8em; line-height: 1.15; margin: 1.8em 0 1em; }
h2 { font-size: 1.12em; margin: 1.5em 0 0.7em; }
.cover { margin: 0; padding: 0; text-align: center; }
.cover img { display: block; width: 100%; height: auto; margin: 0 auto; }
.title-page, .part-page { text-align: center; padding-top: 18%; break-after: page; page-break-after: always; }
.title-page h1, .part-page h1 { text-align: center; }
.eyebrow { text-align: center; font-size: 0.75em; letter-spacing: 0.15em; text-transform: uppercase; }
.credits { margin-top: 22%; }
.credits p { text-align: center; }
.section { break-before: page; page-break-before: always; }
.passage header { text-align: center; padding-top: 8%; }
.passage header h1 { text-align: center; }
.opening { font-variant: small-caps; letter-spacing: 0.04em; }
blockquote { margin: 1.2em 8%; font-style: italic; text-align: center; }
nav ol { list-style: none; padding: 0; }
nav li { margin: 0.65em 0; }
nav a { text-decoration: none; }
'''
    write(STAGE / "OEBPS/styles.css", css)
    write(STAGE / "OEBPS/cover.xhtml", xhtml("Cover", '<section epub:type="cover" class="cover"><img src="images/cover.jpg" alt="Cover of A Journey Back to Silence by Sabino Pereira"/></section>', "cover"))
    title_body = '''<section epub:type="titlepage" class="title-page"><p class="eyebrow">EIGHT PASSAGES FROM NOISE TO STILLNESS</p>
<h1>A Journey Back to Silence</h1><div class="credits"><p>Written by Sabino Pereira</p><p>Companion music by Reira Bin</p></div></section>'''
    copyright_body = '''<section epub:type="copyright-page" class="section"><h1>Copyright</h1>
<p>Copyright © 2026 Sabino Pereira</p><p>All rights reserved.</p><p>First Kindle edition, 2026.</p>
<p>Written by Sabino Pereira (SP). Companion music composed by Reira Bin (RB).</p></section>'''
    write(STAGE / "OEBPS/title.xhtml", xhtml("Title Page", title_body))
    write(STAGE / "OEBPS/copyright.xhtml", xhtml("Copyright", copyright_body))

    manifest_items = []
    spine_items = []
    nav_entries = []
    first_body = None
    for index, (name, body) in enumerate(sections, 1):
        slug = f"section-{index:02d}"
        is_passage = name.startswith("Passage ")
        title_match = re.search(r"(?m)^## (.+)$", body) if is_passage else None
        display_title = title_match.group(1) if title_match else name
        if is_passage:
            body = re.sub(r"(?m)^## .+\n?", "", body, count=1).strip()
            content = f'<article epub:type="chapter" class="section passage"><header><p class="eyebrow">{html.escape(name)}</p><h1>{html.escape(display_title)}</h1></header>{markdown_html(body, passage=True)}</article>'
            if first_body is None:
                first_body = f"{slug}.xhtml"
        elif name in {"Part I", "Part II", "Part III"}:
            title = re.search(r"(?m)^## (.+)$", body).group(1)
            content = f'<section epub:type="part" class="part-page"><p class="eyebrow">{html.escape(name)}</p><h1>{html.escape(title)}</h1></section>'
            display_title = f"{name} — {title}"
        elif name == "Final Page":
            content = f'<section class="section">{markdown_html(body)}</section>'
        else:
            content = f'<section class="section"><h1>{html.escape(name)}</h1>{markdown_html(body)}</section>'
        write(STAGE / f"OEBPS/{slug}.xhtml", xhtml(display_title, content))
        manifest_items.append(f'<item id="{slug}" href="{slug}.xhtml" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{slug}"/>')
        if index == 2:
            spine_items.append('<itemref idref="nav"/>')
        if name != "A Note to the Reader" or True:
            nav_entries.append((f"{slug}.xhtml", display_title))

    nav_list = "".join(f'<li><a href="{href}">{html.escape(title)}</a></li>' for href, title in nav_entries)
    nav = f'''<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{nav_list}</ol></nav>
<nav epub:type="landmarks" hidden="hidden"><ol><li><a epub:type="cover" href="cover.xhtml">Cover</a></li><li><a epub:type="toc" href="nav.xhtml">Contents</a></li><li><a epub:type="bodymatter" href="{first_body}">Start reading</a></li></ol></nav>'''
    write(STAGE / "OEBPS/nav.xhtml", xhtml("Contents", nav, "navigation"))

    uid = "urn:uuid:" + str(uuid.UUID(hashlib.md5(markdown.encode("utf-8")).hexdigest()))
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">{uid}</dc:identifier><dc:title>A Journey Back to Silence</dc:title><dc:creator>Sabino Pereira</dc:creator><dc:contributor>Reira Bin</dc:contributor><dc:language>en</dc:language><dc:publisher>Sabino Pereira</dc:publisher><dc:description>Eight reflective passages from noise to stillness, written by Sabino Pereira with companion music by Reira Bin.</dc:description><meta property="dcterms:modified">2026-07-29T00:00:00Z</meta></metadata>
<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/><item id="title" href="title.xhtml" media-type="application/xhtml+xml"/><item id="copyright" href="copyright.xhtml" media-type="application/xhtml+xml"/><item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/><item id="css" href="styles.css" media-type="text/css"/>{''.join(manifest_items)}</manifest>
<spine><itemref idref="cover"/><itemref idref="title"/><itemref idref="copyright"/>{''.join(spine_items)}</spine></package>'''
    write(STAGE / "OEBPS/content.opf", opf)

    if EPUB.exists():
        EPUB.unlink()
    with zipfile.ZipFile(EPUB, "w") as archive:
        archive.write(STAGE / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(STAGE.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                archive.write(path, path.relative_to(STAGE), compress_type=zipfile.ZIP_DEFLATED)


def main():
    page_count = build_paperback_interior()
    build_paperback_cover(page_count)
    build_epub()
    print(f"paperback_pages={page_count}")
    print(PAPERBACK_INTERIOR)
    print(PAPERBACK_COVER)
    print(EPUB)
    print(EBOOK_COVER)


if __name__ == "__main__":
    main()
