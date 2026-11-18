#!/usr/bin/env python3
"""Synthesise the sound-effects track from the film's cue list. No samples: every sound is built from
noise and partials with numpy, so there is nothing to license.

  python3 render.py --project my-film --cues      # writes sfx_cues.json (items cue themselves)
  python3 build_sfx.py --project my-film          # writes audio/sfx.wav (full level; mix_soundtrack.py sets levels)

Cue kinds (film.cue(kind, t, gain, dur=...); items add most of these on their own):
  pop       print or card landing             slide     newspaper or string sliding in
  whoosh    camera move, route drawing on     marker    highlighter stroke
  pencil    pen circle or underline ("dur")   tick      pencil tick (tally marks)
  snip      tiny cut, a hole punched          click     shutter or film-frame clamp
  stamp     rubber stamp slam                 impact    title or number landing, low thump
  boom      big reveal, sub drop              ticks     a counter rolling up
  shimmer   cluster of small blips (dots)     drop      falling swoop
  riser     noise and tone crescendo into a section change ("dur"; peaks at t + dur)
  heartbeat low lub-dub thump (repeat once a second for a tension bed)
  clock     dry clock ticks, one a second ("dur")
film.room_tone = [[start, end], ...] lays a quiet room tone under those spans (silence elsewhere is
a deliberate beat).
"""
from __future__ import annotations

import argparse
import inspect
import json
import pathlib
import subprocess
import sys

import numpy as np

SR = 48000
BLOCK = 4096
HOP = BLOCK // 2


# ---------------------------------------------------------------- primitives
def n_of(sec):
    return int(sec * SR)


def envelope(points, n):
    """Piecewise-linear envelope over n samples; points are (fraction 0..1, gain)."""
    return np.interp(np.linspace(0.0, 1.0, n), [p[0] for p in points], [p[1] for p in points])


def sweep(a, b, n, curve=1.0):
    return a + (b - a) * np.linspace(0.0, 1.0, n) ** curve


def _band_mask(freqs, lo, hi, tilt):
    mask = np.zeros_like(freqs)
    mask[(freqs >= lo) & (freqs <= hi)] = 1.0
    lower = (freqs < lo) & (freqs > lo / 2)
    if lower.any():
        mask[lower] = 0.5 - 0.5 * np.cos(np.pi * (freqs[lower] - lo / 2) / (lo / 2))
    upper = (freqs > hi) & (freqs < hi * 2)
    if upper.any():
        mask[upper] = 0.5 + 0.5 * np.cos(np.pi * (freqs[upper] - hi) / hi)
    if tilt:
        with np.errstate(divide="ignore"):
            mask *= np.where(freqs > 0, (np.maximum(freqs, 1.0) / 1000.0) ** tilt, 0.0)
    return mask


def band_noise(n, lo, hi, amp, seed, tilt=0.0):
    """Noise confined to a band whose corners may move over time (overlap-add spectral masking)."""
    rng = np.random.default_rng(seed)
    source = rng.standard_normal(n + BLOCK)
    out = np.zeros(n + BLOCK)
    window = np.hanning(BLOCK)
    freqs = np.fft.rfftfreq(BLOCK, 1.0 / SR)
    lo_arr = np.full(n, lo, np.float64) if np.isscalar(lo) else np.asarray(lo, np.float64)
    hi_arr = np.full(n, hi, np.float64) if np.isscalar(hi) else np.asarray(hi, np.float64)
    for start in range(0, n, HOP):
        c = min(start + HOP, n - 1)
        spec = np.fft.rfft(source[start:start + BLOCK] * window)
        spec *= _band_mask(freqs, max(lo_arr[c], 1.0), max(hi_arr[c], 2.0), tilt)
        out[start:start + BLOCK] += np.fft.irfft(spec, BLOCK)
    out = out[:n]
    peak = np.max(np.abs(out))
    return (out / peak if peak > 0 else out) * amp


def tone(n, freq, decay, partials=(1.0, 2.01, 3.03)):
    t = np.arange(n) / SR
    return sum((0.6 ** i) * np.sin(2 * np.pi * freq * r * t) for i, r in enumerate(partials)) * np.exp(-t / decay)


def hit(n, lo, hi, decay, seed):
    return band_noise(n, lo, hi, np.exp(-(np.arange(n) / SR) / decay), seed=seed)


def fade(x, a, b):
    """De-click: short linear fades at both ends (a truncated tail would otherwise be a step, and a step is a click)."""
    out = x.copy()
    na, nb = min(int(a * SR), len(out)), min(int(b * SR), len(out))
    if na > 0:
        out[:na] *= np.linspace(0, 1, na)
    if nb > 0:
        out[-nb:] *= np.linspace(1, 0, nb)
    return out


class Bed:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.buf = np.zeros((2, self.n))

    def add(self, sig, at, gain=1.0, pan=0.0):
        s = int(at * SR)
        if s >= self.n or len(sig) == 0:
            return
        sig = fade(sig[: self.n - s], 0.02, 0.02)
        e = s + len(sig)
        self.buf[0, s:e] += sig * gain * np.sqrt((1.0 - pan) / 2.0) * np.sqrt(2.0)
        self.buf[1, s:e] += sig * gain * np.sqrt((1.0 + pan) / 2.0) * np.sqrt(2.0)

    def render(self, path, headroom_db=-1.0):
        a = self.buf
        b, a_ = _hp_coeffs(28.0)
        for ch in range(2):
            a[ch] = _iir(a[ch], b, a_)
        peak = np.max(np.abs(a))
        if peak > 0:
            a = a / peak * (10 ** (headroom_db / 20))
        pcm = (a.T.reshape(-1) * 32767).astype(np.int16)
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
                        "-c:a", "pcm_s24le", str(path)], input=pcm.tobytes(), check=True)


def _hp_coeffs(fc):
    alpha = 1.0 / (1.0 + 2 * np.pi * fc / SR)
    return (alpha, -alpha), alpha


def _iir(x, b, a):
    """y[n] = a*y[n-1] + b0*x[n] + b1*x[n-1]  (one-pole high-pass), via scipy if present, else a loop."""
    try:
        from scipy.signal import lfilter
        return lfilter([b[0], b[1]], [1.0, -a], x)
    except ImportError:
        y = np.empty_like(x); yp = xp = 0.0
        for i, s in enumerate(x):
            yp = a * yp + b[0] * s + b[1] * xp; xp = s; y[i] = yp
        return y


_LEAD = n_of(.025)


def _lead(x):
    return np.concatenate([np.zeros(_LEAD), x])


# ---------------------------------------------------------------- sounds
def whoosh(seed):
    n = n_of(.55)
    return band_noise(n, sweep(300, 1400, n), sweep(1800, 6000, n), envelope([(0, 0), (.45, 1), (1, 0)], n) ** 1.5, seed=seed, tilt=-.4)


def pop(seed):
    n = n_of(.18); t = np.arange(n) / SR
    return np.sin(2 * np.pi * sweep(260, 150, n) * t) * np.exp(-t / .035) * .8 + hit(n, 1200, 5000, .01, seed) * .25


def slide(seed):
    n = n_of(1.4)
    return band_noise(n, 250, 1800, envelope([(0, 0), (.15, .8), (.85, .8), (1, 0)], n), seed=seed, tilt=-.6) * .8


def marker(seed):
    n = n_of(.45)
    amp = envelope([(0, 0), (.1, .9), (.8, .8), (1, 0)], n) * (1 + .25 * np.sin(2 * np.pi * 23 * np.arange(n) / SR))
    return band_noise(n, 1800, 5200, amp, seed=seed, tilt=.3) * .7


def pencil(seed, dur=1.6):
    n = n_of(dur); t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    stroke = np.abs(np.sin(np.pi * (7 + rng.uniform(-1.5, 1.5)) * t + rng.uniform(0, 3))) ** .6
    amp = stroke * (1 + .3 * np.sin(2 * np.pi * rng.uniform(13, 19) * t)) * envelope([(0, 0), (.06, 1), (.9, .85), (1, 0)], n)
    return band_noise(n, 2400, 8500, amp, seed=seed, tilt=.2) * .55 + band_noise(n, 600, 1800, amp * .3, seed=seed + 1) * .3


def tick(seed):
    n = n_of(.16)
    return _lead(band_noise(n, 2500, 9000, envelope([(0, 0), (.1, 1), (.35, .3), (.45, .9), (1, 0)], n), seed=seed, tilt=.2) * .7)


def snip(seed):
    rng = np.random.default_rng(seed); n = n_of(.07)
    return _lead(tone(n, rng.uniform(2600, 3600), .006, (1.0, 1.52)) * .5 + hit(n, 3000, 10000, .004, seed) * .8)


def click(seed):
    n = n_of(.11); out = np.zeros(n)
    a = hit(n_of(.012), 2500, 9000, .0018, seed) + tone(n_of(.012), 3400, .0015, (1.0,)) * .4
    out[:len(a)] += a
    b = hit(n_of(.01), 2000, 7000, .0015, seed + 1) * .6
    out[n_of(.075):n_of(.075) + len(b)] += b
    return _lead(out)


def stamp(seed):
    n = n_of(.4); t = np.arange(n) / SR
    return np.sin(2 * np.pi * sweep(120, 55, n) * t) * np.exp(-t / .07) + hit(n, 400, 3500, .025, seed) * .8


def impact(seed):
    n = n_of(1.2); t = np.arange(n) / SR
    return np.sin(2 * np.pi * sweep(90, 42, n, .6) * t) * np.exp(-t / .35) + band_noise(n, 200, 2500, np.exp(-t / .12), seed=seed) * .35


def boom(seed):
    n = n_of(2.4); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * sweep(70, 30, n, .5) * t) * np.exp(-t / .8)
    return sub * 1.1 + hit(n, 500, 7000, .05, seed) * .5 + band_noise(n, 60, 400, np.exp(-t / .9), seed=seed + 3) * .4


def ticks(seed):
    n = n_of(1.4); out = np.zeros(n); rng = np.random.default_rng(seed)
    for at in np.cumsum(np.linspace(.04, .11, 18)):      # decelerating, like a counter settling
        s = n_of(at)
        if s >= n:
            break
        c = tone(n_of(.03), 2400 + rng.uniform(-150, 150), .004, (1.0, 2.3))
        out[s:s + len(c)] += c[: n - s]
    return out * .8


def shimmer(seed):
    n = n_of(1.0); out = np.zeros(n); rng = np.random.default_rng(seed)
    for i in range(14):
        s = n_of(i * .05 + rng.uniform(0, .02)); c = tone(n_of(.12), rng.uniform(1600, 3400), .03, (1.0, 2.0))
        out[s:s + len(c)] += c[: n - s] * .5
    return out


def drop(seed):
    n = n_of(.6)
    whistle = np.sin(2 * np.pi * np.cumsum(sweep(900, 120, n, .7)) / SR) * envelope([(0, .2), (.3, 1), (1, 0)], n)
    w = whoosh(seed); out = np.zeros(max(n, len(w)))
    out[:n] += whistle * .5; out[:len(w)] += w * .5
    return out


def riser(seed, dur=2.0):
    """Noise band sweeping up plus a climbing low tone; starts at the cue, peaks at t + dur."""
    n = n_of(dur); t = np.arange(n) / SR
    env = (t / dur) ** 2.4
    out = band_noise(n, sweep(250, 1800, n), sweep(1200, 9000, n), env, seed=seed) * .7 + np.sin(2 * np.pi * np.cumsum(sweep(70, 260, n, 1.4)) / SR) * env * .5
    out[-n_of(.02):] *= np.linspace(1, 0, n_of(.02))
    return out


def heartbeat(seed):
    n = n_of(.75); t = np.arange(n) / SR

    def thump(at, f0, amp):
        tt = np.clip(t - at, 0, None)
        return np.sin(2 * np.pi * sweep(f0, f0 * .55, n, .6) * tt) * np.exp(-tt / .09) * (t >= at) * amp
    return thump(.02, 62, 1.0) + thump(.24, 55, .7)


def clock(seed, dur=4.0):
    n = n_of(dur); out = np.zeros(n)
    for k, at in enumerate(np.arange(.02, dur - .05, 1.0)):
        s = n_of(at); seg = hit(n_of(.05), 1800 if k % 2 == 0 else 1300, 5200, .012, seed + k)
        out[s:s + len(seg)] += seg[: n - s] * .8
    return out


SOUNDS = dict(whoosh=whoosh, pop=pop, slide=slide, marker=marker, pencil=pencil, tick=tick, snip=snip, click=click,
              stamp=stamp, impact=impact, boom=boom, ticks=ticks, shimmer=shimmer, drop=drop, riser=riser,
              heartbeat=heartbeat, clock=clock)


def room_tone(total, spans):
    """Quiet room: low filtered noise, faded in and out over each span."""
    n = n_of(total); gate = np.zeros(n)
    for a, b in spans:
        ia, ib = n_of(a), min(n_of(b), n)
        if ib <= ia:
            continue
        g = np.ones(ib - ia); fi, fo = min(n_of(1.2), len(g) // 3), min(n_of(.4), len(g) // 3)
        g[:fi] = np.linspace(0, 1, fi); g[len(g) - fo:] = np.linspace(1, 0, fo)
        gate[ia:ib] = g
    return band_noise(n, 70, 420, np.ones(n), seed=77) * .3 * gate


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    cp = proj / "sfx_cues.json"
    if not cp.exists():
        sys.exit(f"{cp} not found: run render.py --project {proj} --cues first")
    cues = json.loads(cp.read_text())
    total = cues["duration"]
    unknown = sorted({c["type"] for c in cues["cues"]} - SOUNDS.keys())
    if unknown:
        sys.exit(f"unknown cue kinds: {unknown} (have {sorted(SOUNDS)})")
    bed = Bed(total)
    for i, c in enumerate(cues["cues"]):
        fn = SOUNDS[c["type"]]
        kw = {"dur": c["dur"]} if "dur" in c and "dur" in inspect.signature(fn).parameters else {}
        bed.add(fn(seed=100 + i, **kw), max(c["t"], 0), gain=c.get("gain", 1.0), pan=((i * 37) % 11 - 5) / 20)
    if cues.get("room_tone"):
        bed.add(room_tone(total, cues["room_tone"]), 0, gain=.22)
    out = proj / "audio" / "sfx.wav"
    bed.render(out)
    print(f"sfx: {out}  ({len(cues['cues'])} cues, {total:.1f}s)")


if __name__ == "__main__":
    main()
