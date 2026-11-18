"""cinematic-film film engine: one continuous camera over one world, drawn with Skia.

World units are 4K screen pixels at camera zoom 1. A Film holds items (each knows how to draw
itself at time t), camera keys, spotlight keys, camera shakes and sound cues. A frame is:
camera transform -> items in z order -> spotlight dim -> film finish (glow, grade, vignette,
grain), with motion-blur sub-frames when the camera moves fast.

A project's scene.py imports from here and defines build_film(doc) -> Film. `doc` (a Doc) gives
the voiceover timing (doc.L, doc.E, doc.W), photo sizes and maps. render.py does the rest.

Performance rules baked in (each measured on the film this was built for):
  * images that repeat (cork, paper) are tiled with drawImageRect: a repeating image shader under
    rotation was about 70x slower in Skia's CPU raster
  * every item reports bounds() so off-screen items are skipped
  * static vector art (maps) is drawn once into an image (Cached) and reused
  * photos are capped at 2200 px (x render scale): full-size copies of ~30 photos pushed a 4K
    worker past 2 GB
"""
from __future__ import annotations

import bisect
import json
import math
import pathlib
import re

import numpy as np
import skia
from PIL import Image, ImageFilter

# ---------------------------------------------------------------- palette
TEAL = (112, 178, 182)
RUST = (186, 86, 52)
MUSTARD = (222, 176, 52)
HILITE = (246, 206, 46)
RED = (168, 28, 24)
INK = (40, 30, 22)
CREAM = (239, 230, 212)
WHITE = (246, 243, 236)

# Font roles -> candidates, tried in order (family, weight). Drop <project>/fonts/<role>.ttf (or .otf)
# to force a face, e.g. fonts/cond.ttf = Oswald Bold from Google Fonts (OFL).
FONT_ROLES = {
    "serif": [("Baskerville", 400), ("Libre Baskerville", 400), ("Georgia", 400), ("Times New Roman", 400), ("DejaVu Serif", 400)],
    "mono": [("Courier New", 700), ("Courier Prime", 700), ("Courier", 700), ("DejaVu Sans Mono", 700), ("Menlo", 700)],
    "hand": [("Snell Roundhand", 400), ("Homemade Apple", 400), ("Segoe Script", 400), ("Brush Script MT", 400), ("URW Chancery L", 400)],
    "cond": [("DIN Condensed", 700), ("Oswald", 700), ("Bebas Neue", 400), ("Roboto Condensed", 700), ("Arial Narrow", 700),
             ("DejaVu Sans Condensed", 700), ("Impact", 400)],
    "label": [("Avenir Next", 800), ("Montserrat", 800), ("Helvetica Neue", 700), ("Arial", 700), ("DejaVu Sans", 700)],
    "labelm": [("Avenir Next", 700), ("Montserrat", 600), ("Helvetica Neue", 500), ("Arial", 400), ("DejaVu Sans", 400)],
}

# Looks: the board under everything plus the film finish. A scene picks one with Film(look=...).
LOOKS = {
    # evidence wall: dark cork, warm grade (true stories, history, crime)
    "wall": dict(board="cork_dark.png", bg=(12, 9, 7), grade=(1.015, 1.0, 0.975), grain=0.026, glow=0.24, vignette=0.75, curve=0.25),
    # cool blue-grey board (politics, business, investigations)
    "slate": dict(board="slate.png", bg=(8, 10, 12), grade=(0.99, 1.0, 1.02), grain=0.024, glow=0.22, vignette=0.7, curve=0.25),
    # neutral black (anything; lets colour photos carry the frame)
    "charcoal": dict(board="charcoal.png", bg=(9, 9, 9), grade=(1.0, 1.0, 1.0), grain=0.03, glow=0.2, vignette=0.75, curve=0.3),
    # light paper desk (education, gentle stories)
    "paper": dict(board="paper.png", bg=(220, 216, 208), grade=(1.01, 1.0, 0.98), grain=0.022, glow=0.12, vignette=0.45, curve=0.2, dim=(70, 64, 58)),
    # light seamless studio (product launches, brand stories, explainers with cards)
    "studio": dict(board="studio.png", bg=(214, 212, 208), grade=(1.0, 1.0, 1.0), grain=0.012, glow=0.06, vignette=0.32, curve=0.12, dim=(96, 92, 88)),
    # deep blue drafting sheet with a grid (engineering, science, how things work)
    "blueprint": dict(board="blueprint.png", bg=(12, 30, 60), grade=(0.98, 1.0, 1.04), grain=0.02, glow=0.26, vignette=0.6, curve=0.2, dim=(4, 10, 24)),
    # dark navy, high glow (tech, space, night-time stories, trailers)
    "night": dict(board="night.png", bg=(7, 9, 15), grade=(0.97, 1.0, 1.06), grain=0.022, glow=0.32, vignette=0.8, curve=0.3, dim=(2, 3, 8)),
}


# ---------------------------------------------------------------- easing / splines
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out_cubic(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x); return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.4):
    x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s)


def ramp(t, t0, dur):
    return clamp((t - t0) / dur) if dur > 0 else float(t >= t0)


class Spline:
    """Monotone cubic (Fritsch-Carlson) through (t, value) keys: smooth, no overshoot, and it keeps
    moving through keys that sit on a monotone run, so a hold can drift instead of stopping dead."""

    def __init__(self, keys):
        keys = sorted(keys)
        self.t = [k[0] for k in keys]; self.v = [k[1] for k in keys]
        n = len(keys)
        d = [(self.v[i + 1] - self.v[i]) / max(1e-9, self.t[i + 1] - self.t[i]) for i in range(n - 1)]
        m = [0.0] * n
        if n > 1:
            m[0], m[-1] = d[0], d[-1]
        for i in range(1, n - 1):
            m[i] = 0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2
        for i in range(n - 1):
            if d[i] == 0:
                m[i] = m[i + 1] = 0.0
                continue
            a, b = m[i] / d[i], m[i + 1] / d[i]
            s = a * a + b * b
            if s > 9:
                k = 3 / math.sqrt(s); m[i] = k * a * d[i]; m[i + 1] = k * b * d[i]
        self.m = m

    def __call__(self, t):
        T = self.t
        if t <= T[0]:
            return self.v[0]
        if t >= T[-1]:
            return self.v[-1]
        i = bisect.bisect_right(T, t) - 1
        h = T[i + 1] - T[i]; u = (t - T[i]) / h
        h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u
        h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
        return h00 * self.v[i] + h10 * h * self.m[i] + h01 * self.v[i + 1] + h11 * h * self.m[i + 1]


# ---------------------------------------------------------------- project context
class Doc:
    """A project folder: voiceover timing, photo sizes, maps. Passed to scene.build_film(doc)."""

    def __init__(self, project):
        self.dir = pathlib.Path(project).resolve()
        self.prep = self.dir / "assets" / "prep"
        tp = self.dir / "audio" / "timing.json"
        if not tp.exists():
            raise SystemExit(f"{tp} not found: record a voice (or a scratch track with tts_say.py), "
                             "then run split_takes.py and build_narration.py first")
        self.timing = json.loads(tp.read_text())
        self.seg = {s["id"]: s for s in self.timing["segments"]}
        self.duration = self.timing["total_duration"]
        mp = self.prep / "photos" / "meta.json"
        self.meta = json.loads(mp.read_text()) if mp.exists() else {}

    def L(self, i):
        """Start of narration line i (seconds)."""
        return self.seg[i]["start"]

    def E(self, i):
        """End of narration line i."""
        return self.seg[i]["end"]

    def W(self, i, word, nth=0):
        """When `word` is spoken in line i, by its letter share of the line (pauses spread evenly).
        Search the SPOKEN text: "1929" is spoken "nineteen twenty-nine", so ask for "nineteen"."""
        vo = self.seg[i]["vo"]
        letters = re.sub(r"[^a-z]", "", vo.lower())
        idx, start = -1, 0
        for _ in range(nth + 1):
            idx = vo.lower().find(word.lower(), start); start = idx + 1
            if idx < 0:
                break
        if idx < 0:
            raise ValueError(f"{word!r} (occurrence {nth}) is not in the spoken text of line {i}: {vo!r}")
        before = len(re.sub(r"[^a-z]", "", vo[:idx].lower()))
        return self.L(i) + (self.E(i) - self.L(i)) * before / max(1, len(letters)) + 0.04

    def on(self, pr, fx, fy):
        """World point at a fractional position (0..1, 0..1) inside a print's image area."""
        w, h = pr.size_from(self.meta)
        return rot_point(pr.x, pr.y, (fx - 0.5) * w, (fy - 0.5) * h, pr.rot)

    def res(self):
        """A Res at world scale, for measuring text while laying out (PaperDoc.phrase_pos and friends)."""
        if not hasattr(self, "_res"):
            self._res = Res(1.0, self.prep, self.dir / "fonts")
        return self._res

    def map(self, name):
        p = self.prep / f"map_{name}.json"
        if not p.exists():
            raise SystemExit(f"{p} not found: add the map to map.json and run make_map.py")
        return json.loads(p.read_text())


# ---------------------------------------------------------------- resources
class Res:
    """Per-process cache of images and fonts. Images are downscaled to what the render size can show."""

    def __init__(self, scale, prep=None, fonts_dir=None):
        self.scale = scale
        self.prep = pathlib.Path(prep) if prep else None
        self.fonts_dir = pathlib.Path(fonts_dir) if fonts_dir else None
        self.imgs, self.tf, self.cache = {}, {}, {}
        self.screen_scale = 1.0
        self.view = skia.Rect.MakeXYWH(-80000, -60000, 160000, 120000)
        mp = self.prep / "photos" / "meta.json" if self.prep else None
        self.meta = json.loads(mp.read_text()) if mp and mp.exists() else {}

    def image(self, key, max_side=None):
        if key not in self.imgs:
            path = self.prep / key if "." in key else self.prep / "photos" / f"{key}.jpg"
            if not path.exists():
                raise SystemExit(f"image {key!r} not found at {path}: run prep_assets.py")
            im = Image.open(path).convert("RGBA")
            lim = int(min(max_side or 3200, 2200) * max(self.scale, 0.35))
            if max(im.size) > lim:
                im.thumbnail((lim, lim), Image.LANCZOS)
            arr = np.ascontiguousarray(np.asarray(im))
            self.imgs[key] = skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType).withDefaultMipmaps()
        return self.imgs[key]

    def typeface(self, name):
        if name not in self.tf:
            self.tf[name] = resolve_typeface(name, self.fonts_dir)[0]
        return self.tf[name]

    def wear(self):
        """Speckle mask that distresses type and stamps (alpha = where ink is knocked out)."""
        if "wear" not in self.imgs:
            rng = np.random.default_rng(7)
            n = rng.random((256, 768)) ** 7 * 255
            sm = np.asarray(Image.fromarray(n.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32)
            arr = np.zeros((256, 768, 4), np.uint8); arr[..., 3] = np.clip(sm * 1.6, 0, 255).astype(np.uint8)
            self.imgs["wear"] = skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType)
        return self.imgs["wear"]

    def font(self, name, size):
        f = skia.Font(self.typeface(name), size)
        f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
        return f


def resolve_typeface(role, fonts_dir=None):
    """(typeface, description) for a font role: project override file, then the candidates, then the default."""
    if fonts_dir:
        for ext in (".ttf", ".otf"):
            p = pathlib.Path(fonts_dir) / f"{role}{ext}"
            if p.exists():
                tf = skia.Typeface.MakeFromFile(str(p))
                if tf:
                    return tf, f"{p.name} (project file)"
    mgr = skia.FontMgr.RefDefault()
    for fam, weight in FONT_ROLES.get(role, []):
        tf = mgr.matchFamilyStyle(fam, skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant))
        if tf is not None and tf.getFamilyName().lower() == fam.lower():
            return tf, f"{fam} {weight}"
    tf = mgr.legacyMakeTypeface("", skia.FontStyle.Bold() if role in ("cond", "label", "mono") else skia.FontStyle.Normal())
    return tf, f"system default ({tf.getFamilyName() if tf else '?'}): install one of {[f for f, _ in FONT_ROLES.get(role, [])][:3]}"


SAMPLING = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def color(rgb, a=1.0):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(255 * clamp(a)))


def paint(rgb=(0, 0, 0), a=1.0, stroke=None, blur=None, aa=True):
    p = skia.Paint(AntiAlias=aa, Color=color(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def draw_text(c, res, text, x, y, size, font="serif", rgb=CREAM, a=1.0, track=0.0, align="left", reveal=None):
    """Draw text with letter tracking (em fraction). reveal=n draws only the first n characters."""
    f = res.font(font, size)
    widths = f.getWidths(f.textToGlyphs(text))
    gap = track * size
    total = sum(widths) + gap * (len(text) - 1)
    x0 = x - total / 2 if align == "center" else x - total if align == "right" else x
    p = paint(rgb, a)
    n = len(text) if reveal is None else int(reveal)
    cx = x0
    for i, ch in enumerate(text):
        if i >= n:
            break
        c.drawString(ch, cx, y, f, p)
        cx += widths[i] + gap
    return total


def text_width(res, text, size, font="serif", track=0.0):
    f = res.font(font, size)
    return sum(f.getWidths(f.textToGlyphs(text))) + track * size * (len(text) - 1)


def partial_path(path, p):
    """The first fraction p of a path, by length (for strokes that draw on)."""
    if p >= 1:
        return path
    pm = skia.PathMeasure(path, False)
    out = skia.Path()
    lengths = []
    while True:
        lengths.append(pm.getLength())
        if not pm.nextContour():
            break
    pm = skia.PathMeasure(path, False)
    want = sum(lengths) * clamp(p)
    for L in lengths:
        if want <= 0:
            break
        pm.getSegment(0, min(L, want), out, True)
        want -= L
        pm.nextContour()
    return out


def rot_point(cx, cy, dx, dy, deg):
    r = math.radians(deg)
    return cx + dx * math.cos(r) - dy * math.sin(r), cy + dx * math.sin(r) + dy * math.cos(r)


# ---------------------------------------------------------------- items
class Item:
    """Base item. t_in: when it appears; t_out: when it starts fading (None = stays). sfx=False mutes its auto cues."""
    z = 0

    def __init__(self, t_in=0.0, t_out=None, z=None, sfx=True):
        self.t_in, self.t_out, self.sfx = t_in, t_out, sfx
        if z is not None:
            self.z = z

    def visible(self, t):
        return t >= self.t_in - 0.01 and (self.t_out is None or t < self.t_out + 0.6)

    def bounds(self, res):
        return None

    def fade(self, t):
        return 1.0 if self.t_out is None else 1 - ramp(t, self.t_out, 0.6)

    def cues(self):
        """Sound cues this item makes on its own: [(type, t, gain, extra kwargs)]."""
        return []

    def shakes(self):
        """Camera shakes this item causes: [(t, amplitude, duration)]."""
        return []

    def draw(self, c, res, t):
        raise NotImplementedError


class Cached:
    """Draw a static item once into an image (per process) and reuse it while the camera is far away;
    once the camera is close enough that the image would go soft, draw the vectors live, clipped to
    the view. Big vector art (a map 40,000 px wide) cannot fit one image sharp enough for close-ups."""
    cache_res = 1.0

    def cached_draw(self, c, res, rect, draw_fn):
        cs = min(res.scale * self.cache_res, 8192 / max(rect.width(), rect.height()))
        if res.screen_scale > cs * 1.3:
            c.save(); c.clipRect(res.view, skia.ClipOp.kIntersect, False)
            draw_fn(c, res)
            c.restore()
            return
        key = id(self)
        if key not in res.cache:
            w, h = int(rect.width() * cs) + 2, int(rect.height() * cs) + 2
            surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(w, h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType))
            with surf as cc:
                cc.clear(skia.Color(0, 0, 0, 0)); cc.scale(cs, cs); cc.translate(-rect.left(), -rect.top())
                draw_fn(cc, res)
            res.cache[key] = surf.makeImageSnapshot().withDefaultMipmaps()
        c.drawImageRect(res.cache[key], rect, SAMPLING, skia.Paint(AntiAlias=True))


def tile_image(c, img, rect, tile, paint_=None, clip=True):
    """Cover `rect` with copies of `img`, each `tile` world px square (the fast path; see module notes)."""
    x0 = math.floor(rect.left() / tile) * tile; y0 = math.floor(rect.top() / tile) * tile
    if clip:
        c.save(); c.clipRect(rect, skia.ClipOp.kIntersect, True)
    y = y0
    while y < rect.bottom():
        x = x0
        while x < rect.right():
            c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tile + 0.5, tile + 0.5), SAMPLING, paint_)
            x += tile
        y += tile
    if clip:
        c.restore()


def paper_fill(c, res, rect, a=1.0, scale=1.0, blend=None):
    p = skia.Paint(AntiAlias=True); p.setAlphaf(clamp(a))
    if blend is not None:
        p.setBlendMode(blend)
    tile_image(c, res.image("paper.png", 1024), rect, 1024 * scale, p)


class Board(Item):
    """The endless surface under everything (cork, slate, charcoal or paper), tiled."""
    z = -100

    def __init__(self, texture="cork_dark.png", tile=2458):
        super().__init__(-1)
        self.texture, self.tile = texture, tile

    def draw(self, c, res, t):
        tile_image(c, res.image(self.texture, 1024), res.view, self.tile, clip=False)


def drop_anim(t, t_in, dur=0.5):
    """Physical landing: (scale, alpha, lift) for a print dropping onto the board."""
    u = ramp(t, t_in, dur)
    return 1 + 0.16 * (1 - ease_out_cubic(u)), ramp(t, t_in, 0.12), 1 - ease_out_cubic(u)


def draw_pin(c, x, y, r=34, rgb=(176, 30, 26), a=1.0):
    c.drawCircle(x + r * 0.35, y + r * 0.55, r * 0.95, paint((0, 0, 0), 0.45 * a, blur=r * 0.35))
    c.drawCircle(x, y, r, paint(rgb, a))
    c.drawCircle(x - r * 0.3, y - r * 0.3, r * 0.35, paint((255, 210, 200), 0.55 * a))


def draw_label(c, res, text, x, y, a=1.0, size=128, rot=0.0, reveal=1.0, rgb=(176, 24, 20), text_rgb=(250, 246, 238)):
    """Name label: a colour bar with condensed caps; the bar wipes in left to right."""
    tw = text_width(res, text, size, "cond", 0.06)
    pad = size * 0.45
    W, H = tw + 2 * pad, size * 1.25
    c.save(); c.translate(x, y); c.rotate(rot)
    u = ease_out_cubic(clamp(reveal))
    c.drawRect(skia.Rect.MakeXYWH(-W / 2 + 8, 12, W * u, H), paint((0, 0, 0), 0.45 * a, blur=10))
    c.drawRect(skia.Rect.MakeXYWH(-W / 2, 0, W * u, H), paint(rgb, a))
    c.save(); c.clipRect(skia.Rect.MakeXYWH(-W / 2, 0, W * u, H))
    draw_text(c, res, text, 0, H * 0.8, size, "cond", text_rgb, a, 0.06, "center")
    c.restore(); c.restore()


class Print(Item):
    """A photo or document on the board: paper border, shadow, pin, drop-in. paper=True makes a torn
    newspaper clipping that tears onto the board instead. label= adds a red name bar under it."""
    z = 10

    def __init__(self, key, x, y, w, rot=0.0, t_in=0.0, t_out=None, border=0.035, pin=True,
                 paper=False, z=None, label=None, label_t=None, aspect=None, sfx=True, label_rgb=(176, 24, 20)):
        super().__init__(t_in, t_out, z, sfx)
        self.key, self.x, self.y, self.w, self.rot = key, x, y, w, rot
        self.border, self.pin, self.paper = border, pin, paper
        self.label, self.label_t, self.label_rgb = label, label_t, label_rgb
        self.aspect = aspect
        self.dim = None        # optional callable t -> extra darkening 0..1
        self.exit_vec = None   # (dx, dy): slide off while fading out

    def size_from(self, meta):
        if self.aspect:
            return self.w, self.w / self.aspect
        if self.key not in meta:
            raise SystemExit(f"photo {self.key!r} is not in assets/prep/photos/meta.json: add it to photos.json and run prep_assets.py")
        m = meta[self.key]
        return self.w, self.w * m["h"] / m["w"]

    def size(self, res):
        return self.size_from(res.meta)

    def outer(self, res):
        w, h = self.size(res)
        b = 0 if self.paper else self.border * min(w, h)
        return w + 2 * b, h + 2 * b

    def bounds(self, res):
        W, H = self.outer(res); r = max(W, H) * 0.8 + 400
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r + (300 if self.label else 0))

    def cues(self):
        return [("slide", self.t_in, 0.6, {})] if self.paper else [("pop", self.t_in, 0.8, {})]

    def torn_path(self, W, H, seed=None):
        if getattr(self, "_torn", None) is None:
            rng = np.random.default_rng(seed if seed is not None else sum(map(ord, self.key)) % 9999)
            p = skia.Path(); step = max(W, H) / 70

            def edge(x0, y0, x1, y1, nx, ny, first):
                L = math.hypot(x1 - x0, y1 - y0); n = max(2, int(L / step))
                for i in range(n):
                    u = i / n; d = rng.uniform(0, 0.011) * min(W, H) + (rng.random() < 0.06) * rng.uniform(0.01, 0.02) * min(W, H)
                    x, y = x0 + (x1 - x0) * u + nx * d, y0 + (y1 - y0) * u + ny * d
                    (p.moveTo if (first and i == 0) else p.lineTo)(x, y)
            edge(-W / 2, -H / 2, W / 2, -H / 2, 0, 1, True); edge(W / 2, -H / 2, W / 2, H / 2, -1, 0, False)
            edge(W / 2, H / 2, -W / 2, H / 2, 0, -1, False); edge(-W / 2, H / 2, -W / 2, -H / 2, 1, 0, False)
            p.close(); self._torn = p
        return self._torn

    def draw(self, c, res, t):
        s, a, lift = drop_anim(t, self.t_in)
        tx = ty = tr = 0.0
        if self.paper:                       # clippings tear onto the board: fast slide and settle, no scale pop
            u = ease_out_back(ramp(t, self.t_in, 0.42), 1.1)
            s = 1.0; lift = 1 - ease_out_cubic(ramp(t, self.t_in, 0.42))
            tx, ty, tr = (1 - u) * 260, (1 - u) * 900, (1 - u) * 7
            a = ramp(t, self.t_in, 0.08)
        a *= self.fade(t)
        if a <= 0:
            return
        w, h = self.size(res)
        b = 0 if self.paper else self.border * min(w, h)
        W, H = w + 2 * b, h + 2 * b
        ox, oy = tx, ty
        if self.exit_vec and self.t_out is not None:
            u = ease_in_out(ramp(t, self.t_out, 0.6)); ox += self.exit_vec[0] * u; oy += self.exit_vec[1] * u
        c.save()
        c.translate(self.x + ox, self.y + oy); c.rotate(self.rot + 3.0 * lift + tr); c.scale(s, s)
        off = 18 + 70 * lift
        c.drawRect(skia.Rect.MakeXYWH(-W / 2 + off * 0.4, -H / 2 + off, W, H), paint((0, 0, 0), 0.55 * a, blur=22 + 50 * lift))
        if not self.paper:
            paper_fill(c, res, skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), a, 1.0)
        ip = skia.Paint(AntiAlias=True); ip.setAlphaf(a)
        if self.paper:
            torn = self.torn_path(W, H)
            c.drawPath(torn, paint((240, 237, 230), 0.9 * a, stroke=10))
            c.save(); c.clipPath(torn, skia.ClipOp.kIntersect, True)
            c.drawImageRect(res.image(self.key), skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMPLING, ip)
            c.restore()
        else:
            c.drawImageRect(res.image(self.key), skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMPLING, ip)
        if self.dim:
            d = self.dim(t)
            if d > 0:
                c.drawRect(skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), paint((0, 0, 0), d * a))
        if self.pin:
            if self.paper:
                draw_pin(c, -0.36 * W, -H / 2 + 0.012 * H, r=max(26, 0.02 * W), a=a)
            else:
                draw_pin(c, 0, -H / 2 + max(b * 0.5, 0.03 * H), r=max(26, 0.02 * W), a=a)
        c.restore()
        if self.label:
            lt = self.label_t if self.label_t is not None else self.t_in + 0.35
            la = ramp(t, lt, 0.15) * self.fade(t)
            if la > 0:
                draw_label(c, res, self.label, self.x + ox, self.y + oy + H / 2 * s + 30, la, size=max(120, 0.068 * W), rot=self.rot,
                           reveal=ramp(t, lt, 0.4), rgb=self.label_rgb)


class MapPin(Item):
    """Red map pin with a soft pulse and a typewriter label (case-board style)."""
    z = 30

    def __init__(self, x, y, label=None, t_in=0.0, t_out=None, label_side="right", size=1.0, label_size=70, z=None, sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.x, self.y, self.label, self.side, self.k, self.ls = x, y, label, label_side, size, label_size

    def bounds(self, res):
        L = len(self.label or "") * self.ls * self.k * 0.75 + 400 * self.k
        return skia.Rect.MakeLTRB(self.x - L, self.y - 300 * self.k, self.x + L, self.y + 300 * self.k)

    def cues(self):
        return [("pop", self.t_in, 0.5, {})]

    def draw(self, c, res, t):
        u = ramp(t, self.t_in, 0.35)
        a = u * self.fade(t)
        if a <= 0:
            return
        k = self.k
        ph = (t - self.t_in) % 2.2 / 2.2
        c.drawCircle(self.x, self.y, 30 * k + 120 * k * ph, paint(RED, 0.35 * (1 - ph) * a, stroke=6 * k))
        c.drawCircle(self.x, self.y, 70 * k, paint((220, 40, 30), 0.25 * a, blur=40 * k))
        c.drawCircle(self.x, self.y, 22 * k * ease_out_back(u), paint((200, 34, 28), a))
        c.drawCircle(self.x, self.y, 9 * k, paint((255, 190, 170), a))
        if self.label:
            la = ramp(t, self.t_in + 0.2, 0.4) * self.fade(t)
            n = len(self.label) * ease_out_cubic(ramp(t, self.t_in + 0.2, 0.5))
            dx = 60 * k if self.side == "right" else -60 * k
            draw_text(c, res, self.label, self.x + dx, self.y + self.ls * 0.35, self.ls * k, "mono", (120, 22, 18), la,
                      0.14, "left" if self.side == "right" else "right", reveal=n + 0.999)


class StringLine(Item):
    """Red string pulled from pin to pin, sagging; draws on over `dur`. Fades `hold` seconds after it
    lands unless persist=True: strings are for the beat, and a wall full of them reads as clutter."""
    z = 40

    def __init__(self, a, b, t_in, dur=1.0, sag=0.05, width=9, z=None, pins=True, t_out=None, persist=False, hold=5.0, sfx=True):
        if t_out is None and not persist:
            t_out = t_in + dur + hold
        super().__init__(t_in, t_out, z, sfx)
        self.a, self.b, self.dur, self.sag, self.wd, self.pins = a, b, dur, sag, width, pins

    def bounds(self, res):
        (x0, y0), (x1, y1) = self.a, self.b
        d = math.hypot(x1 - x0, y1 - y0) * self.sag + 200
        return skia.Rect.MakeLTRB(min(x0, x1) - 200, min(y0, y1) - 200, max(x0, x1) + 200, max(y0, y1) + d)

    def cues(self):
        return [("slide", self.t_in, 0.5, {})]

    def path(self):
        (x0, y0), (x1, y1) = self.a, self.b
        d = math.hypot(x1 - x0, y1 - y0)
        p = skia.Path(); p.moveTo(x0, y0); p.quadTo((x0 + x1) / 2, (y0 + y1) / 2 + d * self.sag, x1, y1)
        return p

    def draw(self, c, res, t):
        u = ease_in_out(ramp(t, self.t_in, self.dur))
        a = self.fade(t)
        if u <= 0 or a <= 0:
            return
        seg = partial_path(self.path(), u)
        c.save(); c.translate(10, 22)
        c.drawPath(seg, paint((0, 0, 0), 0.4 * a, stroke=self.wd, blur=6))
        c.restore()
        c.drawPath(seg, paint((150, 24, 20), a, stroke=self.wd))
        c.drawPath(seg, paint((210, 70, 60), 0.35 * a, stroke=self.wd * 0.35))
        if self.pins:
            draw_pin(c, *self.a, r=26, a=a)
            if u >= 0.999:
                draw_pin(c, *self.b, r=26, a=a)


class PenMark(Item):
    """Hand-drawn mark revealed as it is drawn, timed to land on the spoken word.
    kind: ellipse | underline | strike | arrow | highlight (yellow marker, multiply blend)."""
    z = 50

    def __init__(self, kind, x, y, w, h=0, t_in=0.0, dur=0.6, width=12, seed=1, rot=0.0, t_out=None, z=None, rgb=(160, 22, 20), sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.kind, self.x, self.y, self.w, self.h, self.dur, self.wd, self.rot, self.rgb = kind, x, y, w, h, dur, width, rot, rgb
        rng = np.random.default_rng(seed)
        p = skia.Path()
        if kind == "ellipse":
            a0 = rng.uniform(-2.4, -1.8); turns = 1.12; n = 80
            for i in range(n + 1):
                th = a0 + 2 * math.pi * turns * i / n
                wob = 1 + 0.035 * math.sin(3 * th + rng.uniform(0, 6)) + 0.03 * (i / n)
                (p.moveTo if i == 0 else p.lineTo)(math.cos(th) * w / 2 * wob, math.sin(th) * h / 2 * wob)
        elif kind == "highlight":
            p.moveTo(-w / 2, rng.uniform(-3, 3)); p.cubicTo(-w / 6, rng.uniform(-6, 6), w / 6, rng.uniform(-6, 6), w / 2, rng.uniform(-4, 4))
        elif kind == "arrow":
            p.moveTo(-w / 2, 0); p.cubicTo(-w / 4, -h, w / 4, -h, w / 2, 0)
        elif kind == "strike":
            p.moveTo(-w / 2, h / 2 * rng.uniform(-0.2, 0.2)); p.quadTo(0, -h * 0.25, w / 2, h / 2 * rng.uniform(-0.3, 0.3))
        else:  # underline
            p.moveTo(-w / 2, 0); p.cubicTo(-w / 6, h * 0.25 + 4, w / 6, -h * 0.2 - 4, w / 2, h * 0.15 + 2)
        self.p = p

    def cues(self):
        if self.kind == "highlight":
            return [("marker", self.t_in, 0.8, {})]
        if self.kind == "strike" and self.dur < 0.3:
            return [("snip", self.t_in, 0.7, {})]
        return [("pencil", self.t_in, 0.6, {"dur": round(max(0.3, self.dur), 2)})]

    def draw(self, c, res, t):
        u = ease_out_cubic(ramp(t, self.t_in, self.dur))
        a = self.fade(t)
        if u <= 0 or a <= 0:
            return
        c.save(); c.translate(self.x, self.y); c.rotate(self.rot)
        seg = partial_path(self.p, u)
        if self.kind == "highlight":
            hp = paint(HILITE, 0.62 * a, stroke=self.wd); hp.setStrokeCap(skia.Paint.kButt_Cap)
            hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawPath(seg, hp)
        else:
            c.drawPath(seg, paint(self.rgb, 0.9 * a, stroke=self.wd))
            if self.kind == "arrow" and u > 0.92:
                k = self.wd * 3.4; th = math.atan2(self.h, self.w / 4)
                for sgn in (-1, 1):
                    c.drawLine(self.w / 2, 0, self.w / 2 - k * math.cos(th + sgn * 0.5), -k * math.sin(th + sgn * 0.5),
                               paint(self.rgb, 0.9 * a, stroke=self.wd))
        c.restore()


class Chalk(Item):
    """Tally marks, one stroke per time in `times`; optional red strike through them at strike_t."""
    z = 45

    def __init__(self, x, y, times, height=170, gap=62, strike_t=None, t_out=None, seed=3, rgb=INK, width=18, sfx=True):
        super().__init__(min(times), t_out, None, sfx)
        self.rgb, self.width = rgb, width
        self.x, self.y, self.times, self.hh, self.gap, self.strike_t = x, y, times, height, gap, strike_t
        rng = np.random.default_rng(seed)
        self.jit = [(rng.uniform(-8, 8), rng.uniform(-10, 10), rng.uniform(-6, 6)) for _ in times]

    def cues(self):
        out = [("tick", tt, 0.6, {}) for tt in self.times]
        if self.strike_t is not None:
            out.append(("pencil", self.strike_t, 0.7, {"dur": 0.4}))
        return out

    def draw(self, c, res, t):
        a = self.fade(t)
        for i, ti in enumerate(self.times):
            u = ease_out_cubic(ramp(t, ti, 0.12))
            if u <= 0:
                continue
            jx, jy, js = self.jit[i]
            x = self.x + i * self.gap + jx
            c.drawLine(x, self.y + jy, x + js, self.y + jy + self.hh * u, paint(self.rgb, 0.88 * a, stroke=self.width))
        if self.strike_t is not None:
            u = ease_out_cubic(ramp(t, self.strike_t, 0.35))
            if u > 0:
                x0 = self.x - 50; x1 = self.x + (len(self.times) - 1) * self.gap + 50
                c.drawLine(x0, self.y + self.hh * 0.62, x0 + (x1 - x0) * u, self.y + self.hh * 0.38, paint((170, 24, 20), 0.95 * a, stroke=self.width + 2))


class Stamp(Item):
    """Rubber stamp: slams down with overshoot, ink with worn edges, a small camera shake."""
    z = 60

    def __init__(self, text, x, y, size=150, rot=-8.0, t_in=0.0, t_out=None, z=None, rgb=(168, 26, 22), shake=True, sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.text, self.x, self.y, self.size, self.rot, self.rgb, self.shake = text, x, y, size, rot, rgb, shake

    def bounds(self, res):
        r = len(self.text) * self.size * 1.2
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def cues(self):
        return [("stamp", self.t_in, 1.0, {})]

    def shakes(self):
        return [(self.t_in + 0.1, 10, 0.3)] if self.shake else []

    def draw(self, c, res, t):
        u = ramp(t, self.t_in, 0.14)
        if u <= 0:
            return
        a = self.fade(t) * min(1, u * 3)
        s = 1.7 - 0.7 * ease_out_cubic(u)
        tw = text_width(res, self.text, self.size, "cond", 0.05)
        pad = self.size * 0.42
        W, H = tw + 2 * pad, self.size * 1.55
        c.save(); c.translate(self.x, self.y); c.rotate(self.rot); c.scale(s, s)
        c.saveLayerAlpha(None, int(235 * a))
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), 18, 18)
        c.drawRRect(r, paint(self.rgb, 1, stroke=self.size * 0.09))
        draw_text(c, res, self.text, 0, self.size * 0.36, self.size, "cond", self.rgb, 1, 0.05, "center")
        wp = skia.Paint(); wp.setBlendMode(skia.BlendMode.kDstOut)
        c.drawImageRect(res.wear(), skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), SAMPLING, wp)
        c.restore(); c.restore()


class BigText(Item):
    """Large words in world space (years, titles, numbers). grunge=True distresses the ink; bar=rgb wipes
    a colour block in behind it (highlighter yellow or a red bar), bar_h its height as a fraction of the
    size (0.42 = a marker streak through the lower half; 0.92 = a full label block, needed for dark ink
    on a dark board); type_on=seconds types it letter by letter; hit=gain plays an impact on arrival."""
    z = 70

    def __init__(self, text, x, y, size, t_in, t_out=None, font="cond", rgb=WHITE, track=0.04, rules=False,
                 type_on=0.0, z=None, shadow=True, grunge=True, bar=None, bar_h=0.42, hit=None, sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.text, self.x, self.y, self.size, self.font = text, x, y, size, font
        self.rgb, self.track, self.rules, self.type_on, self.shadow = rgb, track, rules, type_on, shadow
        self.grunge, self.bar, self.bar_h, self.hit = grunge, bar, bar_h, hit

    def bounds(self, res):
        r = len(self.text) * self.size * 0.8 + self.size * 3
        return skia.Rect.MakeLTRB(self.x - r, self.y - self.size * 2, self.x + r, self.y + self.size)

    def cues(self):
        return [("impact", self.t_in, self.hit, {})] if self.hit else []

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.5) * self.fade(t)
        if a <= 0:
            return
        reveal = len(self.text) * ramp(t, self.t_in, self.type_on) + 0.999 if self.type_on > 0 else None
        drift = 1 - ease_out_cubic(ramp(t, self.t_in, 1.2))
        tr = self.track + 0.06 * drift
        tw0 = text_width(res, self.text, self.size, self.font, tr)
        if self.bar is not None:
            bu = ease_out_cubic(ramp(t, self.t_in - 0.1, 0.35))
            bh = self.size * self.bar_h
            c.drawRect(skia.Rect.MakeXYWH(self.x - tw0 / 2 - self.size * 0.15, self.y + self.size * 0.063 - bh, (tw0 + self.size * 0.3) * bu, bh),
                       paint(self.bar, 0.92 * self.fade(t)))
        if self.grunge:
            c.saveLayerAlpha(None, 255)
        if self.shadow:
            c.save(); c.translate(6, 14)
            draw_text(c, res, self.text, self.x, self.y, self.size, self.font, (0, 0, 0), 0.55 * a, tr, "center", reveal)
            c.restore()
        tw = draw_text(c, res, self.text, self.x, self.y, self.size, self.font, self.rgb, a, tr, "center", reveal)
        if self.grunge:
            wp = skia.Paint(); wp.setBlendMode(skia.BlendMode.kDstOut)
            c.drawImageRect(res.wear(), skia.Rect.MakeXYWH(self.x - tw / 2 - 20, self.y - self.size, tw + 40, self.size * 1.15), SAMPLING, wp)
            c.restore()
        if self.rules:
            ru = ease_out_cubic(ramp(t, self.t_in + 0.2, 0.9))
            yy = self.y - self.size * 0.33
            L = self.size * 2.2 * ru
            gap = tw / 2 + self.size * 0.45
            p = paint(self.rgb, 0.65 * a, stroke=max(3, self.size * 0.018))
            c.drawLine(self.x - gap, yy, self.x - gap - L, yy, p)
            c.drawLine(self.x + gap, yy, self.x + gap + L, yy, p)


class Counter(Item):
    """A number that rolls up to its value, distressed, with an optional caption under it."""
    z = 70

    def __init__(self, x, y, size, value, t_in, dur=1.3, prefix="", suffix="", caption=None, rgb=WHITE, t_out=None,
                 font="cond", start=0, sfx=True):
        super().__init__(t_in, t_out, None, sfx)
        self.x, self.y, self.size, self.value, self.dur = x, y, size, value, dur
        self.prefix, self.suffix, self.caption, self.rgb, self.font, self.start = prefix, suffix, caption, rgb, font, start

    def bounds(self, res):
        r = self.size * 6
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def cues(self):
        return [("ticks", self.t_in, 0.6, {})]

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.3) * self.fade(t)
        if a <= 0:
            return
        u = ease_out_cubic(ramp(t, self.t_in, self.dur))
        v = int(round(self.start + (self.value - self.start) * u))
        txt = f"{self.prefix}{v:,}{self.suffix}"
        c.saveLayerAlpha(None, 255)
        tw = draw_text(c, res, txt, self.x, self.y, self.size, self.font, self.rgb, a, 0.03, "center")
        wp = skia.Paint(); wp.setBlendMode(skia.BlendMode.kDstOut)
        c.drawImageRect(res.wear(), skia.Rect.MakeXYWH(self.x - tw / 2 - 20, self.y - self.size, tw + 40, self.size * 1.15), SAMPLING, wp)
        c.restore()
        if self.caption:
            ca = ramp(t, self.t_in + self.dur * 0.6, 0.4) * self.fade(t)
            draw_text(c, res, self.caption, self.x, self.y + self.size * 0.42, self.size * 0.24, "cond", self.rgb, 0.85 * ca, 0.12, "center")


class PaperDoc(Item):
    """A typeset paper document drawn in code (a recreation): header lines, soft grey body rows (never
    filler words), and an optional block of real, legible text you can mark with a PenMark."""
    z = 12

    def __init__(self, x, y, w, h, rot=0.0, t_in=0.0, t_out=None, header=(), rows=18, sentence=None,
                 sentence_row=8, sentence_size=58, row_gap=None, seed=21, pin=True, z=None, exit_vec=None, row_start=0.3, sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.x, self.y, self.w, self.h, self.rot = x, y, w, h, rot
        self.header, self.rows, self.sentence, self.srow, self.ssize = header, rows, sentence, sentence_row, sentence_size
        self.row_gap = row_gap or (h * (0.92 - row_start)) / max(1, rows)
        self.row_start, self.pin, self.exit_vec = row_start, pin, exit_vec
        rng = np.random.default_rng(seed)
        self.lens = [rng.uniform(0.55, 0.97) for _ in range(rows)]
        self.sent_lines = []

    def bounds(self, res):
        r = max(self.w, self.h) * 0.8 + 300
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def cues(self):
        return [("pop", self.t_in, 0.8, {})]

    def wrap(self, res):
        if self.sentence and not self.sent_lines:
            line = ""; maxw = self.w * 0.8
            for wd in self.sentence.split():
                trial = (line + " " + wd).strip()
                if text_width(res, trial, self.ssize, "serif") > maxw and line:
                    self.sent_lines.append(line); line = wd
                else:
                    line = trial
            self.sent_lines.append(line)
        return self.sent_lines

    def line_pos(self, res, i):
        """(world point at the left of sentence line i, its width) for placing pen marks."""
        lines = self.wrap(res)
        y = -self.h / 2 + self.h * self.row_start + (self.srow + i) * self.row_gap
        return rot_point(self.x, self.y, -self.w * 0.4, y, self.rot), text_width(res, lines[i], self.ssize, "serif")

    def phrase_spans(self, res, phrase):
        """[(world centre, width)] of `phrase` in the sentence block, one span per wrapped line it covers:
        place one highlight per span (a phrase often wraps). y is the text's x-height middle."""
        lines = self.wrap(res)
        full = " ".join(lines)
        k = full.find(phrase)
        if k < 0:
            raise ValueError(f"{phrase!r} is not in the document text {full!r}")
        spans, pos = [], 0
        for i, ln in enumerate(lines):
            a, b = max(k, pos), min(k + len(phrase), pos + len(ln))
            if a < b:
                x0 = -self.w * 0.4 + text_width(res, ln[:a - pos], self.ssize, "serif")
                pw = text_width(res, ln[a - pos:b - pos].strip(), self.ssize, "serif")
                y = -self.h / 2 + self.h * self.row_start + (self.srow + i) * self.row_gap
                spans.append((rot_point(self.x, self.y, x0 + pw / 2, y, self.rot), pw))
            pos += len(ln) + 1
        return spans

    def phrase_pos(self, res, phrase):
        """(world centre, width) of the first span of `phrase`: for a circle or underline."""
        return self.phrase_spans(res, phrase)[0]

    def draw(self, c, res, t):
        s, a, lift = drop_anim(t, self.t_in)
        a *= self.fade(t)
        if a <= 0:
            return
        ox = oy = 0.0
        if self.exit_vec and self.t_out is not None:
            u = ease_in_out(ramp(t, self.t_out, 0.6)); ox, oy = self.exit_vec[0] * u, self.exit_vec[1] * u
        W, H = self.w, self.h
        c.save(); c.translate(self.x + ox, self.y + oy); c.rotate(self.rot + 3 * lift); c.scale(s, s)
        off = 18 + 70 * lift
        c.drawRect(skia.Rect.MakeXYWH(-W / 2 + off * 0.4, -H / 2 + off, W, H), paint((0, 0, 0), 0.55 * a, blur=22 + 50 * lift))
        paper_fill(c, res, skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), a, 1.0)
        y = -H / 2 + H * 0.09
        for txt, size, font in self.header:
            draw_text(c, res, txt, 0, y + size, size, font, INK, a, 0.08 if font == "mono" else 0.04, "center")
            y += size * 1.45
        lines = self.wrap(res) if self.sentence else []
        for i in range(self.rows):
            yy = -H / 2 + H * self.row_start + i * self.row_gap
            if lines and self.srow <= i < self.srow + len(lines):
                draw_text(c, res, lines[i - self.srow], -W * 0.4, yy + self.ssize * 0.3, self.ssize, "serif", INK, a)
                continue
            c.drawLine(-W * 0.4, yy, -W * 0.4 + W * 0.8 * self.lens[i], yy, paint((150, 140, 124), 0.55 * a, stroke=self.row_gap * 0.22))
        if self.pin:
            draw_pin(c, 0, -H / 2 + H * 0.035, r=max(26, 0.02 * W), a=a)
        c.restore()


class Card(Item):
    """A clean panel for explainers and product stories: rounded, flat colour, an optional accent bar,
    a title and a few short lines of real text. Rises into place with a soft shadow."""
    z = 12

    def __init__(self, x, y, w, h, t_in, title="", lines=(), rgb=(250, 248, 244), text_rgb=(34, 32, 30), accent=None,
                 rot=0.0, t_out=None, radius=36, title_size=None, body_size=None, z=None, sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.x, self.y, self.w, self.h, self.rot = x, y, w, h, rot
        self.title, self.lines, self.rgb, self.text_rgb, self.accent, self.radius = title, list(lines), rgb, text_rgb, accent, radius
        self.ts = title_size or h * 0.16
        self.bs = body_size or h * 0.085

    def bounds(self, res):
        r = max(self.w, self.h) * 0.8 + 300
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def cues(self):
        return [("pop", self.t_in, 0.6, {})]

    def draw(self, c, res, t):
        u = ease_out_back(ramp(t, self.t_in, 0.45), 1.2)
        a = ramp(t, self.t_in, 0.15) * self.fade(t)
        if a <= 0:
            return
        s = 0.92 + 0.08 * u
        W, H = self.w, self.h
        c.save(); c.translate(self.x, self.y + (1 - u) * 120); c.rotate(self.rot); c.scale(s, s)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), self.radius, self.radius)
        c.save(); c.translate(0, 26); c.drawRRect(rr, paint((0, 0, 0), 0.3 * a, blur=40)); c.restore()
        c.drawRRect(rr, paint(self.rgb, a))
        pad = W * 0.08
        if self.accent:
            c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
            c.drawRect(skia.Rect.MakeXYWH(-W / 2, -H / 2, W * 0.035, H), paint(self.accent, a))
            c.restore()
        y = -H / 2 + pad + self.ts * 0.85
        if self.title:
            draw_text(c, res, self.title, -W / 2 + pad, y, self.ts, "label", self.text_rgb, a, 0.0)
            y += self.ts * 0.55
        for i, ln in enumerate(self.lines):
            la = a * ramp(t, self.t_in + 0.25 + 0.12 * i, 0.3)
            y += self.bs * 1.45
            draw_text(c, res, ln, -W / 2 + pad, y, self.bs, "labelm", self.text_rgb, la * 0.85, 0.0)
        c.restore()


class Ledger(Item):
    """Closed ledger or case file drawn in code: cloth cover, leather spine and corners, paper label.
    Slams onto the board with a camera shake."""
    z = 20

    def __init__(self, x, y, w, rot=0.0, t_in=0.0, t_out=None, z=None, label="LEDGER", cloth=(44, 58, 46), sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.x, self.y, self.w, self.rot, self.label, self.cloth = x, y, w, rot, label, cloth

    def bounds(self, res):
        r = self.w * 1.4
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def cues(self):
        return [("impact", self.t_in + 0.3, 1.0, {})]

    def shakes(self):
        return [(self.t_in + 0.3, 18, 0.4)]

    def draw(self, c, res, t):
        u = ramp(t, self.t_in, 0.32)
        if u <= 0:
            return
        a = min(1, u * 4) * self.fade(t)
        s = 1 + 0.35 * (1 - ease_out_cubic(u))
        w = self.w; h = w * 1.32
        c.save(); c.translate(self.x, self.y); c.rotate(self.rot + 5 * (1 - u)); c.scale(s, s)
        off = 30 + 120 * (1 - u)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2 + off * 0.3, -h / 2 + off, w, h), paint((0, 0, 0), 0.6 * a, blur=30 + 60 * (1 - u)))
        c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 10, -h / 2 + 8, w - 4, h - 4), paint((214, 204, 184), a))
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w - 14, h - 12), paint(self.cloth, a))
        paper_fill(c, res, skia.Rect.MakeXYWH(-w / 2, -h / 2, w - 14, h - 12), 0.5 * a, 0.5, skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w * 0.17, h - 12), paint((74, 40, 26), a))
        for k in (0.12, 0.26, 0.74, 0.88):
            c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2 + h * k, w * 0.17, h * 0.018), paint((150, 112, 60), 0.8 * a))
        cs = w * 0.2
        for sy in (-1, 1):
            p = skia.Path(); cx = w / 2 - 14; cy = sy * (h / 2) - (12 if sy > 0 else 0)
            p.moveTo(cx, cy); p.lineTo(cx - cs, cy); p.lineTo(cx, cy - sy * cs); p.close()
            c.drawPath(p, paint((74, 40, 26), a))
        lw, lh = w * 0.42, w * 0.2
        lx, ly = w * 0.06, -h * 0.22
        paper_fill(c, res, skia.Rect.MakeXYWH(lx - lw / 2, ly - lh / 2, lw, lh), a, 0.6)
        c.drawRect(skia.Rect.MakeXYWH(lx - lw / 2 + 10, ly - lh / 2 + 10, lw - 20, lh - 20), paint(INK, 0.7 * a, stroke=4))
        draw_text(c, res, self.label, lx, ly + lh * 0.14, lh * 0.36 * min(1, 6 / max(1, len(self.label))), "serif", INK, a, 0.2, "center")
        c.restore()


class OpenLedger(Item):
    """Open ledger, two-page spread: ruled columns, grey ink rows and one legible handwritten entry
    (a recreation: credit it as one). entry_mark() gives where to circle the last words."""
    z = 22

    def __init__(self, x, y, w, rot=0.0, t_in=0.0, entry="", entry_row=9, t_out=None, seed=31, sfx=True):
        super().__init__(t_in, t_out, None, sfx)
        self.x, self.y, self.w, self.rot, self.entry, self.erow = x, y, w, rot, entry, entry_row
        self.h = w * 0.66; self.rows = 16
        rng = np.random.default_rng(seed)
        self.scrib = [(rng.uniform(0.05, 0.12), rng.uniform(0.25, 0.62), rng.uniform(0.72, 0.9)) for _ in range(self.rows)]

    def bounds(self, res):
        r = self.w * 0.8
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def cues(self):
        return [("pop", self.t_in, 0.9, {})]

    def row_y(self, i):
        return -self.h / 2 + self.h * 0.16 + i * (self.h * 0.78 / self.rows)

    def entry_mark(self, res, words):
        """(world centre of the trailing `words` of the entry, their width) for a pen circle."""
        size = self.h * 0.072
        x0 = self.w / 2 * 0.06; y = self.row_y(self.erow) + size * 0.1
        full = text_width(res, self.entry, size, "hand")
        tail = text_width(res, words, size, "hand")
        return rot_point(self.x, self.y, x0 + full - tail / 2, y - size * 0.25, self.rot), tail

    def draw(self, c, res, t):
        u = ramp(t, self.t_in, 0.45)
        if u <= 0:
            return
        a = min(1, u * 3) * self.fade(t)
        s = 1 + 0.12 * (1 - ease_out_cubic(u))
        W, H = self.w, self.h
        c.save(); c.translate(self.x, self.y); c.rotate(self.rot); c.scale(s, s)
        c.drawRect(skia.Rect.MakeXYWH(-W / 2 + 20, -H / 2 + 40, W, H), paint((0, 0, 0), 0.6 * a, blur=40))
        c.drawRect(skia.Rect.MakeXYWH(-W / 2 - 30, -H / 2 - 20, W + 60, H + 40), paint((44, 58, 46), a))
        paper_fill(c, res, skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), a, 0.8)
        c.drawRect(skia.Rect.MakeXYWH(-W / 2, -H / 2, W, H), paint((214, 200, 170), 0.18 * a))
        g = skia.GradientShader.MakeLinear([skia.Point(-W * 0.06, 0), skia.Point(W * 0.06, 0)],
                                           [skia.Color(0, 0, 0, 0), skia.Color(40, 30, 20, int(90 * a)), skia.Color(0, 0, 0, 0)])
        gp = skia.Paint(); gp.setShader(g); c.drawRect(skia.Rect.MakeXYWH(-W * 0.06, -H / 2, W * 0.12, H), gp)
        for side in (-1, 1):
            px0 = -W / 2 if side < 0 else 0
            pw = W / 2
            for i in range(self.rows + 1):
                yy = self.row_y(i) + H * 0.02
                c.drawLine(px0 + pw * 0.05, yy, px0 + pw * 0.95, yy, paint((120, 140, 160), 0.35 * a, stroke=3))
            for fx in (0.17, 0.66, 0.82):
                c.drawLine(px0 + pw * fx, -H / 2 + H * 0.1, px0 + pw * fx, H / 2 - H * 0.04, paint((170, 60, 50), 0.45 * a, stroke=3))
            for i in range(self.rows):
                if side > 0 and i == self.erow:
                    continue
                yy = self.row_y(i); d0, d1, d2 = self.scrib[i]
                c.drawLine(px0 + pw * d0, yy, px0 + pw * (d0 + 0.07), yy, paint((70, 60, 50), 0.35 * a, stroke=7))
                c.drawLine(px0 + pw * 0.2, yy, px0 + pw * d1, yy, paint((70, 60, 50), 0.32 * a, stroke=7))
                c.drawLine(px0 + pw * 0.69, yy, px0 + pw * d2, yy, paint((70, 60, 50), 0.32 * a, stroke=7))
        size = H * 0.072
        draw_text(c, res, self.entry, W / 2 * 0.06, self.row_y(self.erow) + size * 0.1, size, "hand", (22, 20, 40), a)
        c.restore()


class FilmFrame(Item):
    """Film-strip bands with sprocket holes clamped around a print (for anything that became a movie)."""
    z = 15

    def __init__(self, pr, t_in, t_out=None, sfx=True):
        super().__init__(t_in, t_out, None, sfx)
        self.pr = pr

    def bounds(self, res):
        W, H = self.pr.outer(res); r = max(W, H) * 0.9
        return skia.Rect.MakeLTRB(self.pr.x - r, self.pr.y - r, self.pr.x + r, self.pr.y + r)

    def cues(self):
        return [("click", self.t_in, 0.6, {})]

    def draw(self, c, res, t):
        u = ease_out_cubic(ramp(t, self.t_in, 0.45)); a = u * self.fade(t)
        if a <= 0:
            return
        W, H = self.pr.outer(res); band = H * 0.16
        c.save(); c.translate(self.pr.x, self.pr.y); c.rotate(self.pr.rot)
        for sgn in (-1, 1):
            y = sgn * (H / 2 + band / 2 - band * 0.25) + sgn * (1 - u) * band * 1.5
            r = skia.Rect.MakeXYWH(-W / 2 - band * 0.3, y - band / 2, W + band * 0.6, band)
            c.drawRect(r.makeOffset(10, 18), paint((0, 0, 0), 0.5 * a, blur=14))
            c.drawRect(r, paint((18, 15, 13), 0.96 * a))
            n = int(W / (band * 0.62))
            for i in range(n):
                hx = -W / 2 + (i + 0.5) * W / n
                c.drawRoundRect(skia.Rect.MakeXYWH(hx - band * 0.14, y - band * 0.18, band * 0.28, band * 0.36), band * 0.06, band * 0.06,
                                paint((196, 186, 168), 0.9 * a))
        c.restore()


class Holes(Item):
    """Holes punched into a print at given times (dark core, torn light rim, short cracks).
    pts are fractional (fx, fy) positions inside the print's image."""
    z = 16

    def __init__(self, pr, pts, times, seed=5, sound="snip", sfx=True):
        super().__init__(min(times), None, None, sfx)
        self.pr, self.pts, self.times, self.sound = pr, pts, times, sound
        rng = np.random.default_rng(seed)
        self.cracks = [[(rng.uniform(0, 6.28), rng.uniform(0.6, 1.0)) for _ in range(5)] for _ in pts]

    def bounds(self, res):
        r = max(self.pr.size(res))
        return skia.Rect.MakeLTRB(self.pr.x - r, self.pr.y - r, self.pr.x + r, self.pr.y + r)

    def cues(self):
        return [(self.sound, tt, 0.7, {}) for tt in self.times]

    def draw(self, c, res, t):
        a = self.fade(t)
        w, h = self.pr.size(res)
        c.save(); c.translate(self.pr.x, self.pr.y); c.rotate(self.pr.rot)
        r0 = w * 0.012
        for (fx, fy), ti, cr in zip(self.pts, self.times, self.cracks):
            if ramp(t, ti, 0.06) <= 0:
                continue
            x, y = (fx - 0.5) * w, (fy - 0.5) * h
            for ang, ln in cr:
                c.drawLine(x, y, x + math.cos(ang) * r0 * 3.2 * ln, y + math.sin(ang) * r0 * 3.2 * ln, paint((230, 222, 205), 0.55 * a, stroke=r0 * 0.18))
            c.drawCircle(x, y, r0 * 1.35, paint((235, 228, 210), 0.7 * a))
            c.drawCircle(x, y, r0, paint((8, 6, 5), a))
        c.restore()


class DotField(Item):
    """Dots popping up over an area between t0 and t1 (bars, branches, outbreaks, stores): give world points."""
    z = 8

    def __init__(self, points, t0, t1, seed=11, t_out=None, rgb=(176, 28, 22), r=30, sfx=True):
        super().__init__(t0, t_out, None, sfx)
        rng = np.random.default_rng(seed)
        self.pts, self.rgb, self.r = list(points), rgb, r
        self.times = sorted(rng.uniform(t0, t1, len(self.pts)))
        x = [p[0] for p in self.pts]; y = [p[1] for p in self.pts]
        self.box = skia.Rect.MakeLTRB(min(x) - 200, min(y) - 200, max(x) + 200, max(y) + 200)

    def bounds(self, res):
        return self.box

    def cues(self):
        return [("shimmer", self.t_in, 0.5, {})]

    def draw(self, c, res, t):
        a = self.fade(t)
        for (x, y), ti in zip(self.pts, self.times):
            u = ramp(t, ti, 0.25)
            if u <= 0:
                continue
            r = self.r * ease_out_back(u)
            c.drawCircle(x, y, r * 2.2, paint(self.rgb, 0.18 * a, blur=20))
            c.drawCircle(x, y, r, paint(self.rgb, 0.95 * a))


# ---------------------------------------------------------------- maps
MAP_LOOKS = {
    # teal water, pale relief land, light borders, dark neighbours (modern explainer map)
    "explainer": dict(sheet=(236, 233, 226), water=TEAL, land=(188, 184, 176), border=(178, 170, 158), relief=0.24,
                      neighbor=(222, 218, 210), neighbor_line=(170, 162, 150), dark=(84, 80, 77), dark_line=(60, 58, 56), frame=(60, 58, 56)),
    # parchment sheet, tan land, brown borders (old printed map)
    "period": dict(sheet=(232, 224, 204), water=(196, 206, 196), land=(222, 206, 172), border=(128, 96, 64), relief=0.18,
                   neighbor=(214, 204, 182), neighbor_line=(150, 124, 92), dark=(176, 160, 132), dark_line=(120, 96, 70), frame=(110, 86, 60)),
}


def _rings_path(rings, w):
    p = skia.Path()
    for r_ in rings:
        p.moveTo(*w(r_[0]))
        for pt in r_[1:]:
            p.lineTo(*w(pt))
        p.close()
    return p


class GeoMap(Cached, Item):
    """A printed map sheet from make_map.py output: regions (states, countries) and neighbours.
    K = world px per projection unit (about one earth radius); origin = where unit (0, 0) lands."""
    z = 0

    def __init__(self, data, K, origin=(0, 0), look="explainer", t_in=-1, margin=0.03, relief_tile=9000):
        super().__init__(t_in)
        self.K, self.ox, self.oy, self.relief_tile = K, *origin, relief_tile
        self.look = MAP_LOOKS[look] if isinstance(look, str) else look
        self.data = data
        regions = data["regions"]
        xs = [p[0] for rings in regions.values() for r in rings for p in r]
        ys = [p[1] for rings in regions.values() for r in rings for p in r]
        b = data.get("frame") or [min(xs) - margin, min(ys) - margin * 1.4, max(xs) + margin, max(ys) + margin]
        self.frame = b
        self.region_paths = {n: _rings_path(r, self.w) for n, r in regions.items()}
        self.path = skia.Path()
        for p in self.region_paths.values():
            self.path.addPath(p)
        self.nb_paths = {n: _rings_path(r, self.w) for n, r in data.get("neighbors", {}).items()}
        self.dark = set(data.get("dark", []))

    def w(self, p):
        return self.ox + p[0] * self.K, self.oy + p[1] * self.K

    def place(self, name):
        """World position of a named place from map.json."""
        if name not in self.data.get("places", {}):
            raise KeyError(f"place {name!r} not in the map; add it under places in map.json and rerun make_map.py")
        return self.w(self.data["places"][name])

    def sheet(self):
        x0, y0 = self.w(self.frame[:2]); x1, y1 = self.w(self.frame[2:])
        return skia.Rect.MakeLTRB(x0, y0, x1, y1)

    def bounds(self, res):
        return self.sheet().makeOutset(500, 500)

    def draw(self, c, res, t):
        self.cached_draw(c, res, self.sheet().makeOutset(400, 400), self._draw)

    def _draw(self, c, res):
        L = self.look
        r = self.sheet()
        c.drawRect(r.makeOffset(30, 50), paint((0, 0, 0), 0.6, blur=60))
        c.drawRect(r, paint(L["sheet"]))
        inner = r.makeInset(70, 70)
        c.save(); c.clipRect(inner)
        c.drawRect(inner, paint(L["water"]))
        paper_fill(c, res, inner, 0.22, 2.0, skia.BlendMode.kMultiply)
        for name, path in self.nb_paths.items():
            dark = name in self.dark
            c.drawPath(path, paint(L["dark"] if dark else L["neighbor"], 0.96))
            c.drawPath(path, paint(L["dark_line"] if dark else L["neighbor_line"], 0.7, stroke=4))
        c.drawPath(self.path, paint(L["land"]))
        c.save(); c.clipPath(self.path, skia.ClipOp.kIntersect, True)
        rp = skia.Paint(AntiAlias=True); rp.setBlendMode(skia.BlendMode.kOverlay); rp.setAlphaf(L["relief"])
        # tiled at a fixed world size, so the terrain grain looks the same whatever the map scale
        tile_image(c, res.image("relief.png", 1024), inner, self.relief_tile, rp)
        c.restore()
        c.drawPath(self.path, paint(L["border"], 0.95, stroke=5))
        c.restore()
        c.drawRect(inner, paint(L["frame"], 0.5, stroke=4))


class RegionFill(Item):
    """Fill one or more map regions; can change colour later (active RUST -> visited MUSTARD)."""
    z = 1

    def __init__(self, geomap, names, rgb, t_in, t_out=None, alpha=0.95, to_rgb=None, t_change=None, sfx=True):
        super().__init__(t_in, t_out, None, sfx)
        self.m, self.names, self.rgb, self.alpha, self.to_rgb, self.t_change = geomap, names, rgb, alpha, to_rgb, t_change
        missing = [n for n in names if n not in geomap.region_paths]
        if missing:
            raise KeyError(f"regions {missing} not in the map (have e.g. {sorted(geomap.region_paths)[:8]})")
        b = None
        for n in names:
            r = geomap.region_paths[n].getBounds()
            b = r if b is None else skia.Rect.MakeLTRB(min(b.left(), r.left()), min(b.top(), r.top()), max(b.right(), r.right()), max(b.bottom(), r.bottom()))
        self.box = b.makeOutset(300, 300)

    def bounds(self, res):
        return self.box

    def draw(self, c, res, t):
        a = ease_in_out(ramp(t, self.t_in, 0.6)) * self.fade(t)
        if a <= 0:
            return
        rgb = self.rgb
        if self.to_rgb and self.t_change is not None:
            u = ease_in_out(ramp(t, self.t_change, 0.7))
            rgb = tuple(self.rgb[i] + (self.to_rgb[i] - self.rgb[i]) * u for i in range(3))
        for n in self.names:
            p = self.m.region_paths[n]
            c.drawPath(p, paint(rgb, self.alpha * a))
            c.drawPath(p, paint((250, 246, 238), 0.55 * a, stroke=6))


class Route(Item):
    """White travel line arcing between two points, drawn on with a small leading dot."""
    z = 28

    def __init__(self, a, b, t_in, dur=1.2, bend=0.16, width=10, t_out=None, rgb=(252, 250, 245), sfx=True):
        super().__init__(t_in, t_out, None, sfx)
        (x0, y0), (x1, y1) = a, b
        d = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / max(d, 1), (x1 - x0) / max(d, 1)
        self.p = skia.Path(); self.p.moveTo(x0, y0)
        self.p.quadTo((x0 + x1) / 2 + nx * d * bend, (y0 + y1) / 2 + ny * d * bend, x1, y1)
        self.dur, self.wd, self.rgb = dur, width, rgb
        self.box = self.p.getBounds().makeOutset(300, 300)

    def bounds(self, res):
        return self.box

    def cues(self):
        return [("whoosh", self.t_in, 0.4, {})]

    def draw(self, c, res, t):
        u = ease_in_out(ramp(t, self.t_in, self.dur)); a = self.fade(t)
        if u <= 0 or a <= 0:
            return
        seg = partial_path(self.p, u)
        c.save(); c.translate(6, 12); c.drawPath(seg, paint((0, 0, 0), 0.35 * a, stroke=self.wd, blur=5)); c.restore()
        c.drawPath(seg, paint(self.rgb, 0.95 * a, stroke=self.wd))
        if u < 1:
            pm = skia.PathMeasure(self.p, False); pos = pm.getPosTan(pm.getLength() * u)
            if pos:
                c.drawCircle(pos[0].x(), pos[0].y(), self.wd * 2.2, paint(self.rgb, a))


class XMarker(Item):
    """Explainer map marker: white ring with a red centre, a thin leader line, a bold label that types on."""
    z = 32

    def __init__(self, x, y, label=None, t_in=0.0, t_out=None, side="right", size=1.0, label_size=90,
                 label_rgb=(252, 250, 245), shadow=True, z=None, sfx=True):
        super().__init__(t_in, t_out, z, sfx)
        self.x, self.y, self.label, self.side, self.k, self.ls = x, y, label, side, size, label_size
        self.lrgb, self.shadow = label_rgb, shadow

    def bounds(self, res):
        L = len(self.label or "") * self.ls * self.k * 0.8 + 500 * self.k
        return skia.Rect.MakeLTRB(self.x - L, self.y - 400 * self.k, self.x + L, self.y + 400 * self.k)

    def cues(self):
        return [("pop", self.t_in, 0.6, {})]

    def draw(self, c, res, t):
        u = ramp(t, self.t_in, 0.35); a = u * self.fade(t)
        if a <= 0:
            return
        k = self.k; e = ease_out_back(u)
        c.drawCircle(self.x + 4 * k, self.y + 8 * k, 30 * k * e, paint((0, 0, 0), 0.35 * a, blur=8 * k))
        c.drawCircle(self.x, self.y, 26 * k * e, paint((252, 250, 245), a, stroke=9 * k))
        c.drawCircle(self.x, self.y, 13 * k * e, paint((200, 28, 24), a))
        if not self.label:
            return
        s = 1 if self.side == "right" else -1
        lu = ease_out_cubic(ramp(t, self.t_in + 0.15, 0.35))
        p = skia.Path(); x0, y0 = self.x + s * 34 * k, self.y
        p.moveTo(x0, y0); p.quadTo(x0 + s * 70 * k, y0 - 4 * k, x0 + s * 150 * k, y0 - 46 * k)
        c.drawPath(partial_path(p, lu), paint(self.lrgb, 0.9 * a, stroke=5 * k))
        n = len(self.label) * ramp(t, self.t_in + 0.3, 0.05 * len(self.label) + 0.1)
        tx = x0 + s * 165 * k; ty = y0 - 46 * k + self.ls * k * 0.36
        if self.shadow:
            c.save(); c.translate(4 * k, 7 * k)
            draw_text(c, res, self.label, tx, ty, self.ls * k, "label", (0, 0, 0), 0.5 * a, 0.04, "left" if s > 0 else "right", reveal=n + 0.999)
            c.restore()
        draw_text(c, res, self.label, tx, ty, self.ls * k, "label", self.lrgb, a, 0.04, "left" if s > 0 else "right", reveal=n + 0.999)


# ---------------------------------------------------------------- film
class Film:
    """Everything that happens: items, camera keys, spotlight keys, shakes, sound cues and the look."""

    def __init__(self, duration, fps=30, look="wall"):
        self.duration, self.fps = duration, fps
        self.look = dict(LOOKS[look]) if isinstance(look, str) else dict(look)
        self.board = Board(self.look["board"])
        self.items: list[Item] = [self.board]
        self.cam_keys, self.focus_keys, self.shakes, self.sfx = [], [], [], []
        self.room_tone = []             # [[start, end]] spans of quiet room tone under everything (optional)
        self.fade_in, self.fade_out = 0.9, 2.2
        self.auto_cues, self.auto_whoosh = True, True
        self._cam = self._foc = None

    def add(self, item):
        self.items.append(item)
        for sh in item.shakes():
            self.shake(*sh)
        return item

    def cam(self, t, x, y, zoom, rot=0.0):
        """Camera key: look at world (x, y) at time t. zoom 1 = 4K pixels 1:1; 0.15 shows a whole wall."""
        self.cam_keys.append((t, x, y, zoom, rot)); self._cam = None

    def focus(self, t, x, y, radius, strength=0.55):
        """Spotlight key: everything outside `radius` of (x, y) dims by `strength` (the hero rule)."""
        self.focus_keys.append((t, x, y, radius, strength)); self._foc = None

    def shot(self, t, x, y, zoom, rot=0.0, radius=None, strength=0.55):
        """Camera key and spotlight key on the same point (radius defaults to about 60% of the frame):
        keeps the light on what the camera looks at. Set them apart only on purpose."""
        self.cam(t, x, y, zoom, rot)
        self.focus(t, x, y, radius or 1600 / zoom, strength)

    def shake(self, t, amp=14.0, dur=0.35):
        self.shakes.append((t, amp, dur))

    def cue(self, kind, t, gain=1.0, **kw):
        """A sound effect at time t (see build_sfx.py for the kinds)."""
        self.sfx.append({"type": kind, "t": round(t, 3), "gain": gain, **kw})

    def _build(self):
        if not self.cam_keys:
            raise SystemExit("the film has no camera keys: add film.cam(t, x, y, zoom) calls")
        k = sorted(self.cam_keys)
        self._cam = [Spline([(a[0], a[i]) for a in k]) for i in (1, 2)] + \
                    [Spline([(a[0], math.log(a[3])) for a in k]), Spline([(a[0], a[4]) for a in k])]
        f = sorted(self.focus_keys)
        self._foc = [Spline([(a[0], a[i]) for a in f]) for i in (1, 2, 3, 4)] if f else None

    def camera(self, t):
        if self._cam is None:
            self._build()
        x, y, lz, r = (s(t) for s in self._cam)
        z = math.exp(lz)
        # handheld: slow incommensurate wobble in 4K screen px, converted to world units
        hx = 7 * math.sin(t * 0.83 + 1.3) + 4 * math.sin(t * 1.71 + 0.2) + 2.5 * math.sin(t * 3.3)
        hy = 6 * math.sin(t * 0.67 + 2.1) + 3.5 * math.sin(t * 1.93 + 1.1) + 2 * math.sin(t * 2.9 + 0.5)
        hr = 0.12 * math.sin(t * 0.51 + 0.4) + 0.05 * math.sin(t * 1.37)
        for (ts, amp, dur) in self.shakes:
            if ts <= t < ts + dur:
                u = (t - ts) / dur; e = amp * (1 - u) ** 2
                hx += e * math.sin(u * 60); hy += e * math.cos(u * 47)
        return x + hx / z, y + hy / z, z, r + hr

    def focus_at(self, t):
        if self._cam is None:
            self._build()
        return tuple(s(t) for s in self._foc) if self._foc else None

    def screen_speed(self, t):
        """Approximate camera speed in 4K screen px per frame (pan + zoom + roll)."""
        dt = 1 / self.fps
        a = self.camera(t); b = self.camera(t + dt)
        return (math.hypot(b[0] - a[0], b[1] - a[1]) * a[2] + abs(math.log(b[2] / a[2])) * 1920
                + abs(b[3] - a[3]) * math.pi / 180 * 1920)

    def all_cues(self):
        """Explicit cues, plus each item's own cues and a whoosh on every fast camera move (unless the
        scene placed a cue of the same kind within 0.15 s, or the item has sfx=False)."""
        cues = list(self.sfx)
        def near(kind, t):
            return any(c["type"] == kind and abs(c["t"] - t) < 0.15 for c in cues)
        if self.auto_cues:
            for it in self.items:
                if not it.sfx:
                    continue
                for kind, t, gain, kw in it.cues():
                    if 0 <= t <= self.duration and not near(kind, t):
                        cues.append({"type": kind, "t": round(t, 3), "gain": gain, **kw})
        if self.auto_whoosh and self.cam_keys:
            n = int(self.duration * self.fps); last = -9.0; i = 0
            while i < n:
                t = i / self.fps
                if self.screen_speed(t) > 90 and t - last > 1.4:
                    j = i
                    peak = 0.0
                    while j < n and self.screen_speed(j / self.fps) > 60:
                        peak = max(peak, self.screen_speed(j / self.fps)); j += 1
                    if not near("whoosh", t):
                        cues.append({"type": "whoosh", "t": round(max(0, t - 0.1), 3), "gain": round(min(0.8, 0.3 + peak / 600), 2)})
                    last = t; i = j
                i += 1
        return sorted(cues, key=lambda c: c["t"])


class Renderer:
    def __init__(self, film: Film, width=1920, height=1080, doc: Doc | None = None):
        self.film, self.W, self.H = film, width, height
        self.s = width / 3840.0
        self.res = Res(self.s, doc.prep if doc else None, (doc.dir / "fonts") if doc else None)
        self.surface = skia.Surface.MakeRaster(skia.ImageInfo.Make(width, height, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType))
        L = film.look
        yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
        d = np.sqrt(((xx - width / 2) / (width / 2)) ** 2 + ((yy - height / 2) / (height / 2)) ** 2) / math.sqrt(2)
        self.vignette = (1 - L["vignette"] * np.clip(d - 0.28, 0, 1) ** 1.5 * 1.9).clip(0.22, 1)[..., None].astype(np.float32)
        self.items = sorted(film.items, key=lambda i: i.z)

    def draw_world(self, t):
        f = self.film
        cx, cy, z, rot = f.camera(t)
        k = z * self.s
        self.res.screen_scale = k
        hw, hh = self.W / 2 / k * 1.25, self.H / 2 / k * 1.25
        self.res.view = view = skia.Rect.MakeLTRB(cx - hw, cy - hh, cx + hw, cy + hh)
        with self.surface as c:
            c.clear(color(f.look["bg"]))
            c.save()
            c.translate(self.W / 2, self.H / 2); c.scale(k, k); c.rotate(rot); c.translate(-cx, -cy)
            for it in self.items:
                if it.visible(t):
                    b = it.bounds(self.res)
                    if b is None or skia.Rect.Intersects(b, view):
                        it.draw(c, self.res, t)
            foc = f.focus_at(t)
            if foc:
                fx, fy, fr, fs = foc
                dr, dg, db = f.look.get("dim", (6, 4, 3))
                g = skia.GradientShader.MakeRadial(skia.Point(fx, fy), max(10, fr * 2.4),
                                                   [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(dr, dg, db, int(255 * clamp(fs))),
                                                    skia.Color(dr, dg, db, int(255 * min(0.92, fs + 0.25)))], [0.0, 0.3, 0.68, 1.0])
                p = skia.Paint(); p.setShader(g)
                c.drawRect(skia.Rect.MakeXYWH(cx - 60000, cy - 60000, 120000, 120000), p)
            c.restore()
        return self.surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[..., :3]

    def frame(self, n):
        f = self.film; t = n / f.fps
        sp = f.screen_speed(t) * self.s
        k = int(clamp(math.ceil(sp / (6 * max(self.s, 0.5))), 1, 8))   # motion-blur sub-frames
        if k == 1:
            img = self.draw_world(t).astype(np.float32)
        else:
            acc = np.zeros((self.H, self.W, 3), np.float32)
            for i in range(k):
                acc += self.draw_world(t + (i / k - 0.5) * 0.5 / f.fps)
            img = acc / k
        return self.post(img, n)

    def post(self, img, n):
        """Film finish: glow, S-curve, grade, vignette, grain, fades."""
        L = self.film.look
        if not hasattr(self, "_grain"):
            # half-resolution grain that changes every 2nd frame: reads as film grain and survives
            # re-encoding (full-resolution per-frame noise made a 38 s clip 625 MB)
            rng = np.random.default_rng(99)
            self._grain = [Image.fromarray(np.clip(128 + rng.standard_normal((self.H // 2, self.W // 2)) * 42, 0, 255).astype(np.uint8))
                           for _ in range(10)]
            self._tint = (self.vignette * np.array(L["grade"], np.float32)).astype(np.float32)
        u8 = img.astype(np.uint8) if img.dtype != np.uint8 else img
        f = u8.astype(np.float32); f *= 1 / 255.0
        if L["glow"] > 0:
            small = Image.fromarray(u8).reduce(8)
            hi = np.asarray(small, np.float32) * (1.6 / 255.0) - 0.62 * 1.6
            np.clip(hi, 0, 1, out=hi)
            hi = Image.fromarray((hi * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)).resize((self.W, self.H), Image.BILINEAR)
            f += np.asarray(hi, np.float32) * (L["glow"] / 255.0)
            np.clip(f, 0, 1, out=f)
        cv = L["curve"]
        f *= (1 - cv) + cv * f * (3 - 2 * f)
        f *= self._tint
        tt = n / self.film.fps
        if self.film.fade_in > 0 and tt < self.film.fade_in:
            f *= ease_in_out(tt / self.film.fade_in)
        fo = self.film.fade_out
        if fo > 0 and tt > self.film.duration - fo:
            f *= 1 - ease_in_out((tt - (self.film.duration - fo)) / fo)
        if L["grain"] > 0:
            g = np.asarray(self._grain[((n // 2) * 7) % len(self._grain)].resize((self.W, self.H), Image.BILINEAR), np.float32) - 128.0
            f += g[..., None] * (L["grain"] / 42.0)
        np.clip(f, 0, 1, out=f)
        f *= 255
        return f.astype(np.uint8)
