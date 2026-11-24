"""Catalogus: de vijftig nieuwe voorwerpen in een raster."""
import math
from lib import core as K, hout as H, scene as S, voorwerpen as VW
def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    H.box('grond', 200, 120, 0.5, H.wood('berk', 'X', paint='#efe9df', grain=0.05, key='g'), loc=(0, 0, -0.5), bev=0, base=True)
    K.world_color('#efeae2', 0.55)
    K.light('AREA', (-30, -40, 60), (0, 0, 0), energy=60000, size=40, color=(1, 0.96, 0.9))
    cols, dx, dy = 10, 13.0, 13.0
    big = {'spaghetti_bundel': (0, math.pi / 2, 0), 'kaneelstokje': (0, math.pi / 2, 0), 'wattenstaafje': (0, math.pi / 2, 0),
           'rietje': (0, math.pi / 2, 0), 'speelkaart': (0.4, 0, 0), 'borduurring': (0.9, 0, 0), 'ballon': (0, 0, 0)}
    for k, n in enumerate(VW.ALLE):
        i, j = k % cols, k // cols
        x, y = (i - (cols - 1) / 2) * dx, ((4 - j) - 2) * dy
        rot = big.get(n, (0, 0, 0.4))
        try:
            ob = getattr(VW, n)(f'v_{n}', (x, y, 0.3), rot)
            if n in ('spaghetti_bundel', 'kaneelstokje', 'wattenstaafje', 'rietje'):
                ob.scale = (0.45, 0.45, 0.45)
                ob.location = (x - 4, y, 1.0)
            if n == 'ballon':
                ob.scale = (0.6, 0.6, 0.6)
        except Exception as e:
            print('FOUT', n, e)
    cam = S.cam((0, -95, 120), (0, 0, 0), lens=40, fstop=None)
    S.render(out)
