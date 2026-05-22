#!/usr/bin/env python3
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "books/chess-in-the-block/cover"
OUT_PNG = OUT_DIR / "chess-in-the-block-cover-alt-4.png"
OUT_JPG = OUT_DIR / "chess-in-the-block-cover-alt-4.jpg"

W = 1600
H = 2560
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
GEORGIA = str(FONT_DIR / "Georgia.ttf")
GEORGIA_BOLD = str(FONT_DIR / "Georgia Bold.ttf")
ARIAL = str(FONT_DIR / "Arial Unicode.ttf")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_font(text: str, max_width: int, start: int) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for size in range(start, 50, -4):
        f = font(IMPACT, size)
        box = probe.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
    return font(IMPACT, 50)


def make_bg() -> Image.Image:
    img = Image.new("RGBA", (W, H), (6, 6, 6, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        v = int(5 + 18 * y / H)
        d.line([(0, y), (W, y)], fill=(v, v, v, 255))

    random.seed(401)
    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)
    horizon = int(H * 0.68)
    x = -80
    while x < W + 80:
        bw = random.randint(75, 165)
        bh = random.randint(260, 560)
        y = horizon - bh
        tone = random.randint(17, 42)
        sd.rectangle([x, y, x + bw, horizon + 60], fill=(tone, tone, tone, 210))
        for wx in range(x + 17, x + bw - 12, 34):
            for wy in range(y + 26, horizon - 6, 58):
                if random.random() < 0.19:
                    glow = random.randint(112, 180)
                    sd.rounded_rectangle([wx, wy, wx + 9, wy + 15], radius=2, fill=(glow, glow, glow, 95))
        x += bw + random.randint(8, 28)
    img.alpha_composite(skyline.filter(ImageFilter.GaussianBlur(5)))

    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.rectangle([0, 0, W, int(H * 0.45)], fill=(0, 0, 0, 190))
    vd.rectangle([0, int(H * 0.78), W, H], fill=(0, 0, 0, 165))
    for x in range(W):
        edge = min(x / (W * 0.22), (W - x) / (W * 0.22), 1)
        alpha = int(165 * (1 - edge))
        if alpha:
            vd.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, vignette)


def add_gold_text(img: Image.Image, text: str, y: int, size: int) -> int:
    f = fit_font(text, int(W * 0.84), size)
    mask = Image.new("L", (W, f.size + 44), 0)
    md = ImageDraw.Draw(mask)
    box = md.textbbox((0, 0), text, font=f)
    md.text(((W - (box[2] - box[0])) // 2, -8), text, font=f, fill=255)
    random.seed(size + len(text))
    distress = Image.new("L", mask.size, 0)
    dd = ImageDraw.Draw(distress)
    for _ in range(1200):
        x = random.randint(0, W - 1)
        yy = random.randint(0, mask.size[1] - 1)
        dd.rectangle([x, yy, x + random.randint(1, 4), yy + random.randint(1, 7)], fill=random.randint(20, 96))
    mask = Image.composite(mask.point(lambda p: max(0, p - 74)), mask, distress)

    gold = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    for yy in range(mask.size[1]):
        t = yy / max(1, mask.size[1])
        gd.line([(0, yy), (W, yy)], fill=(int(232 - 72 * t), int(174 - 76 * t), int(88 - 48 * t), 255))
    gold.putalpha(mask)
    img.alpha_composite(gold, (0, y))
    return y + int(f.size * 0.82)


def draw_knight_outline(img: Image.Image) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    try:
        f = font(ARIAL, 930)
        glyph = "♞"
    except OSError:
        f = font(GEORGIA_BOLD, 850)
        glyph = "N"

    box = d.textbbox((0, 0), glyph, font=f, stroke_width=8)
    x = (W - (box[2] - box[0])) // 2
    y = 870

    # Shadow gives it weight on the block/city background.
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x + 42, y + 50), glyph, font=f, fill=(0, 0, 0, 180), stroke_width=28, stroke_fill=(0, 0, 0, 170))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))

    # Heavy black body with a rough white contour.
    d.text((x, y), glyph, font=f, fill=(0, 0, 0, 92), stroke_width=34, stroke_fill=(235, 235, 226, 235))
    d.text((x, y), glyph, font=f, fill=(0, 0, 0, 212), stroke_width=13, stroke_fill=(2, 2, 2, 240))
    d.text((x + 8, y + 10), glyph, font=f, fill=(0, 0, 0, 40), stroke_width=3, stroke_fill=(210, 150, 70, 70))

    # Add worn paint: dark chips punched through the white outline and subtle gold grime.
    random.seed(909)
    chip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chip)
    for _ in range(95):
        cx = random.randint(390, 1210)
        cy = random.randint(955, 1835)
        if random.random() < 0.65:
            cd.line(
                [(cx, cy), (cx + random.randint(22, 90), cy + random.randint(-18, 18))],
                fill=(0, 0, 0, random.randint(95, 170)),
                width=random.randint(3, 9),
            )
        else:
            cd.rectangle(
                [cx, cy, cx + random.randint(8, 30), cy + random.randint(4, 16)],
                fill=(0, 0, 0, random.randint(80, 145)),
            )
    for _ in range(42):
        cx = random.randint(410, 1190)
        cy = random.randint(970, 1810)
        cd.line(
            [(cx, cy), (cx + random.randint(40, 130), cy + random.randint(-22, 22))],
            fill=(190, 130, 55, random.randint(25, 54)),
            width=random.randint(1, 3),
        )
    layer = Image.alpha_composite(layer, chip)

    # A few hard urban marker-like strokes around the horse, restrained.
    for _ in range(18):
        sx = random.randint(390, 1210)
        sy = random.randint(990, 1780)
        d.line(
            [(sx, sy), (sx + random.randint(45, 140), sy + random.randint(-28, 28))],
            fill=(240, 240, 230, random.randint(22, 46)),
            width=random.randint(1, 2),
        )

    img.alpha_composite(layer)


def add_board_floor(img: Image.Image) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    top = int(H * 0.76)
    cell_w = 260
    cell_h = 135
    for row in range(6):
        for col in range(9):
            x = col * cell_w - 300
            y = top + row * cell_h
            tone = 24 if (row + col) % 2 == 0 else 60
            alpha = max(18, 102 - row * 14)
            d.polygon([(x, y), (x + cell_w, y), (x + cell_w + 78, y + cell_h), (x - 78, y + cell_h)], fill=(tone, tone, tone, alpha))
    img.alpha_composite(layer)


def add_texture(img: Image.Image) -> Image.Image:
    random.seed(809)
    noise = Image.new("L", (W, H))
    noise.putdata([random.randint(0, 28) for _ in range(W * H)])
    img = Image.alpha_composite(img, Image.merge("RGBA", (noise, noise, noise, noise.point(lambda p: int(p * 0.32)))))
    scratches = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(scratches)
    for _ in range(24):
        x = random.randint(0, W)
        y = random.randint(0, H)
        d.line([(x, y), (x + random.randint(90, 240), y + random.randint(-35, 35))], fill=(255, 255, 255, random.randint(8, 18)), width=1)
    return Image.alpha_composite(img, scratches)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = make_bg()
    add_board_floor(img)

    y = 160
    y = add_gold_text(img, "CHESS", y, 308)
    y += 18
    y = add_gold_text(img, "IN THE", y, 246)
    y += 18
    add_gold_text(img, "BLOCK", y, 306)

    d = ImageDraw.Draw(img)
    sf = font(GEORGIA, 36)
    sub = "SURVIVAL  .  SILENCE  .  STRATEGY"
    sb = d.textbbox((0, 0), sub, font=sf)
    sx = (W - (sb[2] - sb[0])) // 2
    sy = 1018
    d.line([(180, sy + 22), (sx - 50, sy + 22)], fill=(174, 120, 55, 145), width=2)
    d.line([(sx + sb[2] - sb[0] + 50, sy + 22), (W - 180, sy + 22)], fill=(174, 120, 55, 145), width=2)
    d.text((sx, sy), sub, font=sf, fill=(225, 225, 225, 235))

    draw_knight_outline(img)

    af = font(GEORGIA_BOLD, 58)
    author = "SABINO PEREIRA"
    ab = d.textbbox((0, 0), author, font=af)
    d.text(((W - (ab[2] - ab[0])) // 2, H - 292), author, font=af, fill=(214, 155, 70, 255))
    tf = font(GEORGIA, 33)
    tag = "LEARNING HOW TO MOVE WITHOUT LOSING YOURSELF"
    tb = d.textbbox((0, 0), tag, font=tf)
    d.text(((W - (tb[2] - tb[0])) // 2, H - 220), tag, font=tf, fill=(224, 224, 224, 235))

    img = add_texture(img)
    img.convert("RGB").save(OUT_PNG, "PNG")
    img.convert("RGB").save(OUT_JPG, "JPEG", quality=94, optimize=True)
    print(OUT_PNG)
    print(OUT_JPG)


if __name__ == "__main__":
    main()
