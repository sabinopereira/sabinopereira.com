#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import create_chess_in_the_block_cover_alt4 as alt4


OUT_DIR = alt4.OUT_DIR
OUT_PNG = OUT_DIR / "chess-in-the-block-cover-alt-4-gold-knight.png"
OUT_JPG = OUT_DIR / "chess-in-the-block-cover-alt-4-gold-knight.jpg"


def draw_knight_outline_gold(img):
    from PIL import Image, ImageDraw, ImageFilter
    import random

    layer = Image.new("RGBA", (alt4.W, alt4.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    try:
        f = alt4.font(alt4.ARIAL, 930)
        glyph = "♞"
    except OSError:
        f = alt4.font(alt4.GEORGIA_BOLD, 850)
        glyph = "N"

    box = d.textbbox((0, 0), glyph, font=f, stroke_width=8)
    x = (alt4.W - (box[2] - box[0])) // 2
    y = 870

    shadow = Image.new("RGBA", (alt4.W, alt4.H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x + 42, y + 50), glyph, font=f, fill=(0, 0, 0, 190), stroke_width=30, stroke_fill=(0, 0, 0, 180))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))

    gold_light = (232, 174, 88, 238)
    gold_dark = (137, 86, 35, 230)
    d.text((x, y), glyph, font=f, fill=(0, 0, 0, 82), stroke_width=36, stroke_fill=gold_light)
    d.text((x + 2, y + 2), glyph, font=f, fill=(0, 0, 0, 210), stroke_width=18, stroke_fill=gold_dark)
    d.text((x, y), glyph, font=f, fill=(0, 0, 0, 222), stroke_width=8, stroke_fill=(2, 2, 2, 238))
    d.text((x - 3, y - 3), glyph, font=f, fill=(0, 0, 0, 0), stroke_width=4, stroke_fill=(255, 226, 156, 88))

    random.seed(1009)
    chip = Image.new("RGBA", (alt4.W, alt4.H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chip)
    for _ in range(105):
        cx = random.randint(390, 1210)
        cy = random.randint(955, 1835)
        cd.line(
            [(cx, cy), (cx + random.randint(20, 90), cy + random.randint(-18, 18))],
            fill=(0, 0, 0, random.randint(85, 160)),
            width=random.randint(3, 8),
        )
    for _ in range(42):
        cx = random.randint(410, 1190)
        cy = random.randint(970, 1810)
        cd.line(
            [(cx, cy), (cx + random.randint(40, 130), cy + random.randint(-22, 22))],
            fill=(255, 220, 145, random.randint(22, 45)),
            width=random.randint(1, 3),
        )
    layer = Image.alpha_composite(layer, chip)
    img.alpha_composite(layer)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = alt4.make_bg()
    alt4.add_board_floor(img)

    y = 160
    y = alt4.add_gold_text(img, "CHESS", y, 308)
    y += 18
    y = alt4.add_gold_text(img, "IN THE", y, 246)
    y += 18
    alt4.add_gold_text(img, "BLOCK", y, 306)

    d = __import__("PIL").ImageDraw.Draw(img)
    sf = alt4.font(alt4.GEORGIA, 36)
    sub = "SURVIVAL  .  SILENCE  .  STRATEGY"
    sb = d.textbbox((0, 0), sub, font=sf)
    sx = (alt4.W - (sb[2] - sb[0])) // 2
    sy = 1018
    d.line([(180, sy + 22), (sx - 50, sy + 22)], fill=(174, 120, 55, 145), width=2)
    d.line([(sx + sb[2] - sb[0] + 50, sy + 22), (alt4.W - 180, sy + 22)], fill=(174, 120, 55, 145), width=2)
    d.text((sx, sy), sub, font=sf, fill=(225, 225, 225, 235))

    draw_knight_outline_gold(img)

    af = alt4.font(alt4.GEORGIA_BOLD, 58)
    author = "SABINO PEREIRA"
    ab = d.textbbox((0, 0), author, font=af)
    d.text(((alt4.W - (ab[2] - ab[0])) // 2, alt4.H - 292), author, font=af, fill=(214, 155, 70, 255))
    tf = alt4.font(alt4.GEORGIA, 33)
    tag = "LEARNING HOW TO MOVE WITHOUT LOSING YOURSELF"
    tb = d.textbbox((0, 0), tag, font=tf)
    d.text(((alt4.W - (tb[2] - tb[0])) // 2, alt4.H - 220), tag, font=tf, fill=(224, 224, 224, 235))

    img = alt4.add_texture(img)
    img.convert("RGB").save(OUT_PNG, "PNG")
    img.convert("RGB").save(OUT_JPG, "JPEG", quality=94, optimize=True)
    print(OUT_PNG)
    print(OUT_JPG)


if __name__ == "__main__":
    main()
