"""Burned-in caption styles, chunked from the voiceover timing. Used by burn_captions.py.

Captions are drawn in screen space on their own layer after the film finish, so they stay crisp.
Word times come from each line's letter share (the same estimate the scene uses for hits).

Styles:
  highlighter  condensed caps on a dark band, the current word swiped in yellow (grunge newsprint)
  clean        sentence case with a soft shadow over a bottom gradient (classic documentary subtitle)
  paper        typewriter text typing onto a torn paper strip
  redbar       white condensed caps on a red bar (matches name labels)
"""
import re

import numpy as np
import skia

from engine import HILITE, Res, ease_out_cubic, paint, ramp, text_width, draw_text

MAX_WORDS = {"highlighter": 6, "clean": 9, "paper": 8, "redbar": 5}


def words_with_times(seg):
    """[(word as displayed, start time)] for one line: display text, spoken-text timing."""
    disp = seg["caption"].replace('"', "").split()
    lens = []
    for w in disp:
        letters = len(re.sub(r"[^A-Za-z]", "", w))
        if re.search(r"\d", w):                      # 1929 is long when spoken ("nineteen twenty-nine")
            letters = max(letters, 6 * len(re.sub(r"[^0-9]", "", w)) // 2 + 4)
        lens.append(max(1, letters))
    s = sum(lens); acc = 0; out = []
    dur = seg["end"] - seg["start"]
    for w, l in zip(disp, lens):
        out.append((w, seg["start"] + dur * acc / s)); acc += l
    return out


def chunks_for(timing, style):
    """[{'words': [(w, t)], 't0', 't1'}], breaking at punctuation where possible."""
    mx = MAX_WORDS[style]
    out = []
    for seg in timing["segments"]:
        ws = words_with_times(seg)
        cur, line = [], []
        for i, (w, t) in enumerate(ws):
            cur.append((w, t))
            if len(cur) >= mx or (w[-1] in ".,?!;:" and len(cur) >= max(2, mx // 2)) or i == len(ws) - 1:
                line.append({"words": cur, "t0": cur[0][1]}); cur = []
        for a, b in zip(line, line[1:]):
            a["t1"] = b["t0"]
        line[-1]["t1"] = seg["end"] + 0.25
        out += line
    return out


class Captions:
    def __init__(self, style, width, height, timing, fonts_dir=None):
        self.style, self.W, self.H = style, width, height
        self.k = width / 1920.0
        self.res = Res(width / 3840.0, None, fonts_dir)
        self.chunks = chunks_for(timing, style)
        self.surface = skia.Surface.MakeRaster(skia.ImageInfo.Make(width, height, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType))

    def active(self, t):
        for c in self.chunks:
            if c["t0"] - 0.05 <= t < c["t1"]:
                return c
        return None

    def layer(self, t):
        """Premultiplied RGBA caption layer for time t, or None."""
        c = self.active(t)
        if c is None:
            return None
        with self.surface as cv:
            cv.clear(skia.Color(0, 0, 0, 0))
            getattr(self, "_" + self.style)(cv, c, t)
        return self.surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    def _text(self, c, upper=False):
        txt = " ".join(w for w, _ in c["words"])
        return txt.upper() if upper else txt

    def _highlighter(self, cv, c, t):
        k = self.k; size = 66 * k; y = self.H * 0.897; f = "cond"
        words = [w.upper() for w, _ in c["words"]]
        gap = size * 0.28
        widths = [text_width(self.res, w, size, f, 0.03) for w in words]
        total = sum(widths) + gap * (len(words) - 1)
        x = self.W / 2 - total / 2
        a = ramp(t, c["t0"] - 0.05, 0.12)
        cur = max(i for i, (_, wt) in enumerate(c["words"]) if wt <= t + 0.02) if t >= c["words"][0][1] else 0
        pad = 26 * k
        cv.drawRoundRect(skia.Rect.MakeXYWH(x - pad, y - size * 0.95, total + 2 * pad, size * 1.25), 6 * k, 6 * k, paint((10, 9, 8), 0.62 * a))
        for i, (w, wd) in enumerate(zip(words, widths)):
            if i == cur:
                # white word underneath; the yellow swipe reveals it in black only where the swipe has reached
                u = ease_out_cubic(ramp(t, c["words"][i][1], 0.12))
                box = skia.Rect.MakeXYWH(x - 10 * k, y - size * 0.78, (wd + 20 * k) * u, size * 0.92)
                draw_text(cv, self.res, w, x, y, size, f, (250, 247, 240), a, 0.03)
                cv.drawRect(box, paint(HILITE, 0.95 * a))
                cv.save(); cv.clipRect(box)
                draw_text(cv, self.res, w, x, y, size, f, (18, 16, 14), a, 0.03)
                cv.restore()
            else:
                cv.save(); cv.translate(3 * k, 4 * k)
                draw_text(cv, self.res, w, x, y, size, f, (0, 0, 0), 0.6 * a, 0.03)
                cv.restore()
                draw_text(cv, self.res, w, x, y, size, f, (250, 247, 240), a, 0.03)
            x += wd + gap

    def _clean(self, cv, c, t):
        k = self.k; size = 52 * k; f = "labelm"
        txt = self._text(c)
        a = ramp(t, c["t0"] - 0.05, 0.15) * (1 - ramp(t, c["t1"] - 0.12, 0.12))
        g = skia.GradientShader.MakeLinear([skia.Point(0, self.H * 0.68), skia.Point(0, self.H)], [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, int(190 * a))])
        gp = skia.Paint(); gp.setShader(g); cv.drawRect(skia.Rect.MakeXYWH(0, self.H * 0.68, self.W, self.H * 0.32), gp)
        lines = [txt]
        if text_width(self.res, txt, size, f) > self.W * 0.7:
            ws = txt.split(); half = len(ws) // 2 + (len(ws) % 2)
            lines = [" ".join(ws[:half]), " ".join(ws[half:])]
        y0 = self.H * 0.885 - (len(lines) - 1) * size * 1.25
        for i, ln in enumerate(lines):
            y = y0 + i * size * 1.25
            cv.save(); cv.translate(0, 3 * k)
            tw = text_width(self.res, ln, size, f)
            cv.drawString(ln, self.W / 2 - tw / 2, y, self.res.font(f, size), paint((0, 0, 0), 0.85 * a, blur=6 * k))
            cv.restore()
            draw_text(cv, self.res, ln, self.W / 2, y, size, f, (252, 250, 245), a, 0.0, "center")

    def _paper(self, cv, c, t):
        k = self.k; size = 42 * k; f = "mono"
        txt = self._text(c)
        tw = text_width(self.res, txt, size, f, 0.02)
        a = ramp(t, c["t0"] - 0.05, 0.12)
        W, H = tw + 64 * k, size * 1.75
        cv.save(); cv.translate(self.W / 2, self.H * 0.865); cv.rotate(-0.8)
        rng = np.random.default_rng(int(c["t0"] * 10))
        p = skia.Path(); n = 28
        p.moveTo(-W / 2, -H / 2)
        for i in range(1, n + 1):
            p.lineTo(-W / 2 + W * i / n, -H / 2 + rng.uniform(-3, 3) * k)
        for i in range(n + 1):
            p.lineTo(W / 2 - W * i / n, H / 2 + rng.uniform(-3, 3) * k)
        p.close()
        cv.save(); cv.translate(6 * k, 8 * k); cv.drawPath(p, paint((0, 0, 0), 0.5 * a, blur=8 * k)); cv.restore()
        cv.drawPath(p, paint((240, 236, 226), 0.97 * a))
        n_chars = len(txt) * ramp(t, c["t0"], 0.035 * len(txt) + 0.05)
        draw_text(cv, self.res, txt, -tw / 2, size * 0.32, size, f, (24, 22, 20), a, 0.02, reveal=n_chars + 0.999)
        cv.restore()

    def _redbar(self, cv, c, t):
        k = self.k; size = 60 * k; f = "cond"
        txt = self._text(c, upper=True)
        tw = text_width(self.res, txt, size, f, 0.04)
        u = ease_out_cubic(ramp(t, c["t0"] - 0.05, 0.22)); a = ramp(t, c["t0"] - 0.05, 0.08)
        W, H = tw + 50 * k, size * 1.22
        x0, y0 = self.W / 2 - W / 2, self.H * 0.865 - H * 0.72
        cv.drawRect(skia.Rect.MakeXYWH(x0 + 6 * k, y0 + 8 * k, W * u, H), paint((0, 0, 0), 0.45 * a, blur=8 * k))
        cv.drawRect(skia.Rect.MakeXYWH(x0, y0, W * u, H), paint((176, 24, 20), 0.97 * a))
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(x0, y0, W * u, H))
        draw_text(cv, self.res, txt, self.W / 2, y0 + H * 0.8, size, f, (252, 249, 242), a, 0.04, "center")
        cv.restore()
