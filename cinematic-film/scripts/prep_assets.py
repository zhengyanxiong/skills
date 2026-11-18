#!/usr/bin/env python3
"""Grade the project's images into one look and generate the board textures (no downloaded textures).

  python3 prep_assets.py --project my-film
  python3 prep_assets.py --project my-film --grade natural  # override photos.json "grade"

photos.json:
  {"grade": "bw",
   "photos": [{"id": "P01", "file": "first_flight.jpg", "kind": "photo", "crop": [0.1, 0, 0.9, 1], ...}]}

grade: bw = neutral high-contrast black and white (archive), sepia = warm monochrome,
       natural = keep colour with one shared balance (your own photos, product shots, AI stills)
kind:  photo  -> one duotone (or natural colour)
       paper  -> newsprint: blacks lifted a little so it reads as ink on paper
       doc    -> records and forms: most colour removed, a hint of the paper kept
       color  -> kept in colour, only warmed (magazine covers)
crop:  optional [left, top, right, bottom] as fractions, to cut to the part that matters

Writes assets/prep/photos/<id>.jpg, assets/prep/photos/meta.json and, if missing, the textures
cork.png, cork_dark.png, slate.png, charcoal.png, paper.png, studio.png, night.png, blueprint.png
and relief.png (the boards behind the looks in engine.LOOKS).
"""
import argparse
import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

MAX_SIDE = 3200
GRADES = {
    "bw": ((15, 15, 16), (238, 236, 231), (234, 231, 224)),
    "sepia": ((28, 20, 14), (240, 226, 200), (236, 226, 204)),
    "natural": None,          # keep colour: product shots, brand photos, AI stills, modern stories
}


def duotone(gray, shadow, light):
    g = np.asarray(gray, np.float32)[..., None] / 255.0
    shadow = np.array(shadow, np.float32); light = np.array(light, np.float32)
    return (shadow + (light - shadow) * g).clip(0, 255).astype(np.uint8)


def grade(im, kind, look):
    if GRADES[look] is None:              # natural: gentle contrast and a shared, slightly warm balance
        a = np.asarray(ImageOps.autocontrast(im.convert("RGB"), cutoff=0.5), np.float32)
        lum = a.mean(axis=2, keepdims=True)
        a = (lum + (a - lum) * 0.92) * np.array([1.01, 1.0, 0.98])
        return Image.fromarray(a.clip(0, 255).astype(np.uint8))
    shadow, light, paper_light = GRADES[look]
    if kind == "color":
        a = np.asarray(im.convert("RGB"), np.float32) * np.array([1.0, 0.97, 0.9]) + np.array([4, 2, 0])
        return Image.fromarray(a.clip(0, 255).astype(np.uint8))
    g = ImageOps.grayscale(im)
    if kind == "photo":
        a = np.asarray(ImageOps.autocontrast(g, cutoff=1.0), np.float32) / 255.0
        a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1)
        return Image.fromarray(duotone((a * 255).astype(np.uint8), shadow, light))
    if kind == "paper":
        return Image.fromarray(duotone(ImageOps.autocontrast(g, cutoff=0.4), shadow, paper_light))
    a = np.asarray(im.convert("RGB"), np.float32)
    lum = a.mean(axis=2, keepdims=True)
    a = (lum + (a - lum) * 0.45) * np.array([1.0, 0.99, 0.97])
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def prep_photos(proj, look):
    spec = json.loads((proj / "photos.json").read_text())
    look = look or spec.get("grade", "bw")
    out = proj / "assets" / "prep" / "photos"; out.mkdir(parents=True, exist_ok=True)
    meta, missing = {}, []
    for p in spec["photos"]:
        src = proj / "assets" / "photos" / p["file"] if p.get("file") else None
        if not src or not src.exists():
            missing.append(f"{p['id']} ({p.get('file') or 'no file yet'})"); continue
        im = Image.open(src)
        im = im.convert("RGBA") if im.mode in ("P", "LA", "PA") else im
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (235, 228, 214)); bg.paste(im, mask=im.split()[3]); im = bg
        if p.get("crop"):
            w, h = im.size; c = p["crop"]
            im = im.crop((int(c[0] * w), int(c[1] * h), int(c[2] * w), int(c[3] * h)))
        if max(im.size) > MAX_SIDE:
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        g = grade(im, p.get("kind", "photo"), look)
        g.save(out / f"{p['id']}.jpg", quality=93)
        meta[p["id"]] = {"w": g.width, "h": g.height, "kind": p.get("kind", "photo")}
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"photos: {len(meta)} graded ({look})" + (f"; missing {', '.join(missing)}" if missing else ""))
    return not missing


def tile_noise(size, scale, seed):
    """Tileable value noise from FFT-filtered white noise."""
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((size, size))
    fx = np.fft.fftfreq(size)[:, None]; fy = np.fft.fftfreq(size)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2) * size / scale
    out = np.real(np.fft.ifft2(np.fft.fft2(n) * np.exp(-f ** 2)))
    return (out - out.mean()) / (out.std() + 1e-9)


def make_cork(size=1024):
    base = np.array([92, 62, 38], np.float32)
    n = 0.55 * tile_noise(size, 40, 1) + 0.35 * tile_noise(size, 12, 2) + 0.25 * tile_noise(size, 3, 3)
    speck = np.random.default_rng(4).random((size, size))
    dark = (speck > 0.985).astype(np.float32) * -0.9 + (speck < 0.012).astype(np.float32) * 0.5
    dark = np.asarray(Image.fromarray(((dark + 1) * 127).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 127 - 1
    v = n * 0.16 + dark * 0.35
    return (base[None, None, :] * (1 + v[..., None])).clip(0, 255)


def make_paper(size=1024):
    base = np.array([232, 229, 222], np.float32)
    n = 0.5 * tile_noise(size, 60, 11) + 0.3 * tile_noise(size, 8, 12) + 0.2 * tile_noise(size, 2, 13)
    rng = np.random.default_rng(14)
    fib = np.zeros((size, size), np.float32)
    for _ in range(900):                          # short paper fibres
        x, y = rng.integers(0, size, 2); ang = rng.random() * math.pi; ln = rng.integers(6, 22)
        for k in range(ln):
            fib[int(y + k * math.sin(ang)) % size, int(x + k * math.cos(ang)) % size] += 1
    fib = np.asarray(Image.fromarray((fib.clip(0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    v = n * 0.035 - fib * 0.05
    return (base[None, None, :] * (1 + v[..., None])).clip(0, 255)


def make_flat(rgb, seed, size=1024, amount=0.08):
    n = 0.6 * tile_noise(size, 50, seed) + 0.3 * tile_noise(size, 10, seed + 1) + 0.2 * tile_noise(size, 2, seed + 2)
    return (np.array(rgb, np.float32)[None, None, :] * (1 + n[..., None] * amount)).clip(0, 255)


def make_blueprint(size=1024):
    """Deep blue drafting sheet with a fine grid every 64 px and a heavier line every 256 (tileable)."""
    a = make_flat((22, 52, 98), 71, size, amount=0.06)
    grid = np.zeros((size, size), np.float32)
    for k in range(0, size, 64):
        w = 0.5 if k % 256 == 0 else 0.22
        grid[:, k:k + 2] = np.maximum(grid[:, k:k + 2], w); grid[k:k + 2, :] = np.maximum(grid[k:k + 2, :], w)
    return (a + grid[..., None] * np.array([120, 160, 200], np.float32)).clip(0, 255)


def make_relief(size=1024):
    """Faux terrain relief for map land: tileable multi-octave noise, hill-shaded, soft."""
    n = 0.6 * tile_noise(size, 90, 41) + 0.3 * tile_noise(size, 30, 42) + 0.15 * tile_noise(size, 8, 43)
    gy = (np.roll(n, -1, 0) - np.roll(n, 1, 0)) / 2; gx = (np.roll(n, -1, 1) - np.roll(n, 1, 1)) / 2   # wraps, so it tiles
    shade = np.clip(0.5 + (gx * -1.0 + gy * -1.0) * 1.6, 0, 1)
    return Image.fromarray((shade * 255).astype(np.uint8))


def textures(prep, force=False):
    def save(name, arr):
        p = prep / name
        if force or not p.exists():
            (arr if isinstance(arr, Image.Image) else Image.fromarray(arr.astype(np.uint8))).save(p)
            return name
    made = []
    cork = make_cork() if force or not (prep / "cork.png").exists() or not (prep / "cork_dark.png").exists() else None
    if cork is not None:
        made.append(save("cork.png", cork))
        lum = cork.mean(axis=2, keepdims=True)
        dark = (lum + (cork - lum) * 0.55) * 0.45 + np.array([12, 10, 9]) * 0.55    # calmer cork so colour reads on top
        made.append(save("cork_dark.png", dark))
    if force or not (prep / "paper.png").exists():
        made.append(save("paper.png", make_paper()))
    if force or not (prep / "slate.png").exists():
        made.append(save("slate.png", make_flat((34, 40, 46), 21)))
    if force or not (prep / "charcoal.png").exists():
        made.append(save("charcoal.png", make_flat((30, 29, 28), 31, amount=0.12)))
    if force or not (prep / "relief.png").exists():
        made.append(save("relief.png", make_relief()))
    if force or not (prep / "studio.png").exists():
        made.append(save("studio.png", make_flat((222, 220, 216), 51, amount=0.025)))
    if force or not (prep / "night.png").exists():
        made.append(save("night.png", make_flat((16, 20, 32), 61, amount=0.1)))
    if force or not (prep / "blueprint.png").exists():
        made.append(save("blueprint.png", make_blueprint()))
    made = [m for m in made if m]
    print("textures:", ", ".join(made) if made else "up to date")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--grade", choices=sorted(GRADES), default=None)
    ap.add_argument("--textures", action="store_true", help="regenerate textures even if present")
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    prep = proj / "assets" / "prep"; prep.mkdir(parents=True, exist_ok=True)
    textures(prep, a.textures)
    ok = prep_photos(proj, a.grade) if (proj / "photos.json").exists() else True
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
