from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "built-by-grace-premium-cover-art-v2.png"
OUTPUT = ROOT / "assets" / "built-by-grace-premium-cover-v2.png"
FONT = "/System/Library/Fonts/Supplemental/Didot.ttc"
BASKERVILLE = "/System/Library/Fonts/Supplemental/Baskerville.ttc"

GOLD = (238, 205, 139, 255)
CREAM = (250, 238, 211, 255)
MUTED = (220, 194, 147, 255)
SHADOW = (12, 9, 7, 180)


def tracked_width(draw, text, font, tracking):
    return sum(draw.textlength(char, font=font) for char in text) + tracking * (len(text) - 1)


def centered_tracked(draw, y, text, font, fill, tracking=0, shadow=True):
    width = tracked_width(draw, text, font, tracking)
    x = (992 - width) / 2
    if shadow:
        sx = x + 2
        for char in text:
            draw.text((sx, y + 3), char, font=font, fill=SHADOW)
            sx += draw.textlength(char, font=font) + tracking
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking


def centered(draw, y, text, font, fill, shadow=True):
    box = draw.textbbox((0, 0), text, font=font)
    x = (992 - (box[2] - box[0])) / 2
    if shadow:
        draw.text((x + 2, y + 3), text, font=font, fill=SHADOW)
    draw.text((x, y), text, font=font, fill=fill)


image = Image.open(SOURCE).convert("RGBA")
overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)

# Subtle readability veils that retain the landscape rather than boxing the type.
for y in range(0, 650):
    alpha = int(150 * (1 - y / 650) + 18)
    od.line((0, y, 992, y), fill=(7, 8, 9, alpha))
for y in range(1260, 1586):
    alpha = int(25 + 115 * ((y - 1260) / 326))
    od.line((0, y, 992, y), fill=(6, 6, 7, alpha))

image = Image.alpha_composite(image, overlay)
draw = ImageDraw.Draw(image)

author = ImageFont.truetype(FONT, 36, index=0)
title_large = ImageFont.truetype(FONT, 118, index=1)
title_small = ImageFont.truetype(FONT, 42, index=0)
subtitle = ImageFont.truetype(BASKERVILLE, 25, index=2)
edition = ImageFont.truetype(BASKERVILLE, 20, index=0)

centered_tracked(draw, 62, "SABINO PEREIRA", author, CREAM, tracking=9)
draw.line((250, 132, 742, 132), fill=MUTED, width=1)
centered_tracked(draw, 178, "BUILT", title_large, GOLD, tracking=4)
centered_tracked(draw, 311, "BY", title_small, CREAM, tracking=10)
centered_tracked(draw, 349, "GRACE", title_large, GOLD, tracking=1)

centered(draw, 1410, "A Journey of Prayer, Healing, Love,", subtitle, CREAM)
centered(draw, 1444, "and God in the Center", subtitle, CREAM)
centered_tracked(draw, 1511, "PREMIUM DIGITAL EDITION", edition, MUTED, tracking=4)

image.convert("RGB").save(OUTPUT, quality=96, optimize=True)
print(OUTPUT)
