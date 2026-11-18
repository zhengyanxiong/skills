# Film: the wall, the camera, the items

## Units and the scene file

World units are 4K screen pixels at camera zoom 1. At zoom 1 the frame shows 3840 x 2160 world px; at zoom 0.5 it shows 7680 x 4320; at 0.13 a whole wall about 30,000 px wide.

```python
from engine import Film, GeoMap, Print, Stamp, StringLine, XMarker, RegionFill, RUST, MUSTARD

def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W          # line start, line end, when a spoken word lands
    film = Film(doc.duration, fps=30, look="wall")
    us = film.add(GeoMap(doc.map("us"), 60000))
    pr = film.add(Print("P01", 27800, 300, 2600, rot=-1.2, t_in=L(2) + 0.1, label="PHOTO: JOHN T. DANIELS", label_t=W(4, "took")))
    film.add(Stamp("FAILED", 25150, -7250, size=330, t_in=W(11, "river") - 0.1))
    film.shot(L(2) + 0.9, 27800, 250, 1.12, rot=-0.6)
    return film
```

- `doc.W(i, "word")` searches the **spoken** text: ask for "nineteen", not "1903". Use `nth=1` for a word's second occurrence.
- `doc.on(print, fx, fy)` gives the world point at a fraction of a print's image, rotation included.
- `doc.res()` measures text while laying out (`PaperDoc.phrase_spans(doc.res(), "not a crank")`).
- `film.add()` returns the item, so later lines can point strings, circles and the camera at it.

## Laying out the wall

1. Give each section a **cluster**: an area of the wall with its prints, documents and numbers. Leave about one print's width between clusters.
2. Put a map in the middle if the story travels. Hang clusters near the places they belong, on the map or out on the cork beside it, and tie them to their place with a `StringLine`.
3. Travel between clusters along a string (evidence: this leads to that) or a `Route` (people moving). The camera follows the line as it draws on.
4. Make the final pull-back a composition: everything still visible should read as one designed board.

**Map scale.** `GeoMap(data, K)`: K is world px per earth radius. At K=24000 the lower 48 states are about 17,000 px wide, which suits a story spread across the country. When several places a few hundred km apart each need their own prints (Dayton, Washington, the Outer Banks), use K=50000 to 70000 so each gets its own room. Close up, the map draws live vectors, so it stays sharp at any K.

## Camera

- One `film.shot(t, x, y, zoom, rot)` (or `cam` plus `focus`) every 0.6 to 3 seconds. The spline is monotone and keeps drifting through keys, so a hold is two keys close together, slightly apart.
- **Push in** to land on a hero: zoom from about 0.5 to 0.9 to 1.2 as the line reaches its key word.
- **Pull back** to show a connection or a place: zoom 0.2 to 0.35.
- **Whip** between clusters in 0.8 to 1.2 s. Motion blur and a whoosh are added on their own.
- Lean the roll a degree or two (`rot`) and let it change between keys. The handheld drift is built in.
- Land the camera on a hero about 0.3 s **after** it appears. It reads as the camera noticing it.
- Shakes: `Stamp` and `Ledger` shake the camera by themselves; `film.shake(t, amp, dur)` for anything else.

## Spotlight

`film.focus(t, x, y, radius, strength)` dims everything outside the hero. The hero is clear within about 0.7 x radius, and fully dim (strength) past 2.4 x radius. Use `film.shot()` so the light moves with the camera. For wide shots use a large radius and a low strength (0.15 to 0.3).

## Items

| Item | Use | Key arguments |
| --- | --- | --- |
| `Print(key, x, y, w, rot, t_in)` | A photo or document. `paper=True` makes a torn clipping that tears in | `label`, `label_t` (red name bar), `t_out`, `exit_vec` (slides off), `dim` |
| `PaperDoc(x, y, w, h, ...)` | A typeset document (a recreation): header lines, grey rows, one real sentence | `header=((text, size, font),)`, `sentence`, `phrase_spans()` |
| `Card(x, y, w, h, t_in, title, lines)` | A clean rounded panel for explainers and product stories; rises into place | `accent`, `rgb`, `text_rgb`, `title_size`, `body_size` |
| `Ledger`, `OpenLedger` | A closed ledger or file that slams down; an open spread with one handwritten entry | `label`, `entry`, `entry_mark()` |
| `BigText(text, x, y, size, t_in)` | Years, titles, numbers. Distressed by default | `bar=HILITE`, `bar_h` (0.92 for a full block), `type_on`, `hit` |
| `Counter(x, y, size, value, t_in)` | A number rolling up | `prefix`, `suffix`, `caption`, `dur` |
| `Stamp(text, x, y, size, rot, t_in)` | A verdict slammed onto a print | `rgb`, `shake` |
| `PenMark(kind, x, y, w, h, t_in)` | ellipse, underline, strike, arrow, highlight | `dur`, `width`, `rot`, `rgb` |
| `StringLine(a, b, t_in)` | Red string, pin to pin | `persist=True` to keep it; it fades after `hold` by default |
| `Chalk(x, y, times)` | Tally marks, one per time | `strike_t` |
| `Holes(print, pts, times)` | Holes punched into a print (shots, a punch card) | fractional `pts` |
| `FilmFrame(print, t_in)` | Film-strip bands around a print | |
| `DotField(points, t0, t1)` | Dots popping up (bars, stores, outbreaks) | `rgb`, `r` |
| `GeoMap(data, K)` | The map sheet | `look="explainer"` or `"period"`, `place(name)` |
| `RegionFill(map, names, rgb, t_in)` | Fill states or countries; `to_rgb`/`t_change` turns active RUST into visited MUSTARD | |
| `XMarker(x, y, label, t_in)` | A map marker with a typed-on label | `side`, `size`, `label_size` |
| `MapPin(x, y, label, t_in)` | A pulsing red pin with a typewriter label | |
| `Route(a, b, t_in)` | A white travel arc drawing on | `bend`, `width` |

Every item takes `t_out` (fade out), `z` (stacking order) and `sfx=False` (mute its own sounds). Write a new item by subclassing `Item`: give it `bounds()` for culling, `draw(c, res, t)`, and optionally `cues()` and `shakes()`. A big static drawing (a city street map, a floor plan) subclasses `Cached` too, so it is drawn once and reused.

## Looks and type

`Film(look=...)`:

- `wall`: dark cork, warm. True stories.
- `slate`: blue-grey. Business, politics.
- `charcoal`: neutral black. Lets colour photos lead.
- `paper`: light desk.
- `studio`: light seamless. Products, brands, explainers with cards.
- `blueprint`: deep blue with a grid. Engineering, science.
- `night`: dark navy with strong glow. Tech, space, trailers.

Change the finish with `film.look["grain"]`, `["glow"]`, `["vignette"]`, `["grade"]` and `["dim"]` (the spotlight colour; light looks dim towards grey, not black).

On light looks, use dark type and `BigText(grunge=False, shadow=False)` for a clean finish. Use `Print(pin=False)` for photos that should sit like prints on a table, not pinned evidence.

Font roles are `cond` (labels, numbers, stamps), `label` and `labelm` (map labels, captions), `serif` (documents), `mono` (typewriter), `hand` (handwriting). Each falls back through common fonts. Put a file at `fonts/<role>.ttf` in the project to force one, for example Oswald Bold (OFL) as `cond` on Linux. `check_setup.py` prints what each role resolves to, and `get_fonts.py` fetches Bebas Neue (condensed) and Homemade Apple (handwriting) for any role that would fall back to the system default.

Colour on dark looks: white or cream type. Dark ink goes only on paper, cards or a full yellow block (`bar_h=0.92`).

Pick one accent per film and keep it for the things that matter. In the documentary kit that is yellow for highlights and dates and red for verdicts and names; teal is water, and RUST then MUSTARD marks map regions (active, then visited). A brand film uses its own brand colour as the accent.

## Review loop

```bash
python3 scripts/render.py --project my-film --probe 2,5.5,9,12.5 --size 1280x720   # one still per line
python3 scripts/render.py --project my-film --strip 16.8:21.7:12 --size 1280x720   # a camera move as a contact sheet
```

Put the probe stills on one contact sheet and look at all of them. Check:

- the hero is lit and readable
- nothing important is cut by the frame edge
- type is not dark on dark
- labels don't collide
- the spotlight follows the camera
- no frame is empty mid-move

Fix, then probe again. Use a strip for each move between clusters.
