#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_borrow_ebook_pdf import (  # noqa: E402
    BOOK_DIR,
    COVER_JPG,
    OUT_DIR,
    SOURCE_DOCX,
    create_cover,
    parse_sections,
    read_docx_paragraphs,
)


TITLE = "Borrow. Delay. Repeat."
AUTHOR = "Sabino Pereira"
LANGUAGE = "en"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/borrow-delay-repeat"))

EPUB_DIR = OUT_DIR / "ebook-build"
EPUB_PATH = OUT_DIR / "borrow-delay-repeat-kindle-ebook.epub"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def file_name(index: int) -> str:
    return f"section-{index:02d}.xhtml"


def image_name(title: str) -> str | None:
    mapping = {
        "Chapter 1 - Ask Nicely": "ask.png",
        "Chapter 2 - Promise Tomorrow": "tomorrow.png",
        "Chapter 3 - Strategic Disappearance": "disappear.png",
        "Chapter 4 - Image Control": "image-control.png",
        "Chapter 5 - The Follow-up Defense": "defense.png",
        "Chapter 6 - The Reset": "reset.png",
    }
    return mapping.get(title)


def make_illustration(kind: str, path: Path) -> None:
    width, height = 1000, 420
    im = Image.new("RGB", (width, height), "#fbfaf5")
    draw = ImageDraw.Draw(im)
    impact = "/System/Library/Fonts/Supplemental/Impact.ttf"
    georgia = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    georgia_italic = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
    black = "#161616"
    grey = "#8d8a80"

    draw.rectangle([30, 30, width - 30, height - 30], outline=black, width=4)
    if kind == "ask":
        draw.rounded_rectangle([170, 135, 830, 270], radius=20, outline=black, width=5)
        draw.text((255, 177), "Hey... this is awkward", font=ImageFont.truetype(georgia, 44), fill=black)
        draw.line([360, 318, 640, 318], fill=black, width=5)
    elif kind == "tomorrow":
        draw.rectangle([280, 90, 720, 330], outline=black, width=5)
        draw.line([280, 155, 720, 155], fill=black, width=5)
        draw.text((330, 215), "TOMORROW", font=ImageFont.truetype(impact, 88), fill=black)
    elif kind == "disappear":
        draw.rounded_rectangle([365, 70, 635, 350], radius=32, outline=black, width=5)
        draw.text((440, 165), "seen", font=ImageFont.truetype(georgia_italic, 42), fill=black)
        draw.text((442, 225), "...", font=ImageFont.truetype(impact, 76), fill=black)
    elif kind == "image-control":
        draw.ellipse([380, 90, 620, 330], outline=black, width=5)
        draw.arc([330, 170, 670, 420], 200, 340, fill=black, width=5)
        draw.line([280, 95, 720, 95], fill=black, width=5)
        draw.text((325, 352), "public image, private delay", font=ImageFont.truetype(georgia, 32), fill=grey)
    elif kind == "defense":
        draw.rounded_rectangle([360, 75, 640, 345], radius=45, outline=black, width=5)
        draw.text((462, 135), "?", font=ImageFont.truetype(impact, 160), fill=black)
    else:
        draw.ellipse([350, 80, 650, 380], outline=black, width=5)
        draw.text((395, 185), "RESET", font=ImageFont.truetype(impact, 72), fill=black)
        draw.arc([370, 105, 630, 365], 25, 315, fill=black, width=5)
    im.save(path, "PNG", optimize=True)


def paragraph_html(text: str) -> str:
    escaped = html.escape(text)
    if text == "Part 1 - The Basics":
        return f"<h2>{escaped}</h2>"
    if len(text) <= 34 and not text.endswith("."):
        return f'<p class="short">{escaped}</p>'
    return f"<p>{escaped}</p>"


def build_section(section, index: int) -> str:
    parts = [f'<section epub:type="chapter" id="section-{index:02d}">', f"<h1>{html.escape(section.title)}</h1>"]
    img = image_name(section.title)
    if img:
        parts.append(f'<figure><img src="images/{img}" alt="Illustration for {html.escape(section.title)}"/></figure>')
    for text in section.paragraphs:
        parts.append(paragraph_html(text))
    parts.append("</section>")
    return xhtml_page(section.title, "\n".join(parts))


def build_nav(sections) -> str:
    items = "\n".join(
        f'      <li><a href="{file_name(i)}">{html.escape(section.title)}</a></li>'
        for i, section in enumerate(sections, 1)
    )
    body = f'''  <nav epub:type="toc" id="toc">
    <h1>Contents</h1>
    <ol>
{items}
    </ol>
  </nav>
  <nav epub:type="landmarks" hidden="hidden">
    <h2>Guide</h2>
    <ol>
      <li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
      <li><a epub:type="toc" href="nav.xhtml">Contents</a></li>
      <li><a epub:type="bodymatter" href="section-01.xhtml">Start</a></li>
    </ol>
  </nav>'''
    return xhtml_page("Contents", body)


def build_ncx(sections) -> str:
    nav_points = []
    for i, section in enumerate(sections, 1):
        nav_points.append(
            f'''    <navPoint id="navPoint-{i}" playOrder="{i}">
      <navLabel><text>{html.escape(section.title)}</text></navLabel>
      <content src="{file_name(i)}"/>
    </navPoint>'''
        )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{BOOK_ID}"/>
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


def build_opf(sections) -> str:
    section_items = "\n".join(
        f'    <item id="section-{i:02d}" href="{file_name(i)}" media-type="application/xhtml+xml"/>'
        for i, _ in enumerate(sections, 1)
    )
    section_spine = "\n".join(f'    <itemref idref="section-{i:02d}"/>' for i, _ in enumerate(sections, 1))
    image_items = "\n".join(
        f'    <item id="{Path(img).stem}" href="images/{img}" media-type="image/png"/>'
        for img in ["ask.png", "tomorrow.png", "disappear.png", "image-control.png", "defense.png", "reset.png"]
    )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{LANGUAGE}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
    <dc:title>{html.escape(TITLE)}</dc:title>
    <dc:creator>{html.escape(AUTHOR)}</dc:creator>
    <dc:language>{LANGUAGE}</dc:language>
    <dc:publisher>{html.escape(AUTHOR)}</dc:publisher>
    <meta name="cover" content="cover-image"/>
    <meta property="dcterms:modified">2026-05-19T20:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="style" href="styles.css" media-type="text/css"/>
    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
    <item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
{image_items}
{section_items}
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover" linear="no"/>
{section_spine}
  </spine>
</package>
'''


def build_epub() -> None:
    if not COVER_JPG.exists():
        create_cover(COVER_JPG)
    if EPUB_DIR.exists():
        shutil.rmtree(EPUB_DIR)

    _, _, sections = parse_sections(read_docx_paragraphs(SOURCE_DOCX))
    (EPUB_DIR / "META-INF").mkdir(parents=True)
    (EPUB_DIR / "OEBPS/images").mkdir(parents=True)
    write(EPUB_DIR / "mimetype", "application/epub+zip")
    write(
        EPUB_DIR / "META-INF/container.xml",
        '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
''',
    )
    write(
        EPUB_DIR / "OEBPS/styles.css",
        """body {
  color: #151515;
  font-family: Georgia, serif;
  line-height: 1.55;
  margin: 0 7%;
}
h1 {
  font-size: 1.65em;
  line-height: 1.15;
  margin: 1.1em 0 0.75em;
}
h2 {
  font-size: 1.1em;
  margin: 1.2em 0 0.8em;
  text-align: center;
}
p {
  margin: 0 0 0.85em;
}
.short {
  font-style: italic;
  text-align: center;
}
.cover {
  margin: 0;
  padding: 0;
  text-align: center;
}
.cover img,
figure img {
  height: auto;
  max-width: 100%;
}
figure {
  margin: 0.8em 0 1.2em;
  text-align: center;
}
nav ol {
  line-height: 1.8;
}
""",
    )
    write(EPUB_DIR / "OEBPS/nav.xhtml", build_nav(sections))
    write(EPUB_DIR / "OEBPS/toc.ncx", build_ncx(sections))
    write(EPUB_DIR / "OEBPS/content.opf", build_opf(sections))
    write(
        EPUB_DIR / "OEBPS/cover.xhtml",
        xhtml_page("Cover", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Borrow. Delay. Repeat. cover"/></section>'),
    )
    shutil.copyfile(COVER_JPG, EPUB_DIR / "OEBPS/images/cover.jpg")
    for kind in ["ask", "tomorrow", "disappear", "image-control", "defense", "reset"]:
        make_illustration(kind, EPUB_DIR / f"OEBPS/images/{kind}.png")
    for i, section in enumerate(sections, 1):
        write(EPUB_DIR / "OEBPS" / file_name(i), build_section(section, i))

    if EPUB_PATH.exists():
        EPUB_PATH.unlink()
    with zipfile.ZipFile(EPUB_PATH, "w") as zf:
        zf.write(EPUB_DIR / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for file in sorted(EPUB_DIR.rglob("*")):
            if file.is_file() and file.name != "mimetype":
                zf.write(file, file.relative_to(EPUB_DIR), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(EPUB_DIR)


def main() -> None:
    build_epub()
    print(EPUB_PATH)


if __name__ == "__main__":
    main()
