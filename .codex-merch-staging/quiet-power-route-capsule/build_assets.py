from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, random

OUT = Path(__file__).parent / "exports"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 4500, 5400

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_SERIF = "/System/Library/Fonts/Supplemental/Bodoni 72 Smallcaps Book.ttf"

CREAM = (238, 224, 194, 255)
CORAL = (216, 91, 70, 255)
COBALT = (34, 74, 154, 255)
LAVENDER = (165, 146, 184, 255)
SILVER = (210, 207, 202, 255)

def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def font(path, size):
    return ImageFont.truetype(path, size)

def centered(draw, y, text, fnt, fill, spacing=0):
    if spacing <= 0:
        box = draw.textbbox((0, 0), text, font=fnt)
        x = (W - (box[2] - box[0])) / 2
        draw.text((x, y), text, font=fnt, fill=fill)
        return
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text)-1)
    x = (W-total)/2
    for ch, cw in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += cw + spacing

def line(draw, pts, color, width=26):
    draw.line(pts, fill=color, width=width, joint="curve")

def save(im, name):
    im.save(OUT/name, dpi=(300,300), optimize=True)

def a_front():
    im=canvas(); d=ImageDraw.Draw(im)
    # intersecting routes
    line(d, [(1100,2380),(1650,2250),(2050,1950),(2400,1600),(3100,1370),(3560,1190)], CREAM, 32)
    line(d, [(1100,2920),(1800,2550),(2150,2220),(2420,1710),(2760,1510),(3340,1310)], CREAM, 32)
    line(d, [(1150,1710),(1700,1900),(2200,2000),(2760,2320),(3320,2250),(3600,2150)], CORAL, 38)
    centered(d, 3220, "QUIET POWER", font(FONT_BOLD,250), CREAM, 44)
    save(im,"01-the-route-is-yours-front-dark.png")

def a_back():
    im=canvas(); d=ImageDraw.Draw(im)
    small=font(FONT_BOLD,220); huge=font(FONT_BOLD,950)
    d.text((650,540),"THE",font=small,fill=CREAM)
    centered(d,650,"ROUTE",huge,CREAM)
    d.text((420,1640),"IS",font=small,fill=CREAM)
    centered(d,1680,"YOURS",huge,CREAM)
    line(d,[(650,1450),(1200,1500),(1800,1850),(2500,2120),(3300,2550),(3850,2500)],CORAL,34)
    # intentional handwritten route finish without fake signature
    line(d,[(1550,3730),(1750,3600),(1900,3710),(2100,3560),(2330,3680),(2600,3550),(2900,3660)],CORAL,22)
    centered(d,4050,"MOVE WITH INTENTION",font(FONT_BOLD,150),CREAM,30)
    save(im,"01-the-route-is-yours-back-dark.png")

def b_front():
    im=canvas(); d=ImageDraw.Draw(im)
    line(d,[(1300,2250),(1750,2200),(2200,2020),(2600,1970),(3000,2050),(3400,1950)],CORAL,28)
    centered(d,2500,"WRONG TURNS WELCOME",font(FONT_BOLD,235),CORAL,10)
    save(im,"02-wrong-turns-welcome-front-light.png")

def b_back():
    im=canvas(); d=ImageDraw.Draw(im)
    # abstract transit route network
    line(d,[(600,600),(1800,600),(1800,1350),(2800,1350),(3200,2450),(3950,2850)],COBALT,38)
    line(d,[(1200,1500),(1200,2350),(2250,2350),(2700,1800),(3600,1200),(3600,650)],COBALT,38)
    line(d,[(2250,2350),(2850,3500),(3700,3500),(3700,4250)],COBALT,38)
    line(d,[(3000,2000),(3550,1850)],CORAL,46)
    for x,y,c in [(1200,1500,COBALT),(3600,650,COBALT),(3950,2850,CORAL),(3700,4250,COBALT)]:
        d.ellipse((x-44,y-44,x+44,y+44),outline=c,width=28)
    d.text((500,3000),"NOT",font=font(FONT_BOLD,520),fill=COBALT)
    d.text((500,3480),"LOST.",font=font(FONT_BOLD,520),fill=COBALT)
    d.text((500,4100),"STILL MOVING.",font=font(FONT_BOLD,440),fill=COBALT)
    centered(d,4920,"QUIET POWER  /  MOVE DIFFERENT",font(FONT_BOLD,125),COBALT,8)
    save(im,"02-wrong-turns-welcome-back-light.png")

def brush(draw, x, color, seed):
    rnd=random.Random(seed)
    for _ in range(65):
        yy=rnd.randint(1550,2900); half=rnd.randint(55,130)
        xx=x+rnd.randint(-90,90)
        draw.line((xx-half,yy,xx+half,yy+rnd.randint(-25,25)),fill=color,width=rnd.randint(15,34))

def c_front():
    im=canvas(); d=ImageDraw.Draw(im)
    brush(d,1550,CORAL,1); brush(d,2250,LAVENDER,2); brush(d,2950,SILVER,3)
    centered(d,3300,"QUIET POWER",font(FONT_BOLD,260),CREAM,32)
    save(im,"03-choose-your-signal-front-dark.png")

def c_back():
    im=canvas(); d=ImageDraw.Draw(im)
    cx,cy=2250,2250
    # fingerprint/signal hybrid with deliberate breaks
    for i in range(9):
        rx=420+i*165; ry=650+i*145
        start=195+i*2; end=520-i*3
        box=(cx-rx,cy-ry,cx+rx,cy+ry)
        d.arc(box,start=start,end=end,fill=(CREAM if i%3 else LAVENDER),width=24)
    line(d,[(cx,550),(cx,1750),(cx-220,2050),(cx,2350),(cx,3900)],CORAL,28)
    # subtle waveform
    wave=[]
    for x in range(650,3850,35):
        y=3550 + int(80*math.sin(x/95)) + int(35*math.sin(x/31))
        wave.append((x,y))
    line(d,wave,LAVENDER,16)
    # strong clear type bar over the signal
    d.rounded_rectangle((350,2500,4150,2940),radius=35,fill=(0,0,0,185))
    centered(d,2580,"CHOOSE YOUR SIGNAL",font(FONT_BOLD,315),CREAM,10)
    centered(d,4560,"THE NOISE IS NOT THE MESSAGE",font(FONT_BOLD,170),CREAM,12)
    save(im,"03-choose-your-signal-back-dark.png")

for fn in (a_front,a_back,b_front,b_back,c_front,c_back): fn()
print("generated", len(list(OUT.glob('*.png'))), "assets")
