"""Bouwt het prentenboek 'Opa en het ruimteschip' (Joah en opa) uit de Blender-renders (houten miniatuurwereld).

Formaat zoals de boeken van Daan en Bram: dicht 21 x 21 cm, open 42 x 21 cm.
32 pagina's: voorkant, p. 1-30, achterkant.

    python boek/build.py                 # alles (pagina's, PDF's, bladerboek, artifact)
    python boek/build.py --bron work/proef  # met de previews (snelle versie)
    python boek/build.py --storyboard    # alleen het storyboardblad

Uit:
- tot-voorbij-de-sterren.pdf          bladen van 42 x 21 cm (omslag + 15 dubbele pagina's)
- tot-voorbij-de-sterren-druk.pdf     losse pagina's 21 x 21 cm met 3 mm afloop, voor de drukker
- Tot voorbij de sterren - pagina's (PDF)/   één PDF per pagina (21 x 21 cm)
- Tot voorbij de sterren - pagina's (PNG)/   één PNG per pagina (2480 x 2480, 300 dpi)
- artifact/index.html + artifact/pages/  het bladerboek
- web/                                 hetzelfde bladerboek als losse website
- storyboard.jpg                       alle pagina's op een rij met de tekstplaatsing
"""
import os, sys, json, hashlib, io, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WEB = os.path.join(ROOT, 'web')
ART = os.path.join(ROOT, 'artifact')
FONTS = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
TITLE = 'Opa en het ruimteschip'
SLUG = 'opa-en-het-ruimteschip'
DESC = 'Bladerboek van het houten prentenboek Opa en het ruimteschip: Joah en opa bouwen samen een ruimteschip.'
PX = 2480                                         # 21 cm op 300 dpi
BLEED = 35                                        # 3 mm
N_PAGES = 32

INK = (52, 36, 26)            # warm donkerbruin
CREAM = (253, 249, 240)
YELLOW = (255, 200, 70)
GOLD = (240, 178, 60)
WHITE = (255, 251, 242)


def font(weight, size):
    f = {'body': 'MuseoSansRounded700.otf', 'bold': 'MuseoSansRounded900.otf', 'black': 'MuseoSansRounded1000.otf',
         'light': 'MuseoSansRounded500.otf'}[weight]
    return ImageFont.truetype(os.path.join(FONTS, f), size)


# ------------------------------------------------------------------ indeling
# Elk blad: links + rechts. 'spread' = één render over beide pagina's; anders per pagina een bron.
# Tekst: (tekst, x, y, grootte, stijl, opties) met x/y genormaliseerd over het hele blad (0-1).
B = 96          # leestekst
L_ = dict(anchor='la')
R_ = dict(anchor='ra', align='right')
SHEETS = [
    dict(name='omslag', spread='omslag', left=31, right=0, texts=[
        ('Opa en het', 0.75, 0.2, 200, 'titel', dict(anchor='mm')),
        ('ruimteschip', 0.75, 0.3, 230, 'titel', dict(anchor='mm', fill=YELLOW)),
        ('Opa kan alles maken van hout.\nSamen met Joah bouwt hij\neen ruimteschip.\n\nHet is voor een hele verre reis...',
         0.05, 0.08, 76, 'body', dict(anchor='la', spacing=1.25)),
        ('Voor Joah', 0.05, 0.93, 56, 'klein', dict(anchor='ls')),
    ]),
    dict(name='titelblad', left=('patroon', 'schutblad'), right=('vignet', 'titel', 0.86, 0.14), texts=[
        ('Opa en het', 0.75, 0.1, 170, 'titel_d', dict(anchor='mm')),
        ('ruimteschip', 0.75, 0.18, 190, 'titel_d', dict(anchor='mm', fill=(214, 140, 30))),
    ]),
    dict(name='werkplaats', spread='sp03_werkplaats', texts=[
        ('Dit is Joah.', 0.04, 0.06, B, 'body', L_),
        ('En dit is opa.\nOpa kan alles maken van hout.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='tekening', spread='sp05_tekening', texts=[
        ('‘Zullen we samen iets bouwen?’ vraagt opa.\n‘Iets heel groots. Iets heel bijzonders.’', 0.04, 0.06, B, 'body', L_),
        ('Opa tekent het\nop een groot vel papier.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='zagen', spread='sp07_zagen', texts=[
        ('Eerst zagen.', 0.04, 0.06, B, 'body', L_),
        ('Ritsj, ratsj, ritsj!', 0.27, 0.86, 170, 'klank', dict(anchor='mm', rot=5)),
        ('Joah houdt de plank vast.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='hamer', spread='sp09_hamer', texts=[
        ('Dan timmeren.', 0.04, 0.06, B, 'body', L_),
        ('Tik, tak, tik!', 0.2, 0.2, 180, 'klank', dict(anchor='mm', rot=-6)),
        ('Opa maakt voor Joah\neen eigen hamer.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='onderdelen', spread='sp11_onderdelen', texts=[
        ('Opa weet overal iets op.\nEr komt een motor bij en een vleugel.', 0.04, 0.06, B, 'body', L_),
        ('Het wordt een echt ruimteschip!', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='verven', spread='sp13_verven', texts=[
        ('Joah kiest de kleuren uit:', 0.04, 0.06, B, 'body', L_),
        ('rood, groen, blauw\nen echt goud voor een gele ster.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='klaar', spread='sp15_klaar', texts=[
        ('En dan is het klaar!', 0.04, 0.06, B, 'body', L_),
        ('Het is groot. Het is mooi.\nHet is van opa en Joah samen.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='zoef', spread='sp17_zoef', texts=[
        ('Ze stappen in en\ndoen alsof ze vliegen.', 0.04, 0.06, B, 'body', L_),
        ('‘Drie, twee, één...’', 0.96, 0.06, B, 'body', R_),
        ('ZOEF!', 0.86, 0.8, 230, 'klank', dict(anchor='mm', rot=-7)),
    ]),
    dict(name='stil', spread='sp19_stil', texts=[
        ('Dan wordt opa stil.', 0.04, 0.06, B, 'body', L_),
        ('‘Dit schip is voor een hele verre reis,’\nzegt hij. ‘Ik ga naar de hemel.\nDaar kun jij nog niet naartoe.’',
         0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='houden', spread='sp21_dichtbij', texts=[
        ('‘Mijn lijf is oud en moe.\nIk kom niet meer terug.\nDat is verdrietig.’', 0.04, 0.06, B, 'body', L_),
        ('‘Maar ik blijf altijd\nvan je houden.’', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='afscheid', spread='sp23_afscheid', texts=[
        ('Ze knuffelen heel lang.\nJoah mag de hamer houden.', 0.04, 0.06, B, 'body', L_),
        ('Dan zwaait opa nog één keer.', 0.96, 0.06, B, 'body', R_),
    ]),
    dict(name='vlucht', spread='sp25_vlucht', texts=[
        ('Het schip gaat omhoog,\nhoger en hoger,', 0.04, 0.06, B, 'body', L_),
        ('tot voorbij de sterren.', 0.96, 0.9, B, 'body', dict(anchor='rs', align='right')),
    ]),
    dict(name='raam', spread='sp27_raam', texts=[
        ('Joah mist opa.\nSoms is hij verdrietig,\nen dat mag.', 0.04, 0.06, B, 'body', L_),
        ('Dan kijkt hij omhoog.\nEn houdt zijn hamer goed vast.\nOpa is in de hemel.', 0.96, 0.93, B, 'body', dict(anchor='rs', align='right')),
    ]),
    dict(name='einde', left=('render', 'p29_einde'), right=('patroon', 'schutblad'), texts=[
        ('En als Joah iets bouwt,\ndan weet hij precies hoe het moet.\nWant dat heeft opa hem geleerd.', 0.25, 0.06, 80,
         'body', dict(anchor='ma', align='center')),
        ('Einde', 0.25, 0.95, 140, 'titel', dict(anchor='ms')),
    ]),
]

CHAPTER_TITLES = ['Omslag', 'Titelpagina', 'Dit is Joah', 'De tekening', 'Zagen', 'Een eigen hamer', 'Motor en vleugel',
                  'Verven', 'Klaar!', 'ZOEF!', 'Opa wordt stil', 'Altijd van je houden', 'Afscheid',
                  'Tot voorbij de sterren', 'Joah kijkt omhoog', 'Einde']
TEXTS = [''] * N_PAGES


# ------------------------------------------------------------------ nabewerking
def post(im, bloom=0.22, vign=0.12):
    """Zachte gloed rond heldere lichten en een lichte vignettering."""
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255.0
    lum = a.max(2)
    bright = np.clip((lum - 0.85) / 0.15, 0, 1)[..., None] * a
    b = Image.fromarray((bright * 255).astype(np.uint8))
    r = max(4, im.width // 140)
    glow = np.asarray(b.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0
    glow2 = np.asarray(b.filter(ImageFilter.GaussianBlur(r * 4))).astype(np.float32) / 255.0
    a = 1 - (1 - a) * (1 - np.clip(glow * bloom + glow2 * bloom * 0.8, 0, 1))
    H, W = lum.shape
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    a *= (1 - vign * np.clip(d - 0.35, 0, 1) ** 1.6 / 0.65 ** 1.6)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ------------------------------------------------------------------ tekst
STYLES = {
    'body': dict(font='body', fill=WHITE, stroke=0.09, stroke_fill=(46, 30, 20), shadow=False),
    'body_d': dict(font='body', fill=INK, stroke=0, shadow=False),
    'klank': dict(font='black', fill=YELLOW, stroke=0.11, stroke_fill=INK, shadow=True),
    'titel': dict(font='black', fill=WHITE, stroke=0.1, stroke_fill=INK, shadow=True),
    'sub': dict(font='bold', fill=WHITE, stroke=0.085, stroke_fill=INK, shadow=True),
    'klein': dict(font='light', fill=WHITE, stroke=0.09, stroke_fill=(46, 30, 20), shadow=False),
    'titel_d': dict(font='black', fill=INK, stroke=0, shadow=False),
    'sub_d': dict(font='bold', fill=(120, 96, 80), stroke=0, shadow=False),
}


def draw_text(img, text, x, y, size, style, opt):
    st = dict(STYLES[style])
    st.update({k: v for k, v in opt.items() if k in ('fill', 'stroke', 'stroke_fill', 'shadow')})
    f = font(st['font'], size)
    anchor = opt.get('anchor', 'la')
    align = opt.get('align', 'left' if anchor[0] == 'l' else 'right' if anchor[0] == 'r' else 'center')
    spacing = int(size * (opt.get('spacing', 1.2) - 1)) + 4
    sw = int(round(size * st.get('stroke', 0)))
    tmp = ImageDraw.Draw(Image.new('L', (8, 8)))
    bb = tmp.multiline_textbbox((0, 0), text, font=f, spacing=spacing, align=align, stroke_width=sw)
    pad = int(size * 0.6)
    bb = [int(math.floor(bb[0])), int(math.floor(bb[1])), int(math.ceil(bb[2])), int(math.ceil(bb[3]))]
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.multiline_text((pad - bb[0], pad - bb[1]), text, font=f, fill=tuple(st['fill']) + (255,), spacing=spacing,
                     align=align, stroke_width=sw, stroke_fill=tuple(st.get('stroke_fill') or INK) + (255,))
    if st.get('shadow'):
        alpha = layer.split()[3]
        sh = Image.new('RGBA', layer.size, (10, 12, 20, 0))
        sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(size * 0.09)).point(lambda v: int(v * 0.75)))
        sh2 = Image.new('RGBA', layer.size, (10, 12, 20, 0))
        sh2.putalpha(alpha.filter(ImageFilter.GaussianBlur(size * 0.35)).point(lambda v: int(v * 0.45)))
        base = Image.new('RGBA', layer.size, (0, 0, 0, 0))
        base.alpha_composite(sh2)
        off = Image.new('RGBA', layer.size, (0, 0, 0, 0))
        off.paste(sh, (int(size * 0.03), int(size * 0.05)))
        base.alpha_composite(off)
        base.alpha_composite(layer)
        layer = base
    rot = opt.get('rot', 0)
    if rot:
        layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
    W, H = img.size
    px, py = x * W, y * H
    lw, lh = layer.size
    ax = {'l': pad, 'm': lw / 2, 'r': lw - pad}[anchor[0]]
    ay = {'a': pad, 't': pad, 'm': lh / 2, 's': lh - pad, 'b': lh - pad, 'd': lh - pad}[anchor[1]]
    img.alpha_composite(layer, (int(px - ax), int(py - ay)))


# ------------------------------------------------------------------ pagina's maken
def load(src, name):
    for s in src.split(',') + [os.path.join(ROOT, 'renders')]:
        for ext in ('.png', '.jpg'):
            p = os.path.join(s, name + ext)
            if os.path.exists(p):
                return Image.open(p)
    if '--proef' in sys.argv:
        print('ontbreekt (grijs vlak):', name)
        return Image.new('RGBA', (1260, 630) if name.startswith(('sp', 'omslag')) else (630, 630), (150, 150, 150, 255))
    raise FileNotFoundError(name)


def fit(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def paper(w, h, tone=CREAM):
    a = np.full((h, w, 3), tone, np.float32)
    rng = np.random.default_rng(1)
    n = rng.normal(0, 2.2, (h // 4 + 1, w // 4 + 1))
    n = np.asarray(Image.fromarray(n.astype(np.float32)).resize((w, h), Image.BILINEAR))
    a += n[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def page_source(src, kind, name, w, h, vs=0.8, vy=0.17):
    if kind == 'render':
        return post(fit(load(src, name).convert('RGB'), w, h))
    if kind == 'patroon':
        return fit(load(src, name).convert('RGB'), w, h)
    if kind == 'vignet':
        base = paper(w, h).convert('RGBA')
        v = load(src, name).convert('RGBA')
        v = fit(v, int(w * vs), int(w * vs))
        base.alpha_composite(v, ((w - v.width) // 2, int(h * vy)))
        return base.convert('RGB')
    raise ValueError(kind)


def build_sheet(src, sh, scale=1.0, bleed=BLEED):
    W, H = int((2 * PX + 2 * bleed) * scale), int((PX + 2 * bleed) * scale)
    if 'spread' in sh:
        im = post(fit(load(src, sh['spread']).convert('RGB'), W, H))
    else:
        im = Image.new('RGB', (W, H), CREAM)
        half = W // 2
        for side, key in ((0, 'left'), (1, 'right')):
            kind, name, *extra = sh[key]
            pg = page_source(src, kind, name, half, H, *extra)
            im.paste(pg, (side * half, 0))
    im = im.convert('RGBA')
    inner = im.crop((int(bleed * scale), int(bleed * scale), W - int(bleed * scale), H - int(bleed * scale)))
    ts = PX / 2480
    for (t, x, y, size, style, opt) in sh['texts']:
        draw_text(inner, t, x, y, int(size * scale * ts), style, opt)
    im.paste(inner, (int(bleed * scale), int(bleed * scale)))
    return im.convert('RGB')


def page_number(img, n, side):
    if n in (0, 1, 2, 29, 30, 31):
        return
    d = ImageDraw.Draw(img)
    f = font('light', int(img.width * 0.016))
    x = img.width * (0.05 if side == 0 else 0.95)
    d.text((x, img.height * 0.965), str(n), font=f, fill=(255, 255, 255), anchor='ls' if side == 0 else 'rs',
           stroke_width=max(1, img.width // 900), stroke_fill=(30, 34, 40))


def all_pages(src):
    pages = [None] * N_PAGES
    sheets = []
    for k, sh in enumerate(SHEETS):
        im = build_sheet(src, sh)
        sheets.append(im)
        trim = im.crop((BLEED, BLEED, BLEED + 2 * PX, BLEED + PX))
        L, R = trim.crop((0, 0, PX, PX)), trim.crop((PX, 0, 2 * PX, PX))
        if k == 0:
            pages[31], pages[0] = L, R
        else:
            pages[2 * k - 1], pages[2 * k] = L, R
            page_number(L, 2 * k - 1, 0)
            page_number(R, 2 * k, 1)
        print('blad', k, sh['name'])
    return pages, sheets


# ------------------------------------------------------------------ PDF's
def jpeg_bytes(im, q=90):
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=q, optimize=True, subsampling=0)
    return b.getvalue()


def make_pdfs(pages, sheets):
    import pymupdf
    pt = 72 / 300
    doc = pymupdf.open()
    for k, sh in enumerate(sheets):
        trim = sh.crop((BLEED, BLEED, BLEED + 2 * PX, BLEED + PX))
        if k > 0:
            L, R = pages[2 * k - 1], pages[2 * k]
            trim = Image.new('RGB', (2 * PX, PX))
            trim.paste(L, (0, 0))
            trim.paste(R, (PX, 0))
        pg = doc.new_page(width=2 * PX * pt, height=PX * pt)
        pg.insert_image(pg.rect, stream=jpeg_bytes(trim, 88))
    doc.set_metadata({'title': TITLE, 'author': 'Voor Joah', 'subject': 'Prentenboek',
                      'creator': 'Blender (Cycles) + build.py'})
    doc.save(os.path.join(ROOT, SLUG + '.pdf'), deflate=True, garbage=3)
    doc = pymupdf.open()
    S = PX + 2 * BLEED
    for n in range(N_PAGES):
        if n == 0:
            src = sheets[0].crop((PX + BLEED, 0, 2 * PX + 2 * BLEED, S))
        elif n == 31:
            src = sheets[0].crop((0, 0, PX + BLEED, S))
        else:
            k = (n + 1) // 2
            sh = sheets[k]
            src = sh.crop((0, 0, PX + BLEED, S)) if n % 2 == 1 else sh.crop((PX + BLEED, 0, 2 * PX + 2 * BLEED, S))
        canvas = Image.new('RGB', (S, S))
        if (n % 2 == 1) or n == 31:
            canvas.paste(src, (0, 0))
            strip = src.crop((src.width - BLEED, 0, src.width, S)).transpose(Image.FLIP_LEFT_RIGHT)
            canvas.paste(strip, (src.width, 0))
        else:
            strip = src.crop((0, 0, BLEED, S)).transpose(Image.FLIP_LEFT_RIGHT)
            canvas.paste(strip, (0, 0))
            canvas.paste(src, (BLEED, 0))
        if n not in (0, 31):
            canvas.paste(pages[n], (BLEED, BLEED))
        pg = doc.new_page(width=S * pt, height=S * pt)
        pg.insert_image(pg.rect, stream=jpeg_bytes(canvas, 90))
        try:
            pg.set_trimbox(pymupdf.Rect(BLEED * pt, BLEED * pt, (S - BLEED) * pt, (S - BLEED) * pt))
        except Exception:
            pass
    doc.set_metadata({'title': TITLE + ' - drukbestand (21 x 21 cm, 3 mm afloop)', 'author': 'Voor Joah'})
    doc.save(os.path.join(ROOT, SLUG + '-druk.pdf'), deflate=True, garbage=3)


def page_name(n, ext):
    if n == 0:
        return f'00 voorkant.{ext}'
    if n == N_PAGES - 1:
        return f'{n:02d} achterkant.{ext}'
    return f'{n:02d} pagina {n}.{ext}'


def make_page_files(pages):
    import pymupdf
    pt = 72 / 300
    dpdf = os.path.join(ROOT, TITLE + " - pagina's (PDF)")
    dpng = os.path.join(ROOT, TITLE + " - pagina's (PNG)")
    os.makedirs(dpdf, exist_ok=True)
    os.makedirs(dpng, exist_ok=True)
    for n, im in enumerate(pages):
        im = im.convert('RGB')
        im.save(os.path.join(dpng, page_name(n, 'png')), 'PNG', dpi=(300, 300), compress_level=6)
        doc = pymupdf.open()
        pg = doc.new_page(width=im.width * pt, height=im.height * pt)
        pg.insert_image(pg.rect, stream=jpeg_bytes(im, 92))
        doc.set_metadata({'title': f'{TITLE} - {page_name(n, "pdf")[:-4]}', 'author': 'Voor Joah'})
        doc.save(os.path.join(dpdf, page_name(n, 'pdf')), deflate=True, garbage=3)
    print('losse paginabestanden klaar')


# ------------------------------------------------------------------ bladerboek
def version(folder):
    h = hashlib.sha1()
    for n in sorted(os.listdir(folder)):
        st = os.stat(os.path.join(folder, n))
        h.update(f'{n}{st.st_size}'.encode())
    return h.hexdigest()[:8]


def make_web(pages):
    names = [f'p{i:02d}.jpg' for i in range(N_PAGES)]
    for folder, size, q in (('pages', 1600, 84), ('pages-hd', 2400, 88)):
        os.makedirs(os.path.join(WEB, folder), exist_ok=True)
        for i, im in enumerate(pages):
            im.resize((size, size), Image.LANCZOS).save(os.path.join(WEB, folder, names[i]), 'JPEG', quality=q,
                                                         optimize=True, progressive=True)
    texts = list(TEXTS)
    v = version(os.path.join(WEB, 'pages'))
    body = open(os.path.join(HERE, 'book.template.html'), encoding='utf8').read()
    chapters = [[CHAPTER_TITLES[0], None, 0]] + [[CHAPTER_TITLES[k], 2 * k - 1] for k in range(1, len(SHEETS))] + \
               [['Achterkant', None, N_PAGES - 1]]

    def fill(pages_, hd):
        return (body.replace('/*PAGES*/[]', json.dumps(pages_))
                    .replace('/*HD*/[]', json.dumps(hd))
                    .replace('/*TEXTS*/[]', json.dumps(texts, ensure_ascii=False))
                    .replace('/*CHAPTERS*/[]', json.dumps(chapters, ensure_ascii=False)))

    pp = [f'pages/{n}?v={v}' for n in names]
    hd = [f'pages-hd/{n}?v={v}' for n in names]
    content = fill(pp, hd)
    head = f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{DESC}">
<meta property="og:type" content="book">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="og.jpg">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<style>html{{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px)}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
'''
    title_end = content.index('</title>') + len('</title>')
    title, rest = content[:title_end], content[title_end:]
    rest = rest.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    style_end = rest.index('</style>') + len('</style>')
    html = head + title + rest[:style_end] + '\n</head>\n<body>\n' + rest[style_end:].lstrip() + '\n</body>\n</html>\n'
    open(os.path.join(WEB, 'index.html'), 'w', encoding='utf8').write(html)
    cover = pages[2]
    W = cover.width
    sq = cover.crop((int(W * 0.22), int(W * 0.18), int(W * 0.78), int(W * 0.74)))
    for s_, fn in ((180, 'apple-touch-icon.png'), (48, 'favicon.png')):
        sq.resize((s_, s_), Image.LANCZOS).save(os.path.join(WEB, fn), optimize=True)
    spread = Image.new('RGB', (2 * PX, PX))
    spread.paste(pages[31], (0, 0))
    spread.paste(pages[0], (PX, 0))
    og = Image.new('RGB', (1200, 630), (236, 232, 224))
    og.paste(spread.resize((1130, 565), Image.LANCZOS), (35, 32))
    og.save(os.path.join(WEB, 'og.jpg'), 'JPEG', quality=86, optimize=True)
    os.makedirs(os.path.join(ART, 'pages'), exist_ok=True)
    for n in names:
        Image.open(os.path.join(WEB, 'pages', n)).save(os.path.join(ART, 'pages', n), 'JPEG', quality=82, optimize=True,
                                                        progressive=True)
    open(os.path.join(ART, 'index.html'), 'w', encoding='utf8').write(fill([f'pages/{n}' for n in names], []))
    print('bladerboek klaar, versie', v)


def storyboard(pages, out):
    th = 330
    rows = []
    f = font('bold', 26)
    for k in range(len(SHEETS)):
        if k == 0:
            L, R = pages[31], pages[0]
        else:
            L, R = pages[2 * k - 1], pages[2 * k]
        im = Image.new('RGB', (2 * th + 8, th + 44), (236, 232, 224))
        im.paste(L.resize((th, th), Image.LANCZOS), (4, 40))
        im.paste(R.resize((th, th), Image.LANCZOS), (th + 4, 40))
        lbl = 'omslag (achter | voor)' if k == 0 else f'p. {2 * k - 1}-{2 * k}  {CHAPTER_TITLES[k]}'
        ImageDraw.Draw(im).text((8, 8), lbl, font=f, fill=INK)
        rows.append(im)
    cols = 3
    W = cols * rows[0].width + (cols + 1) * 16
    H = math.ceil(len(rows) / cols) * (rows[0].height + 16) + 16 + 90
    sheet = Image.new('RGB', (W, H), (250, 248, 243))
    d = ImageDraw.Draw(sheet)
    d.text((16, 22), TITLE + ' - storyboard', font=font('black', 44), fill=INK)
    for i, im in enumerate(rows):
        sheet.paste(im, (16 + (i % cols) * (im.width + 16), 90 + (i // cols) * (im.height + 16)))
    sheet.save(out, 'JPEG', quality=88)
    print('storyboard', out)


def main():
    src = os.path.join(ROOT, 'renders')
    if '--bron' in sys.argv:
        src = ','.join(os.path.abspath(x) for x in sys.argv[sys.argv.index('--bron') + 1].split(','))
    global PX, BLEED
    if '--klein' in sys.argv:
        PX, BLEED = 620, 9
    pages, sheets = all_pages(src)
    storyboard(pages, os.path.join(ROOT, 'storyboard.jpg'))
    if '--storyboard' in sys.argv:
        return
    make_pdfs(pages, sheets)
    if '--geen-losse' not in sys.argv:
        make_page_files(pages)
    make_web(pages)


if __name__ == '__main__':
    main()
