"""Alledaagse voorwerpen op ware grootte (cm) die in de miniatuurwereld iets anders worden.

ijsstokje -> vloerplank, lucifersdoosje -> werkbank, potloodstompje -> tafelpoot, dobbelsteen ->
opstapje, garenklosje -> kruk/kabelhaspel, eikeldopje -> lampenkap of kopje, kroonkurk -> verfpot,
punaise -> plankdrager, kraal op een tandenstoker -> hamertje, enzovoort.
"""
import bpy, math, os
import numpy as np
from mathutils import Vector, Matrix, Euler
from . import core as K, hout as H

_T = {}


def _tpl(key, fn):
    """Sjabloon-mesh één keer bouwen (verborgen), daarna gekoppelde kopieën maken."""
    if key not in _T:
        ob = fn()
        ob.hide_render = True
        ob.hide_viewport = True
        _T[key] = ob
    return _T[key]


# ---------------------------------------------------------------- ijsstokje
def ijsstokje_tpl(L=11.4, W=1.0, T=0.2):
    def mk():
        return H.prism('ijsstokje_tpl', H.stadium_pts(L, W, 12), T, H.wood('berk', 'X', var=0.14, key='ijsstokje'),
                       bev=0.045, seg=2, angle=30)
    return _tpl(('ijs', L, W, T), mk)


def ijsstokje(name, loc, rot=(0, 0, 0), parent=None, **kw):
    return H.instance(ijsstokje_tpl(**kw), name, loc, rot, parent=parent)


def vloer(x0, x1, y0, y1, z=0.0, seed=3, L=11.4, W=1.0, gap=0.035):
    """Vloer van ijsstokjes: rijen langs x, verspringende naden."""
    rnd = np.random.default_rng(seed)
    z = z - 0.2   # bovenkant van de ijsstokjes op de gevraagde hoogte
    base = H.box('ondervloer', x1 - x0 + 4, y1 - y0 + 4, 0.2, H.wood('noten', 'X', key='ondervloer'),
                 loc=((x0 + x1) / 2, (y0 + y1) / 2, z - 0.2), bev=0.0, base=True)
    n = 0
    y = y0
    while y < y1:
        x = x0 - rnd.uniform(0, L)
        while x < x1:
            ln = L
            c = x + ln / 2
            ijsstokje(f'stokje_{n}', (c, y + W / 2, z + rnd.uniform(-0.008, 0.008)),
                      (rnd.uniform(-0.006, 0.006), rnd.uniform(-0.006, 0.006), rnd.uniform(-0.004, 0.004)))
            n += 1
            x += ln + gap
        y += W + gap
    return base


# ---------------------------------------------------------------- lucifersdoosje (gewoon kartonnen doosje)
def lucifersdoosje(name, loc=(0, 0, 0), rot=0.0, L=5.3, W=3.6, Hh=1.5, open_=1.6, parent=None, label=True,
                   contents=True, rand='#1f3a68'):
    """Standaard lucifersdoosje: kartonnen huls met etiket bovenop, bruine strijkvlakken op beide lange
    zijkanten (met een smal randje in de kleur van het etiket) en een wit kartonnen laatje."""
    root = K.empty(name, loc, (0, 0, math.radians(rot)), parent=parent)
    t = 0.04
    karton = H.paper('#d9d2c4', rough=0.85, key='karton_grijs', fiber=0.08)
    laakarton = H.paper('#efeae0', rough=0.85, key='karton_wit', fiber=0.06)
    strijk = _strijkvlak(rand=rand)
    lab = H.paper('#efe4cb', os.path.join(H.TEX, 'etiket.png'), rough=0.7, key='etiket', src='GEN') if label else karton
    # huls (open aan de kopse kanten)
    H.box(name + '_boven', L, W, t, lab, loc=(0, 0, Hh - t / 2), bev=0.012, parent=root)
    H.box(name + '_onder', L, W, t, karton, loc=(0, 0, t / 2), bev=0.012, parent=root)
    for sy in (-1, 1):
        H.box(name + f'_zij{sy}', L, t, Hh, strijk, loc=(0, sy * (W / 2 - t / 2), Hh / 2), bev=0.012, parent=root)
    # laatje
    lw, lh, lt = W - 2 * t - 0.03, Hh - 2 * t - 0.03, 0.035
    ven = laakarton
    dr = K.empty(name + '_laatje', (open_, 0, t + 0.012), parent=root)
    H.box(name + '_laabodem', L - 0.04, lw, lt, ven, loc=(0, 0, lt / 2), bev=0.01, parent=dr)
    for sy in (-1, 1):
        H.box(name + f'_laazij{sy}', L - 0.04, lt, lh, ven, loc=(0, sy * (lw / 2 - lt / 2), lh / 2), bev=0.01, parent=dr)
    for sx in (-1, 1):
        H.box(name + f'_laakop{sx}', lt, lw, lh, ven, loc=(sx * (L / 2 - 0.02 - lt / 2), 0, lh / 2), bev=0.01, parent=dr)
    if contents:
        rnd = np.random.default_rng(5)
        cols = ['#d8473a', '#e7b23b', '#3e6ea6', '#3f8a55', '#f2e8d4', '#8b5a36']
        for k in range(9):
            x = L / 2 - 0.5 - rnd.uniform(0, 1.5)
            y = rnd.uniform(-lw / 2 + 0.4, lw / 2 - 0.4)
            knoop(f'{name}_knoop{k}', (x, y, lt + 0.06 + 0.05 * (k % 3)), cols[k % len(cols)], r=rnd.uniform(0.28, 0.42),
                  rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 6)), parent=dr)
        for k in range(5):
            spijkertje(f'{name}_spijker{k}', (L / 2 - 0.6 - rnd.uniform(0, 2.2), rnd.uniform(-lw / 2 + 0.3, lw / 2 - 0.3), lt + 0.08),
                       rot=(math.pi / 2 + rnd.uniform(-0.1, 0.1), 0, rnd.uniform(0, 6.28)), parent=dr)
    return root


def _strijkvlak(key='strijkvlak', rand=None):
    """Bruin, ruw strijkvlak; met `rand` een smal bedrukt randje boven en onder (zijkant van het doosje)."""
    key = f'{key}_{rand}'
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (40, 40, 40)), 1.0, 3.0, 0.7)
    col = g.ramp(n, [(0.3, '#4a2a1e'), (0.7, '#7a4532')])
    ro = 0.9
    h = n
    if rand:
        gz = g.sep(tc.outputs['Generated'])[2]
        band = g.math('MULTIPLY', g.math('GREATER_THAN', gz, 0.17), g.math('LESS_THAN', gz, 0.83))
        col = g.mix(band, rand, col)
        ro = g.mixf(band, 0.55, 0.9)
        h = g.math('MULTIPLY', n, band)
    g.bsdf(col, ro, normal=g.bump(h, 0.6, 0.004))
    return m


def knoop(name, loc, col, r=0.35, rot=(0, 0, 0), parent=None, holes=4, wood=False):
    """Knoop met gaatjes (plastic of hout)."""
    mat = H.wood('noten', 'X', key='knoop_hout') if wood else H.plastic(col, 0.25, coat=0.3)
    h = r * 0.28
    prof = [(0, h * 0.55), (r * 0.7, h * 0.45), (r * 0.86, h * 0.9), (r, h * 0.75), (r, h * 0.2), (r * 0.9, 0), (0, 0)]
    ob = K.lathe(name, prof[::-1], 40, mat, parent)
    ob.location, ob.rotation_euler = loc, rot
    dark = H.plastic('#1a1410', 0.6, key='gaatje')
    for k in range(holes):
        a = math.pi / 4 + k * math.pi / 2
        H.cyl(name + f'_gat{k}', r * 0.1, 0.01, dark, loc=(math.cos(a) * r * 0.25, math.sin(a) * r * 0.25, h * 0.5),
              bev=0.0, seg=12, parent=ob)
    return ob


def spijkertje(name, loc, rot=(0, 0, 0), parent=None, L=1.2):
    steel = H.metal('#b9b6ae', 0.3, key='staal')
    ob = H.cyl(name, 0.035, L, steel, loc=loc, rot=rot, bev=0.005, seg=10, parent=parent, r_top=0.03)
    H.cyl(name + '_kop', 0.09, 0.025, steel, loc=(0, 0, L), bev=0.008, seg=16, parent=ob)
    return ob


# ---------------------------------------------------------------- potloodstompje
def potlood(name, col, L=1.3, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, sharp=False, r=0.37):
    lak = H.wood('ceder', 'Z', paint=col, grain=0.05, rough=0.22, coat=0.6, key=f'lak_{col}')
    pts = [(r * math.cos(math.radians(30 + 60 * k)), r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    ob = H.prism(name, pts, L, lak, loc=loc, rot=rot, bev=0.035, seg=2, parent=parent, angle=25)
    ced = H.wood('ceder', 'Z', key='ceder_kaal')
    gr = H.metal('#2e2e30', 0.45, key='grafiet')
    if sharp:
        K.lathe(name + '_punt', [(0, 0), (r * 0.9, 0), (0.06, 1.25), (0, 1.3)], 32, ced, ob).location = (0, 0, L)
        K.lathe(name + '_stift', [(0, 0), (0.075, 0), (0.02, 0.22), (0, 0.24)], 16, gr, ob).location = (0, 0, L + 1.08)
    return ob


# ---------------------------------------------------------------- dobbelsteen
def dobbelsteen(name, loc=(0, 0, 0), rot=0.0, s=1.6, parent=None, faces=None):
    """Gewone spelletjesdobbelsteen: wit plastic, afgeronde hoeken, zwarte ogen."""
    mat = H.plastic('#f6f3ec', 0.32, key='dobbel_wit', coat=0.15)
    ob = H.box(name, s, s, s, mat, loc=loc, rot=(0, 0, math.radians(rot)), bev=s * 0.16, seg=5, parent=parent, base=True)
    ogen = H.plastic('#141210', 0.35, key='dobbel_oog')
    P = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
         5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
    faces = faces or {'+z': 1, '-y': 2, '+x': 3, '-x': 4, '+y': 5}
    d = s * 0.25
    pr = s * 0.095
    for f, num in faces.items():
        for k, (u, v) in enumerate(P[num]):
            pr_ = pr * 1.25 if num == 1 else pr
            u, v = u * d, v * d
            e = 0.004
            if f == '+z':
                loc_, rot_ = (u, v, s + e), (0, 0, 0)
            elif f == '-y':
                loc_, rot_ = (u, -s / 2 - e, s / 2 + v), (math.pi / 2, 0, 0)
            elif f == '+y':
                loc_, rot_ = (u, s / 2 + e, s / 2 + v), (-math.pi / 2, 0, 0)
            elif f == '+x':
                loc_, rot_ = (s / 2 + e, u, s / 2 + v), (0, math.pi / 2, 0)
            else:
                loc_, rot_ = (-s / 2 - e, u, s / 2 + v), (0, -math.pi / 2, 0)
            K.blob(f'{name}_oog{f}{k}', (pr_, pr_, 0.025), 2.0, (24, 12), mat=ogen, parent=ob, loc=loc_, rot=rot_)
    return ob


# ---------------------------------------------------------------- garenklosje
def garenklos(name, col, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, Hh=2.4, R=1.0, core=0.55, fill=0.86, draad=None):
    mat = H.wood('beuk', 'Z', key='klos')
    f = 0.24
    prof = [(0.22, 0.0), (R - 0.05, 0.0), (R, 0.05), (R, f - 0.05), (R - 0.05, f), (core, f + 0.02), (core, Hh - f - 0.02),
            (R - 0.05, Hh - f), (R, Hh - f + 0.05), (R, Hh - 0.05), (R - 0.05, Hh), (0.22, Hh), (0.22, 0.0)]
    ob = K.lathe(name, prof, 64, mat, parent, close_top=False, close_bot=False)
    ob.location, ob.rotation_euler = loc, rot
    if fill:
        rf = core + (R - core) * fill
        tp = [(core, f + 0.005), (rf - 0.04, f + 0.01), (rf, f + 0.06), (rf + 0.012, Hh / 2), (rf, Hh - f - 0.06),
              (rf - 0.04, Hh - f - 0.01), (core, Hh - f - 0.005)]
        th = K.lathe(name + '_garen', tp, 96, H.thread(col), ob, close_top=False, close_bot=False)
        # los eindje draad (alleen als het klosje gewoon op de grond staat)
        if draad is None:
            draad = abs(rot[0]) < 0.01 and abs(rot[1]) < 0.01 and loc[2] < 0.5
        if not draad:
            return ob
        a = 0.6
        p0 = (rf * math.cos(a), rf * math.sin(a), Hh * 0.62)
        K.curve_tube(name + '_draadje', [p0, (p0[0] + 0.3, p0[1] - 0.25, p0[2] - 0.2), (p0[0] + 0.5, p0[1] - 0.4, p0[2] - 0.9),
                                         (p0[0] + 0.55, p0[1] - 0.6, 0.02 - loc[2]), (p0[0] + 1.3, p0[1] - 1.0, 0.02 - loc[2])],
                     0.012, H.thread(col), ob)
    return ob


# ---------------------------------------------------------------- eikeldopje (kopje of lampenkap)
def eikeldop(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, R=0.85, D=0.62, stem=True):
    """Napje met de opening naar boven (+z). Voor een lampenkap: rot=(pi,0,0)."""
    m = H.oak_cap()
    inner = H.wood('eiken', 'Z', tint=('#b48a5a', '#8d6638'), key='eikeldop_binnen')
    prof = [(0, 0)]
    for k in range(1, 13):
        t = k / 12
        a = t * math.pi / 2
        prof.append((R * math.sin(a) * (1.0 + 0.04 * math.sin(a * 2)), D * (1 - math.cos(a)) * 1.0))
    rim = (R * 0.9, D + 0.02)
    prof += [rim]
    for k in range(12, -1, -1):
        t = k / 12
        a = t * math.pi / 2
        prof.append(((R - 0.07) * math.sin(a), 0.08 + (D - 0.05) * (1 - math.cos(a))))
    ob = K.lathe(name, prof, 72, m, parent, close_top=False, close_bot=False)
    ob.location, ob.rotation_euler = loc, rot
    if stem:
        H.capsule(name + '_steeltje', (0, 0, 0.02), (0.05, 0.03, -0.22), 0.07, H.wood('eiken', 'Z', tint=('#8a6a42', '#6b4d2c'),
                                                                                       key='steeltje'), ob, r1=0.05)
    return ob


def hanglamp(name, loc, ceiling=24.0, energy=60.0, col='#ffcf8f', parent=None):
    root = K.empty(name, loc, parent=parent)
    eikeldop(name + '_kap', (0, 0, 0.55), (math.pi, 0, 0), root)
    K.blob(name + '_lampje', (0.17, 0.17, 0.3), 2.0, (32, 16), mat=H.bulb(col, 25.0), parent=root, loc=(0, 0, -0.08))
    H.cyl(name + '_fitting', 0.15, 0.25, H.metal('#7b6a4f', 0.35, key='fitting'), loc=(0, 0, 0.12), bev=0.02, seg=24,
          parent=root)
    K.curve_tube(name + '_snoer', [(0, 0, 0.75), (0, 0, ceiling - loc[2])], 0.025, H.thread('#3a3330', key='snoer'), root)
    L = K.light('POINT', (0, 0, 0), energy=energy, color=K.srgb(col)[:3], size=0.15, name=name + '_licht')
    L.parent = root
    L.location = (0, 0, -0.1)
    return root


# ---------------------------------------------------------------- kroonkurk met verf
def kroonkurk(name, loc, paint=None, rot=(0, 0, 0), parent=None, R=1.3, Hh=0.62):
    """Kroonkurk met de opening naar boven, eventueel gevuld met verf."""
    mat = H.metal('#b8a888', 0.32, key='kroonkurk')
    nseg, nr = 126, 14
    V, F = [], []
    prof = [(0, 0.0), (R * 0.75, 0.0), (R * 0.92, 0.02), (R * 0.98, 0.12), (R * 1.02, 0.4), (R * 1.08, Hh)]
    inner = [(R * 1.0, Hh), (R * 0.95, 0.42), (R * 0.9, 0.12), (R * 0.72, 0.06), (0, 0.06)]
    pr = prof + inner
    for i, (r, z) in enumerate(pr):
        for j in range(nseg):
            a = 2 * math.pi * j / nseg
            flute = 1 + (0.06 * math.cos(21 * a) * min(1.0, z / Hh * 1.4) if r > R * 0.9 else 0)
            V.append((r * flute * math.cos(a), r * flute * math.sin(a), z))
    n = len(pr)
    for i in range(n - 1):
        for j in range(nseg):
            F.append((i * nseg + j, i * nseg + (j + 1) % nseg, (i + 1) * nseg + (j + 1) % nseg, (i + 1) * nseg + j))
    ob = K.mesh_obj(name, V, F, mat, parent, loc=loc, rot=rot)
    if paint:
        pm = H.metal('#d9aa45', 0.22, key='goudverf_pot') if paint == 'goud' else H.plastic(paint, 0.08, key=f'verf_{paint}', coat=0.5)
        H.cyl(name + '_verf', R * 0.93, Hh * 0.55, pm, loc=(0, 0, 0.05), bev=0.03, seg=64, parent=ob)
    return ob


def vingerhoed(name, loc, rot=(0, 0, 0), parent=None, R=0.8, Hh=2.0):
    m = _vingerhoed_mat()
    prof = [(0, Hh), (R * 0.55, Hh - 0.02), (R * 0.82, Hh - 0.18), (R * 0.9, Hh - 0.5), (R * 0.97, 0.35), (R * 1.08, 0.22),
            (R * 1.08, 0.04), (R * 1.0, 0.0), (R * 0.9, 0.05), (R * 0.88, Hh - 0.5), (0, Hh - 0.08)]
    ob = K.lathe(name, prof[::-1], 72, m, parent, close_top=False, close_bot=False)
    ob.location, ob.rotation_euler = loc, rot
    return ob


def _vingerhoed_mat(key='vingerhoed'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    a = g.math('ARCTAN2', y, x)
    d = g.math('MULTIPLY', g.math('ADD', g.math('SINE', g.math('MULTIPLY', a, 34.0)), 1.0),
               g.math('ADD', g.math('SINE', g.math('MULTIPLY', z, 2 * math.pi / 0.17)), 1.0))
    mask = g.math('GREATER_THAN', z, 0.4)
    h = g.math('MULTIPLY', d, mask)
    g.bsdf('#c9c4bb', 0.28, metal=1.0, normal=g.bump(h, 0.35, 0.02))
    return m


# ---------------------------------------------------------------- kleine dingen
def punaise(name, loc, rot=(0, 0, 0), parent=None, r=0.5):
    m = H.metal('#d4ad5c', 0.25, key='messing')
    ob = K.lathe(name, [(0, 0), (r, 0), (r, 0.03), (r * 0.6, 0.09), (0, 0.11)], 48, m, parent)
    ob.location, ob.rotation_euler = loc, rot
    return ob


def speld(name, loc, col, rot=(0, 0, 0), parent=None, L=1.0, r=0.11):
    ob = K.empty(name, loc, rot, parent=parent)
    H.ball(name + '_kop', r, H.plastic(col, 0.15, coat=0.4), parent=ob, res=(24, 12))
    H.cyl(name + '_pin', 0.022, L, H.metal('#c9c9c9', 0.2, key='speldstaal'), loc=(0, 0, 0), rot=(math.pi / 2, 0, 0),
          bev=0.0, seg=8, parent=ob)
    return ob


def hamertje(name, bead='#d4473a', L=1.25, br=0.2, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Kraal op een stukje tandenstoker. Steel langs -z vanaf de kraal; de kraal ligt dwars (as langs x)."""
    ob = K.empty(name, loc, rot, parent=parent)
    stok = H.wood('berk', 'Z', key='tandenstoker')
    K.lathe(name + '_steel', [(0, -L), (0.02, -L), (0.045, -L + 0.25), (0.045, 0.1), (0, 0.12)], 16, stok, ob)
    kr = H.wood('beuk', 'X', paint=bead, grain=0.25, rough=0.3, coat=0.35, key=f'kraal_{bead}')
    k = H.cyl(name + '_kraal', br, br * 3.0, kr, loc=(-br * 1.5, 0, 0.0), rot=(0, math.pi / 2, 0), bev=br * 0.28, seg=40,
              parent=ob)
    return ob


def zaagje(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), L=1.6):
    """Zaagje: blad van een figuurzaag in een handvat van een kurkschijfje."""
    ob = K.empty(name, loc, rot, parent=parent)
    st = H.metal('#bfc3c6', 0.18, key='zaagblad')
    pts = [(0, 0.0), (L, 0.05)]
    teeth = []
    n = 22
    for k in range(n + 1):
        x = L * (1 - k / n)
        teeth.append((x, -0.42 + 0.06 * (k % 2) + 0.12 * k / n))
    outline = [(0, 0.08), (L, 0.02)] + teeth
    H.prism(name + '_blad', outline, 0.015, st, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), bev=0.0, parent=ob)
    hd = H.cyl(name + '_heft', 0.32, 0.22, H.cork(), loc=(-0.12, 0.11, -0.12), rot=(math.pi / 2, 0, 0), bev=0.04, seg=32,
               parent=ob)
    return ob


def knijpertje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=3.0, W=None, T=None, wood=None):
    """Houten wasknijper naar een echte: twee helften die aan de handvatkant (x = 0) in een V openstaan,
    een veer met een zichtbare spiraal in het inkeepje, een draadarmpje schuin over de zijkant naar de rand,
    een randje waar de bek begint en een groot rond gat in de bek (bek bij x = L).
    Lengte langs x, dikte (beide helften samen) langs y, breedte langs z."""
    T = T if T is not None else 0.17 * L
    W = W if W is not None else 0.125 * L
    ob = K.empty(name, loc, rot, parent=parent)
    m = wood or H.wood('berk', 'X', var=0.12, key='knijper')
    h = T / 2

    def arc(cx, cy, r, a0, a1, n=10):
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
                for k in range(n + 1)]
    xs, rs = 0.42 * L, 0.15 * T        # inkeping voor de veer
    xp, rp = 0.57 * L, 0.06 * T        # draaipunt (klein gaatje)
    xg, rg = 0.82 * L, 0.22 * T        # groot rond gat in de bek
    xst = 0.66 * L                     # randje waar de bek begint
    g0 = 0.13 * T                      # halve V-opening aan de handvatkant
    vy = lambda x: max(0.0, g0 * (1 - x / (xp - rp)))
    pts = [(0.0, g0), (xs - rs, vy(xs - rs))]
    pts += [(x, y + vy(x) * 0.0) for x, y in arc(xs, vy(xs), rs, 180, 0, 12)]
    pts += [(xs + rs, vy(xs + rs)), (xp - rp, 0.0)]
    pts += arc(xp, 0.0, rp, 180, 0, 8)
    pts += [(xg - rg, 0.0)]
    pts += arc(xg, 0.0, rg, 180, 0, 16)
    pts += [(L - 0.02 * T, 0.0), (L, 0.04 * h), (L, 0.86 * h), (L - 0.02 * T, 0.88 * h), (xst + 0.012 * L, 0.92 * h),
            (xst + 0.004 * L, 0.88 * h), (xst - 0.006 * L, 0.88 * h), (xst - 0.012 * L, h), (0.025 * L, h), (0.0, 0.94 * h)]
    for sz in (1, -1):
        P = pts if sz > 0 else [(x, -y) for x, y in pts][::-1]
        hf = H.prism(name + f'_helft{sz}', P, W, m, bev=min(0.04, h * 0.12), seg=2, parent=ob, angle=28)
        hf.location = (0, 0, -W / 2)
    veer = H.metal('#c3c6ca', 0.25, key='veer')
    rw = 0.034 * T
    rc = rs * 0.95
    coil = []
    turns = 7
    for k in range(turns * 16 + 1):
        a_ = 2 * math.pi * k / 16
        coil.append((xs + rc * math.cos(a_), rc * math.sin(a_), -W / 2 - rw + (W + 2 * rw) * k / (turns * 16)))
    K.curve_tube(name + '_veer', coil, rw, veer, ob)
    # armpjes: schuin over de zijkant naar de rand bij het randje, dan om de rand heen
    for sy, sz in ((1, 1), (-1, -1)):
        z0 = sz * (W / 2 + rw)
        arm = [(xs + rc * 0.7, sy * rc * 0.7, z0), (xs + 0.3 * (xst - xs), sy * h * 0.42, z0),
               (xst - 0.02 * L, sy * (h - rw), z0), (xst - 0.012 * L, sy * (h + rw * 1.2), sz * W * 0.38),
               (xst - 0.01 * L, sy * (h + rw * 1.2), sz * W * 0.1)]
        tb = K.curve_tube(name + f'_arm{sy}', arm, rw, veer, ob)
        tb.data.splines[0].order_u = 3
    return ob

def lucifer(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=4.4, s=0.2, burnt=False):
    m = H.wood('populier', 'X', key='lucifer')
    ob = H.box(name, L, s, s, m, loc=loc, rot=rot, bev=0.02, seg=1, parent=parent)
    kop = H.plastic('#2a2320' if burnt else '#c23a2b', 0.7, key='luciferkop' + ('z' if burnt else ''))
    K.blob(name + '_kop', (0.3, 0.14, 0.14), 2.2, (24, 12), mat=kop, parent=ob, loc=(L / 2 - 0.12, 0, 0))
    return ob


# ---------------------------------------------------------------- krullen en zaagsel
def _krul_mat(col):
    key = f'krul_{col}'
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    r = g.vmath('LENGTH', g.comb(x, y, 0.0))
    a = g.math('ARCTAN2', y, x)
    rad = g.noise(g.comb(g.math('MULTIPLY', a, 3.0), r, 0.0), 6.0, 3.0)
    base = g.mix(g.math('MULTIPLY', rad, 0.6), '#e3a978', '#c98a5c')
    rim = g.math('GREATER_THAN', r, g.math('ADD', 0.78, g.math('MULTIPLY', rad, 0.06)))
    col_ = g.mix(rim, base, col)
    core = g.math('LESS_THAN', r, 0.2)
    col_ = g.mix(core, col_, '#4a4440')
    g.bsdf(col_, 0.65, sheen=0.3)
    m.use_backface_culling = False
    return m


def slijpkrul(name, col, loc, rot=(0, 0, 0), parent=None, R=0.86, seed=0):
    """Krul uit een puntenslijper: dun, golvend kegelringetje met het lakrandje."""
    rnd = np.random.default_rng(seed)
    nt, nr = 90, 10
    turns = 1.15
    V = []
    k_wave = rnd.integers(6, 10)
    for i in range(nr):
        r = 0.16 + (R - 0.16) * i / (nr - 1)
        for j in range(nt):
            a = turns * 2 * math.pi * j / (nt - 1)
            z = -0.32 * (r - 0.16) + 0.06 * math.sin(k_wave * a) * (r / R) ** 2 + 0.05 * a / (2 * math.pi)
            V.append((r * math.cos(a), r * math.sin(a), z))
    F = [(i * nt + j, i * nt + j + 1, (i + 1) * nt + j + 1, (i + 1) * nt + j) for i in range(nr - 1) for j in range(nt - 1)]
    ob = K.mesh_obj(name, V, F, _krul_mat(col), parent, loc=loc, rot=rot)
    K.modifier(ob, 'SOLIDIFY', thickness=0.012, offset=0.0)
    return ob


def zaagsel(name, center, size, n=2500, seed=2, zf=0.0, smin=0.02, smax=0.07, falloff=True, soort='grenen', clip=None):
    """Veel kleine snippertjes als één mesh (snel)."""
    rnd = np.random.default_rng(seed)
    V, F = [], []
    cx, cy = center
    sx, sy = size
    for k in range(n):
        if falloff:
            x, y = rnd.normal(cx, sx * 0.5), rnd.normal(cy, sy * 0.5)
        else:
            x, y = rnd.uniform(cx - sx / 2, cx + sx / 2), rnd.uniform(cy - sy / 2, cy + sy / 2)
        if clip and not (clip[0] < x < clip[1] and clip[2] < y < clip[3]):
            continue
        s = rnd.uniform(smin, smax)
        a = rnd.uniform(0, math.pi)
        e = rnd.uniform(0.4, 1.0)
        tilt = rnd.normal(0, 0.25, 2)
        b = len(V)
        for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            px = u * s * math.cos(a) - v * s * e * math.sin(a)
            py = u * s * math.sin(a) + v * s * e * math.cos(a)
            pz = zf + 0.006 + px * tilt[0] + py * tilt[1] + rnd.uniform(0, 0.01)
            V.append((x + px, y + py, max(zf + 0.002, pz)))
        F.append((b, b + 1, b + 2, b + 3))
    m = H.wood(soort, 'X', var=0.2, key=f'zaagsel_{soort}')
    ob = K.mesh_obj(name, V, F, m, smooth=False)
    m.use_backface_culling = False
    return ob


def gaatjesplaat(name, W, Hh, mat, pitch=2.54, hole=0.3, T=0.4, skip=None, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Gaatjesplaat van multiplex in het xy-vlak (dikte langs z), linksonder op (0,0). skip(i,j) -> True laat een
    cel weg (voor een raam)."""
    nx, ny = int(W / pitch), int(Hh / pitch)
    seg = 20
    V, F = [], []
    for i in range(nx):
        for j in range(ny):
            if skip and skip(i, j):
                continue
            x0, y0 = i * pitch, j * pitch
            cx, cy = x0 + pitch / 2, y0 + pitch / 2
            b = len(V)
            for k in range(seg):
                a = 2 * math.pi * k / seg + math.pi / 4
                ca, sa = math.cos(a), math.sin(a)
                m = max(abs(ca), abs(sa))
                V.append((cx + ca / m * pitch / 2, cy + sa / m * pitch / 2, 0))
                V.append((cx + ca * hole, cy + sa * hole, 0))
            for k in range(seg):
                k2 = (k + 1) % seg
                F.append((b + 2 * k, b + 2 * k2, b + 2 * k2 + 1, b + 2 * k + 1))
    ob = K.mesh_obj(name, V, F, mat, parent, smooth=False, loc=loc, rot=rot)
    # vierkante hoekpunten van elke cel ontbreken in het ringmodel -> hoeken met driehoeken opvullen
    K.modifier(ob, 'WELD', merge_threshold=0.001)
    K.modifier(ob, 'SOLIDIFY', thickness=T, offset=-1.0, use_even_offset=True)
    return ob


def krulletjes(name, center, size, n=60, seed=8, zf=0.0, rmin=0.04, rmax=0.11, soort='grenen', falloff=True, clip=None):
    """Kleine opgerolde schaafkrulletjes (zoals uit opa's schaafje), samen één mesh."""
    rnd = np.random.default_rng(seed)
    V, F = [], []
    cx, cy = center
    sx, sy = size
    for k in range(n):
        if falloff:
            x, y = rnd.normal(cx, sx * 0.5), rnd.normal(cy, sy * 0.5)
        else:
            x, y = rnd.uniform(cx - sx / 2, cx + sx / 2), rnd.uniform(cy - sy / 2, cy + sy / 2)
        if clip and not (clip[0] < x < clip[1] and clip[2] < y < clip[3]):
            continue
        r0 = rnd.uniform(rmin, rmax)
        w = rnd.uniform(0.7, 1.6) * r0 * 1.6
        turns = rnd.uniform(1.3, 2.6)
        tail = rnd.uniform(0.0, 3.0) * r0
        nt = int(28 * turns)
        pts = []
        for i in range(nt):
            t = turns * 2 * math.pi * i / (nt - 1)
            r = r0 * (0.35 + 0.65 * t / (turns * 2 * math.pi))
            pts.append((r * math.cos(t), r * math.sin(t)))
        a0 = turns * 2 * math.pi
        ex, ey = pts[-1]
        tx, ty = -math.sin(a0), math.cos(a0)
        for i in range(1, 6):
            pts.append((ex + tx * tail * i / 5, ey + ty * tail * i / 5 - 0.002 * i))
        ang = rnd.uniform(0, 2 * math.pi)
        ca, sa = math.cos(ang), math.sin(ang)
        tilt = rnd.uniform(-0.25, 0.25)
        zc = zf + r0 * 0.95
        b = len(V)
        m = len(pts)
        for (px, py) in pts:
            for side in (-1, 1):
                q = side * w / 2 * (1 - 0.15 * rnd.random())
                lx, ly, lz = px, q, py
                lz += tilt * q
                # as van de rol ligt horizontaal (lokale y), draai om z
                wx = lx * ca - ly * sa
                wy = lx * sa + ly * ca
                V.append((x + wx, y + wy, max(zf + 0.004, zc + lz)))
        for i in range(m - 1):
            F.append((b + 2 * i, b + 2 * i + 2, b + 2 * i + 3, b + 2 * i + 1))
    mat = H.wood(soort, 'X', var=0.18, key=f'krulletje_{soort}')
    mat.use_backface_culling = False
    ob = K.mesh_obj(name, V, F, mat)
    K.modifier(ob, 'SOLIDIFY', thickness=0.006, offset=0.0)
    return ob


# ---------------------------------------------------------------- meer alledaagse dingen
def _lathe_ribbed(name, prof, seg, ribs, amp, mat, parent=None, rmin_rib=0.0):
    """Draaivorm met ribbeltjes (zoals de rand van een frisdrankdop) op punten met r >= rmin_rib."""
    V, F = [], []
    for r, z in prof:
        for j in range(seg):
            a = 2 * math.pi * j / seg
            f = 1 + (amp * (0.5 + 0.5 * math.cos(ribs * a)) if r >= rmin_rib else 0)
            V.append((r * f * math.cos(a), r * f * math.sin(a), z))
    n = len(prof)
    for i in range(n - 1):
        for j in range(seg):
            F.append((i * seg + j, i * seg + (j + 1) % seg, (i + 1) * seg + (j + 1) % seg, (i + 1) * seg + j))
    return K.mesh_obj(name, V, F, mat, parent)


def frisdrankdop(name, loc, col, paint=None, rot=(0, 0, 0), parent=None, R=1.5, Hh=1.15, up=True):
    """Plastic schroefdop van een frisdrankfles. up=True: opening naar boven (als potje of emmertje)."""
    mat = H.plastic(col, 0.38, key=f'dop_{col}')
    t = 0.1
    prof = [(0, 0), (R * 0.9, 0), (R - 0.04, 0.03), (R, 0.12), (R, Hh - 0.1), (R - 0.03, Hh), (R - t, Hh),
            (R - t, t + 0.05), (0, t)]
    ob = _lathe_ribbed(name, prof, 240, 120, 0.012, mat, parent, rmin_rib=R - 0.001)
    ob.location = loc
    ob.rotation_euler = rot if up else (math.pi + rot[0], rot[1], rot[2])
    pts = []
    for k in range(80):
        a = k / 79 * 2 * math.pi * 1.6
        pts.append(((R - t - 0.03) * math.cos(a), (R - t - 0.03) * math.sin(a), Hh * 0.35 + 0.18 * a / (2 * math.pi)))
    K.curve_tube(name + '_draad', pts, 0.035, mat, ob)
    if paint:
        pm = H.metal('#d9aa45', 0.22, key='goudverf_pot') if paint == 'goud' else H.plastic(paint, 0.12, key=f'verf_{paint}', coat=0.6)
        H.cyl(name + '_verf', R - t - 0.01, Hh * 0.78 - t, pm, loc=(0, 0, t), bev=0.04, seg=64, parent=ob)
    return ob


def bliklipje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=2.1, W=1.3):
    """Lipje van een blikje (aluminium) met het grote vingergat en het kleine klinkgaatje. Lengte langs y."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = 0.012
    cu.bevel_depth = 0.01
    cu.bevel_resolution = 2

    def add(pts):
        sp = cu.splines.new('POLY')
        sp.points.add(len(pts) - 1)
        for p, (x, y) in zip(sp.points, pts):
            p.co = (x, y, 0, 1)
        sp.use_cyclic_u = True

    out = []
    for k in range(64):
        a = 2 * math.pi * k / 64
        c, s_ = math.cos(a), math.sin(a)
        y = L / 2 * math.copysign(abs(s_) ** (2 / 3.2), s_)
        x = W / 2 * math.copysign(abs(c) ** (2 / 3.2), c) * (1 - 0.18 * (y / L + 0.5))
        out.append((x, y))
    add(out)
    add([(W * 0.33 * math.cos(2 * math.pi * k / 40), -L * 0.17 + L * 0.21 * math.sin(2 * math.pi * k / 40)) for k in range(40)][::-1])
    add([(0.13 * math.cos(2 * math.pi * k / 20), L * 0.3 + 0.13 * math.sin(2 * math.pi * k / 20)) for k in range(20)][::-1])
    ob = bpy.data.objects.new(name, cu)
    cu.materials.append(H.metal('#c9cdd2', 0.22, key='aluminium'))
    ob.location, ob.rotation_euler = loc, rot
    return K.link(ob, parent)


def gum(name, loc, rot=0.0, parent=None, L=4.2, W=1.9, T=1.0):
    """Gummetje, half rood en half blauw (schuin gedeeld)."""
    key = 'gum'
    if key in H._M:
        m = H._M[key]
    else:
        m = H._new(key)
        g = H.G(m)
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        side = g.math('GREATER_THAN', g.math('ADD', x, g.math('MULTIPLY', z, 0.9)), 0.35)
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (25, 25, 25)), 1.0, 3.0)
        col = g.mix(side, '#d6443a', '#3a5fae')
        col = g.mul(col, g.math('ADD', 0.94, g.math('MULTIPLY', n, 0.12)))
        g.bsdf(col, 0.62, normal=g.bump(n, 0.15, 0.01), sheen=0.15)
    return H.box(name, L, W, T, m, loc=loc, rot=(0, 0, math.radians(rot)), bev=0.14, seg=4, parent=parent, base=True)


def batterij(name, loc, rot=(0, 0, 0), parent=None, R=0.52, Hh=4.45, col='#2f4f8f'):
    """AAA-batterijtje (als gasfles)."""
    ob = H.cyl(name, R, Hh - 0.1, H.plastic(col, 0.3, coat=0.4, key=f'batt_{col}'), loc=loc, rot=rot, bev=0.05, seg=48,
               parent=parent)
    st = H.metal('#cfd2d6', 0.2, key='batt_staal')
    H.cyl(name + '_kap', R * 1.005, 0.9, H.metal('#c9a14a', 0.25, key='batt_goud'), loc=(0, 0, Hh - 1.0), bev=0.05, seg=48,
          parent=ob)
    H.cyl(name + '_nop', R * 0.36, 0.2, st, loc=(0, 0, Hh - 0.12), bev=0.04, seg=32, parent=ob)
    return ob


def elastiekje(name, top, parent=None, col='#c9473b', w=1.6, h=3.2, r=0.06):
    """Elastiekje dat aan een speld hangt (als een rol touw)."""
    x, y, z = top
    pts = []
    for k in range(40):
        a = 2 * math.pi * k / 40
        px = x + math.sin(a) * w * 0.5 * (0.6 + 0.4 * (1 - math.cos(a)) / 2)
        pz = z - (1 - math.cos(a)) / 2 * h
        pts.append((px, y - 0.08 - 0.05 * math.sin(a * 2), pz))
    return K.curve_tube(name, pts, r, H.plastic(col, 0.55, key=f'elastiek_{col}'), parent, cyclic=True)


def paperclip(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, col='#d4473a', L=3.3, Wd=0.95, r=0.045):
    """Paperclip (gem-vorm) in het xy-vlak, lengte langs x."""
    def arc(cx, cy, rad, a0, a1, n=10):
        return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + rad * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
                for k in range(n + 1)]
    pts = [(0.75, 0.15)]
    pts += arc(L - Wd / 2 + 0.05, Wd / 2, Wd / 2, -90, 90)
    pts += arc(0.42, Wd / 2 + 0.07, Wd / 2 - 0.12, 90, 270)
    pts += arc(L - 0.75, Wd / 2 + 0.07, 0.22, -90, 90)
    pts += [(1.0, Wd / 2 + 0.29)]
    P = [(x - L / 2, y - Wd / 2, 0) for x, y in pts]
    ob = K.curve_tube(name, P, r, H.plastic(col, 0.3, coat=0.3, key=f'clip_{col}'), parent)
    ob.data.splines[0].order_u = 2
    ob.location, ob.rotation_euler = loc, rot
    return ob


def knikker(name, loc, parent=None, R=0.8, col='#2f7fc8'):
    m = H.glass('#eef6f7', 0.0)
    ob = H.ball(name, R, m, loc=loc, parent=parent, res=(48, 24))
    swirl = H.plastic(col, 0.2, key=f'knikker_{col}')
    K.blob(name + '_draai', (R * 0.75, R * 0.12, R * 0.6), 2.0, (32, 16), mat=swirl, parent=ob,
           deform=lambda D, P: P + np.stack([np.zeros(len(P)), np.sin(P[:, 0] * 4) * R * 0.25, np.zeros(len(P))], 1),
           rot=(0.4, 0.3, 0.8))
    return ob


def liniaal(name, loc, rot=(0, 0, 0), parent=None, L=30.0, W=3.0, T=0.3):
    """Houten liniaal met centimeter- en millimeterstreepjes langs de voorkant (-y)."""
    key = 'liniaal'
    if key in H._M:
        m = H._M[key]
    else:
        m = H._new(key)
        g = H.G(m)
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        xs = g.math('ADD', x, L / 2 - 1.0)
        mm = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', xs, 0.1)), 0.11)
        cmk = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', g.math('ADD', xs, 0.006), 1.0)), 0.016)
        half = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', g.math('ADD', xs, 0.006), 0.5)), 0.032)
        ln = g.math('ADD', 0.22, g.math('ADD', g.math('MULTIPLY', half, 0.13), g.math('MULTIPLY', cmk, 0.2)))
        edge = g.math('LESS_THAN', g.math('SUBTRACT', y, -W / 2), ln)
        top = g.math('GREATER_THAN', z, T / 2 - 0.01)
        inr = g.math('MULTIPLY', g.math('GREATER_THAN', xs, -0.01), g.math('LESS_THAN', xs, L - 1.95))
        tick = g.math('MULTIPLY', g.math('MULTIPLY', g.math('MAXIMUM', mm, cmk), edge), g.math('MULTIPLY', top, inr))
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (0.6, 30, 30)), 1.0, 3.0)
        col = g.mix(n, '#e2bf93', '#d1a97c')
        col = g.mix(tick, col, '#2a2420')
        g.bsdf(col, g.mixf(tick, 0.5, 0.35), coat=0.25, normal=g.bump(n, 0.08, 0.003))
    return H.box(name, L, W, T, m, loc=loc, rot=rot, bev=0.04, seg=2, parent=parent)


def kwastje(name, paint='#d6a640', loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=1.3):
    """Kwastje: steeltje (tandenstoker, rood gelakt), metalen huls en haren met een klodder verf. Haren bij -z."""
    ob = K.empty(name, loc, rot, parent=parent)
    H.cyl(name + '_steel', 0.045, L, H.wood('berk', 'Z', paint='#c8392f', grain=0.1, coat=0.4, key='kwaststeel'),
          loc=(0, 0, 0), bev=0.02, seg=16, parent=ob)
    H.cyl(name + '_huls', 0.055, 0.22, H.metal('#c9c9c9', 0.25, key='speldstaal'), loc=(0, 0, -0.2), bev=0.01, seg=16,
          parent=ob)
    K.lathe(name + '_haar', [(0, -0.48), (0.03, -0.46), (0.06, -0.3), (0.055, -0.18), (0, -0.17)], 16,
            H.plastic('#3a2a1e', 0.7, key='kwasthaar'), ob)
    K.lathe(name + '_verf', [(0, -0.5), (0.035, -0.48), (0.065, -0.38), (0, -0.36)], 16,
            H.metal(paint, 0.25, key='verf_kwast_' + paint) if paint == '#d6a640' else H.plastic(paint, 0.1, key='verfk_' + paint),
            ob)
    return ob


def sterretjes(name, pts, ceiling=24.0, col='#f2c94c', size=0.8, seed=3):
    """Papieren sterretjes aan draadjes, hangend van het plafond."""
    rnd = np.random.default_rng(seed)
    m = H.paper(col, rough=0.7, key=f'papierster_{col}', fiber=0.05)
    dr = H.thread('#e8e2d6', key='draadje_wit')
    for k, (x, y, z) in enumerate(pts):
        st = K.poly_obj(f'{name}{k}', K.round_star_pts(size, 0.5), depth=0.02, bevel=0.006, mat=m, loc=(x, y, z),
                        rot=(math.pi / 2, 0, rnd.uniform(-0.6, 0.6)))
        K.curve_tube(f'{name}_draad{k}', [(x, y, z + size * 0.95), (x, y, ceiling)], 0.008, dr)
    return None


def bedje(name, loc=(0, 0, 0), rot=0.0, parent=None):
    """Bedje van een laatje van een lucifersdoosje, met een wattenschijfje als kussen en een zakdoek als deken."""
    root = K.empty(name, loc, (0, 0, math.radians(rot)), parent=parent)
    karton = H.paper('#efeae0', rough=0.85, key='karton_wit', fiber=0.06)
    L, W, Hh, t = 5.2, 3.4, 1.25, 0.04
    H.box(name + '_bodem', L, W, t, karton, loc=(0, 0, t / 2), bev=0.01, parent=root)
    for sy in (-1, 1):
        H.box(name + f'_zij{sy}', L, t, Hh, karton, loc=(0, sy * (W / 2 - t / 2), Hh / 2), bev=0.01, parent=root)
    for sx in (-1, 1):
        H.box(name + f'_kop{sx}', t, W, Hh, karton, loc=(sx * (L / 2 - t / 2), 0, Hh / 2), bev=0.01, parent=root)
    watten = H._new(name + '_watten') if (name + '_watten') not in H._M else H._M[name + '_watten']
    g = H.G(watten)
    tc = g.node('ShaderNodeTexCoord')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (30, 30, 30)), 1.0, 6.0, 0.7)
    g.bsdf('#f7f5f0', 0.95, sheen=1.0, normal=g.bump(n, 0.5, 0.02))
    K.blob(name + '_kussen', (0.75, 1.3, 0.3), 2.6, (48, 24), mat=watten, parent=root, loc=(-L / 2 + 1.0, 0, Hh * 0.75))
    K.blob(name + '_matras', (L / 2 - 0.15, W / 2 - 0.15, 0.25), 4.0, (48, 24), mat=watten, parent=root, loc=(0, 0, 0.35))
    # zakdoek met ruitjes als deken
    key = 'zakdoek'
    if key in H._M:
        zk = H._M[key]
    else:
        zk = H._new(key)
        g = H.G(zk)
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        a = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', x, 0.5)), 0.5)
        b = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', y, 0.5)), 0.5)
        c = g.math('ADD', g.math('MULTIPLY', a, 0.5), g.math('MULTIPLY', b, 0.5))
        col = g.ramp(c, [(0.0, '#f3ece0'), (0.45, '#f3ece0'), (0.5, '#e7a0a0'), (0.95, '#e7a0a0'), (1.0, '#c9473b')])
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (60, 60, 60)), 1.0, 2.0)
        g.bsdf(col, 0.85, sheen=0.8, normal=g.bump(n, 0.2, 0.004))
    nx, ny = 24, 18
    V = []
    for i in range(nx):
        for j in range(ny):
            u, v = i / (nx - 1), j / (ny - 1)
            x = -L / 2 + 1.8 + u * (L - 1.4)
            y = (v - 0.5) * (W + 0.8)
            zz = 0.9 + 0.25 * math.sin(u * 3.0) * math.cos((v - 0.5) * 2.6)
            if abs(y) > W / 2 - 0.05:
                zz -= (abs(y) - (W / 2 - 0.05)) * 2.2
            V.append((x, y, zz))
    F = [(i * ny + j, (i + 1) * ny + j, (i + 1) * ny + j + 1, i * ny + j + 1) for i in range(nx - 1) for j in range(ny - 1)]
    dk = K.mesh_obj(name + '_deken', V, F, zk, root)
    K.modifier(dk, 'SOLIDIFY', thickness=0.05, offset=0.0)
    return root


def _curve2d(name, splines, depth, bevel, mat, parent=None):
    """Vlakke vorm (eerste spline = buitenrand, volgende = gaten), dikte 2*depth langs z."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = depth
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    for pts in splines:
        sp = cu.splines.new('POLY')
        sp.points.add(len(pts) - 1)
        for pt, (x, y) in zip(sp.points, pts):
            pt.co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    return K.link(ob, parent)


def _smooth_loop(pts, n=6):
    P = np.array(pts + pts[:3], float)
    out = []
    for i in range(len(pts)):
        p0, p1, p2, p3 = P[i - 1] if i > 0 else P[len(pts) - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    return out


def handzaag(name, L=2.4, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, wood=None):
    """Gewone handzaag: taps blad met tanden en een gaatje bij de punt, een dichte houten greep met een gat voor
    de hand en drie schroefjes. Oorsprong = midden van de greep (daar zit de hand). Blad naar +x, tanden naar -z."""
    ob = K.empty(name, loc, rot, parent=parent)
    th = 0.014
    st = H.metal('#c4c8cb', 0.18, key='zaagblad')
    x0, yb = 0.22, -0.5
    n = 44
    pts = []
    for k in range(n + 1):
        x = x0 + (L - x0) * k / n
        pts.append((x, yb - (0.035 if k % 2 == 0 else 0.0)))
    pts += [(L, yb + 0.2), (L - 0.06, yb + 0.25), (x0 + 0.3, 0.12), (x0 - 0.1, 0.14)]
    bl = H.prism(name + '_blad', pts, th, st, bev=0.0, parent=ob, angle=60)
    bl.rotation_euler = (math.pi / 2, 0, 0)
    bl.location = (0, th / 2, 0)
    dark = H.plastic('#2a2622', 0.6, key='gaatje')
    for sy in (-1, 1):
        H.cyl(name + f'_gaatje{sy}', 0.05, 0.004, dark, loc=(L - 0.17, sy * (th / 2 + 0.001), yb + 0.12),
              rot=(math.pi / 2, 0, 0), bev=0.0, seg=16, parent=ob)
    # greep: 2D-vorm met een gat, in het xz-vlak
    dx, dz = 0.13, 0.05
    outer = [(0.62, -0.5), (0.68, 0.02), (0.56, 0.3), (0.3, 0.43), (0.0, 0.47), (-0.22, 0.41), (-0.3, 0.2),
             (-0.25, -0.12), (-0.17, -0.41), (-0.04, -0.56), (0.22, -0.6)]
    hs = 0.66
    outer = [((x + dx) * hs, (z + dz) * hs) for x, z in outer]
    hole = []
    for k in range(28):
        a = 2 * math.pi * k / 28
        x, z = 0.14 * math.cos(a), 0.29 * math.sin(a)
        c, s_ = math.cos(math.radians(-14)), math.sin(math.radians(-14))
        hole.append(((0.16 + dx + x * c - z * s_) * hs, (-0.04 + dz + x * s_ + z * c) * hs))
    hm = wood or H.wood('beuk', 'X', key='zaaggreep', coat=0.2)
    gr = _curve2d(name + '_greep', [_smooth_loop(outer, 6), hole[::-1]], 0.06, 0.02, hm, ob)
    gr.rotation_euler = (math.pi / 2, 0, 0)
    for k, (x, z) in enumerate(((0.5, -0.02), (0.5, -0.24), (0.6, 0.16))):
        for sy in (-1, 1):
            H.cyl(f'{name}_schroef{k}{sy}', 0.045, 0.02, H.metal('#d4ad5c', 0.25, key='messing'),
                  loc=(x, sy * 0.095, z), rot=(math.pi / 2 * sy, 0, 0), bev=0.008, seg=16, parent=ob)
    return ob


def klauwhamer(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=1.9):
    """Klauwhamer: houten steel, stalen kop met klauw. Steel langs -z vanaf de kop."""
    ob = K.empty(name, loc, rot, parent=parent)
    H.cyl(name + '_steel', 0.085, L, H.wood('eiken', 'Z', key='steel_essen', coat=0.15), loc=(0, 0, -L), bev=0.04, seg=16,
          parent=ob, r_top=0.075)
    st = H.metal('#9da1a5', 0.3, key='hamerstaal')
    H.cyl(name + '_kop', 0.12, 0.45, st, loc=(0.0, 0, 0.0), rot=(0, math.pi / 2, 0), bev=0.03, seg=20, parent=ob)
    H.cyl(name + '_slag', 0.15, 0.12, st, loc=(0.42, 0, 0.0), rot=(0, math.pi / 2, 0), bev=0.03, seg=20, parent=ob)
    pts = [(0.0, 0, 0.03), (-0.25, 0, 0.05), (-0.45, 0, -0.02), (-0.58, 0, -0.16)]
    for sy in (-0.035, 0.035):
        K.curve_tube(name + f'_klauw{sy}', [(x, sy, z) for x, _, z in pts], 0.045, st, ob)
    return ob


def schroevendraaier(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, hout=False):
    ob = K.empty(name, loc, rot, parent=parent)
    hm = (H.wood('beuk', 'Z', key='heft_hout', coat=0.2) if hout else
          H.wood('beuk', 'Z', paint='#c8392f', grain=0.12, coat=0.4, key='schroevendraaier_heft'))
    K.lathe(name + '_heft', [(0, 0), (0.12, 0.02), (0.15, 0.25), (0.14, 0.62), (0.1, 0.72), (0.05, 0.75), (0, 0.76)], 24, hm, ob)
    H.cyl(name + '_schacht', 0.035, 0.95, H.metal('#c9c9c9', 0.2, key='speldstaal'), loc=(0, 0, -0.95), bev=0.005, seg=12, parent=ob)
    H.box(name + '_punt', 0.1, 0.02, 0.12, H.metal('#c9c9c9', 0.2, key='speldstaal'), loc=(0, 0, -0.98), bev=0.005, parent=ob)
    return ob


def beitel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    ob = K.empty(name, loc, rot, parent=parent)
    K.lathe(name + '_heft', [(0, 0), (0.1, 0.0), (0.12, 0.08), (0.11, 0.7), (0.13, 0.76), (0.12, 0.82), (0, 0.84)], 20,
            H.wood('eiken', 'Z', key='beitel_heft', coat=0.15), ob)
    H.box(name + '_blad', 0.2, 0.05, 0.75, H.metal('#a9adb0', 0.25, key='beitelstaal'), loc=(0, 0, -0.37), bev=0.01, parent=ob)
    return ob


def _zet(ob, onder, p, rx=0.0, ry=0.0, rz=0.0, sc=1.0):
    """Zet een gereedschap zo neer dat zijn lokale punt `onder` precies op `p` staat, gekanteld met (rx, ry, rz)."""
    R = Euler((rx, ry, rz), 'XYZ').to_matrix().to_4x4()
    ob.matrix_basis = Matrix.Translation(Vector(p)) @ R @ Matrix.Scale(sc, 4) @ Matrix.Translation(-Vector(onder))
    return ob


def gereedschapskist(name, loc=(0, 0, 0), rot=0.0, parent=None, tools=True, s=0.85, omgeving=False):
    """De oude houten gereedschapskist van opa, naar zijn tekening: een open bak met twee hoge kopse kanten met een
    ronde bovenkant en een rond handgat, zijkanten van een brede plank met spijkerkopjes, verweerd hout. Het
    gereedschap staat er rechtop in: beitel, schroevendraaier en klauwhamer met de steel omlaag, een liniaal schuin
    omhoog, en de handzaag met het blad in de kist en de greep schuin boven de rand. Bij s = 1 is de kist 2,6 lang."""
    root = K.empty(name, loc, (0, 0, math.radians(rot)), parent=parent)
    root.scale = (s, s, s)
    oud = ('#a98a64', '#7a5e40')
    oud = ('#a8957a', '#957f65')
    m = H.wood('eiken', 'X', var=0.06, key='kist_hout3', tint=oud, rough=0.8)
    mz = H.wood('eiken', 'Y', var=0.06, key='kist_hout_kop3', tint=oud, rough=0.8)
    L, W, t, hw, gh = 2.6, 1.35, 0.1, 1.2, 2.1
    # bodem en zijplanken (een brede plank per kant, over de kopse kanten heen)
    H.box(name + '_bodem', L - 0.02, W - 2 * t, t, m, loc=(0, 0, 0), bev=0.03, base=True, parent=root)
    for sy in (-1, 1):
        H.box(f'{name}_zij{sy}', L, t, hw, m, loc=(0, sy * (W / 2 - t / 2), 0), bev=0.03, base=True, parent=root)
    # kopse kanten: recht omhoog en dan een halve cirkel, met een rond handgat
    wi = W - 2 * t
    r_ = wi / 2
    za = gh - r_
    prof = [(-r_, 0), (r_, 0), (r_, za)]
    for k in range(1, 18):
        a_ = math.radians(180 * k / 18)
        prof.append((r_ * math.cos(a_), za + r_ * math.sin(a_)))
    prof.append((-r_, za))
    hc = gh - 0.5
    hole = [(0.2 * math.cos(2 * math.pi * k / 28), hc + 0.17 * math.sin(2 * math.pi * k / 28)) for k in range(28)][::-1]
    for sx in (-1, 1):
        g = _curve2d(name + f'_kop{sx}', [prof, hole], t / 2, 0.025, mz, root)
        g.rotation_euler = (math.pi / 2, 0, math.pi / 2)
        g.location = (sx * (L / 2 - t / 2 - 0.01), 0, 0)
    nail = H.metal('#4a443d', 0.45, key='spijkerkop_oud')
    for sx in (-1, 1):
        for sy in (-1, 1):
            for zz in (0.3, 0.9):
                H.cyl(f'{name}_nagel{sx}{sy}{zz}', 0.032, 0.015, nail, loc=(sx * (L / 2 - t / 2), sy * (W / 2 + 0.001), zz),
                      rot=(-sy * math.pi / 2, 0, 0), bev=0.006, seg=10, parent=root)
        for xx in (-0.75, 0.75):
            H.cyl(f'{name}_bodemnagel{sx}{xx}', 0.032, 0.015, nail, loc=(xx, sx * (W / 2 + 0.001), 0.05),
                  rot=(-sx * math.pi / 2, 0, 0), bev=0.006, seg=10, parent=root)
    if tools:
        zb = t + 0.01
        # beitel en schroevendraaier links, heft omhoog
        _zet(beitel(name + '_beitel', parent=root), (0, 0, -0.745), (-0.92, 0.0, zb), rx=0.1, ry=-0.1, rz=0.3, sc=1.45)
        _zet(schroevendraaier(name + '_schroef', parent=root, hout=True), (0, 0, -0.98), (-0.52, 0.26, zb), rx=-0.06, ry=-0.12, sc=1.4)
        # klauwhamer in het midden, kop boven
        _zet(klauwhamer(name + '_hamer', parent=root, L=2.0), (0, 0, -2.0), (-0.1, 0.22, zb), rx=-0.07, ry=0.08, rz=0.5, sc=1.02)
        # liniaal schuin omhoog naar rechts, achterin
        lat = liniaal(name + '_lat', (0, 0, 0), parent=root, L=2.9, W=0.3, T=0.06)
        R2 =Matrix.Rotation(-math.radians(70), 4, 'Y') @ Matrix.Rotation(math.pi / 2, 4, 'X')
        lat.matrix_basis = Matrix.Translation(Vector((0.2, 0.42, zb + 0.15))) @ R2 @ Matrix.Translation(Vector((1.45, 0, 0)))
        # timmermanspotlood, schuin tegen de achterkant
        pl = H.box(name + '_potlood', 1.0, 0.24, 0.1, H.wood('ceder', 'X', paint='#c8392f', grain=0.1, coat=0.4, key='timmerpotlood'),
                   bev=0.025, parent=root)
        pl.matrix_basis = (Matrix.Translation(Vector((0.55, 0.36, zb + 0.32))) @ Matrix.Rotation(math.radians(-55), 4, 'Y') @
                           Matrix.Rotation(math.radians(80), 4, 'X'))
        # handzaag: greep schuin boven de rechterkant, blad omlaag de kist in (tanden naar linksboven)
        G = Vector((0.82, -0.38, 2.3))
        T_ = Vector((-0.7, -0.38, 0.3))
        d = (T_ - G).normalized()
        X = d
        Y = Vector((0, 1, 0))
        Z = X.cross(Y)
        Rz = Matrix((X, Y, Z)).transposed().to_4x4()
        zg = handzaag(name + '_zaag', L=(T_ - G).length, parent=root)
        zg.matrix_basis = Matrix.Translation(G) @ Rz
        for k in range(3):
            spijkertje(f'{name}_spijker{k}', (0.1 + 0.18 * k, -0.15 + 0.11 * k, t + 0.04), rot=(0, math.pi / 2, 0.35 * k - 0.3),
                       parent=root, L=0.55)
    if omgeving:
        blok = H.wood('grenen', 'X', key='blokje')
        H.box(name + '_blokje', 1.1, 0.65, 0.5, blok, loc=(2.2, -1.2, 0), rot=(0, 0, 0.3), bev=0.05, base=True, parent=root)
        for k in range(2):
            spijkertje(f'{name}_losse_spijker{k}', (1.8 + 0.5 * k, -1.9 + 0.2 * k, 0.06), rot=(math.pi / 2, 0, 1.2 + k), parent=root,
                       L=0.8)
    return root


def rolmaat(name, loc=(0, 0, 0), rot=0.0, parent=None, uit=4.0):
    """Rolmaat: geel met zwart, het meetlint een stukje uitgetrokken."""
    root = K.empty(name, loc, (0, 0, math.radians(rot)), parent=parent)
    geel = H.plastic('#f0b929', 0.35, key='rolmaat_geel', coat=0.3)
    zwart = H.plastic('#26231f', 0.5, key='rolmaat_zwart')
    K.blob(name + '_huis', (1.75, 0.8, 1.75), (6.0, 3.0, 6.0), (64, 32), mat=geel, parent=root, loc=(0, 0, 1.75))
    for sy in (-1, 1):
        K.blob(name + f'_rubber{sy}', (1.5, 0.12, 1.5), (5.0, 2.0, 5.0), (48, 24), mat=zwart, parent=root,
               loc=(0, sy * 0.78, 1.75))
    H.box(name + '_knop', 0.5, 0.5, 0.35, zwart, loc=(0.6, 0, 3.45), bev=0.1, parent=root)
    tape = H.paper('#f2c230', os.path.join(H.TEX, 'meetlint.png'), rough=0.35, key='meetlint', src='GEN', fiber=0.02)
    H.box(name + '_lint', uit, 0.95, 0.03, tape, loc=(1.6 + uit / 2, 0, 0.05), bev=0.0, parent=root)
    H.box(name + '_haakje', 0.06, 0.95, 0.35, H.metal('#b8b8b8', 0.3, key='staal'), loc=(1.6 + uit, 0, 0.18), bev=0.01, parent=root)
    return root


def theelichtje(name, loc=(0, 0, 0), parent=None):
    al = H.metal('#d8dade', 0.18, key='aluminium_cup')
    ob = K.lathe(name, [(0, 0), (1.86, 0), (1.9, 0.05), (1.92, 1.55), (1.86, 1.6), (1.82, 1.6), (1.82, 0.08), (0, 0.08)], 96, al, parent)
    ob.location = loc
    was = H.plastic('#f7f3ea', 0.6, key='was')
    H.cyl(name + '_was', 1.8, 1.4, was, loc=(0, 0, 0.08), bev=0.03, seg=64, parent=ob)
    K.curve_tube(name + '_lontje', [(0, 0, 1.45), (0.03, 0, 1.75), (0.1, 0.02, 1.9)], 0.03, H.plastic('#2a2420', 0.7, key='lont'), ob)
    return ob


def muntstapel(name, loc=(0, 0, 0), n=4, parent=None, seed=0):
    """Stapeltje euromunten (2 euro): zilveren rand, gouden hart."""
    rnd = np.random.default_rng(seed)
    root = K.empty(name, loc, parent=parent)
    zil = H.metal('#c9ccd0', 0.22, key='munt_zilver')
    goud = H.metal('#d7b25a', 0.24, key='munt_goud')
    for k in range(n):
        dx, dy = rnd.normal(0, 0.06, 2)
        H.cyl(f'{name}_rand{k}', 1.29, 0.21, zil, loc=(dx, dy, k * 0.22), bev=0.04, seg=64, parent=root)
        H.cyl(f'{name}_hart{k}', 0.92, 0.215, goud, loc=(dx, dy, k * 0.22 - 0.0025), bev=0.03, seg=48, parent=root)
    return root


def bolletje_wol(name, loc, R=2.2, col='#c8473b', parent=None):
    key = f'wol_{col}'
    if key in H._M:
        m = H._M[key]
    else:
        m = H._new(key)
        g = H.G(m)
        tc = g.node('ShaderNodeTexCoord')
        v = tc.outputs['Object']
        lines = None
        for k, rr in enumerate(((0.3, 0.2, 0.1), (1.2, 0.3, 0.6), (0.1, 1.3, 0.2), (0.7, 0.9, 1.4))):
            mp = g.node('ShaderNodeMapping', vector_type='POINT')
            mp.inputs['Rotation'].default_value = rr
            g.link(v, mp.inputs['Vector'])
            w = g.node('ShaderNodeTexWave')
            w.wave_type = 'BANDS'
            w.inputs['Scale'].default_value = 1.2
            w.inputs['Distortion'].default_value = 2.0
            g.link(mp.outputs[0], w.inputs['Vector'])
            f = w.outputs['Fac']
            lines = f if lines is None else g.math('MAXIMUM', lines, g.math('MULTIPLY', f, 0.9))
        col_ = g.mul(col, g.math('ADD', 0.7, g.math('MULTIPLY', lines, 0.35)))
        g.bsdf(col_, 0.9, sheen=1.0, normal=g.bump(lines, 0.6, 0.05))
    ob = H.ball(name, R, m, loc=loc, parent=parent, res=(64, 32))
    K.curve_tube(name + '_draad', [(R * 0.7, -R * 0.6, -R * 0.2), (R * 1.2, -R * 1.0, -R * 0.8), (R * 1.8, -R * 1.1, -R + 0.05),
                                   (R * 2.6, -R * 0.8, -R + 0.05)], 0.08, m, ob)
    return ob


def sleutel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, s=1.0):
    """Gewone huissleutel (cilindersleutel), plat in het xy-vlak."""
    m = H.metal('#c8c2b0', 0.22, key='sleutel_metaal')
    head = []
    for k in range(40):
        a = 2 * math.pi * k / 40
        head.append((-1.3 * s + 1.0 * s * math.cos(a), 1.0 * s * math.sin(a) * 0.95))
    hole = [(-1.8 * s + 0.22 * s * math.cos(2 * math.pi * k / 20), 0.22 * s * math.sin(2 * math.pi * k / 20)) for k in range(20)][::-1]
    blade = [(-0.4 * s, -0.32 * s), (2.6 * s, -0.32 * s), (2.9 * s, -0.05 * s), (2.6 * s, 0.32 * s)]
    teeth = [(2.3 * s, 0.32 * s), (2.1 * s, 0.12 * s), (1.85 * s, 0.32 * s), (1.6 * s, 0.18 * s), (1.35 * s, 0.32 * s),
             (1.1 * s, 0.1 * s), (0.85 * s, 0.32 * s), (-0.4 * s, 0.32 * s)]
    outline = blade + teeth
    a = _curve2d(name, [head, hole], 0.1 * s, 0.03 * s, m, parent)
    b = _curve2d(name + '_baard', [outline], 0.07 * s, 0.02 * s, m, a)
    a.location, a.rotation_euler = loc, rot
    return a


def losse_elastiekjes(name, center, n=3, seed=1, col='#d9a441'):
    rnd = np.random.default_rng(seed)
    for k in range(n):
        cx, cy = center[0] + rnd.normal(0, 0.8), center[1] + rnd.normal(0, 0.8)
        r = rnd.uniform(1.2, 1.8)
        pts = [(cx + r * math.cos(a) * (1 + 0.15 * math.sin(3 * a + k)), cy + r * math.sin(a) * 0.7, 0.05 + 0.03 * math.sin(2 * a))
               for a in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
        K.curve_tube(f'{name}{k}', pts, 0.05, H.plastic(col, 0.6, key=f'elastiek_{col}'), cyclic=True)


def duimstok_ladder(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=7.0):
    """Stukje gele duimstok als ladder, met tandenstokers als sporten."""
    ob = K.empty(name, loc, rot, parent=parent)
    d = H.paper('#f2c230', os.path.join(H.TEX, 'duimstok.png'), rough=0.4, key='duimstok', src='GEN', fiber=0.02)
    H.box(name + '_lat', L, 1.6, 0.3, d, loc=(L / 2, 0, 0.15), bev=0.03, parent=ob)
    st = H.wood('berk', 'Z', key='tandenstoker')
    # sporten precies op de centimeterstreepjes (de textuur heeft 10 cm over de hele lengte), dus nooit over een cijfer
    for k in range(5):
        x = L * (2 * k + 1) / 10
        H.cyl(f'{name}_sport{k}', 0.06, 1.5, st, loc=(x, -0.75, 0.32), rot=(-math.pi / 2, 0, 0), bev=0.02, seg=10, parent=ob)
    return ob
