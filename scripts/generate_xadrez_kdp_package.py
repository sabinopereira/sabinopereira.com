#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = ROOT / "output/pdf/xadrez-no-comando/xadrez-no-comando.html"
COVER_IMAGE = ROOT / "output/pdf/xadrez-no-comando/assets/cover.png"
OUT_DIR = ROOT / "books/xadrez-no-comando"
PAPERBACK_DIR = OUT_DIR / "paperback"
EBOOK_DIR = OUT_DIR / "ebook"
PREVIEWS_DIR = OUT_DIR / "previews"

TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch


@dataclass
class Block:
    kind: str
    text: str


@dataclass
class Chapter:
    title: str
    blocks: list[Block]


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    fonts = {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
        "Georgia-BoldItalic": font_dir / "Georgia Bold Italic.ttf",
        "Impact": font_dir / "Impact.ttf",
        "ArialUnicode": font_dir / "Arial Unicode.ttf",
    }
    for name, path in fonts.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_chapters(source: str) -> list[Chapter]:
    chapters: list[Chapter] = []
    sections = re.findall(r'<section class="chapter">(.*?)</section>', source, re.S)
    for section in sections:
        title_match = re.search(r"<h2>(.*?)</h2>", section, re.S)
        if not title_match:
            continue
        title = clean_text(title_match.group(1))
        content = section[title_match.end() :]
        blocks: list[Block] = []
        pos = 0
        block_re = re.compile(r'<div class="(stanza|quote)">(.*?)</div>', re.S)
        for match in block_re.finditer(content):
            for p in re.findall(r"<p>(.*?)</p>", content[pos : match.start()], re.S):
                text = clean_text(p)
                if text:
                    blocks.append(Block("body", text))
            kind = match.group(1)
            stanza_texts = [clean_text(p) for p in re.findall(r"<p>(.*?)</p>", match.group(2), re.S)]
            stanza_texts = [text for text in stanza_texts if text]
            if stanza_texts:
                blocks.append(Block(kind, "<br/>".join(stanza_texts)))
            pos = match.end()
        for p in re.findall(r"<p>(.*?)</p>", content[pos:], re.S):
            text = clean_text(p)
            if text:
                blocks.append(Block("body", text))
        chapters.append(Chapter(title, blocks))
    return chapters


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    escaped = html.escape(text).replace("&lt;br/&gt;", "<br/>")
    return Paragraph(escaped, style)


def draw_page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    # Keep front matter quiet; KDP still counts these pages in the PDF.
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFont("Georgia", 9)
    canv.setFillColor(colors.HexColor("#555555"))
    canv.drawCentredString(TRIM_W / 2, 0.42 * inch, str(doc.page))
    canv.restoreState()


def piece_story(title: str, subtitle: str, symbol: str, styles: dict[str, ParagraphStyle]) -> list:
    return [
        Spacer(1, 1.2 * inch),
        KeepTogether(
            [
                Spacer(1, 0.45 * inch),
                paragraph(symbol, styles["PieceSymbol"]),
                Spacer(1, 0.18 * inch),
                paragraph(title, styles["PieceTitle"]),
                Spacer(1, 0.05 * inch),
                paragraph(subtitle, styles["PieceSub"]),
                Spacer(1, 0.45 * inch),
            ]
        ),
        PageBreak(),
    ]


def build_interior(chapters: list[Chapter], output_pdf: Path) -> int:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "TitleImpact",
            fontName="Impact",
            fontSize=39,
            leading=40,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            "Subtitle",
            fontName="Georgia-Italic",
            fontSize=13,
            leading=19,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Author",
            fontName="Georgia",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceBefore=34,
        )
    )
    styles.add(
        ParagraphStyle(
            "ChapterTitle",
            fontName="Impact",
            fontSize=26,
            leading=27,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#111111"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodyBook",
            fontName="Georgia",
            fontSize=11.4,
            leading=17.2,
            firstLineIndent=0,
            spaceAfter=7.5,
            textColor=colors.HexColor("#151515"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Stanza",
            fontName="Georgia",
            fontSize=11.2,
            leading=17,
            leftIndent=16,
            spaceBefore=5,
            spaceAfter=9,
            textColor=colors.HexColor("#151515"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Quote",
            fontName="Georgia-Italic",
            fontSize=11.2,
            leading=17,
            leftIndent=24,
            rightIndent=18,
            spaceBefore=7,
            spaceAfter=11,
            textColor=colors.HexColor("#222222"),
        )
    )
    styles.add(
        ParagraphStyle(
            "Toc",
            fontName="Georgia",
            fontSize=12,
            leading=22,
            textColor=colors.HexColor("#151515"),
        )
    )
    styles.add(
        ParagraphStyle(
            "PieceSymbol",
            fontName="ArialUnicode",
            fontSize=92,
            leading=96,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
        )
    )
    styles.add(
        ParagraphStyle(
            "PieceTitle",
            fontName="Impact",
            fontSize=25,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
        )
    )
    styles.add(
        ParagraphStyle(
            "PieceSub",
            fontName="Georgia-Italic",
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
        )
    )

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output_pdf),
        pagesize=(TRIM_W, TRIM_H),
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
        title="Xadrez no Comando - Paperback Interior",
        author="Sabino Pereira",
    )
    odd = Frame(0.62 * inch, 0.72 * inch, TRIM_W - 1.14 * inch, TRIM_H - 1.42 * inch, id="odd")
    even = Frame(0.52 * inch, 0.72 * inch, TRIM_W - 1.14 * inch, TRIM_H - 1.42 * inch, id="even")
    doc.addPageTemplates(
        [
            PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
            PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
        ]
    )

    story: list = [NextPageTemplate("Even")]
    story.extend(
        [
            Spacer(1, 2.05 * inch),
            paragraph("XADREZ<br/>NO COMANDO", styles["TitleImpact"]),
            Spacer(1, 0.18 * inch),
            paragraph("Cada peça tem uma dor. Cada movimento tem um preço.", styles["Subtitle"]),
            paragraph("Sabino Pereira", styles["Author"]),
            PageBreak(),
            Spacer(1, 2.0 * inch),
            paragraph("Xadrez no Comando", styles["Subtitle"]),
            Spacer(1, 0.25 * inch),
            paragraph("Copyright © 2026 Sabino Pereira. Todos os direitos reservados.", styles["Toc"]),
            paragraph("Nenhuma parte deste livro pode ser reproduzida sem autorização do autor, exceto em breves citações para crítica ou divulgação.", styles["Toc"]),
            Spacer(1, 0.3 * inch),
            paragraph("Primeira edição paperback.", styles["Toc"]),
            PageBreak(),
            paragraph("Índice", styles["ChapterTitle"]),
        ]
    )
    for chapter in chapters:
        story.append(paragraph(chapter.title, styles["Toc"]))
    story.append(PageBreak())

    piece_meta = {
        "Abertura - O Tabuleiro": ("Abertura", "O tabuleiro", "□"),
        "O Peão": ("O Peão", "Um passo de cada vez", "♙"),
        "O Cavalo": ("O Cavalo", "Os caminhos tortos", "♞"),
        "O Bispo": ("O Bispo", "Olhar na diagonal", "♝"),
        "A Torre": ("A Torre", "A força que fica de pé", "♜"),
        "A Rainha": ("A Rainha", "O poder que protege", "♛"),
        "O Rei": ("O Rei", "O medo de perder tudo", "♚"),
        "Xeque-Mate": ("Xeque-Mate", "Quando já não há fuga", "×"),
        "Fim de Jogo": ("Fim de Jogo", "O que sobra depois", "○"),
    }
    for chapter in chapters:
        if chapter.title in piece_meta:
            story.extend(piece_story(*piece_meta[chapter.title], styles))
        story.extend([paragraph(chapter.title, styles["ChapterTitle"]), Spacer(1, 4)])
        for block in chapter.blocks:
            if block.kind == "quote":
                story.append(paragraph(block.text, styles["Quote"]))
            elif block.kind == "stanza":
                story.append(paragraph(block.text, styles["Stanza"]))
            else:
                story.append(paragraph(block.text, styles["BodyBook"]))
        story.append(PageBreak())

    story.extend(
        [
            Spacer(1, 3.25 * inch),
            paragraph("Xadrez no Comando", styles["Subtitle"]),
        ]
    )
    doc.build(story)

    reader = PdfReader(str(output_pdf))
    page_count = len(reader.pages)
    if page_count % 2:
        blank = canvas.Canvas(str(output_pdf.with_suffix(".blank.pdf")), pagesize=(TRIM_W, TRIM_H))
        blank.showPage()
        blank.save()
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_page(PdfReader(str(output_pdf.with_suffix(".blank.pdf"))).pages[0])
        with output_pdf.open("wb") as handle:
            writer.write(handle)
        output_pdf.with_suffix(".blank.pdf").unlink()
        page_count += 1
    return page_count


def strip_unused_font_resources(pdf_path: Path) -> None:
    return
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    for page in reader.pages:
        resources = page.get("/Resources")
        fonts = resources.get("/Font") if resources else None
        if fonts:
            fonts = fonts.get_object()
            content = page.get_contents()
            if isinstance(content, list):
                data = b"\n".join(part.get_data() for part in content)
            elif content:
                data = content.get_data()
            else:
                data = b""
            for name in list(fonts.keys()):
                if name.encode("latin-1") not in data:
                    del fonts[name]
        writer.add_page(page)
    tmp = pdf_path.with_suffix(".clean.pdf")
    with tmp.open("wb") as handle:
        writer.write(handle)
    tmp.replace(pdf_path)


def fit_image_size(img_w: float, img_h: float, box_w: float, box_h: float) -> tuple[float, float]:
    scale = min(box_w / img_w, box_h / img_h)
    return img_w * scale, img_h * scale


def draw_wrapped_text(
    canv: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font: str,
    size: float,
    leading: float,
    color=colors.black,
) -> float:
    canv.setFillColor(color)
    canv.setFont(font, size)
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if canv.stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    for line in lines:
        canv.drawString(x, y, line)
        y -= leading
    return y


def fit_font_to_width(font_path: str, text: str, max_width: int, start_size: int, min_size: int = 24) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        left, _, right, _ = ImageDraw.Draw(Image.new("RGB", (10, 10))).textbbox((0, 0), text, font=font)
        if right - left <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, min_size)


def create_front_cover_art(output_path: Path, width_px: int, height_px: int) -> None:
    impact = "/System/Library/Fonts/Supplemental/Impact.ttf"
    georgia = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    georgia_bold = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
    georgia_italic = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"

    source = Image.open(COVER_IMAGE).convert("RGB")
    crop_h = source.height
    crop_w = round(source.width * 0.56)
    # Keep the fallen king and cracked ground, while hiding most embedded square-cover typography.
    crop_x = 0
    crop_y = 0
    crop = source.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
    cover = crop.resize((width_px, height_px), Image.Resampling.LANCZOS).convert("RGBA")

    # Strong paperback mood: darker top for title, darker bottom for author/tagline.
    overlay = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(height_px):
        top_alpha = max(0, int(230 * (1 - y / (height_px * 0.42))))
        bottom_alpha = max(0, int(210 * ((y - height_px * 0.52) / (height_px * 0.48))))
        alpha = min(245, max(top_alpha, bottom_alpha))
        if alpha:
            od.line([(0, y), (width_px, y)], fill=(0, 0, 0, alpha))
    # Left/right vignette gives the title and subtitle quieter breathing room.
    for x in range(width_px):
        edge = min(x / (width_px * 0.23), (width_px - x) / (width_px * 0.23), 1)
        alpha = int(105 * (1 - edge))
        if alpha:
            od.line([(x, 0), (x, height_px)], fill=(0, 0, 0, alpha))
    cover = Image.alpha_composite(cover, overlay)

    draw = ImageDraw.Draw(cover)
    margin = round(width_px * 0.09)
    cream = (238, 236, 224, 255)
    muted = (196, 193, 180, 255)
    white = (255, 255, 255, 255)
    red = (166, 19, 18, 255)

    title_font = fit_font_to_width(impact, "NO COMANDO", width_px - 2 * margin, round(width_px * 0.21), 54)
    title_font_big = fit_font_to_width(impact, "XADREZ", width_px - 2 * margin, round(width_px * 0.24), 62)
    subtitle_font = ImageFont.truetype(georgia_italic, round(width_px * 0.052))
    author_font = ImageFont.truetype(georgia_bold, round(width_px * 0.055))
    kicker_font = ImageFont.truetype(georgia, round(width_px * 0.025))

    draw.rectangle([0, 0, width_px, round(height_px * 0.43)], fill=(0, 0, 0, 155))
    y = round(height_px * 0.075)
    draw.text((margin, y), "XADREZ", font=title_font_big, fill=white)
    y += round(title_font_big.size * 0.88)
    draw.text((margin, y), "NO COMANDO", font=title_font, fill=white)
    y += round(title_font.size * 1.03)
    draw.rectangle([margin, y, margin + round(width_px * 0.28), y + 5], fill=red)
    draw.rectangle([margin + round(width_px * 0.30), y, margin + round(width_px * 0.48), y + 5], fill=cream)

    bottom_y = round(height_px * 0.765)
    draw.rectangle(
        [margin, bottom_y - round(height_px * 0.025), width_px - margin, bottom_y + round(height_px * 0.155)],
        fill=(0, 0, 0, 142),
    )
    line1 = "Cada peça tem uma dor."
    line2 = "Cada movimento tem um preço."
    draw.text((margin + 22, bottom_y), line1, font=subtitle_font, fill=cream)
    draw.text((margin + 22, bottom_y + round(subtitle_font.size * 1.28)), line2, font=subtitle_font, fill=cream)

    draw.text((margin, height_px - round(height_px * 0.108)), "SABINO PEREIRA", font=author_font, fill=white)
    draw.text((margin, height_px - round(height_px * 0.057)), "UM LIVRO SOBRE ESTRATÉGIA, PERDA E MATURIDADE", font=kicker_font, fill=muted)

    # Print-safe inner frame, far enough from the trim not to be chopped by KDP.
    inset = round(width_px * 0.036)
    draw.rectangle([inset, inset, width_px - inset, height_px - inset], outline=(238, 236, 224, 165), width=max(2, round(width_px * 0.004)))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cover.convert("RGB").save(output_path, quality=96)


def build_cover(page_count: int, output_pdf: Path, preview_png: Path) -> dict[str, float]:
    spine = page_count * WHITE_PAPER_SPINE_PER_PAGE
    cover_w = BLEED + TRIM_W + spine + TRIM_W + BLEED
    cover_h = TRIM_H + 2 * BLEED
    back_x = BLEED
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_pdf), pagesize=(cover_w, cover_h))
    c.setTitle("Xadrez no Comando - Paperback Cover")
    c.setAuthor("Sabino Pereira")
    c.setFillColor(colors.black)
    c.rect(0, 0, cover_w, cover_h, stroke=0, fill=1)

    # Front cover: full-bleed paperback artwork generated from the original square art.
    front_box_w = TRIM_W + BLEED
    front_box_h = cover_h
    front_art = preview_png.parent / "tmp-xadrez-no-comando-front-art.png"
    create_front_cover_art(front_art, round((front_box_w / inch) * 300), round((front_box_h / inch) * 300))
    c.drawImage(
        str(front_art),
        front_x,
        0,
        width=front_box_w,
        height=front_box_h,
        preserveAspectRatio=False,
        mask="auto",
    )

    # Back cover.
    safe_x = back_x + 0.42 * inch
    y = cover_h - 0.82 * inch
    c.setFont("Impact", 26)
    c.setFillColor(colors.white)
    c.drawString(safe_x, y, "XADREZ NO COMANDO")
    y -= 0.35 * inch
    c.setStrokeColor(colors.white)
    c.setLineWidth(1.2)
    c.line(safe_x, y, safe_x + 1.25 * inch, y)
    y -= 0.36 * inch
    blurb = (
        "No tabuleiro comum, todas as peças têm lugar marcado. Na vida real, nem todos começam do mesmo lado da sorte. "
        "Xadrez no Comando usa o xadrez para falar de sobrevivência emocional, pressão, silêncio, amor, perda e maturidade."
    )
    y = draw_wrapped_text(c, blurb, safe_x, y, TRIM_W - 0.9 * inch, "Georgia", 12.2, 18, colors.HexColor("#eeeeee"))
    y -= 0.22 * inch
    quote = "Cada peça tem uma dor. Cada movimento tem um preço."
    y = draw_wrapped_text(c, quote, safe_x, y, TRIM_W - 1.05 * inch, "Georgia-Italic", 13, 20, colors.white)
    y -= 0.26 * inch
    c.setFont("Georgia", 10)
    c.setFillColor(colors.HexColor("#cfcfcf"))
    c.drawString(safe_x, y, "Sabino Pereira")

    # Leave a clean barcode area. KDP can place its barcode here automatically.
    barcode_w = 2.0 * inch
    barcode_h = 1.2 * inch
    c.setFillColor(colors.white)
    c.rect(back_x + TRIM_W - barcode_w - 0.35 * inch, 0.42 * inch, barcode_w, barcode_h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Georgia", 6.5)
    c.drawCentredString(back_x + TRIM_W - barcode_w / 2 - 0.35 * inch, 0.96 * inch, "Barcode KDP")

    # Spine text only because the generated book has more than 79 pages.
    if page_count > 79:
        c.saveState()
        c.translate(spine_x + spine / 2, cover_h / 2)
        c.rotate(90)
        c.setFont("Impact", max(6, min(11, spine * 0.42)))
        c.setFillColor(colors.white)
        c.drawCentredString(0, -spine * 0.18, "XADREZ NO COMANDO")
        c.setFont("Georgia", max(4.5, min(7.2, spine * 0.26)))
        c.drawCentredString(0, spine * 0.26, "SABINO PEREIRA")
        c.restoreState()

    c.showPage()
    c.save()
    front_art.unlink(missing_ok=True)

    make_cover_preview(preview_png, cover_w, cover_h, spine, page_count)
    return {
        "page_count": page_count,
        "trim_width_in": TRIM_W / inch,
        "trim_height_in": TRIM_H / inch,
        "bleed_in": BLEED / inch,
        "spine_width_in": spine / inch,
        "cover_width_in": cover_w / inch,
        "cover_height_in": cover_h / inch,
    }


def make_cover_preview(preview_png: Path, cover_w_pt: float, cover_h_pt: float, spine_pt: float, page_count: int) -> None:
    scale = 110
    w = round(cover_w_pt / inch * scale)
    h = round(cover_h_pt / inch * scale)
    im = Image.new("RGB", (w, h), "black")
    draw = ImageDraw.Draw(im)
    bleed_px = round((BLEED / inch) * scale)
    trim_w_px = round((TRIM_W / inch) * scale)
    spine_px = max(1, round((spine_pt / inch) * scale))
    spine_x = bleed_px + trim_w_px
    front_x = spine_x + spine_px
    cover_h_px = h
    front_box_w = trim_w_px + bleed_px
    preview_front = preview_png.with_name("tmp-xadrez-no-comando-front-preview-art.png")
    create_front_cover_art(preview_front, front_box_w, cover_h_px)
    front_art = Image.open(preview_front).convert("RGB")
    im.paste(front_art, (front_x, 0))
    preview_front.unlink(missing_ok=True)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 34)
        body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 17)
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 12)
    except OSError:
        title_font = body_font = small_font = ImageFont.load_default()
    x = bleed_px + round(0.42 * scale)
    y = round(0.72 * scale)
    draw.text((x, y), "XADREZ NO COMANDO", fill="white", font=title_font)
    y += round(0.7 * scale)
    back_lines = [
        "No tabuleiro comum, todas as peças têm",
        "lugar marcado. Na vida real, nem todos",
        "começam do mesmo lado da sorte.",
        "",
        "Cada peça tem uma dor.",
        "Cada movimento tem um preço.",
    ]
    for line in back_lines:
        draw.text((x, y), line, fill=(232, 232, 232), font=body_font)
        y += round(0.26 * scale)
    draw.rectangle(
        [
            bleed_px + trim_w_px - round(2.35 * scale),
            h - round(1.65 * scale),
            bleed_px + trim_w_px - round(0.35 * scale),
            h - round(0.45 * scale),
        ],
        fill="white",
    )
    if page_count > 79:
        draw.rectangle([spine_x, 0, spine_x + spine_px, h], fill=(16, 16, 16))
    draw.rectangle([bleed_px, bleed_px, w - bleed_px, h - bleed_px], outline=(180, 180, 180), width=2)
    preview_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(preview_png)


def write_metadata(specs: dict[str, float], output_path: Path) -> None:
    metadata = {
        "title": "Xadrez no Comando",
        "author": "Sabino Pereira",
        "language": "Portuguese",
        "format": "Paperback",
        "kdp_setup": {
            "trim_size": "6 x 9 in",
            "interior": "Black & white",
            "paper": "White paper",
            "bleed": "No bleed for interior",
            "cover_finish": "Matte recommended",
            "reading_direction": "Left to Right",
        },
        "files": {
            "paperback_interior_pdf": "paperback/xadrez-no-comando-paperback-miolo-kdp.pdf",
            "paperback_cover_pdf": "paperback/xadrez-no-comando-paperback-capa-kdp.pdf",
            "ebook_epub": "ebook/xadrez-no-comando-kindle-ebook.epub",
            "ebook_cover_jpg": "ebook/xadrez-no-comando-ebook-cover.jpg",
            "cover_preview_png": "previews/xadrez-no-comando-paperback-spread-preview.png",
        },
        "description_pt": (
            "Xadrez no Comando é um livro em português sobre estratégia, sobrevivência emocional, pressão, silêncio, amor, perda e maturidade. "
            "Cada peça representa uma fase humana: o peão, o cavalo, o bispo, a torre, a rainha, o rei, o xeque-mate e o fim de jogo."
        ),
        "keywords_suggested": [
            "xadrez",
            "estratégia",
            "maturidade emocional",
            "sobrevivência emocional",
            "reflexões",
            "literatura portuguesa",
            "crescimento pessoal",
        ],
        "categories_suggested": [
            "Literary Collections / Essays",
            "Self-Help / Personal Growth / General",
            "Biography & Autobiography / Personal Memoirs",
        ],
        "print_specs": specs,
    }
    output_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_readme(specs: dict[str, float], output_path: Path) -> None:
    output_path.write_text(
        f"""# Xadrez no Comando - Amazon KDP package

Files prepared for Amazon KDP paperback and Kindle/eBook upload.

## Upload files

- Paperback interior/manuscript: `paperback/xadrez-no-comando-paperback-miolo-kdp.pdf`
- Paperback cover: `paperback/xadrez-no-comando-paperback-capa-kdp.pdf`
- Kindle/eBook manuscript: `ebook/xadrez-no-comando-kindle-ebook.epub`
- Kindle/eBook cover: `ebook/xadrez-no-comando-ebook-cover.jpg`
- Visual previews: `previews/`
- Metadata helper: `kdp-metadata.json`

For paperback, upload the two PDF files. For Kindle/eBook, upload the EPUB manuscript and JPG cover. PNG files are previews/checks only.

## KDP setup

- Format: Paperback
- Trim size: 6 x 9 in
- Interior: Black & white
- Paper: White paper
- Interior bleed: No bleed
- Cover bleed: 0.125 in
- Cover finish: Matte recommended
- Reading direction: Left to Right

## Generated dimensions

- Interior page count: {int(specs["page_count"])}
- Spine width: {specs["spine_width_in"]:.4f} in
- Full cover width: {specs["cover_width_in"]:.4f} in
- Full cover height: {specs["cover_height_in"]:.4f} in

## Before publishing

1. Paperback: upload `paperback/xadrez-no-comando-paperback-miolo-kdp.pdf` and `paperback/xadrez-no-comando-paperback-capa-kdp.pdf`.
2. Kindle/eBook: upload `ebook/xadrez-no-comando-kindle-ebook.epub` and `ebook/xadrez-no-comando-ebook-cover.jpg`.
3. Open KDP's online previewer and check every flagged page/screen.
4. Order a paperback proof copy before enabling live sales.
5. If KDP assigns a free ISBN, verify whether you want to add it to a future copyright page revision.
""",
        encoding="utf-8",
    )


def main() -> None:
    register_fonts()
    source = SOURCE_HTML.read_text(encoding="utf-8")
    chapters = extract_chapters(source)
    if len(chapters) != 9:
        raise SystemExit(f"Expected 9 chapters, found {len(chapters)}")

    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    interior_pdf = PAPERBACK_DIR / "xadrez-no-comando-paperback-miolo-kdp.pdf"
    cover_pdf = PAPERBACK_DIR / "xadrez-no-comando-paperback-capa-kdp.pdf"
    cover_preview = PREVIEWS_DIR / "xadrez-no-comando-paperback-spread-preview.png"
    page_count = build_interior(chapters, interior_pdf)
    specs = build_cover(page_count, cover_pdf, cover_preview)
    write_metadata(specs, OUT_DIR / "kdp-metadata.json")
    write_readme(specs, OUT_DIR / "README.md")
    print(json.dumps(specs, indent=2))


if __name__ == "__main__":
    main()
