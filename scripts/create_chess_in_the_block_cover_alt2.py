#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "books/chess-in-the-block/cover"
OUT_PNG = OUT_DIR / "chess-in-the-block-cover-alt-2.png"
OUT_JPG = OUT_DIR / "chess-in-the-block-cover-alt-2.jpg"

W = 1600
H = 2560
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
GEORGIA = str(FONT_DIR / "Georgia.ttf")
GEORGIA_BOLD = str(FONT_DIR / "Georgia Bold.ttf")
ARIAL_UNICODE = str(FONT_DIR / "Arial Unicode.ttf")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_font(text: str, max_width: int, start: int, min_size: int = 50) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    size = start
    while size >= min_size:
        f = font(IMPACT, size)
        box = probe.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
        size -= 4
    return font(IMPACT, min_size)


def add_grain(img: Image.Image) -> Image.Image:
    random.seed(44)
    noise = Image.new("L", img.size)
    noise.putdata([random.randint(0, 34) for _ in range(W * H)])
    alpha = noise.point(lambda p: int(p * 0.34))
    rgba = Image.merge("RGBA", (noise, noise, noise, alpha))
    return Image.alpha_composite(img.convert("RGBA"), rgba)


def draw_background() -> Image.Image:
    img = Image.new("RGBA", (W, H), (8, 8, 8, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        v = int(7 + 22 * y / H)
        d.line([(0, y), (W, y)], fill=(v, v, v, 255))

    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)
    random.seed(19)
    horizon = int(H * 0.59)
    x = -80
    while x < W + 80:
        bw = random.randint(85, 190)
        bh = random.randint(260, 650)
        y = horizon - bh
        shade = random.randint(16, 42)
        sd.rectangle([x, y, x + bw, horizon + 80], fill=(shade, shade, shade + 3, 235))
        for wx in range(x + 18, x + bw - 12, 32):
            for wy in range(y + 24, horizon - 12, 58):
                if random.random() < 0.22:
                    glow = random.randint(105, 180)
                    sd.rounded_rectangle([wx, wy, wx + 10, wy + 16], radius=2, fill=(glow, glow, glow, 115))
        x += bw + random.randint(10, 34)
    skyline = skyline.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(skyline)

    board = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(board)
    top = int(H * 0.64)
    cell_w = 230
    cell_h = 110
    for row in range(8):
        for col in range(9):
            x = col * cell_w - 220
            y = top + row * cell_h
            tone = 28 if (row + col) % 2 == 0 else 76
            alpha = max(18, 112 - row * 11)
            bd.polygon([(x, y), (x + cell_w, y), (x + cell_w + 55, y + cell_h), (x - 55, y + cell_h)], fill=(tone, tone, tone, alpha))
    img.alpha_composite(board.filter(ImageFilter.GaussianBlur(0.5)))

    return img


def draw_photographic_king(img: Image.Image) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = W // 2
    base_y = int(H * 0.82)
    gold_edge = (201, 145, 65, 52)
    black = (5, 5, 5, 242)
    dark = (22, 22, 22, 235)
    mid = (48, 48, 48, 210)
    shine = (210, 210, 210, 42)

    # Shadow.
    d.ellipse([cx - 390, base_y - 70, cx + 390, base_y + 45], fill=(0, 0, 0, 180))

    # Base rings.
    d.rounded_rectangle([cx - 270, base_y - 250, cx + 270, base_y - 160], radius=42, fill=black, outline=gold_edge, width=5)
    d.rounded_rectangle([cx - 230, base_y - 340, cx + 230, base_y - 235], radius=48, fill=dark, outline=(120, 120, 120, 38), width=4)
    d.rounded_rectangle([cx - 175, base_y - 440, cx + 175, base_y - 315], radius=52, fill=black, outline=gold_edge, width=4)

    # Stem.
    d.rounded_rectangle([cx - 108, base_y - 900, cx + 108, base_y - 405], radius=52, fill=black, outline=(100, 100, 100, 36), width=4)
    d.rectangle([cx - 42, base_y - 888, cx - 18, base_y - 430], fill=shine)
    d.rectangle([cx + 58, base_y - 862, cx + 76, base_y - 445], fill=(255, 255, 255, 20))

    # Collar and head.
    d.rounded_rectangle([cx - 210, base_y - 955, cx + 210, base_y - 835], radius=50, fill=dark, outline=gold_edge, width=4)
    d.ellipse([cx - 160, base_y - 1145, cx + 160, base_y - 850], fill=black, outline=(130, 130, 130, 42), width=5)
    d.rectangle([cx - 48, base_y - 1275, cx + 48, base_y - 1085], fill=black, outline=gold_edge, width=4)
    d.rectangle([cx - 132, base_y - 1218, cx + 132, base_y - 1134], fill=black, outline=gold_edge, width=4)

    # Strong side shadows and highlight.
    d.rectangle([cx - 270, base_y - 1265, cx - 110, base_y - 155], fill=(0, 0, 0, 62))
    d.rectangle([cx + 118, base_y - 1240, cx + 270, base_y - 165], fill=(0, 0, 0, 55))
    d.line([(cx - 35, base_y - 1230), (cx - 96, base_y - 190)], fill=(255, 255, 255, 32), width=12)
    d.line([(cx + 82, base_y - 1180), (cx + 156, base_y - 280)], fill=(255, 255, 255, 20), width=7)

    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.2)))


def draw_side_piece(img: Image.Image, glyph: str, cx: int, cy: int, size: int, blur: int) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(ARIAL_UNICODE, size)
    box = d.textbbox((0, 0), glyph, font=f)
    d.text((cx - (box[2] - box[0]) // 2, cy - (box[3] - box[1]) // 2 - box[1]), glyph, font=f, fill=(4, 4, 4, 205))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def text_mask(text: str, f: ImageFont.FreeTypeFont) -> Image.Image:
    mask = Image.new("L", (W, f.size + 44), 0)
    d = ImageDraw.Draw(mask)
    box = d.textbbox((0, 0), text, font=f)
    d.text(((W - (box[2] - box[0])) // 2, -8), text, font=f, fill=255)
    random.seed(f.size + len(text))
    scratches = Image.new("L", mask.size, 0)
    sd = ImageDraw.Draw(scratches)
    for _ in range(1300):
        x = random.randint(0, W - 1)
        y = random.randint(0, mask.size[1] - 1)
        sd.rectangle([x, y, x + random.randint(1, 4), y + random.randint(1, 7)], fill=random.randint(20, 100))
    return Image.composite(mask.point(lambda p: max(0, p - 80)), mask, scratches)


def gold_text(img: Image.Image, text: str, y: int, size: int) -> int:
    f = fit_font(text, int(W * 0.87), size)
    mask = text_mask(text, f)
    gold = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(gold)
    for yy in range(mask.size[1]):
        t = yy / max(1, mask.size[1])
        d.line([(0, yy), (W, yy)], fill=(int(232 - 70 * t), int(173 - 72 * t), int(87 - 50 * t), 255))
    gold.putalpha(mask)
    img.alpha_composite(gold, (0, y))
    return y + int(f.size * 0.82)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = draw_background()
    draw_side_piece(img, "♟", 300, 1830, 560, 5)
    draw_side_piece(img, "♞", 585, 1740, 520, 4)
    draw_side_piece(img, "♜", 1295, 1775, 520, 4)
    draw_photographic_king(img)

    # Dramatic title shadow.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0, 0, W, int(H * 0.50)], fill=(0, 0, 0, 192))
    for x in range(W):
        edge = min(x / (W * 0.22), (W - x) / (W * 0.22), 1)
        alpha = int(140 * (1 - edge))
        if alpha:
            sd.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, shade)

    y = 170
    y = gold_text(img, "CHESS", y, 300)
    y += 18
    y = gold_text(img, "IN THE", y, 245)
    y += 18
    gold_text(img, "BLOCK", y, 300)

    d = ImageDraw.Draw(img)
    small = font(GEORGIA, 34)
    subtitle = "BIG MOVES DON'T NEED NOISE"
    box = d.textbbox((0, 0), subtitle, font=small)
    sx = (W - (box[2] - box[0])) // 2
    sy = 1044
    d.line([(190, sy + 20), (sx - 55, sy + 20)], fill=(174, 120, 55, 150), width=2)
    d.line([(sx + box[2] - box[0] + 55, sy + 20), (W - 190, sy + 20)], fill=(174, 120, 55, 150), width=2)
    d.text((sx, sy), subtitle, font=small, fill=(196, 196, 196, 215))

    author = font(GEORGIA_BOLD, 55)
    author_text = "SABINO PEREIRA"
    ab = d.textbbox((0, 0), author_text, font=author)
    d.text(((W - (ab[2] - ab[0])) // 2, H - 260), author_text, font=author, fill=(212, 154, 68, 255))
    tagline = "SURVIVAL. SILENCE. STRATEGY."
    tf = font(GEORGIA, 32)
    tb = d.textbbox((0, 0), tagline, font=tf)
    d.text(((W - (tb[2] - tb[0])) // 2, H - 190), tagline, font=tf, fill=(205, 205, 205, 225))

    random.seed(55)
    for _ in range(36):
        x = random.randint(0, W)
        y = random.randint(0, H)
        length = random.randint(60, 180)
        angle = random.uniform(-0.65, 0.65)
        d.line([(x, y), (int(x + math.cos(angle) * length), int(y + math.sin(angle) * length))], fill=(255, 255, 255, random.randint(9, 22)), width=1)

    img = add_grain(img)
    img.convert("RGB").save(OUT_PNG, "PNG")
    img.convert("RGB").save(OUT_JPG, "JPEG", quality=94, optimize=True)
    print(OUT_PNG)
    print(OUT_JPG)


if __name__ == "__main__":
    main()
