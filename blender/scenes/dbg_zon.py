import bpy
from lib import core as K, scene as S, werkplaats as WP
def main(out, opts):
    S.setup(opts, 'spread', exposure=0.0)
    WP.bouw(lamp=False)
    WP.licht(fill=0.0, world=0.0, haze=0.0)
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name != 'Zon':
            ob.data.energy = 0
    S.cam((2, -22, 21), (-4, 2, 0), lens=24, fstop=None)
    S.render(out)
