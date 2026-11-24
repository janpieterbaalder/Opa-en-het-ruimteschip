"""Gezichten van voren en schuin."""
import math
from lib import core as K, hout as H, scene as S, figuren as FG, spullen as SP


def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    H.box('grond', 40, 40, 0.5, H.wood('berk', 'X', key='grond'), loc=(0, 0, -0.5), bev=0, base=True)
    H.box('achter', 40, 0.5, 20, H.wood('beuk', 'Z', paint='#8fa598', key='achter'), loc=(0, 8, 0), bev=0, base=True)
    K.world_color('#d9c7ad', 0.25)
    K.light('AREA', (-10, -18, 14), (0, 0, 3), energy=2500, size=10, color=(1, 0.93, 0.84))
    K.light('AREA', (12, -6, 6), (0, 0, 3), energy=600, size=6, color=(0.85, 0.9, 1.0))
    for k, rot in enumerate((0, 35, 90)):
        o = FG.Pop(dict(FG.OPA), name=f'opa{k}')
        o.place(-5.5 + k * 3.0, 0, 0, rot=rot)
        o.pose(armL=(10, 8, 10), armR=(10, 8, 10))
    for k, rot in enumerate((0, -35)):
        j = FG.Pop(dict(FG.JONGEN), name=f'jongen{k}')
        j.place(4.0 + k * 2.6, 0, 1.6, rot=rot)
        SP.dobbelsteen(f'dob{k}', (4.0 + k * 2.6, 0, 0))
    S.cam((0.5, -19, 4.9), (0.5, 0, 4.3), lens=70, fstop=0.4, focus=(0.5, 0, 4.4))
    S.render(out)
