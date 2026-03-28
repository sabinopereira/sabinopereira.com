#!/usr/bin/env python3
"""Generate Quiet Power Workbook 1 as a paginated PDF without third-party libs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap


PAGE_WIDTH = 595.0
PAGE_HEIGHT = 842.0
MARGIN_X = 58.0
TOP_Y = 780.0
BOTTOM_Y = 72.0
TEXT_WIDTH = PAGE_WIDTH - (MARGIN_X * 2)


def pdf_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def normalize(text: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def wrap_text(text: str, width: int) -> list[str]:
    normalized = normalize(" ".join(text.split()))
    return textwrap.wrap(normalized, width=width, break_long_words=False)


@dataclass
class WorkbookPage:
    number: str
    title: str
    trigger: str
    reality: str
    exercise_title: str
    exercise_items: list[str]
    insight: str
    action: str


class PDFBuilder:
    def __init__(self) -> None:
        self.objects: list[bytes] = []
        self.page_ids: list[int] = []
        self.font_ids: dict[str, int] = {}
        self.pages_id: int | None = None
        self.catalog_id: int | None = None

    def add_object(self, payload: bytes) -> int:
        self.objects.append(payload)
        return len(self.objects)

    def add_font(self, key: str, base_font: str) -> None:
        obj_id = self.add_object(
            f"<< /Type /Font /Subtype /Type1 /BaseFont /{base_font} >>".encode("latin-1")
        )
        self.font_ids[key] = obj_id

    def begin(self) -> None:
        self.add_font("F1", "Helvetica")
        self.add_font("F2", "Helvetica-Bold")
        self.add_font("F3", "Times-Roman")

    def add_page(self, stream: str) -> None:
        stream_bytes = stream.encode("latin-1")
        content_id = self.add_object(
            b"<< /Length %d >>\nstream\n" % len(stream_bytes)
            + stream_bytes
            + b"\nendstream"
        )
        font_map = " ".join(
            f"/{name} {obj_id} 0 R" for name, obj_id in self.font_ids.items()
        )
        page_payload = (
            "<< /Type /Page /Parent PAGES_ID 0 R /MediaBox [0 0 %.0f %.0f] "
            "/Resources << /Font << %s >> >> /Contents %d 0 R >>"
        ) % (PAGE_WIDTH, PAGE_HEIGHT, font_map, content_id)
        page_id = self.add_object(page_payload.encode("latin-1"))
        self.page_ids.append(page_id)

    def finalize(self) -> bytes:
        kids = " ".join(f"{pid} 0 R" for pid in self.page_ids)
        self.pages_id = self.add_object(
            f"<< /Type /Pages /Count {len(self.page_ids)} /Kids [{kids}] >>".encode("latin-1")
        )
        self.catalog_id = self.add_object(
            f"<< /Type /Catalog /Pages {self.pages_id} 0 R >>".encode("latin-1")
        )

        patched_objects: list[bytes] = []
        for obj in self.objects:
            if b"PAGES_ID" in obj:
                obj = obj.replace(b"PAGES_ID", str(self.pages_id).encode("ascii"))
            patched_objects.append(obj)

        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(patched_objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode("ascii"))
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")

        xref_pos = len(pdf)
        pdf.extend(f"xref\n0 {len(patched_objects) + 1}\n".encode("ascii"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        pdf.extend(
            (
                "trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(patched_objects) + 1, self.catalog_id, xref_pos)
            ).encode("ascii")
        )
        return bytes(pdf)


class Canvas:
    def __init__(self) -> None:
        self.ops: list[str] = []

    def text(self, x: float, y: float, text: str, font: str = "F1", size: int = 12) -> None:
        safe = pdf_escape(normalize(text))
        self.ops.append(f"BT /{font} {size} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({safe}) Tj ET")

    def multi_text(
        self,
        x: float,
        y: float,
        text: str,
        width_chars: int,
        font: str = "F1",
        size: int = 12,
        leading: int = 16,
    ) -> float:
        current_y = y
        for line in wrap_text(text, width_chars):
            self.text(x, current_y, line, font=font, size=size)
            current_y -= leading
        return current_y

    def line(self, x1: float, y1: float, x2: float, y2: float, width: float = 1.0) -> None:
        self.ops.append(f"{width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def rect(self, x: float, y: float, w: float, h: float, fill_rgb: tuple[float, float, float] | None = None, stroke: bool = False) -> None:
        commands: list[str] = []
        if fill_rgb is not None:
            r, g, b = fill_rgb
            commands.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
        commands.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re")
        if fill_rgb is not None and stroke:
            commands.append("B")
        elif fill_rgb is not None:
            commands.append("f")
        else:
            commands.append("S")
        self.ops.append(" ".join(commands))

    def stream(self) -> str:
        return "\n".join(self.ops)


WORKBOOK_PAGES = [
    WorkbookPage(
        "01",
        "Attention Is Under Attack",
        "You don't lack time. You lack control of attention.",
        "Your attention is constantly being pulled - notifications, people, habits.",
        "Attention Leak Scan",
        [
            "List 5 moments today where you lost focus.",
            "What triggered each one?",
            "Was it necessary? (Yes / No)",
        ],
        "Who controls your attention right now?",
        "Turn off all non-essential notifications for 24h.",
    ),
    WorkbookPage(
        "02",
        "Noise Looks Like Work",
        "Busy does not mean productive.",
        "Most people fill their day to avoid doing what actually matters.",
        "Noise vs Value",
        [
            "List your last 10 tasks.",
            "Mark N (Noise).",
            "Mark V (Value).",
        ],
        'What are you calling "work" that is actually avoidance?',
        'Remove 1 "noise task" tomorrow.',
    ),
    WorkbookPage(
        "03",
        "Reactivity Is a Trap",
        "Your first reaction is rarely your best move.",
        "Instant responses feel efficient, but reduce your control.",
        "Reaction Log",
        [
            "Recall 3 recent reactions.",
            "What triggered them?",
            "What would a delayed response look like?",
        ],
        "How much control do you really have in the moment?",
        "Delay your next response by 10 seconds.",
    ),
    WorkbookPage(
        "04",
        "Fragmentation Is the Real Enemy",
        "You are not tired. You are fragmented.",
        "Switching tasks destroys focus more than hard work.",
        "Fragmentation Map",
        [
            "Track your last hour.",
            "Count how many times you switched tasks.",
        ],
        "How often do you actually stay with one thing?",
        "Block 30 minutes for uninterrupted work.",
    ),
    WorkbookPage(
        "05",
        "Your Day Is Not Yours",
        "If you don't control your day, someone else will.",
        "Most schedules are reactive, not intentional.",
        "Control Audit",
        [
            "Who dictated your last 3 actions?",
            "You or external demands?",
        ],
        "Where did you give away control today?",
        "Start tomorrow with 1 intentional task.",
    ),
    WorkbookPage(
        "06",
        "Emotions Drive Decisions",
        "Most decisions are emotional, not logical.",
        "Stress and urgency lead to poor decisions.",
        "Emotional Trigger Scan",
        [
            "What stressed you today?",
            "What decision came from that?",
        ],
        "Do you decide - or react?",
        'Pause before your next decision. Ask: "Is this emotional?"',
    ),
    WorkbookPage(
        "07",
        "Urgency Is Often Fake",
        "Not everything that feels urgent matters.",
        "Urgency is often imposed, not real.",
        "Urgency Filter",
        [
            'List 5 "urgent" things today.',
            "Did they truly matter? (Yes / No)",
        ],
        "Who benefits from your urgency?",
        'Delay 1 "urgent" task by 1 hour.',
    ),
    WorkbookPage(
        "08",
        "Distraction Is a Choice",
        "Distraction is often a choice.",
        "You use distraction to avoid discomfort.",
        "Distraction Check",
        [
            "What did you avoid today?",
            "What did you replace it with?",
        ],
        "What are you avoiding right now?",
        "Do the avoided task first tomorrow.",
    ),
    WorkbookPage(
        "09",
        "Input Overload",
        "Too much information kills clarity.",
        "Constant input blocks independent thinking.",
        "Input Audit",
        [
            "How many hours of content did you consume today?",
            "Did it create value?",
        ],
        "Are you thinking - or just consuming?",
        "Consume nothing for 2 hours tomorrow.",
    ),
    WorkbookPage(
        "10",
        "Awareness Is the First Power",
        "You cannot control what you don't see.",
        "Most people operate on autopilot.",
        "Pattern Recognition",
        [
            "What pattern repeats in your days?",
            "Where do you lose control most?",
        ],
        "What is your biggest hidden weakness right now?",
        "Write 1 pattern you will break tomorrow.",
    ),
]


def add_cover(builder: PDFBuilder) -> None:
    c = Canvas()
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill_rgb=(0.95, 0.93, 0.89))
    c.rect(42, 42, PAGE_WIDTH - 84, PAGE_HEIGHT - 84, fill_rgb=(0.99, 0.985, 0.97))
    c.line(82, 635, PAGE_WIDTH - 82, 635, width=1.4)
    c.text(82, 710, "QUIET POWER", font="F2", size=18)
    c.text(82, 675, "REACTION", font="F2", size=34)
    c.multi_text(82, 634, "How the world hits you", width_chars=28, font="F3", size=18, leading=22)
    c.text(82, 560, "Workbook 1", font="F1", size=14)
    c.multi_text(
        82,
        486,
        "A focused workbook for noticing how attention, urgency, emotion, and distraction shape your days.",
        width_chars=42,
        font="F1",
        size=13,
        leading=18,
    )
    c.text(82, 128, "Sabino Pereira", font="F2", size=14)
    c.text(PAGE_WIDTH - 180, 128, "quietpower system", font="F1", size=10)
    builder.add_page(c.stream())


def add_intro_page(builder: PDFBuilder) -> None:
    c = Canvas()
    c.text(MARGIN_X, TOP_Y, "Introduction", font="F2", size=24)
    y = TOP_Y - 48
    intro_lines = [
        "This is not a book.",
        "This is a system.",
        "",
        "Most people don't lack intelligence.",
        "They lack control.",
        "",
        "They react too fast, absorb too much, and lose direction without noticing.",
        "",
        "This workbook is designed to make that visible.",
        "",
        "No theory.",
        "Just awareness.",
    ]
    for entry in intro_lines:
        if not entry:
            y -= 18
            continue
        y = c.multi_text(MARGIN_X, y, entry, width_chars=56, font="F3", size=16, leading=22) - 2
    c.line(MARGIN_X, 100, PAGE_WIDTH - MARGIN_X, 100)
    c.text(MARGIN_X, 78, "Quiet Power Workbook 1", font="F1", size=10)
    builder.add_page(c.stream())


def add_usage_page(builder: PDFBuilder) -> None:
    c = Canvas()
    c.text(MARGIN_X, TOP_Y, "How to Use This Workbook", font="F2", size=24)
    tips = [
        "One page per day.",
        "Write, don't just read.",
        "Be honest - no performance.",
        "Apply immediately.",
    ]
    y = TOP_Y - 56
    for tip in tips:
        c.text(MARGIN_X, y, tip, font="F3", size=16)
        y -= 34
    y -= 10
    y = c.multi_text(MARGIN_X, y, "This is not about finishing fast. It's about seeing clearly.", width_chars=54, font="F1", size=14, leading=20)
    y -= 20
    y = c.multi_text(MARGIN_X, y, "If you rush, you miss the point. If you reflect, you gain control.", width_chars=54, font="F1", size=14, leading=20)
    c.line(MARGIN_X, 160, PAGE_WIDTH - MARGIN_X, 160)
    c.text(MARGIN_X, 134, "Use this workbook like a daily control drill.", font="F2", size=12)
    c.text(MARGIN_X, 78, "Write slowly. Notice what lands.", font="F1", size=10)
    builder.add_page(c.stream())


def add_level_page(builder: PDFBuilder) -> None:
    c = Canvas()
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill_rgb=(0.09, 0.10, 0.11))
    c.text(78, 620, "LEVEL 1", font="F1", size=14)
    c.text(78, 570, "REACTION", font="F2", size=42)
    c.line(78, 540, 280, 540, width=1.3)
    c.multi_text(78, 500, "How the world hits you", width_chars=28, font="F3", size=20, leading=24)
    c.text(78, 120, "Awareness before control.", font="F1", size=12)
    builder.add_page(c.stream())


def add_workbook_page(builder: PDFBuilder, page: WorkbookPage) -> None:
    c = Canvas()
    c.text(MARGIN_X, TOP_Y, f"PAGE {page.number}", font="F1", size=10)
    c.text(MARGIN_X, TOP_Y - 26, page.title.upper(), font="F2", size=22)
    c.line(MARGIN_X, TOP_Y - 40, PAGE_WIDTH - MARGIN_X, TOP_Y - 40)

    y = TOP_Y - 88
    c.text(MARGIN_X, y, "Trigger", font="F2", size=12)
    y = c.multi_text(MARGIN_X, y - 24, page.trigger, width_chars=58, font="F3", size=14, leading=18) - 14

    c.text(MARGIN_X, y, "Reality Check", font="F2", size=12)
    y = c.multi_text(MARGIN_X, y - 24, page.reality, width_chars=58, font="F1", size=13, leading=18) - 18

    c.text(MARGIN_X, y, f"Exercise - {page.exercise_title}", font="F2", size=12)
    y -= 26
    for item in page.exercise_items:
        y = c.multi_text(MARGIN_X + 16, y, f"- {item}", width_chars=54, font="F1", size=13, leading=17) - 8

    y -= 4
    line_count = 5 if len(page.exercise_items) < 3 else 4
    for _ in range(line_count):
        c.line(MARGIN_X, y, PAGE_WIDTH - MARGIN_X, y, width=0.7)
        y -= 28

    y -= 4
    c.text(MARGIN_X, y, "Insight Lock", font="F2", size=12)
    y = c.multi_text(MARGIN_X, y - 24, page.insight, width_chars=58, font="F3", size=14, leading=18) - 10
    c.line(MARGIN_X, y - 6, PAGE_WIDTH - MARGIN_X, y - 6, width=0.7)
    y -= 36

    c.text(MARGIN_X, y, "Action", font="F2", size=12)
    c.multi_text(MARGIN_X, y - 24, page.action, width_chars=58, font="F1", size=13, leading=18)
    c.text(PAGE_WIDTH - 94, 48, page.number, font="F1", size=10)
    builder.add_page(c.stream())


def add_shift_page(builder: PDFBuilder) -> None:
    c = Canvas()
    c.text(MARGIN_X, TOP_Y, "The Shift", font="F2", size=24)
    y = TOP_Y - 56
    paragraphs = [
        "Most people stay reactive.",
        "They move fast, respond instantly, and mistake activity for control.",
        "You now see the pattern.",
        "Awareness is the first step. But awareness alone changes nothing.",
        "Control requires selection.",
        "What you allow in. What you ignore. What you delay.",
        "This is where control begins.",
    ]
    for paragraph in paragraphs:
        y = c.multi_text(MARGIN_X, y, paragraph, width_chars=58, font="F3", size=15, leading=22) - 10
    c.line(MARGIN_X, 178, PAGE_WIDTH - MARGIN_X, 178, width=1.0)
    c.text(MARGIN_X, 148, "Continue", font="F2", size=14)
    c.multi_text(MARGIN_X, 122, "Workbook 2 - Filter\nHow you filter the noise", width_chars=38, font="F1", size=12, leading=18)
    builder.add_page(c.stream())


def main() -> None:
    output_dir = Path("downloads")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "quiet-power-workbook-1.pdf"

    builder = PDFBuilder()
    builder.begin()
    add_cover(builder)
    add_intro_page(builder)
    add_usage_page(builder)
    add_level_page(builder)
    for page in WORKBOOK_PAGES:
        add_workbook_page(builder, page)
    add_shift_page(builder)

    pdf_path.write_bytes(builder.finalize())
    print(pdf_path)


if __name__ == "__main__":
    main()
