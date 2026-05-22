#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "books/chess-in-the-block/cover"
OUT_PNG = OUT_DIR / "chess-in-the-block-cover-draft.png"
OUT_JPG = OUT_DIR / "chess-in-the-block-cover-draft.jpg"

W = 1600
H = 2560


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
GEORGIA = str(FONT_DIR / "Georgia.ttf")
GEORGIA_BOLD = str(FONT_DIR / "Georgia Bold.ttf")
ARIAL_UNICODE = str(FONT_DIR / "Arial Unicode.ttf")


def fit_font(text: str, max_width: int, start: int, min_size: int = 40) -> ImageFont.FreeTypeFont:
    size = start
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while size >= min_size:
        f = font(IMPACT, size)
        box = probe.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
        size -= 4
    return font(IMPACT, min_size)


def add_noise(img: Image.Image, amount: int = 28) -> Image.Image:
    random.seed(8)
    px = Image.new("L", img.size)
    data = [random.randint(0, amount) for _ in range(img.size[0] * img.size[1])]
    px.putdata(data)
    noise = Image.merge("RGBA", (px, px, px, px.point(lambda p: int(p * 0.45))))
    return Image.alpha_composite(img.convert("RGBA"), noise)


def draw_skyline(layer: Image.Image) -> None:
    d = ImageDraw.Draw(layer)
    random.seed(11)
    horizon = int(H * 0.61)
    x = -40
    while x < W + 40:
        bw = random.randint(70, 155)
        bh = random.randint(220, 570)
        y = horizon - bh
        shade = random.randint(20, 48)
        d.rectangle([x, y, x + bw, horizon + 60], fill=(shade, shade, shade + 4, 220))
        for wx in range(x + 15, x + bw - 10, random.randint(22, 34)):
            for wy in range(y + 25, horizon - 8, random.randint(44, 62)):
                if random.random() < 0.28:
                    glow = random.randint(110, 190)
                    d.rounded_rectangle([wx, wy, wx + 9, wy + 14], radius=2, fill=(glow, glow, glow, 110))
        x += bw + random.randint(8, 28)

    # Low fog line.
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for i in range(80):
        y = horizon - 50 + i
        alpha = max(0, 74 - i)
        fd.line([(0, y), (W, y)], fill=(175, 175, 175, alpha), width=2)
    layer.alpha_composite(fog.filter(ImageFilter.GaussianBlur(18)))


def draw_board(layer: Image.Image) -> None:
    d = ImageDraw.Draw(layer)
    top = int(H * 0.66)
    cell_w = W // 8
    cell_h = 105
    for row in range(7):
        y = top + row * cell_h
        for col in range(8):
            x = col * cell_w
            base = 28 if (row + col) % 2 == 0 else 72
            alpha = max(26, 120 - row * 10)
            d.polygon(
                [
                    (x, y),
                    (x + cell_w, y),
                    (x + cell_w + 52, y + cell_h),
                    (x - 52, y + cell_h),
                ],
                fill=(base, base, base, alpha),
            )
    for y in range(top, H, 70):
        d.line([(0, y), (W, y + 80)], fill=(180, 180, 180, 18), width=2)
    d.rectangle([0, top, W, H], fill=(0, 0, 0, 65))


def draw_piece(layer: Image.Image, glyph: str, cx: int, cy: int, size: int, alpha: int = 235, blur: float = 0) -> None:
    piece_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(piece_layer)
    try:
        f = font(ARIAL_UNICODE, size)
    except OSError:
        f = font(GEORGIA_BOLD, size)
    box = d.textbbox((0, 0), glyph, font=f)
    x = cx - (box[2] - box[0]) // 2
    y = cy - (box[3] - box[1]) // 2 - box[1]
    d.text((x + 8, y + 12), glyph, font=f, fill=(255, 255, 255, 35))
    d.text((x, y), glyph, font=f, fill=(4, 4, 4, alpha))
    d.text((x + 2, y + 2), glyph, font=f, fill=(28, 28, 28, min(alpha, 165)))
    if blur:
        piece_layer = piece_layer.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(piece_layer)


def distressed_text_mask(text: str, f: ImageFont.FreeTypeFont) -> Image.Image:
    mask = Image.new("L", (W, 330), 0)
    d = ImageDraw.Draw(mask)
    box = d.textbbox((0, 0), text, font=f)
    x = (W - (box[2] - box[0])) // 2
    d.text((x, 0), text, font=f, fill=255)
    random.seed(len(text) * 31)
    scratch = Image.new("L", mask.size, 0)
    sd = ImageDraw.Draw(scratch)
    for _ in range(1700):
        x = random.randint(0, W - 1)
        y = random.randint(0, mask.size[1] - 1)
        shade = random.randint(24, 105)
        sd.rectangle([x, y, x + random.randint(1, 4), y + random.randint(1, 9)], fill=shade)
    mask = Image.composite(mask.point(lambda p: max(0, p - 95)), mask, scratch)
    return mask


def draw_gold_text(layer: Image.Image, text: str, y: int, size: int) -> int:
    f = fit_font(text, int(W * 0.82), size)
    mask = distressed_text_mask(text, f)
    gold = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    for yy in range(mask.size[1]):
        t = yy / max(1, mask.size[1] - 1)
        r = int(226 - 62 * t)
        g = int(169 - 74 * t)
        b = int(86 - 54 * t)
        gd.line([(0, yy), (W, yy)], fill=(r, g, b, 255))
    gold.putalpha(mask)
    layer.alpha_composite(gold, (0, y))
    return y + f.size


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    bg = Image.new("RGBA", (W, H), (8, 8, 8, 255))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        v = int(8 + 28 * (y / H))
        d.line([(0, y), (W, y)], fill=(v, v, v, 255))

    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_skyline(skyline)
    skyline = skyline.filter(ImageFilter.GaussianBlur(5))
    bg.alpha_composite(skyline)

    board = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_board(board)
    bg.alpha_composite(board)

    draw_piece(bg, "♟", 330, 1825, 510, 205, 4)
    draw_piece(bg, "♞", 645, 1715, 470, 210, 2)
    draw_piece(bg, "♜", 1250, 1765, 470, 210, 3)
    draw_piece(bg, "♚", 820, 1570, 760, 248, 0)

    # Vignette and top shadow for typography.
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for y in range(H):
        top_alpha = max(0, int(205 * (1 - y / (H * 0.46))))
        bottom_alpha = max(0, int(140 * ((y - H * 0.65) / (H * 0.35))))
        alpha = min(230, max(top_alpha, bottom_alpha))
        if alpha:
            vd.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    for x in range(W):
        edge = min(x / (W * 0.23), (W - x) / (W * 0.23), 1)
        alpha = int(155 * (1 - edge))
        if alpha:
            vd.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    bg = Image.alpha_composite(bg, vignette)

    y = 210
    y = draw_gold_text(bg, "CHESS", y, 310)
    # Large chess silhouette between the title lines.
    emblem = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(emblem)
    try:
        ef = font(ARIAL_UNICODE, 390)
    except OSError:
        ef = font(GEORGIA_BOLD, 390)
    glyph = "♚"
    box = ed.textbbox((0, 0), glyph, font=ef)
    ex = (W - (box[2] - box[0])) // 2
    ey = y - 62
    ed.text((ex + 10, ey + 14), glyph, font=ef, fill=(226, 169, 86, 45))
    ed.text((ex, ey), glyph, font=ef, fill=(3, 3, 3, 210))
    ed.text((ex + 4, ey + 4), glyph, font=ef, fill=(226, 169, 86, 78))
    bg.alpha_composite(emblem)
    y += 300
    y = draw_gold_text(bg, "IN THE", y, 265)
    y += 28
    draw_gold_text(bg, "BLOCK", y, 300)

    d = ImageDraw.Draw(bg)
    small = font(GEORGIA, 38)
    author = font(GEORGIA_BOLD, 54)
    gold = (207, 151, 69, 255)
    grey = (184, 184, 184, 230)

    subtitle = "SURVIVAL  .  SILENCE  .  STRATEGY"
    box = d.textbbox((0, 0), subtitle, font=small)
    sx = (W - (box[2] - box[0])) // 2
    sy = 1210
    d.line([(175, sy + 22), (sx - 45, sy + 22)], fill=(156, 102, 45, 170), width=2)
    d.line([(sx + (box[2] - box[0]) + 45, sy + 22), (W - 175, sy + 22)], fill=(156, 102, 45, 170), width=2)
    d.text((sx, sy), subtitle, font=small, fill=grey)

    author_text = "SABINO PEREIRA"
    abox = d.textbbox((0, 0), author_text, font=author)
    d.text(((W - (abox[2] - abox[0])) // 2, H - 270), author_text, font=author, fill=gold)

    tagline = "LEARNING HOW TO MOVE WITHOUT LOSING YOURSELF"
    tfont = font(GEORGIA, 31)
    tbox = d.textbbox((0, 0), tagline, font=tfont)
    d.text(((W - (tbox[2] - tbox[0])) // 2, H - 198), tagline, font=tfont, fill=grey)

    # Subtle scratches.
    random.seed(24)
    for _ in range(80):
        x = random.randint(0, W)
        y = random.randint(0, H)
        length = random.randint(45, 210)
        angle = random.uniform(-0.7, 0.7)
        x2 = int(x + math.cos(angle) * length)
        y2 = int(y + math.sin(angle) * length)
        d.line([(x, y), (x2, y2)], fill=(255, 255, 255, random.randint(8, 25)), width=1)

    bg = add_noise(bg, 30)
    bg.convert("RGB").save(OUT_PNG, "PNG")
    bg.convert("RGB").save(OUT_JPG, "JPEG", quality=94, optimize=True)
    print(OUT_PNG)
    print(OUT_JPG)


if __name__ == "__main__":
    main()
