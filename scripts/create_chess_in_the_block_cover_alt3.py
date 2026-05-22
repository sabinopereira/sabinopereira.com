#!/usr/bin/env python3
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "books/chess-in-the-block/cover"
OUT_PNG = OUT_DIR / "chess-in-the-block-cover-alt-3.png"
OUT_JPG = OUT_DIR / "chess-in-the-block-cover-alt-3.jpg"

W = 1600
H = 2560
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
GEORGIA = str(FONT_DIR / "Georgia.ttf")
GEORGIA_BOLD = str(FONT_DIR / "Georgia Bold.ttf")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_font(text: str, max_width: int, start: int, min_size: int = 52) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for size in range(start, min_size - 1, -4):
        f = font(IMPACT, size)
        box = probe.textbbox((0, 0), text, font=f)
        if box[2] - box[0] <= max_width:
            return f
    return font(IMPACT, min_size)


def add_texture(img: Image.Image) -> Image.Image:
    random.seed(301)
    noise = Image.new("L", img.size)
    noise.putdata([random.randint(0, 30) for _ in range(W * H)])
    alpha = noise.point(lambda p: int(p * 0.35))
    img = Image.alpha_composite(img.convert("RGBA"), Image.merge("RGBA", (noise, noise, noise, alpha)))
    scratches = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(scratches)
    for _ in range(34):
        x = random.randint(40, W - 40)
        y = random.randint(40, H - 40)
        length = random.randint(90, 240)
        d.line([(x, y), (x + length, y + random.randint(-35, 35))], fill=(255, 255, 255, random.randint(9, 20)), width=1)
    return Image.alpha_composite(img, scratches)


def draw_city(img: Image.Image) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    random.seed(99)
    horizon = int(H * 0.70)
    x = -100
    while x < W + 100:
        bw = random.randint(75, 160)
        bh = random.randint(260, 560)
        y = horizon - bh
        tone = random.randint(18, 42)
        d.rectangle([x, y, x + bw, horizon + 70], fill=(tone, tone, tone, 215))
        for wx in range(x + 18, x + bw - 8, 34):
            for wy in range(y + 26, horizon - 8, 60):
                if random.random() < 0.20:
                    glow = random.randint(115, 180)
                    d.rounded_rectangle([wx, wy, wx + 10, wy + 16], radius=2, fill=(glow, glow, glow, 100))
        x += bw + random.randint(8, 25)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(4)))


def draw_board(img: Image.Image) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    top = int(H * 0.72)
    cell_w = 250
    cell_h = 130
    for row in range(7):
        for col in range(9):
            x = col * cell_w - 260
            y = top + row * cell_h
            tone = 22 if (row + col) % 2 == 0 else 58
            alpha = max(20, 112 - row * 13)
            d.polygon([(x, y), (x + cell_w, y), (x + cell_w + 70, y + cell_h), (x - 70, y + cell_h)], fill=(tone, tone, tone, alpha))
    img.alpha_composite(layer)


def draw_minimal_king(img: Image.Image, cx: int, cy: int, scale: float, alpha: int = 236) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = scale
    black = (3, 3, 3, alpha)
    edge = (210, 150, 70, 58)
    light = (255, 255, 255, 28)

    def r(x: float) -> int:
        return int(x * s)

    # Soft shadow
    d.ellipse([cx - r(330), cy + r(455), cx + r(330), cy + r(560)], fill=(0, 0, 0, 140))

    # Cross and crown top
    d.rounded_rectangle([cx - r(32), cy - r(460), cx + r(32), cy - r(305)], radius=r(8), fill=black, outline=edge, width=max(2, r(3)))
    d.rounded_rectangle([cx - r(105), cy - r(412), cx + r(105), cy - r(355)], radius=r(8), fill=black, outline=edge, width=max(2, r(3)))

    # Head
    d.ellipse([cx - r(145), cy - r(330), cx + r(145), cy - r(80)], fill=black, outline=edge, width=max(2, r(4)))

    # Neck and body
    d.rounded_rectangle([cx - r(95), cy - r(115), cx + r(95), cy + r(255)], radius=r(44), fill=black, outline=edge, width=max(2, r(4)))
    d.rounded_rectangle([cx - r(175), cy + r(175), cx + r(175), cy + r(295)], radius=r(46), fill=black, outline=edge, width=max(2, r(4)))
    d.rounded_rectangle([cx - r(230), cy + r(280), cx + r(230), cy + r(405)], radius=r(52), fill=black, outline=edge, width=max(2, r(4)))
    d.rounded_rectangle([cx - r(280), cy + r(390), cx + r(280), cy + r(492)], radius=r(44), fill=black, outline=edge, width=max(2, r(4)))

    # Highlights
    d.line([(cx - r(62), cy - r(265)), (cx - r(105), cy + r(355))], fill=light, width=max(3, r(8)))
    d.line([(cx + r(86), cy - r(215)), (cx + r(145), cy + r(360))], fill=(255, 255, 255, 18), width=max(2, r(5)))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.35)))


def gold_text(img: Image.Image, text: str, y: int, size: int) -> int:
    f = fit_font(text, int(W * 0.82), size)
    mask = Image.new("L", (W, f.size + 44), 0)
    md = ImageDraw.Draw(mask)
    box = md.textbbox((0, 0), text, font=f)
    md.text(((W - (box[2] - box[0])) // 2, -10), text, font=f, fill=255)
    random.seed(len(text) + size)
    distress = Image.new("L", mask.size, 0)
    dd = ImageDraw.Draw(distress)
    for _ in range(1100):
        x = random.randint(0, W - 1)
        yy = random.randint(0, mask.size[1] - 1)
        dd.rectangle([x, yy, x + random.randint(1, 4), yy + random.randint(1, 7)], fill=random.randint(24, 100))
    mask = Image.composite(mask.point(lambda p: max(0, p - 78)), mask, distress)

    gold = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    for yy in range(mask.size[1]):
        t = yy / max(1, mask.size[1] - 1)
        gd.line([(0, yy), (W, yy)], fill=(int(232 - 76 * t), int(174 - 78 * t), int(88 - 50 * t), 255))
    gold.putalpha(mask)
    img.alpha_composite(gold, (0, y))
    return y + int(f.size * 0.83)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (W, H), (7, 7, 7, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        v = int(6 + 17 * y / H)
        d.line([(0, y), (W, y)], fill=(v, v, v, 255))
    draw_city(img)
    draw_board(img)

    # Minimal pieces: one strong central silhouette, faint side pieces.
    draw_minimal_king(img, W // 2, 1380, 1.28, 238)
    draw_minimal_king(img, 240, 1710, 0.46, 160)
    draw_minimal_king(img, 1345, 1720, 0.50, 150)

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0, 0, W, int(H * 0.58)], fill=(0, 0, 0, 180))
    sd.rectangle([0, int(H * 0.83), W, H], fill=(0, 0, 0, 165))
    for x in range(W):
        edge = min(x / (W * 0.24), (W - x) / (W * 0.24), 1)
        alpha = int(150 * (1 - edge))
        if alpha:
            sd.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, shade)

    y = 190
    y = gold_text(img, "CHESS", y, 308)
    y += 22
    y = gold_text(img, "IN THE", y, 246)
    y += 22
    gold_text(img, "BLOCK", y, 306)

    d = ImageDraw.Draw(img)
    white = (218, 218, 218, 235)
    gold = (214, 155, 70, 255)
    sub = "SURVIVAL  .  SILENCE  .  STRATEGY"
    sf = font(GEORGIA, 36)
    sb = d.textbbox((0, 0), sub, font=sf)
    sx = (W - (sb[2] - sb[0])) // 2
    sy = 1045
    d.line([(180, sy + 22), (sx - 50, sy + 22)], fill=(174, 120, 55, 150), width=2)
    d.line([(sx + sb[2] - sb[0] + 50, sy + 22), (W - 180, sy + 22)], fill=(174, 120, 55, 150), width=2)
    d.text((sx, sy), sub, font=sf, fill=white)

    af = font(GEORGIA_BOLD, 58)
    author = "SABINO PEREIRA"
    ab = d.textbbox((0, 0), author, font=af)
    d.text(((W - (ab[2] - ab[0])) // 2, H - 292), author, font=af, fill=gold)
    tf = font(GEORGIA, 33)
    tag = "LEARNING HOW TO MOVE WITHOUT LOSING YOURSELF"
    tb = d.textbbox((0, 0), tag, font=tf)
    d.text(((W - (tb[2] - tb[0])) // 2, H - 220), tag, font=tf, fill=white)

    img = add_texture(img)
    img.convert("RGB").save(OUT_PNG, "PNG")
    img.convert("RGB").save(OUT_JPG, "JPEG", quality=94, optimize=True)
    print(OUT_PNG)
    print(OUT_JPG)


if __name__ == "__main__":
    main()
