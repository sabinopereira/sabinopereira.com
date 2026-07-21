from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
COVER = ROOT / "assets" / "built-by-grace-premium-cover-v2.png"
BODY = ROOT / "build" / "rendered-new-cover" / "Built by Grace - Premium Edition.pdf"
TMP_COVER = ROOT / "build" / "premium-cover-full-bleed.pdf"
OUTPUT = ROOT / "dist" / "Built by Grace - Premium Edition.pdf"

PAGE_WIDTH = 6.25 * 72
PAGE_HEIGHT = 10 * 72

cover_pdf = canvas.Canvas(str(TMP_COVER), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
cover_pdf.drawImage(
    str(COVER),
    0,
    0,
    width=PAGE_WIDTH,
    height=PAGE_HEIGHT,
    preserveAspectRatio=True,
    anchor="c",
    mask="auto",
)
cover_pdf.showPage()
cover_pdf.save()

cover_reader = PdfReader(str(TMP_COVER))
body_reader = PdfReader(str(BODY))
writer = PdfWriter()
writer.add_page(cover_reader.pages[0])
for page in body_reader.pages[1:]:
    writer.add_page(page)

writer.add_metadata({
    "/Title": "Built by Grace - Premium Edition",
    "/Author": "Sabino Pereira",
    "/Subject": "A Journey of Prayer, Healing, Love, and God in the Center",
})
with OUTPUT.open("wb") as handle:
    writer.write(handle)

print(OUTPUT)
