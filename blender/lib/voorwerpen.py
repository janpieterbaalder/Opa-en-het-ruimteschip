"""Vijftig extra alledaagse voorwerpen (op ware grootte, in cm), zoals je ze in elk huis of elke
supermarkt in Nederland vindt. Elk voorwerp: functie(naam, loc, rot, parent, ...) -> object.
"""
import bpy, math, os
import numpy as np
from mathutils import Vector
from . import core as K, hout as H, spullen as SP


def _mat(key, build):
    if key in H._M:
        return H._M[key]
    m = H._new(key)
    build(H.G(m))
    return m


def _place(ob, loc, rot, parent=None):
    ob.location, ob.rotation_euler = loc, rot
    if parent is not None:
        ob.parent = parent
    return ob


def _noise_mat(key, c0, c1, scale=8.0, rough=0.6, bump=0.3, metal=0.0, sheen=0.0, coat=0.0):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (scale, scale, scale)), 1.0, 5.0, 0.6)
        g.bsdf(g.mix(n, c0, c1), rough, metal=metal, sheen=sheen, coat=coat, normal=g.bump(n, bump, 0.02))
    return _mat(key, b)


def _stripes_mat(key, c0, c1, period, axis=2, rough=0.4, coat=0.2, twist=0.0):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        c = (x, y, z)[axis]
        if twist:
            c = g.math('ADD', c, g.math('MULTIPLY', g.math('ARCTAN2', y, x), twist))
        st = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', c, period)), 0.5)
        g.bsdf(g.mix(st, c0, c1), rough, coat=coat)
    return _mat(key, b)


# ---------------------------------------------------------------- 1-10: kurk, suiker, koffie, ei, pasta
def wijnkurk(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, h=4.4):
    return _place(H.cyl(name, 1.2, h, H.cork(), bev=0.08, seg=48), loc, rot, parent)


def champagnekurk(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    """Champagnekurk met het draadkapje (muselet): een stoeltje."""
    ob = K.lathe(name, [(0, 0), (0.9, 0), (0.95, 0.1), (1.0, 2.3), (1.45, 2.45), (1.55, 3.0), (1.3, 3.6), (0.8, 3.85), (0, 3.9)],
                 64, H.cork())
    met = H.metal('#c9c2ae', 0.3, key='muselet')
    goud = H.metal('#d6b15a', 0.25, key='muselet_kap')
    H.cyl(name + '_kapje', 0.85, 0.06, goud, loc=(0, 0, 3.88), bev=0.02, seg=40, parent=ob)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        pts = [(0.7 * math.cos(a), 0.7 * math.sin(a), 3.92), (1.35 * math.cos(a), 1.35 * math.sin(a), 3.6),
               (1.56 * math.cos(a), 1.56 * math.sin(a), 2.9), (1.05 * math.cos(a), 1.05 * math.sin(a), 2.3)]
        K.curve_tube(f'{name}_draad{k}', pts, 0.035, met, ob)
    K.curve_tube(name + '_ring', [(1.07 * math.cos(a), 1.07 * math.sin(a), 2.28) for a in np.linspace(0, 2 * math.pi, 41)[:-1]],
                 0.04, met, ob, cyclic=True)
    return _place(ob, loc, rot, parent)


def suikerklontje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, s=1.5):
    m = _mat('suiker', lambda g: g.bsdf('#fbfaf6', 0.75, sheen=0.3,
                                        normal=g.bump(g.noise(g.vmath('MULTIPLY', g.node('ShaderNodeTexCoord').outputs['Object'],
                                                                      (40, 40, 40)), 1.0, 3.0), 0.6, 0.01)))
    return _place(H.box(name, s, s, s, m, bev=0.12, base=True), loc, rot, parent)


def suikerzakje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _stripes_mat('suikerzakje', '#f5f2ea', '#3a6fb0', 1.5, axis=1, rough=0.7, coat=0.0)
    return _place(K.blob(name, (1.5, 2.25, 0.12), (6.0, 6.0, 2.0), (48, 24), mat=m), loc, rot, parent)


def koffiemelkcupje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    wit = H.plastic('#f6f4ef', 0.35, key='cupje_wit')
    ob = K.lathe(name, [(0, 0), (0.9, 0), (1.25, 1.5), (1.4, 1.55), (1.38, 1.6), (1.18, 1.55), (0.82, 0.1), (0, 0.1)], 48, wit)
    folie = H.metal('#d9dcdf', 0.3, key='folie')
    H.cyl(name + '_deksel', 1.45, 0.03, folie, loc=(0, 0, 1.6), bev=0.0, seg=48, parent=ob)
    H.box(name + '_lipje', 0.8, 0.5, 0.03, folie, loc=(1.6, 0, 1.62), rot=(0, math.radians(-15), 0), bev=0.0, parent=ob)
    return _place(ob, loc, rot, parent)


def eierdopje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    prof = [(0, 0), (1.3, 0), (1.3, 0.25), (0.6, 0.5), (0.55, 1.1), (1.2, 1.5), (1.95, 2.4), (2.0, 3.3), (1.85, 3.3), (1.8, 2.5),
            (1.1, 1.7), (0, 1.6)]
    return _place(K.lathe(name, prof, 64, H.wood('beuk', 'Z', key='eierdop_hout', coat=0.3)), loc, rot, parent)


def eierschaal(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _noise_mat('eierschaal', '#efe3d0', '#e6d4bb', 6.0, 0.55, 0.1, sheen=0.2)
    prof = []
    for a in range(0, 101, 5):
        r = math.radians(a)
        prof.append((2.1 * math.sin(r), 2.6 * (1 - math.cos(r))))
    ob = K.lathe(name, prof, 64, m, zfn=lambda x, y: 0.12 * math.sin(7 * math.atan2(y, x)) * (abs(x) + abs(y) > 1.9),
                 close_top=False)
    K.modifier(ob, 'SOLIDIFY', thickness=0.05, offset=-1.0)
    return _place(ob, loc, rot, parent)


def macaroni(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, R=0.9, ang=130):
    m = _noise_mat('pasta', '#f1d48e', '#e2bb6c', 12.0, 0.55, 0.15)
    pts = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), 0) for a in np.linspace(0, ang, 16)]
    ob, _ = K.tube(name, pts, [0.32] * len(pts), mat=m, caps=(False, False), ring=32)
    K.modifier(ob, 'SOLIDIFY', thickness=0.07, offset=-1.0)
    m.use_backface_culling = False
    return _place(ob, loc, rot, parent)


def farfalle(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _noise_mat('pasta', '#f1d48e', '#e2bb6c', 12.0, 0.55, 0.15)

    def fn(U, V):
        x = (U - 0.5) * 3.2
        pinch = 0.35 + 0.65 * np.abs(U - 0.5) * 2
        y = (V - 0.5) * 2.2 * pinch
        z = 0.18 * np.sin((U - 0.5) * 9) * np.abs(V - 0.5) * 2 + 0.05 * np.sin(V * 40) * (np.abs(V - 0.5) > 0.42)
        return np.stack([x, y, z], 1)
    ob = K.grid_mesh(name, 40, 20, fn, m)
    K.modifier(ob, 'SOLIDIFY', thickness=0.06, offset=0.0)
    return _place(ob, loc, rot, parent)


def spaghetti_bundel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, n=24, L=25.0):
    m = _noise_mat('spaghetti', '#efd39a', '#e3bf78', 3.0, 0.4, 0.05)
    root = K.empty(name, loc, rot, parent=parent)
    rnd = np.random.default_rng(4)
    for k in range(n):
        a, r = rnd.uniform(0, 2 * math.pi), 0.45 * math.sqrt(rnd.random())
        H.cyl(f'{name}_{k}', 0.09, L + rnd.uniform(-0.3, 0.3), m, loc=(r * math.cos(a), r * math.sin(a), 0), bev=0.02, seg=8,
              parent=root)
    K.curve_tube(name + '_elastiek', [(0.6 * math.cos(a), 0.6 * math.sin(a), L * 0.6) for a in np.linspace(0, 2 * math.pi, 25)[:-1]],
                 0.06, H.plastic('#c9473b', 0.6, key='elastiek_#c9473b'), root, cyclic=True)
    return root


# ---------------------------------------------------------------- 11-25: keukenkastje en natuur
def koffieboon(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _noise_mat('koffieboon', '#4a2a17', '#6b3f22', 10.0, 0.35, 0.1, coat=0.4)

    def d(D, P):
        groove = np.exp(-(D[:, 1] ** 2) / 0.004) * (D[:, 2] > 0)
        P = P.copy()
        P[:, 2] = np.where(D[:, 2] > 0, P[:, 2] * 0.55, P[:, 2]) - groove * 0.12
        return P
    return _place(K.blob(name, (0.55, 0.42, 0.35), 2.0, (48, 24), deform=d, mat=m), loc, rot, parent)


def kruidnagel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _noise_mat('kruidnagel', '#3d2216', '#5c3320', 14.0, 0.7, 0.4)
    ob = K.lathe(name, [(0, 0), (0.05, 0.0), (0.12, 1.0), (0.14, 1.15), (0, 1.16)], 16, m)
    for k in range(4):
        a = k * math.pi / 2
        H.capsule(f'{name}_kelk{k}', (0, 0, 1.15), (0.22 * math.cos(a), 0.22 * math.sin(a), 1.38), 0.06, m, ob)
    H.ball(name + '_knop', 0.11, m, loc=(0, 0, 1.33), parent=ob, res=(16, 8))
    return _place(ob, loc, rot, parent)


def steranijs(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, s=1.0):
    m = _noise_mat('steranijs', '#5e321c', '#8a5131', 10.0, 0.65, 0.5)
    zaad = H.plastic('#b07a3e', 0.2, key='anijszaad', coat=0.6)
    root = K.empty(name, loc, rot, parent=parent)
    for k in range(8):
        a = k * math.pi / 4
        e = K.empty(f'{name}_p{k}', (0, 0, 0), (0, 0, a), parent=root)
        K.blob(f'{name}_peul{k}', (0.62 * s, 0.22 * s, 0.24 * s), (2.0, 2.0, 2.6), (32, 16), mat=m, parent=e, loc=(0.62 * s, 0, 0),
               deform=lambda D, P: P * np.where(D[:, 0] > 0, 1 - 0.35 * D[:, 0] ** 2, 1)[:, None])
        K.blob(f'{name}_zaad{k}', (0.22 * s, 0.11 * s, 0.08 * s), 2.0, (16, 8), mat=zaad, parent=e, loc=(0.6 * s, 0, 0.2 * s))
    return root


def kaneelstokje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=8.0):
    m = _noise_mat('kaneel', '#7c4426', '#a15f36', 6.0, 0.8, 0.5)
    pts = [(0.15 + 0.06 * t) * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(0.3, 4.4 * math.pi, 70)]
    V = [(p[0], p[1], 0) for p in pts] + [(p[0], p[1], L) for p in pts]
    n = len(pts)
    F = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    ob = K.mesh_obj(name, V, F, m)
    K.modifier(ob, 'SOLIDIFY', thickness=0.06, offset=0.0)
    m.use_backface_culling = False
    return _place(ob, loc, rot, parent)


def laurierblad(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=6.0):
    m = _noise_mat('laurier', '#8b9a5f', '#6f7d48', 4.0, 0.7, 0.2, sheen=0.2)

    def fn(U, V):
        w = np.sin(U * math.pi) ** 0.8 * 1.1
        x = U * L
        y = (V - 0.5) * 2 * w
        z = 0.25 * np.sin(U * math.pi) - 0.3 * (V - 0.5) ** 2 * 2 + 0.08 * np.abs(V - 0.5) * 0
        return np.stack([x, y, z], 1)
    ob = K.grid_mesh(name, 30, 10, fn, m)
    K.modifier(ob, 'SOLIDIFY', thickness=0.03, offset=0.0)
    K.curve_tube(name + '_nerf', [(0, 0, 0.02), (L * 0.5, 0, 0.27), (L, 0, 0.02)], 0.03, m, ob)
    return _place(ob, loc, rot, parent)


def rozijn(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _noise_mat('rozijn', '#3a1f22', '#5b2f30', 9.0, 0.35, 0.6, coat=0.3)
    return _place(K.blob(name, (0.55, 0.4, 0.3), 2.0, (48, 24), mat=m,
                         deform=lambda D, P: P * (1 + 0.12 * np.sin(D[:, 0] * 13) * np.cos(D[:, 1] * 11))[:, None]),
                  loc, rot, parent)


def pinda(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        v = g.node('ShaderNodeTexVoronoi')
        v.feature = 'DISTANCE_TO_EDGE'
        g.link(tc.outputs['Object'], v.inputs['Vector'])
        v.inputs['Scale'].default_value = 6.0
        g.bsdf(g.ramp(v.outputs['Distance'], [(0.0, '#b48a55'), (0.1, '#d9b98a')]), 0.85, normal=g.bump(v.outputs['Distance'], 0.5, 0.03))
    m = _mat('pindadop', b)
    return _place(K.blob(name, (1.6, 0.7, 0.7), 2.0, (64, 32), mat=m,
                         deform=lambda D, P: P * (1 - 0.18 * np.exp(-(D[:, 0] ** 2) / 0.02))[:, None]), loc, rot, parent)


def hazelnoot(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _stripes_mat('hazelnoot', '#8a5a33', '#a26c40', 0.12, axis=0, rough=0.35, coat=0.3)
    ob = K.blob(name, (0.8, 0.8, 0.85), 2.0, (48, 24), mat=m, deform=lambda D, P: P + np.stack(
        [np.zeros(len(P)), np.zeros(len(P)), 0.25 * np.clip(D[:, 2], 0, 1) ** 4], 1))
    K.blob(name + '_bodem', (0.55, 0.55, 0.12), 2.0, (32, 16), mat=H.plastic('#c9a77a', 0.8, key='hazel_bodem'), parent=ob,
           loc=(0, 0, -0.78))
    return _place(ob, loc, rot, parent)


def dennenappel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, Hh=7.0):
    m = _noise_mat('dennenappel', '#5a3a22', '#8a5c34', 6.0, 0.8, 0.4)
    root = K.empty(name, loc, rot, parent=parent)
    n = 110
    for k in range(n):
        t = k / (n - 1)
        z = 0.3 + t * (Hh - 0.6)
        r = 1.9 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.8 * (1 - 0.3 * t)
        a = k * math.radians(137.5)
        e = K.empty(f'{name}_s{k}', (0, 0, z), (0, 0, a), parent=root)
        H.box(f'{name}_schub{k}', max(0.4, r), 0.55, 0.12, m, loc=(max(0.4, r) / 2, 0, 0), rot=(0, math.radians(-25 + 30 * t), 0),
              bev=0.04, parent=e)
    H.cyl(name + '_kern', 0.45, Hh, m, bev=0.2, seg=16, parent=root)
    return root


def kastanje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _stripes_mat('kastanje', '#5a2a14', '#6e3519', 0.3, axis=0, rough=0.15, coat=0.6)
    ob = K.blob(name, (1.4, 1.3, 1.0), 2.0, (64, 32), mat=m, deform=lambda D, P: P + np.stack(
        [np.zeros(len(P)), np.zeros(len(P)), 0.3 * np.clip(D[:, 2], 0, 1) ** 6], 1))
    K.blob(name + '_navel', (0.9, 0.8, 0.12), 2.0, (32, 16), mat=H.plastic('#c7b08a', 0.8, key='kastanje_navel'), parent=ob,
           loc=(0, 0, -0.93))
    return _place(ob, loc, rot, parent)


def eikel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = H.plastic('#9a7a3e', 0.35, key='eikel_noot', coat=0.4)
    ob = K.blob(name, (0.75, 0.75, 1.1), 2.0, (48, 24), mat=m, deform=lambda D, P: P + np.stack(
        [np.zeros(len(P)), np.zeros(len(P)), -0.25 * np.clip(-D[:, 2], 0, 1) ** 5], 1))
    SP.eikeldop(name + '_dop', (0, 0, 1.2), (math.pi, 0, 0), ob, R=0.8, D=0.55)
    return _place(ob, loc, rot, parent)


def veertje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=7.0):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        n = g.noise(g.comb(g.math('MULTIPLY', y, 40.0), x, 0.0), 1.0, 2.0)
        col = g.ramp(g.math('DIVIDE', x, L), [(0.0, '#d8d3cc'), (0.6, '#f4f1ec'), (1.0, '#9a8f86')])
        g.bsdf(col, 0.8, sheen=1.0, normal=g.bump(n, 0.4, 0.01))
    m = _mat('veer', b)
    m.use_backface_culling = False

    def fn(U, V):
        x = U * L
        w = np.sin(np.clip(U, 0.08, 1) * math.pi) ** 0.6 * 1.0
        y = (V - 0.5) * 2 * w + 0.4 * U ** 2
        z = 0.4 * np.sin(U * math.pi) - 0.3 * (V - 0.5) ** 2
        return np.stack([x, y, z], 1)
    ob = K.grid_mesh(name, 40, 12, fn, m)
    K.curve_tube(name + '_schacht', [(-0.8, 0, -0.1), (0, 0, 0.0), (L * 0.5, 0.1, 0.41), (L, 0.4, 0.0)], 0.04,
                 H.plastic('#efe9e0', 0.4, key='veerschacht'), ob)
    return _place(ob, loc, rot, parent)


def schelpje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _stripes_mat('schelp', '#f0cdb5', '#e0a98c', 0.5, axis=0, rough=0.4, coat=0.3)

    def fn(U, V):
        a = (U - 0.5) * math.radians(150)
        r = V * 2.2
        x, y = r * np.sin(a), r * np.cos(a) - 0.4
        z = 0.5 * np.sin(V * math.pi * 0.8) + 0.06 * np.abs(np.sin(U * 40)) * V
        return np.stack([x, y, z], 1)
    ob = K.grid_mesh(name, 60, 16, fn, m)
    K.modifier(ob, 'SOLIDIFY', thickness=0.06, offset=0.0)
    return _place(ob, loc, rot, parent)


def kiezel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, s=1.0, seed=0):
    m = _noise_mat('kiezel', '#8d8a84', '#b9b4aa', 5.0, 0.45, 0.1)
    return _place(K.blob(name, (1.2 * s, 0.9 * s, 0.55 * s), 2.4, (48, 24), mat=m,
                         deform=lambda D, P: P * (1 + 0.08 * np.sin(D[:, 0] * 3 + seed) * np.cos(D[:, 1] * 2))[:, None]),
                  loc, rot, parent)


# ---------------------------------------------------------------- 26-35: badkamer, bureau
def wattenstaafje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=7.4):
    ob = H.cyl(name, 0.12, L, H.plastic('#f7f6f2', 0.35, key='wattenstok'), bev=0.03, seg=16)
    w = _noise_mat('watten', '#ffffff', '#f1ede6', 14.0, 0.95, 0.6, sheen=1.0)
    for k, z in enumerate((0.0, L)):
        K.blob(f'{name}_watje{k}', (0.32, 0.32, 0.55), 2.0, (32, 16), mat=w, parent=ob, loc=(0, 0, z),
               deform=lambda D, P: P * (1 + 0.06 * np.sin(D[:, 0] * 20) * np.cos(D[:, 2] * 17))[:, None])
    return _place(ob, loc, rot, parent)


def pleister(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        holes = g.math('LESS_THAN', g.math('ADD', g.math('ABSOLUTE', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', x, 3.0)), 0.5)),
                                                   g.math('ABSOLUTE', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', y, 3.0)), 0.5))), 0.12)
        pad = g.math('LESS_THAN', g.math('ABSOLUTE', x), 1.1)
        col = g.mix(pad, '#e6b48e', '#f3e7dc')
        col = g.mix(g.math('MULTIPLY', holes, g.math('SUBTRACT', 1.0, pad)), col, '#c99470')
        g.bsdf(col, 0.6)
    m = _mat('pleister', b)
    pts = H.rounded_rect_pts(7.2, 1.9, 0.9, 8)
    ob = H.prism(name, pts, 0.05, m, bev=0.015)
    return _place(ob, loc, rot, parent)


def veiligheidsspeld(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=3.8):
    met = H.metal('#cfd2d6', 0.2, key='speld_staal')
    root = K.empty(name, loc, rot, parent=parent)
    coil = [(0.25 * math.cos(a), 0.0, 0.25 * math.sin(a) + 0.25) for a in np.linspace(math.pi, 3 * math.pi + 1.0, 30)]
    K.curve_tube(name + '_veer', coil, 0.035, met, root)
    K.curve_tube(name + '_been1', [(-0.25, 0, 0.25), (-L, 0, 0.05)], 0.035, met, root)
    K.curve_tube(name + '_been2', [(0.12, 0, 0.48), (-L + 0.3, 0, 0.5)], 0.035, met, root)
    H.box(name + '_kap', 0.6, 0.18, 0.62, met, loc=(-L - 0.05, 0, 0.27), bev=0.06, parent=root)
    return root


def schuifspeldje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=5.0):
    m = H.metal('#3a2f2a', 0.35, key='haarspeld')
    pts = [(0, 0.0, 0)] + [(x, 0.08 + 0.04 * math.sin(x * 6), 0) for x in np.linspace(0.2, L, 12)]
    pts2 = [(0, -0.0, 0)] + [(x, -0.12, 0) for x in np.linspace(0.2, L, 4)]
    root = K.empty(name, loc, rot, parent=parent)
    K.curve_tube(name + '_a', pts, 0.04, m, root)
    K.curve_tube(name + '_b', pts2, 0.04, m, root)
    K.curve_tube(name + '_bocht', [(0, 0.04, 0), (-0.12, 0.0, 0), (0, -0.04, 0)], 0.04, m, root)
    return root


def knoopcel(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    ob = H.cyl(name, 1.0, 0.32, H.metal('#c9ccd0', 0.18, key='knoopcel'), bev=0.04, seg=48)
    H.cyl(name + '_min', 0.82, 0.06, H.metal('#b2b5b9', 0.3, key='knoopcel2'), loc=(0, 0, -0.03), bev=0.01, seg=40, parent=ob)
    return _place(ob, loc, rot, parent)


def nietjes(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        gr = g.math('LESS_THAN', g.math('FRACT', g.math('MULTIPLY', x, 22.0)), 0.25)
        g.bsdf('#b9bcc0', 0.3, metal=1.0, normal=g.bump(gr, 0.5, 0.005))
    m = _mat('nietjes', b)
    ob = H.prism(name, [(-2.0, -0.6), (2.0, -0.6), (2.0, 0.6), (-2.0, 0.6)], 0.45, m, bev=0.02)
    return _place(ob, loc, rot, parent)


def jampotje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, vulling=True):
    gl = H.glass('#f4f8f6', 0.02, key='jamglas')
    ob = K.lathe(name, [(0, 0), (1.6, 0), (1.7, 0.2), (1.7, 2.6), (1.5, 2.9), (1.45, 3.2), (1.38, 3.2), (1.42, 2.9), (1.6, 2.6),
                        (1.6, 0.25), (0, 0.15)], 64, gl)
    if vulling:
        rnd = np.random.default_rng(3)
        cols = ['#d8473a', '#e7b23b', '#3e6ea6', '#3f8a55', '#f4f1ea', '#8b5a36', '#7a4ea0']
        for k in range(26):
            a, r = rnd.uniform(0, 2 * math.pi), 1.25 * math.sqrt(rnd.random())
            z = 0.3 + (k // 7) * 0.32 + rnd.uniform(0, 0.15)
            SP.knoop(f'{name}_knoop{k}', (r * math.cos(a), r * math.sin(a), z), cols[k % len(cols)], r=rnd.uniform(0.25, 0.38),
                     rot=(rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(0, 6)), parent=ob)
    return _place(ob, loc, rot, parent)


def plakband(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    karton = H.paper('#c9a77c', rough=0.8, key='plakband_karton', fiber=0.1)
    tape = _mat('tape', lambda g: g.bsdf('#e9dcae', 0.25, transmission=0.0, coat=0.6))
    ob = K.lathe(name, [(1.3, 0), (2.4, 0), (2.42, 0.05), (2.42, 1.85), (2.4, 1.9), (1.3, 1.9), (1.3, 0)], 96, tape,
                 close_top=False, close_bot=False)
    K.lathe(name + '_kern', [(1.12, 0), (1.32, 0), (1.32, 1.9), (1.12, 1.9), (1.12, 0)], 96, karton, ob, close_top=False, close_bot=False)
    return _place(ob, loc, rot, parent)


def bindclip(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    zw = H.metal('#1e1d1f', 0.35, key='bindclip_zwart')
    st = H.metal('#cfd2d6', 0.2, key='speld_staal')
    root = K.empty(name, loc, rot, parent=parent)
    ob = H.prism(name + '_lijf', [(-1.0, 0), (1.0, 0), (0.25, 1.5), (-0.25, 1.5)], 3.2, zw, bev=0.05, parent=root)
    ob.rotation_euler = (math.pi / 2, 0, 0)
    ob.location = (0, 1.6, 0)
    for sx in (-1, 1):
        K.curve_tube(f'{name}_beugel{sx}', [(sx * 0.32, -1.3, 1.45), (sx * 0.6, -1.3, 2.4), (sx * 0.6, 1.3, 2.4), (sx * 0.32, 1.3, 1.45)],
                     0.05, st, root)
    return root


def pennendop(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, col='#2f4f9a'):
    m = H.plastic(col, 0.3, key=f'pendop_{col}', coat=0.3)
    ob = K.lathe(name, [(0, 4.6), (0.38, 4.55), (0.48, 4.3), (0.5, 0.2), (0.45, 0.0), (0.38, 0.0), (0.4, 4.2), (0, 4.4)][::-1], 32, m)
    H.box(name + '_clip', 0.25, 0.12, 3.2, m, loc=(0, 0.6, 1.4), bev=0.05, base=True, parent=ob)
    return _place(ob, loc, rot, parent)


# ---------------------------------------------------------------- 36-50: spelletjes, feest, naaidoos
def dominosteen(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, a=3, b=5):
    ob = H.box(name, 4.4, 2.2, 0.8, H.plastic('#f3ede0', 0.3, key='domino', coat=0.3), bev=0.15, base=True)
    zw = H.plastic('#1a1715', 0.4, key='domino_oog')
    H.box(name + '_streep', 0.06, 1.7, 0.02, zw, loc=(0, 0, 0.8), bev=0.0, parent=ob)
    P = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
         5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
    for side, num in ((-1, a), (1, b)):
        for k, (u, v) in enumerate(P[num]):
            H.cyl(f'{name}_oog{side}{k}', 0.16, 0.02, zw, loc=(side * 1.1 + u * 0.55, v * 0.55, 0.8), bev=0.0, seg=16, parent=ob)
    return _place(ob, loc, rot, parent)


def pion(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, col='#d8473a'):
    m = H.wood('beuk', 'Z', paint=col, grain=0.2, coat=0.4, key=f'pion_{col}')
    prof = [(0, 0), (0.95, 0), (1.0, 0.15), (0.9, 0.35), (0.55, 0.6), (0.42, 1.7), (0.6, 1.85), (0.6, 1.95), (0.32, 2.05), (0, 2.08)]
    ob = K.lathe(name, prof, 48, m)
    H.ball(name + '_kop', 0.55, m, loc=(0, 0, 2.5), parent=ob)
    return _place(ob, loc, rot, parent)


def damsteen(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, dark=False):
    m = H.wood('noten' if dark else 'esdoorn', 'Z', key=f'damsteen_{dark}', coat=0.3)
    ob = H.cyl(name, 1.5, 0.55, m, bev=0.08, seg=64)
    for k in range(3):
        K.curve_tube(f'{name}_groef{k}', [((0.6 + 0.3 * k) * math.cos(a), (0.6 + 0.3 * k) * math.sin(a), 0.555)
                                          for a in np.linspace(0, 2 * math.pi, 49)[:-1]], 0.02,
                     H.wood('noten', 'Z', key='damgroef'), ob, cyclic=True)
    return _place(ob, loc, rot, parent)


def speelkaart(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = H.paper('#fbfaf7', os.path.join(H.TEX, 'speelkaart.png'), rough=0.5, key='speelkaart', src='GEN', fiber=0.02)
    ob = H.prism(name, H.rounded_rect_pts(5.7, 8.8, 0.4, 6), 0.03, m, bev=0.0)
    return _place(ob, loc, rot, parent)


def tol(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    m = _stripes_mat('tol', '#d8473a', '#f2c94c', 0.35, axis=2, rough=0.35, coat=0.4)
    prof = [(0, 0), (0.2, 0.15), (1.2, 1.0), (1.55, 1.5), (1.5, 1.8), (1.1, 2.0), (0.25, 2.05), (0.2, 3.1), (0.12, 3.2), (0, 3.2)]
    return _place(K.lathe(name, prof, 48, m), loc, rot, parent)


def jojo(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, col='#3561a8'):
    m = H.wood('beuk', 'Z', paint=col, grain=0.2, coat=0.4, key=f'jojo_{col}')
    root = K.empty(name, loc, rot, parent=parent)
    for sz in (-1, 1):
        sch = K.lathe(f'{name}_schijf{sz}', [(0, 0), (1.6, 0), (1.7, 0.2), (1.6, 0.6), (0.6, 0.65), (0, 0.66)], 48, m, root)
        sch.location = (0, 0, 0.12 if sz > 0 else -0.12)
        sch.rotation_euler = (0 if sz > 0 else math.pi, 0, 0)
    K.curve_tube(name + '_touw', [(0, -0.25, 0), (0.6, -1.2, 0.3), (1.8, -1.8, 0.0), (3.4, -1.4, -0.6)], 0.035,
                 H.thread('#f4f1ea', key='draadje_wit'), root)
    return root


def verjaardagskaarsje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, lit=True, col='#4a8fd8'):
    m = _stripes_mat(f'kaars_{col}', '#f6f2ea', col, 0.45, axis=2, rough=0.4, coat=0.2, twist=0.2)
    ob = H.cyl(name, 0.22, 5.5, m, bev=0.05, seg=24)
    K.curve_tube(name + '_lont', [(0, 0, 5.45), (0.02, 0, 5.75)], 0.025, H.plastic('#2a2420', 0.7, key='lont'), ob)
    if lit:
        K.blob(name + '_vlam', (0.11, 0.11, 0.3), 2.0, (24, 12), mat=H.emit('#ffb54a', 18.0, key='vlam'), parent=ob, loc=(0.02, 0, 6.0),
               deform=lambda D, P: P * np.where(D[:, 2] > 0, 1 - 0.6 * D[:, 2], 1)[:, None])
        L = K.light('POINT', (0.02, 0, 6.05), energy=14, color=(1.0, 0.62, 0.25), size=0.1, name=name + '_licht')
        L.parent = ob
    return _place(ob, loc, rot, parent)


def sleutelring(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, R=1.3):
    pts = [(R * math.cos(t), R * math.sin(t), 0.09 * t / (2 * math.pi)) for t in np.linspace(0, 4 * math.pi, 120)]
    ob = K.curve_tube(name, pts, 0.07, H.metal('#cfd2d6', 0.2, key='speld_staal'))
    return _place(ob, loc, rot, parent)


def ijslepeltje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=9.5):
    pts = []
    for a in np.linspace(-90, 90, 14):
        pts.append((L - 1.3 + 1.3 * math.cos(math.radians(a)), 1.25 * math.sin(math.radians(a))))
    for a in np.linspace(90, 270, 10):
        pts.append((0.5 + 0.5 * math.cos(math.radians(a)), 0.5 * math.sin(math.radians(a))))
    ob = SP._curve2d(name, [pts], 0.08, 0.05, H.wood('berk', 'X', key='ijslepel'))
    return _place(ob, loc, rot, parent)


def cocktailprikker(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, col='#d8473a', L=6.5):
    root = K.empty(name, loc, rot, parent=parent)
    K.lathe(name + '_stok', [(0, 0), (0.06, 0.4), (0.07, L - 0.4), (0, L)], 12, H.wood('berk', 'Z', key='tandenstoker'), root)
    vl = _mat(f'vlag_{col}', lambda g: g.bsdf(col, 0.7, sheen=0.3))
    vl.use_backface_culling = False

    def fn(U, V):
        return np.stack([U * 2.4, np.zeros_like(U) + 0.12 * np.sin(U * 5), V * 1.5], 1)
    f = K.grid_mesh(name + '_vlag', 16, 4, fn, vl, root)
    f.location = (0.05, 0, L - 1.8)
    return root


def rietje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, L=14.0):
    m = _stripes_mat('rietje', '#f7f4ee', '#d23b30', 1.4, axis=2, rough=0.3, coat=0.4, twist=0.25)
    m.use_backface_culling = False
    pts = [(0, 0, 0), (0, 0, L * 0.7), (0, 0, L * 0.8), (0.4, 0, L * 0.88), (1.6, 0, L * 0.95), (3.0, 0, L * 0.97)]
    ob, _ = K.tube(name, pts, [0.3] * len(pts), mat=m, caps=(False, False), ring=24)
    K.modifier(ob, 'SOLIDIFY', thickness=0.03, offset=-1.0)
    return _place(ob, loc, rot, parent)


def onderzetter(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, R=5.3):
    def b(g):
        tc = g.node('ShaderNodeTexCoord')
        x, y, z = g.sep(tc.outputs['Object'])
        r = g.vmath('LENGTH', g.comb(x, y, 0.0))
        ring = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', r, R * 0.82)), 0.25)
        ring2 = g.math('LESS_THAN', g.math('ABSOLUTE', g.math('SUBTRACT', r, R * 0.62)), 0.12)
        col = g.mix(g.math('MAXIMUM', ring, ring2), '#efe6d0', '#b5432f')
        n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (8, 8, 8)), 1.0, 6.0)
        g.bsdf(g.mul(col, g.math('ADD', 0.94, g.math('MULTIPLY', n, 0.1))), 0.9, normal=g.bump(n, 0.15, 0.01))
    m = _mat('onderzetter', b)
    return _place(H.cyl(name, R, 0.15, m, bev=0.04, seg=96), loc, rot, parent)


def meetlintje(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    tape = H.paper('#f2c230', os.path.join(H.TEX, 'meetlint.png'), rough=0.4, key='meetlint', src='GEN', fiber=0.02)
    root = K.empty(name, loc, rot, parent=parent)
    pts = [((0.3 + 0.045 * t) * math.cos(t), (0.3 + 0.045 * t) * math.sin(t), 0) for t in np.linspace(0, 12 * math.pi, 300)]
    V = [(x, y, 0) for x, y, _ in pts] + [(x, y, 1.6) for x, y, _ in pts]
    n = len(pts)
    ob = K.mesh_obj(name + '_rol', V, [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)], tape, root)
    K.modifier(ob, 'SOLIDIFY', thickness=0.02, offset=0.0)
    end = pts[-1]
    H.box(name + '_eind', 4.0, 0.02, 1.6, tape, loc=(end[0] + 2.0, end[1], 0.8), rot=(0, 0, 0.1), bev=0.0, parent=root)
    return root


def borduurring(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, R=6.0):
    m = H.wood('beuk', 'X', key='borduurring', coat=0.2)
    root = K.empty(name, loc, rot, parent=parent)
    for k, (r, w) in enumerate(((R, 0.7), (R + 0.25, 0.55))):
        K.lathe(f'{name}_ring{k}', [(r - 0.12, 0), (r + 0.12, 0), (r + 0.12, w), (r - 0.12, w), (r - 0.12, 0)], 128, m, root,
                close_top=False, close_bot=False)
    H.cyl(name + '_schroef', 0.22, 1.2, H.metal('#c9c2ae', 0.3, key='muselet'), loc=(0, R + 0.45, -0.2), bev=0.04, seg=16, parent=root)
    return root


def pompon(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, R=1.6, col='#e47a9a'):
    m = _noise_mat(f'pompon_{col}', col, col, 30.0, 0.95, 0.9, sheen=1.0)
    return _place(K.blob(name, (R, R, R), 2.0, (96, 48), mat=m,
                         deform=lambda D, P: P * (1 + 0.07 * np.sin(D[:, 0] * 41) * np.sin(D[:, 1] * 37) * np.sin(D[:, 2] * 43))[:, None]),
                  loc, rot, parent)


def ballon(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, col='#d8473a', R=1.6, draad=6.0):
    """Feestballonnetje met een touwtje (oorsprong = onderkant van het touwtje)."""
    m = _mat(f'ballon_{col}', lambda g: g.bsdf(col, 0.18, coat=0.8, sheen=0.1))
    root = K.empty(name, loc, rot, parent=parent)
    b = K.blob(name + '_bol', (R, R, R * 1.18), 2.0, (64, 32), mat=m, parent=root, loc=(0, 0, draad + R * 1.18),
               deform=lambda D, P: P * np.where(D[:, 2] < 0, 1 - 0.25 * D[:, 2] ** 2, 1)[:, None])
    K.lathe(name + '_knoopje', [(0, -0.25), (0.12, -0.22), (0.18, -0.05), (0.08, 0.05), (0, 0.06)], 16, m, root).location = (0, 0, draad)
    K.curve_tube(name + '_touw', [(0, 0, 0), (0.15, 0.1, draad * 0.4), (-0.1, 0.0, draad * 0.75), (0, 0, draad - 0.2)], 0.015,
                 H.thread('#f4f1ea', key='draadje_wit'), root)
    return root


ALLE = ['wijnkurk', 'champagnekurk', 'suikerklontje', 'suikerzakje', 'koffiemelkcupje', 'eierdopje', 'eierschaal', 'macaroni',
        'farfalle', 'spaghetti_bundel', 'koffieboon', 'kruidnagel', 'steranijs', 'kaneelstokje', 'laurierblad', 'rozijn', 'pinda',
        'hazelnoot', 'dennenappel', 'kastanje', 'eikel', 'veertje', 'schelpje', 'kiezel', 'wattenstaafje', 'pleister',
        'veiligheidsspeld', 'schuifspeldje', 'knoopcel', 'nietjes', 'jampotje', 'plakband', 'bindclip', 'pennendop', 'dominosteen',
        'pion', 'damsteen', 'speelkaart', 'tol', 'jojo', 'verjaardagskaarsje', 'sleutelring', 'ijslepeltje', 'cocktailprikker',
        'rietje', 'onderzetter', 'meetlintje', 'borduurring', 'pompon', 'ballon']
