"""Proef: het schip in de werkplaats."""
import math
from lib import core as K, hout as H, scene as S, werkplaats as WP, figuren as FG, spullen as SP, schip as SC


def main(out, opts):
    S.setup(opts, 'spread', exposure=0.35)
    WP.bouw(bench=False, lamp=False, bankje=False, floor=False)
    WP.licht()
    SC.bouw(loc=(0.5, -2.6, 0), rot=-18, stage=opts.get('stage', 'klaar'))
    j = FG.jongen()
    j.place(-7.2, -8.5)
    j.face_to(0, -20)
    j.pose(armL=(10, 20, 20), armR=(150, 20, 10))
    o = FG.opa()
    o.place(8.4, -8.0)
    o.face_to(2, -20)
    o.pose(armL=(15, 15, 30), armR=(20, 10, 30))
    S.cam((0.5, -31, 10.5), (0.5, -3.0, 5.0), lens=40, fstop=0.25, focus=(0.5, -7, 4))
    S.render(out)
