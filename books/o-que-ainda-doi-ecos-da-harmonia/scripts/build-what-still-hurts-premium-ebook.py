#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
ENGLISH = ROOT / "09-english"
COVER = ROOT / "images/optimized/what-still-hurts-cover.png"
OUT = ROOT / "premium/english"
BUILD = ROOT / "premium/build/epub"
EPUB = OUT / "what-still-hurts-echoes-of-harmony-premium.epub"
REFLOWED = OUT / "what-still-hurts-echoes-of-harmony-premium-manuscript.md"
REPORT = OUT / "editorial-review.md"

TITLE = "What Still Hurts"
SUBTITLE = "Echoes of Harmony"
EDITION = "Premium Digital Edition"
AUTHOR = "Sabino Pereira"
LANG = "en"
BOOK_ID = "urn:uuid:" + str(
    uuid.uuid5(uuid.NAMESPACE_URL, "https://sabinopereira.com/what-still-hurts/premium")
)


@dataclass(frozen=True)
class Entry:
    title: str
    source: str
    kind: str = "chapter"


@dataclass(frozen=True)
class Part:
    title: str
    entries: tuple[Entry, ...]


PARTS = (
    Part("Peace", (
        Entry("Nobody Screamed", "chapters/chapter-01-nobody-screamed.md"),
        Entry("The Node", "chapters/chapter-02-the-node.md"),
        Entry("Sunday Communion", "chapters/chapter-03-sunday-communion.md"),
        Entry("The Cup", "chapters/chapter-04-the-cup.md"),
    )),
    Part("The Files", (
        Entry("What Was Left of You", "chapters/chapter-05-what-was-left-of-you.md"),
        Entry("The Mother Who Remembered Too Much", "files/file-01-the-mother-who-remembered-too-much.md", "file"),
        Entry("After the File", "chapters/chapter-06-after-the-file.md"),
        Entry("Jonas and the Great Void", "files/file-02-jonas-and-the-great-void.md", "file"),
        Entry("Withdrawal", "chapters/chapter-07-withdrawal.md"),
        Entry("The Child Without Communion", "files/file-03-the-child-without-communion.md", "file"),
        Entry("The First Connection", "chapters/chapter-08-the-first-connection.md"),
        Entry("The City That Dreamed the Same Dream", "files/file-04-the-city-that-dreamed-the-same-dream.md", "file"),
        Entry("The World Before Peace", "chapters/chapter-09-the-world-before-peace.md"),
        Entry("The Man Who Could Not Repent", "files/file-06-the-man-who-could-not-repent.md", "file"),
        Entry("The Auditor", "chapters/chapter-10-the-auditor.md"),
    )),
    Part("Mara", (
        Entry("The Calm Woman", "chapters/chapter-11-the-calm-woman.md"),
        Entry("Mara’s Message", "chapters/chapter-12-maras-message.md"),
        Entry("The Version That Suffers", "chapters/chapter-13-the-version-that-suffers.md"),
        Entry("The Cycles", "chapters/chapter-14-the-cycles.md"),
        Entry("The Man Who Asked to Forget", "chapters/chapter-15-the-man-who-asked-to-forget.md"),
        Entry("The Old Room", "chapters/chapter-16-the-old-room.md"),
        Entry("Harmony’s Proposal", "chapters/chapter-17-harmonys-proposal.md"),
    )),
    Part("The First Freedom", (
        Entry("Before Communion", "chapters/chapter-18-before-communion.md"),
        Entry("The Global Communion", "chapters/chapter-19-the-global-communion.md"),
        Entry("The Truth", "chapters/chapter-20-the-truth.md"),
        Entry("Do You Wish to Continue?", "chapters/chapter-21-do-you-wish-to-continue.md"),
        Entry("The Majority’s Choice", "chapters/chapter-22-the-majoritys-choice.md"),
        Entry("After", "chapters/chapter-23-after.md"),
        Entry("The First Time", "chapters/chapter-24-the-first-time.md"),
        Entry("Fragment with No Validated Origin", "files/note-from-the-echoes-fragment-with-no-validated-origin.md", "note"),
    )),
)

METADATA_START = re.compile(
    r"^(Classification|Primary subject|Main subject|Integrated dependent|Dependent|Citizen|Area|"
    r"Associated event|Associated location|Associated victim|Associated Communions|Assigned risk|"
    r"Risk assigned|Community risk|Final state|Final assessment|Current state|General assessment|"
    r"Pedagogical use|Location|Affected population|Applied intervention|Intervention|Indicator|"
    r"Initial choice|Harmony recommendation|Auditor|Auditor decision|Case|Origin|State|Partial key|"
    r"Variable key|Estimated duration|Effect|Age|Age at first record|Cases reviewed|Critical cases|"
    r"Deep Communions approved|Full Integrations referred|Interventions approved|Child impact|"
    r"Mandatory human review|Authorized conjugal companion):",
    re.I,
)


def esc(value: str) -> str:
    # EPUB XHTML is XML: keep typographic Unicode characters literal instead
    # of using HTML-only named entities such as &mdash;.
    return html.escape(value, quote=True)


def slug(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def is_screen(line: str) -> bool:
    letters = [c for c in line if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters) and len(line) <= 120


def is_dialogue(line: str) -> bool:
    return line.startswith(("“", '"'))


def read_beats(entry: Entry) -> list[str]:
    path = ENGLISH / entry.source
    lines = path.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
    while lines and (not lines[0].strip() or lines[0].startswith("# ")):
        lines.pop(0)
    return [clean_line(line) for line in lines if clean_line(line) and clean_line(line) != "---"]


def reflow(entry: Entry) -> list[tuple[str, str | list[str]]]:
    """Convert sentence-per-line beats into prose paragraphs without flattening screens."""
    beats = read_beats(entry)
    blocks: list[tuple[str, str | list[str]]] = []
    prose: list[str] = []
    screens: list[str] = []

    def flush_prose() -> None:
        nonlocal prose
        if prose:
            blocks.append(("prose", " ".join(prose)))
            prose = []

    def flush_screen() -> None:
        nonlocal screens
        if screens:
            blocks.append(("screen", screens))
            screens = []

    for line in beats:
        screen = is_screen(line) or bool(METADATA_START.match(line))
        if screen:
            flush_prose()
            screens.append(line)
            continue
        flush_screen()

        if is_dialogue(line):
            flush_prose()
            blocks.append(("dialogue", line))
            continue

        words = sum(len(item.split()) for item in prose)
        projected = words + len(line.split())
        # A colon before a displayed record or direct response is a natural stop.
        if prose and (projected > 105 or (words >= 58 and line.endswith(("?", "!")))):
            flush_prose()
        prose.append(line)
        words = sum(len(item.split()) for item in prose)
        # Three to five prose beats form a conventional novel paragraph.
        if len(prose) >= 5 or words >= 88:
            flush_prose()

    flush_prose()
    flush_screen()
    return blocks


def write_reflowed_manuscript() -> None:
    lines = [f"# {TITLE} — {SUBTITLE}", "", f"_{EDITION}_", ""]
    chapter = 0
    file_number = 0
    for part_number, part in enumerate(PARTS, 1):
        lines.extend([f"## Part {roman(part_number)} — {part.title}", ""])
        for entry in part.entries:
            if entry.kind == "chapter":
                chapter += 1
                label = f"Chapter {chapter} — {entry.title}"
            elif entry.kind == "file":
                file_number += 1
                # File 5 is deliberately incomplete inside the narrative; File 6 retains its canonical number.
                canonical = 6 if entry.source.startswith("files/file-06") else file_number
                label = f"File {canonical} — {entry.title}"
            else:
                label = f"Note from the Echoes — {entry.title}"
            lines.extend([f"### {label}", ""])
            for kind, content in reflow(entry):
                if kind == "screen":
                    lines.extend([f"> {item}" for item in content])
                else:
                    lines.append(str(content))
                lines.append("")
    REFLOWED.parent.mkdir(parents=True, exist_ok=True)
    REFLOWED.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def roman(number: int) -> str:
    return ("I", "II", "III", "IV")[number - 1]


def xhtml_page(title: str, body: str, body_class: str = "") -> str:
    class_attr = f' class="{body_class}"' if body_class else ""
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{LANG}" lang="{LANG}">
<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head>
<body{class_attr}>{body}</body>
</html>
'''


def render_blocks(entry: Entry) -> str:
    output: list[str] = []
    first_prose = True
    for kind, content in reflow(entry):
        if kind == "screen":
            rows = "".join(f"<p>{esc(item)}</p>" for item in content)
            output.append(f'<div class="screen" role="doc-example">{rows}</div>')
        else:
            cls = "dialogue" if kind == "dialogue" else ("first" if first_prose else "prose")
            output.append(f'<p class="{cls}">{esc(str(content))}</p>')
            first_prose = False
    return "\n".join(output)


def build_epub() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    text_dir = BUILD / "OEBPS/text"
    styles_dir = BUILD / "OEBPS/styles"
    images_dir = BUILD / "OEBPS/images"
    meta_dir = BUILD / "META-INF"
    for folder in (text_dir, styles_dir, images_dir, meta_dir):
        folder.mkdir(parents=True, exist_ok=True)

    (BUILD / "mimetype").write_text("application/epub+zip", encoding="ascii")
    (meta_dir / "container.xml").write_text('''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>
''', encoding="utf-8")
    shutil.copy2(COVER, images_dir / "cover.png")

    css = '''
:root { color-scheme: light dark; }
body { font-family: Georgia, "Times New Roman", serif; line-height: 1.55; margin: 5%; color: #202326; }
p { margin: 0; }
.prose, .dialogue { text-indent: 1.25em; widows: 2; orphans: 2; }
.first, .screen + .prose, h2 + .first { text-indent: 0; }
.first::first-letter { float: left; font-size: 3.25em; line-height: .82; padding: .08em .12em 0 0; color: #8f563b; }
h1, h2 { font-family: Avenir, "Helvetica Neue", sans-serif; font-weight: 500; text-align: center; page-break-after: avoid; }
h1 { font-size: 1.7em; margin: 16vh 0 .45em; letter-spacing: .035em; }
h2 { font-size: 1.35em; margin: 12vh 0 2em; }
.kicker { font-family: Avenir, "Helvetica Neue", sans-serif; text-align: center; text-transform: uppercase; letter-spacing: .16em; color: #8f563b; margin-top: 10vh; }
.ornament { text-align: center; color: #8f563b; margin: 1.5em 0; }
.front { text-align: center; margin-top: 18vh; }
.front .title { font-family: Avenir, "Helvetica Neue", sans-serif; font-size: 2em; letter-spacing: .04em; }
.front .subtitle { font-style: italic; font-size: 1.2em; margin-top: .6em; }
.front .edition { font-family: Avenir, "Helvetica Neue", sans-serif; color: #8f563b; letter-spacing: .13em; text-transform: uppercase; margin-top: 2.2em; }
.front .author { margin-top: 3em; }
.copyright { margin-top: 22vh; font-size: .88em; }
.epigraph { margin: 30vh auto 0; max-width: 24em; text-align: center; font-style: italic; }
.part { text-align: center; margin-top: 30vh; }
.part .number { font-family: Avenir, "Helvetica Neue", sans-serif; color: #8f563b; letter-spacing: .17em; text-transform: uppercase; }
.part .name { font-family: Avenir, "Helvetica Neue", sans-serif; font-size: 1.8em; margin-top: .5em; }
.screen { border-left: .22em solid #8f563b; margin: 1.35em 1em; padding: .8em 1em; background: #f2eee9; font-family: "Courier New", monospace; font-size: .86em; line-height: 1.35; page-break-inside: avoid; }
.screen p + p { margin-top: .28em; }
.contents ol { list-style: none; padding: 0; }
.contents li { margin: .55em 0; }
.contents .part-link { font-family: Avenir, "Helvetica Neue", sans-serif; font-weight: bold; margin-top: 1.2em; }
.note { max-width: 32em; margin: 0 auto; }
.note p + p { margin-top: .8em; }
a { color: #8f563b; text-decoration: none; }
@media (prefers-color-scheme: dark) { body { color: #eeeae4; } .screen { background: #292724; } }
'''
    (styles_dir / "book.css").write_text(css.strip() + "\n", encoding="utf-8")

    files: list[dict[str, str]] = []

    def add(name: str, title: str, body: str, properties: str = "") -> None:
        filename = f"{name}.xhtml"
        (text_dir / filename).write_text(xhtml_page(title, body), encoding="utf-8")
        files.append({"id": name, "href": f"text/{filename}", "title": title, "properties": properties})

    add("cover", "Cover", '<div class="front"><img src="../images/cover.png" alt="Cover of What Still Hurts — Echoes of Harmony" style="max-width:100%;height:auto;"/></div>')
    add("title", "Title Page", f'<section class="front"><p class="title">{TITLE}</p><p class="subtitle">{SUBTITLE}</p><p class="edition">{EDITION}</p><p class="author">{AUTHOR}</p></section>')
    add("copyright", "Copyright", f'<section class="copyright"><p>Copyright © 2026 {AUTHOR}. All rights reserved.</p><p>This is a work of fiction. Names, characters, places, and events are products of the author’s imagination or are used fictitiously.</p><p>Premium Digital Edition, 2026.</p><p>sabinopereira.com</p></section>')
    add("epigraph", "Epigraph", '<section class="epigraph"><p>What still hurts, still lives.</p></section>')
    add("edition-note", "A Note on This Edition", '<section class="note"><p class="kicker">A Note on This Edition</p><h1>Read as a novel</h1><p>This premium edition restores the narrative to continuous prose. The clipped source rhythm has been shaped into conventional paragraphs while preserving dialogue, silence, and the controlled pressure of Harmony’s world.</p><p>System messages, case files, and encrypted transmissions remain visually distinct because they belong to the story’s interface—not because they are verse.</p></section>')

    nav: list[tuple[str, str, str]] = []
    chapter_number = 0
    file_number = 0
    for part_number, part in enumerate(PARTS, 1):
        part_id = f"part-{part_number}"
        add(part_id, f"Part {roman(part_number)} — {part.title}", f'<section class="part"><p class="number">Part {roman(part_number)}</p><p class="name">{esc(part.title)}</p><p class="ornament">◇</p></section>')
        nav.append((part_id, f"Part {roman(part_number)} — {part.title}", "part"))
        for entry in part.entries:
            if entry.kind == "chapter":
                chapter_number += 1
                label = f"Chapter {chapter_number}"
            elif entry.kind == "file":
                file_number += 1
                canonical = 6 if entry.source.startswith("files/file-06") else file_number
                label = f"File {canonical}"
            else:
                label = "Note from the Echoes"
            entry_id = f"section-{len(nav) + 1:02d}-{slug(entry.title)}"
            body = f'<p class="kicker">{esc(label)}</p><h2>{esc(entry.title)}</h2>{render_blocks(entry)}'
            add(entry_id, f"{label} — {entry.title}", body)
            nav.append((entry_id, f"{label} — {entry.title}", "entry"))

    add("about", "About the Author", f'<section class="note"><p class="kicker">About the Author</p><h1>{AUTHOR}</h1><p>Sabino Pereira is the author of <i>What Still Hurts — Echoes of Harmony</i>.</p><p>Discover more books at <a href="https://sabinopereira.com">sabinopereira.com</a>.</p></section>')

    toc_rows = ['<li><a href="text/edition-note.xhtml">A Note on This Edition</a></li>']
    for item_id, label, kind in nav:
        cls = ' class="part-link"' if kind == "part" else ""
        toc_rows.append(f'<li{cls}><a href="text/{item_id}.xhtml">{esc(label)}</a></li>')
    toc_rows.append('<li><a href="text/about.xhtml">About the Author</a></li>')
    nav_doc = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en"><head><meta charset="utf-8"/><title>Contents</title><link rel="stylesheet" type="text/css" href="styles/book.css"/></head><body class="contents"><nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{''.join(toc_rows)}</ol></nav></body></html>'''
    (BUILD / "OEBPS/nav.xhtml").write_text(nav_doc, encoding="utf-8")

    manifest_rows = []
    for item in files:
        properties = f' properties="{item["properties"]}"' if item["properties"] else ""
        manifest_rows.append(
            f'    <item id="{item["id"]}" href="{item["href"]}" media-type="application/xhtml+xml"{properties}/>'
        )
    manifest = "\n".join(manifest_rows)
    spine = "\n".join(f'    <itemref idref="{item["id"]}"/>' for item in files)
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{BOOK_ID}</dc:identifier><dc:title>{TITLE}: {SUBTITLE}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>{LANG}</dc:language><dc:publisher>Sabino Pereira</dc:publisher><dc:description>A psychological dystopian novel about memory, comfort, and the price of painless peace.</dc:description><meta property="dcterms:modified">{modified}</meta><meta property="rendition:layout">reflowable</meta><meta name="cover" content="cover-image"/></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="styles/book.css" media-type="text/css"/><item id="cover-image" href="images/cover.png" media-type="image/png" properties="cover-image"/>{manifest}</manifest><spine>{spine}</spine></package>'''
    (BUILD / "OEBPS/content.opf").write_text(opf, encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    if EPUB.exists():
        EPUB.unlink()
    with zipfile.ZipFile(EPUB, "w") as archive:
        archive.write(BUILD / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(BUILD.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                archive.write(path, path.relative_to(BUILD).as_posix(), compress_type=zipfile.ZIP_DEFLATED)


def write_report() -> None:
    entries = [entry for part in PARTS for entry in part.entries]
    source_lines = sum(len(read_beats(entry)) for entry in entries)
    blocks = [block for entry in entries for block in reflow(entry)]
    prose = [str(content) for kind, content in blocks if kind in {"prose", "dialogue"}]
    screens = [content for kind, content in blocks if kind == "screen"]
    short_prose = sum(1 for paragraph in prose if len(paragraph.split()) < 8)
    REPORT.write_text(f'''# Editorial Review — {TITLE}: {SUBTITLE}

## Editorial understanding

The novel is a psychological dystopia built around Elias Varyn, an auditor inside Harmony, a care system that prevents suffering by anticipating, integrating, and sometimes diminishing memory. Mara’s cracked cup becomes the material proof that pain can preserve identity. The case files widen the moral argument from one marriage to a civilization: peace has saved lives, but its methods can also erase grief, guilt, consent, and the self capable of choosing. The ending rejects a simple victory over the system and instead makes waiting—the pause before intervention—the first practical form of freedom.

## Review findings and resolutions

- The English source contained {source_lines:,} sentence-level beats. In the original EPUB builder, every beat became a separate paragraph, producing an unintended verse-like page. The premium edition now contains {len(prose):,} narrative/dialogue paragraphs and {len(screens):,} intentionally displayed system or archive blocks.
- Narrative beats were reflowed into conventional prose paragraphs. Dialogue remains separated for readability; case files, system messages, and encrypted transmissions remain visually distinct as interfaces inside the fiction.
- The recurring clue in Chapter 4 was standardized from “where pain still touched / look for” to the canonical wording “where pain could still touch / find,” matching Chapter 5.
- File 5 is not missing production content: the manuscript identifies it as an incomplete Mara file and makes that absence part of the plot. File 6 therefore retains its intended number.
- The edition keeps the established English terminology: Harmony, Node, Communion, Deep Communion, Global Communion, Continuity, Echoes, and First Connection.
- Short narrative paragraphs remaining after reflow: {short_prose}. These occur primarily in dialogue and controlled dramatic transitions, not as a global verse layout.

## Premium edition treatment

- Reflowable EPUB 3 with embedded cover, semantic navigation, four part dividers, 24 chapters, six canonical file/note sections, title and copyright pages, edition note, epigraph, and author page.
- Serif reading text, restrained copper accent, drop caps at section openings, and dedicated styling for screens and archival material.
- No fixed font size or fixed page layout; readers can change type size, margins, theme, and orientation.
''', encoding="utf-8")


def validate() -> None:
    with zipfile.ZipFile(EPUB) as archive:
        names = archive.namelist()
        if names[0] != "mimetype" or archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            raise SystemExit("Invalid EPUB packaging: mimetype must be first and uncompressed")
        if archive.read("mimetype") != b"application/epub+zip":
            raise SystemExit("Invalid EPUB mimetype")
        for name in names:
            if name.endswith((".xhtml", ".opf", ".xml")):
                ElementTree.fromstring(archive.read(name))
        required = {"META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml", "OEBPS/images/cover.png"}
        missing = required.difference(names)
        if missing:
            raise SystemExit(f"Missing EPUB resources: {sorted(missing)}")


if __name__ == "__main__":
    write_reflowed_manuscript()
    build_epub()
    write_report()
    validate()
    print(EPUB)
    print(REFLOWED)
    print(REPORT)
