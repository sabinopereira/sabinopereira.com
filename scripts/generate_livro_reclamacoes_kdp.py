#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import uuid
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Flowable,
)


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "books/livro-reclamacoes"
SOURCE_TXT = BOOK_DIR / "source/livro-reclamacoes-source-textutil.txt"
KDP_UPLOAD_EPUB = BOOK_DIR / "source/livro-reclamacoes-amazon-kdp-upload-original.epub"
EDITED_TXT = BOOK_DIR / "source/livro-reclamacoes-edited.txt"
EBOOK_DIR = BOOK_DIR / "ebook"
PAPERBACK_DIR = BOOK_DIR / "paperback"
PREVIEWS_DIR = BOOK_DIR / "previews"

EBOOK_COVER = EBOOK_DIR / "livro-reclamacoes-ebook-cover.jpg"
SELECTED_COVER = PREVIEWS_DIR / "livro-reclamacoes-cover-improved-approved.png"
EPUB_OUT = EBOOK_DIR / "livro-reclamacoes-kindle-ebook.epub"
INTERIOR_PDF = PAPERBACK_DIR / "livro-reclamacoes-paperback-miolo-kdp.pdf"
COVER_PDF = PAPERBACK_DIR / "livro-reclamacoes-paperback-capa-kdp.pdf"
METADATA_JSON = BOOK_DIR / "kdp-metadata.json"

TITLE = "Livro de Reclamações para o Mundo"
SUBTITLE = "Crónicas do Absurdo"
AUTHOR = "Sabino Pereira"
LANGUAGE = "pt"

TRIM_W = 6 * inch
TRIM_H = 9 * inch
BLEED = 0.125 * inch
WHITE_PAPER_SPINE_PER_PAGE = 0.002252 * inch

DROP_TITLES = {
    "A Indústria da Beleza Impossível",
    "Gurus da Alma e da Carteira",
    "A Maquilhagem do Óbvio (O Gourmet da Banalidade)",
    "Consumismo Disfarçado (O Luxo do Lixo)",
    "Celebridades Anónimas",
}

SUPPLEMENTAL_AFTER_TITLE = "O Negócio da Cauda a Abanar"
SUPPLEMENTAL_TITLES = ["O Mercado da Fé"]

TITLE_REWRITES = {
    "A Ditadura do Ofendidinho": "A Ditadura da Reação",
    "O Manual Infinito do Ser (A Confusão dos Géneros)": "O Manual Infinito do Falar Certo",
    "A Ditadura da Melhor Versão  (Optimismo Tóxico)": "A Ditadura da Melhor Versão (Otimismo Tóxico)",
    "A Arquitetura da Exclusão  (O Teatro da Acessibilidade)": "A Arquitetura da Exclusão (O Teatro da Acessibilidade)",
    "O Paradoxo da Conectividade  (A Solidão Digital)": "O Paradoxo da Conectividade (A Solidão Digital)",
}

PART_TITLES = {
    "Parte I": "Mundo em modo espetáculo",
    "Parte II": "Mercado da alma, do corpo e da fé",
    "Parte III": "Relações, máscaras e solidão",
    "Parte IV": "Identidade, exaustão e confusão",
    "Parte V": "Memória, medo e fim de linha",
}

ILLUSTRATED_TITLES = {
    "O Inocente do Jogo Limpo": "stamp",
    "O Teatro do Candidato Ideal": "mask",
    "A Liturgia do Calendário Cheio": "calendar",
    "O Labirinto do \"Aguarde\" (Apoio ao Cliente)": "counter",
    "O Negócio da Cauda a Abanar": "vet",
    "O Mercado da Fé": "altar",
    "O Paradoxo da Conectividade (A Solidão Digital)": "phone",
    "O Depósito da Memória": "memory",
    "A Fila Invisível (A Caridade como Espetáculo)": "queue",
}

DEFAULT_ILLUSTRATION_SEQUENCE = [
    "stamp",
    "counter",
    "phone",
    "calendar",
    "mask",
    "queue",
    "memory",
    "altar",
    "vet",
]


@dataclass
class Chapter:
    number: int
    title: str
    subtitle: str
    paragraphs: list[str]


@dataclass
class Part:
    roman: str
    title: str
    chapters: list[Chapter]


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    fonts = {
        "Georgia": font_dir / "Georgia.ttf",
        "Georgia-Bold": font_dir / "Georgia Bold.ttf",
        "Georgia-Italic": font_dir / "Georgia Italic.ttf",
        "Georgia-BoldItalic": font_dir / "Georgia Bold Italic.ttf",
        "Impact": font_dir / "Impact.ttf",
    }
    for name, path in fonts.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def source_lines() -> list[str]:
    text = SOURCE_TXT.read_text(encoding="utf-8")
    text = text.replace("\xa0", " ").replace("\u200b", "")
    # Keep U+2028 soft line separators as intentional verse breaks.
    lines = [clean_line(line) for line in text.split("\n")]
    return [line for line in lines if line]


def clean_line(text: str) -> str:
    text = text.strip()
    text = text.replace("\u2028", " <br/> ")
    text = text.replace("\u2011", "-").replace("\u2010", "-").replace("\u2013", "–")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = text.replace("Optimismo", "Otimismo")
    text = text.replace("pára", "para")
    text = text.replace("never saíram", "nunca saíram")
    text = text.replace("neutral —", "neutro —")
    text = text.replace("Inteligência Artificialem", "Inteligência Artificial em")
    text = text.replace("Chamamos-lheaproveitamento", "Chamamos-lhe aproveitamento")
    text = text.replace("Chamamos-lheatualização", "Chamamos-lhe atualização")
    text = text.replace("Chamamos-lheretenção", "Chamamos-lhe retenção")
    text = text.replace("Chamamos-lheaceleração", "Chamamos-lhe aceleração")
    text = text.replace("Chamamos-lhedinamismo", "Chamamos-lhe dinamismo")
    text = text.replace("Chamamos-lhecuradoria", "Chamamos-lhe curadoria")
    text = text.replace("Chamamos-lheconstrução", "Chamamos-lhe construção")
    text = text.replace("Chamamos-lhe falta", "Chamamos-lhe falta")
    text = text.replace("MB Way", "MB WAY")
    text = text.replace("Linked In", "LinkedIn")
    text = text.replace("TikTokcom", "TikTok com")
    text = text.replace("do “Aguarde”", "do \"Aguarde\"")
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9“])", r"\1 \2", text)
    text = re.sub(r"([a-záéíóúâêôãõç])([(])", r"\1 \2", text)
    text = re.sub(r"([)])([A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç])", r"\1 \2", text)
    text = re.sub(r"([a-záéíóúâêôãõç])([A-ZÁÉÍÓÚÂÊÔÃÕÇ])", r"\1 \2", text)
    text = re.sub(r"\s*<br/>\s*", "<br/>", text)
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace(" ;", ";")
    text = text.replace(" :", ":")
    text = text.replace("Linked In", "LinkedIn")
    return text


def canonical_title(text: str) -> str:
    return re.sub(r"\s+", " ", clean_line(text)).strip()


class BlockTextParser(HTMLParser):
    block_tags = {"h1", "h2", "h3", "p"}

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[tuple[str, str]] = []
        self.current_tag: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.block_tags:
            self.current_tag = tag
            self.current_text = []
        elif tag == "br" and self.current_tag:
            self.current_text.append(" <br/> ")

    def handle_endtag(self, tag: str) -> None:
        if tag == self.current_tag:
            text = " ".join("".join(self.current_text).split())
            if text:
                self.blocks.append((tag, text))
            self.current_tag = None
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_tag:
            self.current_text.append(data)


def extract_kdp_epub_chapter(title: str) -> Chapter | None:
    if not KDP_UPLOAD_EPUB.exists():
        return None
    with ZipFile(KDP_UPLOAD_EPUB) as z:
        for name in z.namelist():
            if not name.endswith(".xhtml"):
                continue
            raw = z.read(name).decode("utf-8", errors="replace")
            if title not in raw:
                continue
            parser = BlockTextParser()
            parser.feed(raw)
            blocks = [(tag, clean_line(text)) for tag, text in parser.blocks]
            h1_titles = [text for tag, text in blocks if tag == "h1"]
            if title not in h1_titles:
                continue
            paragraphs: list[str] = []
            collecting = False
            for tag, text in blocks:
                if tag == "h1" and text == title:
                    collecting = True
                    continue
                if not collecting:
                    continue
                if text.startswith("Parte "):
                    break
                if text == title:
                    continue
                paragraphs.append(text)
            return Chapter(number=0, title=title, subtitle="", paragraphs=paragraphs)
    return None


def supplemental_chapters() -> list[Chapter]:
    chapters: list[Chapter] = []
    for title in SUPPLEMENTAL_TITLES:
        chapter = extract_kdp_epub_chapter(title)
        if chapter is not None:
            chapters.append(chapter)
    return chapters


def parse_book() -> tuple[list[str], list[Part]]:
    lines = source_lines()
    pref_start = next(i for i, line in enumerate(lines) if line == "Prefácio" and i > 20)
    first_part = next(i for i, line in enumerate(lines[pref_start:], pref_start) if line.startswith("Parte I"))
    preface = [line.replace("34 reclamações", "30 reclamações") for line in lines[pref_start + 1 : first_part]]

    chapter_starts = [i for i, line in enumerate(lines) if line.startswith("Reclamação n.º")]
    part_for_chapter: dict[int, str] = {}
    current_roman = "I"
    chapter_start_set = set(chapter_starts)
    for i in range(first_part, len(lines)):
        roman_match = re.match(r"Parte\s+([IVX]+)", lines[i])
        if roman_match:
            current_roman = roman_match.group(1)
        if i in chapter_start_set:
            part_for_chapter[i] = current_roman
    parts: list[Part] = []
    current_part: Part | None = None
    kept_chapters: list[Chapter] = []
    supplements = supplemental_chapters()

    for idx, start in enumerate(chapter_starts):
        end = chapter_starts[idx + 1] if idx + 1 < len(chapter_starts) else len(lines)
        title = canonical_title(lines[start + 1])
        if title in DROP_TITLES:
            continue
        roman = part_for_chapter.get(start, "I")
        part_title = PART_TITLES.get(f"Parte {roman}", "")
        if current_part is None or current_part.roman != roman:
            current_part = Part(roman=roman, title=part_title, chapters=[])
            parts.append(current_part)

        raw_title = TITLE_REWRITES.get(title, title)
        subtitle = ""
        body_start = start + 2
        if body_start < end and lines[body_start].startswith("("):
            subtitle = lines[body_start]
            body_start += 1
        paragraphs = [clean_line(line) for line in lines[body_start:end]]
        paragraphs = [line for line in paragraphs if not line.startswith("Parte ")]
        paragraphs = polish_chapter(raw_title, paragraphs)
        chapter = Chapter(number=len(kept_chapters) + 1, title=raw_title, subtitle=subtitle, paragraphs=paragraphs)
        kept_chapters.append(chapter)
        current_part.chapters.append(chapter)
        if title == SUPPLEMENTAL_AFTER_TITLE:
            for supplement in supplements:
                inserted = Chapter(
                    number=len(kept_chapters) + 1,
                    title=supplement.title,
                    subtitle=supplement.subtitle,
                    paragraphs=supplement.paragraphs,
                )
                kept_chapters.append(inserted)
                current_part.chapters.append(inserted)

    return preface, parts


def polish_chapter(title: str, paragraphs: list[str]) -> list[str]:
    if title == "O Paradoxo da Conectividade (A Solidão Digital)":
        return [
            "I. A Aldeia Sem Porta",
            "Ensinaram-te<br/>que o mundo agora<br/>cabia na tua mão.",
            "Prometeram-te proximidade.",
            "Prometeram-te comunidade.",
            "Prometeram-te que ninguém<br/>voltaria a estar sozinho.",
            "Mas tu descobriste<br/>uma verdade mais silenciosa:",
            "estar ligado a tudo<br/>não é o mesmo<br/>que pertencer a alguém.",
            "A tua rede é vasta.",
            "Os teus contactos<br/>contam-se aos milhares.",
            "Mas, nas noites difíceis,<br/>o ecrã é muitas vezes<br/>a única luz acesa.",
            "Há fibra ótica.",
            "Há notificações.",
            "Há grupos,<br/>canais,<br/>mensagens,<br/>reações.",
            "E mesmo assim,<br/>falta a voz.",
            "Falta a presença.",
            "Falta alguém<br/>que repare<br/>quando o teu silêncio<br/>mudou de peso.",
            "Chamam-lhe<br/>conectividade total.",
            "Mas parece<br/>uma casa cheia de janelas<br/>sem nenhuma porta aberta.",
            "II. Resposta Automática da Rede Global<br/>(não responder)",
            "Estimado Utilizador<br/>Hiper-Conectado,",
            "Obrigado por manter<br/>o seu tráfego ativo.",
            "Lamentamos<br/>que se sinta sozinho<br/>no meio da nossa rede,<br/>mas importa esclarecer:",
            "Nós não vendemos companhia.",
            "Vendemos a infraestrutura<br/>para a simular.",
            "Se tem mil contactos<br/>e ninguém para chamar<br/>numa emergência?",
            "Chamamos-lhe<br/>otimização social.",
            "Se sente ansiedade<br/>quando o telemóvel<br/>fica em silêncio?",
            "Chamamos-lhe<br/>engajamento saudável.",
            "O nosso modelo<br/>é simples:",
            "quanto mais vazio<br/>se sentir por dentro,",
            "mais tempo passa<br/>à procura de sinal<br/>por fora.",
            "Não nos peça<br/>relações humanas.",
            "Oferecemos velocidade.",
            "Oferecemos alcance.",
            "Oferecemos presença digital<br/>sem presença real.",
            "Com os melhores cumprimentos,<br/>A Administração da Solidão Assistida.",
            "III. O Eco do Wi-Fi Vazio",
            "A bateria chegou ao fim.",
            "O quarto ficou escuro.",
            "Pela primeira vez<br/>em muitas horas,<br/>nada vibrou.",
            "Chegou o momento<br/>de olhar<br/>para a tua vida social<br/>sem filtro azul.",
            "Conversas curtas.",
            "Respostas adiadas.",
            "Amigos que existem<br/>mais no feed<br/>do que na tua mesa.",
            "Uma galeria de rostos<br/>que sabem onde estiveste,<br/>mas não sabem<br/>como estás.",
            "E aí percebes<br/>a armadilha:",
            "a tecnologia aproximou<br/>os corpos distantes,",
            "mas ensinou os próximos<br/>a desaparecer<br/>sem se levantarem da cadeira.",
            "O mundo chama-lhe<br/>era da comunicação.",
            "Tu sabes<br/>a verdade:",
            "o sinal está no máximo,",
            "mas a escuta<br/>quase desapareceu.",
            "Fica a luz azul<br/>no rosto cansado.",
            "Fica o carregador<br/>na mão.",
            "E fica uma vontade simples:",
            "bater à porta de alguém<br/>sem marcar hora,",
            "só para lembrar<br/>que a rede mais importante<br/>do mundo",
            "ainda não tem app.",
        ]
    if title == "O Manual Infinito do Falar Certo":
        return [
            "I. A Burocracia da Conversa",
            "Ensinaram-nos que respeito é atenção ao outro.",
            "Mas tu descobriste que, em alguns espaços, a conversa deixou de ser conversa. Passou a ser exame oral, com atualização semanal e penalização imediata.",
            "A intenção já não chega. A escuta já não chega. Até a boa fé precisa de manual.",
            "O problema não é aprender a tratar melhor as pessoas. O problema é quando a linguagem se transforma numa repartição: senha na mão, medo no peito, formulário invisível antes de cada frase.",
            "II. Resposta Automática do Comité da Palavra Certa (não responder)",
            "Caro Falante em Processo de Atualização,",
            "Obrigado por tentar comunicar sem causar danos irreversíveis ao universo.",
            "Lamentamos que a sua dúvida pareça humana, mas importa esclarecer:",
            "Nós não vendemos entendimento. Vendemos conformidade ansiosa.",
            "Se hesita antes de falar? Chamamos-lhe consciência em falta.",
            "Se pergunta para aprender? Chamamos-lhe atraso cultural.",
            "Se se engana numa palavra, mesmo sem maldade? Chamamos-lhe material para julgamento público.",
            "O nosso modelo não é aproximar pessoas. É criar distância com vocabulário técnico.",
            "Não nos peça paciência. Oferecemos correção imediata, tom superior e uma lista de leituras que muda antes de chegar à página três.",
            "Com vigilância cordial, A Administração da Linguagem Impecável.",
            "III. O Dia em que o Café Arrefeceu",
            "Sentado à mesa, tentaste falar com cuidado.",
            "Querias ouvir. Querias compreender. Querias acertar.",
            "Mas cada frase parecia atravessar um campo minado.",
            "O café arrefeceu enquanto procuravas a palavra perfeita.",
            "E aí percebeste a ironia: quando o medo de errar se torna maior do que a vontade de conversar, ninguém aprende nada. Apenas se cala melhor.",
            "O mundo chama-lhe evolução da linguagem. Tu sabes a verdade: o respeito sem humanidade vira protocolo.",
            "Fica a vontade simples de voltar a uma conversa onde se possa perguntar, corrigir, ouvir e continuar sentado à mesma mesa.",
        ]
    return paragraphs


def roman_num(value: int) -> str:
    mapping = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    result = ""
    for n, r in mapping:
        while value >= n:
            result += r
            value -= n
    return result


def illustration_kind_for(chapter: Chapter) -> str:
    if chapter.title in ILLUSTRATED_TITLES:
        return ILLUSTRATED_TITLES[chapter.title]
    return DEFAULT_ILLUSTRATION_SEQUENCE[(chapter.number - 1) % len(DEFAULT_ILLUSTRATION_SEQUENCE)]


def write_edited_text(preface: list[str], parts: list[Part]) -> None:
    lines: list[str] = [TITLE, SUBTITLE, AUTHOR, "", "Prefácio", *preface, ""]
    for part in parts:
        lines.extend([f"Parte {part.roman} - {part.title}", ""])
        for chapter in part.chapters:
            lines.append(f"Reclamação n.º {chapter.number}")
            lines.append(chapter.title)
            if chapter.subtitle:
                lines.append(chapter.subtitle)
            lines.extend(chapter.paragraphs)
            lines.append("")
    EDITED_TXT.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def p(text: str, style: ParagraphStyle) -> Paragraph:
    escaped = html.escape(text).replace("&lt;br/&gt;", "<br/>")
    return Paragraph(escaped, style)


def epub_text(text: str) -> str:
    return html.escape(text).replace("&lt;br/&gt;", "<br/>")


def epub_illustration_png(kind: str) -> bytes:
    img = Image.new("RGB", (650, 310), "white")
    d = ImageDraw.Draw(img)
    black = (18, 18, 18)
    gray = (95, 95, 95)
    w = 5

    if kind == "stamp":
        d.rectangle((145, 95, 500, 205), outline=black, width=w)
        d.line((175, 165, 470, 165), fill=black, width=3)
        d.text((215, 125), "RECLAMACAO", fill=black)
    elif kind == "mask":
        d.ellipse((150, 80, 295, 220), outline=black, width=w)
        d.ellipse((355, 80, 500, 220), outline=black, width=w)
        for x in (200, 245, 405, 450):
            d.ellipse((x - 9, 140, x + 9, 158), fill=black)
        d.arc((190, 145, 255, 200), 20, 160, fill=black, width=4)
        d.arc((395, 160, 460, 205), 200, 340, fill=black, width=4)
    elif kind == "calendar":
        d.rectangle((135, 60, 515, 245), outline=black, width=w)
        d.line((135, 110, 515, 110), fill=black, width=w)
        for x in (211, 287, 363, 439):
            d.line((x, 110, x, 245), fill=gray, width=2)
        for y in (155, 200):
            d.line((135, y, 515, y), fill=gray, width=2)
        d.text((160, 78), "SEM TEMPO", fill=black)
    elif kind == "counter":
        d.rectangle((100, 190, 550, 230), outline=black, width=w)
        d.rectangle((350, 78, 515, 190), outline=black, width=w)
        d.ellipse((150, 95, 230, 175), outline=black, width=w)
        d.line((190, 175, 190, 205), fill=black, width=w)
        d.text((382, 122), "AGUARDE", fill=black)
    elif kind == "vet":
        d.ellipse((120, 95, 245, 195), outline=black, width=w)
        d.ellipse((155, 70, 225, 140), outline=black, width=w)
        d.line((145, 190, 125, 235), fill=black, width=w)
        d.line((225, 190, 250, 235), fill=black, width=w)
        d.rectangle((360, 70, 490, 225), outline=black, width=w)
        d.text((397, 125), "FATURA", fill=black)
        d.line((385, 165, 465, 165), fill=black, width=3)
    elif kind == "altar":
        d.rectangle((155, 205, 500, 250), outline=black, width=w)
        d.line((325, 70, 325, 205), fill=black, width=w)
        d.line((275, 125, 375, 125), fill=black, width=w)
        d.rectangle((185, 135, 265, 190), outline=black, width=w)
        d.text((210, 152), "MB", fill=black)
        d.ellipse((430, 110, 485, 165), outline=black, width=w)
        d.line((458, 165, 458, 215), fill=black, width=w)
    elif kind == "phone":
        d.rounded_rectangle((250, 40, 400, 260), radius=18, outline=black, width=w)
        d.ellipse((318, 230, 332, 244), fill=black)
        for y in (95, 135, 175):
            d.line((275, y, 375, y), fill=black, width=3)
        d.arc((115, 100, 200, 190), 295, 65, fill=black, width=4)
        d.arc((450, 100, 535, 190), 115, 245, fill=black, width=4)
    elif kind == "memory":
        d.rectangle((115, 80, 225, 220), outline=black, width=w)
        d.rectangle((275, 105, 375, 195), outline=black, width=w)
        d.rectangle((425, 80, 535, 220), outline=black, width=w)
        d.ellipse((150, 115, 190, 155), outline=black, width=w)
        d.line((445, 100, 515, 200), fill=black, width=w)
        d.line((515, 100, 445, 200), fill=black, width=w)
    else:
        for x in (150, 240, 330, 420):
            d.ellipse((x - 20, 70, x + 20, 110), outline=black, width=w)
            d.line((x, 110, x, 200), fill=black, width=w)
            d.line((x - 35, 150, x + 35, 150), fill=black, width=w)
        d.rectangle((495, 120, 550, 225), outline=black, width=w)
        d.line((115, 235, 560, 235), fill=black, width=3)

    out = BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


def draw_page_number(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    if doc.page <= 4:
        return
    canv.saveState()
    canv.setFont("Georgia", 9)
    canv.setFillColor(colors.HexColor("#555555"))
    canv.drawCentredString(TRIM_W / 2, 0.42 * inch, str(doc.page))
    canv.restoreState()


class EditorialIllustration(Flowable):
    def __init__(self, kind: str, width: float = 3.25 * inch, height: float = 1.55 * inch) -> None:
        super().__init__()
        self.kind = kind
        self.width = width
        self.height = height

    def wrap(self, availWidth: float, availHeight: float) -> tuple[float, float]:
        return min(self.width, availWidth), self.height

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        c.saveState()
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.white)
        c.setLineWidth(1.3)
        getattr(self, f"draw_{self.kind}", self.draw_stamp)(c, w, h)
        c.restoreState()

    def draw_stamp(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.rect(0.35 * inch, 0.28 * inch, 2.25 * inch, 0.78 * inch, stroke=1, fill=0)
        c.setFont("Impact", 18)
        c.drawCentredString(1.48 * inch, 0.66 * inch, "RECLAMAÇÃO")
        c.line(0.55 * inch, 0.45 * inch, 2.4 * inch, 0.45 * inch)

    def draw_mask(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.ellipse(0.6 * inch, 0.25 * inch, 1.55 * inch, 1.2 * inch)
        c.ellipse(1.7 * inch, 0.25 * inch, 2.65 * inch, 1.2 * inch)
        c.circle(0.95 * inch, 0.8 * inch, 0.07 * inch)
        c.circle(1.2 * inch, 0.8 * inch, 0.07 * inch)
        c.arc(0.85 * inch, 0.45 * inch, 1.3 * inch, 0.75 * inch, 200, 140)
        c.circle(2.05 * inch, 0.8 * inch, 0.07 * inch)
        c.circle(2.3 * inch, 0.8 * inch, 0.07 * inch)
        c.arc(1.95 * inch, 0.45 * inch, 2.4 * inch, 0.75 * inch, 20, 140)

    def draw_calendar(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.rect(0.45 * inch, 0.25 * inch, 2.45 * inch, 1.05 * inch)
        c.line(0.45 * inch, 1.02 * inch, 2.9 * inch, 1.02 * inch)
        for x in [0.95, 1.45, 1.95, 2.45]:
            c.line(x * inch, 0.25 * inch, x * inch, 1.02 * inch)
        for y in [0.52, 0.78]:
            c.line(0.45 * inch, y * inch, 2.9 * inch, y * inch)
        c.setFont("Georgia-Bold", 10)
        c.drawString(0.62 * inch, 1.1 * inch, "SEM TEMPO")

    def draw_counter(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.rect(0.35 * inch, 0.25 * inch, 2.75 * inch, 0.28 * inch, fill=0)
        c.rect(1.65 * inch, 0.53 * inch, 1.05 * inch, 0.65 * inch, fill=0)
        c.circle(0.8 * inch, 0.82 * inch, 0.2 * inch)
        c.line(0.8 * inch, 0.62 * inch, 0.8 * inch, 0.28 * inch)
        c.line(0.55 * inch, 0.45 * inch, 1.05 * inch, 0.45 * inch)
        c.setFont("Georgia-Bold", 9)
        c.drawCentredString(2.17 * inch, 0.83 * inch, "AGUARDE")

    def draw_vet(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.circle(0.95 * inch, 0.8 * inch, 0.28 * inch)
        c.ellipse(0.55 * inch, 0.45 * inch, 1.45 * inch, 0.85 * inch)
        c.line(0.6 * inch, 0.45 * inch, 0.5 * inch, 0.25 * inch)
        c.line(1.3 * inch, 0.45 * inch, 1.42 * inch, 0.25 * inch)
        c.rect(1.85 * inch, 0.35 * inch, 0.75 * inch, 0.95 * inch)
        c.setFont("Georgia-Bold", 9)
        c.drawCentredString(2.22 * inch, 0.86 * inch, "FATURA")
        c.line(1.95 * inch, 0.65 * inch, 2.5 * inch, 0.65 * inch)

    def draw_altar(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.rect(0.75 * inch, 0.25 * inch, 1.9 * inch, 0.3 * inch)
        c.line(1.7 * inch, 0.55 * inch, 1.7 * inch, 1.28 * inch)
        c.line(1.38 * inch, 1.0 * inch, 2.02 * inch, 1.0 * inch)
        c.rect(0.9 * inch, 0.62 * inch, 0.52 * inch, 0.38 * inch)
        c.setFont("Georgia-Bold", 8)
        c.drawCentredString(1.16 * inch, 0.76 * inch, "MB")
        c.circle(2.28 * inch, 0.9 * inch, 0.16 * inch)
        c.line(2.28 * inch, 0.74 * inch, 2.28 * inch, 0.45 * inch)

    def draw_phone(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.roundRect(1.1 * inch, 0.18 * inch, 1.05 * inch, 1.22 * inch, 0.08 * inch)
        c.circle(1.62 * inch, 0.34 * inch, 0.04 * inch)
        c.line(1.25 * inch, 1.05 * inch, 2.0 * inch, 1.05 * inch)
        c.line(1.25 * inch, 0.82 * inch, 2.0 * inch, 0.82 * inch)
        c.line(1.25 * inch, 0.59 * inch, 2.0 * inch, 0.59 * inch)
        c.arc(0.55 * inch, 0.5 * inch, 1.0 * inch, 1.0 * inch, 300, 120)
        c.arc(2.25 * inch, 0.5 * inch, 2.7 * inch, 1.0 * inch, 120, 300)

    def draw_memory(self, c: canvas.Canvas, w: float, h: float) -> None:
        c.rect(0.45 * inch, 0.35 * inch, 0.75 * inch, 0.8 * inch)
        c.rect(1.35 * inch, 0.5 * inch, 0.6 * inch, 0.55 * inch)
        c.rect(2.1 * inch, 0.32 * inch, 0.65 * inch, 0.78 * inch)
        c.circle(0.83 * inch, 0.78 * inch, 0.13 * inch)
        c.line(0.62 * inch, 0.52 * inch, 1.03 * inch, 0.52 * inch)
        c.line(1.48 * inch, 0.68 * inch, 1.82 * inch, 0.68 * inch)
        c.line(2.22 * inch, 0.55 * inch, 2.63 * inch, 0.95 * inch)
        c.line(2.63 * inch, 0.55 * inch, 2.22 * inch, 0.95 * inch)

    def draw_queue(self, c: canvas.Canvas, w: float, h: float) -> None:
        for x in [0.65, 1.15, 1.65, 2.15]:
            c.circle(x * inch, 0.98 * inch, 0.12 * inch)
            c.line(x * inch, 0.86 * inch, x * inch, 0.42 * inch)
            c.line((x - 0.16) * inch, 0.65 * inch, (x + 0.16) * inch, 0.65 * inch)
        c.rect(2.55 * inch, 0.28 * inch, 0.34 * inch, 0.6 * inch)
        c.line(0.45 * inch, 0.25 * inch, 2.95 * inch, 0.25 * inch)


def add_blank_page(pdf_path: Path) -> None:
    blank_path = pdf_path.with_suffix(".blank.pdf")
    c = canvas.Canvas(str(blank_path), pagesize=(TRIM_W, TRIM_H))
    c.showPage()
    c.save()
    reader = PdfReader(str(pdf_path))
    blank = PdfReader(str(blank_path)).pages[0]
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_page(blank)
    with pdf_path.open("wb") as handle:
        writer.write(handle)
    blank_path.unlink(missing_ok=True)


def build_interior(preface: list[str], parts: list[Part]) -> int:
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BookTitle", fontName="Impact", fontSize=36, leading=38, alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle("Subtitle", fontName="Georgia-Italic", fontSize=14, leading=19, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Author", fontName="Georgia", fontSize=11.5, leading=16, alignment=TA_CENTER, spaceBefore=34))
    styles.add(ParagraphStyle("Small", fontName="Georgia", fontSize=9.4, leading=14, textColor=colors.HexColor("#333333")))
    styles.add(ParagraphStyle("Copyright", fontName="Georgia", fontSize=9.4, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#333333")))
    styles.add(ParagraphStyle("Toc", fontName="Georgia", fontSize=10.7, leading=15.2, spaceAfter=1))
    styles.add(ParagraphStyle("PrefaceTitle", fontName="Impact", fontSize=26, leading=30, alignment=TA_LEFT, spaceAfter=18))
    styles.add(ParagraphStyle("PartTitle", fontName="Impact", fontSize=25, leading=28, alignment=TA_CENTER, textColor=colors.white, spaceAfter=12))
    styles.add(ParagraphStyle("PartSubtitle", fontName="Georgia-Italic", fontSize=14, leading=20, alignment=TA_CENTER, textColor=colors.white))
    styles.add(ParagraphStyle("ComplaintNo", fontName="Georgia-Bold", fontSize=10.5, leading=15, textColor=colors.HexColor("#777777"), spaceAfter=6))
    styles.add(ParagraphStyle("ChapterTitle", fontName="Impact", fontSize=23, leading=27, alignment=TA_LEFT, spaceAfter=8))
    styles.add(ParagraphStyle("ChapterSubtitle", fontName="Georgia-Italic", fontSize=12.5, leading=18, alignment=TA_LEFT, textColor=colors.HexColor("#333333"), spaceAfter=16))
    styles.add(ParagraphStyle("Section", fontName="Georgia-BoldItalic", fontSize=12.8, leading=18, alignment=TA_LEFT, spaceBefore=12, spaceAfter=9))
    styles.add(ParagraphStyle("Body", fontName="Georgia", fontSize=10.9, leading=16.4, spaceAfter=7.5))
    styles.add(ParagraphStyle("Short", fontName="Georgia-Italic", fontSize=11.5, leading=17, alignment=TA_CENTER, spaceAfter=7.5))

    doc = BaseDocTemplate(
        str(INTERIOR_PDF),
        pagesize=(TRIM_W, TRIM_H),
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
        title=TITLE,
        author=AUTHOR,
    )
    odd = Frame(0.72 * inch, 0.72 * inch, TRIM_W - 1.28 * inch, TRIM_H - 1.42 * inch, id="odd")
    even = Frame(0.56 * inch, 0.72 * inch, TRIM_W - 1.28 * inch, TRIM_H - 1.42 * inch, id="even")
    doc.addPageTemplates(
        [
            PageTemplate(id="Odd", frames=[odd], onPage=draw_page_number, autoNextPageTemplate="Even"),
            PageTemplate(id="Even", frames=[even], onPage=draw_page_number, autoNextPageTemplate="Odd"),
        ]
    )

    story: list = [
        Spacer(1, 1.9 * inch),
        p("LIVRO DE<br/>RECLAMAÇÕES<br/>PARA O MUNDO", styles["BookTitle"]),
        p(SUBTITLE, styles["Subtitle"]),
        p(AUTHOR, styles["Author"]),
        PageBreak(),
        Spacer(1, 2.1 * inch),
        p(TITLE, styles["Subtitle"]),
        Spacer(1, 0.25 * inch),
        p("Copyright © 2026 Sabino Pereira. Todos os direitos reservados.", styles["Copyright"]),
        p("Esta é uma obra de crónica, sátira e observação social.", styles["Copyright"]),
        p("Nova edição preparada para Amazon KDP.", styles["Copyright"]),
        PageBreak(),
        p("Índice", styles["PrefaceTitle"]),
    ]
    for part in parts:
        story.append(p(f"Parte {part.roman} - {part.title}", styles["Toc"]))
        for chapter in part.chapters:
            story.append(p(f"  {chapter.number}. {chapter.title}", styles["Toc"]))
        story.append(Spacer(1, 0.08 * inch))
    story.append(PageBreak())
    story.append(p("Prefácio", styles["PrefaceTitle"]))
    for para in preface:
        story.append(p(para, styles["Body"]))
    story.append(PageBreak())

    for part in parts:
        story.extend(part_opener(part, styles))
        for chapter in part.chapters:
            story.append(Spacer(1, 0.28 * inch))
            story.append(p(f"Reclamação n.º {chapter.number}", styles["ComplaintNo"]))
            story.append(p(chapter.title, styles["ChapterTitle"]))
            if chapter.subtitle:
                story.append(p(chapter.subtitle, styles["ChapterSubtitle"]))
            story.append(Spacer(1, 0.08 * inch))
            story.append(EditorialIllustration(illustration_kind_for(chapter)))
            story.append(Spacer(1, 0.18 * inch))
            for para in chapter.paragraphs:
                if re.match(r"^[IVX]+\.", para):
                    story.append(p(para, styles["Section"]))
                else:
                    story.append(p(para, styles["Body"]))
            story.append(PageBreak())

    story.extend([Spacer(1, 3.0 * inch), p(TITLE, styles["Short"]), p("Fim.", styles["Short"])])
    doc.build(story)
    page_count = len(PdfReader(str(INTERIOR_PDF)).pages)
    while page_count < 24 or page_count % 2:
        add_blank_page(INTERIOR_PDF)
        page_count += 1
    return page_count


def part_opener(part: Part, styles: dict[str, ParagraphStyle]) -> list:
    class BlackPage(Spacer):
        def drawOn(self, canv: canvas.Canvas, x: float, y: float, _sW: float = 0) -> None:
            canv.saveState()
            canv.setFillColor(colors.black)
            canv.rect(0, 0, TRIM_W, TRIM_H, stroke=0, fill=1)
            canv.restoreState()

    return [
        BlackPage(1, 0.1),
        Spacer(1, 2.25 * inch),
        KeepTogether(
            [
                p(f"PARTE {part.roman}", styles["PartTitle"]),
                p(part.title, styles["PartSubtitle"]),
            ]
        ),
        PageBreak(),
    ]


def create_cover_jpg() -> None:
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 2560
    original = SELECTED_COVER if SELECTED_COVER.exists() else BOOK_DIR / "source/livro-reclamacoes-original-cover.jpg"
    img = Image.open(original).convert("RGB")
    scale = max(width / img.width, height / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    img = resized.crop((left, top, left + width, top + height))
    img.save(EBOOK_COVER, quality=94, subsampling=1)
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    img.resize((674, 1018), Image.Resampling.LANCZOS).save(PREVIEWS_DIR / "livro-reclamacoes-cover-preview.jpg", quality=92)


def draw_wrapped(c: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float, color) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if c.stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def build_cover_pdf(page_count: int) -> dict[str, float]:
    create_cover_jpg()
    spine = page_count * WHITE_PAPER_SPINE_PER_PAGE
    cover_w = BLEED + TRIM_W + spine + TRIM_W + BLEED
    cover_h = TRIM_H + 2 * BLEED
    back_x = BLEED
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine
    c = canvas.Canvas(str(COVER_PDF), pagesize=(cover_w, cover_h))
    c.setFillColor(colors.HexColor("#0d0d0d"))
    c.rect(0, 0, cover_w, cover_h, stroke=0, fill=1)
    front_safe_inset = 0.32 * inch
    c.drawImage(
        str(EBOOK_COVER),
        front_x + front_safe_inset,
        BLEED + front_safe_inset,
        width=TRIM_W - (2 * front_safe_inset),
        height=TRIM_H - (2 * front_safe_inset),
        preserveAspectRatio=False,
    )

    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#9b1c1f"))
    c.setLineWidth(3)
    back_safe_x = back_x + 0.64 * inch
    back_safe_w = TRIM_W - 1.28 * inch
    c.rect(back_x + 0.52 * inch, 0.65 * inch, TRIM_W - 1.04 * inch, cover_h - 1.3 * inch, stroke=1, fill=0)
    y = cover_h - 0.85 * inch
    y = draw_wrapped(c, TITLE.upper(), back_safe_x, y, back_safe_w, "Impact", 22, 24, colors.white)
    y -= 0.12 * inch
    c.setStrokeColor(colors.HexColor("#f3f0e8"))
    c.line(back_safe_x, y, back_safe_x + 2.25 * inch, y)
    y -= 0.35 * inch
    blurb = (
        "Um livro de crónicas sobre sistemas que falham, promessas vazias, "
        "burocracias infinitas, mercados de ego e a sensação de que o mundo enlouqueceu devagar."
    )
    y = draw_wrapped(c, blurb, back_safe_x, y, back_safe_w, "Georgia", 11.5, 16, colors.HexColor("#f3f0e8"))
    y -= 0.25 * inch
    y = draw_wrapped(c, "Não é autoajuda. Não é manual de soluções rápidas. É uma coleção de reclamações organizadas contra o absurdo moderno.", back_safe_x, y, back_safe_w, "Georgia-Italic", 11.2, 16, colors.HexColor("#d8d1c7"))
    c.setFont("Georgia", 10)
    c.drawString(back_safe_x, 0.82 * inch, AUTHOR)

    if spine >= 0.12 * inch:
        c.saveState()
        c.translate(spine_x + spine / 2, cover_h / 2)
        c.rotate(90)
        c.setFont("Impact", min(15, max(9, spine * 52)))
        c.setFillColor(colors.HexColor("#f3f0e8"))
        c.drawCentredString(0, -4, TITLE.upper())
        c.restoreState()
    c.save()
    return {"page_count": page_count, "spine_width_in": spine / inch, "cover_width_in": cover_w / inch, "cover_height_in": cover_h / inch}


def chapter_xhtml(chapter: Chapter) -> str:
    parts = [f"<h1>Reclamação n.º {chapter.number}</h1>", f"<h2>{html.escape(chapter.title)}</h2>"]
    if chapter.subtitle:
        parts.append(f"<p class=\"subtitle\">{epub_text(chapter.subtitle)}</p>")
    kind = illustration_kind_for(chapter)
    parts.append(f"<div class=\"chapter-illustration\"><img src=\"images/illustration-{kind}.png\" alt=\"\"/></div>")
    for para in chapter.paragraphs:
        if re.match(r"^[IVX]+\\.", para):
            parts.append(f"<h3>{epub_text(para)}</h3>")
        else:
            parts.append(f"<p>{epub_text(para)}</p>")
    return "\n".join(parts)


def build_epub(preface: list[str], parts: list[Part]) -> None:
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    book_id = f"urn:uuid:{uuid.uuid4()}"
    css = """
body { font-family: Georgia, serif; line-height: 1.45; color: #111; }
h1, h2 { page-break-before: always; break-before: page; }
h1 { font-size: 1.15em; color: #666; margin-top: 2em; }
h2 { font-size: 1.75em; margin: .2em 0 .5em; }
h3 { text-align: left; font-style: italic; margin: 1.5em 0 .8em; }
.chapter-illustration { margin: 1.1em 0 1.3em; text-align: center; }
.chapter-illustration img { width: 62%; max-width: 360px; height: auto; }
.title, .part { text-align: center; page-break-before: always; break-before: page; margin-top: 35%; }
.subtitle { font-style: italic; }
.toc li { margin-bottom: .35em; }
"""
    chapters = [chapter for part in parts for chapter in part.chapters]
    illustration_kinds = sorted({illustration_kind_for(chapter) for chapter in chapters})
    manifest = [
        '<item id="css" href="css/book.css" media-type="text/css"/>',
        '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="preface" href="preface.xhtml" media-type="application/xhtml+xml"/>',
    ]
    for kind in illustration_kinds:
        manifest.append(f'<item id="illustration-{kind}" href="images/illustration-{kind}.png" media-type="image/png"/>')
    spine = ['<itemref idref="title"/>', '<itemref idref="preface"/>']
    files: dict[str, str] = {
        "OEBPS/css/book.css": css,
        "OEBPS/title.xhtml": xhtml_page("title", f"<section class=\"title\"><h1>{TITLE}</h1><p>{SUBTITLE}</p><p>{AUTHOR}</p></section>"),
        "OEBPS/preface.xhtml": xhtml_page("preface", "<h1>Prefácio</h1>" + "".join(f"<p>{epub_text(x)}</p>" for x in preface)),
    }
    nav_items = ["<li><a href=\"preface.xhtml\">Prefácio</a></li>"]
    part_index = 0
    for part in parts:
        part_index += 1
        part_id = f"part-{part_index}"
        part_file = f"{part_id}.xhtml"
        manifest.append(f'<item id="{part_id}" href="{part_file}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{part_id}"/>')
        files[f"OEBPS/{part_file}"] = xhtml_page(part_id, f"<section class=\"part\"><h1>Parte {part.roman}</h1><p>{html.escape(part.title)}</p></section>")
        nav_items.append(f"<li><a href=\"{part_file}\">Parte {part.roman} - {html.escape(part.title)}</a></li>")
        for chapter in part.chapters:
            cid = f"chapter-{chapter.number}"
            href = f"{cid}.xhtml"
            manifest.append(f'<item id="{cid}" href="{href}" media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="{cid}"/>')
            files[f"OEBPS/{href}"] = xhtml_page(cid, chapter_xhtml(chapter))
            nav_items.append(f"<li><a href=\"{href}\">{chapter.number}. {html.escape(chapter.title)}</a></li>")
    files["OEBPS/nav.xhtml"] = xhtml_page("nav", f"<nav epub:type=\"toc\"><h1>Índice</h1><ol class=\"toc\">{''.join(nav_items)}</ol></nav>")
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{book_id}</dc:identifier>
    <dc:title>{html.escape(TITLE)}</dc:title>
    <dc:creator>{html.escape(AUTHOR)}</dc:creator>
    <dc:language>{LANGUAGE}</dc:language>
    <meta property="dcterms:modified">2026-05-21T00:00:00Z</meta>
  </metadata>
  <manifest>{''.join(manifest)}</manifest>
  <spine>{''.join(spine)}</spine>
</package>"""
    files["OEBPS/content.opf"] = opf
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""
    with ZipFile(EPUB_OUT, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=ZIP_DEFLATED)
        z.write(EBOOK_COVER, "OEBPS/images/cover.jpg", compress_type=ZIP_DEFLATED)
        for kind in illustration_kinds:
            z.writestr(f"OEBPS/images/illustration-{kind}.png", epub_illustration_png(kind), compress_type=ZIP_DEFLATED)
        for name, value in files.items():
            z.writestr(name, value, compress_type=ZIP_DEFLATED)


def xhtml_page(identifier: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pt">
<head><title>{html.escape(TITLE)}</title><link rel="stylesheet" href="css/book.css" type="text/css"/></head>
<body id="{identifier}">{body}</body>
</html>"""


def write_metadata(page_count: int, cover_meta: dict[str, float]) -> None:
    metadata = {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "author": AUTHOR,
        "language": "Portuguese",
        "edition": "Nova edição revista",
        "paperback": {
            "trim_size": "6 x 9 in",
            "interior": str(INTERIOR_PDF.relative_to(ROOT)),
            "cover_pdf": str(COVER_PDF.relative_to(ROOT)),
            **cover_meta,
        },
        "ebook": {
            "epub": str(EPUB_OUT.relative_to(ROOT)),
            "cover_jpg": str(EBOOK_COVER.relative_to(ROOT)),
        },
    }
    METADATA_JSON.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    register_fonts()
    EBOOK_DIR.mkdir(parents=True, exist_ok=True)
    PAPERBACK_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    preface, parts = parse_book()
    write_edited_text(preface, parts)
    create_cover_jpg()
    page_count = build_interior(preface, parts)
    cover_meta = build_cover_pdf(page_count)
    build_epub(preface, parts)
    write_metadata(page_count, cover_meta)
    print(f"Generated {TITLE}: {page_count} pages")
    print(INTERIOR_PDF)
    print(COVER_PDF)
    print(EPUB_OUT)
    print(EBOOK_COVER)


if __name__ == "__main__":
    main()
