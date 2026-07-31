#!/usr/bin/env python3
"""Build the Portuguese Xadrez no Comando premium digital PDF."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageBreak, PageTemplate, Paragraph, Spacer
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/pdf/xadrez-no-comando/xadrez-no-comando.html"
COVER = ROOT / "books/xadrez-no-comando/ebook/xadrez-no-comando-ebook-cover.jpg"
OUTPUT_DIR = ROOT / "books/xadrez-no-comando/direct-sale/portuguese"
OUTPUT = OUTPUT_DIR / "xadrez-no-comando-premium-digital-edition.pdf"
PAGE_W, PAGE_H = 6 * inch, 9 * inch
INK = colors.HexColor("#171717")
RED = colors.HexColor("#9f1717")
GRAY = colors.HexColor("#66625d")
PAPER = colors.HexColor("#f8f5ef")


@dataclass
class Chapter:
    title: str
    paragraphs: list[tuple[str, bool]]


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def chapters() -> list[Chapter]:
    source = SOURCE.read_text(encoding="utf-8")
    result: list[Chapter] = []
    for section in re.findall(r'<section class="chapter">(.*?)</section>', source, re.S):
        heading = re.search(r"<h2>(.*?)</h2>", section, re.S)
        if not heading:
            continue
        body = section[heading.end() :]
        blocks: list[tuple[str, bool]] = []
        token_re = re.compile(r'<div class="quote">(.*?)</div>|<p>(.*?)</p>', re.S)
        for token in token_re.finditer(body):
            quote, para = token.groups()
            if quote is not None:
                text = " ".join(clean(p) for p in re.findall(r"<p>(.*?)</p>", quote, re.S) if clean(p))
                if text:
                    blocks.append((text, True))
            else:
                text = clean(para)
                if text:
                    blocks.append((text, False))
        result.append(Chapter(clean(heading.group(1)), blocks))
    return result


def register_fonts() -> None:
    folder = Path("/System/Library/Fonts/Supplemental")
    for name, filename in {
        "Helvetica": "Georgia.ttf",
        "Georgia": "Georgia.ttf",
        "Georgia-Bold": "Georgia Bold.ttf",
        "Georgia-Italic": "Georgia Italic.ttf",
        "Impact": "Impact.ttf",
        "ArialUnicode": "Arial Unicode.ttf",
    }.items():
        pdfmetrics.registerFont(TTFont(name, str(folder / filename)))


class EmbeddedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("initialFontName", "Georgia")
        super().__init__(*args, **kwargs)


class CoverPage(Flowable):
    def __init__(self, image_path: Path):
        super().__init__()
        self.image_path = image_path
        self.width, self.height = PAGE_W, PAGE_H

    def wrap(self, available_width, available_height):
        return PAGE_W, PAGE_H

    def draw(self):
        self.canv.setFillColor(colors.black)
        self.canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        with Image.open(self.image_path) as image:
            ratio = image.width / image.height
        width = PAGE_H * ratio
        self.canv.drawImage(str(self.image_path), (PAGE_W - width) / 2, 0, width=width, height=PAGE_H, preserveAspectRatio=True, mask="auto")


def background(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    canv.saveState()
    canv.setFillColor(PAPER)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if doc.page > 4:
        canv.setStrokeColor(colors.HexColor("#c9c0b5"))
        canv.setLineWidth(0.45)
        canv.line(0.68 * inch, PAGE_H - 0.48 * inch, PAGE_W - 0.68 * inch, PAGE_H - 0.48 * inch)
        canv.setFont("Georgia", 7.4)
        canv.setFillColor(GRAY)
        canv.drawString(0.68 * inch, 0.4 * inch, "Xadrez no Comando")
        canv.drawRightString(PAGE_W - 0.68 * inch, 0.4 * inch, str(doc.page))
    canv.restoreState()


def blank(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    canv.saveState()
    canv.setFillColor(colors.black)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canv.restoreState()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("PremiumTitle", parent=base["Title"], fontName="Impact", fontSize=38, leading=39, alignment=TA_CENTER, textColor=INK, spaceAfter=16),
        "subtitle": ParagraphStyle("PremiumSubtitle", parent=base["Normal"], fontName="Georgia-Italic", fontSize=12.5, leading=18, alignment=TA_CENTER, textColor=GRAY),
        "author": ParagraphStyle("PremiumAuthor", parent=base["Normal"], fontName="Georgia-Bold", fontSize=11, alignment=TA_CENTER, textColor=INK, spaceBefore=28),
        "chapter": ParagraphStyle("PremiumChapter", parent=base["Heading1"], fontName="Impact", fontSize=25, leading=28, alignment=TA_LEFT, textColor=INK, spaceAfter=18),
        "body": ParagraphStyle("PremiumBody", parent=base["Normal"], fontName="Georgia", fontSize=11.1, leading=17.2, alignment=TA_LEFT, textColor=INK, spaceAfter=8.2),
        "quote": ParagraphStyle("PremiumQuote", parent=base["Normal"], fontName="Georgia-Italic", fontSize=11, leading=17, leftIndent=20, rightIndent=14, textColor=colors.HexColor("#34302d"), spaceBefore=5, spaceAfter=11),
        "toc": ParagraphStyle("PremiumToc", parent=base["Normal"], fontName="Georgia", fontSize=11.5, leading=20, textColor=INK),
        "small": ParagraphStyle("PremiumSmall", parent=base["Normal"], fontName="Georgia", fontSize=8.8, leading=13.5, textColor=GRAY, spaceAfter=9),
        "end": ParagraphStyle("PremiumEnd", parent=base["Normal"], fontName="Georgia-Italic", fontSize=12, leading=18, alignment=TA_CENTER, textColor=GRAY),
    }


def build() -> None:
    register_fonts()
    book = chapters()
    if len(book) != 9:
        raise SystemExit(f"Esperados 9 capítulos; encontrados {len(book)}")
    if 'class="stanza"' in SOURCE.read_text(encoding="utf-8"):
        raise SystemExit("A fonte ainda contém blocos stanza; interrompido para evitar falsos versos.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    st = styles()
    doc = BaseDocTemplate(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0, title="Xadrez no Comando - Edição Digital Premium", author="Sabino Pereira", subject="Edição digital premium em português")
    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, 0, 0, 0, 0, id="cover")
    body_frame = Frame(0.68 * inch, 0.62 * inch, PAGE_W - 1.36 * inch, PAGE_H - 1.18 * inch, 0, 0, 0.2 * inch, 0.12 * inch, id="body")
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=blank, autoNextPageTemplate="Body"),
        PageTemplate(id="Body", frames=[body_frame], onPage=background),
    ])
    story = [CoverPage(COVER), PageBreak(), Spacer(1, 1.45 * inch), Paragraph("XADREZ<br/>NO COMANDO", st["title"]), Paragraph("Cada peça tem uma dor. Cada movimento tem um preço.", st["subtitle"]), Paragraph("Sabino Pereira", st["author"]), PageBreak(), Spacer(1, 0.7 * inch), Paragraph("Copyright", st["chapter"]), Paragraph("Copyright © 2026 Sabino Pereira. Todos os direitos reservados.", st["small"]), Paragraph("Nenhuma parte desta publicação pode ser reproduzida, armazenada, distribuída ou transmitida sem autorização prévia do autor, exceto em breves citações usadas em crítica ou divulgação.", st["small"]), Paragraph("Edição digital Premium em português, 2026.", st["small"]), PageBreak(), Paragraph("Índice", st["chapter"])]
    for chapter in book:
        story.append(Paragraph(html.escape(chapter.title), st["toc"]))
    story.append(PageBreak())
    for chapter in book:
        story.extend([Spacer(1, 0.38 * inch), Paragraph(html.escape(chapter.title), st["chapter"])])
        for text, quote in chapter.paragraphs:
            story.append(Paragraph(html.escape(text), st["quote"] if quote else st["body"]))
        story.append(PageBreak())
    story.extend([Spacer(1, 2.55 * inch), Paragraph("O jogo continua.", st["end"]), Spacer(1, 0.2 * inch), Paragraph("sabinopereira.com", st["end"])])
    doc.build(story, canvasmaker=EmbeddedCanvas)
    (OUTPUT_DIR / "README.txt").write_text(
        "XADREZ NO COMANDO - EDIÇÃO DIGITAL PREMIUM\n\n"
        f"Produto para Fourthwall: {OUTPUT.name}\n"
        "Idioma: Português (Portugal)\n"
        "Formato: PDF digital 6 x 9 in, capa incluída\n"
        "Conteúdo: prosa limpa; sem falsos versos\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    build()
