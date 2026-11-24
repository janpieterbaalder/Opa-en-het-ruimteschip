"""Testplaat p. 3-4: 'Dit is [naam]. En dit is opa.' De jongen op zijn dobbelsteen links, opa rechts."""
import math
from lib import core as K, hout as H, scene as S, werkplaats as WP, figuren as FG, spullen as SP


def main(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw()
    WP.licht()
    bx, by = WP.BENCH
    top = WP.BENCH_TOP

    # de jongen op zijn opstapje, met het hamertje boven de spijker
    SP.dobbelsteen('opstapje', (bx - 3.8, by - 1.2, 0), rot=-10)
    j = FG.jongen()
    j.place(bx - 3.8, by - 1.2, 1.6)
    j.face_to(bx + 1.5, by - 9.0)
    j.pose(armL=(58, 32, 38), armR=(20, 14, 35), lean=4)
    hj = SP.hamertje('hamertje', bead='#d4473a', L=1.0, br=0.17)
    j.hold(hj, 'L', loc=(0, -0.3, 0.0), rot=(90, 0, 0))

    # opa aan de andere kant, hand op de werkbank, eigen hamer in de hand
    o = FG.opa()
    o.place(bx + 3.9, by - 1.0)
    o.face_to(bx - 1.2, by - 9.0)
    o.pose(armR=(52, 18, 30), armL=(30, 12, 62), lean=5)
    ham = SP.hamertje('opa_hamer', bead='#e7b23b', L=1.5, br=0.24)
    o.hold(ham, 'L', loc=(0, -0.42, 0.0), rot=(90, 0, 0))

    o.look_at(j.head_world(), amount=0.3)
    j.look_at(o.head_world(), amount=0.4, tilt=-5)

    cx = bx
    S.cam((cx, -16.5, 7.6), (cx, by - 0.4, 3.9), lens=40, fstop=0.16, focus=(cx, by - 1.1, 4.0))
    S.render(out)
