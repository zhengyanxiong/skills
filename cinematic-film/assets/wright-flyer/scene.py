"""TWELVE SECONDS: the Wright Flyer, about 90 s. The worked example for cinematic-film.

One continuous camera over one wall: a US map print in the middle, the cold open (the first-flight
photograph) out on the cork past North Carolina, Dayton's prints above the Great Lakes, Langley's
prints to the north-east. Every time comes from the voiceover: doc.L(i) is when line i starts,
doc.W(i, "word") when a spoken word lands, so a new voice re-times the whole film by itself.

World units are 4K pixels at zoom 1 (zoom 0.5 shows 7680 x 4320 world px).
"""
from engine import (HILITE, MUSTARD, RUST, WHITE, BigText, Counter, Film, GeoMap, PaperDoc, PenMark, Print,
                    RegionFill, Route, Stamp, StringLine, XMarker)

CX = 27800                      # the cold-open cluster, out on the cork past the coast
K = 60000                       # map scale: big enough that Dayton, Washington and the Outer Banks each get room
LBL = dict(size=3.0, label_size=150)


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    res = doc.res()
    film = Film(doc.duration, fps=30, look="wall")
    cam, foc, cue = film.cam, film.focus, film.cue

    us = film.add(GeoMap(doc.map("us"), K, look="explainer"))
    kdh, dayton, dc = us.place("Kill Devil Hills"), us.place("Dayton"), us.place("Washington")

    # ============================================================ COLD OPEN (1-4)
    # 1 the date, then the pin on the Outer Banks
    film.add(BigText("DECEMBER 17, 1903", CX, -2350, 520, L(1) - 0.1, t_out=L(3), type_on=0.6, bar=HILITE, bar_h=0.92, rgb=(30, 26, 22), shadow=False))
    film.add(RegionFill(us, ["North Carolina"], RUST, W(1, "beach"), to_rgb=MUSTARD, t_change=L(5) + 0.5))
    film.add(XMarker(*kdh, "KILL DEVIL HILLS, N.C.", t_in=W(1, "North"), side="left", **LBL))

    # 2 the photograph lands out past the coast, tied to the pin
    photo = film.add(Print("P01", CX, 300, 2600, rot=-1.2, t_in=L(2) + 0.1, label="PHOTO: JOHN T. DANIELS", label_t=W(4, "took")))
    film.add(StringLine(kdh, (CX - 1250, -560), t_in=L(2) + 0.2, dur=0.7, sag=0.03, width=16, persist=True))

    # 3 two counters roll up under it
    c12 = film.add(Counter(CX - 1100, 2950, 760, 12, W(3, "Twelve") - 0.05, dur=0.8, caption="SECONDS"))
    film.add(Counter(CX + 1250, 2950, 760, 120, W(3, "hundred") - 0.15, dur=1.0, caption="FEET"))

    # 4 the photographer's name bar (Print label), then the title
    title_t = E(4) + 0.45
    film.add(BigText("TWELVE SECONDS", CX, -2300, 860, title_t, rgb=(244, 240, 232), hit=None))
    ring = film.add(PenMark("ellipse", CX, -2560, 7600, 1500, t_in=title_t + 0.35, dur=0.8, width=26, seed=4, rot=-2, rgb=(236, 230, 220)))
    cue("boom", title_t, 0.55)

    cam(0.0, CX, -2150, 1.0, -1.0)
    cam(W(1, "windy") - 0.3, CX - 600, -1900, 0.92, -0.6)
    cam(W(1, "North") + 0.4, 22300, -1100, 0.33, 0.0)               # pull back: the pin and the date together
    cam(L(2) + 0.9, CX, 250, 1.12, -0.6)
    cam(L(3) + 0.3, CX + 50, 1300, 0.95, -0.3)
    cam(E(3) + 0.1, CX + 50, 1900, 0.88, 0.0)
    cam(L(4) + 0.6, CX, 900, 0.86, 0.2)
    cam(E(4) + 0.3, CX, -400, 0.52, 0.0)
    cam(title_t + 1.0, CX, -1100, 0.46, -0.2)
    foc(0.0, CX, -2300, 1700, 0.5)
    foc(W(1, "North") + 0.3, 22300, -1100, 7000, 0.3)
    foc(L(2) + 0.6, CX, 300, 1700, 0.6)
    foc(L(3) + 0.3, CX + 50, 2200, 1900, 0.55)
    foc(L(4) + 0.5, CX, 900, 2000, 0.55)
    foc(title_t + 0.2, CX, -1200, 4200, 0.5)

    # ============================================================ DAYTON (5-8)
    film.add(StringLine((CX - 1250, -560), dayton, t_in=L(5) + 0.15, dur=1.2, sag=0.02, width=22))
    film.add(RegionFill(us, ["Ohio"], RUST, W(5, "Dayton") - 0.2, to_rgb=MUSTARD, t_change=L(14) + 0.6))
    film.add(XMarker(*dayton, "DAYTON", t_in=W(5, "Dayton"), side="right", **LBL))
    shop = film.add(Print("P02", 9400, -7100, 2000, rot=1.5, t_in=W(5, "bicycle") - 0.1))
    wil = film.add(Print("P03", 6500, -7350, 1700, rot=-2.0, t_in=W(6, "Wilbur") - 0.1, label="WILBUR WRIGHT", label_t=W(6, "Wilbur") + 0.1))
    orv = film.add(Print("P04", 12350, -7350, 1700, rot=2.2, t_in=W(6, "Orville") - 0.1, label="ORVILLE WRIGHT", label_t=W(6, "Orville") + 0.1))
    letter = film.add(PaperDoc(15900, -7500, 2500, 3200, rot=1.6, t_in=W(7, "wrote") - 0.1, rows=16, sentence_row=5, sentence_size=96,
                               header=(("WRIGHT CYCLE COMPANY", 130, "serif"), ("DAYTON, OHIO  ·  MAY 30, 1899", 78, "mono")),
                               sentence="I am an enthusiast, but not a crank in the sense that I have some pet theories as to the proper construction of a flying machine."))
    (ex, ey), ew = letter.phrase_pos(res, "I am an enthusiast,")
    (nx, ny), nw = letter.phrase_pos(res, "not a crank")
    film.add(PenMark("highlight", ex, ey - 30, ew + 60, 0, t_in=W(8, "enthusiast") - 0.35, dur=0.45, width=120, rot=1.6))
    film.add(PenMark("highlight", nx, ny - 30, nw + 60, 0, t_in=W(8, "crank") - 0.45, dur=0.4, width=120, rot=1.6, seed=3))

    cam(L(5) + 0.5, 17500, -2500, 0.26, 0.0)                       # wide: the string races to Dayton
    cam(W(5, "bicycle") + 0.2, 9600, -5000, 0.44, 0.3)
    cam(E(5) + 0.2, 9400, -6500, 0.6, 0.5)
    cam(L(6) + 0.5, 9400, -6900, 0.43, 0.0)                         # all three prints
    cam(E(6) + 0.1, 10200, -6900, 0.45, -0.2)
    cam(W(7, "wrote") + 0.4, 15600, -7500, 0.7, 0.6)
    cam(E(7) + 0.1, 15900, -7400, 0.8, 0.8)
    cam(W(8, "enthusiast"), ex + 300, ey + 150, 1.1, 1.0)
    cam(E(8) + 0.2, nx + 100, ny + 120, 1.12, 1.2)
    foc(L(5) + 0.4, 15000, -2500, 9000, 0.25)
    foc(W(5, "bicycle") + 0.1, 9400, -6000, 2600, 0.5)
    foc(L(6) + 0.4, 9400, -7000, 5200, 0.45)
    foc(W(7, "wrote") + 0.3, 15900, -7500, 2000, 0.6)
    foc(W(8, "enthusiast"), ex + 300, ey, 1300, 0.62)

    # ============================================================ THE RIVAL (9-13)
    cue("riser", L(9) - 1.3, 0.5, dur=1.2)
    lang = film.add(Print("P05", 20700, -7600, 1900, rot=-1.4, t_in=W(9, "Samuel") - 0.15, label="SAMUEL P. LANGLEY", label_t=W(9, "Samuel") + 0.1))
    film.add(StringLine((17000, -8900), (20700, -8620), t_in=W(9, "charge") - 0.1, dur=0.7, sag=0.06, width=16))
    film.add(Counter(20700, -4750, 800, 50000, W(10, "fifty") - 0.15, dur=1.2, prefix="$", caption="WAR DEPARTMENT"))
    boat = film.add(Print("P06", 25300, -7400, 2700, rot=1.2, t_in=W(11, "launched") - 0.15, label="OCTOBER 7, 1903", label_t=W(11, "October")))
    film.add(XMarker(*dc, "WASHINGTON", t_in=W(11, "Potomac") - 0.1, side="right", **LBL))
    film.add(StringLine(dc, (25300 - 900, -8350), t_in=W(11, "Potomac"), dur=0.8, sag=0.03, width=18))
    film.add(Stamp("FAILED", 25150, -7250, size=330, rot=-9, t_in=W(11, "river") - 0.1))
    nyt = film.add(PaperDoc(29700, -7600, 2400, 3150, rot=-1.5, t_in=W(12, "Times") - 0.2, rows=15, sentence_row=6, sentence_size=78,
                            header=(("THE NEW YORK TIMES", 150, "serif"), ("FRIDAY, OCTOBER 9, 1903", 70, "mono"),
                                    ("FLYING MACHINES WHICH DO NOT FLY", 96, "cond")),
                            sentence="...the flying machine which will really fly might be evolved by the combined and continuous efforts "
                                     "of mathematicians and mechanicians in from one million to ten million years."))
    spans = nyt.phrase_spans(res, "one million to ten million years.")
    for k, ((hx, hy), hw) in enumerate(spans):
        film.add(PenMark("highlight", hx, hy - 24, hw + 50, 0, t_in=W(12, "million") - 0.4 + 0.25 * k, dur=0.35, width=100, rot=-1.5, seed=7 + k))
    film.add(Stamp("FAILED AGAIN", 25500, -6500, size=270, rot=6, t_in=W(13, "result") - 0.1))
    for k in range(3):
        cue("heartbeat", L(13) + 0.1 + k * 0.95, 0.55)

    cam(L(9) + 0.6, 18300, -7600, 0.55, 0.6)
    cam(W(9, "Samuel") + 0.4, 20700, -7400, 0.78, 0.0)
    cam(E(9) + 0.1, 20750, -7000, 0.7, -0.3)
    cam(W(10, "fifty") + 0.1, 20700, -5800, 0.72, -0.4)
    cam(E(10) + 0.2, 21500, -6200, 0.55, 0.0)
    cam(W(11, "launched") + 0.3, 21800, -5600, 0.3, 0.2)            # wide: Washington, Langley, the houseboat
    cam(W(11, "Potomac") + 0.4, 22200, -5300, 0.27, 0.2)
    cam(W(11, "river") - 0.3, 25300, -7300, 0.8, 0.6)
    cam(E(11) + 0.2, 25350, -7200, 0.86, 0.8)
    cam(W(12, "Times") + 0.3, 29700, -7700, 0.72, -0.6)
    hx0, hy0 = spans[0][0]
    cam(W(12, "million"), hx0 + 200, hy0 + 100, 1.0, -1.0)
    cam(E(12) + 0.2, hx0 + 260, hy0 + 140, 1.05, -1.2)
    cam(L(13) + 0.5, 25400, -7000, 0.74, 0.3)
    cam(E(13) + 0.3, 25450, -6900, 0.82, 0.5)
    foc(L(9) + 0.5, 19000, -7800, 2600, 0.5)
    foc(W(9, "Samuel") + 0.3, 20700, -7400, 1700, 0.62)
    foc(W(10, "fifty"), 20700, -5800, 1900, 0.6)
    foc(W(11, "launched") + 0.2, 21500, -5600, 7000, 0.3)
    foc(W(11, "river") - 0.2, 25300, -7300, 2000, 0.6)
    foc(W(12, "Times") + 0.2, 29700, -7600, 2000, 0.6)
    foc(W(12, "million"), hx0 + 200, hy0, 1300, 0.62)
    foc(L(13) + 0.4, 25400, -7000, 2100, 0.62)

    # ============================================================ KITTY HAWK (14-17)
    cue("riser", L(14) - 1.2, 0.45, dur=1.1)
    film.add(Route(dayton, kdh, t_in=L(14) + 0.4, dur=1.6, bend=0.18, width=55))
    film.add(RegionFill(us, ["North Carolina"], RUST, L(14) + 1.9, alpha=0.95))
    thousand = film.add(Counter(CX, 5000, 820, 1000, W(15, "less") - 0.1, dur=1.0, prefix="UNDER $", caption="1900 TO 1903, TRAVEL INCLUDED"))
    film.add(PenMark("underline", CX - 1100, 3200, 1500, 40, t_in=W(16, "Orville") - 0.1, dur=0.4, width=22, seed=12))
    film.add(Counter(CX + 4350, 2950, 760, 59, W(16, "fifty") - 0.1, dur=0.9, caption="SECONDS"))
    tele = film.add(Print("P07", CX + 4350, -150, 2600, rot=1.4, t_in=L(17) + 0.05))
    (sx, sy) = doc.on(tele, 0.08, 0.742)
    (cx, cy) = doc.on(tele, 0.17, 0.942)
    film.add(PenMark("highlight", sx, sy, 0.115 * 2600, 0, t_in=W(17, "Success") - 0.2, dur=0.3, width=95, rot=1.4))
    film.add(PenMark("highlight", cx, cy, 0.29 * 2600, 0, t_in=W(17, "Christmas") - 0.45, dur=0.45, width=95, rot=1.4, seed=5))

    cam(L(14) + 0.6, 17500, -2400, 0.19, 0.0)                       # wide: the route home to the beach
    cam(E(14) - 0.2, CX - 2500, -400, 0.34, -0.2)
    cam(W(15, "less") + 0.2, CX, 4000, 0.68, -0.4)
    cam(E(15) + 0.2, CX, 4400, 0.7, -0.2)
    cam(L(16) + 0.4, CX - 400, 2900, 0.72, 0.0)
    cam(W(16, "fifty") + 0.2, CX + 2400, 2500, 0.62, 0.3)
    cam(L(17) + 0.6, CX + 4350, -150, 0.92, 0.8)
    cam(W(17, "Success") + 0.3, sx + 650, sy - 50, 1.25, 1.0)
    cam(W(17, "Christmas"), cx + 300, cy - 200, 1.2, 1.2)
    film.shot(E(17) + 0.6, CX + 4100, 300, 0.85, 0.8)
    foc(L(14) + 0.5, 15000, -2500, 9500, 0.2)
    foc(W(15, "less"), CX, 4400, 1900, 0.58)
    foc(L(16) + 0.3, CX - 400, 3000, 2600, 0.5)
    foc(W(16, "fifty"), CX + 3000, 2600, 2600, 0.5)
    foc(L(17) + 0.5, CX + 4350, -150, 1900, 0.6)
    foc(W(17, "Success") + 0.2, sx + 500, sy, 1300, 0.6)

    # ============================================================ CLOSE (18-19)
    film.add(PenMark("ellipse", 20700, -5050, 3900, 1150, t_in=W(18, "fifty") - 0.1, dur=0.6, width=24, seed=21, rot=-2))
    film.add(PenMark("ellipse", CX, 4700, 6300, 1250, t_in=W(19, "thousand") - 0.2, dur=0.6, width=24, seed=22, rot=2))
    cam(L(18) + 0.9, 22800, -6100, 0.4, 0.0)                        # back across the wall to Langley
    cam(E(18), 22600, -5900, 0.42, -0.2)
    cam(W(19, "bicycle") + 0.4, 24500, 300, 0.21, 0.0)
    cam(W(19, "sky"), 21500, -1400, 0.16, 0.0)
    cam(film.duration, 18500, -1700, 0.122, 0.0)                    # the whole wall
    foc(L(18) + 0.8, 22800, -6100, 3800, 0.45)
    foc(W(19, "bicycle") + 0.3, 24500, 0, 9000, 0.3)
    foc(W(19, "sky"), 19000, -1500, 22000, 0.1)

    film.fade_in, film.fade_out = 0.9, 2.2
    return film
