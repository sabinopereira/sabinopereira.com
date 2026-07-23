from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parents[1] / "output/pdf/um-lugar-a-mesa/Um Lugar à Mesa - Edicao Premium.pdf"
OUTPUT = ROOT.parents[1] / "output/pdf/um-lugar-a-mesa/Um Lugar à Mesa - Edicao Premium Marfim.pdf"
PAPER = HexColor("#F3E8D2")

reader = PdfReader(str(SOURCE))
writer = PdfWriter()

for index, page in enumerate(reader.pages):
    if index == 0:
        writer.add_page(page)
        continue

    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.save()
    buffer.seek(0)
    background = PdfReader(buffer).pages[0]
    background.merge_page(page)
    writer.add_page(background)

writer.add_metadata({
    "/Title": "Um Lugar à Mesa - Edição Premium",
    "/Author": "Sabino Pereira",
    "/Subject": "Edição digital premium em papel marfim #F3E8D2",
})

with OUTPUT.open("wb") as handle:
    writer.write(handle)

print(OUTPUT)
