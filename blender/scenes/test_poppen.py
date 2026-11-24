"""Close-up van de poppetjes op een eenvoudige ondergrond."""
import math
from lib import core as K, hout as H, scene as S, figuren as FG, spullen as SP


def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    H.box('grond', 40, 40, 0.5, H.wood('berk', 'X', key='grond'), loc=(0, 0, -0.5), bev=0, base=True)
    H.box('achter', 40, 0.5, 20, H.wood('beuk', 'Z', paint='#8fa598', key='achter'), loc=(0, 8, 0), bev=0, base=True)
    K.world_color('#d9c7ad', 0.25)
    K.light('AREA', (-10, -18, 14), (0, 0, 3), energy=2500, size=10, color=(1, 0.93, 0.84))
    K.light('AREA', (12, -6, 6), (0, 0, 3), energy=600, size=6, color=(0.85, 0.9, 1.0))
    o = FG.opa()
    o.place(-1.6, 0)
    o.face_to(1.0, -8)
    o.pose(armL=(30, 10, 40), armR=(62, -4, 70), lean=4)
    ham = SP.hamertje('opa_hamer', bead='#e7b23b', L=1.5, br=0.24)
    o.hold(ham, 'R', loc=(0, -0.42, 0.0), rot=(90, 0, 0))
    SP.dobbelsteen('opstapje', (1.8, 0.2, 0), rot=12)
    j = FG.jongen()
    j.place(1.8, 0.2, 1.6)
    j.face_to(-1.0, -8)
    j.pose(armR=(100, 6, 25), armL=(25, 18, 30))
    hj = SP.hamertje('hamertje', bead='#d4473a', L=1.0, br=0.17)
    j.hold(hj, 'R', loc=(0, -0.3, 0.0), rot=(90, 0, 0))
    o.look_at(j.head_world(), amount=0.6)
    j.look_at(o.head_world(), amount=0.6)
    S.cam((0.2, -17, 4.6), (0.2, 0, 3.0), lens=50, fstop=0.2, focus=(0.2, 0, 3.5))
    S.render(out)
