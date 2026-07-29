#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import sys

source = Path(sys.argv[1])
output = Path(sys.argv[2])
output.mkdir(parents=True, exist_ok=True)

files = sorted(
    source.glob("page-*.png"),
    key=lambda path: int(path.stem.split("-")[-1]),
)
cols, rows = 4, 3
thumb_w, thumb_h = 240, 360
label_h = 24

for start in range(0, len(files), cols * rows):
    batch = files[start:start + cols * rows]
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#d9d3c7")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(batch):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % cols) * thumb_w + (thumb_w - image.width) // 2
        y = (index // cols) * (thumb_h + label_h)
        sheet.paste(image, (x, y))
        draw.text((x + 6, y + thumb_h + 4), path.stem, fill="#111b2d")
    sheet.save(output / f"contact-{start + 1:02d}-{start + len(batch):02d}.jpg", quality=92)

print(f"created {len(list(output.glob('contact-*.jpg')))} contact sheets")
