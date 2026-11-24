"""Houten speelpoppetjes: opa en de jongen.

Gebouwd uit eenvoudige houten vormen: een bol als hoofd (esdoorn, met een geverfd gezichtje), een
gedraaid lijfje, armen en benen van rondhout met afgeronde uiteinden, kraaltjes als schouders,
houten bolletjes als handen en blokjes als schoenen. Haar is uit hout gesneden (een schil om het
hoofd met gutsgroeven). Alles staat in een hiërarchie van lege objecten zodat je kunt poseren.

Voorkant van een poppetje = -y. Linkerkant van het poppetje = +x.
"""
import bpy, math, os
import numpy as np
from mathutils import Vector, Matrix
from . import core as K, hout as H

OPA = dict(
    name='opa',
    hip=2.30, leg_x=0.30, leg_r=0.24, th_l=1.05, sh_l=1.0, shoe=(0.27, 0.43, 0.17), shoe_dy=-0.12,
    body_drop=0.25,
    body_prof=[(0, 0), (0.55, 0.0), (0.69, 0.08), (0.75, 0.35), (0.77, 0.80), (0.74, 1.25), (0.65, 1.58),
               (0.46, 1.79), (0.2, 1.88), (0, 1.89)],
    neck_r=0.21, neck_h=0.20, head_r=0.68,
    sh_x=0.80, sh_z=1.36, ua_r=0.17, ua_l=0.80, fa_r=0.155, fa_l=0.72, hand_r=0.21,
    shirt='#6d90b2', trousers='#5f4b3b', shoes='#3b2c22', hair='#dcd7ce', rolled=True,
    apron='#8b5a36',
    face=dict(eye=(0.29, 0.10, 0.052, 0.066), cheek=(0.48, -0.14, 0.12, 0.42), mouth=('arc', 0.0, -0.27, 0.16, 0.024, 52),
              brow=(0.29, 0.25, 0.11, 0.036, '#b9b2a8'), eye_col='#2a1d16', mouth_col='#7d3326'),
    hairstyle='kaal', glasses=True, nose=0.15, ears=True, pencil=False,
)

JONGEN = dict(
    name='jongen',
    hip=1.15, leg_x=0.20, leg_r=0.17, th_l=0.50, sh_l=0.47, shoe=(0.19, 0.30, 0.12), shoe_dy=-0.09,
    body_drop=0.18,
    body_prof=[(0, 0), (0.40, 0.0), (0.50, 0.06), (0.55, 0.30), (0.55, 0.60), (0.50, 0.90), (0.37, 1.05),
               (0.16, 1.12), (0, 1.13)],
    neck_r=0.15, neck_h=0.12, head_r=0.63,
    sh_x=0.58, sh_z=0.84, ua_r=0.13, ua_l=0.44, fa_r=0.12, fa_l=0.40, hand_r=0.16,
    shirt='#d4473a', shirt2='#f2e8d4', stripes=(0.20, 0.5), trousers='#3e6ea6', shoes='#e7b23b',
    hair='#d6ad62', rolled=False,
    face=dict(eye=(0.28, 0.01, 0.062, 0.078), cheek=(0.47, -0.20, 0.13, 0.55), mouth=('open', 0.0, -0.26, 0.15, 0.10, 0),
              brow=None, eye_col='#2a1d16', mouth_col='#8c3a2c'),
    hairstyle='kort', glasses=False, nose=0.10, ears=True, pencil=False,
)


# ---------------------------------------------------------------- gezicht schilderen
def _comp(rgba, col, a):
    """Verf `col` met dekking a (H,W) over rgba (straight alpha)."""
    c = np.array(K.srgb(col)[:3]) if isinstance(col, str) else np.array(col)
    # srgb() geeft lineair; de afbeelding is sRGB -> zet terug
    c = np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.maximum(c, 1e-9), 1 / 2.4) - 0.055)
    oa = rgba[..., 3]
    na = a + oa * (1 - a)
    for i in range(3):
        rgba[..., i] = np.where(na > 1e-6, (c[i] * a + rgba[..., i] * oa * (1 - a)) / np.maximum(na, 1e-6), c[i])
    rgba[..., 3] = na


def paint_face(name, F, W=1536, Hh=768):
    """Gezicht op een equirectangulaire kaart voor de bolprojectie van Blender (voorkant = u 0.5)."""
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(Hh) + 0.5) / Hh
    U, V = np.meshgrid(u, v)
    th = np.pi * (1 - V)
    a = np.pi * (1 - 2 * U)
    dpx, dpy, dz = np.sin(th) * np.sin(a), np.sin(th) * np.cos(a), np.cos(th)
    dx, dy = -dpx, -dpy
    front = (dy < -0.05).astype(float)
    fx, fz = dx, dz
    aa = 2 * np.pi / W * 1.2
    rgba = np.zeros((Hh, W, 4))
    rgba[..., :3] = 0.8

    def disc(cx, cz, rx, rz):
        q = np.sqrt(((fx - cx) / rx) ** 2 + ((fz - cz) / rz) ** 2)
        return np.clip((1 - q) * min(rx, rz) / aa + 0.5, 0, 1) * front

    def arc(cx, cz, R, thick, a0, a1):
        ang = np.degrees(np.arctan2(fz - cz, fx - cx))
        angc = np.clip(ang, a0, a1)
        px = cx + R * np.cos(np.radians(angc))
        pz = cz + R * np.sin(np.radians(angc))
        d = np.sqrt((fx - px) ** 2 + (fz - pz) ** 2)
        return np.clip((thick / 2 - d) / aa + 0.5, 0, 1) * front

    # wangetjes (zacht, als met een droog penseel)
    cx, cz, s, al = F['cheek']
    for sx in (-1, 1):
        g = np.exp(-((fx - sx * cx) ** 2 + (fz - cz) ** 2) / (2 * s * s)) * al * front
        _comp(rgba, '#ef8f7c', np.clip(g * 1.15, 0, al))
    # wenkbrauwen (tilt > 0: binnenkant omhoog = verdrietig/bezorgd)
    if F.get('brow'):
        bx, bz, R, t, col = F['brow']
        tl = F.get('brow_tilt', 0)
        for sx in (-1, 1):
            _comp(rgba, col, arc(sx * bx, bz - R, R, t, 58 - sx * tl, 122 - sx * tl))
    # ogen + lichtje
    ex, ez, rx, rz = F['eye']
    style = F.get('eye_style', 'dot')
    for sx in (-1, 1):
        if style == 'half':
            # dichte, lachende oogjes (boogjes)
            R = rx * 1.25
            _comp(rgba, F['eye_col'], arc(sx * ex, ez - R * 0.55, R, rz * 0.42, 35, 145))
        else:
            _comp(rgba, F['eye_col'], disc(sx * ex, ez, rx, rz))
            _comp(rgba, '#fff8ee', disc(sx * ex + rx * 0.32, ez + rz * 0.36, rx * 0.28, rx * 0.28))
            if style == 'nat':
                _comp(rgba, '#fff8ee', disc(sx * ex - rx * 0.3, ez - rz * 0.4, rx * 0.16, rx * 0.16))
    # traantje
    if F.get('tear'):
        sx = F['tear']
        tx, tz = sx * ex + rx * 0.2, ez - rz - 0.085
        _comp(rgba, '#7fbde6', disc(tx, tz, 0.038, 0.055))
        _comp(rgba, '#7fbde6', disc(tx, tz + 0.045, 0.018, 0.045))
        _comp(rgba, '#ffffff', disc(tx + 0.012, tz + 0.016, 0.01, 0.013))
    # mond
    kind, mx, mz, mw, mt, span = F['mouth']
    if kind == 'arc':
        R = mw
        _comp(rgba, F['mouth_col'], arc(mx, mz + R, R, mt, -90 - span, -90 + span))
    elif kind == 'frown':
        R = mw
        _comp(rgba, F['mouth_col'], arc(mx, mz - R, R, mt, 90 - span, 90 + span))
    elif kind == 'small':
        _comp(rgba, F['mouth_col'], disc(mx, mz, mw, mt))
    else:
        # open lach: halve ellips (bovenrand recht, iets gebogen)
        top = mz + mt * 0.15 + 0.02 * ((fx - mx) / mw) ** 2
        q = ((fx - mx) / mw) ** 2 + ((fz - top) / mt) ** 2
        inside = np.clip((1 - q) * mt / aa * 0.5 + 0.5, 0, 1) * np.clip((top - fz) / aa + 0.5, 0, 1) * front
        _comp(rgba, F['mouth_col'], inside)
        tq = ((fx - mx) / (mw * 0.55)) ** 2 + ((fz - (top - mt * 0.95)) / (mt * 0.45)) ** 2
        _comp(rgba, '#e0786a', np.clip((1 - tq) * mt * 0.4 / aa + 0.5, 0, 1) * inside)
    path = os.path.join(H.TEX, f'gezicht_{name}.png')
    img = bpy.data.images.new(f'gezicht_{name}', W, Hh, alpha=True)
    img.pixels.foreach_set(rgba.astype(np.float32).ravel())
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    return path


def head_mat(name, F):
    path = paint_face(name, F)
    return H.wood('esdoorn', 'Z', img=path, key=f'hoofd_{name}', img_rough=0.28, img_proj='SPHERE')


# ---------------------------------------------------------------- haar
def _hair_fn(style, R):
    def fn(D, P):
        x, y, z = D[:, 0], D[:, 1], D[:, 2]
        hz = np.sqrt(x * x + y * y) + 1e-9
        cf = -y / hz                          # 1 = voorkant, -1 = achterkant
        phi = np.arctan2(x, -y)
        if style == 'kort':
            h = -0.02 + 0.45 * cf - 0.03 * cf * cf
            h += 0.05 * np.cos(phi * 9) * np.clip(cf, 0, 1) ** 2
            m = K.smoothstep(h - 0.02, h + 0.05, z)
            T = 0.085 * (1 + 0.10 * np.sin(phi * 15 + z * 4))
        else:  # kaal: krans van grijs haar rond de achterkant, voller achterin, dun bij de slapen
            lo = -0.12 - 0.36 * np.clip(-cf, 0, 1) + 0.03 * np.sin(phi * 7)
            hi = 0.22 + 0.22 * np.clip(-cf, 0, 1) - 0.06 * np.clip(cf, 0, 1)
            band = K.smoothstep(lo - 0.04, lo + 0.06, z) * (1 - K.smoothstep(hi - 0.08, hi + 0.06, z))
            back = 1 - K.smoothstep(-0.05, 0.38, cf)
            m = band * back
            T = (0.05 + 0.06 * np.clip(-cf, 0, 1)) * (1 + 0.22 * np.sin(phi * 21 + z * 9))
        f = 1 + T * m - 0.05 * (1 - m)
        return P * f[:, None]
    return fn


# ---------------------------------------------------------------- het poppetje
class Pop:
    def __init__(self, S, name=None):
        self.S = S
        n = self.n = name or S['name']
        self.root = K.empty(n)
        self.pelvis = K.empty(n + '_bekken', (0, 0, S['hip']), parent=self.root)
        self.torso = K.empty(n + '_romp', (0, 0, 0), parent=self.pelvis)
        self.hands = {}
        self._mats()
        self._body()
        self._head()
        self._arms()
        self._legs()
        if S.get('apron'):
            self._apron()

    # -------------------------------------------------- materialen
    def _mats(self):
        S = self.S
        st = S.get('stripes')
        self.m_shirt = H.wood('beuk', 'Z', paint=S['shirt'], paint2=S.get('shirt2'), stripes=st, grain=0.22,
                              rough=0.45, key=f'shirt_{self.n}')
        self.m_sleeve = H.wood('beuk', 'Z', paint=S['shirt'], paint2=S.get('shirt2'), stripes=st, grain=0.22,
                               rough=0.45, key=f'mouw_{self.n}')
        self.m_trousers = H.wood('beuk', 'Z', paint=S['trousers'], grain=0.25, rough=0.5, key=f'broek_{self.n}')
        self.m_shoes = H.wood('beuk', 'Y', paint=S['shoes'], grain=0.18, rough=0.35, coat=0.25, key=f'schoen_{self.n}')
        self.m_skin = H.wood('esdoorn', 'Z', key=f'huid_{self.n}')
        self.m_hair = H.wood('esdoorn', 'Z', paint=S['hair'], grain=0.3, rough=0.5, key=f'haar_{self.n}')

    # -------------------------------------------------- lijf
    def _body(self):
        S = self.S
        b = K.lathe(self.n + '_lijf', S['body_prof'], 64, self.m_shirt, self.torso)
        b.location = (0, 0, -S['body_drop'])
        self.body_top = S['body_prof'][-1][1] - S['body_drop']

    def body_r(self, z):
        """Straal van het lijf op hoogte z (t.o.v. de heup)."""
        pr = np.array(self.S['body_prof'][1:-1])
        return float(np.interp(z + self.S['body_drop'], pr[:, 1], pr[:, 0]))

    # -------------------------------------------------- hoofd
    def _head(self):
        S = self.S
        R = S['head_r']
        self.neck = K.empty(self.n + '_nek', (0, 0, self.body_top - 0.06), parent=self.torso)
        H.cyl(self.n + '_nekje', S['neck_r'], S['neck_h'] + 0.12, self.m_skin, loc=(0, 0, -0.06), parent=self.neck,
              bev=0.03)
        self.head = K.empty(self.n + '_hoofd', (0, 0, S['neck_h']), parent=self.neck)
        c = (0, 0, R * 0.9)
        self.head_c = c
        hm = head_mat(self.n, S['face'])
        H.ball(self.n + '_kop', R, hm, loc=c, parent=self.head, res=(96, 48))
        # haar
        K.blob(self.n + '_haar', (R, R, R), 2.0, (160, 80), deform=_hair_fn(S['hairstyle'], R), mat=self.m_hair,
               parent=self.head, loc=c)
        # neus
        if S.get('nose'):
            H.ball(self.n + '_neus', R * S['nose'], self.m_skin, loc=(0, -R * 0.97, c[2] - R * 0.05),
                   parent=self.head, res=(32, 16))
        # oren
        if S.get('ears'):
            for sx in (-1, 1):
                H.ball(self.n + f'_oor{sx}', R * 0.17, self.m_skin, loc=(sx * R * 0.96, R * 0.05, c[2] - R * 0.08),
                       parent=self.head, res=(24, 12), scale=(0.5, 0.9, 1.15))
        if S.get('glasses'):
            self._glasses(R, c)
        if S.get('pencil'):
            pm = H.wood('ceder', 'Z', paint='#c8372d', grain=0.1, rough=0.3, coat=0.4, key='potlood_rood')
            p = H.cyl(self.n + '_potlood', 0.05, 0.62, pm, parent=self.head, bev=0.01, seg=6)
            p.location = (-R * 1.02, R * 0.05 - 0.31, c[2] + R * 0.12)
            p.rotation_euler = (math.radians(-90), 0, math.radians(-8))
            tip = K.lathe(self.n + '_potloodpunt', [(0, 0), (0.05, 0), (0.01, 0.12), (0, 0.13)], 16,
                          H.wood('ceder', 'Z', key='ceder_kaal'), p)
            tip.location = (0, 0, 0.62)

    def _glasses(self, R, c):
        wm = H.metal('#c8c2b6', 0.22, key='brilmontuur')
        ex, ez = self.S['face']['eye'][:2]
        rr = R * 0.205
        for sx in (-1, 1):
            ang = math.asin(ex) * sx
            cen = Vector((sx * R * 0.315, -R * 1.07, c[2] + R * ez))
            pts = []
            for k in range(25):
                t = 2 * math.pi * k / 24
                v = Vector((math.cos(t) * rr * 1.08, 0, math.sin(t) * rr))
                v.rotate(Matrix.Rotation(ang, 3, 'Z'))
                pts.append(tuple(cen + v))
            K.curve_tube(self.n + f'_glas{sx}', pts, 0.022, wm, self.head, cyclic=True)
            outer = cen + Matrix.Rotation(ang, 3, 'Z') @ Vector((sx * rr * 1.08, 0, rr * 0.2))
            K.curve_tube(self.n + f'_poot{sx}', [tuple(outer), (sx * R * 0.9, -R * 0.66, c[2] + R * 0.17),
                                                  (sx * R * 1.1, -R * 0.08, c[2] + R * 0.12),
                                                  (sx * R * 1.07, R * 0.2, c[2] - R * 0.02)], 0.02, wm, self.head)
        K.curve_tube(self.n + '_brug', [(-R * 0.115, -R * 1.07, c[2] + R * (ez + 0.02)), (0, -R * 1.13, c[2] + R * (ez + 0.09)),
                                        (R * 0.115, -R * 1.07, c[2] + R * (ez + 0.02))], 0.02, wm, self.head)

    # -------------------------------------------------- armen
    def _arms(self):
        S = self.S
        self.sh, self.el = {}, {}
        for side, sx in (('L', 1), ('R', -1)):
            sh = K.empty(self.n + '_schouder' + side, (sx * S['sh_x'], 0, S['sh_z']), parent=self.torso)
            H.ball(self.n + '_kraal' + side, S['ua_r'] * 1.28, self.m_sleeve, parent=sh, res=(32, 16))
            H.capsule(self.n + '_bovenarm' + side, (0, 0, 0), (0, 0, -S['ua_l']), S['ua_r'], self.m_sleeve, sh)
            el = K.empty(self.n + '_elleboog' + side, (0, 0, -S['ua_l']), parent=sh)
            fm = self.m_skin if S.get('rolled') else self.m_sleeve
            H.capsule(self.n + '_onderarm' + side, (0, 0, 0), (0, 0, -S['fa_l']), S['fa_r'], fm, el)
            if S.get('rolled'):
                H.capsule(self.n + '_omslag' + side, (0, 0, 0.02), (0, 0, -0.2), S['fa_r'] * 1.3, self.m_sleeve, el)
            hd = K.empty(self.n + '_hand' + side, (0, 0, -S['fa_l'] - S['hand_r'] * 0.55), parent=el)
            H.ball(self.n + '_handje' + side, S['hand_r'], self.m_skin, parent=hd, res=(32, 16))
            self.sh[side], self.el[side], self.hands[side] = sh, el, hd

    # -------------------------------------------------- benen
    def _legs(self):
        S = self.S
        self.hp, self.kn, self.an = {}, {}, {}
        sx_, sy_, sz_ = S['shoe']
        ankle = S['hip'] - S['th_l'] - S['sh_l']
        for side, sx in (('L', 1), ('R', -1)):
            hp = K.empty(self.n + '_heup' + side, (sx * S['leg_x'], 0, 0), parent=self.pelvis)
            H.capsule(self.n + '_dij' + side, (0, 0, 0.1), (0, 0, -S['th_l']), S['leg_r'], self.m_trousers, hp)
            kn = K.empty(self.n + '_knie' + side, (0, 0, -S['th_l']), parent=hp)
            H.capsule(self.n + '_scheen' + side, (0, 0, 0), (0, 0, -S['sh_l']), S['leg_r'] * 0.95, self.m_trousers, kn)
            an = K.empty(self.n + '_enkel' + side, (0, 0, -S['sh_l']), parent=kn)
            K.blob(self.n + '_schoen' + side, (sx_, sy_, sz_), (2.0, 2.6, 3.2), (48, 24), mat=self.m_shoes, parent=an,
                   loc=(0, S['shoe_dy'], -ankle + sz_ * 0.98))
            self.hp[side], self.kn[side], self.an[side] = hp, kn, an

    # -------------------------------------------------- schort (opa)
    def _apron(self):
        S = self.S
        mat = H.wood('beuk', 'Z', paint=S['apron'], grain=0.15, rough=0.55, key=f'schort_{self.n}')
        rmax = max(r for r, z in S['body_prof'])
        z0, z1 = -0.62, 1.42
        nz, nt = 34, 28
        V = []
        for i in range(nz):
            z = z0 + (z1 - z0) * i / (nz - 1)
            r = (rmax if z < 0.5 else self.body_r(z)) + 0.04
            hw = 1.05 if z < 0.95 else 1.05 - (z - 0.95) / (z1 - 0.95) * 0.5
            for j in range(nt):
                t = -math.pi / 2 - hw + 2 * hw * j / (nt - 1)
                V.append((r * math.cos(t), r * math.sin(t), z))
        F = [(i * nt + j, i * nt + j + 1, (i + 1) * nt + j + 1, (i + 1) * nt + j) for i in range(nz - 1) for j in range(nt - 1)]
        ob = K.mesh_obj(self.n + '_schort', V, F, mat, self.torso)
        K.modifier(ob, 'SOLIDIFY', thickness=0.045, offset=0.0, use_even_offset=True)
        H._harden(ob, 0.015, 2)
        # band om de buik en nekband
        zb = 0.55
        rb = self.body_r(zb) + 0.03
        K.curve_tube(self.n + '_schortband', [(rb * math.cos(t), rb * math.sin(t), zb) for t in np.linspace(0, 2 * math.pi, 33)],
                     0.03, mat, self.torso, cyclic=True)
        rt = self.body_r(z1) + 0.04
        hw = 0.55
        a0, a1 = -math.pi / 2 - hw, -math.pi / 2 + hw
        p0 = (rt * math.cos(a0), rt * math.sin(a0), z1)
        p1 = (rt * math.cos(a1), rt * math.sin(a1), z1)
        top = self.body_top
        K.curve_tube(self.n + '_nekband', [p0, (-0.42, -0.05, top - 0.02), (-0.18, 0.28, top + 0.05), (0.18, 0.28, top + 0.05),
                                            (0.42, -0.05, top - 0.02), p1], 0.035, mat, self.torso)
        # zakje met een potloodje
        r = rmax + 0.075
        zp = 0.12
        pk = H.box(self.n + '_zak', 0.62, 0.05, 0.36, mat, loc=(0.12, -r, zp), bev=0.02, parent=self.torso)
        pk.rotation_euler = (0, 0, math.radians(-6))
        pm = H.wood('ceder', 'Z', paint='#2f6a3a', grain=0.1, rough=0.3, coat=0.4, key='potlood_groen')
        p = H.cyl(self.n + '_zakpotlood', 0.045, 0.5, pm, loc=(0.3, -r + 0.02, zp - 0.05), bev=0.01, seg=6,
                  parent=self.torso)
        p.rotation_euler = (0, math.radians(-12), 0)

    # -------------------------------------------------- plaatsen en poseren
    def place(self, x, y, z=0.0, rot=0.0):
        self.root.location = (x, y, z)
        self.root.rotation_euler = (0, 0, math.radians(rot))
        return self

    def face_to(self, tx, ty):
        x, y = self.root.location.x, self.root.location.y
        self.root.rotation_euler[2] = math.atan2(tx - x, -(ty - y))
        return self

    def pose(self, armL=(0, 8, 10), armR=(0, 8, 10), legL=(0, 0), legR=(0, 0), lean=0.0, twist=0.0, head=(0, 0, 0),
             hip_drop=0.0):
        """arm = (naar voren, opzij, elleboog) in graden; been = (naar voren, knie); head = (draai, knik, kanteling)."""
        for side, sx, a in (('L', 1, armL), ('R', -1, armR)):
            fwd, spread, elbow = (tuple(a) + (0, 0, 0))[:3]
            sh = self.sh[side]
            sh.rotation_mode = 'YXZ'
            sh.rotation_euler = (math.radians(-fwd), math.radians(-sx * spread), 0)
            self.el[side].rotation_euler = (math.radians(-elbow), 0, 0)
        for side, l in (('L', legL), ('R', legR)):
            fwd, knee = (tuple(l) + (0, 0))[:2]
            self.hp[side].rotation_euler = (math.radians(-fwd), 0, 0)
            self.kn[side].rotation_euler = (math.radians(knee), 0, 0)
            self.an[side].rotation_euler = (math.radians(fwd - knee), 0, 0)
        self.torso.rotation_euler = (math.radians(lean), 0, math.radians(twist))
        self.pelvis.location.z = self.S['hip'] - hip_drop
        t, n, k = (tuple(head) + (0, 0, 0))[:3]
        self.head.rotation_euler = (math.radians(n), math.radians(k), math.radians(t))
        return self

    def look_at(self, target, tilt=0.0, amount=1.0):
        """Draai het hoofd naar een punt in de wereld (zonder het lijf te draaien)."""
        bpy.context.view_layer.update()
        self.head.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()
        M = self.head.matrix_world
        c = M @ Vector(self.head_c)
        d = M.to_3x3().inverted() @ (Vector(target) - c)
        yaw = math.atan2(d.x, -d.y) * amount
        pitch = math.atan2(-d.z, math.hypot(d.x, d.y)) * amount
        self.head.rotation_euler = (pitch, math.radians(tilt), yaw)
        return self

    def head_world(self):
        bpy.context.view_layer.update()
        return self.head.matrix_world @ Vector(self.head_c)

    def hold(self, ob, side='R', loc=(0, 0, 0), rot=(0, 0, 0)):
        """Hang een object aan een hand (lokale coördinaten van de hand)."""
        ob.parent = self.hands[side]
        ob.location = loc
        ob.rotation_euler = tuple(math.radians(a) for a in rot)
        return ob


def opa(**over):
    S = dict(OPA)
    S.update(over)
    return Pop(S)


def jongen(**over):
    S = dict(JONGEN)
    S.update(over)
    return Pop(S)


# ---------------------------------------------------------------- gezichtsuitdrukkingen
def _face(base, **kw):
    F = dict(base)
    F.update(kw)
    return F


OPA_LIEF = _face(OPA['face'], eye_style='half', mouth=('arc', 0.0, -0.26, 0.13, 0.024, 44), brow_tilt=6)
OPA_ERNSTIG = _face(OPA['face'], mouth=('arc', 0.0, -0.29, 0.34, 0.022, 9), brow_tilt=12)
JOAH_LUISTER = _face(JONGEN['face'], mouth=('small', 0.0, -0.27, 0.045, 0.035, 0), brow=(0.28, 0.2, 0.1, 0.025, '#b88a52'),
                     brow_tilt=12)
JOAH_VERDRIETIG = _face(JONGEN['face'], eye_style='nat', mouth=('frown', 0.0, -0.33, 0.12, 0.03, 52),
                        brow=(0.28, 0.2, 0.1, 0.032, '#b88a52'), brow_tilt=26, cheek=(0.47, -0.2, 0.13, 0.35))
JOAH_TRAAN = _face(JOAH_VERDRIETIG, tear=-1)
OPA_ZACHT = _face(OPA['face'], eye_style='half', mouth=('arc', 0.0, -0.27, 0.12, 0.022, 16), brow_tilt=9)
JOAH_TRAAN_LIEF = _face(JOAH_VERDRIETIG, tear=-1, mouth=('arc', 0.0, -0.29, 0.11, 0.03, 34), brow_tilt=14)
