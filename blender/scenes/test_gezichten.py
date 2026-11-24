import math
from lib import core as K, hout as H, scene as S, figuren as FG
def main(out, opts):
    S.setup(opts, 'spread', exposure=0.3)
    H.box('achter', 60, 0.5, 30, H.wood('beuk', 'Z', paint='#8fa598', key='a'), loc=(0, 8, -5), bev=0, base=True)
    K.world_color('#d9c7ad', 0.35)
    K.light('AREA', (-6, -16, 10), (0, 0, 3), energy=2200, size=10, color=(1, 0.94, 0.86))
    faces = [('opa', FG.OPA['face']), ('opa', FG.OPA_LIEF), ('opa', FG.OPA_ERNSTIG),
             ('jongen', FG.JOAH_LUISTER), ('jongen', FG.JOAH_VERDRIETIG), ('jongen', FG.JOAH_TRAAN)]
    for k, (who, F) in enumerate(faces):
        S_ = dict(FG.OPA if who == 'opa' else FG.JONGEN)
        S_['face'] = F
        p = FG.Pop(S_, name=f'{who}{k}')
        x = -7.5 + k * 3.0
        p.place(x, 0, -3.6 if who == 'opa' else -1.3)
    S.cam((0, -26, 2.0), (0, 0, 1.8), lens=55, fstop=None)
    S.render(out)
