#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "build" / "pdf-pages"
out = ROOT / "build" / "contact-sheets"
out.mkdir(parents=True, exist_ok=True)

files = sorted(src.glob("page-*.png"))
cols, rows = 4, 3
thumb_w, thumb_h = 216, 324
label_h = 24

for start in range(0, len(files), cols * rows):
    batch = files[start:start + cols * rows]
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#d9d3c7")
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(batch):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w + (thumb_w - image.width) // 2
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.text((x + 6, y + thumb_h + 4), path.stem, fill="#111b2d")
    sheet.save(out / f"contact-{start + 1:02d}-{start + len(batch):02d}.jpg", quality=92)

print(f"created {len(list(out.glob('contact-*.jpg')))} contact sheets")
