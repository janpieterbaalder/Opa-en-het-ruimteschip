"""Het schip van opa en Joah, gebouwd uit spullen uit huis (zoals op opa's bouwtekening).

Romp: rond houten kaasdoosje (camembert) met deksel als dek, op drie wasknijpers met knoopjes als
voetjes. Hutje: rood geverfd lucifersdoosje met deurtje en knoop als raampje, dak van ijsstokjes,
vingerhoed als schoorsteen. Propeller van ijsstokjes op een garenklosje. Vleugels van wasknijpers.
Motor: garenklos achterop met een kerstlampje erin. Raampjes van knoopjes, gouden ster voorop.
Op het dek twee stoeltjes met een paperclip als rugleuning en een tandwieltje als stuur.

Voorkant van het schip = -y. Oorsprong op de grond in het midden.
"""
import bpy, math, os
import numpy as np
from mathutils import Vector
from . import core as K, hout as H, spullen as SP, voorwerpen as VW

R = 5.6          # straal kaasdoosje
HB = 2.9         # onderkant romp (pootjes eronder)
HWALL = 3.0      # hoogte doosje
DECK = HB + 3.42 # bovenkant deksel = dek

ROOD = '#c8392f'
BLAUW = '#3561a8'
GROEN = '#3f8a55'
GOUD = '#d6a640'


def _goud():
    return H.metal(GOUD, 0.28, key='goudverf')


def tandwiel(name, r=0.8, n=18, t=0.12, mat=None, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Tandwieltje uit een oude klok (messing), in het xy-vlak."""
    mat = mat or H.metal('#cfa452', 0.25, key='messing_klok')
    pts = []
    for k in range(n * 4):
        a = 2 * math.pi * k / (n * 4)
        ph = k % 4
        rr = r if ph in (1, 2) else r * 0.86
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    ob = H.prism(name, pts, t, mat, loc=loc, rot=rot, bev=0.012, seg=1, parent=parent, angle=60)
    H.cyl(name + '_as', r * 0.14, t + 0.12, mat, loc=(0, 0, -0.06), bev=0.02, seg=24, parent=ob)
    for k in range(5):
        a = 2 * math.pi * k / 5
        H.cyl(name + f'_gat{k}', r * 0.17, t + 0.004, H.plastic('#2a2420', 0.6, key='tandwielgat'),
              loc=(math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, -0.002), bev=0.0, seg=20, parent=ob)
    return ob


def theezakjeslabel(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), w=1.5, h=1.15):
    m = H.paper('#f1d36b', rough=0.8, key='theelabel', fiber=0.05)
    ob = K.mesh_obj(name, [(0, -h / 2, 0), (w, -h / 2, 0), (w, h / 2, 0), (0, h / 2, 0)], [(0, 1, 2, 3)], m, parent,
                    loc=loc, rot=rot)
    K.modifier(ob, 'SOLIDIFY', thickness=0.02, offset=0.0)
    # rand en een getekend kopje
    ink = H.plastic('#8a5a2a', 0.6, key='theelabel_inkt')
    K.curve_tube(name + '_rand', [(0.1, -h / 2 + 0.1, 0.012), (w - 0.1, -h / 2 + 0.1, 0.012), (w - 0.1, h / 2 - 0.1, 0.012),
                                  (0.1, h / 2 - 0.1, 0.012)], 0.012, ink, ob, cyclic=True)
    return ob


def bouw(loc=(0, 0, 0), rot=0.0, stage='klaar', lights=False, flag=True, parent=None, seats=True, wheel=True):
    before = set(bpy.data.objects)
    out = _bouw(loc, rot, stage, lights, flag, parent, seats, wheel)
    root = out['root']
    for ob in bpy.data.objects:
        if ob not in before and ob is not root and ob.parent is None:
            ob.parent = root
    return out


def _bouw(loc, rot, stage, lights, flag, parent, seats, wheel):
    """stage: 'doos' (alleen het kaasdoosje met deksel), 'bouw' (romp, pootjes, hutje, één vleugel; ongeverfd),
    'verf' (alles erop, geverfd, ster net klaar), 'klaar'. Geeft een dict met dek-hoogte en zitplaatsen."""
    root = K.empty('schip', loc, (0, 0, math.radians(rot)), parent=parent)
    painted = stage in ('verf', 'klaar')
    hull = H.wood('populier', 'X', var=0.05, key='kaasdoos')
    out = dict(root=root, deck=DECK, seats={'L': (-1.35, -1.7), 'R': (1.45, -1.7)})

    hb = HB if stage != 'doos' else 0.0
    # ---------------------------------------------------- romp: kaasdoosje + deksel
    base = [(0, hb), (R - 0.05, hb), (R, hb + 0.05), (R, hb + HWALL), (R - 0.12, hb + HWALL), (R - 0.12, hb + 0.15),
            (0, hb + 0.15)]
    K.lathe('romp', base, 128, hull, root)
    lid = [(0, hb + 3.28), (R - 0.02, hb + 3.28), (R - 0.02, hb + 2.2), (R + 0.1, hb + 2.2), (R + 0.13, hb + 2.26),
           (R + 0.13, hb + 3.36), (R + 0.06, hb + 3.42), (0, hb + 3.42)]
    K.lathe('deksel', lid, 128, hull, root)
    # naad van het gebogen fineer
    H.box('naad', 0.9, 0.03, HWALL - 0.3, hull, loc=(R * math.cos(1.2), R * math.sin(1.2), hb + 1.2),
          rot=(0, 0, 1.2 + math.pi / 2), bev=0.01)
    if stage == 'doos':
        return out
    deck = DECK

    # ---------------------------------------------------- pootjes: wasknijpers met knoopjes als voetjes
    for k, a in enumerate((-145, -35, 90)):
        ar = math.radians(a)
        x, y = R * math.cos(ar), R * math.sin(ar)
        SP.knijpertje(f'poot{k}', loc=(x, y, 0.22), rot=(0, -math.pi / 2, ar + math.pi / 2), L=hb + 1.1)
        SP.knoop(f'voetje{k}', (x * 1.02, y * 1.02, 0.0), '#e7b23b' if not painted else ('#d8473a', '#3f73b5', '#3f8a55')[k],
                 r=0.75, rot=(0, 0, 0.3 * k))

    # ---------------------------------------------------- raampjes (knopen) en de gouden ster
    zr = hb + 1.45
    kc = ['#f4f1ea', '#e7b23b', '#f4f1ea', '#e7b23b']
    for k, b in enumerate((-90 - 62, -90 - 30, -90 + 30, -90 + 62)):
        br = math.radians(b)
        SP.knoop(f'patrijspoort{k}', ((R + 0.02) * math.cos(br), (R + 0.02) * math.sin(br), zr), kc[k], r=0.55,
                 rot=(math.pi / 2, 0, br + math.pi / 2))
    if stage in ('verf', 'klaar'):
        st = K.poly_obj('ster', K.round_star_pts(1.05, 0.5), depth=0.03, bevel=0.012, mat=_goud(),
                        loc=(0, -(R + 0.02), zr), rot=(math.pi / 2, 0, 0))

    # ---------------------------------------------------- hutje: lucifersdoosje
    cab = H.wood('populier', 'X', paint=ROOD if painted else None, grain=0.15, rough=0.45, key=f'hut_{painted}')
    cw, cd, ch = 5.3, 1.6, 3.6
    cy = 2.55
    H.box('hut', cw, cd, ch, cab, loc=(0, cy, deck), bev=0.04, base=True)
    door = H.wood('berk', 'Z', key='deurtje')
    for k in (0, 1):
        H.box(f'deur{k}', 0.5, 0.06, 2.3, door, loc=(-1.05 + k * 0.52, cy - cd / 2 - 0.02, deck + 0.02), bev=0.03, base=True)
    H.ball('deurknop', 0.09, H.metal('#d4ad5c', 0.25, key='messing'), loc=(-0.65, cy - cd / 2 - 0.1, deck + 1.2))
    SP.knoop('hutraam', (1.2, cy - cd / 2 - 0.03, deck + 2.15), '#f4f1ea' if painted else '#e7b23b', r=0.5,
             rot=(math.pi / 2, 0, 0))
    # dak van ijsstokjes
    rf = H.wood('berk', 'X', paint=BLAUW if painted else None, grain=0.15, key=f'dak_{painted}')
    for side in (-1, 1):
        for k in range(2):
            ang = math.radians(32) * side
            yy = cy + side * (0.45 + k * 0.95) * math.cos(math.radians(32))
            zz = deck + ch + 0.95 - (0.45 + k * 0.95) * math.sin(math.radians(32))
            H.prism(f'dak{side}{k}', H.stadium_pts(6.0, 1.0, 10), 0.2, rf, bev=0.04, loc=(0, yy, zz), rot=(-ang, 0, 0))
    ridge = deck + ch + 1.05
    # schoorsteen: vingerhoed (opening naar boven)
    SP.vingerhoed('schoorsteen', (1.6, cy + 0.3, ridge + 0.75), rot=(math.pi, 0, 0), R=0.5, Hh=1.3)

    # ---------------------------------------------------- propeller van ijsstokjes op een klosje
    SP.garenklos('propklos', '#e7b23b' if painted else '#d8d2c4', loc=(-0.9, cy, ridge - 0.25), R=0.42, Hh=1.0, core=0.25,
                 fill=0.8)
    pr = K.empty('propeller', (-0.9, cy, ridge + 0.85), (0, 0, math.radians(20)), parent=root)
    for k in range(2):
        blade = SP.ijsstokje(f'blad{k}', (0, 0, 0.11 * k), (0, 0, math.radians(90 * k)), parent=pr)
        if painted:
            tip = H.wood('berk', 'X', paint=GROEN, grain=0.12, key='groene_punt')
            for s_ in (-1, 1):
                H.prism(f'bladpunt{k}{s_}', H.stadium_pts(2.2, 1.04, 10), 0.215, tip, bev=0.04,
                        loc=(s_ * 4.6 * math.cos(math.radians(90 * k)), s_ * 4.6 * math.sin(math.radians(90 * k)), 0.11 * k - 0.006),
                        rot=(0, 0, math.radians(90 * k)), parent=pr)
    H.ball('propdop', 0.28, H.plastic('#d8473a', 0.3, key='propdop'), loc=(0, 0, 0.35), parent=pr)

    # ---------------------------------------------------- vleugels: wasknijpers
    wing = H.wood('beuk', 'X', paint=BLAUW if painted else None, grain=0.15, key=f'vleugel_{painted}')
    for side in ((-1, 1) if stage != 'bouw' else (-1,)):
        L = 7.2
        x0 = side * (R + L - 1.0)
        knp = SP.knijpertje(f'vleugel{side}', loc=(x0, 0.4, hb + 1.9), rot=(math.pi / 2, math.radians(10), 0 if side < 0 else math.pi),
                            L=L)
        if painted and not (stage == 'verf' and side > 0):
            for c in knp.children:
                if c.type == 'MESH' and 'helft' in c.name:
                    c.data.materials.clear()
                    c.data.materials.append(wing)
    out['wing_free'] = (R + 7.2 - 1.0, 0.4, hb + 1.9)

    # ---------------------------------------------------- motor: garenklos achterop met een lampje
    if stage != 'bouw':
        SP.garenklos('motor', '#d8473a' if painted else '#c9c2b2', loc=(0, R + 2.45, hb + 1.5), rot=(math.pi / 2, 0, 0),
                     R=1.05, Hh=2.5, core=0.55, fill=0.85)
        K.blob('motorgloed', (0.2, 0.2, 0.2), 2.0, (24, 12), mat=H.bulb('#ffb35c', 40.0 if lights else 4.0),
               parent=root, loc=(0, R + 2.5, hb + 1.5))
        if lights:
            L_ = K.light('POINT', (0, R + 2.7, hb + 1.5), energy=120, color=(1.0, 0.6, 0.25), size=0.25, name='motorlicht')
            L_.parent = root

    # ---------------------------------------------------- vlaggetje: labeltje van een theezakje
    if flag and stage == 'klaar':
        H.cyl('vlagstok', 0.06, 4.0, H.wood('berk', 'Z', key='tandenstoker'), loc=(2.3, cy + 0.5, ridge - 0.9), bev=0.02, seg=12)
        K.curve_tube('vlagdraad', [(2.3, cy + 0.5, ridge + 2.9), (2.55, cy + 0.5, ridge + 2.75), (2.75, cy + 0.5, ridge + 2.55)],
                     0.012, H.thread('#f4f1ea', key='draadje_wit'), root)
        theezakjeslabel('vlag', root, loc=(2.36, cy + 0.5, ridge + 2.45), rot=(math.pi / 2, 0, 0))

    # ---------------------------------------------------- extra's: zeefje, antennes, belletje, boei, anker, reling, ladder
    if stage == 'klaar':
        _extras(root, deck, cy, cd, ch, ridge, hb)

    # ---------------------------------------------------- lampjes op de rand van het dek
    cols = ['#ff5a4a', '#5cff8a', '#ffd25c', '#ffd25c']
    for k, a in enumerate((-130, -50, 150, 30)):
        ar = math.radians(a)
        x, y = (R - 0.45) * math.cos(ar), (R - 0.45) * math.sin(ar)
        H.cyl(f'fitting{k}', 0.16, 0.25, H.metal('#7b6a4f', 0.35, key='fitting'), loc=(x, y, deck), bev=0.03, seg=20)
        K.blob(f'lampje{k}', (0.16, 0.16, 0.26), 2.0, (24, 12), mat=H.bulb(cols[k], 30.0 if lights else 2.5, key=f'lampje{k}_{lights}'),
               parent=root, loc=(x, y, deck + 0.48))
        if lights:
            L_ = K.light('POINT', (x, y, deck + 0.5), energy=18, color=K.srgb(cols[k])[:3], size=0.15, name=f'scheepslamp{k}')
            L_.parent = root

    # ---------------------------------------------------- stoeltjes met paperclip-leuning en het stuur
    if seats:
        seat = H.wood('beuk', 'X', paint='#e7b23b' if painted else None, grain=0.18, key=f'stoel_{painted}')
        for side, (sx, sy) in out['seats'].items():
            H.box(f'stoel{side}', 1.7, 1.35, 1.2, seat, loc=(sx, sy, deck), bev=0.06, base=True)
            SP.paperclip(f'leuning{side}', (sx, sy + 0.6, deck + 1.9), (math.pi / 2, math.radians(90), 0),
                         col='#3f73b5' if side == 'L' else '#d4473a', L=2.0, Wd=1.2, r=0.05)
    if wheel:
        SP.potlood('stuurpaal', '#3f8a55', 1.6, loc=(0.0, -3.7, deck), r=0.22)
        tandwiel('stuur', 0.85, 18, loc=(0.0, -3.55, deck + 1.95), rot=(math.radians(70), 0, 0))
    out['seat_top'] = deck + 1.2
    return out


def _zeef_mat(key='zeefgaas'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    lx = g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', g.math('ADD', x, z), 9.0)), 0.32)
    ly = g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', g.math('SUBTRACT', y, z), 9.0)), 0.32)
    wire = g.math('MAXIMUM', lx, ly)
    b = g.bsdf('#cfd2d6', 0.25, metal=1.0, alpha=wire)
    return m


def _boei_mat(key='boei'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    a = g.math('ARCTAN2', y, x)
    band = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', a, 2 * math.pi / 8)), 0.5)
    g.bsdf(g.mix(band, '#f4f1ea', '#d23b30'), 0.55, sheen=0.4)
    return m


def _extras(root, deck, cy, cd, ch, ridge, hb):
    met = H.metal('#b9bdc2', 0.25, key='breinaald')
    # theezeefje als schotel op het dak
    z = K.empty('zeefje', (2.4, cy - 0.2, ridge - 0.15), (math.radians(-38), math.radians(10), 0))
    prof = [(0.9 * math.sin(math.radians(a)), 0.9 * (1 - math.cos(math.radians(a)))) for a in range(0, 91, 6)]
    bowl = K.lathe('zeef_kom', prof, 48, _zeef_mat(), z, close_top=False, close_bot=False)
    K.modifier(bowl, 'SOLIDIFY', thickness=0.02, offset=0.0)
    K.curve_tube('zeef_rand', [(0.9 * math.cos(a), 0.9 * math.sin(a), 0.9) for a in np.linspace(0, 2 * math.pi, 41)[:-1]], 0.04, met,
                 z, cyclic=True)
    K.curve_tube('zeef_steel', [(0.9, 0, 0.9), (1.5, 0, 0.92), (2.0, 0, 0.95), (2.1, 0.12, 0.95), (2.0, 0.24, 0.95), (1.5, 0.1, 0.92)],
                 0.035, met, z)
    H.cyl('zeef_paal', 0.05, 0.9, met, loc=(0, 0, -0.9), bev=0.01, seg=12, parent=z)
    # breinaalden als antennes met een kraal op de punt
    for k, (x, col, tilt) in enumerate(((-2.3, '#d8473a', -14), (-1.75, '#e7b23b', 6))):
        a = K.empty(f'antenne{k}', (x, cy + 0.3, ridge - 0.6), (math.radians(tilt * 0.5), math.radians(tilt), 0))
        H.cyl(f'antenne{k}_naald', 0.05, 4.4, met, loc=(0, 0, 0), bev=0.02, seg=12, parent=a)
        H.ball(f'antenne{k}_kraal', 0.24, H.plastic(col, 0.25, coat=0.4), loc=(0, 0, 4.45), parent=a, res=(24, 12))
    # belletje aan de hut
    br = H.metal('#d4ad5c', 0.22, key='messing')
    K.curve_tube('bel_draad', [(-2.55, cy - cd / 2 - 0.25, deck + ch + 0.15), (-2.55, cy - cd / 2 - 0.25, deck + ch - 0.4)], 0.015,
                 H.thread('#c8392f', key='draadje_rood'))
    bel = K.lathe('belletje', [(0, 0.55), (0.1, 0.53), (0.18, 0.4), (0.21, 0.18), (0.3, 0.02), (0.29, 0.0), (0.0, 0.05)][::-1], 32, br)
    bel.location = (-2.55, cy - cd / 2 - 0.25, deck + ch - 0.95)
    H.ball('klepel', 0.07, br, loc=(-2.55, cy - cd / 2 - 0.25, deck + ch - 1.0))
    # haarelastiekje als reddingsboei op de hut
    pts = [(0.55 * math.cos(a), 0.55 * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 49)[:-1]]
    bo = K.curve_tube('boei', pts, 0.17, _boei_mat(), cyclic=True)
    bo.location, bo.rotation_euler = (2.15, cy - cd / 2 - 0.2, deck + 1.25), (math.pi / 2, 0, 0)
    # sleuteltje als anker aan een touwtje voorop
    ar = math.radians(-128)
    ax, ay = (R + 0.15) * math.cos(ar), (R + 0.15) * math.sin(ar)
    K.curve_tube('anker_touw', [(ax * 0.97, ay * 0.97, deck - 0.05), (ax, ay, deck - 0.3), (ax * 1.01, ay * 1.01, hb + 1.0)], 0.025,
                 H.thread('#a8834e', key='touw'))
    SP.sleutel('anker', (ax * 1.01, ay * 1.01, hb + 0.95), rot=(math.pi / 2, math.pi / 2, ar + math.pi / 2), s=0.32)
    # reling van tandenstokers met een rood draadje
    st = H.wood('berk', 'Z', key='tandenstoker')
    tops = []
    for a in (-162, -146, -112, -97, -83, -68, -34, -18):
        ar = math.radians(a)
        x, y = (R - 0.25) * math.cos(ar), (R - 0.25) * math.sin(ar)
        H.cyl(f'reling{a}', 0.05, 1.15, st, loc=(x, y, deck - 0.05), bev=0.02, seg=10)
        tops.append((x, y, deck + 1.05))
    K.curve_tube('reling_draad', tops, 0.022, H.thread('#c8392f', key='draadje_rood'))
    # ballonnetjes aan het dak
    for k, (col, ax, ay) in enumerate((('#d8473a', -0.9, -0.5), ('#e7b23b', 0.2, 0.6), ('#3f8a55', 1.0, -0.2))):
        VW.ballon(f'ballon{k}', (0.9, cy + 0.4, ridge + 0.2), rot=(math.radians(ax * 14), math.radians(-ay * 14 + 8), 0),
                  col=col, R=1.05, draad=3.2 + k * 0.7)
    # vlaggenlijn van de vlaggenstok naar de antenne
    a0 = Vector((2.3, cy + 0.5, ridge + 3.0))
    a1 = Vector((-2.3 - 4.4 * math.sin(math.radians(-7)) * 0, cy + 0.3, ridge - 0.6 + 4.2))
    pts = [a0.lerp(a1, t) - Vector((0, 0, 0.9 * math.sin(math.pi * t))) for t in np.linspace(0, 1, 12)]
    K.curve_tube('vlaggenlijn', [tuple(p_) for p_ in pts], 0.012, H.thread('#f4f1ea', key='draadje_wit'))
    for k in range(1, 11):
        p_ = pts[k]
        col = ('#d8473a', '#e7b23b', '#3561a8', '#3f8a55')[k % 4]
        vm = H.paper(col, rough=0.7, key=f'vlagje_{col}', fiber=0.03)
        vm.use_backface_culling = False
        K.mesh_obj(f'vlagje{k}', [(-0.22, 0, 0), (0.22, 0, 0), (0, 0, -0.5)], [(0, 1, 2)], vm, loc=tuple(p_), rot=(0, 0, 0.1 * k))
    # periscoop van een rietje en een wolkje watten uit de schoorsteen
    VW.rietje('periscoop', (0.4, cy + 0.5, ridge - 0.6), rot=(0, 0, math.radians(-90)), L=5.0)
    w = VW._noise_mat('watten', '#ffffff', '#f1ede6', 14.0, 0.95, 0.6, sheen=1.0)
    for k, (dx, dz, r) in enumerate(((0.0, 1.0, 0.55), (0.45, 1.7, 0.7), (1.1, 2.4, 0.85))):
        K.blob(f'rookwolkje{k}', (r, r * 0.9, r * 0.8), 2.0, (32, 16), mat=w, loc=(1.6 + dx, cy + 0.3, ridge + 0.75 + dz),
               deform=lambda D, P: P * (1 + 0.1 * np.sin(D[:, 0] * 9) * np.cos(D[:, 2] * 7))[:, None])
    # propellertjes aan de vleugelpunten (knoop met twee mini-ijsstokjes)
    for side in (-1, 1):
        cx_ = side * (R + 7.2 - 1.0) + side * 0.2
        hub = K.empty(f'vleugelprop{side}', (cx_, 0.4 - 0.75, hb + 1.9 + 0.3 * side * 0), (math.pi / 2, 0, 0))
        SP.knoop(f'vleugelprop{side}_naaf', (0, 0, 0), '#d8473a', r=0.35, parent=hub)
        for k in range(2):
            H.prism(f'vleugelprop{side}_blad{k}', H.stadium_pts(3.0, 0.5, 10), 0.08, H.wood('berk', 'X', key='ijsstokje'),
                    bev=0.03, loc=(0, 0, -0.1), rot=(0, 0, math.radians(40 + 90 * k)), parent=hub)
    # opa's reservebril als rond raampje in de hut en een vlaggetje op het dak
    gl = H.glass('#eef6f7', 0.0)
    for sx in (-1, 1):
        cxx = 1.2 + sx * 0.0
    ring = [(1.25 + 0.42 * math.cos(a), cy - cd / 2 - 0.05, deck + 2.15 + 0.42 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 33)[:-1]]
    K.curve_tube('brilraam_montuur', ring, 0.045, H.metal('#c8c2b6', 0.22, key='brilmontuur'), cyclic=True)
    H.cyl('brilraam_glas', 0.42, 0.03, gl, loc=(1.25, cy - cd / 2 - 0.05, deck + 2.15), rot=(math.pi / 2, 0, 0), bev=0.0, seg=32)
    K.curve_tube('brilraam_poot', [(1.67, cy - cd / 2 - 0.05, deck + 2.25), (2.2, cy - cd / 2 - 0.1, deck + 2.35),
                                   (2.45, cy - cd / 2 - 0.1, deck + 2.1)], 0.035, H.metal('#c8c2b6', 0.22, key='brilmontuur'))
    VW.cocktailprikker('vlaggetje2', (-1.2, cy - 0.5, ridge - 0.5), rot=(math.radians(-8), 0, 0), col='#e7b23b', L=4.0)
    # duimstok als laddertje tegen de romp
    base, top = Vector((8.4, -2.6, 0.0)), Vector((5.45, -1.1, deck + 0.1))
    d = top - base
    yaw = math.atan2(d.y, d.x)
    pitch = math.asin(d.z / d.length)
    SP.duimstok_ladder('ladder', loc=tuple(base), rot=(0, -pitch, yaw), L=d.length)
