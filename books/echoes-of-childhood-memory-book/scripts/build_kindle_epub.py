#!/usr/bin/env python3
"""Build the Amazon Kindle EPUB edition of Echoes of Childhood."""

from __future__ import annotations

import hashlib
import html
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/echoes-of-childhood-final-manuscript.md"
SOURCE_COVER = ROOT / "assets/cover/echoes-of-childhood-memory-book-cover-print-1850x2775.jpg"
SOURCE_IMAGES = ROOT / "assets/illustrations-print-jpeg"
OUT = ROOT / "amazon-kdp/ebook"
STAGE = ROOT / "build/kindle-epub"
EPUB = OUT / "echoes-of-childhood-kindle-ebook.epub"
COVER = OUT / "echoes-of-childhood-kindle-cover.jpg"


@dataclass
class Section:
    slug: str
    title: str
    kind: str
    markdown: str
    image: str | None = None
    label: str | None = None


CHAPTERS = [
    ("chapter-01", "Before the World Got Loud", "01-before-the-world-got-loud.jpg", "Chapter One"),
    ("chapter-02", "Saturday Mornings", "02-saturday-mornings.jpg", "Chapter Two"),
    ("chapter-03", "The Long Summer", "03-the-long-summer.jpg", "Chapter Three"),
    ("chapter-04", "The Toy We Couldn't Put Down", "04-the-toy-we-couldnt-put-down.jpg", "Chapter Four"),
    ("chapter-05", "Until the Streetlights Came On", "05-until-the-streetlights-came-on.jpg", "Chapter Five"),
    ("chapter-06", "The Bell Between Lessons", "06-the-bell-between-lessons.jpg", "Chapter Six"),
    ("chapter-07", "The First Butterfly", "07-the-first-butterfly.jpg", "Chapter Seven"),
    ("chapter-08", "The Hands That Held Ours", "08-the-hands-that-held-ours.jpg", "Chapter Eight"),
    ("chapter-09", "Christmas Morning", "09-christmas-morning.jpg", "Chapter Nine"),
    ("chapter-10", "One Last Summer Evening", "10-one-last-summer-evening.jpg", "Chapter Ten"),
    ("chapter-11", "Echoes of Childhood", "11-echoes-of-childhood.jpg", "Chapter Eleven"),
    ("epilogue", "Home Was Never a Place", "12-home-was-never-a-place.jpg", "Epilogue"),
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def block(markdown: str, heading: str, next_heading: str | None = None) -> str:
    start_marker = f"# {heading}\n"
    start = markdown.index(start_marker) + len(start_marker)
    if next_heading:
        end = markdown.index(f"# {next_heading}\n", start)
    else:
        end = len(markdown)
    return markdown[start:end].strip().removesuffix("---").strip()


def chapter_block(markdown: str, label: str, next_label: str | None) -> str:
    start = markdown.index(f"# {label}\n") + len(f"# {label}\n")
    end = markdown.index(f"# {next_label}\n", start) if next_label else markdown.index("# Acknowledgements\n", start)
    return markdown[start:end].strip().removesuffix("---").strip()


def inline(text: str) -> str:
    value = html.escape(text.strip(), quote=False)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*(.+?)\*", r"<em>\1</em>", value)
    return value


def markdown_html(text: str, omit_first_h2: bool = False) -> str:
    lines = text.splitlines()
    result: list[str] = []
    paragraph: list[str] = []
    first_h2_seen = False

    def flush() -> None:
        if paragraph:
            result.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    for raw in lines:
        line = raw.strip()
        if not line or line == "---":
            flush()
            continue
        if line.startswith("### "):
            flush()
            result.append(f"<h2 class=\"fragment-label\">{inline(line[4:])}</h2>")
        elif line.startswith("## "):
            flush()
            if omit_first_h2 and not first_h2_seen:
                first_h2_seen = True
                continue
            first_h2_seen = True
            result.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("> "):
            flush()
            result.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        else:
            paragraph.append(line)
    flush()
    return "\n".join(result)


def xhtml(title: str, body: str, body_class: str = "") -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="styles.css"/></head>
<body class="{body_class}">{body}</body>
</html>'''


def make_sections(markdown: str) -> list[Section]:
    sections = [
        Section("title", "Echoes of Childhood", "front", ""),
        Section("introduction", "Introduction", "front", block(markdown, "Introduction", "Before You Begin")),
        Section("before-you-begin", "Before You Begin", "front", block(markdown, "Before You Begin", "Contents")),
        Section("part-1", "Where It All Began", "part", "", label="Part One"),
    ]
    labels = [item[3] for item in CHAPTERS]
    for index, (slug, title, image_name, label) in enumerate(CHAPTERS):
        if index == 8:
            sections.append(Section("part-2", "The Echoes We Carry", "part", "", label="Part Two"))
        next_label = labels[index + 1] if index + 1 < len(labels) else None
        sections.append(Section(slug, title, "chapter", chapter_block(markdown, label, next_label), image_name, label))
    sections.extend([
        Section("acknowledgements", "Acknowledgements", "back", block(markdown, "Acknowledgements", "Final Page")),
        Section("final-page", "One Day", "back", block(markdown, "Final Page")),
    ])
    return sections


def resize_jpeg(source: Path, destination: Path, max_width: int, quality: int = 88) -> None:
    with Image.open(source) as image:
        image = image.convert("RGB")
        if image.width > max_width:
            height = round(image.height * max_width / image.width)
            image = image.resize((max_width, height), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "JPEG", quality=quality, optimize=True, progressive=True)


def section_body(section: Section) -> str:
    if section.kind == "front" and section.slug == "title":
        return '''<section epub:type="titlepage" class="title-page">
<p class="eyebrow">A MEMORY BOOK</p><h1>ECHOES <span>of</span> CHILDHOOD</h1>
<p class="tagline">The days we didn't know we'd miss.</p>
<div class="credits"><p>Written by Sabino Pereira</p><p>Music by RB</p></div></section>'''
    if section.kind == "part":
        return f'''<section epub:type="part" class="part-page"><p class="eyebrow">{html.escape(section.label or '')}</p>
<h1>{html.escape(section.title)}</h1><div class="ornament">◆</div></section>'''
    if section.kind == "chapter":
        image = f'<figure><img src="images/{html.escape(section.image or "")}" alt="Illustration for {html.escape(section.title)}"/></figure>'
        content = markdown_html(section.markdown, omit_first_h2=True)
        return f'''<article epub:type="chapter" class="chapter">{image}<header><p class="eyebrow">{html.escape(section.label or '')}</p>
<h1>{html.escape(section.title)}</h1></header>{content}</article>'''
    return f'''<section class="front-back"><h1>{html.escape(section.title)}</h1>{markdown_html(section.markdown)}</section>'''


def build() -> None:
    markdown = MANUSCRIPT.read_text(encoding="utf-8")
    sections = make_sections(markdown)
    if STAGE.exists():
        shutil.rmtree(STAGE)
    (STAGE / "META-INF").mkdir(parents=True)
    (STAGE / "OEBPS/images").mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)

    resize_jpeg(SOURCE_COVER, COVER, 1800, 92)
    shutil.copyfile(COVER, STAGE / "OEBPS/images/cover.jpg")
    for _, _, image_name, _ in CHAPTERS:
        resize_jpeg(SOURCE_IMAGES / image_name, STAGE / f"OEBPS/images/{image_name}", 1400, 86)

    write(STAGE / "mimetype", "application/epub+zip")
    write(STAGE / "META-INF/container.xml", '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles></container>''')

    css = '''@charset "UTF-8";
body { color:#172438; background:#fbf4e3; font-family: Georgia, "Times New Roman", serif; line-height:1.58; margin:0 5%; }
p { margin:0 0 1em; text-align:left; }
h1,h2 { font-weight:normal; color:#172438; }
h1 { font-size:2em; line-height:1.12; text-align:center; margin:0.35em 0 0.8em; }
h2 { font-size:1.15em; margin:1.5em 0 0.7em; }
.cover { margin:0; padding:0; text-align:center; background:#111; }
.cover img { display:block; width:100%; height:auto; margin:0 auto; }
.title-page,.part-page { text-align:center; padding-top:18%; page-break-after:always; break-after:page; }
.title-page h1 { font-size:2.35em; letter-spacing:0.05em; }
.title-page h1 span { display:block; font-size:0.62em; font-style:italic; letter-spacing:0; }
.tagline { text-align:center; font-style:italic; color:#8a6334; }
.credits { margin-top:25%; font-size:0.85em; letter-spacing:0.08em; text-transform:uppercase; }
.credits p { text-align:center; }
.eyebrow { text-align:center; color:#a6783d; font-size:0.72em; letter-spacing:0.16em; text-transform:uppercase; }
.part-page h1 { margin-top:1em; }
.ornament { color:#a6783d; margin-top:2em; }
.front-back { padding-top:8%; }
.chapter figure { margin:0 -5.5% 2.2em; page-break-after:always; break-after:page; text-align:center; }
.chapter figure img { display:block; width:100%; max-height:96vh; object-fit:contain; margin:auto; }
.chapter header { padding-top:8%; page-break-before:always; break-before:page; }
.chapter header + p { text-align:center; color:#8a6334; font-style:italic; }
.fragment-label { text-align:center; color:#a6783d; font-size:0.72em; letter-spacing:0.13em; text-transform:uppercase; margin-top:2.5em; }
blockquote { margin:0.8em 8% 2em; font-style:italic; text-align:center; color:#354052; }
nav ol { list-style:none; padding:0; }
nav li { margin:0.7em 0; }
nav a { color:#172438; text-decoration:none; }
@media amzn-kf8 { .chapter figure img { height:auto; } }
'''
    write(STAGE / "OEBPS/styles.css", css)
    write(STAGE / "OEBPS/cover.xhtml", xhtml("Cover", '<section epub:type="cover" class="cover"><img src="images/cover.jpg" alt="Cover of Echoes of Childhood: A Memory Book"/></section>', "cover"))

    for section in sections:
        write(STAGE / f"OEBPS/{section.slug}.xhtml", xhtml(section.title, section_body(section), section.kind))

    nav_items = "".join(f'<li><a href="{s.slug}.xhtml">{html.escape(s.label + " — " if s.kind == "chapter" and s.label else "")}{html.escape(s.title)}</a></li>' for s in sections if s.slug != "title")
    nav_body = f'''<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{nav_items}</ol></nav>
<nav epub:type="landmarks" hidden="hidden"><ol><li><a epub:type="cover" href="cover.xhtml">Cover</a></li><li><a epub:type="toc" href="nav.xhtml">Contents</a></li><li><a epub:type="bodymatter" href="introduction.xhtml">Start</a></li></ol></nav>'''
    write(STAGE / "OEBPS/nav.xhtml", xhtml("Contents", nav_body, "navigation"))

    uid = "urn:uuid:" + str(uuid.UUID(hashlib.md5(markdown.encode("utf-8")).hexdigest()))
    image_items = ['<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>']
    for i, (_, _, image_name, _) in enumerate(CHAPTERS, 1):
        image_items.append(f'<item id="image-{i:02d}" href="images/{image_name}" media-type="image/jpeg"/>')
    section_items = "".join(f'<item id="{s.slug}" href="{s.slug}.xhtml" media-type="application/xhtml+xml"/>' for s in sections)
    spine = "".join(f'<itemref idref="{s.slug}"/>' for s in sections)
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">{uid}</dc:identifier><dc:title>Echoes of Childhood: A Memory Book</dc:title><dc:creator>Sabino Pereira</dc:creator><dc:contributor>RB</dc:contributor><dc:language>en</dc:language><dc:publisher>Sabino Pereira</dc:publisher><dc:description>A reflective visual journey through the universal memories of childhood.</dc:description><meta property="dcterms:modified">2026-07-27T00:00:00Z</meta></metadata>
<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/><item id="css" href="styles.css" media-type="text/css"/>{section_items}{''.join(image_items)}</manifest>
<spine><itemref idref="cover"/>{spine}</spine></package>'''
    write(STAGE / "OEBPS/content.opf", opf)

    if EPUB.exists():
        EPUB.unlink()
    with zipfile.ZipFile(EPUB, "w") as archive:
        archive.write(STAGE / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(STAGE.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                archive.write(path, path.relative_to(STAGE), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(STAGE)
    print(EPUB)
    print(COVER)


if __name__ == "__main__":
    build()
