#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_xadrez_kdp_package import (  # noqa: E402
    EBOOK_DIR,
    OUT_DIR,
    SOURCE_HTML,
    Chapter,
    clean_text,
    create_front_cover_art,
    extract_chapters,
)


BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/xadrez-no-comando"))
TITLE = "Xadrez no Comando"
AUTHOR = "Sabino Pereira"
LANGUAGE = "pt-PT"
EPUB_DIR = OUT_DIR / "ebook-build"
EPUB_PATH = EBOOK_DIR / "xadrez-no-comando-kindle-ebook.epub"
COVER_JPG = EBOOK_DIR / "xadrez-no-comando-ebook-cover.jpg"


def ensure_cover() -> None:
    if COVER_JPG.exists():
        return
    tmp = COVER_JPG.with_suffix(".png")
    create_front_cover_art(tmp, 1600, 2560)
    from PIL import Image

    Image.open(tmp).convert("RGB").save(COVER_JPG, "JPEG", quality=95, optimize=True)
    tmp.unlink()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def xhtml_page(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pt-PT" xml:lang="pt-PT">
<head>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
{body}
</body>
</html>
'''


def chapter_filename(index: int) -> str:
    return f"chapter-{index:02d}.xhtml"


def block_to_html(kind: str, text: str) -> str:
    safe = html.escape(text).replace("&lt;br/&gt;", "<br/>")
    if kind == "quote":
        return f'<blockquote class="quote"><p>{safe}</p></blockquote>'
    if kind == "stanza":
        return f'<div class="stanza"><p>{safe}</p></div>'
    return f"<p>{safe}</p>"


def build_chapter(chapter: Chapter, index: int) -> str:
    body = [f'<section epub:type="chapter" id="chapter-{index:02d}">']
    body.append(f"<h1>{html.escape(chapter.title)}</h1>")
    for block in chapter.blocks:
        body.append(block_to_html(block.kind, block.text))
    body.append("</section>")
    return xhtml_page(chapter.title, "\n".join(body))


def build_nav(chapters: list[Chapter]) -> str:
    items = "\n".join(
        f'      <li><a href="{chapter_filename(i)}">{html.escape(chapter.title)}</a></li>'
        for i, chapter in enumerate(chapters, 1)
    )
    body = f'''  <nav epub:type="toc" id="toc">
    <h1>Índice</h1>
    <ol>
{items}
    </ol>
  </nav>
  <nav epub:type="landmarks" hidden="hidden">
    <h2>Guia</h2>
    <ol>
      <li><a epub:type="cover" href="cover.xhtml">Capa</a></li>
      <li><a epub:type="toc" href="nav.xhtml">Índice</a></li>
      <li><a epub:type="bodymatter" href="chapter-01.xhtml">Início</a></li>
    </ol>
  </nav>'''
    return xhtml_page("Índice", body)


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


def build_opf(chapters: list[Chapter]) -> str:
    manifest_chapters = "\n".join(
        f'    <item id="chapter-{i:02d}" href="{chapter_filename(i)}" media-type="application/xhtml+xml"/>'
        for i, _ in enumerate(chapters, 1)
    )
    spine_chapters = "\n".join(f'    <itemref idref="chapter-{i:02d}"/>' for i, _ in enumerate(chapters, 1))
    return f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{LANGUAGE}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
    <dc:title>{html.escape(TITLE)}</dc:title>
    <dc:creator>{html.escape(AUTHOR)}</dc:creator>
    <dc:language>{LANGUAGE}</dc:language>
    <dc:publisher>{html.escape(AUTHOR)}</dc:publisher>
    <meta name="cover" content="cover-image"/>
    <meta property="dcterms:modified">2026-05-19T09:30:00Z</meta>
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


def build_epub(chapters: list[Chapter]) -> None:
    if EPUB_DIR.exists():
        shutil.rmtree(EPUB_DIR)
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
.stanza,
.quote {
  margin: 1em 0 1.1em 1.2em;
  font-style: italic;
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
    write(EPUB_DIR / "OEBPS/nav.xhtml", build_nav(chapters))
    write(EPUB_DIR / "OEBPS/toc.ncx", build_ncx(chapters))
    write(EPUB_DIR / "OEBPS/content.opf", build_opf(chapters))
    write(
        EPUB_DIR / "OEBPS/cover.xhtml",
        xhtml_page("Capa", '<section class="cover" epub:type="cover"><img src="images/cover.jpg" alt="Capa de Xadrez no Comando"/></section>'),
    )
    for i, chapter in enumerate(chapters, 1):
        write(EPUB_DIR / "OEBPS" / chapter_filename(i), build_chapter(chapter, i))
    shutil.copyfile(COVER_JPG, EPUB_DIR / "OEBPS/images/cover.jpg")

    if EPUB_PATH.exists():
        EPUB_PATH.unlink()
    with zipfile.ZipFile(EPUB_PATH, "w") as zf:
        zf.write(EPUB_DIR / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for file in sorted(EPUB_DIR.rglob("*")):
            if file.is_file() and file.name != "mimetype":
                zf.write(file, file.relative_to(EPUB_DIR), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(EPUB_DIR)


def main() -> None:
    ensure_cover()
    chapters = extract_chapters(SOURCE_HTML.read_text(encoding="utf-8"))
    if len(chapters) != 9:
        raise SystemExit(f"Expected 9 chapters, found {len(chapters)}")
    build_epub(chapters)
    print(EPUB_PATH)


if __name__ == "__main__":
    main()
