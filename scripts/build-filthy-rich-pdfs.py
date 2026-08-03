#!/usr/bin/env python3

from pathlib import Path
from html import escape
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "filthy-rich"
ASSETS = ROOT / "assets" / "filthy-rich"
OUTPUT = ROOT / "output" / "pdf"
PAGE_SIZE = (6 * inch, 9 * inch)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE


def clean_text(value: str) -> str:
    replacements = {
        "—": " - ",
        "–": "-",
        "…": "...",
        "❤️": "<3",
        "❤": "<3",
        "👀": "",
        "😂": ":D",
        "😍": "<3",
        "✓": "[x]",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_episode(path: Path):
    text = path.read_text(encoding="utf-8").strip()
    blocks = [clean_text(block) for block in re.split(r"\n\s*\n", text) if block.strip()]
    if len(blocks) < 4:
        raise ValueError(f"Episode is too short: {path}")
    episode_label = blocks[2]
    match = re.match(r"Episode\s+(\d+)\s+-\s+(.+)", episode_label)
    if not match:
        raise ValueError(f"Unexpected episode heading in {path}: {episode_label}")
    return {
        "number": int(match.group(1)),
        "label": f"Episode {int(match.group(1)):02d}",
        "title": match.group(2),
        "body": blocks[3:],
    }


def make_styles(accent: str):
    red = HexColor(accent)
    ink = HexColor("#181512")
    muted = HexColor("#756b60")
    styles = getSampleStyleSheet()
    return {
        "season_kicker": ParagraphStyle(
            "season_kicker",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            tracking=4,
            textColor=red,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "season_title": ParagraphStyle(
            "season_title",
            parent=styles["Title"],
            fontName="Times-Roman",
            fontSize=31,
            leading=35,
            textColor=ink,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "tagline": ParagraphStyle(
            "tagline",
            parent=styles["Normal"],
            fontName="Times-Italic",
            fontSize=11,
            leading=16,
            textColor=muted,
            alignment=TA_CENTER,
        ),
        "contents_title": ParagraphStyle(
            "contents_title",
            parent=styles["Heading1"],
            fontName="Times-Roman",
            fontSize=22,
            leading=28,
            textColor=ink,
            alignment=TA_CENTER,
            spaceAfter=24,
        ),
        "contents_item": ParagraphStyle(
            "contents_item",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=11.5,
            leading=17,
            textColor=ink,
            leftIndent=18,
            rightIndent=18,
            spaceAfter=7,
        ),
        "episode_kicker": ParagraphStyle(
            "episode_kicker",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            tracking=3,
            textColor=red,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "episode_title": ParagraphStyle(
            "episode_title",
            parent=styles["Heading1"],
            fontName="Times-Roman",
            fontSize=27,
            leading=32,
            textColor=ink,
            alignment=TA_CENTER,
            spaceAfter=30,
        ),
        "body": ParagraphStyle(
            "body",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=10.4,
            leading=15.2,
            textColor=ink,
            alignment=TA_LEFT,
            spaceAfter=6.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "screen": ParagraphStyle(
            "screen",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            textColor=HexColor("#3d3833"),
            alignment=TA_CENTER,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=2,
            spaceAfter=8,
        ),
    }


def looks_like_screen_text(block: str) -> bool:
    if block.startswith("“") or block.startswith('"'):
        return False
    if len(block) > 90:
        return False
    cues = (
        block.isupper()
        or block.startswith("✓")
        or block.startswith("Seen ")
        or block.startswith("Location unavailable")
        or block in {"Not now.", "Decide later.", "Thank you.", "Really good."}
    )
    return cues


class FilthyRichDocTemplate(BaseDocTemplate):
    def __init__(self, filename, season_name, **kwargs):
        super().__init__(filename, pagesize=PAGE_SIZE, **kwargs)
        self.season_name = season_name
        cover_frame = Frame(0, 0, PAGE_WIDTH, PAGE_HEIGHT, leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0, id="cover-frame")
        body_frame = Frame(0.68 * inch, 0.67 * inch, PAGE_WIDTH - 1.36 * inch,
                           PAGE_HEIGHT - 1.34 * inch, id="body-frame")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame]),
            PageTemplate(id="body", frames=[body_frame], onPage=self.draw_footer),
        ])

    def draw_footer(self, canvas, doc):
        page = canvas.getPageNumber()
        if page <= 1:
            return
        canvas.saveState()
        canvas.setStrokeColor(HexColor("#b8afa5"))
        canvas.setLineWidth(0.35)
        canvas.line(0.68 * inch, 0.48 * inch, PAGE_WIDTH - 0.68 * inch, 0.48 * inch)
        canvas.setFillColor(HexColor("#756b60"))
        canvas.setFont("Helvetica", 7)
        canvas.drawString(0.68 * inch, 0.31 * inch, "FILTHY RICH")
        canvas.drawRightString(PAGE_WIDTH - 0.68 * inch, 0.31 * inch, str(page - 1))
        canvas.restoreState()


def build_season(season_number, season_name, cover_path, source_dir, output_path, descriptor):
    episodes = sorted((parse_episode(p) for p in source_dir.glob("episode-*.md")), key=lambda x: x["number"])
    if len(episodes) != 10:
        raise ValueError(f"Expected 10 episodes in {source_dir}, found {len(episodes)}")

    styles = make_styles("#9f241c")
    doc = FilthyRichDocTemplate(
        str(output_path),
        season_name,
        title=f"FILTHY RICH - Season {season_number}: {season_name}",
        author="Reira Bin",
        subject="FILTHY RICH literary series",
    )
    story = []

    story.append(Image(str(cover_path), width=PAGE_WIDTH, height=PAGE_HEIGHT))
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())

    story.append(Spacer(1, 1.15 * inch))
    story.append(Paragraph(f"SEASON {season_number}", styles["season_kicker"]))
    story.append(Paragraph("FILTHY RICH", styles["season_title"]))
    story.append(Paragraph(escape(season_name.upper()), styles["season_kicker"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(escape(descriptor), styles["tagline"]))
    story.append(Spacer(1, 1.25 * inch))
    story.append(Paragraph("A SERIES BY REIRA BIN", styles["season_kicker"]))
    story.append(PageBreak())

    story.append(Spacer(1, 0.42 * inch))
    story.append(Paragraph("Contents", styles["contents_title"]))
    for episode in episodes:
        line = f'<font name="Helvetica-Bold" color="#9f241c">{episode["number"]:02d}</font>&nbsp;&nbsp;&nbsp;{escape(episode["title"])}'
        story.append(Paragraph(line, styles["contents_item"]))

    for episode in episodes:
        story.append(PageBreak())
        story.append(Spacer(1, 0.35 * inch))
        story.append(Paragraph(episode["label"].upper(), styles["episode_kicker"]))
        story.append(Paragraph(escape(episode["title"]), styles["episode_title"]))
        for block in episode["body"]:
            style = styles["screen"] if looks_like_screen_text(block) else styles["body"]
            story.append(Paragraph(escape(block), style))

    OUTPUT.mkdir(parents=True, exist_ok=True)
    doc.build(story)


def main():
    build_season(
        "ONE",
        "The Performance",
        ASSETS / "season-01-the-performance-cover.png",
        CONTENT / "season-01",
        OUTPUT / "filthy-rich-season-01-the-performance.pdf",
        "Too glamorous to check the balance.",
    )
    build_season(
        "TWO",
        "The Relationship",
        ASSETS / "season-02-the-relationship-cover-v2.png",
        CONTENT / "season-02",
        OUTPUT / "filthy-rich-season-02-the-relationship.pdf",
        "A season about how we show love. And who we show it to.",
    )


if __name__ == "__main__":
    main()
