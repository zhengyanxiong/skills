#!/usr/bin/env python3
"""Vectorise a raster icon into a layered SVG of filled paths, without an external tracer.

  trace_rgba(rgba, out_w, out_h, max_colors=10) -> (svg_text, info)
  python3 scripts/distill/trace_bitmap.py icon.png [-o icon.svg] [--width-pt 24]

Method
  1. premultiplied Lanczos upscale so the long side is ~420 px (edges stay smooth when thresholded)
  2. colours: k-means in CIELAB over opaque, low-gradient pixels (antialiased edge pixels would otherwise form
     their own clusters); the smallest k whose 97th-percentile distance to its centre is <= 10 (at most max_colors); clusters
     under 0.15 % of the opaque area merge into their nearest neighbour; every opaque pixel then takes its nearest
     centre, so an antialiased edge splits at its midpoint
  3. a 5x5 majority filter on the label map removes speckle
  4. stacked layers, largest area first: layer i is filled wherever a pixel belongs to layer i or to any later layer,
     so shapes overlap instead of leaving hairline gaps, and the last layer painted on a pixel is its own colour
  5. each layer mask -> sub-pixel contours of the lightly blurred mask (skimage find_contours) -> polygon
     simplification -> quadratic smoothing through edge midpoints, keeping corners sharper than 55 degrees ->
     one path per colour with fill-rule evenodd (holes come out as inner contours)
Partially transparent pixels are thresholded at alpha 0.5; soft shadows and glows are not icons and should be
filtered out before tracing (mech_bitmaps.py triage).
"""
import argparse, math, sys
import numpy as np
from PIL import Image


def _resize_premul(rgba, size):
    f = rgba.astype(np.float32) / 255.0
    a = f[..., 3]
    chans = [f[..., 0] * a, f[..., 1] * a, f[..., 2] * a, a]
    out = [np.asarray(Image.fromarray(c, mode='F').resize(size, Image.LANCZOS)) for c in chans]
    A = np.clip(out[3], 0, 1)
    rgb = np.stack([np.where(A > 1e-3, out[i] / np.maximum(A, 1e-3), 0) for i in range(3)], axis=2)
    return np.clip(rgb, 0, 1), A


def _kmeans_colors(lab_sample, max_colors, tol):
    from sklearn.cluster import KMeans
    best = None
    for k in range(1, max_colors + 1):
        if k > len(lab_sample): break
        km = KMeans(n_clusters=k, n_init=3, random_state=0).fit(lab_sample)
        d = np.sqrt(((lab_sample - km.cluster_centers_[km.labels_]) ** 2).sum(axis=1))
        best = km
        # the 97th percentile, not the mean: a few small but distinct colours (the paint dots of a palette icon)
        # barely move the mean distance and would be absorbed into the big areas
        if np.percentile(d, 97) <= tol: break
    return best.cluster_centers_


def _smooth_path(pts, sx, sy, corner_deg=55.0):
    n = len(pts)
    if n < 3: return ''
    P = [(x * sx, y * sy) for x, y in pts]
    mid = [((P[i][0] + P[(i + 1) % n][0]) / 2, (P[i][1] + P[(i + 1) % n][1]) / 2) for i in range(n)]
    d = ['M%.2f %.2f' % mid[-1]]
    for i in range(n):
        a, p, c = P[i - 1], P[i], P[(i + 1) % n]
        v1, v2 = (p[0] - a[0], p[1] - a[1]), (c[0] - p[0], c[1] - p[1])
        ang = abs(math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])))
        if ang > corner_deg:
            d.append('L%.2f %.2f L%.2f %.2f' % (p[0], p[1], mid[i][0], mid[i][1]))
        else:
            d.append('Q%.2f %.2f %.2f %.2f' % (p[0], p[1], mid[i][0], mid[i][1]))
    d.append('Z')
    return ' '.join(d)


def trace_rgba(rgba, out_w, out_h, max_colors=10, tol=10.0, long_side=420, min_area_frac=0.0015, simplify=0.8):
    """rgba: HxWx4 uint8. Returns (svg_text, info) with the SVG in a viewBox of out_w x out_h (e.g. print pt)."""
    from scipy import ndimage
    from skimage import measure
    from skimage.color import rgb2lab
    rgba = np.asarray(rgba)
    H0, W0 = rgba.shape[:2]
    f = max(1.0, long_side / max(H0, W0))
    W, H = max(2, int(round(W0 * f))), max(2, int(round(H0 * f)))
    rgb, A = _resize_premul(rgba, (W, H))
    opaque = A >= 0.5
    info = {'px': [W0, H0], 'upscaled': [W, H], 'layers': 0, 'colors': []}
    if opaque.sum() < 16:
        return None, dict(info, error='empty')
    lab = rgb2lab(rgb)
    grad = np.hypot(ndimage.sobel(lab[..., 0], axis=0), ndimage.sobel(lab[..., 0], axis=1))
    # sample colours away from antialiased edges; the absolute floor keeps the centre pixels of thin lines, whose
    # gradient is ~0 but which a pure percentile cut (mostly-flat icons have a 0 percentile) would drop
    flat = opaque & (grad <= max(float(np.percentile(grad[opaque], 60)), 12.0))
    src = lab[flat] if flat.sum() >= 64 else lab[opaque]
    rng = np.random.default_rng(0)
    sample = src[rng.choice(len(src), size=min(len(src), 24000), replace=False)]
    centers = _kmeans_colors(sample, max_colors, tol)
    flat_lab = lab.reshape(-1, 3)
    dist = ((flat_lab[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    labels = dist.argmin(axis=1).reshape(H, W)
    labels[~opaque] = -1
    # merge tiny clusters into the nearest remaining centre
    total = opaque.sum()
    counts = np.array([(labels == k).sum() for k in range(len(centers))])
    alive = [k for k in range(len(centers)) if counts[k] >= min_area_frac * total] or [int(counts.argmax())]
    if len(alive) < len(centers):
        cd = ((centers[:, None, :] - centers[None, alive, :]) ** 2).sum(axis=2)
        remap = np.array([alive[int(cd[k].argmin())] for k in range(len(centers))])
        labels = np.where(labels >= 0, remap[np.maximum(labels, 0)], -1)
    # majority filter
    ks = sorted(set(np.unique(labels)) - {-1})
    votes = np.stack([ndimage.uniform_filter((labels == k).astype(np.float32), size=5) for k in ks], axis=0)
    labels = np.where(opaque, np.array(ks)[votes.argmax(axis=0)], -1)
    areas = {k: int((labels == k).sum()) for k in ks}
    order = [k for k in sorted(ks, key=lambda k: -areas[k]) if areas[k] > 0]
    sx, sy = out_w / W, out_h / H
    paths = []
    for i, k in enumerate(order):
        mask = np.isin(labels, order[i:])
        sel = (labels == k)
        col = (rgb[sel].mean(axis=0) * 255).round().astype(int) if sel.any() else np.array([0, 0, 0])
        hexc = '#%02x%02x%02x' % tuple(int(v) for v in np.clip(col, 0, 255))
        padded = np.pad(mask.astype(np.float32), 2)
        soft = ndimage.gaussian_filter(padded, sigma=0.9)
        segs = []
        for c in measure.find_contours(soft, 0.5):
            if len(c) < 4: continue
            c = measure.approximate_polygon(c, tolerance=simplify)
            if len(c) < 4: continue
            xy = [(p[1] - 2 + 0.5, p[0] - 2 + 0.5) for p in c[:-1]]
            area = 0.5 * abs(sum(xy[j][0] * xy[(j + 1) % len(xy)][1] - xy[(j + 1) % len(xy)][0] * xy[j][1] for j in range(len(xy))))
            if area < 6.0: continue
            segs.append(_smooth_path(xy, sx, sy))
        if segs:
            paths.append('<path fill="%s" fill-rule="evenodd" d="%s"/>' % (hexc, ' '.join(segs)))
            info['colors'].append(hexc)
    info['layers'] = len(paths)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.3f %.3f" width="%.3f" height="%.3f">'
           '<g data-traced="1">%s</g></svg>' % (out_w, out_h, out_w, out_h, ''.join(paths)))
    return svg, info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('png'); ap.add_argument('-o', '--out'); ap.add_argument('--width-pt', type=float, default=None)
    ap.add_argument('--max-colors', type=int, default=10)
    a = ap.parse_args()
    im = np.asarray(Image.open(a.png).convert('RGBA'))
    h, w = im.shape[:2]
    ow = a.width_pt or w; oh = ow * h / w
    svg, info = trace_rgba(im, ow, oh, max_colors=a.max_colors)
    if svg is None: sys.exit('nothing to trace: %s' % info)
    out = a.out or a.png.rsplit('.', 1)[0] + '.svg'
    open(out, 'w', encoding='utf-8').write(svg)
    print('wrote %s: %d layers %s' % (out, info['layers'], info['colors']))


if __name__ == '__main__':
    main()
