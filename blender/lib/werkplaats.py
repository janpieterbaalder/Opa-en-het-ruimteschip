"""Opa's werkplaats: een miniatuurkamer van alledaagse dingen.

Vloer van ijsstokjes, achterwand van berken gaatjesplaat met een raam (houten fotolijstje met
koffieroerstaafjes als roedes), werkbank van een lucifersdoosje op potloodstompjes, eikeldop-lampje,
plankje van een ijsstokje op punaises met kroonkurkjes vol verf, garenklosje als kruk.
"""
import bpy, math, os
import numpy as np
from . import core as K, hout as H, spullen as SP, voorwerpen as VW

PITCH = 2.54
WALL_Y = 6.5
X0 = -10 * PITCH            # linkerrand gaatjesplaat
NX, NY = 20, 10              # cellen
WIN = (5, 9, 1, 3)           # raamcellen i0..i1, j0..j1
BENCH = (0.0, 1.4)           # midden werkbank
BENCH_TOP = 1.3 + 1.5


def cell_x(i):
    return X0 + i * PITCH


def wall_hole(i, j):
    """Wereldpositie van gaatje (i, j) aan de voorkant van de wand."""
    return (X0 + (i + 0.5) * PITCH, WALL_Y, (j + 0.5) * PITCH)


def bouw(sun_az=None, lamp=True, outside=True, bench=True, lamp_loc=None, floor=True, bankje=True, mood='dag',
         bench_at=None, moon=(-7.0, 13.0), lamp_energy=300, krullen=True, rommel=True, tekening=True, kist=(10.0, 3.8, -12)):
    out = {}
    bx, by = bench_at or BENCH
    # ---------------------------------------------------- vloer, wanden, plafond
    SP.vloer(-26, 26, -30, WALL_Y + 0.5)
    ply = H.wood('berk', 'X', paint='#8ea595', grain=0.12, rough=0.5, ply=0.4 / 5, key='gaatjesplaat', var=0.04)
    i0, i1, j0, j1 = WIN
    SP.gaatjesplaat('wand', NX * PITCH, NY * PITCH, ply, skip=lambda i, j: i0 <= i <= i1 and j0 <= j <= j1,
                    loc=(X0, WALL_Y, 0), rot=(math.pi / 2, 0, 0))
    # donkere achterwand achter de gaatjes (met een gat voor het raam)
    back = H.wood('noten', 'Z', paint='#2e2520', grain=0.1, key='achterwand')
    bw, bh = NX * PITCH, NY * PITCH
    xa_, xb_ = cell_x(i0), cell_x(i1 + 1)
    za_, zb_ = j0 * PITCH, (j1 + 1) * PITCH
    yb = WALL_Y + 1.2
    H.box('achter_l', xa_ - X0, 0.3, bh, back, loc=((X0 + xa_) / 2, yb, 0), bev=0, base=True)
    H.box('achter_r', X0 + bw - xb_, 0.3, bh, back, loc=((xb_ + X0 + bw) / 2, yb, 0), bev=0, base=True)
    H.box('achter_o', xb_ - xa_, 0.3, za_, back, loc=((xa_ + xb_) / 2, yb, 0), bev=0, base=True)
    H.box('achter_b', xb_ - xa_, 0.3, bh - zb_, back, loc=((xa_ + xb_) / 2, yb, zb_), bev=0, base=True)
    for k, (x0_, x1_) in enumerate(((xa_, xa_ + 0.3), (xb_ - 0.3, xb_))):
        H.box(f'neg{k}', 0.3, 1.2, zb_ - za_, back, loc=((x0_ + x1_) / 2, WALL_Y + 0.6, za_), bev=0, base=True)
    for k, z_ in enumerate((za_, zb_ - 0.3)):
        H.box(f'negh{k}', xb_ - xa_, 1.2, 0.3, back, loc=((xa_ + xb_) / 2, WALL_Y + 0.6, z_), bev=0, base=True)
    # bovenste strook wand en zijwanden van grenen planken
    planks = H.wood('grenen', 'Z', key='planken', var=0.12)
    H.box('wand_boven', NX * PITCH + 8, 0.6, 20, planks, loc=(0, WALL_Y + 0.5, NY * PITCH), bev=0.05, base=True)
    for sx in (-1, 1):
        H.box(f'zijwand{sx}', 0.6, 60, 45, planks, loc=(sx * (NX * PITCH / 2 + 0.3), WALL_Y - 28, 0), bev=0.05, base=True)
    H.box('plafond', 70, 60, 0.6, planks, loc=(0, WALL_Y - 28, 24.0), bev=0.05, base=True)

    # ---------------------------------------------------- raam: fotolijstje + roerstaafjes
    xa, xb = cell_x(i0), cell_x(i1 + 1)
    za, zb = j0 * PITCH, (j1 + 1) * PITCH
    fr = H.wood('eiken', 'X', key='lijst', coat=0.15)
    frz = H.wood('eiken', 'Z', key='lijst_z', coat=0.15)
    w, d = 0.75, 0.55
    H.box('lijst_onder', xb - xa + 2 * w, d, w, fr, loc=((xa + xb) / 2, WALL_Y - d / 2 + 0.02, za - w / 2 + 0.15), bev=0.08)
    H.box('lijst_boven', xb - xa + 2 * w, d, w, fr, loc=((xa + xb) / 2, WALL_Y - d / 2 + 0.02, zb + w / 2 - 0.15), bev=0.08)
    for x in (xa - w / 2 + 0.15, xb + w / 2 - 0.15):
        H.box(f'lijst_zij{x:.1f}', w, d, zb - za + 2 * w - 0.3, frz, loc=(x, WALL_Y - d / 2 + 0.02, (za + zb) / 2), bev=0.08)
    roer = H.wood('berk', 'X', key='roerstaafje')
    H.box('roede_h', xb - xa + 0.2, 0.1, 0.5, roer, loc=((xa + xb) / 2, WALL_Y + 0.15, (za + zb) / 2), bev=0.03)
    H.box('roede_v', 0.5, 0.1, zb - za + 0.2, H.wood('berk', 'Z', key='roerstaafje_z'), loc=((xa + xb) / 2, WALL_Y + 0.25, (za + zb) / 2),
          bev=0.03)
    # vensterbank: ijsstokje
    SP.ijsstokje('vensterbank', ((xa + xb) / 2, WALL_Y - 0.45, za - 0.05))

    # ---------------------------------------------------- buiten: tuin en lucht (zacht onscherp)
    if outside:
        sky = _buiten_mat('buiten_' + mood, mood)
        ob = K.mesh_obj('buiten', [(-60, 0, -10), (60, 0, -10), (60, 0, 50), (-60, 0, 50)], [(0, 1, 2, 3)], sky)
        ob.location = (0, WALL_Y + 30, 0)
        ob.visible_shadow = False
        rnd = np.random.default_rng(11)
        leaf = H._new('blad_' + mood)
        g = H.G(leaf)
        bc, ec, es = {'dag': ('#5d8c42', '#8fbf5e', 0.9), 'avond': ('#4b5a2c', '#9a7a3a', 0.45),
                      'schemer': ('#2e3340', '#6e6488', 0.3), 'nacht': ('#0f1a18', '#16263a', 0.15)}[mood]
        g.bsdf(bc, 0.8, emission=ec, emit_str=es)
        if mood in ('nacht', 'schemer') and moon:
            mm = H.emit('#fff1c8', 6.0 if mood == 'nacht' else 2.2, key='maan_' + mood)
            K.mesh_obj('maan', *_disc(2.6), mm, loc=(moon[0], WALL_Y + 27, moon[1]), rot=(math.pi / 2, 0, 0))
        for k in range(14):
            x = rnd.uniform(-24, 4)
            H.ball(f'struik{k}', rnd.uniform(2.5, 5.0), leaf, loc=(x, WALL_Y + rnd.uniform(9, 22), rnd.uniform(-1, 5)),
                   res=(24, 12))

    if bench:
        # ---------------------------------------------------- werkbank: lucifersdoosje op potloodstompjes
        bx, by = BENCH
        L, Wd = 5.3, 3.6
        cols = ['#3f8a55', '#d4473a', '#3e6ea6', '#e7b23b']
        for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
            SP.potlood(f'poot{k}', cols[k], 1.3, loc=(bx + sx * (L / 2 - 0.55), by + sy * (Wd / 2 - 0.5), 0))
        SP.lucifersdoosje('werkbank', (bx, by, 1.3), 0.0, open_=0.35)
        out['bench_top'] = BENCH_TOP

    gereedschapswand()
    wandplanken()

    # ---------------------------------------------------- liniaal als wandplank, frisdrankdopjes vol verf
    zs = 4.6
    x0s = 5.2
    for k in (0, 1):
        SP.punaise(f'plankdrager{k}', (x0s + 1.2 + k * 9.0, WALL_Y - 0.02, zs - 0.5), (math.pi / 2, 0, 0))
    SP.liniaal('plank_liniaal', (x0s + 15.0, WALL_Y - 1.55, zs - 0.15))
    for k, (cap, verf) in enumerate((('#f4f2ec', '#3f73b5'), ('#d8473a', '#f0b52f'), ('#3f8a55', '#d8473a'))):
        SP.frisdrankdop(f'verfpot{k}', (x0s + 1.7 + k * 3.25, WALL_Y - 1.6, zs), cap, paint=verf)
    SP.knikker('knikker', (x0s + 10.6, WALL_Y - 1.4, zs + 0.8))
    SP.vingerhoed('vingerhoed', (x0s + 12.6, WALL_Y - 1.4, zs))

    if tekening:
        # ---------------------------------------------------- bouwtekening met een paperclip
        nw, nh = 6.4, 4.8
        note = H.paper('#c9a87c', os.path.join(H.TEX, 'bouwtekening.png'), rough=0.9, key='bouwtekening', src='GEN', fiber=0.1)
        nx, nz = 4.6, 8.3
        K.mesh_obj('briefje', [(-nw / 2, -nh / 2, 0), (nw / 2, -nh / 2, 0), (nw / 2, nh / 2, 0), (-nw / 2, nh / 2, 0)],
                   [(0, 1, 2, 3)], note, loc=(nx, WALL_Y - 0.06, nz), rot=(math.pi / 2, math.radians(2.5), 0))
        SP.paperclip('briefclip', (nx - 1.6, WALL_Y - 0.12, nz + nh / 2 - 0.9), (math.pi / 2, math.radians(88), 0), col='#3f73b5')
        SP.speld('briefspeld', (nx + 2.2, WALL_Y - 0.5, nz + nh / 2 - 0.35), '#d4473a')

    # ---------------------------------------------------- postzegel als schilderijtje
    pz = H.paper('#f7f1e4', os.path.join(H.TEX, 'postzegel.png'), rough=0.8, key='postzegel', src='GEN', fiber=0.04)
    pz.blend_method = 'CLIP' if hasattr(pz, 'blend_method') else None
    _alpha_cut(pz)
    K.mesh_obj('postzegel', [(-1.1, -1.3, 0), (1.1, -1.3, 0), (1.1, 1.3, 0), (-1.1, 1.3, 0)], [(0, 1, 2, 3)], pz,
               loc=(9.4, WALL_Y - 0.05, 7.4), rot=(math.pi / 2, math.radians(-3), 0))

    # ---------------------------------------------------- gereedschap aan bliklipjes
    hx, hz = wall_hole(10, 2)[0], wall_hole(10, 2)[2]
    SP.speld('haak1', (hx, WALL_Y - 0.4, hz), '#e7b23b')
    SP.bliklipje('lipje1', (hx, WALL_Y - 0.12, hz - 0.62), (math.pi / 2, math.radians(4), 0))
    SP.hamertje('wandhamer', bead='#3e6ea6', L=1.6, br=0.24, loc=(hx + 0.05, WALL_Y - 0.25, hz - 0.95),
                rot=(0, math.radians(180 + 12), 0))
    hx2, hz2 = wall_hole(10, 1)[0], wall_hole(10, 1)[2]
    SP.speld('haak2', (hx2, WALL_Y - 0.4, hz2), '#3f8a55')
    SP.bliklipje('lipje2', (hx2, WALL_Y - 0.12, hz2 - 0.62), (math.pi / 2, math.radians(-6), 0))
    SP.elastiekje('elastiek', (hx2, WALL_Y - 0.15, hz2 - 1.05), w=1.0, h=1.6, r=0.045)

    # ---------------------------------------------------- hout op voorraad (rechts)
    st = H.wood('berk', 'Z', key='roerstaafje_z')
    for k in range(5):
        H.box(f'roerstaafje{k}', 0.5, 0.1, 14, st, loc=(9.0 + k * 0.55, WALL_Y - 0.9 + k * 0.05, -0.3),
              rot=(math.radians(-7 - k), math.radians(3 - 2 * k), 0), bev=0.03, base=True)
    sate = H.wood('berk', 'Z', key='sate')
    for k in range(4):
        H.cyl(f'sate{k}', 0.15, 22, sate, loc=(12.4 + k * 0.4, WALL_Y - 1.4, 0.05), rot=(math.radians(-6), math.radians(-3 - k), 0),
              bev=0.05, seg=12)
    for k in range(6):
        SP.lucifer(f'luciferhoop{k}', (7.5 + 0.05 * k, -0.5 + k * 0.22, 0.1 + 0.2 * (k % 2)), (0, 0, math.radians(80 + 5 * k)))

    # ---------------------------------------------------- bankje, krukje, gasfles
    if bankje:
        SP.gum('bankje', (-7.4, 4.5, 0), rot=4)
    if floor:
        SP.frisdrankdop('krukje1', (-6.5, 1.9, 1.15), '#d8473a', up=False)
    SP.batterij('gasfles', (6.2, 3.7, 0))

    # ---------------------------------------------------- garenklos-kruk en vloerspul
    if floor:
        SP.garenklos('kruk', '#c23a2f', loc=(7.4, 1.6, 0))
    if krullen:
        SP.krulletjes('krullen_vloer', (bx - 0.5, by - 2.2), (9, 4), n=60, seed=3, rmin=0.06, rmax=0.16)
    if krullen:
        SP.krulletjes('krullen_onder', (bx, by), (5, 3), n=35, seed=5, rmin=0.06, rmax=0.16)
    if bench:
        SP.krulletjes('krullen_bank', (bx - 0.6, by - 0.4), (2.4, 1.6), n=14, seed=9, zf=BENCH_TOP, rmin=0.035, rmax=0.07,
                      clip=(bx - 2.5, bx + 2.5, by - 1.65, by + 1.65))
    if krullen:
        SP.zaagsel('zaagsel_vloer', (bx, by - 1.0), (14, 8), n=3500)
    if bench:
        SP.zaagsel('zaagsel_bank', (bx - 0.6, by), (3.2, 2.0), n=500, zf=BENCH_TOP, smax=0.05,
                   clip=(bx - 2.55, bx + 2.55, by - 1.7, by + 1.7))

    if bench:
        # ---------------------------------------------------- spullen op de werkbank
        SP.knijpertje('klem', loc=(bx + 1.2, by - 0.1, BENCH_TOP + 0.21), rot=(0, 0, math.radians(-75)), L=2.4)
        H.prism('werkstuk', H.stadium_pts(3.6, 1.0, 12)[:13] + [(-1.8, 0.5), (-1.8, -0.5)], 0.2,
                H.wood('berk', 'X', key='ijsstokje'), bev=0.045, loc=(bx - 0.2, by - 0.5, BENCH_TOP + 0.005),
                rot=(0, 0, math.radians(8)))
        SP.spijkertje('spijker', (bx - 1.25, by - 0.65, BENCH_TOP + 0.2), L=0.55)
        SP.spijkertje('spijker2', (bx - 0.55, by - 0.55, BENCH_TOP + 0.2), L=0.12)
        puntenslijper('slijper', (bx - 1.7, by + 1.0, BENCH_TOP), rot=25)
        cup = SP.eikeldop('koffiekopje', (bx + 1.9, by + 1.1, BENCH_TOP), (0, 0, 0), R=0.5, D=0.38, stem=False)
        H.cyl('koffie', 0.42, 0.02, H.plastic('#3a2114', 0.05, key='koffie'), loc=(bx + 1.9, by + 1.1, BENCH_TOP + 0.3), bev=0.0,
              seg=32)

    if rommel:
        _rommel(kist)

    # ---------------------------------------------------- lampje
    if lamp:
        SP.hanglamp('lamp', lamp_loc or (bx + 0.3, by + 0.9, 7.0), ceiling=24.0, energy=lamp_energy)
    return out


def _disc(r, n=48):
    V = [(0, 0, 0)] + [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), 0) for k in range(n)]
    F = [(0, k + 1, (k + 1) % n + 1) for k in range(n)]
    return V, F


def _buiten_mat(key='buiten', mood='dag'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    t = g.sstep(-2.0, 30.0, z)
    if mood == 'dag':
        col = g.ramp(t, [(0.0, '#7fa35a'), (0.25, '#a9c27a'), (0.4, '#cfe3ea'), (1.0, '#8fbde6')])
        n = g.noise(g.comb(x, z, 0.0), 0.15, 3.0)
        col = g.mix(g.math('MULTIPLY', g.sstep(0.45, 0.7, n), g.sstep(18.0, 2.0, z)), col, '#5c8a45')
        strength = 2.2
    elif mood == 'schemer':
        col = g.ramp(t, [(0.0, '#e9a888'), (0.2, '#d998a6'), (0.45, '#9c90c4'), (0.75, '#5d73b2'), (1.0, '#41599a')])
        v = g.node('ShaderNodeTexVoronoi')
        g.link(g.comb(x, z, 0.0), v.inputs['Vector'])
        v.inputs['Scale'].default_value = 0.6
        star = g.math('MULTIPLY', g.sstep(0.04, 0.015, v.outputs['Distance']), g.sstep(12.0, 22.0, z))
        col = g.mix(g.math('MULTIPLY', star, 0.5), col, '#fff4dc')
        strength = 1.6
    elif mood == 'avond':
        col = g.ramp(t, [(0.0, '#6b5a33'), (0.22, '#e59a5a'), (0.45, '#f3c08a'), (0.75, '#c58fa8'), (1.0, '#7d7fb8')])
        strength = 2.0
    else:
        col = g.ramp(t, [(0.0, '#0b1226'), (0.3, '#1b2c58'), (1.0, '#0d1838')])
        v = g.node('ShaderNodeTexVoronoi')
        g.link(g.comb(x, z, 0.0), v.inputs['Vector'])
        v.inputs['Scale'].default_value = 0.9
        star = g.sstep(0.07, 0.02, v.outputs['Distance'])
        star = g.math('MULTIPLY', star, g.sstep(4.0, 12.0, z))
        col = g.mix(star, col, '#fff4d6')
        strength = 1.2
    e = g.node('ShaderNodeEmission')
    g.link(col, e.inputs['Color'])
    e.inputs['Strength'].default_value = strength
    o = g.node('ShaderNodeOutputMaterial')
    g.link(e.outputs[0], o.inputs['Surface'])
    return m


def licht(sun=6.0, sun_dir=(-0.8, 1.0, 0.45), fill=1400.0, world=0.12, haze=0.004, key=2600.0):
    """Zon van buiten (door het raam en de gaatjes), zachte vullamp aan de camerakant, beetje omgevingslicht."""
    K.world_color('#d9c7ad', world)
    d = np.array(sun_dir, float)
    d /= np.linalg.norm(d)
    K.light('SUN', tuple(d * 80), (0, 0, 0), energy=sun, color=(1.0, 0.9, 0.76), angle=1.2, name='Zon')
    K.light('AREA', (-14, -30, 16), (0, 0, 3), energy=fill, size=18, color=(0.92, 0.95, 1.0), name='Vullicht',
            visible_glossy=False)
    # laag, warm zijlicht van links (middagzon door een zijraam buiten beeld)
    if key:
        K.light('AREA', (-17, -6, 8.5), (0, 1.0, 3.0), energy=key, size=3.5, color=(1.0, 0.82, 0.6), name='Zijlicht')
    K.light('AREA', (16, -22, 6), (0, 2, 3), energy=fill * 0.35, size=10, color=(1.0, 0.86, 0.7), name='Warmlicht',
            visible_glossy=False)
    if haze:
        # een beetje stof in de lucht: zonnestralen door het raam worden zichtbaar
        m = bpy.data.materials.new('stof')
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        v = nt.nodes.new('ShaderNodeVolumePrincipled')
        v.inputs['Density'].default_value = haze
        v.inputs['Anisotropy'].default_value = 0.55
        v.inputs['Color'].default_value = (1.0, 0.95, 0.88, 1)
        o = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(v.outputs[0], o.inputs['Volume'])
        bx_ = H.box('stofkamer', 50, 36, 23.5, m, loc=(0, WALL_Y - 18.2, 0.05), bev=0, base=True)
        bx_.visible_shadow = False
        bpy.context.scene.cycles.volume_bounces = 0
        bpy.context.scene.cycles.volume_step_rate = 4.0


def _alpha_cut(m):
    """Laat de alfa van de afbeelding in een papiermateriaal ook echt doorzichtig zijn (kartelrand)."""
    nt = m.node_tree
    img = next(n for n in nt.nodes if n.type == 'TEX_IMAGE')
    bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    nt.links.new(img.outputs['Alpha'], bs.inputs['Alpha'])


def puntenslijper(name, loc, rot=0.0):
    """Metalen puntenslijpertje: opa's machine."""
    ob = K.empty(name, loc, (0, 0, math.radians(rot)))
    al = H.metal('#b9bcc0', 0.3, key='slijper_alu')
    pts = [(-0.75, -0.45), (0.75, -0.45), (0.75, 0.2), (0.45, 0.45), (-0.75, 0.45)]
    body = H.prism(name + '_blok', pts, 0.8, al, bev=0.06, parent=ob)
    body.rotation_euler = (math.pi / 2, 0, 0)
    body.location = (0, 0.4, 0.45)
    H.cyl(name + '_gat', 0.28, 0.05, H.plastic('#1b1816', 0.6, key='gat_zwart'), loc=(-0.35, -0.42, 0.42),
          rot=(math.pi / 2, 0, 0), bev=0.0, seg=32, parent=ob)
    H.box(name + '_mesje', 0.9, 0.5, 0.04, H.metal('#d9dcdf', 0.15, key='mesje'), loc=(0.1, 0.0, 0.92 - 0.0), rot=(0, 0, 0.05),
          bev=0.01, parent=ob)
    H.cyl(name + '_schroef', 0.09, 0.06, H.metal('#c9c9c9', 0.2, key='speldstaal'), loc=(0.35, 0.0, 0.94), bev=0.02,
          seg=16, parent=ob)
    return ob


def licht_avond(fill=900.0, haze=0.004):
    """Lage, oranje avondzon door het raam."""
    licht(sun=5.0, sun_dir=(-0.55, 1.0, 0.2), fill=fill, world=0.08, haze=haze, key=1600.0)
    for ob in bpy.data.objects:
        if ob.name == 'Zon':
            ob.data.color = (1.0, 0.58, 0.28)
        if ob.name == 'Zijlicht':
            ob.data.color = (1.0, 0.62, 0.35)
        if ob.name == 'Vullicht':
            ob.data.color = (0.75, 0.78, 1.0)


def licht_nacht(fill=260.0, moon=0.9, world=0.05, haze=0.003):
    """Nacht: koel maanlicht door het raam, een beetje blauw omgevingslicht; warme lampjes doen de rest."""
    K.world_color('#2a3a66', world)
    d = np.array((-0.5, 1.0, 0.55))
    d /= np.linalg.norm(d)
    K.light('SUN', tuple(d * 80), (0, 0, 0), energy=moon, color=(0.62, 0.72, 1.0), angle=0.8, name='Maanlicht')
    K.light('AREA', (-14, -30, 16), (0, 0, 3), energy=fill, size=18, color=(0.55, 0.65, 1.0), name='Vullicht',
            visible_glossy=False)
    if haze:
        licht(sun=0.0, fill=0.0, world=world, haze=haze, key=0.0)
        for ob in list(bpy.data.objects):
            if ob.type == 'LIGHT' and ob.data.energy == 0.0:
                bpy.data.objects.remove(ob)
        K.world_color('#2a3a66', world)


def _rommel(kist=(10.0, 3.8, -12)):
    """Spullen in de hoeken van de werkplaats (opa's gereedschapskist, rolmaat, theelichtjes, munten, wol, ...)."""
    if kist:
        SP.gereedschapskist('opas_kist', (kist[0], kist[1], kist[3] if len(kist) > 3 else 0), rot=kist[2])
    for k in range(3):
        SP.lucifersdoosje(f'doosjesstapel{k}', (13.6 + 0.12 * k, 4.2 - 0.1 * k, 1.5 * k), 6 - 7 * k, open_=0.0 if k != 1 else 0.6,
                          contents=False)
    SP.bolletje_wol('wol', (16.9, 2.6, 2.0), R=2.0, col='#d9a441')
    SP.rolmaat('rolmaat', (-15.2, 3.0, 0), rot=25)
    kachelhoek()
    SP.theelichtje('theelicht2', (-14.6, -8.6, 0))
    SP.muntstapel('munten', (14.4, -9.6, 0), n=4)
    SP.muntstapel('munten2', (12.6, -10.8, 0), n=2, seed=3)
    SP.sleutel('sleutel', (11.0, -12.6, 0.11), rot=(0, 0, math.radians(30)))
    SP.losse_elastiekjes('elastiek', (-12.6, -11.6))
    for k, (x, y) in enumerate(((-16.0, -5.6), (16.0, -4.6), (-9.8, -13.6))):
        SP.kroonkurk(f'losse_kurk{k}', (x, y, 0.62), rot=(math.pi, 0, 0.4 * k))


# ----------------------------------------------------------------------- de wand: gereedschap en planken
def _silhouet(name, pts, x, z, rot=0.0):
    """Geschilderde omtrek van een stuk gereedschap op de gaatjesplaat (zoals op een echte gereedschapswand)."""
    m = H.wood('berk', 'X', paint='#5f7867', grain=0.08, rough=0.55, key='silhouet')
    ob = H.prism(name, pts, 0.02, m, bev=0.0)
    ob.rotation_euler = (math.pi / 2, rot, 0)
    ob.location = (x, WALL_Y - 0.005, z)
    return ob


def gereedschapswand():
    """Links van het raam: gereedschap netjes aan spelden, met de omtrek erachter geschilderd."""
    wy = WALL_Y - 0.32
    pin = lambda n, x, z, c: SP.speld(n, (x, WALL_Y - 0.45, z), c)
    # twee klauwhamers
    for k, x in enumerate((-23.0, -21.2)):
        _silhouet(f'sil_hamer{k}', [(-0.75, 0.45), (0.75, 0.45), (0.75, 0.05), (0.16, 0.05), (0.16, -2.05), (-0.16, -2.05),
                                    (-0.16, 0.05), (-0.75, 0.05)][::-1], x, 10.6)
        SP.klauwhamer(f'wandhamer{k}', loc=(x - 0.05, wy, 10.35), rot=(0, 0, 0), L=1.9)
        pin(f'hamerpin{k}', x, 10.75, '#d8473a')
    # twee zagen
    for k, (x, z) in enumerate(((-18.6, 11.0), (-15.9, 11.0))):
        _silhouet(f'sil_zaag{k}', [(-0.35, 0.65), (0.45, 0.75), (0.55, 0.0), (0.3, -2.9), (-0.25, -2.9), (-0.45, 0.0)], x, z)
        SP.handzaag(f'wandzaag{k}', L=2.6, loc=(x, wy, z), rot=(0, math.radians(90), math.radians(180)))
        pin(f'zaagpin{k}', x - 0.05, z + 0.85, '#3f73b5')
    # schroevendraaiers en beitels op een rij
    for k, x in enumerate((-23.6, -22.6, -21.6, -20.6, -19.6)):
        z = 6.6
        _silhouet(f'sil_staaf{k}', H.rounded_rect_pts(0.42, 2.0, 0.18, 4), x, z - 0.15)
        if k < 3:
            SP.schroevendraaier(f'wandschroef{k}', loc=(x, wy, z + 0.25), rot=(0, 0, 0))
        else:
            SP.beitel(f'wandbeitel{k}', loc=(x, wy, z + 0.2), rot=(0, 0, 0))
        pin(f'staafpin{k}', x, z + 1.15, ('#e7b23b', '#3f8a55', '#d8473a', '#3f73b5', '#e7b23b')[k])
    # lijmklemmen (knijpertjes) en een rolletje touw
    for k, x in enumerate((-17.8, -16.8, -15.8)):
        SP.knijpertje(f'wandklem{k}', loc=(x, WALL_Y - 0.25, 4.2), rot=(math.pi / 2, math.pi / 2, 0), L=2.6)
        pin(f'klempin{k}', x, 4.35, '#f4f1ea')
    SP.elastiekje('wandtouw', (-21.6, WALL_Y - 0.15, 4.6), w=1.4, h=2.0, r=0.05, col='#b08a5a')
    pin('touwpin', -21.6, 4.6, '#d8473a')
    # bordje erboven
    SP.ijsstokje('wandbordje', (-19.5, WALL_Y - 0.12, 13.4), (math.pi / 2, 0, 0))


def wandplanken():
    """Planken boven het raam en rechts, met potjes, klosjes, dopjes en spelletjes erop."""
    for k, (x0, x1, z) in enumerate(((-13.0, -0.6, 12.2), (-13.0, -0.6, 15.4), (7.6, 20.6, 11.8))):
        L = x1 - x0
        SP.liniaal(f'wandplank{k}', ((x0 + x1) / 2, WALL_Y - 1.25, z - 0.15), L=L, W=2.4, T=0.3)
        for j, x in enumerate((x0 + 1.0, x1 - 1.0)):
            SP.punaise(f'plankpunaise{k}{j}', (x, WALL_Y - 0.02, z - 0.6), (math.pi / 2, 0, 0))
    # plank boven het raam
    VW.jampotje('knopenpot', (-11.6, WALL_Y - 1.3, 12.2))
    for j, (x, c) in enumerate(((-9.0, '#d8473a'), (-7.1, '#3f73b5'), (-5.2, '#e7b23b'))):
        SP.garenklos(f'plankklos{j}', c, loc=(x, WALL_Y - 1.3, 12.2), R=0.8, Hh=2.0, core=0.45, draad=False)
    VW.eierdopje('spijkerbakje', (-2.6, WALL_Y - 1.3, 12.2))
    for j in range(6):
        VW.kruidnagel(f'kruidnagel{j}', (-2.6 + 0.3 * math.cos(j), WALL_Y - 1.3 + 0.3 * math.sin(j), 14.6),
                      rot=(0.25 * math.cos(j * 2), 0.25 * math.sin(j * 2), 0))
    # hoogste plank
    for j, (x, c) in enumerate(((-11.8, '#d8473a'), (-9.8, '#3f8a55'), (-7.8, '#3561a8'))):
        SP.kroonkurk(f'plankverf{j}', (x, WALL_Y - 1.3, 15.4), paint=c, R=0.85, Hh=0.45)
    VW.pion('pion_rood', (-5.6, WALL_Y - 1.3, 15.4), col='#d8473a')
    VW.pion('pion_geel', (-4.4, WALL_Y - 0.9, 15.4), col='#e7b23b')
    VW.plakband('plakband', (-2.4, WALL_Y - 1.2, 15.4))
    # plank rechts
    for j in range(2):
        SP.lucifersdoosje(f'plankdoosje{j}', (9.8, WALL_Y - 1.25, 11.8 + 1.5 * j), 4 - 8 * j, open_=0.0, contents=False)
    VW.koffiemelkcupje('cupje1', (13.2, WALL_Y - 1.3, 11.8))
    VW.koffiemelkcupje('cupje2', (15.2, WALL_Y - 1.1, 11.8), rot=(0, 0, 1.0))
    VW.meetlintje('meetlintje', (17.6, WALL_Y - 1.4, 11.8))
    VW.jojo('jojo', (19.6, WALL_Y - 1.3, 12.0), rot=(math.pi / 2, 0, 0))
    VW.speelkaart('kaart_poster', (16.5, WALL_Y - 0.06, 8.2), rot=(math.pi / 2, math.radians(-4), 0))


def kachelhoek(x=-11.7, y=1.4):
    """Een theelichtje als kacheltje, met een rietje als kachelpijp en kaneelstokjes als brandhout."""
    SP.theelichtje('kacheltje', (x, y, 0))
    SP.eikeldop('kopje_thee', (x + 0.3, y - 0.3, 1.5), R=0.5, D=0.38, stem=False)
    VW.rietje('kachelpijp', (x - 1.2, y + 0.9, 1.3), rot=(0, 0, math.radians(90)), L=13.0)
    for k in range(5):
        VW.kaneelstokje(f'brandhout{k}', (x - 4.6 + (k % 3) * 0.75, y + 2.6, 0.45 + (k // 3) * 0.75), rot=(0, math.pi / 2, 0), L=4.0)
    VW.suikerzakje('suikerzakje', (x + 2.4, y - 1.8, 0.12), rot=(0, 0, 0.5))


# ----------------------------------------------------------------------- bouwplaats rond het schip
def zaagbok(name, loc, rot=0.0):
    root = K.empty(name, loc, (0, 0, math.radians(rot)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            SP.knijpertje(f'{name}_poot{sx}{sy}', loc=(sx * 1.4, sy * 0.6, 0.0),
                          rot=(math.radians(-sy * 18), -math.pi / 2 + math.radians(4), 0), L=2.8, parent=root)
    SP.ijsstokje(name + '_plank', (0, 0, 2.75), (0, 0, 0), parent=root)
    return root


def kruiwagen(name, loc, rot=0.0):
    root = K.empty(name, loc, (0, 0, math.radians(rot)))
    karton = H.paper('#efeae0', rough=0.85, key='karton_wit', fiber=0.06)
    L, W, Hh, t = 5.0, 3.2, 1.3, 0.04
    tray = K.empty(name + '_bak', (0, 0, 1.15), (0, math.radians(-8), 0), parent=root)
    H.box(name + '_bodem', L, W, t, karton, loc=(0, 0, 0), bev=0.01, parent=tray)
    for sy in (-1, 1):
        H.box(name + f'_zij{sy}', L, t, Hh, karton, loc=(0, sy * (W / 2), Hh / 2), bev=0.01, parent=tray)
    for sx in (-1, 1):
        H.box(name + f'_kop{sx}', t, W, Hh, karton, loc=(sx * L / 2, 0, Hh / 2), bev=0.01, parent=tray)
    SP.knoop(name + '_wiel', (-L / 2 - 0.6, 0, 1.05), '#d8473a', r=1.05, rot=(math.pi / 2, 0, 0), parent=root)
    for sy in (-1, 1):
        SP.ijsstokje(f'{name}_handvat{sy}', (L / 2 - 1.5, sy * 1.3, 1.2), (0, math.radians(-12), 0), parent=root)
        H.cyl(f'{name}_steun{sy}', 0.08, 1.1, H.wood('berk', 'Z', key='tandenstoker'), loc=(L / 2 - 0.6, sy * 1.3, 0.0), bev=0.02,
              seg=10, parent=root)
    rnd = np.random.default_rng(7)
    for k in range(10):
        SP.knoop(f'{name}_lading{k}', (rnd.uniform(-1.8, 1.8), rnd.uniform(-1.1, 1.1), 0.2 + 0.12 * (k % 3)),
                 ('#e7b23b', '#3e6ea6', '#f4f1ea', '#3f8a55')[k % 4], r=rnd.uniform(0.3, 0.45),
                 rot=(rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 6)), parent=tray)
    return root


def steiger(name, x0, x1, y0, y1, levels=(4.2, 8.6)):
    """Steiger van rietjes met koffieroerstaafjes als schoren en ijsstokjes als loopplanken."""
    m = VW._stripes_mat('rietje', '#f7f4ee', '#d23b30', 1.4, axis=2, rough=0.3, coat=0.4, twist=0.25)
    top = levels[-1] + 2.2
    for x in np.linspace(x0, x1, 3):
        for y in (y0, y1):
            H.cyl(f'{name}_paal{x:.1f}{y:.1f}', 0.3, top, m, loc=(x, y, 0), bev=0.03, seg=24)
    st = H.wood('berk', 'X', key='roerstaafje')
    for z in levels:
        for y in (y0, y1):
            H.box(f'{name}_ligger{z}{y}', x1 - x0 + 0.6, 0.1, 0.5, st, loc=((x0 + x1) / 2, y + (0.35 if y == y0 else -0.35), z), bev=0.03)
        for k in range(2):
            SP.ijsstokje(f'{name}_plank{z}{k}', ((x0 + x1) / 2, (y0 + y1) / 2 + (k - 0.5) * 1.05, z + 0.3), (0, 0, 0))
    # schoren
    for y in (y0, y1):
        a = math.atan2(levels[0], (x1 - x0) / 2)
        H.box(f'{name}_schoor{y}', math.hypot((x1 - x0) / 2, levels[0]), 0.1, 0.5, st,
              loc=((x0 * 3 + x1) / 4, y + (0.45 if y == y0 else -0.45), levels[0] / 2), rot=(0, -a, 0), bev=0.03)
    SP.duimstok_ladder(name + '_ladder', loc=(x1 + 2.6, (y0 + y1) / 2, 0.0), rot=(0, math.radians(-62), math.radians(180)), L=5.6)


def kraantje(name, loc, jib_dir=180.0):
    """Hijskraantje: een garenklos als voet, een potlood als mast, een stuk duimstok als arm en een paperclip als haak."""
    x, y = loc[0], loc[1]
    SP.garenklos(name + '_voet', '#3f8a55', loc=(x, y, 0), R=1.2, Hh=2.4, draad=False)
    SP.potlood(name + '_mast', '#e7b23b', 8.0, loc=(x, y, 2.4), r=0.34)
    a = math.radians(jib_dir)
    d = SP.paper if False else None
    arm = H.paper('#f2c230', __import__('os').path.join(H.TEX, 'duimstok.png'), rough=0.4, key='duimstok', src='GEN', fiber=0.02)
    L = 8.0
    H.box(name + '_arm', L, 1.2, 0.3, arm, loc=(x + math.cos(a) * (L / 2 - 0.8), y + math.sin(a) * (L / 2 - 0.8), 10.55),
          rot=(0, 0, a), bev=0.03)
    ex, ey = x + math.cos(a) * (L - 1.2), y + math.sin(a) * (L - 1.2)
    K.curve_tube(name + '_touw', [(ex, ey, 10.4), (ex, ey, 6.2)], 0.025, H.thread('#a8834e', key='touw'))
    SP.paperclip(name + '_haak', (ex, ey, 5.6), (math.pi / 2, math.radians(90), a), col='#c9c9c9', L=1.6, Wd=0.6, r=0.04)
    SP.knoop(name + '_last', (ex, ey, 4.6), '#e7b23b', r=0.9, rot=(math.pi / 2, 0, a + math.pi / 2))


def bouwplaats(kist=(10.0, 3.8, -12)):
    """Alles voor een herkenbare (fantasie)bouwplaats rond het schip; gebruik met bouw(rommel=False)."""
    kachelhoek()
    if kist:
        SP.gereedschapskist('opas_kist', (kist[0], kist[1], 0), rot=kist[2])
    zaagbok('zaagbok1', (-17.2, -3.4, 0), rot=8)
    zaagbok('zaagbok2', (-17.0, 0.4, 0), rot=4)
    for k in range(4):
        for j in range(3):
            SP.ijsstokje(f'stapel{k}{j}', (-21.0 + (j - 1) * 1.1 * (k % 2 == 0), 2.2 + (j - 1) * 1.1 * (k % 2 == 1), 0.1 + 0.22 * k),
                         (0, 0, math.pi / 2 if k % 2 else 0))
    steiger('steiger', 15.2, 21.6, 3.4, 5.6)
    kraantje('kraan', (18.4, -1.6), jib_dir=172)
    kruiwagen('kruiwagen', (16.8, -8.2, 0), rot=-20)
    for k, (x, y, z) in enumerate(((12.4, -3.2, 0), (14.4, -3.4, 0), (13.4, -3.3, 2.4))):
        SP.garenklos(f'klossenstapel{k}', ('#d8473a', '#3f73b5', '#e7b23b')[k], loc=(x, y, z), R=1.0, Hh=2.4, draad=False)
    SP.frisdrankdop('knijperemmer', (11.6, -6.4, 0), '#3f73b5')
    for k in range(4):
        SP.knijpertje(f'emmerknijper{k}', loc=(11.6 + 0.3 * math.cos(k * 1.6), -6.4 + 0.3 * math.sin(k * 1.6), 0.4),
                      rot=(0, -math.radians(70 + 6 * k), k * 1.6), L=3.0)
    SP.theelichtje('theelicht2', (-14.6, -8.6, 0))
    SP.muntstapel('munten', (14.4, -11.2, 0), n=4)
    SP.losse_elastiekjes('elastiek', (-12.6, -11.6))
    VW.wattenstaafje('bezem', (-9.4, 5.9, 0.4), rot=(math.radians(-16), math.radians(8), 0))
    VW.pompon('pompon', (-20.0, -7.0, 1.4), col='#e47a9a')


def licht_schemer(fill=900.0, haze=0.003):
    """Late schemering: de lucht nog warm aan de horizon, binnen warme lampjes."""
    licht(sun=2.4, sun_dir=(-0.6, 1.0, 0.1), fill=fill, world=0.16, haze=haze, key=700.0)
    for ob in bpy.data.objects:
        if ob.name == 'Zon':
            ob.data.color = (1.0, 0.6, 0.42)
        if ob.name == 'Zijlicht':
            ob.data.color = (1.0, 0.66, 0.42)
        if ob.name == 'Vullicht':
            ob.data.color = (0.72, 0.72, 1.0)
    K.world_color('#9d93c2', 0.18)
