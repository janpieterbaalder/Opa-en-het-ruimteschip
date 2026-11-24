import math
from lib import core as K, hout as H, scene as S, spullen as SP
def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    H.box('grond', 40, 40, 0.5, H.wood('beuk', 'X', paint='#f0ece4', grain=0.05, key='g'), loc=(0, 0, -0.5), bev=0, base=True)
    K.world_color('#e9e4da', 0.5)
    K.light('AREA', (-6, -12, 10), (0, 0, 2), energy=1600, size=8)
    SP.knijpertje('k1', loc=(-2.2, 0, 7.4), rot=(math.pi / 2, math.pi / 2, 0), L=7.2)
    SP.knijpertje('k2', loc=(1.6, 0.6, 7.4), rot=(math.pi / 2, math.pi / 2, math.radians(-40)), L=7.2)
    S.cam((0, -24, 3.8), (0, 0, 3.7), lens=60, fstop=None)
    S.render(out)
