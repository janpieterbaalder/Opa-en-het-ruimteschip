"""Alle platen van het boek. Eén functie per plaat; scenes/<naam>.py roept die aan.

Eenheden in cm. Werkplaats: achterwand op y = 6.5, raam x -12.7..0 / z 2.5..10.2, vloer z = 0.
"""
import math
import bpy
import numpy as np
from mathutils import Vector, Matrix
from . import core as K, hout as H, scene as S, werkplaats as WP, figuren as FG, spullen as SP, schip as SC


# ---------------------------------------------------------------- hulpjes
def hamer_j(name='hamertje'):
    return SP.hamertje(name, bead='#d4473a', L=1.0, br=0.17)


def hamer_o(name='opa_hamer'):
    return SP.hamertje(name, bead='#e7b23b', L=1.5, br=0.24)


def zit(fig, x, y, seat_top, rot=0.0, **pose):
    """Laat een poppetje zitten met de billen op hoogte seat_top."""
    z = seat_top + fig.S['leg_r'] * 0.85 - fig.S['hip']
    fig.place(x, y, z, rot)
    pose.setdefault('legL', (86, 86))
    pose.setdefault('legR', (86, 86))
    fig.pose(**pose)
    return fig


def reach(fig, side, target):
    """Zoek arm-hoeken (naar voren, opzij, elleboog) waarbij de hand van het poppetje op `target` uitkomt."""
    bpy.context.view_layer.update()
    sh, el, hd = fig.sh[side], fig.el[side], fig.hands[side]
    sh.rotation_mode = 'YXZ'
    P = sh.parent.matrix_world.copy()
    tgt = Vector(target)
    sx = 1 if side == 'L' else -1

    def err(f, sp, eb):
        sh.rotation_euler = (math.radians(-f), math.radians(-sx * sp), 0)
        el.rotation_euler = (math.radians(-eb), 0, 0)
        pos = (P @ sh.matrix_basis @ el.matrix_basis @ hd.matrix_basis).translation
        return (pos - tgt).length + 0.0004 * abs(eb)

    best = None
    for f in range(-30, 181, 6):
        for sp in range(-60, 91, 6):
            for eb in range(0, 151, 8):
                e = err(f, sp, eb)
                if best is None or e < best[0]:
                    best = (e, f, sp, eb)
    e, f0, s0, e0 = best
    for step in (2.0, 0.5):
        for _ in range(6):
            improved = False
            for df in (-step, 0, step):
                for ds in (-step, 0, step):
                    for de in (-step, 0, step):
                        e2 = err(f0 + df, s0 + ds, max(0, e0 + de))
                        if e2 < e - 1e-6:
                            e, f0, s0, e0 = e2, f0 + df, s0 + ds, max(0, e0 + de)
                            improved = True
            if not improved:
                break
    err(f0, s0, e0)
    return e


def ship_xy(ship_loc, ship_rot, x, y):
    r = math.radians(ship_rot)
    return (ship_loc[0] + x * math.cos(r) - y * math.sin(r), ship_loc[1] + x * math.sin(r) + y * math.cos(r))


def watten_mat(key='watten'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (6, 6, 6)), 1.0, 8.0, 0.7)
    g.bsdf('#f7f5f0', 0.95, sheen=1.0, normal=g.bump(n, 0.8, 0.05), emission='#c9d4ff', emit_str=0.18)
    return m


def wolk(name, loc, size=(3, 1.5, 1.2), seed=0):
    rnd = np.random.default_rng(seed)

    def deform(D, P):
        n = np.sin(D[:, 0] * 7 + seed) * np.cos(D[:, 1] * 5) * 0.12 + np.sin(D[:, 2] * 9 + seed * 2) * 0.08
        return P * (1 + n)[:, None]
    ob = K.blob(name, size, 2.0, (64, 32), deform=deform, mat=watten_mat(), loc=loc)
    for k in range(6):
        sc_ = rnd.uniform(0.45, 0.8)
        K.blob(f'{name}_{k}', (size[0] * sc_ * 0.6, size[1] * sc_, size[0] * sc_ * 0.55), 2.0, (48, 24), deform=deform,
               mat=watten_mat(), parent=ob,
               loc=(rnd.uniform(-1, 1) * size[0] * 0.7, rnd.uniform(-0.3, 0.3), rnd.uniform(0.2, 0.9) * size[2]))
    return ob


def zaagselval(name, x, y, ztop, n=700, seed=4):
    """Zaagsel dat van de zaagsnede naar beneden dwarrelt, met een hoopje op de vloer."""
    rnd = np.random.default_rng(seed)
    V, F = [], []
    for k in range(n):
        falling = k < n * 0.55
        z = rnd.uniform(0.05, ztop) if falling else 0.004
        spread = (0.04 + (ztop - z) * 0.07) if falling else 0.45
        px, py = rnd.normal(x, spread), rnd.normal(y, spread)
        s = rnd.uniform(0.012, 0.04)
        a = rnd.uniform(0, 6.3)
        b = rnd.uniform(0, 6.3) if falling else rnd.uniform(-0.2, 0.2)
        e = len(V)
        for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            lx, ly = u * s, v * s * 0.7
            wx = lx * math.cos(a) - ly * math.sin(a)
            wy = lx * math.sin(a) + ly * math.cos(a)
            wz = ly * math.sin(b)
            V.append((px + wx, py + wy * math.cos(b), z + wz + (0.005 if not falling else 0)))
        F.append((e, e + 1, e + 2, e + 3))
    m = H.wood('grenen', 'X', var=0.2, key='zaagsel_grenen')
    m.use_backface_culling = False
    return K.mesh_obj(name, V, F, m, smooth=False)


def notendop_bootje(name, loc, rot=0.0):
    """Joahs eigen bootje: halve walnoot met een tandenstoker als mast en een theezakjeslabel als zeil."""
    root = K.empty(name, loc, (0, 0, math.radians(rot)))
    key = 'walnoot'
    if key in H._M:
        m = H._M[key]
    else:
        m = H._new(key)
        g = H.G(m)
        tc = g.node('ShaderNodeTexCoord')
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (4, 7, 7)), 1.0, 6.0, 0.65, 0.6)
        col = g.ramp(n, [(0.2, '#5a3a22'), (0.55, '#a4753f'), (0.8, '#c99a5c')])
        g.bsdf(col, 0.7, normal=g.bump(n, 0.9, 0.05))
    prof = [(0.0, -0.75), (0.5, -0.68), (0.85, -0.4), (1.0, 0.0), (0.92, 0.04), (0.78, -0.33), (0.45, -0.58), (0.0, -0.63)]
    K.lathe(name + '_dop', prof, 48, m, root, sx=1.35, sy=1.0).location = (0, 0, 0.75)
    H.cyl(name + '_mast', 0.045, 2.2, H.wood('berk', 'Z', key='tandenstoker'), loc=(0, 0, 0.15), bev=0.02, seg=12, parent=root)
    SC.theezakjeslabel(name + '_zeil', root, loc=(0.05, 0, 1.75), rot=(math.pi / 2, 0, 0), w=1.1, h=0.85)
    return root


# ---------------------------------------------------------------- p. 3-4  de werkplaats
def sp03_werkplaats(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(tekening=False, kist=(0.15, 2.6, -8, 2.8))
    WP.licht()
    bx, by = WP.BENCH
    SP.dobbelsteen('opstapje', (bx - 3.8, by - 1.2, 0), rot=-10)
    j = FG.jongen()
    j.place(bx - 3.8, by - 1.2, 1.6)
    j.face_to(bx + 1.5, by - 9.0)
    j.pose(armL=(58, 32, 38), armR=(20, 14, 35), lean=4)
    o = FG.opa()
    o.place(bx + 3.9, by - 1.0)
    o.face_to(bx - 1.2, by - 9.0)
    o.pose(armR=(52, 18, 30), armL=(30, 12, 62), lean=5)
    o.hold(hamer_o(), 'L', loc=(0, -0.42, 0.0), rot=(90, 0, 0))
    reach(j, 'L', (bx - 1.25, by - 0.65, WP.BENCH_TOP + 0.72))
    o.look_at(j.head_world(), amount=0.3)
    j.look_at(o.head_world(), amount=0.4, tilt=-5)
    S.cam((bx, -16.5, 7.6), (bx, by - 0.4, 3.9), lens=40, fstop=0.16, focus=(bx, by - 1.1, 4.0))
    S.render(out)


# ---------------------------------------------------------------- p. 5-6  de bouwtekening op een groot vel papier
def sp05_tekening(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(bench=False, floor=False, lamp_loc=(-2.0, -2.0, 15.5), krullen=False, tekening=False, kist=False)
    SP.gereedschapskist('opas_kist', (9.0, -8.4, 0.03), rot=-24)
    WP.licht()
    pw, ph = 21.0, 14.8
    import os
    pap = H.paper('#c9a87c', os.path.join(H.TEX, 'bouwtekening.png'), rough=0.9, key='bouwtekening', src='GEN', fiber=0.1)
    ob = K.mesh_obj('groot_vel', [(-pw / 2, -ph / 2, 0), (pw / 2, -ph / 2, 0), (pw / 2, ph / 2, 0), (-pw / 2, ph / 2, 0)],
                    [(0, 1, 2, 3)], pap, loc=(0.0, -4.2, 0.03), rot=(0, 0, math.radians(-3)))
    # een echt potlood ernaast: voor de poppetjes een reuzenboomstam
    SP.potlood('reuzenpotlood', '#3e6ea6', 15.0, loc=(-12.5, -9.0, 0.37), rot=(0, math.radians(90), math.radians(-62)), sharp=True)
    o = FG.opa()
    o.place(5.6, -9.4, 0.03)
    o.face_to(-1.0, -2.0)
    o.pose(armL=(78, 18, 8), armR=(18, 10, 30), lean=10)
    pot = SP.potlood('opapotlood', '#c8372d', 0.9, r=0.07, sharp=False)
    o.hold(pot, 'L', loc=(0, -0.05, -0.1), rot=(0, 0, 0))
    j = FG.jongen()
    zit(j, -2.8, -9.6, 0.03, rot=0)
    j.face_to(-1.0, -2.0)
    j.pose(armL=(55, 25, 20), armR=(55, 25, 20), legL=(84, 8), legR=(84, 8), lean=12)
    o.look_at(j.head_world(), amount=0.4)
    j.look_at((0.5, -2.5, 0.0), amount=0.7)
    S.cam((0.5, -27.5, 17.0), (0.5, -4.3, 0.6), lens=40, fstop=0.3, focus=(1.0, -8.0, 2.0))
    S.render(out)


# ---------------------------------------------------------------- p. 7-8  zagen
def sp07_zagen(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(kist=(0.15, 2.6, -10, 2.8))
    WP.licht()
    bx, by = WP.BENCH
    top = WP.BENCH_TOP
    # een ijsstokje dwars op de werkbank; het steekt naar voren uit en daar zaagt opa het af
    sx_, cut_y = bx - 1.6, by - 2.6
    plank = H.prism('plank', H.stadium_pts(8.0, 1.0, 12), 0.2, H.wood('berk', 'X', key='ijsstokje'), bev=0.045,
                    loc=(sx_, by - 1.0, top + 0.005), rot=(0, 0, math.pi / 2))
    cutter = H.box('zaagsnede', 1.6, 0.05, 0.5, None, loc=(sx_, cut_y, top + 0.09), bev=0.0, base=True)
    cutter.hide_render = True
    cutter.display_type = 'WIRE'
    bm = plank.modifiers.new('snede', 'BOOLEAN')
    bm.operation = 'DIFFERENCE'
    bm.object = cutter
    SP.zaagsel('zaagsel_snede', (sx_, cut_y), (0.9, 0.5), n=140, zf=top + 0.205, smin=0.01, smax=0.03,
               clip=(sx_ - 0.48, sx_ + 0.48, cut_y - 0.45, cut_y + 0.45))
    zaagselval('zaagselval', sx_, cut_y - 0.05, top + 0.1)
    # de handzaag staat met de tanden in de snede; de greep zit in opa's rechterhand
    G = (sx_ - 1.15, cut_y, top + 0.09 + 0.54)
    SP.handzaag('zaag', L=2.5, loc=G)
    o = FG.opa()
    o.place(sx_ - 2.65, cut_y + 0.75)
    o.face_to(sx_ + 6, cut_y + 0.75)
    o.pose(armR=(60, 0, 30), armL=(35, -10, 55), lean=8)
    reach(o, 'R', G)
    reach(o, 'L', (sx_ - 0.05, cut_y + 1.25, top + 0.42))
    # Joah knielt op de werkbank en houdt het stokje met twee handen recht voor zich vast
    j = FG.jongen()
    jz = top + j.S['leg_r'] + j.S['th_l'] - j.S['hip']
    j.place(sx_ + 1.3, by - 0.6, jz)
    j.face_to(sx_ - 5.0, by - 0.6)
    j.pose(armL=(40, 4, 15), armR=(40, 4, 15), legL=(0, 90), legR=(0, 90), lean=26)
    reach(j, 'L', (sx_ + 0.32, by - 0.95, top + 0.36))
    reach(j, 'R', (sx_ + 0.32, by - 0.25, top + 0.36))
    o.look_at((sx_, cut_y, top), amount=0.45)
    j.look_at(o.head_world(), amount=0.55)
    S.cam((bx - 1.2, -14.5, 7.4), (bx - 1.4, by - 0.8, 3.4), lens=45, fstop=0.18, focus=(sx_, cut_y, 3.4))
    S.render(out)


# ---------------------------------------------------------------- p. 9-10  een eigen hamer
def sp09_hamer(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(kist=(0.15, 2.6, 8, 2.8))
    WP.licht()
    bx, by = WP.BENCH
    top = WP.BENCH_TOP
    SC.bouw(loc=(9.6, 1.2, 0), rot=-25, stage='doos')
    o = FG.opa()
    o.place(bx - 1.6, by - 3.2)
    o.face_to(bx + 6, by - 6.0)
    o.pose(armR=(72, 4, 12), armL=(20, 12, 50), lean=10)
    o.hold(hamer_j('hamertje'), 'R', loc=(0, -0.05, -0.1), rot=(90, 0, 0))
    SP.dobbelsteen('opstapje', (bx + 1.9, by - 3.4, 0), rot=-8)
    j = FG.jongen()
    j.place(bx + 1.9, by - 3.4, 1.6)
    j.face_to(bx - 6, by - 6.0)
    j.pose(armL=(78, 6, 18), armR=(78, 6, 18), lean=6)
    o.look_at(j.head_world(), amount=0.7)
    j.look_at(o.head_world(), amount=0.7)
    for k in range(4):
        SP.spijkertje(f'losse_spijker{k}', (bx - 1.2 + 0.35 * k, by - 0.7 + 0.2 * (k % 2), top + 0.05),
                      rot=(math.pi / 2, 0, 0.4 * k), L=1.0)
    S.cam((bx + 0.2, -15.0, 6.4), (bx + 0.2, by - 1.6, 3.7), lens=50, fstop=0.18, focus=(bx + 0.2, by - 3.3, 4.0))
    S.render(out)


# ---------------------------------------------------------------- p. 11-12  motor en vleugel erbij
def sp11_onderdelen(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(bench=False, lamp=False, bankje=True, floor=False, rommel=False)
    WP.bouwplaats(kist=(13.6, -8.6, -32))
    WP.licht()
    sl, sr = (1.0, -1.6), -10
    SC.bouw(loc=(sl[0], sl[1], 0), rot=sr, stage='bouw')
    # Joah sleept de tweede vleugel (een wasknijper, twee keer zo lang als hijzelf) aan zijn linkerkant naar het schip:
    # voorkant omhoog in zijn handen, de achterkant schuift over de vloer
    j = FG.jongen()
    j.place(-5.4, -10.6)
    j.face_to(10.0, -11.0)
    j.pose(armL=(40, 10, 30), armR=(40, -10, 30), lean=8)
    Lk = 7.2
    Tk, Wk = 0.17 * Lk, 0.125 * Lk
    zf = 1.85
    th = math.asin((zf - Tk / 2) / Lk)
    Rk = Matrix.Rotation(-th, 4, 'X') @ Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    kn = SP.knijpertje('losse_vleugel', loc=(1.08, -1.15, zf), parent=j.root, L=Lk)
    kn.rotation_euler = Rk.to_euler()
    bpy.context.view_layer.update()
    Mj = j.root.matrix_world
    reach(j, 'L', tuple(Mj @ Vector((0.95, -1.0, zf + Tk / 2 * math.cos(th) - 0.02))))
    reach(j, 'R', tuple(Mj @ Vector((0.62, -1.3, zf - Tk / 2 * math.cos(th) - 0.08))))
    # opa draagt de motor (een garenklos) met twee handen naar het schip
    o = FG.opa()
    o.place(7.4, -9.4)
    o.face_to(-2.0, -15.0)
    o.pose(armL=(40, 20, 40), armR=(40, 20, 40), lean=4)
    Hh = 2.5
    SP.garenklos('losse_motor', '#c9c2b2', loc=(0, -0.86, 2.75), rot=(math.pi / 2, 0, 0), parent=o.root, R=1.05, Hh=Hh,
                 core=0.55, fill=0.85, draad=False)
    bpy.context.view_layer.update()
    M = o.root.matrix_world
    reach(o, 'L', tuple(M @ Vector((1.16, -0.98, 2.75))))
    reach(o, 'R', tuple(M @ Vector((-1.16, -0.98, 2.75))))
    o.look_at(j.head_world(), amount=0.35)
    j.look_at(o.head_world(), amount=0.3)
    S.cam((1.0, -41, 11.5), (1.0, -3.2, 5.0), lens=36, fstop=0.25, focus=(1.0, -10.0, 3.0))
    S.render(out)


# ---------------------------------------------------------------- p. 13-14  verven
def sp13_verven(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(bench=False, lamp=False, bankje=True, floor=False, rommel=False)
    WP.bouwplaats(kist=(3.0, -7.2, -12))
    WP.licht()
    sl, sr = (1.0, -2.2), 0
    SC.bouw(loc=(sl[0], sl[1], 0), rot=sr, stage='verf')
    zr = SC.HB + 1.45
    star = (sl[0], sl[1] - SC.R - 0.05, zr)
    # Joah staat op zijn dobbelsteen en schildert de ster, van opzij gezien zodat je zijn gezicht en de kwast ziet
    dx_, dy_ = sl[0] - 2.4, sl[1] - SC.R - 0.95
    SP.dobbelsteen('opstapje', (dx_, dy_, 0), rot=10)
    j = FG.jongen()
    j.place(dx_, dy_, 1.6)
    j.face_to(dx_ + 5.0, dy_ + 2.6)
    j.pose(armL=(95, 10, 20), armR=(25, -12, 30), lean=6)
    touch = Vector((star[0] - 0.42, star[1] - 0.1, star[2] - 0.05))
    bpy.context.view_layer.update()
    shL = j.sh['L'].matrix_world.translation
    d0 = (touch - shL).normalized()
    reach(j, 'L', tuple(touch - d0 * 1.0))
    bpy.context.view_layer.update()
    hp = j.hands['L'].matrix_world.translation.copy()
    d1 = (touch - hp).normalized()
    kw = SP.kwastje('kwast', '#d6a640', L=1.6)
    kw.rotation_mode = 'QUATERNION'
    kw.rotation_quaternion = (-d1).to_track_quat('Z', 'Y')
    kw.location = hp + d1 * 0.5
    o = FG.opa()
    o.place(sl[0] + 4.6, sl[1] - SC.R - 2.6)
    o.face_to(sl[0] - 3, sl[1] - 16)
    o.pose(armL=(30, 20, 70), armR=(15, 12, 25), lean=4)
    o.look_at(star, amount=0.5)
    j.look_at(star, amount=0.6)
    # kleine verfpotjes van kroonkurken naast het opstapje: rood, groen, blauw en goud
    for k, (c, dx, dy) in enumerate((('#d8473a', -5.4, -6.0), ('#3f8a55', -7.4, -5.6), ('#3561a8', -6.8, -7.6),
                                      ('goud', -4.3, -7.7))):
        SP.kroonkurk(f'verfpot{k}', (sl[0] + dx, sl[1] + dy, 0.02), paint=c, R=0.8, Hh=0.42, rot=(0, 0, 0.5 * k))
    SP.kwastje('kwast2', '#3561a8', loc=(sl[0] - 9.0, sl[1] - 7.4, 0.06), rot=(0, math.radians(92), math.radians(20)))
    S.cam((-1.4, -31, 9.4), (-0.4, -6.5, 4.0), lens=42, fstop=0.22, focus=(-1.0, -10.0, 3.5))
    S.render(out)


# ---------------------------------------------------------------- p. 15-16  klaar!
def sp15_klaar(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(bench=False, lamp=False, bankje=True, floor=False, rommel=False)
    WP.bouwplaats(kist=(4.5, -10.0, -18))
    WP.licht()
    SC.bouw(loc=(0.6, -2.4, 0), rot=-12, stage='klaar')
    j = FG.jongen()
    j.place(-6.6, -8.4)
    j.face_to(-2, -20)
    j.pose(armL=(165, 25, 15), armR=(165, 25, 15))
    j.hold(hamer_j(), 'R', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    o = FG.opa()
    o.place(8.0, -9.4)
    o.face_to(2, -20)
    o.pose(armL=(15, 15, 30), armR=(20, 35, 70))
    o.look_at(j.head_world(), amount=0.25)
    S.cam((0.6, -42, 12.0), (0.6, -3.5, 7.4), lens=35, fstop=0.28, focus=(0.6, -9.5, 4.5))
    S.render(out)


# ---------------------------------------------------------------- p. 17-18  ZOEF!
def sp17_zoef(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(bench=False, lamp=False, bankje=True, floor=False, rommel=False)
    WP.bouwplaats()
    WP.licht()
    sl, sr = (0.0, -1.6), 0
    sh = SC.bouw(loc=(sl[0], sl[1], 0), rot=sr, stage='klaar')
    st = sh['seat_top']
    o = FG.opa()
    x, y = ship_xy(sl, sr, *sh['seats']['L'])
    zit(o, x, y, st, rot=sr, armL=(62, -6, 28), armR=(62, 6, 28), lean=8)
    j = FG.jongen()
    x, y = ship_xy(sl, sr, *sh['seats']['R'])
    zit(j, x, y + 0.1, st, rot=sr, armL=(170, 28, 10), armR=(170, 28, 10), lean=-6)
    o.look_at(j.head_world(), amount=0.35)
    j.look_at((0, -40, 20), amount=0.6)
    rnd = np.random.default_rng(6)
    pts = []
    for k in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(7.5, 14)
        x_ = r * math.cos(a)
        if abs(x_) < 6.0:
            x_ = math.copysign(6.0 + abs(x_) * 0.5, x_ if x_ != 0 else 1)
        pts.append((x_, sl[1] + 1.5 + abs(r * math.sin(a)) * 0.4, rnd.uniform(9.5, 15.5)))
    SP.sterretjes('papierster', pts, size=0.75)
    S.cam((0.0, -21.5, 12.0), (0.0, -2.0, 8.6), lens=45, fstop=0.22, focus=(0.0, -3.6, 9.0))
    S.render(out)


# ---------------------------------------------------------------- p. 19-22  opa wordt stil (avond, op het gummetje)
def _bankje_avond(opts, close=False):
    S.setup(opts, 'spread', exposure=0.45)
    WP.bouw(bench=False, lamp=False, floor=False, mood='avond', kist=(-3.6, 3.0, -18))
    WP.licht_avond()
    SC.bouw(loc=(9.5, -2.0, 0), rot=-30, stage='klaar', flag=True)
    gx, gy = -7.4, 4.5
    seat = 1.0
    o = FG.opa(face=FG.OPA_ZACHT if close else FG.OPA_ERNSTIG)
    zit(o, gx - 1.05, gy - 0.25, seat, rot=4, armL=(18, 62, 78), armR=(30, 8, 45), lean=4)
    j = FG.jongen(face=FG.JOAH_TRAAN_LIEF if close else FG.JOAH_LUISTER)
    zit(j, gx + 1.15, gy - 0.35, seat, rot=4, armL=(28, 10, 60), armR=(30, 8, 60), lean=0)
    j.hold(hamer_j(), 'R', loc=(0, -0.25, 0.0), rot=(60, 0, 20))
    o.look_at(j.head_world(), amount=0.45 if close else 0.6)
    j.look_at(o.head_world(), amount=0.5 if close else 0.7)
    if close:
        S.cam((gx + 1.6, -7.4, 4.3), (gx, gy, 3.3), lens=58, fstop=0.16, focus=(gx, gy - 0.4, 3.6))
    else:
        S.cam((gx + 1.8, -15.0, 5.6), (gx + 1.0, gy - 0.5, 3.2), lens=42, fstop=0.2, focus=(gx, gy - 0.5, 3.2))


def sp19_stil(out, opts):
    _bankje_avond(opts, close=False)
    S.render(out)


def sp21_dichtbij(out, opts):
    _bankje_avond(opts, close=True)
    S.render(out)


# ---------------------------------------------------------------- p. 23-24  afscheid (nacht)
def sp23_afscheid(out, opts):
    S.setup(opts, 'spread', exposure=0.6)
    WP.bouw(bench=False, floor=False, bankje=True, mood='schemer', lamp_loc=(-9.0, 0.0, 12.0), lamp_energy=220, moon=(-6.5, 9.0),
            kist=(-8.9, -2.3, 22))
    WP.licht_schemer()
    sl, sr = (2.2, -2.0), -14
    sh = SC.bouw(loc=(sl[0], sl[1], 0), rot=sr, stage='klaar', lights=True, seats=False, wheel=False)
    o = FG.opa(face=FG.OPA_LIEF)
    x, y = ship_xy(sl, sr, -0.6, -2.4)
    o.place(x, y, SC.DECK, sr)
    o.face_to(-6, -14)
    o.pose(armL=(170, 28, 18), armR=(15, 10, 25))
    j = FG.jongen(face=FG.JOAH_VERDRIETIG)
    j.place(-6.2, -2.9)
    j.face_to(0.0, -2.0)
    j.pose(armL=(30, 12, 40), armR=(18, 10, 20))
    j.hold(hamer_j(), 'L', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    o.look_at(j.head_world(), amount=0.8)
    j.look_at(o.head_world(), amount=0.9)
    K.light('POINT', (-5.0, -9.5, 6.0), energy=150, color=(1.0, 0.75, 0.45), size=2.0, name='warmgezicht')
    K.light('POINT', (2.0, -8.5, 11.0), energy=110, color=(1.0, 0.8, 0.55), size=2.0, name='warmopa')
    S.cam((-0.6, -40, 11.6), (0.6, -3.0, 7.9), lens=34, fstop=0.25, focus=(-2.0, -4.0, 5.0))
    S.render(out)


# ---------------------------------------------------------------- p. 25-26  tot voorbij de sterren
def _nachtlucht_mat(key='nachtlucht'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    t = g.sstep(-5.0, 60.0, z)
    col = g.ramp(t, [(0.0, '#3c3a6a'), (0.12, '#2a3466'), (0.4, '#17244e'), (1.0, '#0b1433')])
    v = g.node('ShaderNodeTexVoronoi')
    g.link(g.comb(x, z, 0.0), v.inputs['Vector'])
    v.inputs['Scale'].default_value = 0.55
    star = g.math('MULTIPLY', g.sstep(0.05, 0.015, v.outputs['Distance']), g.sstep(8.0, 22.0, z))
    col = g.mix(g.math('MULTIPLY', star, 0.8), col, '#fff1cf')
    e = g.node('ShaderNodeEmission')
    g.link(col, e.inputs['Color'])
    e.inputs['Strength'].default_value = 1.0
    o = g.node('ShaderNodeOutputMaterial')
    g.link(e.outputs[0], o.inputs['Surface'])
    return m


def _kistje_huis(name, loc, rot=0.0, W=11.0, D=7.5, Hh=8.0):
    """Opa's werkplaats van buiten: een houten fruitkistje met spleten tussen de latten, een open deur
    met warm licht en een dakje van multiplex."""
    root = K.empty(name, loc, (0, 0, math.radians(rot)))
    lat = H.wood('grenen', 'X', var=0.15, key='kistlat', tint=('#c99c68', '#9a6b40'))
    latz = H.wood('grenen', 'Z', var=0.15, key='kistlat_z', tint=('#c99c68', '#9a6b40'))
    t, hgap = 0.3, 0.22
    nl = 8
    lh = (Hh - (nl - 1) * hgap) / nl
    dx0, dx1, dz1 = -2.6, -0.2, 4.6      # deuropening (in x vanaf het midden) en hoogte
    wx0, wx1, wz0, wz1 = 1.6, 3.6, 3.0, 5.0
    for k in range(nl):
        z0 = k * (lh + hgap)
        # voorkant in stukken rond deur en raampje
        segs = [(-W / 2, W / 2)]
        cuts = []
        if z0 < dz1:
            cuts.append((dx0, dx1))
        if z0 + lh > wz0 and z0 < wz1:
            cuts.append((wx0, wx1))
        for c0, c1 in cuts:
            new = []
            for a, b in segs:
                if c1 <= a or c0 >= b:
                    new.append((a, b))
                else:
                    if c0 > a:
                        new.append((a, c0))
                    if c1 < b:
                        new.append((c1, b))
            segs = new
        for i, (a, b) in enumerate(segs):
            H.box(f'{name}_voor{k}_{i}', b - a, t, lh, lat, loc=((a + b) / 2, -D / 2 + t / 2, z0), bev=0.05, base=True, parent=root)
        H.box(f'{name}_achter{k}', W, t, lh, lat, loc=(0, D / 2 - t / 2, z0), bev=0.05, base=True, parent=root)
        for sx in (-1, 1):
            H.box(f'{name}_zij{k}{sx}', t, D - 2 * t, lh, lat, loc=(sx * (W / 2 - t / 2), 0, z0), bev=0.05, base=True, parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            H.box(f'{name}_hoek{sx}{sy}', 0.5, 0.5, Hh, latz, loc=(sx * (W / 2 - 0.25), sy * (D / 2 - 0.25), 0), bev=0.05, base=True,
                  parent=root)
    ply = H.wood('berk', 'X', paint='#5a3a2c', grain=0.15, ply=0.06, key='dakplaat')
    for sy in (-1, 1):
        H.box(f'{name}_dak{sy}', W + 1.4, D / 2 + 1.2, 0.35, ply, loc=(0, sy * (D / 4 + 0.35), Hh + 1.45),
              rot=(sy * math.radians(-28), 0, 0), bev=0.06, parent=root)
    H.box(f'{name}_gevel', W - 0.2, 0.25, 2.4, lat, loc=(0, -D / 2 + 0.15, Hh), bev=0.04, base=True, parent=root)
    # open deur (een ijsstokje-deurtje dat openstaat)
    H.box(f'{name}_deur', dx1 - dx0, 0.2, dz1 - 0.1, H.wood('berk', 'Z', paint='#3f6f5a', grain=0.2, key='deurverf'),
          loc=(dx0 - 0.3, -D / 2 - 1.0, 0.0), rot=(0, 0, math.radians(-70)), bev=0.04, base=True, parent=root)
    # warm licht binnen
    L = K.light('POINT', (0, 0, 3.5), energy=900, color=(1.0, 0.72, 0.38), size=1.5, name=name + '_binnenlicht')
    L.parent = root
    L2 = K.light('AREA', ((dx0 + dx1) / 2, -D / 2 + 0.8, 2.6), energy=350, size=2.0, color=(1.0, 0.7, 0.38), name=name + '_deurlicht')
    L2.parent = root
    L2.rotation_euler = (math.radians(70), 0, 0)
    SP.hanglamp(name + '_lamp', (-1.0, 0.5, Hh - 1.8), ceiling=Hh + 0.3, energy=0, parent=root)
    return root


def _schemer_mat(key='schemerlucht'):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    g = H.G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    t = g.sstep(-10.0, 95.0, z)
    col = g.ramp(t, [(0.0, '#f7c79c'), (0.16, '#f0ad9a'), (0.34, '#d49db0'), (0.55, '#a59ccb'), (0.78, '#6f86c4'),
                     (1.0, '#4b67a8')], interp='B_SPLINE')
    v = g.node('ShaderNodeTexVoronoi')
    g.link(g.comb(x, z, 0.0), v.inputs['Vector'])
    v.inputs['Scale'].default_value = 0.35
    star = g.math('MULTIPLY', g.sstep(0.035, 0.012, v.outputs['Distance']), g.sstep(0.62, 0.9, t))
    col = g.mix(g.math('MULTIPLY', star, 0.55), col, '#fff4dc')
    e = g.node('ShaderNodeEmission')
    g.link(col, e.inputs['Color'])
    e.inputs['Strength'].default_value = 1.25
    o = g.node('ShaderNodeOutputMaterial')
    g.link(e.outputs[0], o.inputs['Surface'])
    return m


def _schemerwolk(name, loc, size, seed=0):
    key = 'schemerwolk'
    if key in H._M:
        m = H._M[key]
    else:
        m = H._new(key)
        g = H.G(m)
        tc = g.node('ShaderNodeTexCoord')
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (5, 5, 5)), 1.0, 8.0, 0.7)
        g.bsdf('#fff8f2', 0.95, sheen=1.0, normal=g.bump(n, 0.8, 0.05), emission='#ffd9c4', emit_str=0.22)
    rnd = np.random.default_rng(seed)

    def deform(D, P):
        n = np.sin(D[:, 0] * 7 + seed) * np.cos(D[:, 1] * 5) * 0.12 + np.sin(D[:, 2] * 9 + seed * 2) * 0.08
        return P * (1 + n)[:, None]
    ob = K.blob(name, size, 2.0, (64, 32), deform=deform, mat=m, loc=loc)
    for k in range(7):
        sc_ = rnd.uniform(0.45, 0.8)
        K.blob(f'{name}_{k}', (size[0] * sc_ * 0.55, size[1] * sc_, size[0] * sc_ * 0.5), 2.0, (48, 24), deform=deform, mat=m,
               parent=ob, loc=(rnd.uniform(-1, 1) * size[0] * 0.75, rnd.uniform(-0.3, 0.3), rnd.uniform(0.2, 0.9) * size[2]))
    return ob


def sp25_vlucht(out, opts):
    """Alleen de lucht bij schemering, met het schip dat opstijgt en opa die zwaait."""
    S.setup(opts, 'spread', exposure=0.35)
    K.world_color('#c3b4d6', 0.55)
    K.mesh_obj('lucht', [(-180, 0, -40), (180, 0, -40), (180, 0, 120), (-180, 0, 120)], [(0, 1, 2, 3)], _schemer_mat(),
               loc=(0, 90, 0))
    # het schip, schuin omhoog, met opa die zwaait
    sh = SC.bouw(loc=(4.5, 14.0, 13.0), rot=-24, stage='klaar', lights=True, seats=False, wheel=False)
    sh['root'].rotation_euler = (math.radians(10), math.radians(-9), math.radians(-24))
    o = FG.opa(face=FG.OPA_LIEF)
    o.place(-0.4, -2.4, SC.DECK)
    o.root.parent = sh['root']
    o.pose(armL=(165, 30, 15), armR=(20, 10, 20))
    # wattenwolkjes, lager dan het schip
    for k, (x, y, z, sz) in enumerate(((-26, 34, 6.5, 5.0), (-9, 42, 4.0, 6.0), (14, 38, 6.0, 5.4), (32, 46, 9.0, 4.6),
                                      (-38, 50, 12.0, 3.8), (26, 30, 1.5, 4.0))):
        _schemerwolk(f'wolk{k}', (x, y, z), (sz * 1.7, sz * 0.7, sz * 0.6), seed=k)
    # een paar kleine sterretjes aan dunne draadjes, hoog in de lucht
    gs = H._new('gouden_ster_klein')
    g = H.G(gs)
    g.bsdf('#d6a640', 0.3, metal=1.0, emission='#f0c070', emit_str=0.15)
    dr = H.thread('#efe6dc', key='draadje_licht')
    for k, (x, y, z, sz) in enumerate(((-26, 30, 27, 0.6), (-12, 40, 33, 0.45), (22, 34, 30, 0.55), (34, 44, 26, 0.4),
                                      (-34, 46, 20, 0.4), (12, 50, 38, 0.35))):
        K.poly_obj(f'ster{k}', K.round_star_pts(sz, 0.5), depth=0.12, bevel=0.03, mat=gs, loc=(x, y, z),
                   rot=(math.pi / 2, 0, 0.3 * k))
        K.curve_tube(f'sterdraad{k}', [(x, y, z + sz * 0.95), (x, y, 90)], 0.008, dr)
    # een bleek houten maantje
    maan = H.wood('berk', 'X', key='maanhout', tint=('#f6ead0', '#eadbb8'))
    pts = [(2.2 * math.cos(math.radians(a)), 2.2 * math.sin(math.radians(a))) for a in np.linspace(60, 300, 48)]
    pts += [(1.76 + 2.02 * math.cos(math.radians(a)), 2.02 * math.sin(math.radians(a))) for a in np.linspace(251, 109, 40)[1:-1]]
    H.prism('maantje', pts, 0.25, maan, bev=0.06, loc=(-24.0, 40.0, 31.0), rot=(math.pi / 2, 0, math.radians(15)))
    K.curve_tube('maandraad', [(-24.0, 40.0, 33.2), (-24.0, 40.0, 90)], 0.008, dr)
    # klein spoor van gouden glinsteringen achter de motor
    bpy.context.view_layer.update()
    Mo = sh['root'].matrix_world
    m0 = Mo @ Vector((0, SC.R + 2.6, SC.HB + 1.5))
    path = [m0, m0 + Vector((-3, -1, -2.5)), m0 + Vector((-7, -2, -6)), m0 + Vector((-11, -3, -10))]
    C, u = K.catmull([tuple(p_) for p_ in path], 14)
    gm = H._new('spoorgoud')
    g = H.G(gm)
    g.bsdf('#e8b84f', 0.25, metal=1.0, emission='#ffcf6a', emit_str=0.8)
    rnd = np.random.default_rng(5)
    for i in range(0, len(C), 2):
        c = Vector(C[i]) + Vector(rnd.normal(0, 0.25 + 0.5 * u[i], 3))
        sz = 0.3 * (1 - u[i]) + 0.08
        if i % 4 == 0:
            K.poly_obj(f'spoorster{i}', K.round_star_pts(sz, 0.5), depth=0.05, bevel=0.015, mat=gm, loc=tuple(c),
                       rot=(math.pi / 2 + rnd.uniform(-0.5, 0.5), rnd.uniform(-1, 1), rnd.uniform(0, 6)))
        else:
            H.ball(f'spoorpunt{i}', sz * 0.3, gm, loc=tuple(c), res=(12, 6))
    # licht: lage, warme avondzon van links, koel licht van boven
    K.light('SUN', (-70, -10, 14), (0, 0, 0), energy=3.2, color=(1.0, 0.72, 0.48), angle=2.5, name='Avondzon')
    K.light('SUN', (20, -30, 80), (0, 0, 0), energy=0.6, color=(0.7, 0.75, 1.0), angle=8.0, name='Hemel')
    K.light('AREA', (-4, -30, 6), (4, 14, 12), energy=900, size=24, color=(1.0, 0.86, 0.78), name='Vullicht', visible_glossy=False)
    S.cam((-6.0, -30.0, 3.0), (-3.5, 14.0, 19.5), lens=30, fstop=0.5, focus=(4.5, 14.0, 18.0))
    S.render(out)


# ---------------------------------------------------------------- p. 27-28  Joah bij het raam
def sp27_raam(out, opts):
    S.setup(opts, 'spread', exposure=1.1)
    SP.vloer(-26, 26, -30, 7)
    wall = H.wood('beuk', 'Z', paint='#6d7fa6', grain=0.15, key='slaapkamerwand')
    wy = 6.0
    xa, xb, za, zb = -1.0, 9.0, 3.2, 11.2
    H.box('wand_l', 30, 0.5, 26, wall, loc=(xa - 15, wy, 0), bev=0, base=True)
    H.box('wand_r', 30, 0.5, 26, wall, loc=(xb + 15, wy, 0), bev=0, base=True)
    H.box('wand_o', xb - xa, 0.5, za, wall, loc=((xa + xb) / 2, wy, 0), bev=0, base=True)
    H.box('wand_b', xb - xa, 0.5, 26 - zb, wall, loc=((xa + xb) / 2, wy, zb), bev=0, base=True)
    H.box('plafond', 70, 60, 0.6, wall, loc=(0, -20, 24), bev=0, base=True)
    fr = H.wood('eiken', 'X', key='lijst', coat=0.15)
    frz = H.wood('eiken', 'Z', key='lijst_z', coat=0.15)
    w, d = 0.7, 0.7
    H.box('lijst_onder', xb - xa + 2 * w, d, w, fr, loc=((xa + xb) / 2, wy - 0.3, za - w / 2), bev=0.08)
    H.box('lijst_boven', xb - xa + 2 * w, d, w, fr, loc=((xa + xb) / 2, wy - 0.3, zb + w / 2), bev=0.08)
    for x in (xa - w / 2, xb + w / 2):
        H.box(f'lijst_zij{x:.1f}', w, d, zb - za, frz, loc=(x, wy - 0.3, (za + zb) / 2), bev=0.08)
    SP.lucifer('roede_h', ((xa + xb) / 2, wy, (za + zb) / 2), (0, 0, 0), L=(xb - xa))
    SP.lucifer('roede_v', ((xa + xb) / 2, wy + 0.25, (za + zb) / 2), (0, math.pi / 2, 0), L=(zb - za))
    SP.ijsstokje('vensterbank', ((xa + xb) / 2, wy - 0.7, za - 0.1))
    sky = WP._buiten_mat('buiten_nacht', 'nacht')
    K.mesh_obj('buiten', [(-60, 0, -10), (60, 0, -10), (60, 0, 50), (-60, 0, 50)], [(0, 1, 2, 3)], sky, loc=(0, wy + 30, 0))
    mm = H.emit('#fff1c8', 6.0, key='maan')
    K.mesh_obj('maan', *WP._disc(2.4), mm, loc=(9.0, wy + 27, 17.0), rot=(math.pi / 2, 0, 0))
    # één sterretje net iets feller dan de rest
    H.ball('opa_ster', 0.13, H.emit('#ffe6b0', 5.0, key='opa_ster'), loc=(1.2, wy + 18, 15.5), res=(16, 8))
    K.light('SUN', (20, 60, 25), (0, 0, 0), energy=3.0, color=(0.62, 0.72, 1.0), angle=1.0, name='Maanlicht')
    K.world_color('#2c3c6c', 0.18)
    K.light('AREA', (6, -26, 12), (3, 2, 4), energy=800, size=14, color=(0.6, 0.68, 1.0), name='Vullicht', visible_glossy=False)
    K.light('AREA', (4.0, 1.0, 9.0), (4.2, 3.6, 4.0), energy=60, size=3, color=(0.7, 0.78, 1.0), name='maangezicht', visible_glossy=False)
    # bedje en nachtlampje
    SP.bedje('bed', (-7.5, 1.8, 0), rot=10)
    SP.garenklos('nachtkastje', '#3561a8', loc=(-3.4, 3.6, 0), R=1.0, Hh=2.4)
    SP.vingerhoed('nachtlampkap', (-3.4, 3.6, 2.4 + 1.3), rot=(math.pi, 0, 0), R=0.55, Hh=1.3)
    K.blob('nachtlampje', (0.18, 0.18, 0.26), 2.0, (24, 12), mat=H.bulb('#ffc070', 30.0, key='nachtlampje'),
           loc=(-3.4, 3.6, 2.4 + 0.25))
    K.light('POINT', (-3.4, 3.2, 2.9), energy=45, color=(1.0, 0.68, 0.35), size=0.3, name='nachtlicht')
    # Joah op de dobbelsteen voor het raam, met zijn hamer
    SP.gereedschapskist('opas_kist', (1.5, 3.4, 0), rot=18)
    SP.dobbelsteen('opstapje', (4.2, 3.6, 0), rot=-6)
    j = FG.jongen()
    j.place(4.2, 3.6, 1.6)
    j.face_to(2.5, 12)
    j.pose(armR=(22, 22, 35), armL=(10, 10, 25))
    j.hold(hamer_j(), 'R', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    j.look_at((1.2, wy + 18, 15.5), amount=0.6)
    S.cam((10.5, -11.0, 3.0), (2.8, 4.4, 6.0), lens=30, fstop=0.18, focus=(4.2, 3.6, 3.6))
    S.render(out)


# ---------------------------------------------------------------- p. 29  Joah bouwt zelf (pagina)
def p29_einde(out, opts):
    S.setup(opts, 'page', exposure=0.35)
    WP.bouw(kist=(0.15, 2.6, -12, 2.8))
    WP.licht()
    bx, by = WP.BENCH
    top = WP.BENCH_TOP
    notendop_bootje('bootje', (bx - 0.9, by - 0.6, top), rot=-20)
    SP.dobbelsteen('opstapje', (bx - 3.8, by - 1.2, 0), rot=-10)
    j = FG.jongen()
    j.place(bx - 3.8, by - 1.2, 1.6)
    j.face_to(bx + 1.5, by - 6.0)
    j.pose(armL=(70, 30, 50), armR=(20, 14, 35), lean=6)
    j.hold(hamer_j(), 'L', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    j.look_at((bx - 0.9, by - 0.6, top + 0.6), amount=0.7)
    S.cam((bx - 2.0, -10.5, 6.6), (bx - 2.0, by - 0.6, 3.6), lens=45, fstop=0.16, focus=(bx - 2.6, by - 1.0, 3.8))
    S.render(out)


# ---------------------------------------------------------------- titelpagina: vignet (transparant)
def titel(out, opts):
    S.setup(opts, 'page', exposure=0.3, transparent=True)
    K.world_color('#ffffff', 0.9)
    K.light('AREA', (-8, -12, 14), (0, 0, 2.5), energy=1700, size=8, color=(1.0, 0.95, 0.88))
    K.light('AREA', (9, -6, 6), (0, 0, 2.5), energy=550, size=6, color=(0.9, 0.93, 1.0))
    # een vlotje van ijsstokjes met de gereedschapskist van opa in het midden
    for k in range(7):
        H.prism(f'vlot{k}', H.stadium_pts(10.0, 1.0, 12), 0.2, H.wood('berk', 'X', key='ijsstokje'), bev=0.045,
                loc=(0.25 * (k % 2), -3.2 + k * 1.04, 0), rot=(0, 0, math.radians(1.2 * (k % 3 - 1))))
    # opa's gereedschapskist vooraan op het vlotje, opa en Joah er vlak achter
    SP.gereedschapskist('kist', (0.5, -1.7, 0.2), rot=36, s=0.9)
    SP.krulletjes('vlotkrullen', (-3.4, -2.2), (2.0, 1.2), n=12, zf=0.2, rmin=0.07, rmax=0.16, clip=(-4.8, 4.8, -3.6, 3.0))
    H.box('vlotblokje', 1.0, 0.7, 0.5, H.wood('grenen', 'X', key='blokje'), loc=(-3.4, -2.0, 0.2), rot=(0, 0, 0.4), bev=0.06, base=True)
    for k in range(2):
        SP.spijkertje(f'vlotspijker{k}', (2.6 + 0.5 * k, -2.5 + 0.25 * k, 0.24), rot=(0, math.pi / 2, 1.0 + 0.8 * k), L=0.8)
    o = FG.opa()
    o.place(3.1, 0.7, 0.2)
    o.face_to(0.6, -8)
    o.pose(armL=(25, 50, 70), armR=(15, 10, 25))
    j = FG.jongen()
    j.place(-1.7, -0.2, 0.2)
    j.face_to(0.5, -8)
    j.pose(armR=(140, 15, 20), armL=(15, 12, 25))
    j.hold(hamer_j(), 'R', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    o.look_at(j.head_world(), amount=0.5)
    S.cam((0.15, -27, 9.8), (0.15, -0.4, 2.6), lens=72, fstop=None)
    S.render(out)


# ---------------------------------------------------------------- schutblad: patroon op donkerblauw hout
def schutblad(out, opts):
    S.setup(opts, 'page', exposure=0.2)
    bord = H.wood('beuk', 'X', paint='#24365e', grain=0.22, rough=0.55, key='schutblad_bord')
    H.box('bord', 60, 60, 1.0, bord, loc=(0, 0, -1.0), bev=0, base=True)
    K.world_color('#c9d3e8', 0.25)
    K.light('AREA', (-12, -10, 30), (0, 0, 0), energy=5200, size=14, color=(1.0, 0.95, 0.88))
    gold = H.metal('#d6a640', 0.28, key='goudverf')
    n = 5
    cell = 4.2
    kinds = ['hamer', 'knoop', 'ster', 'knijper', 'klos', 'dop']
    k = 0
    for i in range(n + 1):
        for jx in range(n + 1):
            x = (jx - n / 2) * cell + (cell / 2 if i % 2 else 0)
            y = (i - n / 2) * cell
            kind = kinds[(i * 2 + jx) % len(kinds)]
            a = math.radians(((i + jx) % 4) * 35 - 50)
            if kind == 'hamer':
                h = SP.hamertje(f'pat_hamer{k}', bead='#d4473a', L=2.0, br=0.34)
                h.location, h.rotation_euler = (x, y, 0.18), (math.pi / 2, 0, a)
            elif kind == 'knoop':
                SP.knoop(f'pat_knoop{k}', (x, y, 0.0), ('#d8473a', '#e7b23b', '#f4f1ea')[k % 3], r=1.0, rot=(0, 0, a))
            elif kind == 'ster':
                K.poly_obj(f'pat_ster{k}', K.round_star_pts(1.1, 0.5), depth=0.12, bevel=0.03, mat=gold, loc=(x, y, 0.0),
                           rot=(0, 0, a))
            elif kind == 'knijper':
                SP.knijpertje(f'pat_knijper{k}', loc=(x - 1.5 * math.cos(a), y - 1.5 * math.sin(a), 0.21), rot=(0, 0, a), L=3.0)
            elif kind == 'klos':
                SP.garenklos(f'pat_klos{k}', ('#d8473a', '#3f8a55', '#e7b23b')[k % 3], loc=(x, y, 0.0), R=0.9, Hh=1.9, draad=False)
            else:
                SP.frisdrankdop(f'pat_dop{k}', (x, y, 0.95), ('#f4f2ec', '#3f8a55', '#d8473a')[k % 3], up=False, R=1.2, Hh=0.95)
            k += 1
    cam = S.cam((0, 0, 60), (0, 0, 0), lens=50, fstop=None)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 5 * cell
    cam.rotation_mode = 'XYZ'
    cam.rotation_euler = (0, 0, 0)
    S.render(out)


# ---------------------------------------------------------------- omslag (achter | voor)
def omslag(out, opts):
    S.setup(opts, 'spread', exposure=0.45)
    WP.bouw(bench=True, bench_at=(-9.5, 1.4), lamp=True, lamp_loc=(-9.0, 2.0, 7.6), floor=False, bankje=False, mood='avond',
            rommel=False)
    WP.licht_avond(fill=1300)
    sl, sr = (11.8, -2.2), -18
    SC.bouw(loc=(sl[0], sl[1], 0), rot=sr, stage='klaar', lights=True)
    SP.gereedschapskist('opas_kist', (4.9, -13.8, 0), rot=30)
    SP.bolletje_wol('wol', (-4.2, 3.2, 2.0), R=2.0, col='#d9a441')
    SP.muntstapel('munten', (20.0, -9.0, 0), n=3)
    j = FG.jongen()
    j.place(8.0, -15.2)
    j.face_to(6, -28)
    j.pose(armL=(25, 20, 30), armR=(150, 25, 15))
    j.hold(hamer_j(), 'R', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    o = FG.opa()
    o.place(11.2, -14.8)
    o.face_to(8, -28)
    o.pose(armR=(25, 55, 75), armL=(18, 10, 25))
    o.look_at(j.head_world(), amount=0.4)
    j.look_at(o.head_world(), amount=0.3)
    h = hamer_j('bank_hamer')
    h.location, h.rotation_euler = (-9.0, 0.9, WP.BENCH_TOP + 0.18), (math.pi / 2, 0, math.radians(-25))
    S.cam((6.0, -42.0, 7.0), (6.0, -3.0, 5.6), lens=33, fstop=0.28, focus=(9.6, -15.0, 3.6))
    S.render(out)


