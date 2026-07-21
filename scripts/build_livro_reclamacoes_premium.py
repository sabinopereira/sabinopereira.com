#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "books/livro-reclamacoes/premium/livro-reclamacoes-premium-manuscrito.md"
COVER = ROOT / "books/livro-reclamacoes/ebook/livro-reclamacoes-ebook-cover.jpg"
PREMIUM_DIR = ROOT / "books/livro-reclamacoes/premium"
PDF_OUT = ROOT / "output/pdf/livro-reclamacoes-premium/livro-de-reclamacoes-para-o-mundo-edicao-premium.pdf"
EPUB_OUT = PREMIUM_DIR / "livro-de-reclamacoes-para-o-mundo-edicao-premium.epub"
DOWNLOAD_PDF = ROOT / "downloads/livro-de-reclamacoes-para-o-mundo-edicao-premium.pdf"
DOWNLOAD_EPUB = ROOT / "downloads/livro-de-reclamacoes-para-o-mundo-edicao-premium.epub"

TITLE = "Livro de Reclamações para o Mundo"
SUBTITLE = "Crónicas do Absurdo"
EDITION = "Edição Digital Premium"
AUTHOR = "Sabino Pereira"
SITE = "https://sabinopereira.com"
AMAZON = "https://www.amazon.es/dp/B0GX2ZW3LQ"
CAMPAIGN_END = "30 de agosto de 2026"

PAGE_W = 6 * inch
PAGE_H = 9 * inch
INK = colors.HexColor("#171512")
RED = colors.HexColor("#A62C2B")
MUTED = colors.HexColor("#6F6760")
PAPER = colors.HexColor("#F6F0E7")
RULE = colors.HexColor("#D9C9B8")


@dataclass
class Complaint:
    number: int
    title: str
    subtitle: str
    paragraphs: list[str]


@dataclass
class Part:
    number: str
    title: str
    complaints: list[Complaint]


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    candidates = {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
        "Avenir": font_dir / "Avenir Next.ttc",
    }
    for name, path in candidates.items():
        if path.exists() and path.suffix.lower() == ".ttf":
            pdfmetrics.registerFont(TTFont(name, str(path)))


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("Linked In", "LinkedIn").replace("Only Fans", "OnlyFans")
    return text


def paragraphs_from(lines: list[str]) -> list[str]:
    # The editorial source uses one physical line per deliberate prose beat.
    # Preserve those beats instead of merging a whole complaint into one giant
    # paragraph; this also gives the PDF renderer safe page-break points.
    return [clean_text(line) for line in lines if line.strip() and line.strip() != "---"]


def proseify(lines: list[str]) -> list[str]:
    """Turn source beats into prose, retaining only clearly intentional verse runs."""
    if not lines:
        return []
    protected = [False] * len(lines)

    # Preserve short, non-sentential runs as verse. These are the deliberate
    # closing cadences; ordinary sentence-per-line source formatting becomes prose.
    index = 0
    while index < len(lines):
        if re.match(r"^[IVX]+\.\s+", lines[index]) or " – " in lines[index]:
            index += 1
            continue
        end = index
        while end < len(lines):
            line = lines[end]
            if re.match(r"^[IVX]+\.\s+", line) or " – " in line or len(line) > 78:
                break
            if line.endswith((".", "!", "?", "…”", ".”", '”')):
                break
            end += 1
        # Only a closing cadence may remain as verse. Earlier short runs are
        # usually source-layout fragments, examples, or lists and become prose.
        in_closing_cadence = index >= max(0, len(lines) - 11)
        if end - index >= 3 and in_closing_cadence:
            for pos in range(index, end):
                protected[pos] = True
        index = max(end, index + 1)

    output: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if buffer:
            output.append(clean_text(" ".join(buffer)))
            buffer = []

    for pos, line in enumerate(lines):
        special = (
            protected[pos]
            or re.match(r"^[IVX]+\.\s+", line)
            or " – " in line
            or line.startswith(("Estimado ", "Estimada ", "Caro ", "Cara "))
            or line.startswith(("Com os melhores", "Com consideração", "Com entusiasmo", "Com votos", "Com termos"))
        )
        if special:
            flush()
            output.append(line)
            continue
        projected = len(" ".join(buffer + [line]))
        if buffer and projected > 520:
            flush()
        buffer.append(line)
        if len(buffer) >= 4 or (len(buffer) >= 2 and line.endswith(("?", "!"))):
            flush()
    flush()
    return output


def parse_manuscript() -> tuple[list[str], list[Part], list[str]]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    preface: list[str] = []
    author_note: list[str] = []
    parts: list[Part] = []
    current_part: Part | None = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line == "# Prefácio":
            i += 1
            buf: list[str] = []
            while i < len(lines) and not lines[i].startswith("# Parte "):
                buf.append(lines[i])
                i += 1
            preface = paragraphs_from(buf)
            continue
        if line.startswith("# Parte "):
            match = re.match(r"# Parte ([IVX]+)\s*-\s*(.+)", line)
            if not match:
                raise SystemExit(f"Título de parte inválido: {line}")
            current_part = Part(match.group(1), match.group(2).strip(), [])
            parts.append(current_part)
            i += 1
            continue
        if line.startswith("## Reclamação n.º "):
            if current_part is None:
                raise SystemExit("Reclamação sem parte")
            number = int(re.search(r"(\d+)", line).group(1))
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            title = clean_text(lines[i])
            i += 1
            subtitle = ""
            if i < len(lines) and lines[i].strip().startswith("("):
                subtitle = clean_text(lines[i]).strip("()")
                i += 1
            buf = []
            while i < len(lines):
                marker = lines[i].strip()
                if marker.startswith("## Reclamação n.º ") or marker.startswith("# Parte ") or marker == "Nota do autor":
                    break
                buf.append(lines[i])
                i += 1
            current_part.complaints.append(Complaint(number, title, subtitle, proseify(paragraphs_from(buf))))
            continue
        if line == "Nota do autor":
            author_note = paragraphs_from(lines[i + 1 :])
            break
        i += 1

    complaints = [c for part in parts for c in part.complaints]
    if len(parts) != 5 or len(complaints) != 30:
        raise SystemExit(f"Esperadas 5 partes e 30 reclamações; encontradas {len(parts)} e {len(complaints)}")
    expected = list(range(1, 31))
    if [c.number for c in complaints] != expected:
        raise SystemExit("A numeração das reclamações não é contínua")
    return preface, parts, author_note


def esc(text: str) -> str:
    return html.escape(text).replace("—", "&mdash;").replace("…", "&hellip;")


def pdf_styles() -> dict[str, ParagraphStyle]:
    sheet = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitlePremium", parent=sheet["Title"], fontName="Times-Bold", fontSize=29, leading=34, alignment=TA_CENTER, textColor=INK, spaceAfter=12),
        "subtitle": ParagraphStyle("SubtitlePremium", fontName="Times-Italic", fontSize=13, leading=18, alignment=TA_CENTER, textColor=MUTED, spaceAfter=20),
        "edition": ParagraphStyle("EditionPremium", fontName="Times-Bold", fontSize=9.5, leading=13, alignment=TA_CENTER, textColor=RED, spaceAfter=24),
        "author": ParagraphStyle("AuthorPremium", fontName="Times-Bold", fontSize=12, leading=16, alignment=TA_CENTER, textColor=INK),
        "kicker": ParagraphStyle("KickerPremium", fontName="Times-Bold", fontSize=9, leading=12, textColor=RED, spaceAfter=8),
        "h1": ParagraphStyle("H1Premium", fontName="Times-Bold", fontSize=24, leading=29, textColor=INK, spaceAfter=18),
        "part": ParagraphStyle("PartPremium", fontName="Times-Bold", fontSize=27, leading=32, alignment=TA_CENTER, textColor=colors.white, spaceAfter=15),
        "part_label": ParagraphStyle("PartLabelPremium", fontName="Times-Bold", fontSize=10, leading=14, alignment=TA_CENTER, textColor=RED, spaceAfter=16),
        "chapter": ParagraphStyle("ChapterPremium", fontName="Times-Bold", fontSize=22, leading=27, textColor=INK, spaceAfter=9),
        "chapter_label": ParagraphStyle("ChapterLabelPremium", fontName="Times-Bold", fontSize=9, leading=12, textColor=RED, spaceAfter=10),
        "chapter_subtitle": ParagraphStyle("ChapterSubtitlePremium", fontName="Times-Italic", fontSize=11.5, leading=16, textColor=MUTED, spaceAfter=18),
        "subhead": ParagraphStyle("SubheadPremium", fontName="Times-Bold", fontSize=12.2, leading=16, textColor=INK, spaceBefore=12, spaceAfter=7, keepWithNext=True),
        "body": ParagraphStyle("BodyPremium", fontName="Times-Roman", fontSize=10.6, leading=16.2, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=9, allowWidows=0, allowOrphans=0),
        "letter": ParagraphStyle("LetterPremium", fontName="Times-Italic", fontSize=10.3, leading=15.8, leftIndent=15, rightIndent=10, textColor=INK, spaceAfter=9),
        "bullet": ParagraphStyle("BulletPremium", fontName="Times-Roman", fontSize=10.4, leading=15.5, leftIndent=18, firstLineIndent=-10, textColor=INK, spaceAfter=5),
        "toc": ParagraphStyle("TocPremium", fontName="Times-Roman", fontSize=10.4, leading=15, textColor=INK, spaceAfter=5),
        "small": ParagraphStyle("SmallPremium", fontName="Times-Roman", fontSize=8.5, leading=13, alignment=TA_CENTER, textColor=MUTED, spaceAfter=7),
        "note": ParagraphStyle("NotePremium", fontName="Times-Roman", fontSize=11, leading=17, textColor=INK, spaceAfter=11),
        "cta": ParagraphStyle("CtaPremium", fontName="Times-Bold", fontSize=11, leading=17, alignment=TA_CENTER, textColor=INK, spaceAfter=11),
    }


def draw_page(canv, doc) -> None:
    canv.saveState()
    canv.setFillColor(PAPER)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if doc.page > 4:
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(0.72 * inch, PAGE_H - 0.53 * inch, PAGE_W - 0.72 * inch, PAGE_H - 0.53 * inch)
        canv.setFont("Times-Roman", 7.8)
        canv.setFillColor(MUTED)
        canv.drawString(0.72 * inch, PAGE_H - 0.42 * inch, "LIVRO DE RECLAMAÇÕES PARA O MUNDO")
        canv.drawRightString(PAGE_W - 0.72 * inch, 0.42 * inch, str(doc.page - 1))
    canv.restoreState()


def draw_part_page(canv, doc) -> None:
    canv.saveState()
    canv.setFillColor(INK)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.setStrokeColor(RED)
    canv.setLineWidth(1.2)
    canv.line(1.6 * inch, 1.15 * inch, PAGE_W - 1.6 * inch, 1.15 * inch)
    canv.restoreState()


def append_body(story: list, text: str, s: dict[str, ParagraphStyle]) -> None:
    if re.match(r"^[IVX]+\.\s+", text):
        story.append(Paragraph(esc(text), s["subhead"]))
        return
    if " – " in text and (text.startswith("Por isso:") or text.startswith("Empreendedorismo onde:")):
        intro, *items = text.split(" – ")
        story.append(Paragraph(esc(intro), s["body"]))
        for item in items:
            story.append(Paragraph("- " + esc(item.strip()), s["bullet"]))
        return
    style = s["letter"] if text.startswith(("Estimado ", "Estimada ", "Caro ", "Cara ", "Com os melhores", "Com consideração", "Com entusiasmo", "Com votos")) else s["body"]
    story.append(Paragraph(esc(text), style))


def build_pdf(preface: list[str], parts: list[Part], author_note: list[str]) -> None:
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    s = pdf_styles()
    doc = BaseDocTemplate(str(PDF_OUT), pagesize=(PAGE_W, PAGE_H), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0, title=f"{TITLE} — {EDITION}", author=AUTHOR, subject=SUBTITLE)
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
    body_frame = Frame(0.72 * inch, 0.67 * inch, PAGE_W - 1.44 * inch, PAGE_H - 1.27 * inch, leftPadding=0, rightPadding=0, topPadding=0.12 * inch, bottomPadding=0.05 * inch, id="body")
    part_frame = Frame(0.78 * inch, 1.2 * inch, PAGE_W - 1.56 * inch, PAGE_H - 2.4 * inch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="part")
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame]),
        PageTemplate(id="Body", frames=[body_frame], onPage=draw_page),
        PageTemplate(id="Part", frames=[part_frame], onPage=draw_part_page),
    ])

    cover = PILImage.open(COVER)
    ratio = min(PAGE_W / cover.width, PAGE_H / cover.height)
    story: list = [Image(str(COVER), width=cover.width * ratio, height=cover.height * ratio), NextPageTemplate("Body"), PageBreak()]
    story.extend([
        Spacer(1, 1.35 * inch), Paragraph(TITLE, s["title"]), Paragraph(SUBTITLE, s["subtitle"]),
        Paragraph(EDITION.upper(), s["edition"]), Paragraph(AUTHOR.upper(), s["author"]), PageBreak(),
        Spacer(1, 1.12 * inch), Paragraph("UMA OFERTA DO AUTOR", s["kicker"]),
        Paragraph("Gratuito por tempo limitado", s["h1"]),
        Paragraph(f"Esta edição digital é oferecida gratuitamente até {CAMPAIGN_END}, como convite para conheceres a escrita e o universo criativo de Sabino Pereira.", s["note"]),
        Paragraph("Podes guardá-la e lê-la para uso pessoal. Não é permitida a revenda, reprodução comercial ou redistribuição do ficheiro.", s["note"]),
        Spacer(1, 0.18 * inch), Paragraph(f'<link href="{SITE}" color="#A62C2B">sabinopereira.com</link>', s["cta"]), PageBreak(),
        Spacer(1, 1.15 * inch), Paragraph("Copyright © 2026 Sabino Pereira", s["small"]),
        Paragraph("Todos os direitos reservados.", s["small"]),
        Paragraph("Edição Digital Premium — revista e oferecida pelo autor.", s["small"]),
        Paragraph("Uso pessoal apenas. Não autorizada para revenda ou redistribuição.", s["small"]),
        Spacer(1, 0.22 * inch), Paragraph(f'<link href="{SITE}" color="#A62C2B">{SITE}</link>', s["small"]), PageBreak(),
        Paragraph("ANTES DE RECLAMAR", s["kicker"]), Paragraph("Prefácio", s["h1"]),
    ])
    for p in preface:
        story.append(Paragraph(esc(p), s["note"]))
    story.extend([PageBreak(), Paragraph("ÍNDICE", s["kicker"]), Paragraph("Trinta reclamações. Cinco frentes.", s["h1"])])
    for part in parts:
        story.append(Paragraph(f"PARTE {part.number} · {esc(part.title)}", s["chapter_label"]))
        for complaint in part.complaints:
            story.append(Paragraph(f'<a href="#reclamacao-{complaint.number}">{complaint.number:02d} &nbsp; {esc(complaint.title)}</a>', s["toc"]))

    for part in parts:
        story.extend([NextPageTemplate("Part"), PageBreak(), Spacer(1, 1.35 * inch), Paragraph(f"PARTE {part.number}", s["part_label"]), Paragraph(esc(part.title), s["part"]), NextPageTemplate("Body")])
        for complaint in part.complaints:
            story.extend([PageBreak(), Paragraph(f'<a name="reclamacao-{complaint.number}"/>RECLAMAÇÃO N.º {complaint.number}', s["chapter_label"]), Paragraph(esc(complaint.title), s["chapter"])])
            if complaint.subtitle:
                story.append(Paragraph(esc(complaint.subtitle), s["chapter_subtitle"]))
            for p in complaint.paragraphs:
                append_body(story, p, s)

    story.extend([PageBreak(), Paragraph("DEPOIS DA ÚLTIMA RECLAMAÇÃO", s["kicker"]), Paragraph("Nota do autor", s["h1"])])
    for p in author_note:
        story.append(Paragraph(esc(p), s["note"]))
    story.extend([
        PageBreak(), Spacer(1, 0.95 * inch), Paragraph("CONTINUA A DESCOBRIR", s["kicker"]),
        Paragraph("Mais livros, ensaios e música", s["h1"]),
        Paragraph("Se este livro te fez reconhecer um pouco do absurdo à tua volta, visita o site do autor para descobrir os outros projetos — livros em português e inglês, ensaios e música publicada sob o nome Reira Bin.", s["note"]),
        Spacer(1, 0.16 * inch), Paragraph(f'<link href="{SITE}" color="#A62C2B">VISITAR SABINOPEREIRA.COM</link>', s["cta"]),
        Paragraph(f'<link href="{AMAZON}" color="#A62C2B">COMPRAR A EDIÇÃO IMPRESSA NA AMAZON</link>', s["cta"]),
        Spacer(1, 0.35 * inch), Paragraph("Obrigado por leres — e por continuares atento.", s["subtitle"]),
    ])
    doc.build(story)
    DOWNLOAD_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PDF_OUT, DOWNLOAD_PDF)


def xhtml(title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt"><head><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="styles.css"/></head><body>{body}</body></html>'''


def epub_paragraphs(paragraphs: list[str]) -> str:
    chunks: list[str] = []
    for p in paragraphs:
        if re.match(r"^[IVX]+\.\s+", p):
            chunks.append(f"<h3>{html.escape(p)}</h3>")
        elif " – " in p and (p.startswith("Por isso:") or p.startswith("Empreendedorismo onde:")):
            intro, *items = p.split(" – ")
            chunks.append(f"<p>{html.escape(intro)}</p><ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>")
        else:
            chunks.append(f"<p>{html.escape(p)}</p>")
    return "".join(chunks)


def build_epub(preface: list[str], parts: list[Part], author_note: list[str]) -> None:
    build = ROOT / "tmp/pdfs/livro-reclamacoes-premium/epub"
    if build.exists():
        shutil.rmtree(build)
    (build / "META-INF").mkdir(parents=True)
    (build / "OEBPS/images").mkdir(parents=True)
    (build / "mimetype").write_text("application/epub+zip", encoding="ascii")
    (build / "META-INF/container.xml").write_text('<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>', encoding="utf-8")
    shutil.copy2(COVER, build / "OEBPS/images/cover.jpg")
    css = '''@page{margin:5%}body{font-family:serif;line-height:1.55;color:#171512}h1,h2,h3{page-break-after:avoid}h1{font-size:2em}h2{font-size:1.55em}h3{font-size:1.05em;margin-top:1.4em}.center{text-align:center}.kicker{color:#a62c2b;font-weight:bold;letter-spacing:.08em}.part{page-break-before:always;text-align:center;margin-top:35%}.complaint{page-break-before:always}.subtitle{font-style:italic;color:#6f6760}.small{font-size:.85em;color:#6f6760}.cta{border-top:1px solid #d9c9b8;margin-top:2em;padding-top:1em}a{color:#a62c2b}li{margin-bottom:.35em}'''
    (build / "OEBPS/styles.css").write_text(css, encoding="utf-8")

    files: list[tuple[str, str, str]] = []
    title_body = f'<div class="center"><p class="kicker">{EDITION.upper()}</p><h1>{TITLE}</h1><p class="subtitle">{SUBTITLE}</p><p>{AUTHOR}</p></div>'
    files.append(("title.xhtml", "title", xhtml(TITLE, title_body)))
    offer = f'<p class="kicker">UMA OFERTA DO AUTOR</p><h1>Gratuito por tempo limitado</h1><p>Esta edição digital é oferecida gratuitamente até {CAMPAIGN_END}, como convite para conheceres a escrita e o universo criativo de Sabino Pereira.</p><p>Podes guardá-la e lê-la para uso pessoal. Não é permitida a revenda, reprodução comercial ou redistribuição do ficheiro.</p><p><a href="{SITE}">sabinopereira.com</a></p>'
    files.append(("offer.xhtml", "offer", xhtml("Oferta do autor", offer)))
    copyright_body = f'<div class="center small"><p>Copyright © 2026 Sabino Pereira</p><p>Todos os direitos reservados.</p><p>Edição Digital Premium — revista e oferecida pelo autor.</p><p>Uso pessoal apenas. Não autorizada para revenda ou redistribuição.</p></div>'
    files.append(("copyright.xhtml", "copyright", xhtml("Direitos de autor", copyright_body)))
    files.append(("preface.xhtml", "preface", xhtml("Prefácio", '<p class="kicker">ANTES DE RECLAMAR</p><h1>Prefácio</h1>' + epub_paragraphs(preface))))
    nav_items = ['<li><a href="preface.xhtml">Prefácio</a></li>']
    for part_index, part in enumerate(parts, 1):
        part_file = f"part-{part_index}.xhtml"
        files.append((part_file, f"part{part_index}", xhtml(f"Parte {part.number}", f'<div class="part"><p class="kicker">PARTE {part.number}</p><h1>{html.escape(part.title)}</h1></div>')))
        nav_items.append(f'<li><a href="{part_file}">Parte {part.number} — {html.escape(part.title)}</a><ol>')
        for complaint in part.complaints:
            filename = f"complaint-{complaint.number:02d}.xhtml"
            subtitle = f'<p class="subtitle">{html.escape(complaint.subtitle)}</p>' if complaint.subtitle else ""
            body = f'<article class="complaint"><p class="kicker">RECLAMAÇÃO N.º {complaint.number}</p><h1>{html.escape(complaint.title)}</h1>{subtitle}{epub_paragraphs(complaint.paragraphs)}</article>'
            files.append((filename, f"complaint{complaint.number}", xhtml(complaint.title, body)))
            nav_items.append(f'<li><a href="{filename}">{complaint.number}. {html.escape(complaint.title)}</a></li>')
        nav_items.append('</ol></li>')
    files.append(("author-note.xhtml", "authornote", xhtml("Nota do autor", '<p class="kicker">DEPOIS DA ÚLTIMA RECLAMAÇÃO</p><h1>Nota do autor</h1>' + epub_paragraphs(author_note))))
    files.append(("discover.xhtml", "discover", xhtml("Continua a descobrir", f'<p class="kicker">CONTINUA A DESCOBRIR</p><h1>Mais livros, ensaios e música</h1><p>Visita o site do autor para descobrires os outros projetos.</p><div class="cta"><p><a href="{SITE}">Visitar sabinopereira.com</a></p><p><a href="{AMAZON}">Comprar a edição impressa na Amazon</a></p></div>')))
    nav_items.extend(['<li><a href="author-note.xhtml">Nota do autor</a></li>', '<li><a href="discover.xhtml">Continua a descobrir</a></li>'])
    nav = xhtml("Índice", '<nav epub:type="toc" xmlns:epub="http://www.idpf.org/2007/ops"><h1>Índice</h1><ol>' + "".join(nav_items) + '</ol></nav>')
    (build / "OEBPS/nav.xhtml").write_text(nav, encoding="utf-8")
    for filename, _, content in files:
        (build / "OEBPS" / filename).write_text(content, encoding="utf-8")

    book_id = str(uuid.uuid4())
    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>', '<item id="css" href="styles.css" media-type="text/css"/>', '<item id="cover" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>']
    spine = []
    for filename, item_id, _ in files:
        manifest.append(f'<item id="{item_id}" href="{filename}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{item_id}"/>')
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">urn:uuid:{book_id}</dc:identifier><dc:title>{TITLE}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:language>pt</dc:language><dc:description>{SUBTITLE} — {EDITION}</dc:description><meta property="dcterms:modified">2026-07-20T00:00:00Z</meta></metadata><manifest>{''.join(manifest)}</manifest><spine>{''.join(spine)}</spine></package>'''
    (build / "OEBPS/content.opf").write_text(opf, encoding="utf-8")

    EPUB_OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(EPUB_OUT, "w") as zf:
        zf.write(build / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(build.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                zf.write(path, path.relative_to(build), compress_type=zipfile.ZIP_DEFLATED)
    shutil.copy2(EPUB_OUT, DOWNLOAD_EPUB)


def main() -> None:
    register_fonts()
    preface, parts, author_note = parse_manuscript()
    build_pdf(preface, parts, author_note)
    build_epub(preface, parts, author_note)
    print(PDF_OUT)
    print(EPUB_OUT)


if __name__ == "__main__":
    main()
