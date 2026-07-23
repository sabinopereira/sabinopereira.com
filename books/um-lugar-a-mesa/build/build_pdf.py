from pathlib import Path
from html import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT.parents[1] / "output" / "pdf" / "um-lugar-a-mesa"
OUT = OUT_DIR / "Um Lugar à Mesa - Edicao Premium.pdf"
COVER = ROOT / "assets" / "um-lugar-a-mesa-cover-premium-1600x2560.jpg"
CHAPTERS = [ROOT / "source" / f"capitulo-{n:02d}-completo.md" for n in range(1, 13)]
EPILOGUE = ROOT / "source" / "epilogo-completo.md"

CHAPTER_TITLES = [
    "A Mesa", "A Entrada", "O Apetite", "O Ás", "A Rainha", "O Rei",
    "O Homem do Avental", "A Cadeira Sem Nome", "O Envelope Azul",
    "A Mulher na Escada", "Perder de Propósito", "A Porta",
]

PAGE_W, PAGE_H = 6.25 * inch, 10 * inch
BURGUNDY = colors.HexColor("#5A1F27")
GOLD = colors.HexColor("#A77A35")
INK = colors.HexColor("#171513")
MUTED = colors.HexColor("#514941")
HAIRLINE = colors.HexColor("#DED7CF")

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("Georgia", str(FONT_DIR / "Georgia.ttf")))
pdfmetrics.registerFont(TTFont("Georgia-Italic", str(FONT_DIR / "Georgia Italic.ttf")))
pdfmetrics.registerFont(TTFont("Georgia-Bold", str(FONT_DIR / "Georgia Bold.ttf")))
pdfmetrics.registerFontFamily(
    "Georgia", normal="Georgia", bold="Georgia-Bold",
    italic="Georgia-Italic", boldItalic="Georgia-Bold"
)


class FullPageCover(Flowable):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = str(image_path)
        self.width = PAGE_W
        self.height = PAGE_H

    def wrap(self, avail_width, avail_height):
        return 0, 0

    def draw(self):
        pass


class PremiumDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
            id="main",
        )
        self.addPageTemplates(PageTemplate(id="premium", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.drawImage(
                str(COVER), 0, 0, width=PAGE_W, height=PAGE_H,
                preserveAspectRatio=False, mask="auto",
            )
            canvas.restoreState()
            return
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        if doc.page >= 7:
            canvas.setFont("Georgia", 8)
            canvas.setFillColor(colors.HexColor("#7A716A"))
            canvas.drawCentredString(PAGE_W / 2, 0.42 * inch, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "ChapterTitle":
            text = getattr(flowable, "toc_label", flowable.getPlainText())
            key = f"chapter-{self.seq.nextf('chapter')}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=0, closed=False)
            self.notify("TOCEntry", (0, text, self.page, key))


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
            flush()
            blocks.append(("divider", "•"))
            continue
        marked = (line.startswith("**") and line.endswith("**")) or (
            line.startswith("*") and line.endswith("*")
        )
        plain = clean_markdown(line)
        if line.startswith("“") or line.startswith('"'):
            flush()
            blocks.append(("dialogue", plain))
            continue
        if marked:
            flush()
            blocks.append(("display", plain))
            continue
        buffer.append(plain)
        chars += len(plain)
        if len(buffer) >= 4 or chars >= 420 or plain.endswith(":"):
            flush()
    flush()
    return blocks


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="BookBody", fontName="Georgia", fontSize=10.6, leading=15.5,
    textColor=INK, alignment=TA_JUSTIFY, firstLineIndent=15,
    spaceAfter=5.5, splitLongWords=False, allowWidows=0, allowOrphans=0,
))
styles.add(ParagraphStyle(
    name="Dialogue", parent=styles["BookBody"], firstLineIndent=0,
    alignment=TA_LEFT, spaceAfter=5.2,
))
styles.add(ParagraphStyle(
    name="Display", parent=styles["BookBody"], firstLineIndent=0,
    alignment=TA_CENTER, fontSize=9.7, leading=14.5, textColor=BURGUNDY,
    leftIndent=22, rightIndent=22, spaceBefore=8, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="ChapterTitle", fontName="Georgia", fontSize=20, leading=26,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="ChapterSubtitle", fontName="Georgia-Italic", fontSize=12,
    leading=17, textColor=MUTED, alignment=TA_CENTER, spaceAfter=14,
))
styles.add(ParagraphStyle(
    name="FrontTitle", fontName="Georgia", fontSize=26, leading=32,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=14,
))
styles.add(ParagraphStyle(
    name="FrontHeading", fontName="Georgia", fontSize=18, leading=23,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=18,
))
styles.add(ParagraphStyle(
    name="FrontBody", fontName="Georgia", fontSize=10.2, leading=15,
    textColor=INK, alignment=TA_LEFT, spaceAfter=9,
))
styles.add(ParagraphStyle(
    name="Centered", parent=styles["FrontBody"], alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="Epigraph", parent=styles["Centered"], fontName="Georgia-Italic",
    fontSize=12, leading=18, leftIndent=28, rightIndent=28,
))
styles.add(ParagraphStyle(
    name="TOCHeading", fontName="Georgia", fontSize=20, leading=25,
    textColor=BURGUNDY, alignment=TA_CENTER, spaceAfter=20,
))


def add_chapter_opener(story, label, subtitle):
    story.append(PageBreak())
    story.append(Spacer(1, 2.72 * inch))
    story.append(Paragraph("•", ParagraphStyle(
        "Ornament", fontName="Georgia", fontSize=8, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=10,
    )))
    heading = Paragraph(escape(label), styles["ChapterTitle"])
    heading.toc_label = f"{label} - {subtitle}"
    story.append(heading)
    story.append(Paragraph(escape(subtitle), styles["ChapterSubtitle"]))
    story.append(Table([[""]], colWidths=[0.78 * inch], rowHeights=[0.5], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GOLD),
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, GOLD),
    ])))
    story.append(PageBreak())


def add_book_text(story, source):
    first = True
    for kind, text in prose_blocks(source.read_text(encoding="utf-8")):
        if kind == "divider":
            story.append(Spacer(1, 9))
            story.append(Paragraph("•", ParagraphStyle(
                "SceneBreak", fontName="Georgia", fontSize=7, textColor=GOLD,
                alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
            )))
            story.append(Spacer(1, 9))
            first = False
            continue
        style = styles["BookBody"]
        if kind == "dialogue":
            style = styles["Dialogue"]
        elif kind == "display":
            style = styles["Display"]
        p = Paragraph(escape(text), style)
        if first and kind == "narrative":
            p.style = ParagraphStyle("OpeningParagraph", parent=styles["BookBody"], firstLineIndent=0)
        story.append(p)
        first = False


def build_story():
    story = [FullPageCover(COVER), PageBreak()]

    story += [
        Spacer(1, 3.25 * inch),
        Paragraph("UM LUGAR À MESA", styles["FrontTitle"]),
        Paragraph("SABINO PEREIRA", ParagraphStyle(
            "Author", fontName="Georgia", fontSize=12, leading=16,
            textColor=GOLD, alignment=TA_CENTER, spaceBefore=4,
        )),
        PageBreak(),
        Spacer(1, 0.7 * inch),
        Paragraph("Direitos de autor", styles["FrontHeading"]),
        Paragraph("<i>Um Lugar à Mesa</i>", styles["FrontBody"]),
        Paragraph("Copyright © 2026 Sabino Pereira", styles["FrontBody"]),
        Paragraph("Todos os direitos reservados.", styles["FrontBody"]),
        Paragraph("Nenhuma parte desta publicação pode ser reproduzida, armazenada ou transmitida, por qualquer forma ou meio, eletrónico, mecânico, fotocópia, gravação ou outro, sem autorização prévia e escrita do autor, exceto no caso de breves citações utilizadas em críticas ou recensões.", styles["FrontBody"]),
        Paragraph("Esta é uma obra de ficção. Nomes, personagens, organizações, acontecimentos e lugares são produto da imaginação do autor ou utilizados de forma fictícia. Qualquer semelhança com pessoas reais, vivas ou falecidas, ou com acontecimentos reais é mera coincidência.", styles["FrontBody"]),
        Paragraph("Edição portuguesa premium<br/>Primeira edição digital, 2026", styles["FrontBody"]),
        PageBreak(),
        Spacer(1, 3.05 * inch),
        Paragraph("Para todos os que alguma vez confundiram um lugar à mesa com um lugar no mundo.", styles["Centered"]),
        PageBreak(),
        Spacer(1, 2.9 * inch),
        Paragraph("Há pessoas que passam a vida inteira a conquistar um lugar sem perguntarem quem teve de se levantar.", styles["Epigraph"]),
        PageBreak(),
        Spacer(1, 0.55 * inch),
        Paragraph("Índice", styles["TOCHeading"]),
    ]

    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle(
        "TOCLevel1", fontName="Georgia", fontSize=10.2, leading=17,
        leftIndent=0, firstLineIndent=0, textColor=INK,
        spaceBefore=2, spaceAfter=2,
    )]
    story += [toc, PageBreak(), Spacer(1, 0.7 * inch), Paragraph("Nota ao leitor", styles["FrontHeading"])]
    note = [
        "Todos acreditamos saber quem somos.",
        "Até ao momento em que uma escolha nos obriga a descobrir quem estamos dispostos a sacrificar.",
        "Esta história começa com um jantar.",
        "À volta da mesa sentam-se pessoas habituadas ao poder, ao sucesso e ao controlo. Cada uma acredita conhecer a verdade sobre a própria vida. Cada uma transporta um segredo que preferia deixar enterrado.",
        "Ao longo da noite, as cartas serão distribuídas.",
        "Não para decidir quem vence.",
        "Mas para revelar quem cada um sempre foi.",
        "Bem-vindo a <i>Um Lugar à Mesa</i>.",
    ]
    story.extend(Paragraph(p, styles["FrontBody"]) for p in note)

    for n, source in enumerate(CHAPTERS, 1):
        add_chapter_opener(story, f"CAPÍTULO {n}", CHAPTER_TITLES[n - 1])
        add_book_text(story, source)

    add_chapter_opener(story, "EPÍLOGO", "Quando Ninguém Está a Olhar")
    add_book_text(story, EPILOGUE)
    return story


OUT_DIR.mkdir(parents=True, exist_ok=True)
doc = PremiumDocTemplate(
    str(OUT), pagesize=portrait((PAGE_W, PAGE_H)),
    leftMargin=0.74 * inch, rightMargin=0.74 * inch,
    topMargin=0.78 * inch, bottomMargin=0.72 * inch,
    title="Um Lugar à Mesa", author="Sabino Pereira",
    subject="Edição portuguesa premium",
)
doc.multiBuild(build_story())
print(OUT)
