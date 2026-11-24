"""Opzet per plaat: formaat, kwaliteit, camera met scherptediepte (miniatuurfoto)."""
import bpy
from . import core as K

SPREAD = (5040, 2520)   # 42 x 21 cm + afloop, 300 dpi
PAGE = (2520, 2520)


def setup(opts, kind='spread', exposure=0.0, look='Medium High Contrast', seed=1, transparent=False):
    K.reset(seed)
    q = opts.get('q', 'preview')
    W, H = SPREAD if kind == 'spread' else PAGE
    if opts.get('w'):
        f = int(opts['w']) / W
        W, H = int(W * f), int(H * f)
    elif q == 'preview':
        W, H = W // 4, H // 4
    elif q == 'mid':
        W, H = W // 2, H // 2
    samples = int(opts.get('samples') or (64 if q == 'preview' else 192 if q == 'mid' else 512))
    K.render_setup(W, H, samples=samples, exposure=exposure, look=look, transparent=transparent)
    sc = bpy.context.scene
    sc.cycles.adaptive_threshold = 0.012 if q == 'preview' else 0.005
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 12
    sc.cycles.sample_clamp_indirect = 5.0
    return dict(q=q, W=W, H=H)


def cam(loc, target, lens=50, fstop=0.08, focus=None, shift=(0, 0), roll=0.0):
    """1 eenheid = 1 cm, Blender rekent in meters: f/5.6 in het echt ~ fstop 0.056 hier."""
    return K.camera(loc, target, lens=lens, fstop=fstop, focus=focus if focus is not None else target,
                    shift=shift, roll=roll, clip=(0.05, 400))


def render(path):
    import time
    t0 = time.time()
    K.render(path)
    print(f'RENDERTIJD {time.time() - t0:.0f}s')
