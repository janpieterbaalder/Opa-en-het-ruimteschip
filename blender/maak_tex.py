"""Bedrukte plaatjes voor de voorwerpen (etiket van het lucifersdoosje, opa's bouwtekening).

Draait met gewone Python (Pillow):  python blender/maak_tex.py   -> blender/tex/
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'tex')
os.makedirs(OUT, exist_ok=True)
UF = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
WF = r'C:\Windows\Fonts'


def font(name, size):
    for d in (UF, WF):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def star(d, cx, cy, r, fill, inner=0.45, rot=-90):
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36)
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- etiket lucifersdoosje: "Sterretje"
def maan(d, cx, cy, r, fill, bg):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    d.ellipse([cx - r * 0.55, cy - r * 1.05, cx + r * 1.35, cy + r * 0.75], fill=bg)


def etiket():
    S = 3
    W, H = 1060 * S, 720 * S
    bg = '#1f3a68'
    im = Image.new('RGB', (W, H), '#f1e6cc')
    d = ImageDraw.Draw(im)
    m = 34 * S
    d.rounded_rectangle([m, m, W - m, H - m], radius=24 * S, fill=bg)
    d.rounded_rectangle([m + 16 * S, m + 16 * S, W - m - 16 * S, H - m - 16 * S], radius=16 * S, outline='#e0a33a', width=5 * S)
    rnd = random.Random(4)
    for _ in range(34):
        x, y = rnd.uniform(m + 40 * S, W - m - 40 * S), rnd.uniform(m + 40 * S, H - m - 40 * S)
        if 300 * S < x < 780 * S and 120 * S < y < 610 * S:
            continue
        star(d, x, y, rnd.uniform(5, 12) * S, '#f1e6cc')
    maan(d, 640 * S, 300 * S, 95 * S, '#f1e6cc', bg)
    star(d, 470 * S, 380 * S, 120 * S, '#f3b03c', 0.47, -90 + 8)
    star(d, 470 * S, 380 * S, 70 * S, '#f7c766', 0.47, -90 + 8)
    f1 = font('MuseoSansRounded1000.otf', 96 * S)
    f2 = font('MuseoSansRounded700.otf', 34 * S)
    for txt, f, y, col in (('Sterretje', f1, 140 * S, '#f3b03c'), ('VEILIGHEIDSLUCIFERS', f2, 610 * S, '#f1e6cc')):
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, y - f.size * 0.55), txt, font=f, fill=col)
    im = im.resize((W // S, H // S), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    im.save(os.path.join(OUT, 'etiket.png'))


# ---------------------------------------------------------------- opa's bouwtekening (potlood op bruin papier)
def bouwtekening():
    S = 2
    W, H = 1200 * S, 900 * S
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    pen = (58, 52, 48, 215)
    thin = (58, 52, 48, 120)

    def wob(pts, width=4, col=pen, n=6, amp=2.2):
        out = []
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            for k in range(n):
                t = k / n
                out.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp) * S, y0 + (y1 - y0) * t + rnd.uniform(-amp, amp) * S))
        out.append(pts[-1])
        d.line(out, fill=col, width=int(width * S), joint='curve')

    def ell(cx, cy, rx, ry, width=4, col=pen, a0=0, a1=360):
        pts = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 8)]
        wob(pts, width, col, 2, 1.2)

    # romp: rond kaasdoosje (van opzij)
    hx0, hx1, hy0, hy1 = 220 * S, 700 * S, 470 * S, 640 * S
    wob([(hx0, hy0), (hx1, hy0), (hx1 + 18 * S, (hy0 + hy1) / 2), (hx1, hy1), (hx0, hy1), (hx0 - 18 * S, (hy0 + hy1) / 2), (hx0, hy0)])
    wob([(hx0 - 8 * S, hy0 + 40 * S), (hx1 + 8 * S, hy0 + 40 * S)], 2, thin, 8, 0.8)          # deksel
    for k in range(4):
        ell(hx0 + (90 + k * 100) * S, hy0 + 95 * S, 22 * S, 22 * S, 3)                    # knoopjes als raampjes
        for dx, dy in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
            ell(hx0 + (90 + k * 100 + dx) * S, hy0 + (95 + dy) * S, 2.5 * S, 2.5 * S, 2)
    # hutje: lucifersdoosje met deurtje en schoorsteen (vingerhoed)
    wob([(330 * S, hy0), (330 * S, 330 * S), (560 * S, 330 * S), (560 * S, hy0)])
    wob([(310 * S, 335 * S), (445 * S, 250 * S), (580 * S, 335 * S)])
    wob([(380 * S, hy0), (380 * S, 380 * S), (430 * S, 380 * S), (430 * S, hy0)], 3)
    ell(490 * S, 395 * S, 26 * S, 26 * S, 3)
    wob([(520 * S, 300 * S), (522 * S, 230 * S), (560 * S, 228 * S), (558 * S, 300 * S)], 3)
    for k in range(3):
        ell((545 + k * 18) * S, (205 - k * 36) * S, (12 + k * 6) * S, (9 + k * 4) * S, 2, thin)   # rookwolkjes
    # propeller van ijsstokjes op een klosje
    wob([(445 * S, 250 * S), (445 * S, 170 * S)], 3)
    wob([(420 * S, 170 * S), (470 * S, 170 * S), (470 * S, 150 * S), (420 * S, 150 * S), (420 * S, 170 * S)], 3)
    ell(345 * S, 150 * S, 75 * S, 14 * S, 3)
    ell(545 * S, 150 * S, 75 * S, 14 * S, 3)
    # vleugels: wasknijpers
    for sx, x0 in ((-1, hx0), (1, hx1)):
        wob([(x0, 520 * S), (x0 + sx * 150 * S, 470 * S), (x0 + sx * 165 * S, 495 * S), (x0, 570 * S)])
        ell(x0 + sx * 95 * S, 505 * S, 8 * S, 8 * S, 3)
    # pootjes: knijpers met knoopjes als voetjes
    for x in (280, 460, 640):
        wob([(x * S, hy1), ((x - 15) * S, 760 * S)], 4)
        ell((x - 15) * S, 772 * S, 30 * S, 10 * S, 3)
    # motortje achter: garenklosje
    wob([(hx0 - 18 * S, 520 * S), (120 * S, 505 * S), (120 * S, 605 * S), (hx0 - 18 * S, 590 * S)])
    for k in range(4):
        wob([(125 * S, (522 + k * 20) * S), (hx0 - 22 * S, (526 + k * 18) * S)], 2, thin, 3, 0.6)
    # vlaggetje: labeltje van een theezakje
    wob([(700 * S, 470 * S), (760 * S, 300 * S)], 2)
    wob([(752 * S, 320 * S), (820 * S, 335 * S), (812 * S, 380 * S), (744 * S, 366 * S)], 3)
    f = font('segoepr.ttf', 40 * S)
    fb = font('segoeprb.ttf', 64 * S)
    d.text((780 * S, 60 * S), 'ONS SCHIP', font=fb, fill=pen)
    d.text((800 * S, 160 * S), 'van opa', font=font('segoepr.ttf', 46 * S), fill=pen)
    d.text((800 * S, 225 * S), '& mij', font=font('segoepr.ttf', 46 * S), fill=pen)
    d.text((40 * S, 690 * S), 'kaasdoosje', font=f, fill=pen)
    wob([(160 * S, 690 * S), (240 * S, 620 * S)], 2, thin, 3, 0.6)
    d.text((40 * S, 400 * S), 'knijper', font=f, fill=pen)
    wob([(130 * S, 455 * S), (170 * S, 490 * S)], 2, thin, 3, 0.6)
    d.text((100 * S, 90 * S), 'ijsstokjes', font=f, fill=pen)
    wob([(250 * S, 140 * S), (300 * S, 150 * S)], 2, thin, 3, 0.6)
    d.text((585 * S, 245 * S), 'vingerhoed', font=font('segoepr.ttf', 30 * S), fill=pen)
    # de ster van de jongen, met geel waskrijt
    st = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    star(sd, 1000 * S, 640 * S, 130 * S, (240, 190, 40, 235), 0.5, -90 + 6)
    noise = Image.effect_noise((W, H), 90).convert('L').point(lambda v: 255 if v > 95 else 0)
    a = st.getchannel('A')
    st.putalpha(Image.composite(a, Image.new('L', (W, H), 0), noise))
    im = Image.alpha_composite(im, st)
    im = im.resize((W // S, H // S), Image.LANCZOS)
    im.save(os.path.join(OUT, 'bouwtekening.png'))


def etiket_zij():
    S = 3
    W, H = 1590 * S, 450 * S
    im = Image.new('RGB', (W, H), '#f1e6cc')
    d = ImageDraw.Draw(im)
    m = 22 * S
    d.rectangle([0, m, W, H - m], fill='#1f3a68')
    d.line([(0, m + 18 * S), (W, m + 18 * S)], fill='#e0a33a', width=5 * S)
    d.line([(0, H - m - 18 * S), (W, H - m - 18 * S)], fill='#e0a33a', width=5 * S)
    f = font('MuseoSansRounded1000.otf', 140 * S)
    txt = 'Sterretje'
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, H / 2 - 96 * S), txt, font=f, fill='#f3b03c')
    for x in (150, 300, 1290, 1440):
        star(d, x * S, H / 2, 34 * S, '#f1e6cc')
    im.resize((W // S, H // S), Image.LANCZOS).save(os.path.join(OUT, 'etiket_zij.png'))


if __name__ == '__main__':
    etiket_zij()
    etiket()
    bouwtekening()
    print('klaar ->', OUT)


def postzegel():
    """Postzegel met kartelrand (alfa): een zeilbootje onder een ster."""
    S = 3
    W, H = 440 * S, 520 * S
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, H], fill=(247, 241, 228, 255))
    r = 13 * S
    step = 40 * S
    for x in range(step // 2, W, step):
        for y in (0, H):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(0, 0, 0, 0))
    for y in range(step // 2, H, step):
        for x in (0, W):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(0, 0, 0, 0))
    m = 40 * S
    d.rectangle([m, m, W - m, H - m - 60 * S], fill='#e9b860')
    d.rectangle([m, (H - 60 * S) * 0.62, W - m, H - m - 60 * S], fill='#3b6ea8')
    for k in range(5):
        y = (H - 60 * S) * 0.66 + k * 18 * S
        d.arc([m + 20 * S, y, m + 80 * S, y + 20 * S], 200, 340, fill='#8fb8de', width=3 * S)
        d.arc([W - m - 120 * S, y + 8 * S, W - m - 60 * S, y + 28 * S], 200, 340, fill='#8fb8de', width=3 * S)
    cx = W / 2
    hy = (H - 60 * S) * 0.62
    d.polygon([(cx - 110 * S, hy - 10 * S), (cx + 110 * S, hy - 10 * S), (cx + 80 * S, hy + 40 * S), (cx - 80 * S, hy + 40 * S)], fill='#8b5a36')
    d.polygon([(cx - 5 * S, hy - 20 * S), (cx - 5 * S, hy - 230 * S), (cx - 100 * S, hy - 20 * S)], fill='#f7f1e4')
    d.polygon([(cx + 5 * S, hy - 20 * S), (cx + 5 * S, hy - 190 * S), (cx + 80 * S, hy - 20 * S)], fill='#d8473a')
    d.line([(cx, hy - 10 * S), (cx, hy - 240 * S)], fill='#5a3a22', width=5 * S)
    star(d, W - m - 70 * S, m + 70 * S, 40 * S, '#fff6d8')
    f = font('MuseoSansRounded900.otf', 54 * S)
    d.text((m, H - m - 52 * S), '15', font=f, fill='#3b2a20')
    f2 = font('MuseoSansRounded700.otf', 28 * S)
    d.text((W - m - 150 * S, H - m - 40 * S), 'POST', font=f2, fill='#3b2a20')
    im.resize((W // S, H // S), Image.LANCZOS).save(os.path.join(OUT, 'postzegel.png'))


if __name__ == '__main__':
    postzegel()


def maatlint(fn, W=2400, H=380, bg='#f2c230', cm_px=240, start=1):
    """Gele strook met millimeter-, centimeterstreepjes en cijfers (duimstok, meetlint)."""
    S = 2
    im = Image.new('RGB', (W * S, H * S), bg)
    d = ImageDraw.Draw(im)
    f = font('ariblk.ttf', int(H * S * 0.32))
    mm = cm_px * S / 10
    n = int(W * S / mm) + 1
    for k in range(n):
        x = k * mm
        ln = H * S * (0.42 if k % 10 == 0 else 0.26 if k % 5 == 0 else 0.15)
        d.line([(x, 0), (x, ln)], fill='#1d1a17', width=max(2, S * 2 if k % 10 == 0 else S))
        if k % 10 == 0 and k > 0:
            num = str(start + k // 10 - 1)
            col = '#c8302a' if (start + k // 10 - 1) % 10 == 0 else '#1d1a17'
            d.text((x - 4 * S, H * S * 0.5), num, font=f, fill=col, anchor='rm')
    im.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, fn))


if __name__ == '__main__':
    maatlint('duimstok.png', start=11)
    maatlint('meetlint.png', W=1600, H=380, cm_px=400, start=1)


def speelkaart():
    S = 3
    W, H = 570 * S, 880 * S
    im = Image.new('RGBA', (W, H), (251, 250, 247, 255))
    d = ImageDraw.Draw(im)
    red = (200, 40, 44, 255)

    def hart(cx, cy, r):
        d.ellipse([cx - r, cy - r * 0.9, cx, cy + r * 0.1], fill=red)
        d.ellipse([cx, cy - r * 0.9, cx + r, cy + r * 0.1], fill=red)
        d.polygon([(cx - r * 0.97, cy - r * 0.25), (cx + r * 0.97, cy - r * 0.25), (cx, cy + r * 1.05)], fill=red)
    hart(W / 2, H / 2, 120 * S)
    f = font('MuseoSansRounded900.otf', 90 * S)
    for (x, y, rot) in ((50 * S, 40 * S, 0), (W - 50 * S, H - 40 * S, 180)):
        t = Image.new('RGBA', (160 * S, 220 * S), (0, 0, 0, 0))
        td = ImageDraw.Draw(t)
        td.text((80 * S, 50 * S), 'A', font=f, fill=red, anchor='mm')
        dd = ImageDraw.Draw(t)
        r = 28 * S
        cx, cy = 80 * S, 140 * S
        dd.ellipse([cx - r, cy - r * 0.9, cx, cy + r * 0.1], fill=red)
        dd.ellipse([cx, cy - r * 0.9, cx + r, cy + r * 0.1], fill=red)
        dd.polygon([(cx - r * 0.97, cy - r * 0.25), (cx + r * 0.97, cy - r * 0.25), (cx, cy + r * 1.05)], fill=red)
        t = t.rotate(rot)
        im.alpha_composite(t, (int(x - 80 * S), int(y - 50 * S)) if rot == 0 else (int(x - 80 * S), int(y - 170 * S)))
    im.convert('RGB').resize((W // S, H // S), Image.LANCZOS).save(os.path.join(OUT, 'speelkaart.png'))


if __name__ == '__main__':
    speelkaart()
