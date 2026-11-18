"""Starter scene: a short explainer in the studio look, built only from code (no photos needed).

Runs as soon as the project has a voice:
  tts_say.py -> split_takes.py -> build_narration.py -> render.py --probe / --out

Replace it with your film. The pattern stays the same: lay the world out in clusters, add items on
voiceover times (doc.L line start, doc.W spoken word), then camera keys with film.shot().
World units are 4K pixels at zoom 1 (zoom 0.5 shows 7680 x 4320).
"""
from engine import BigText, Card, Counter, Film, PenMark, Route

ACCENT = (198, 92, 46)
INK = (34, 32, 30)
CARD_W, CARD_H, GAP = 3200, 1800, 4400          # four cards in a row, one per step
XS = [i * GAP for i in range(4)]
MID = (XS[0] + XS[-1]) / 2


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="studio")

    # 1  the title, then an underline on the word that matters
    film.add(BigText("FROM CHERRY TO CUP", MID, -2300, 760, L(1) - 0.1, rgb=INK, shadow=False, grunge=False, type_on=0.7))
    film.add(PenMark("underline", MID, -2080, 5800, 60, t_in=W(1, "cherry") - 0.2, dur=0.5, width=34, rgb=ACCENT))

    # 2-5  a card per step appears as its line starts; arrows draw on between them
    steps = [("GROW", ["On a shrub, in the Coffee Belt"], 2),
             ("PICK", ["Ripe cherries only", "Fruit washed or dried away"], 3),
             ("ROAST", ["The green seed turns brown"], 4),
             ("BREW", ["Ground, brewed, poured"], 5)]
    for (title, lines, line), x in zip(steps, XS):
        film.add(Card(x, 0, CARD_W, CARD_H, L(line) + 0.05, title=title, lines=lines, accent=ACCENT, title_size=300, body_size=150))
    for a, b, line in zip(XS, XS[1:], (3, 4, 5)):
        film.add(Route((a + CARD_W / 2 + 80, 0), (b - CARD_W / 2 - 80, 0), t_in=L(line) - 0.2, dur=0.5, bend=-0.3, width=24, rgb=INK))
    film.add(Counter(XS[2], 2150, 600, 200, W(4, "two") - 0.1, dur=1.0, suffix="°C", caption="ROAST", rgb=ACCENT))

    # camera: the title, then along the row (landing on each card just after it appears), then the whole journey
    film.shot(0.0, MID, -2250, 0.52)
    film.shot(E(1) + 0.3, MID, -1100, 0.34)                    # wide: the title and the empty row the cards will fill
    for (title, lines, line), x in zip(steps, XS):
        film.shot(L(line) + 0.45, x, 350, 0.62, rot=-0.4 if line % 2 else 0.4)
        film.shot(E(line) - 0.1, x + 350, 500 if line != 4 else 600, 0.58)
    film.shot(L(6) + 0.6, MID, 0, 0.27)
    film.shot(film.duration, MID, -200, 0.205, radius=20000, strength=0.1)
    return film
