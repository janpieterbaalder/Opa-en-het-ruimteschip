import math
from lib import core as K, hout as H, scene as S, spullen as SP, figuren as FG
def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    H.box('grond', 60, 40, 0.5, H.wood('beuk', 'X', paint='#f0ece4', grain=0.05, key='g'), loc=(0, 0, -0.5), bev=0, base=True)
    K.world_color('#e9e4da', 0.5)
    K.light('AREA', (-6, -12, 10), (0, 0, 2), energy=1600, size=8)
    SP.gereedschapskist('kist_groot', (-4.0, 0, 0), rot=36, s=1.6)
    SP.gereedschapskist('kist', (3.6, -0.6, 0), rot=28)
    o = FG.opa(); o.place(6.4, 0.6); o.face_to(4, -8)
    j = FG.jongen(); j.place(1.2, 0.4); j.face_to(2, -8)
    S.cam((0, -26, 5.0), (0, 0, 2.2), lens=55, fstop=None)
    S.render(out)
