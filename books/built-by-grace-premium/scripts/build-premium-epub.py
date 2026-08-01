#!/usr/bin/env python3
"""Build the reflowable EPUB 3 edition of Built by Grace."""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build" / "built-by-grace-premium-manuscript.md"
COVER_SOURCE = ROOT / "assets" / "built-by-grace-premium-cover-v2.png"
OUTPUT = ROOT / "dist" / "Built by Grace - Premium Edition.epub"


def inline(text: str) -> str:
    escaped = html.escape(text.strip())
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"_([^_]+)_", r"<em>\1</em>", escaped)
    return escaped


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "section"


def split_sections(source: str) -> list[list[str]]:
    return [part.strip().splitlines() for part in re.split(r"(?m)^\\pagebreak\s*$", source) if part.strip()]


def section_title(lines: list[str]) -> str:
    headings = [re.sub(r"^#{1,6}\s+", "", line).strip() for line in lines if re.match(r"^#{1,6}\s+", line)]
    if not headings:
        return "Built by Grace"
    if headings[0].lower().startswith("chapter ") and len(headings) > 1:
        return f"{headings[0]} — {headings[1]}"
    if headings[0] in {"Introduction", "Bonus Reflection", "Closing"} and len(headings) > 1:
        return f"{headings[0]} — {headings[1]}"
    return headings[0]


def paragraphs(lines: list[str]) -> str:
    output: list[str] = []
    buffer: list[str] = []
    special: str | None = None

    def flush() -> None:
        nonlocal buffer
        if not buffer:
            return
        body = " ".join(piece.strip() for piece in buffer).strip()
        if body:
            css = f' class="{special}"' if special else ""
            output.append(f"<p{css}>{inline(body)}</p>")
        buffer = []

    for raw in lines:
        line = raw.rstrip()
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            flush()
            level = min(len(heading.group(1)) + 1, 4)
            text = heading.group(2).strip()
            if text in {"Prayer", "Closing Thought"}:
                special = slug(text)
            output.append(f'<h{level} id="{slug(text)}">{inline(text)}</h{level}>')
            continue
        if not line.strip():
            flush()
            continue
        if line.endswith("  "):
            buffer.append(line[:-2])
            flush()
            continue
        buffer.append(line)
    flush()
    return "\n".join(output)


def xhtml(title: str, body: str, body_class: str = "") -> str:
    class_attr = f' class="{body_class}"' if body_class else ""
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="styles.css"/></head>
<body{class_attr}>{body}</body>
</html>
'''


def build() -> None:
    sections = split_sections(SOURCE.read_text(encoding="utf-8"))
    book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'https://sabinopereira.com/books/built-by-grace')}"

    with tempfile.TemporaryDirectory(prefix="built-by-grace-epub-") as temp_name:
        temp = Path(temp_name)
        meta_inf = temp / "META-INF"
        epub = temp / "EPUB"
        meta_inf.mkdir()
        epub.mkdir()
        (temp / "mimetype").write_text("application/epub+zip", encoding="ascii")
        (meta_inf / "container.xml").write_text('''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
''', encoding="utf-8")

        cover_path = epub / "cover.png"
        try:
            subprocess.run(["sips", "-z", "2560", "1600", str(COVER_SOURCE), "--out", str(cover_path)], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            shutil.copy2(COVER_SOURCE, cover_path)

        (epub / "styles.css").write_text('''
@namespace epub "http://www.idpf.org/2007/ops";
body { font-family: Georgia, serif; line-height: 1.55; margin: 5%; color: #241d18; }
h1, h2, h3, h4 { color: #513f2d; font-weight: normal; text-align: center; page-break-after: avoid; }
h1 { font-size: 2em; margin: 2.5em 0 0.35em; }
h2 { font-size: 1.45em; margin: 1.8em 0 1.2em; }
h3 { font-size: 1.1em; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2em; }
h4 { font-size: 1em; margin-top: 1.8em; }
p { margin: 0 0 0.85em; text-align: left; }
.prayer { font-style: italic; }
.closing-thought { text-align: center; font-style: italic; margin: 1.5em 8%; }
.frontmatter { text-align: center; }
.cover { margin: 0; padding: 0; text-align: center; }
.cover img { width: 100%; height: auto; max-height: 100vh; object-fit: contain; }
nav ol { list-style: none; padding-left: 0; }
nav li { margin: 0.6em 0; }
nav a { color: #513f2d; text-decoration: none; }
''', encoding="utf-8")

        (epub / "cover.xhtml").write_text(xhtml("Cover", '<div class="cover"><img src="cover.png" alt="Built by Grace cover"/></div>', "cover"), encoding="utf-8")

        manifest_items = [
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            '<item id="css" href="styles.css" media-type="text/css"/>',
            '<item id="cover-image" href="cover.png" media-type="image/png" properties="cover-image"/>',
            '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
        ]
        spine_items = ['<itemref idref="cover" linear="yes"/>']
        nav_entries: list[str] = []

        for index, lines in enumerate(sections, start=1):
            title = section_title(lines)
            filename = f"section-{index:02d}.xhtml"
            item_id = f"section-{index:02d}"
            body_class = "frontmatter" if index <= 5 else ""
            (epub / filename).write_text(xhtml(title, paragraphs(lines), body_class), encoding="utf-8")
            manifest_items.append(f'<item id="{item_id}" href="{filename}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="{item_id}"/>')
            nav_entries.append(f'<li><a href="{filename}">{html.escape(title)}</a></li>')

        nav = xhtml("Contents", f'''<nav epub:type="toc" id="toc">
<h1>Contents</h1><ol>{''.join(nav_entries)}</ol></nav>''')
        (epub / "nav.xhtml").write_text(nav, encoding="utf-8")

        package = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">{book_id}</dc:identifier>
    <dc:title id="title">Built by Grace</dc:title>
    <meta refines="#title" property="title-type">main</meta>
    <dc:creator id="creator">Sabino Pereira</dc:creator>
    <meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
    <dc:language>en</dc:language>
    <dc:publisher>Sabino Pereira</dc:publisher>
    <dc:description>A Journey of Prayer, Healing, Love, and God in the Center</dc:description>
    <dc:rights>Copyright © 2026 Sabino Pereira. All rights reserved.</dc:rights>
    <meta property="dcterms:modified">2026-08-01T00:00:00Z</meta>
  </metadata>
  <manifest>{''.join(manifest_items)}</manifest>
  <spine>{''.join(spine_items)}</spine>
</package>
'''
        (epub / "package.opf").write_text(package, encoding="utf-8")

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(OUTPUT, "w") as archive:
            archive.write(temp / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
            for path in sorted(temp.rglob("*")):
                if path.is_file() and path.name != "mimetype":
                    archive.write(path, path.relative_to(temp).as_posix(), compress_type=zipfile.ZIP_DEFLATED)

    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    build()
