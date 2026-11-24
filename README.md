# Opa en het ruimteschip

Een houten prentenboek voor Joah (4), die zijn opa heeft verloren. Opa kan alles maken van hout.
Samen bouwen ze een schip van spullen uit huis (een kaasdoosje, wasknijpers, knoopjes, een
garenklosje). Als het klaar is, nemen ze afscheid en vliegt opa ermee naar de hemel, tot voorbij
de sterren.

Zelfde aanpak als *Bram en de grote kraan* en *Agent Daan & Joep*: alle platen worden in
**Blender 5.1 (Cycles)** volledig vanuit Python opgebouwd, zonder AI-beeldgenerator of
externe modellen. Formaat 21 × 21 cm, 32 pagina's (voorkant, p. 1-30, achterkant).

| Bestand | Wat het is |
|---|---|
| `opa-en-het-ruimteschip.pdf` | Het boek als bladen van 42 × 21 cm: omslag en 15 dubbele pagina's. |
| `opa-en-het-ruimteschip-druk.pdf` | Drukbestand: 32 losse pagina's van 21 × 21 cm met 3 mm afloop (300 dpi). |
| `Opa en het ruimteschip - pagina's (PDF)/` | Eén PDF per pagina. |
| `Opa en het ruimteschip - pagina's (PNG)/` | Eén PNG per pagina (2480 × 2480, 300 dpi), bijvoorbeeld voor een fotoboek. |
| `web/` | Het online bladerboek: https://opa-en-het-ruimteschip.vercel.app (Vercel-project `opa-en-het-ruimteschip-web`, map `web`; elke push naar `main` publiceert opnieuw). |
| `storyboard.jpg` | Alle bladen op een rij met beeld en tekst. |
| `verhaal.md` | De tekst per pagina en het idee voor het schip. |
| `voorwerpen.md` | Voorraadlijst van ~500 kleine alledaagse voorwerpen als bouwstenen. |
| `renders/` | De ruwe Cycles-renders (2520 × 1260 per dubbele pagina). |

## Zelf opnieuw maken

```bash
python blender/maak_tex.py                                         # etiketten, bouwtekening, postzegel
blender/r.sh sp03_werkplaats work/test.png --w 1260                # één plaat (snelle proef)
SAMPLES=160 blender/batch.sh mid renders $(cat blender/alle_platen.txt)   # alle platen
python boek/build.py                                               # PDF's, losse pagina's, bladerboek, storyboard
git add -A && git commit -m "..." && git push                        # bladerboek online bijwerken
```

- `blender/lib/hout.py`: procedureel hout (jaarringen, nerf, poriën, multiplexranden), verf over hout,
  metaal, plastic, papier, garen, kurk, eikeldop; basisvormen met afgeronde randen.
- `blender/lib/figuren.py`: de houten poppetjes (opa en Joah): geschilderde gezichtjes, gesneden haar,
  bril, schort, poseren, zitten.
- `blender/lib/spullen.py`: alledaagse voorwerpen op ware grootte: ijsstokje, lucifersdoosje, dobbelsteen,
  garenklos, eikeldop-lamp, wasknijper, frisdrankdop, bliklipje, gum, batterij, paperclip, knikker,
  liniaal, kwastje, bedje, krulletjes en zaagsel.
- `blender/lib/voorwerpen.py`: vijftig extra alledaagse voorwerpen (kurken, suikerklontje, eierdopje, pasta, kruidnagel,
  steranijs, kaneel, dennenappel, wattenstaafje, pleister, jampot met knopen, plakband, domino, pion, tol, jojo, kaarsje,
  rietje, ballon, ...).
- `blender/lib/schip.py`: het schip (kaasdoosje, lucifersdoosjes-hutje, wasknijpers, garenklos-motor, knoopjes,
  propeller van ijsstokjes, tandwielstuur), in bouwfasen.
- `blender/lib/werkplaats.py`: opa's werkplaats, met dag-, avond- en nachtlicht.
- `blender/lib/platen.py`: alle platen; `blender/scenes/` roept ze aan.
- `boek/build.py`: tekstopmaak, PDF's, losse pagina's, bladerboek en storyboard. Lettertype: Museo Sans Rounded.
