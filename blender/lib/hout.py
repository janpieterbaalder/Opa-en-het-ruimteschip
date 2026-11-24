"""Materialen (hout, verf, metaal, draad, kurk, papier, glas) en basisvormen met afgeronde randen.

Eenheden: 1 Blender-eenheid = 1 cm in het echt. De poppetjes zijn ~5 cm, alles is op ware grootte,
dus ook de houtnerf: jaarringen liggen een paar millimeter uit elkaar.

Hout is volledig procedureel: een boomstam (cilinder met de kern ergens naast het stuk hout)
met ringen die door ruis golven, zodat planken vlammen/kathedraaltekening krijgen en kopse kanten
ringen. Elk object krijgt via Object Info > Random een eigen stuk van de stam.
"""
import bpy, math, os
import numpy as np
from . import core as K

TEX = os.path.join(K.ROOT, 'tex')

# vroeghout, laathout, ringen per cm, breedte laathout, nerfstrepen, poriën, ruwheid
SOORT = {
    'beuk':     dict(e='#dcb48c', l='#c99c72', f=4.2, lw=0.30, st=0.08, po=0.25, ro=0.55),
    'esdoorn':  dict(e='#f1ddbb', l='#e8d0a9', f=4.8, lw=0.25, st=0.05, po=0.04, ro=0.50),
    'berk':     dict(e='#eedab3', l='#e0c59c', f=3.6, lw=0.26, st=0.07, po=0.06, ro=0.60),
    'grenen':   dict(e='#edcd96', l='#cf8d52', f=2.2, lw=0.40, st=0.08, po=0.03, ro=0.60),
    'eiken':    dict(e='#d2a66d', l='#a57744', f=3.0, lw=0.40, st=0.14, po=0.80, ro=0.60),
    'noten':    dict(e='#80593b', l='#563827', f=3.6, lw=0.40, st=0.12, po=0.45, ro=0.50),
    'kersen':   dict(e='#d09264', l='#b2714a', f=4.0, lw=0.30, st=0.08, po=0.12, ro=0.50),
    'populier': dict(e='#efe2c6', l='#e3d2ae', f=3.0, lw=0.20, st=0.05, po=0.04, ro=0.70),
    'ceder':    dict(e='#d99d6c', l='#bb7449', f=4.0, lw=0.35, st=0.08, po=0.05, ro=0.60),
}

_M = {}


# ---------------------------------------------------------------- knopen bouwen
class G:
    def __init__(self, mat):
        mat.use_nodes = True
        self.nt = mat.node_tree
        self.N = self.nt.nodes
        self.L = self.nt.links
        self.N.clear()

    def node(self, t, **props):
        n = self.N.new(t)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def set(self, n, key, v):
        s = n.inputs[key]
        if isinstance(v, bpy.types.NodeSocket):
            self.L.new(v, s)
        elif isinstance(v, str):
            s.default_value = K.srgb(v)
        elif s.type == 'RGBA' and np.isscalar(v):
            s.default_value = (v, v, v, 1.0)
        elif s.type == 'RGBA' and len(v) == 3:
            s.default_value = (v[0], v[1], v[2], 1.0)
        else:
            s.default_value = v

    def link(self, a, b):
        self.L.new(a, b)

    def math(self, op, a, b=0.0, c=None, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.set(n, 0, a)
        self.set(n, 1, b)
        if c is not None:
            self.set(n, 2, c)
        return n.outputs[0]

    def vmath(self, op, a, b=None):
        n = self.node('ShaderNodeVectorMath', operation=op)
        self.set(n, 0, a)
        if b is not None:
            self.set(n, 1, b)
        return n.outputs['Vector'] if op not in ('LENGTH', 'DOT_PRODUCT', 'DISTANCE') else n.outputs['Value']

    def comb(self, x, y, z):
        n = self.node('ShaderNodeCombineXYZ')
        for i, v in enumerate((x, y, z)):
            self.set(n, i, v)
        return n.outputs[0]

    def sep(self, v):
        n = self.node('ShaderNodeSeparateXYZ')
        self.set(n, 0, v)
        return n.outputs[0], n.outputs[1], n.outputs[2]

    def mix(self, fac, a, b, blend='MIX'):
        n = self.node('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        self.set(n, 0, fac)
        self.set(n, 6, a)
        self.set(n, 7, b)
        return n.outputs[2]

    def mixf(self, fac, a, b):
        n = self.node('ShaderNodeMix', data_type='FLOAT')
        self.set(n, 0, fac)
        self.set(n, 2, a)
        self.set(n, 3, b)
        return n.outputs[0]

    def mul(self, col, s):
        return self.mix(1.0, col, s, 'MULTIPLY')

    def noise(self, vec, scale=1.0, detail=2.0, rough=0.5, dist=0.0, out='Fac'):
        n = self.node('ShaderNodeTexNoise')
        self.set(n, 'Vector', vec)
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        n.inputs['Distortion'].default_value = dist
        return n.outputs[out]

    def ramp(self, fac, stops, interp='LINEAR'):
        n = self.node('ShaderNodeValToRGB')
        cr = n.color_ramp
        cr.interpolation = interp
        els = cr.elements
        while len(els) < len(stops):
            els.new(0.5)
        for e, (pos, val) in zip(els, stops):
            e.position = pos
            e.color = K.srgb(val) if isinstance(val, str) else ((val, val, val, 1.0) if np.isscalar(val) else val)
        self.set(n, 'Fac', fac)
        return n.outputs['Color']

    def sstep(self, a, b, x):
        """smoothstep van a naar b (float)."""
        n = self.node('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP')
        self.set(n, 'Value', x)
        n.inputs['From Min'].default_value = a
        n.inputs['From Max'].default_value = b
        return n.outputs['Result']

    def bsdf(self, col, rough, metal=0.0, coat=0.0, coat_rough=0.12, normal=None, spec=0.5, sheen=0.0,
             alpha=None, ior=None, transmission=0.0, emission=None, emit_str=0.0):
        b = self.node('ShaderNodeBsdfPrincipled')
        self.set(b, 'Base Color', col)
        self.set(b, 'Roughness', rough)
        self.set(b, 'Metallic', metal)
        self.set(b, 'Coat Weight', coat)
        self.set(b, 'Coat Roughness', coat_rough)
        self.set(b, 'Specular IOR Level', spec)
        if sheen:
            self.set(b, 'Sheen Weight', sheen)
        if alpha is not None:
            self.set(b, 'Alpha', alpha)
        if ior is not None:
            self.set(b, 'IOR', ior)
        if transmission:
            self.set(b, 'Transmission Weight', transmission)
        if emission is not None:
            self.set(b, 'Emission Color', emission)
            self.set(b, 'Emission Strength', emit_str)
        if normal is not None:
            self.link(normal, b.inputs['Normal'])
            self.link(normal, b.inputs['Coat Normal'])
        o = self.node('ShaderNodeOutputMaterial')
        self.link(b.outputs[0], o.inputs['Surface'])
        return b

    def bump(self, h, strength=0.2, dist=0.004):
        n = self.node('ShaderNodeBump')
        self.set(n, 'Height', h)
        n.inputs['Strength'].default_value = strength
        n.inputs['Distance'].default_value = dist
        return n.outputs['Normal']


def _new(key):
    m = bpy.data.materials.new(key)
    _M[key] = m
    return m


# ---------------------------------------------------------------- hout
def _coords(g, axis, scale=1.0, src='Object', size=None):
    tc = g.node('ShaderNodeTexCoord')
    v = tc.outputs[src]
    if src == 'Generated' and size is not None:
        v = g.vmath('MULTIPLY', v, tuple(size))
    mp = g.node('ShaderNodeMapping', vector_type='POINT')
    rot = {'X': (0, 0, 0), 'Y': (0, 0, -math.pi / 2), 'Z': (0, math.pi / 2, 0)}[axis]
    mp.inputs['Rotation'].default_value = rot
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    g.link(v, mp.inputs['Vector'])
    oi = g.node('ShaderNodeObjectInfo')
    r = oi.outputs['Random']
    ox = g.math('MULTIPLY', g.math('FRACT', g.math('MULTIPLY', r, 17.31)), 40.0)
    oy = g.math('MULTIPLY', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', r, 71.73)), 0.5), 5.0)
    oz = g.math('MULTIPLY', g.math('SUBTRACT', g.math('FRACT', g.math('MULTIPLY', r, 313.1)), 0.5), 5.0)
    p = g.vmath('ADD', mp.outputs[0], g.comb(ox, oy, oz))
    return p, r, tc


def wood(soort='beuk', axis='X', paint=None, paint2=None, stripes=None, grain=None, rough=None, coat=0.0,
         img=None, img_rough=0.32, scale=1.0, tint=None, var=0.10, ply=None, src='Object', size=None,
         bump=1.0, key=None, pith=(7.0, -10.0), satin=None, img_proj='UV', paint_until=None):
    """Hout. paint: verfkleur (nerf blijft zichtbaar volgens `grain`). stripes=(periode, aandeel) langs object-z
    met paint2. img: afbeelding (pad) via UV, de alfa bepaalt waar verf zit. ply: laagdikte multiplex (cm)
    voor de randen (dikte langs object-z)."""
    key = key or f'hout_{soort}_{axis}_{paint}_{paint2}_{stripes}_{grain}_{rough}_{coat}_{img}_{scale}_{tint}_{ply}_{src}_{size}_{bump}'
    if key in _M:
        return _M[key]
    S = dict(SOORT[soort])
    if tint:
        S['e'], S['l'] = tint
    m = _new(key)
    g = G(m)
    p, rnd, tc = _coords(g, axis, scale, src, size)
    x, y, z = g.sep(p)
    # stam: kern naast het stuk, ringen golven met ruis
    yy = g.math('ADD', y, pith[0])
    zz = g.math('ADD', z, pith[1])
    r = g.vmath('LENGTH', g.comb(0.0, yy, zz))
    n_small = g.noise(g.vmath('MULTIPLY', p, (0.6, 3.2, 3.2)), 1.0, 4.0, 0.55)
    n_large = g.noise(g.vmath('MULTIPLY', p, (0.05, 0.22, 0.22)), 1.0, 2.0, 0.5)
    r = g.math('ADD', r, g.math('MULTIPLY', g.math('SUBTRACT', n_small, 0.5), 0.10))
    r = g.math('ADD', r, g.math('MULTIPLY', g.math('SUBTRACT', n_large, 0.5), 1.6))
    ring = g.math('FRACT', g.math('MULTIPLY', r, S['f']))
    lw = S['lw']
    late = g.ramp(ring, [(0.0, 0.0), (max(0.05, 0.92 - lw - 0.25), 0.04), (0.92 - lw * 0.35, 1.0),
                         (0.975, 0.85), (1.0, 0.0)])
    streak = g.noise(g.vmath('MULTIPLY', p, (0.8, 34.0, 34.0)), 1.0, 2.0, 0.6)
    pores = g.ramp(g.noise(g.vmath('MULTIPLY', p, (3.0, 65.0, 65.0)), 1.0, 0.0, 0.5),
                   [(0.0, 0.0), (0.6, 0.0), (0.72, 1.0)])
    objv = g.math('ADD', 1.0 - var, g.math('MULTIPLY', g.math('FRACT', g.math('MULTIPLY', rnd, 977.3)), 2 * var))
    smul = g.math('ADD', 1.0 - S['st'], g.math('MULTIPLY', streak, 2 * S['st']))

    if paint is None:
        col = g.mix(late, S['e'], S['l'])
        col = g.mul(col, smul)
        col = g.mix(g.math('MULTIPLY', pores, S['po'] * 0.55), col, g.mul(col, 0.45))
        col = g.mul(col, objv)
        ro = g.math('ADD', rough if rough is not None else S['ro'], g.math('MULTIPLY', late, 0.08))
        h = g.math('ADD', g.math('MULTIPLY', late, 0.7), g.math('MULTIPLY', pores, -1.2 * S['po']))
        h = g.math('ADD', h, g.math('MULTIPLY', streak, 0.35))
        bstr = 0.12 * bump
    else:
        gk = 0.28 if grain is None else grain
        pc = paint
        if stripes is not None:
            per, duty = stripes
            zo = g.sep(tc.outputs['Object'])[2]
            st = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', zo, per)), duty)
            pc = g.mix(st, paint, paint2)
        col = g.mul(pc, g.math('SUBTRACT', 1.0, g.math('MULTIPLY', late, gk)))
        col = g.mul(col, g.math('ADD', 1.0 - 0.04, g.math('MULTIPLY', streak, 0.08)))
        col = g.mul(col, g.math('ADD', 1.0 - var * 0.3, g.math('MULTIPLY', g.math('FRACT', g.math('MULTIPLY', rnd, 977.3)), var * 0.6)))
        ro = rough if rough is not None else 0.42
        h = g.math('ADD', g.math('MULTIPLY', late, 0.5 * gk / 0.28), g.math('MULTIPLY', streak, 0.15))
        bstr = 0.08 * bump
        if paint_until is not None:
            ncol = g.mul(g.mul(g.mix(late, S['e'], S['l']), smul), objv)
            mk = g.math('LESS_THAN', g.sep(tc.outputs['Object'])[0], paint_until)
            col = g.mix(mk, ncol, col)
            ro = g.mixf(mk, S['ro'], ro)

    if ply is not None:
        nz = g.sep(tc.outputs['Normal'])[2]
        edge = g.sstep(0.75, 0.35, g.math('ABSOLUTE', nz))
        zo = g.sep(tc.outputs['Object'])[2]
        layer = g.math('LESS_THAN', g.math('FRACT', g.math('DIVIDE', zo, ply)), 0.5)
        lc = g.mix(layer, '#e4c79c', '#c9a57a')
        lc = g.mix(g.math('MULTIPLY', g.math('LESS_THAN', g.math('FRACT', g.math('ADD', g.math('DIVIDE', zo, ply), 0.03)), 0.06), 1.0), lc, '#8a6a45')
        col = g.mix(edge, col, lc)

    if img is not None:
        it = g.node('ShaderNodeTexImage')
        it.image = bpy.data.images.load(img, check_existing=True)
        it.interpolation = 'Cubic'
        if img_proj == 'SPHERE':
            # bolprojectie rond de oorsprong van het object; voorkant (-y) valt op u = 0.5
            it.projection = 'SPHERE'
            mp = g.node('ShaderNodeMapping', vector_type='POINT')
            mp.inputs['Rotation'].default_value = (0, 0, math.pi)
            mp.inputs['Scale'].default_value = (0.1, 0.1, 0.1)
            mp.inputs['Location'].default_value = (0.5, 0.5, 0.5)
            g.link(tc.outputs['Object'], mp.inputs['Vector'])
            g.link(mp.outputs[0], it.inputs['Vector'])
        elif img_proj == 'GEN':
            g.link(tc.outputs['Generated'], it.inputs['Vector'])
        else:
            uv = g.node('ShaderNodeUVMap')
            g.link(uv.outputs[0], it.inputs['Vector'])
        a = it.outputs['Alpha']
        col = g.mix(a, col, it.outputs['Color'])
        ro = g.mixf(a, ro, img_rough)
        h = g.math('ADD', h, g.math('MULTIPLY', a, 0.6))

    nrm = g.bump(h, bstr, 0.003)
    g.bsdf(col, ro, coat=coat, normal=nrm, spec=0.45 if satin is None else satin)
    return m


# ---------------------------------------------------------------- overige materialen
def metal(col='#c9c9c9', rough=0.25, key=None, aniso=False):
    key = key or f'metaal_{col}_{rough}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    tc = g.node('ShaderNodeTexCoord')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (60, 60, 60)), 1.0, 2.0)
    ro = g.math('ADD', rough, g.math('MULTIPLY', g.math('SUBTRACT', n, 0.5), 0.12))
    g.bsdf(col, ro, metal=1.0, normal=g.bump(n, 0.03, 0.002))
    return m


def plastic(col, rough=0.3, key=None, coat=0.0):
    key = key or f'plastic_{col}_{rough}_{coat}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    g.bsdf(col, rough, coat=coat)
    return m


def glass(col='#ffffff', rough=0.02, key=None):
    key = key or f'glas_{col}_{rough}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    g.bsdf(col, rough, transmission=1.0, ior=1.45)
    return m


def emit(col='#ffd9a0', strength=10.0, key=None):
    key = key or f'licht_{col}_{strength}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    e = g.node('ShaderNodeEmission')
    g.set(e, 'Color', col)
    e.inputs['Strength'].default_value = strength
    o = g.node('ShaderNodeOutputMaterial')
    g.link(e.outputs[0], o.inputs['Surface'])
    return m


def bulb(col='#ffcf8a', strength=30.0, key=None):
    """Kerstlampje: glas met een gloeiende kern (emissie + doorschijnend)."""
    key = key or f'lampje_{col}_{strength}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    g.bsdf(col, 0.15, transmission=0.0, emission=col, emit_str=strength)
    return m


def paper(col='#e8dcc2', img=None, rough=0.85, key=None, src='UV', fiber=0.06):
    key = key or f'papier_{col}_{img}_{src}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    tc = g.node('ShaderNodeTexCoord')
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (9, 9, 9)), 1.0, 6.0, 0.6)
    col_s = g.mul(col, g.math('ADD', 1.0 - fiber, g.math('MULTIPLY', n, 2 * fiber)))
    if img is not None:
        it = g.node('ShaderNodeTexImage')
        it.image = bpy.data.images.load(img, check_existing=True)
        it.interpolation = 'Cubic'
        if src == 'UV':
            uv = g.node('ShaderNodeUVMap')
            g.link(uv.outputs[0], it.inputs['Vector'])
        elif src == 'GENXZ':
            gx, gy, gz = g.sep(tc.outputs['Generated'])
            g.link(g.comb(gx, gz, 0.0), it.inputs['Vector'])
        else:
            g.link(tc.outputs['Generated'], it.inputs['Vector'])
        col_s = g.mix(it.outputs['Alpha'], col_s, g.mix(1.0, it.outputs['Color'], col_s, 'MULTIPLY'))
    g.bsdf(col_s, rough, normal=g.bump(n, 0.05, 0.003), sheen=0.2)
    return m


def thread(col, key=None, period=0.022):
    """Garen op een klosje: fijne windingen rond object-z."""
    key = key or f'garen_{col}'
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    tc = g.node('ShaderNodeTexCoord')
    x, y, z = g.sep(tc.outputs['Object'])
    a = g.math('ARCTAN2', y, x)
    w = g.math('SINE', g.math('MULTIPLY', g.math('ADD', z, g.math('MULTIPLY', a, 0.004)), 2 * math.pi / period))
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (3, 3, 40)), 1.0, 2.0)
    shade = g.math('ADD', 0.82, g.math('MULTIPLY', g.math('ADD', w, 1.0), 0.09))
    shade = g.math('MULTIPLY', shade, g.math('ADD', 0.92, g.math('MULTIPLY', n, 0.16)))
    g.bsdf(g.mul(col, shade), 0.6, sheen=0.6, normal=g.bump(w, 0.25, 0.004))
    return m


def cork(key='kurk'):
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    tc = g.node('ShaderNodeTexCoord')
    v = g.node('ShaderNodeTexVoronoi')
    g.link(tc.outputs['Object'], v.inputs['Vector'])
    v.inputs['Scale'].default_value = 18.0
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (14, 14, 14)), 1.0, 5.0, 0.6)
    f = g.math('MULTIPLY', v.outputs['Distance'], n)
    col = g.ramp(f, [(0.0, '#5b3a20'), (0.12, '#8c6038'), (0.35, '#b98b5a'), (0.7, '#d1a774')])
    g.bsdf(col, 0.85, normal=g.bump(f, 0.5, 0.01))
    return m


def oak_cap(key='eikeldop'):
    """Eikeldopje: schubbetjes."""
    if key in _M:
        return _M[key]
    m = _new(key)
    g = G(m)
    tc = g.node('ShaderNodeTexCoord')
    v = g.node('ShaderNodeTexVoronoi')
    v.feature = 'F1'
    g.link(tc.outputs['Object'], v.inputs['Vector'])
    v.inputs['Scale'].default_value = 9.0
    d = v.outputs['Distance']
    n = g.noise(g.vmath('MULTIPLY', tc.outputs['Object'], (20, 20, 20)), 1.0, 4.0)
    col = g.ramp(g.math('ADD', d, g.math('MULTIPLY', n, 0.3)),
                 [(0.0, '#c9a46c'), (0.35, '#a07848'), (0.7, '#6d4b2b'), (1.0, '#4a311c')])
    g.bsdf(col, 0.7, normal=g.bump(g.math('SUBTRACT', 1.0, d), 0.6, 0.02))
    return m


# ---------------------------------------------------------------- vormen
def _harden(ob, width, seg=3, angle=35):
    width = float(width)
    if width <= 0:
        return ob
    ob.data.polygons.foreach_set('use_smooth', np.ones(len(ob.data.polygons), dtype=bool))
    m = ob.modifiers.new('bevel', 'BEVEL')
    m.width = width
    m.segments = seg
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    try:
        m.harden_normals = True
    except Exception:
        pass
    return ob


def box(name, sx, sy, sz, mat, loc=(0, 0, 0), rot=(0, 0, 0), bev=0.04, seg=3, parent=None, base=False):
    """Blok met afgeronde randen; sx, sy, sz zijn de volle maten. base=True: oorsprong op de onderkant."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    z0, z1 = (0, sz) if base else (-hz, hz)
    V = [(-hx, -hy, z0), (hx, -hy, z0), (hx, hy, z0), (-hx, hy, z0),
         (-hx, -hy, z1), (hx, -hy, z1), (hx, hy, z1), (-hx, hy, z1)]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = K.mesh_obj(name, V, F, mat, parent, smooth=False, loc=loc, rot=rot)
    _harden(ob, min(bev, 0.45 * min(sx, sy, sz)), seg)
    return ob


def prism(name, pts2d, h, mat, loc=(0, 0, 0), rot=(0, 0, 0), bev=0.03, seg=2, parent=None, angle=35):
    """Prisma: 2D-omtrek (tegen de klok in) in xy, hoogte h langs z vanaf 0."""
    n = len(pts2d)
    V = [(x, y, 0) for x, y in pts2d] + [(x, y, h) for x, y in pts2d]
    F = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        F.append((i, j, n + j, n + i))
    ob = K.mesh_obj(name, V, F, mat, parent, smooth=False, loc=loc, rot=rot)
    _harden(ob, bev, seg, angle)
    return ob


def rounded_rect_pts(w, d, r, n=8):
    """Omtrek van een afgeronde rechthoek (midden op 0), tegen de klok in."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -d / 2 + r, -90), (w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90),
                       (-w / 2 + r, -d / 2 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def stadium_pts(L, W, n=14):
    """Omtrek van een ijsstokje (rechthoek met halve cirkels), lengte langs x."""
    r = W / 2
    pts = []
    for k in range(n + 1):
        a = math.radians(-90 + 180 * k / n)
        pts.append((L / 2 - r + r * math.cos(a), r * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(90 + 180 * k / n)
        pts.append((-L / 2 + r + r * math.cos(a), r * math.sin(a)))
    return pts


def cyl(name, r, h, mat, loc=(0, 0, 0), rot=(0, 0, 0), bev=0.03, seg=48, parent=None, r_top=None):
    """Cilinder (as langs z, van 0 tot h) met afgeronde randen."""
    rt = r if r_top is None else r_top
    b = min(bev, 0.45 * min(r, rt, h / 2))
    prof = [(0, 0)]
    for k in range(5):
        a = math.radians(-90 + 90 * k / 4)
        prof.append((r - b + b * math.cos(a), b + b * math.sin(a)))
    for k in range(5):
        a = math.radians(90 * k / 4)
        prof.append((rt - b + b * math.cos(a), h - b + b * math.sin(a)))
    prof.append((0, h))
    ob = K.lathe(name, prof, seg, mat, parent)
    ob.location, ob.rotation_euler = loc, rot
    return ob


def ball(name, r, mat, loc=(0, 0, 0), parent=None, res=(48, 24), scale=(1, 1, 1)):
    return K.blob(name, (r * scale[0], r * scale[1], r * scale[2]), 2.0, res, mat=mat, parent=parent, loc=loc)


def capsule(name, p0, p1, r, mat, parent=None, r1=None, ring=32):
    ob, _ = K.tube(name, [p0, p1], [r, r if r1 is None else r1], mat=mat, parent=parent, ring=ring, per=4)
    return ob


def instance(src, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, parent=None):
    """Gekoppelde kopie (zelfde mesh, eigen plaats en eigen houttekening)."""
    ob = bpy.data.objects.new(name, src.data)
    ob.location, ob.rotation_euler = loc, rot
    ob.scale = (scale,) * 3 if np.isscalar(scale) else scale
    for md in src.modifiers:
        m = ob.modifiers.new(md.name, md.type)
        for attr in ('width', 'segments', 'limit_method', 'angle_limit', 'harden_normals', 'thickness', 'offset',
                     'use_even_offset', 'levels', 'render_levels'):
            if hasattr(md, attr):
                try:
                    setattr(m, attr, getattr(md, attr))
                except Exception:
                    pass
    return K.link(ob, parent)


def to_mesh(ob):
    """Curve-object omzetten naar een mesh-object (zelfde naam, plaats)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    new = bpy.data.objects.new(ob.name + '_m', me)
    new.matrix_world = ob.matrix_world.copy()
    K.link(new)
    new.parent = ob.parent
    if ob.parent is not None:
        new.matrix_parent_inverse = ob.matrix_parent_inverse.copy()
        new.location, new.rotation_euler = ob.location.copy(), ob.rotation_euler.copy()
    bpy.data.objects.remove(ob)
    return new
