from pathlib import Path
from html import escape
from uuid import UUID
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ebook" / "um-lugar-a-mesa-edicao-premium-pt.epub"
STAGE = ROOT / "build" / "epub-stage"
OEBPS = STAGE / "OEBPS"
META = STAGE / "META-INF"
COVER = ROOT / "assets" / "um-lugar-a-mesa-cover-premium-1600x2560.jpg"
BOOK_ID = "urn:uuid:53e8f3c6-f319-4e66-9466-f2542f640bda"

CHAPTERS = [ROOT / "source" / f"capitulo-{n:02d}-completo.md" for n in range(1, 13)]
EPILOGUE = ROOT / "source" / "epilogo-completo.md"
CHAPTER_TITLES = [
    "A Mesa", "A Entrada", "O Apetite", "O Ás", "A Rainha", "O Rei",
    "O Homem do Avental", "A Cadeira Sem Nome", "O Envelope Azul",
    "A Mulher na Escada", "Perder de Propósito", "A Porta",
]

def reset_stage():
    if STAGE.exists():
        for p in sorted(STAGE.rglob("*"), reverse=True):
            if p.is_file() or p.is_symlink():
                p.unlink()
            elif p.is_dir():
                p.rmdir()
    OEBPS.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    (OEBPS / "images").mkdir(exist_ok=True)

def xhtml(title, body, body_class=""):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt-PT" lang="pt-PT">
<head><meta charset="utf-8"/><title>{escape(title)}</title><link rel="stylesheet" type="text/css" href="styles.css"/></head>
<body class="{body_class}">{body}</body></html>'''

def clean_markdown(text):
    return text.replace("**", "").replace("*", "").strip()

def prose_blocks(text):
    blocks, buffer = [], []
    chars = 0
    def flush():
        nonlocal buffer, chars
        if buffer:
            blocks.append(("narrative", " ".join(buffer)))
            buffer, chars = [], 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "---":
            flush(); blocks.append(("divider", "◆")); continue
        marked = line.startswith("**") and line.endswith("**")
        plain = clean_markdown(line)
        if line.startswith("“") or line.startswith('"'):
            flush(); blocks.append(("dialogue", plain)); continue
        if marked:
            flush(); blocks.append(("display", plain)); continue
        buffer.append(plain)
        chars += len(plain)
        if len(buffer) >= 4 or chars >= 420 or plain.endswith(":"):
            flush()
    flush()
    return blocks

def chapter_opener(number, epilogue=False):
    label = "EPÍLOGO" if epilogue else f"CAPÍTULO {number}"
    subtitle = "Quando Ninguém Está a Olhar" if epilogue else CHAPTER_TITLES[number - 1]
    return f'<main class="chapter-opener"><div class="opener-inner"><div class="ornament">◆</div><h1>{label}</h1><h2>{escape(subtitle)}</h2><div class="rule"></div></div></main>'

def chapter_text(path):
    blocks = prose_blocks(path.read_text(encoding="utf-8"))
    parts = ['<main class="chapter-text">']
    first = True
    for kind, text in blocks:
        if kind == "divider":
            parts.append('<div class="scene-break" aria-hidden="true">◆</div>')
            first = False
            continue
        cls = kind
        if first and kind == "narrative": cls += " first"
        parts.append(f'<p class="{cls}">{escape(text)}</p>')
        first = False
    parts.append('</main>')
    return "\n".join(parts)

CSS = '''
@page { margin: 6%; }
html, body { margin: 0; padding: 0; }
body { background: #FFFFFF; color: #171513; font-family: Georgia, "Times New Roman", serif; font-size: 1em; line-height: 1.52; }
p { margin: 0 0 0.48em 0; text-indent: 1.25em; text-align: justify; orphans: 2; widows: 2; }
p.dialogue { text-indent: 0; margin: 0 0 0.42em 0; }
p.display { text-indent: 0; text-align: center; letter-spacing: 0.08em; color: #5A1F27; margin: 1em 8%; }
.chapter-title-page { margin: 0; padding: 0; }
.chapter-opener { display: table; width: 100%; height: 92vh; min-height: 30em; text-align: center; }
.opener-inner { display: table-cell; width: 100%; vertical-align: middle; text-align: center; }
.chapter-opener h1 { font-family: Georgia, "Times New Roman", serif; font-size: 1.5em; font-weight: normal; letter-spacing: 0.14em; color: #5A1F27; margin: 0.5em 0; }
.chapter-opener h2 { font-family: Georgia, "Times New Roman", serif; font-size: 1em; font-weight: normal; font-style: italic; color: #49413B; margin: 0.55em 0 1em; }
.chapter-text { margin: 0; padding: 0; }
.ornament { color: #A77A35; font-size: 0.72em; }
.rule { width: 4.5em; height: 1px; background: #A77A35; margin: 1em auto 0; }
.scene-break { text-align: center; color: #A77A35; font-size: 0.65em; margin: 2em 0; }
.front { text-align: center; }
.front h1 { color: #5A1F27; font-size: 2.1em; font-weight: normal; letter-spacing: 0.08em; margin: 25vh 0 0.4em; }
.front .author { color: #A77A35; letter-spacing: 0.14em; text-indent: 0; text-align: center; }
.front-page { margin: 7vh auto 0; max-width: 32em; }
.front-page h1 { color: #5A1F27; font-weight: normal; text-align: center; letter-spacing: 0.06em; }
.front-page p { text-indent: 0; text-align: left; margin-bottom: 0.9em; }
.dedication p, .epigraph p { text-align: center; text-indent: 0; margin: 28vh 12% 0; }
.epigraph p { font-style: italic; }
.toc ul { list-style: none; margin: 1.4em 0 0; padding: 0; }
.toc li { margin: 0.36em 0; padding: 0; text-align: left; border-bottom: 1px solid #E7E1DA; }
.toc a { display: block; color: #241E1A; text-decoration: none; padding: 0.22em 0; }
.toc .num { display: inline-block; width: 5.8em; color: #5A1F27; font-size: 0.78em; letter-spacing: 0.06em; }
.toc .name { color: #241E1A; }
.note p { text-indent: 0; text-align: left; }
.cover { background: #FFFFFF; margin: 0; padding: 0; text-align: center; }
.cover img { display: block; width: 100%; height: auto; margin: 0 auto; }
'''.strip()

reset_stage()
(STAGE / "mimetype").write_text("application/epub+zip", encoding="ascii")
(META / "container.xml").write_text('''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''', encoding="utf-8")
(OEBPS / "styles.css").write_text(CSS, encoding="utf-8")
(OEBPS / "images" / "cover.jpg").write_bytes(COVER.read_bytes())

(OEBPS / "cover.xhtml").write_text(xhtml("Capa", '<img src="images/cover.jpg" alt="Capa de Um Lugar à Mesa, de Sabino Pereira"/>', "cover"), encoding="utf-8")
(OEBPS / "title.xhtml").write_text(xhtml("Folha de rosto", '<main class="front"><h1>UM LUGAR À MESA</h1><p class="author">SABINO PEREIRA</p></main>'), encoding="utf-8")

copyright_body = '''<main class="front-page"><h1>Direitos de autor</h1>
<p><em>Um Lugar à Mesa</em></p><p>Copyright © 2026 Sabino Pereira</p><p>Todos os direitos reservados.</p>
<p>Nenhuma parte desta publicação pode ser reproduzida, armazenada ou transmitida, por qualquer forma ou meio, eletrónico, mecânico, fotocópia, gravação ou outro, sem autorização prévia e escrita do autor, exceto no caso de breves citações utilizadas em críticas ou recensões.</p>
<p>Esta é uma obra de ficção. Nomes, personagens, organizações, acontecimentos e lugares são produto da imaginação do autor ou utilizados de forma fictícia. Qualquer semelhança com pessoas reais, vivas ou falecidas, ou com acontecimentos reais é mera coincidência.</p>
<p>Edição portuguesa premium<br/>Primeira edição digital, 2026</p></main>'''
(OEBPS / "copyright.xhtml").write_text(xhtml("Direitos de autor", copyright_body), encoding="utf-8")
(OEBPS / "dedication.xhtml").write_text(xhtml("Dedicatória", '<main class="dedication"><p>Para todos os que alguma vez confundiram um lugar à mesa com um lugar no mundo.</p></main>'), encoding="utf-8")
(OEBPS / "epigraph.xhtml").write_text(xhtml("Epígrafe", '<main class="epigraph"><p>Há pessoas que passam a vida inteira a conquistar um lugar sem perguntarem quem teve de se levantar.</p></main>'), encoding="utf-8")

toc_items = [f'<li><a href="chapter-{n:02d}.xhtml"><span class="num">CAPÍTULO {n}</span><span class="name">{escape(CHAPTER_TITLES[n-1])}</span></a></li>' for n in range(1, 13)]
toc_items.append('<li><a href="epilogue.xhtml"><span class="num">EPÍLOGO</span><span class="name">Quando Ninguém Está a Olhar</span></a></li>')
toc_body = '<main class="front-page toc"><h1>Índice</h1><ul>' + ''.join(toc_items) + '</ul></main>'
(OEBPS / "toc.xhtml").write_text(xhtml("Índice", toc_body), encoding="utf-8")

note = ['Todos acreditamos saber quem somos.', 'Até ao momento em que uma escolha nos obriga a descobrir quem estamos dispostos a sacrificar.', 'Esta história começa com um jantar.', 'À volta da mesa sentam-se pessoas habituadas ao poder, ao sucesso e ao controlo. Cada uma acredita conhecer a verdade sobre a própria vida. Cada uma transporta um segredo que preferia deixar enterrado.', 'Ao longo da noite, as cartas serão distribuídas.', 'Não para decidir quem vence.', 'Mas para revelar quem cada um sempre foi.', 'Bem-vindo a Um Lugar à Mesa.']
note_body = '<main class="front-page note"><h1>Nota ao leitor</h1>' + ''.join(f'<p>{escape(p)}</p>' for p in note) + '</main>'
(OEBPS / "note.xhtml").write_text(xhtml("Nota ao leitor", note_body), encoding="utf-8")

for n, path in enumerate(CHAPTERS, 1):
    (OEBPS / f"chapter-{n:02d}.xhtml").write_text(xhtml(f"Capítulo {n}", chapter_opener(n), "chapter-title-page"), encoding="utf-8")
    (OEBPS / f"chapter-{n:02d}-text.xhtml").write_text(xhtml(f"Capítulo {n} — texto", chapter_text(path)), encoding="utf-8")
(OEBPS / "epilogue.xhtml").write_text(xhtml("Epílogo", chapter_opener(None, epilogue=True), "chapter-title-page"), encoding="utf-8")
(OEBPS / "epilogue-text.xhtml").write_text(xhtml("Epílogo — texto", chapter_text(EPILOGUE)), encoding="utf-8")

nav_links = ''.join(f'<li><a href="chapter-{n:02d}.xhtml">Capítulo {n}: {escape(CHAPTER_TITLES[n-1])}</a></li>' for n in range(1, 13)) + '<li><a href="epilogue.xhtml">Epílogo: Quando Ninguém Está a Olhar</a></li>'
nav = f'''<nav epub:type="toc" id="toc" xmlns:epub="http://www.idpf.org/2007/ops"><h1>Índice</h1><ol><li><a href="note.xhtml">Nota ao leitor</a></li>{nav_links}</ol></nav>'''
(OEBPS / "nav.xhtml").write_text(xhtml("Navegação", nav), encoding="utf-8")

manifest = [
    '<item id="css" href="styles.css" media-type="text/css"/>',
    '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
    '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="copyright" href="copyright.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="dedication" href="dedication.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="epigraph" href="epigraph.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="tocpage" href="toc.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="note" href="note.xhtml" media-type="application/xhtml+xml"/>',
    '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
]
for n in range(1, 13):
    manifest.append(f'<item id="ch{n}" href="chapter-{n:02d}.xhtml" media-type="application/xhtml+xml"/>')
    manifest.append(f'<item id="ch{n}text" href="chapter-{n:02d}-text.xhtml" media-type="application/xhtml+xml"/>')
manifest.append('<item id="epilogue" href="epilogue.xhtml" media-type="application/xhtml+xml"/>')
manifest.append('<item id="epiloguetext" href="epilogue-text.xhtml" media-type="application/xhtml+xml"/>')
spine = ['cover', 'title', 'copyright', 'dedication', 'epigraph', 'tocpage', 'note']
for n in range(1, 13):
    spine.extend([f'ch{n}', f'ch{n}text'])
spine.extend(['epilogue', 'epiloguetext'])

opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="pt-PT">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{BOOK_ID}</dc:identifier><dc:title>Um Lugar à Mesa</dc:title><dc:creator>Sabino Pereira</dc:creator><dc:language>pt-PT</dc:language><dc:date>2026-07-22</dc:date><dc:publisher>Sabino Pereira</dc:publisher><dc:subject>Thriller psicológico</dc:subject><meta property="dcterms:modified">2026-07-22T20:00:00Z</meta></metadata>
<manifest>{''.join(manifest)}</manifest><spine>{''.join(f'<itemref idref="{x}"/>' for x in spine)}</spine></package>'''
(OEBPS / "content.opf").write_text(opf, encoding="utf-8")

OUT.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(OUT, "w") as z:
    z.write(STAGE / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
    for p in sorted(STAGE.rglob("*")):
        if p.is_file() and p.name != "mimetype":
            z.write(p, p.relative_to(STAGE).as_posix(), compress_type=zipfile.ZIP_DEFLATED)
print(OUT)
