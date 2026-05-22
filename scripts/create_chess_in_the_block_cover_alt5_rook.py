#!/usr/bin/env python3
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "books/chess-in-the-block/cover"
OUT_PNG = OUT_DIR / "chess-in-the-block-cover-alt-5-rook.png"
OUT_JPG = OUT_DIR / "chess-in-the-block-cover-alt-5-rook.jpg"

W = 1600
H = 2560
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
GEORGIA = str(FONT_DIR / "Georgia.ttf")
GEORGIA_BOLD = str(FONT_DIR / "Georgia Bold.ttf")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_font(text: str, max_width: int, start: int) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for size in range(start, 52, -4):
        f = font(IMPACT, size)
        box = probe.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
    return font(IMPACT, 52)


def background() -> Image.Image:
    img = Image.new("RGBA", (W, H), (7, 7, 7, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        v = int(6 + 17 * y / H)
        d.line([(0, y), (W, y)], fill=(v, v, v, 255))

    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)
    random.seed(141)
    horizon = int(H * 0.71)
    x = -120
    while x < W + 120:
        bw = random.randint(78, 170)
        bh = random.randint(250, 570)
        y = horizon - bh
        tone = random.randint(18, 45)
        sd.rectangle([x, y, x + bw, horizon + 70], fill=(tone, tone, tone + 3, 218))
        for wx in range(x + 18, x + bw - 10, 34):
            for wy in range(y + 26, horizon - 10, 60):
                if random.random() < 0.20:
                    glow = random.randint(110, 180)
                    sd.rounded_rectangle([wx, wy, wx + 10, wy + 16], radius=2, fill=(glow, glow, glow, 98))
        x += bw + random.randint(8, 26)
    img.alpha_composite(skyline.filter(ImageFilter.GaussianBlur(5)))

    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor)
    top = int(H * 0.82)
    cell_w = 260
    cell_h = 120
    for row in range(5):
        for col in range(9):
            x = col * cell_w - 300
            y = top + row * cell_h
            tone = 23 if (row + col) % 2 == 0 else 57
            alpha = max(18, 104 - row * 13)
            fd.polygon([(x, y), (x + cell_w, y), (x + cell_w + 72, y + cell_h), (x - 72, y + cell_h)], fill=(tone, tone, tone, alpha))
    img.alpha_composite(floor)

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(shade)
    vd.rectangle([0, 0, W, int(H * 0.48)], fill=(0, 0, 0, 190))
    vd.rectangle([0, int(H * 0.84), W, H], fill=(0, 0, 0, 170))
    for x in range(W):
        edge = min(x / (W * 0.23), (W - x) / (W * 0.23), 1)
        alpha = int(160 * (1 - edge))
        if alpha:
            vd.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, shade)


def gold_text(img: Image.Image, text: str, y: int, size: int) -> int:
    f = fit_font(text, int(W * 0.82), size)
    mask = Image.new("L", (W, f.size + 44), 0)
    md = ImageDraw.Draw(mask)
    box = md.textbbox((0, 0), text, font=f)
    md.text(((W - (box[2] - box[0])) // 2, -8), text, font=f, fill=255)
    random.seed(size + len(text))
    distress = Image.new("L", mask.size, 0)
    dd = ImageDraw.Draw(distress)
    for _ in range(1050):
        x = random.randint(0, W - 1)
        yy = random.randint(0, mask.size[1] - 1)
        dd.rectangle([x, yy, x + random.randint(1, 4), yy + random.randint(1, 7)], fill=random.randint(18, 90))
    mask = Image.composite(mask.point(lambda p: max(0, p - 70)), mask, distress)

    gold = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    for yy in range(mask.size[1]):
        t = yy / max(1, mask.size[1] - 1)
        gd.line([(0, yy), (W, yy)], fill=(int(232 - 72 * t), int(174 - 76 * t), int(88 - 48 * t), 255))
    gold.putalpha(mask)
    img.alpha_composite(gold, (0, y))
    return y + int(f.size * 0.82)


def draw_rook_building(img: Image.Image) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = W // 2
    top = 1225
    base = 2145
    outer = [
        (cx - 300, base),
        (cx - 300, 1975),
        (cx - 235, 1900),
        (cx - 205, top + 205),
        (cx - 290, top + 205),
        (cx - 290, top + 35),
        (cx - 185, top + 35),
        (cx - 185, top + 135),
        (cx - 72, top + 135),
        (cx - 72, top + 35),
        (cx + 72, top + 35),
        (cx + 72, top + 135),
        (cx + 185, top + 135),
        (cx + 185, top + 35),
        (cx + 290, top + 35),
        (cx + 290, top + 205),
        (cx + 205, top + 205),
        (cx + 235, 1900),
        (cx + 300, 1975),
        (cx + 300, base),
    ]

    # Shadow and body.
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(x + 32, y + 44) for x, y in outer], fill=(0, 0, 0, 185))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(17)))

    d.polygon(outer, fill=(5, 5, 5, 226))
    d.line(outer + [outer[0]], fill=(235, 225, 205, 215), width=7, joint="curve")
    d.line(outer + [outer[0]], fill=(210, 150, 72, 74), width=16, joint="curve")
    d.line(outer + [outer[0]], fill=(0, 0, 0, 230), width=3, joint="curve")

    # Geometric block/building lines.
    white = (232, 225, 211, 205)
    gold = (216, 157, 74, 126)
    lines = [
        ((cx - 250, 2000), (cx + 250, 2000)),
        ((cx - 255, 1880), (cx + 230, 1880)),
        ((cx - 220, 1740), (cx + 220, 1740)),
        ((cx - 195, 1585), (cx + 195, 1585)),
        ((cx - 160, 1395), (cx + 160, 1395)),
        ((cx, top + 55), (cx, base - 18)),
        ((cx - 210, 1905), (cx + 160, 1395)),
        ((cx + 210, 1905), (cx - 160, 1395)),
        ((cx - 210, 1740), (cx + 235, 2035)),
        ((cx + 220, 1740), (cx - 255, 2035)),
        ((cx - 130, 1585), (cx - 235, 1900)),
        ((cx + 135, 1585), (cx + 235, 1900)),
    ]
    for i, (a, b) in enumerate(lines):
        d.line([a, b], fill=white if i % 3 else gold, width=3)

    # Lit windows.
    d.rounded_rectangle([cx + 72, 1575, cx + 142, 1685], radius=8, fill=(236, 174, 90, 205))
    d.line([(cx + 107, 1575), (cx + 107, 1685)], fill=(25, 18, 13, 165), width=3)
    d.line([(cx + 72, 1630), (cx + 142, 1630)], fill=(25, 18, 13, 165), width=3)
    d.rounded_rectangle([cx - 165, 1370, cx - 75, 1468], radius=6, outline=white, width=3)
    d.rounded_rectangle([cx + 74, 1370, cx + 164, 1468], radius=6, outline=white, width=3)

    # Distressed cuts on the piece.
    random.seed(277)
    for _ in range(65):
        x = random.randint(cx - 285, cx + 285)
        y = random.randint(top + 80, base - 40)
        d.line([(x, y), (x + random.randint(24, 95), y + random.randint(-18, 18))], fill=(0, 0, 0, random.randint(80, 150)), width=random.randint(2, 6))

    img.alpha_composite(layer)


def texture(img: Image.Image) -> Image.Image:
    random.seed(512)
    noise = Image.new("L", (W, H))
    noise.putdata([random.randint(0, 28) for _ in range(W * H)])
    img = Image.alpha_composite(img, Image.merge("RGBA", (noise, noise, noise, noise.point(lambda p: int(p * 0.30)))))
    scratches = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(scratches)
    for _ in range(28):
        x = random.randint(0, W)
        y = random.randint(0, H)
        d.line([(x, y), (x + random.randint(80, 230), y + random.randint(-35, 35))], fill=(255, 255, 255, random.randint(7, 17)), width=1)
    return Image.alpha_composite(img, scratches)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = background()
    y = 150
    y = gold_text(img, "CHESS", y, 308)
    y += 16
    y = gold_text(img, "IN THE", y, 246)
    y += 16
    gold_text(img, "BLOCK", y, 306)

    d = ImageDraw.Draw(img)
    sf = font(GEORGIA, 36)
    sub = "SURVIVAL  .  SILENCE  .  STRATEGY"
    sb = d.textbbox((0, 0), sub, font=sf)
    sx = (W - (sb[2] - sb[0])) // 2
    sy = 1012
    d.line([(180, sy + 22), (sx - 50, sy + 22)], fill=(174, 120, 55, 140), width=2)
    d.line([(sx + sb[2] - sb[0] + 50, sy + 22), (W - 180, sy + 22)], fill=(174, 120, 55, 140), width=2)
    d.text((sx, sy), sub, font=sf, fill=(225, 225, 225, 235))

    draw_rook_building(img)

    af = font(GEORGIA_BOLD, 58)
    author = "SABINO PEREIRA"
    ab = d.textbbox((0, 0), author, font=af)
    d.text(((W - (ab[2] - ab[0])) // 2, H - 292), author, font=af, fill=(214, 155, 70, 255))
    tf = font(GEORGIA, 33)
    tag = "LEARNING HOW TO MOVE WITHOUT LOSING YOURSELF"
    tb = d.textbbox((0, 0), tag, font=tf)
    d.text(((W - (tb[2] - tb[0])) // 2, H - 220), tag, font=tf, fill=(224, 224, 224, 235))

    img = texture(img)
    img.convert("RGB").save(OUT_PNG, "PNG")
    img.convert("RGB").save(OUT_JPG, "JPEG", quality=94, optimize=True)
    print(OUT_PNG)
    print(OUT_JPG)


if __name__ == "__main__":
    main()
