import math
from lib import core as K, hout as H, scene as S, spullen as SP
def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    SP.vloer(-30, 30, -20, 10)
    K.world_color('#e9e4da', 0.45)
    K.light('AREA', (-8, -14, 14), (0, 0, 2), energy=2600, size=10, color=(1, 0.95, 0.88))
    SP.gereedschapskist('kist', (-9.5, 1.0, 0), rot=10)
    SP.handzaag('zaag', L=2.4, loc=(-3.6, -2.0, 0.8), rot=(0, 0, math.radians(-10)))
    SP.rolmaat('rolmaat', (1.0, 2.0, 0), rot=-20)
    SP.theelichtje('thee', (7.5, -1.0, 0))
    SP.muntstapel('munten', (11.5, -1.5, 0))
    SP.bolletje_wol('wol', (15.5, 2.5, 2.2))
    SP.sleutel('sleutel', (4.5, -4.5, 0.12), rot=(0, 0, 0.5))
    SP.losse_elastiekjes('elastiek', (-4, -5.5))
    SP.duimstok_ladder('ladder', loc=(-16, -3, 0), rot=(0, math.radians(-35), 0.3))
    SP.knijpertje('knp', loc=(9, -5.5, 0.6), rot=(math.pi/2, 0, 0.3), L=7.2,
                  wood=H.wood('berk', 'X', paint='#3561a8', grain=0.15, paint_until=4.2, key='halfblauw'))
    S.cam((0, -30, 13), (0, 0, 1.5), lens=40, fstop=None)
    S.render(out)
