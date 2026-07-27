#!/usr/bin/env python3
"""Render KDP PDFs and create contact sheets for visual quality control."""

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
KDP = ROOT / "amazon-kdp" / "paperback"
INTERIOR = KDP / "interior" / "echoes-of-childhood-paperback-interior-kdp.pdf"
COVER = KDP / "cover" / "echoes-of-childhood-paperback-cover-kdp.pdf"
PREVIEWS = KDP / "previews"
PAGES = PREVIEWS / "interior-pages"
CONTACTS = PREVIEWS / "contact-sheets"


def render_pdf(source, destination, scale):
    destination.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(source))
    for index, page in enumerate(document):
        image = page.render(scale=scale).to_pil().convert("RGB")
        image.save(destination / f"page-{index + 1:02d}.jpg", quality=90)


def make_contacts():
    CONTACTS.mkdir(parents=True, exist_ok=True)
    files = sorted(PAGES.glob("page-*.jpg"))
    cols, rows = 4, 3
    thumb_w, thumb_h, label_h = 204, 308, 22
    for start in range(0, len(files), cols * rows):
        batch = files[start:start + cols * rows]
        sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#d8d0c3")
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(batch):
            image = Image.open(path).convert("RGB")
            image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = (index % cols) * thumb_w + (thumb_w - image.width) // 2
            y = (index // cols) * (thumb_h + label_h)
            sheet.paste(image, (x, y))
            draw.text((x + 5, y + thumb_h + 3), path.stem, fill="#182331")
        sheet.save(CONTACTS / f"contact-{start + 1:02d}-{start + len(batch):02d}.jpg", quality=90)


def main():
    render_pdf(INTERIOR, PAGES, 1.25)
    make_contacts()
    render_pdf(COVER, PREVIEWS / "cover", 2.0)
    print(f"rendered {len(list(PAGES.glob('page-*.jpg')))} interior pages")


if __name__ == "__main__":
    main()
