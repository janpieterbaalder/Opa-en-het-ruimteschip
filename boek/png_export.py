"""Losse PNG's per pagina (21 x 21 cm op 300 dpi = 2480 x 2480 px), om het boek te laten afdrukken
als fotoboek (bijvoorbeeld bij de HEMA, vierkant 21 x 21 cm).

    python boek/png_export.py                        # uit renders_druk/ (drukresolutie), anders renders/
    python boek/png_export.py --bron renders         # uit een andere map

Uit: 'Bram en de grote kraan - pagina's (PNG)'/
     00 voorkant.png, 01 pagina 1.png ... 30 pagina 30.png, 31 achterkant.png
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build  # noqa: E402

OUT = os.path.join(ROOT, "Bram en de grote kraan - pagina's (PNG)")


def name(n):
    if n == 0:
        return '00 voorkant.png'
    if n == build.N_PAGES - 1:
        return f'{n:02d} achterkant.png'
    return f'{n:02d} pagina {n}.png'


def main():
    src = os.path.join(ROOT, 'renders_druk')
    if '--bron' in sys.argv:
        src = os.path.abspath(sys.argv[sys.argv.index('--bron') + 1])
    pages, _ = build.all_pages(src)
    os.makedirs(OUT, exist_ok=True)
    for n, im in enumerate(pages):
        p = os.path.join(OUT, name(n))
        im.convert('RGB').save(p, 'PNG', dpi=(300, 300), optimize=False, compress_level=6)
        print('png', os.path.basename(p), im.size)


if __name__ == '__main__':
    main()
