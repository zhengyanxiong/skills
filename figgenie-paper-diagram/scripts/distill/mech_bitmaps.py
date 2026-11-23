#!/usr/bin/env python3
"""Harvest the bitmaps embedded in a parts-mining package's figures as icon candidates, and vectorise the icons.

  python3 scripts/distill/mech_bitmaps.py --package mech-parts/pilot-evolution [--figs id,id] [--no-trace]

1. render  every visible <image> element (measured geometry; images that only feed <mask>/<pattern> definitions are
           never drawn and are skipped) is cut out with its ancestors' masks and clip paths (mech_svg.subtractive_cut)
           and rendered on a transparent page at its native pixel density (1-8 px per unit, long side <= 768 px), so
           PowerPoint soft masks become real alpha
2. triage  tiny | effect (few colours + mostly soft alpha: shadows, glows) | flat (one solid colour) | photo (many
           colours and texture) | gradient (smooth ramps) | icon (everything else)
3. dedupe  near-identical renders across the whole package (grey dHash + alpha mask + mean colour + aspect ratio);
           the largest render represents its group; every placement is kept as a context
4. trace   icons are vectorised at their displayed print size (trace_bitmap.trace_rgba) and scored against the raster
           (SSIM on grey composited over white, mean absolute colour error)
5. write   <package>/bitmaps/index.json, png/<bid>.png (RGBA), svg/<bid>.svg (vector trace),
           sheets/icons_NN.png + .json (raster | vector pairs, most frequent first), sheets/other_NN.png + .json
"""
import argparse, collections, hashlib, io, json, math, sys, time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_parts as X          # noqa: E402
import mech_svg as M               # noqa: E402
import trace_bitmap as T           # noqa: E402

MAX_SIDE = 768
TRACE_SSIM_OK, TRACE_MAE_OK = 0.80, 18.0


def collect(figs):
    jobs = [(f, fi) for f in figs for fi in f['files'] if b'<image' in open(fi['path'], 'rb').read()]
    geoms = M.measure_files([(fi['path'], str(Path(f['dir']) / ('geom_%d.json' % fi['index']))) for f, fi in jobs])
    occ, roots = [], {}
    for (f, fi), g in zip(jobs, geoms):
        root = M.parse(fi['path']); anc = M.anchors(root); roots[fi['path']] = root
        s = fi['scale_pt_per_unit']; ox, oy = fi['frame_src'][:2]
        texts = [e for e in g['els'] if e['tag'] == 'text' and e['v'] and e.get('t')]
        for e in g['els']:
            if e['tag'] != 'image' or not e['v'] or e['w'] <= 0 or e['h'] <= 0: continue
            data = M.href_bytes(anc[e['i']])
            if not data: continue
            try:
                im = Image.open(io.BytesIO(data)); natural, fmt = im.size, (im.format or '').lower()
                raw_alpha = im.mode in ('RGBA', 'LA', 'PA') or (im.mode == 'P' and 'transparency' in im.info)
            except Exception:  # noqa: BLE001
                continue
            tol = 12.0 / s
            near = []
            for t in texts:
                dx = max(e['x'] - (t['x'] + t['w']), t['x'] - (e['x'] + e['w']), 0); dy = max(e['y'] - (t['y'] + t['h']), t['y'] - (e['y'] + e['h']), 0)
                if math.hypot(dx, dy) <= tol: near.append(t['t'])
            occ.append({'fig': f['id'], 'file': fi['index'], 'idx': e['i'], 'path': fi['path'], 'box': [e['x'], e['y'], e['w'], e['h']],
                        'bbox_pt': [round((e['x'] - ox) * s, 1), round((e['y'] - oy) * s, 1), round((e['x'] + e['w'] - ox) * s, 1), round((e['y'] + e['h'] - oy) * s, 1)],
                        'disp_pt': [round(e['w'] * s, 1), round(e['h'] * s, 1)], 'natural_px': list(natural), 'fmt': fmt,
                        'data_sha1': hashlib.sha1(data).hexdigest(), 'texts': near[:6], 'caption': (f.get('caption') or '')[:200],
                        'raw_alpha': raw_alpha, '_data': data})
    return occ, roots


def with_pixel_size(svg, W, H):
    """Give the SVG a whole-pixel CSS size (viewBox does the scaling) so it can be rendered at scale factor 1.
    A fractional CSS size at a high device scale factor is rasterised at the rounded-up size and scaled back:
    a 15.1 px wide icon came out 15.1/16 = 6 % too small."""
    root = M.etree.fromstring(svg.encode('utf-8'))
    root.set('width', str(int(W))); root.set('height', str(int(H))); root.set('preserveAspectRatio', 'none')
    return M.etree.tostring(root, encoding='unicode')


def render_occurrences(occ, roots):
    from playwright.sync_api import sync_playwright
    out = [None] * len(occ)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb'])
        for k, o in enumerate(occ):
            x, y, w, h = o['box']
            ppu = min(8.0, max(1.0, o['natural_px'][0] / w))
            ppu = min(ppu, MAX_SIDE / max(w, h)) if max(w, h) * ppu > MAX_SIDE else ppu
            W, H = max(1, int(round(w * ppu))), max(1, int(round(h * ppu)))
            svg = with_pixel_size(M.subtractive_cut(roots[o['path']], {o['idx']}, (x, y, w, h), prefix='bm%d-' % k), W, H)
            pg = b.new_page(viewport={'width': max(200, W + 2), 'height': max(200, H + 2)}, device_scale_factor=1)
            pg.set_default_timeout(240000)
            try:
                pg.set_content(M.page_html(svg, bg='transparent'), wait_until='load')
                png = pg.locator('svg').first.screenshot(omit_background=True)
                out[k] = np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))
            except Exception as exc:  # noqa: BLE001
                print('  render failed %s #%d: %s' % (o['fig'], o['idx'], exc), file=sys.stderr)
            pg.close()
        b.close()
    return out


def hidden_content(data, render):
    """True when the figure hides drawn content of the embedded image -- a clip path or mask cuts part of it away:
    pixels invisible in the placed render that differ clearly from the raw image's dominant colour. Watermarks and
    stock ids hide this way; a mask that only shapes a solid-colour or plain-background image does not trigger it."""
    try:
        raw = Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception:  # noqa: BLE001
        return False
    H, W = render.shape[:2]
    raw = np.asarray(raw.resize((W, H), Image.LANCZOS)).astype(np.int16)
    hidden = (render[..., 3] < 8) & (raw[..., 3] > 200)
    if hidden.sum() < 20: return False
    q = (raw[..., :3] // 32).reshape(-1, 3)
    dom = int(np.bincount(q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]).argmax())
    dom_rgb = np.array([dom // 64, (dom // 8) % 8, dom % 8]) * 32 + 16
    ink = (np.abs(raw[..., :3] - dom_rgb).max(axis=2) > 64) & hidden
    return int(ink.sum()) >= max(20, int(0.002 * W * H))


def over_white(rgba):
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    return (rgba[..., :3].astype(np.float32) * a + 255.0 * (1 - a)).astype(np.uint8)


def triage(rgba, disp_pt, natural_px=None, fmt=''):
    H, W = rgba.shape[:2]
    a = rgba[..., 3].astype(np.float32) / 255.0
    vis = a > 0.04
    nvis = int(vis.sum())
    if nvis < 16 or min(W, H) < 8 or max(disp_pt) < 4 or (natural_px and min(natural_px) < 20):
        return 'tiny', {'visible_px': nvis}
    opaque = a > 0.85
    pfrac = float((vis & ~opaque).sum()) / nvis
    rgb = rgba[..., :3][vis].astype(int)
    q = rgb // 24
    _u, cnt = np.unique(q[:, 0] * 121 + q[:, 1] * 11 + q[:, 2], return_counts=True)
    cnt = np.sort(cnt)[::-1]
    n90 = int(np.searchsorted(np.cumsum(cnt) / cnt.sum(), 0.90) + 1)
    std = float(rgb.std(axis=0).mean())
    gray = over_white(rgba).mean(axis=2)
    gy, gx = np.gradient(gray)
    edges = float((np.hypot(gx, gy) > 18).mean())
    stats = {'soft_alpha': round(pfrac, 3), 'colours90': n90, 'colour_std': round(std, 1), 'edges': round(edges, 3),
             'coverage': round(nvis / float(W * H), 3)}
    coverage = nvis / float(W * H)
    # a single colour is still an icon when the alpha draws a shape (masked glyphs: check marks, router, pins, arcs);
    # it is a flat fill only when the alpha fills the box, and an effect (shadow, glow) only when it is mostly soft
    if n90 <= 3 and pfrac >= 0.6: return 'effect', stats
    if n90 <= 2 and std < 8 and coverage >= 0.9 and pfrac < 0.15: return 'flat', stats
    if (fmt in ('jpeg', 'jpg') and n90 >= 16) or (n90 >= 80 and edges > 0.12): return 'photo', stats
    if n90 >= 10 and edges < 0.02: return 'gradient', stats
    return 'icon', stats


def fingerprint(rgba):
    im = Image.fromarray(rgba, 'RGBA')
    wh = Image.fromarray(over_white(rgba), 'RGB')
    g = np.asarray(wh.convert('L').resize((17, 16), Image.BILINEAR), dtype=np.int16)
    dh = (g[:, 1:] > g[:, :-1]).flatten()
    al = (np.asarray(im.getchannel('A').resize((16, 16), Image.BILINEAR)) > 127).flatten()
    m = rgba[..., 3] > 127
    mean = rgba[..., :3][m].mean(axis=0) if m.any() else np.array([255.0, 255.0, 255.0])
    return dh, al, mean, rgba.shape[1] / float(rgba.shape[0])


def group(prints):
    n = len(prints); uf = X.UF(n)
    for i in range(n):
        di, ai, mi, ri = prints[i]
        for j in range(i + 1, n):
            dj, aj, mj, rj = prints[j]
            if abs(math.log(ri / rj)) > 0.12: continue
            if np.count_nonzero(di != dj) <= 14 and np.count_nonzero(ai != aj) <= 10 and np.linalg.norm(mi - mj) <= 28:
                uf.union(i, j)
    groups = collections.defaultdict(list)
    for i in range(n): groups[uf.find(i)].append(i)
    return list(groups.values())


def render_svgs_to(arrs_and_svgs):
    """[(svg_text, (w_px, h_px), w_units)] -> RGBA arrays rendered at exactly w_px x h_px."""
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb'])
        for svg, (wpx, hpx), wu in arrs_and_svgs:
            pg = b.new_page(viewport={'width': max(200, int(wpx) + 2), 'height': max(200, int(hpx) + 2)}, device_scale_factor=1)
            pg.set_content(M.page_html(with_pixel_size(svg, wpx, hpx), bg='transparent'), wait_until='load')
            png = pg.locator('svg').first.screenshot(omit_background=True)
            im = Image.open(io.BytesIO(png)).convert('RGBA')
            if im.size != (wpx, hpx): im = im.resize((wpx, hpx), Image.LANCZOS)
            out.append(np.asarray(im)); pg.close()
        b.close()
    return out


def score(raster, vector, side=96):
    """SSIM (grey) and mean colour error at a 96 px downsample: at full size a one-pixel shift of a thin line
    already halves SSIM although the two look the same at print size."""
    from skimage.metrics import structural_similarity
    def small(x):
        im = Image.fromarray(over_white(x), 'RGB'); r = side / float(max(im.size))
        if r < 1: im = im.resize((max(8, int(im.width * r)), max(8, int(im.height * r))), Image.BOX)
        return np.asarray(im).astype(np.float32)
    A = small(raster); B = small(vector)
    if A.shape != B.shape: B = np.asarray(Image.fromarray(B.astype(np.uint8)).resize((A.shape[1], A.shape[0]), Image.BOX)).astype(np.float32)
    ga, gb = A.mean(axis=2), B.mean(axis=2)
    win = min(7, (min(ga.shape) // 2) * 2 - 1)
    ssim = float(structural_similarity(ga, gb, data_range=255, win_size=win)) if win >= 3 else 0.0
    return round(ssim, 3), round(float(np.abs(A - B).mean()), 2)


def checker(size):
    c = Image.new('RGB', size, '#ffffff'); d = ImageDraw.Draw(c)
    for y in range(0, size[1], 10):
        for x in range(0, size[0], 10):
            if (x // 10 + y // 10) % 2: d.rectangle([x, y, x + 9, y + 9], fill='#e9e9e9')
    return c


def fit_tile(rgba, side):
    im = Image.fromarray(rgba, 'RGBA')
    r = min(side / im.width, side / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS if r < 1 else Image.NEAREST)
    bg = checker((side, side)).convert('RGBA'); bg.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    return bg.convert('RGB')


def sheets(entries, reps, traces, out_dir, prefix, with_trace):
    F = X._fonts()
    side, cols, rows = 130, 5, 6
    per = cols * rows
    tw = side * (2 if with_trace else 1) + 18; th = side + 52
    names = []
    for s in range(0, len(entries), per):
        batch = entries[s:s + per]; n = s // per + 1
        img = Image.new('RGB', (cols * tw + 16, math.ceil(len(batch) / cols) * th + 44), '#ffffff'); dr = ImageDraw.Draw(img)
        dr.text((8, 10), '%s %d  (%d-%d of %d)  %s' % (prefix, n, s + 1, s + len(batch), len(entries),
                                                     'left: raster as placed (checker = transparent) | right: vector trace' if with_trace else 'raster only'),
                fill='#111111', font=F['hdr'])
        tiles = {}
        for k, e in enumerate(batch):
            r, c = divmod(k, cols); x = 8 + c * tw; y = 40 + r * th
            dr.rectangle([x, y, x + tw - 6, y + th - 6], outline='#d8d8d8')
            img.paste(fit_tile(reps[e['bid']], side), (x + 4, y + 18))
            if with_trace and e['bid'] in traces:
                img.paste(fit_tile(traces[e['bid']], side), (x + 8 + side, y + 18))
            dr.rectangle([x + 2, y + 2, x + 34, y + 17], fill='#1a1a1a'); dr.text((x + 6, y + 2), str(k + 1), fill='#ffffff', font=F['lbl'])
            dr.text((x + 40, y + 4), '%s  x%d  %s' % (e['bid'], e['occurrences'], e['triage']), fill='#0b57a4', font=F['lbl'])
            t = e.get('trace') or {}
            line = '%.0fx%.0f pt  %dx%d px' % (e['disp_pt'][0], e['disp_pt'][1], e['size_px'][0], e['size_px'][1])
            if e.get('cropped'): line += '  CROPPED'
            if t: line += '  ssim %.2f  err %.0f  %d layers' % (t.get('ssim', 0), t.get('mae', 0), t.get('layers', 0))
            dr.text((x + 4, y + side + 21), line, fill='#c02020' if (t and not e.get('trace_ok')) else '#333333', font=F['txt'])
            ctx = e['contexts'][0]
            dr.text((x + 4, y + side + 34), ('%s  %s' % (ctx['fig'], ' | '.join(ctx['texts'])[:40]))[:60], fill='#777777', font=F['txt'])
            tiles[str(k + 1)] = {'bid': e['bid'], 'triage': e['triage'], 'png': e['png'], 'svg': e.get('svg')}
        png = out_dir / ('%s_%02d.png' % (prefix, n)); img.save(png)
        (out_dir / ('%s_%02d.json' % (prefix, n))).write_text(json.dumps({'sheet': png.name, 'tiles': tiles}, indent=1), encoding='utf-8')
        names.append(png.name)
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--package', required=True); ap.add_argument('--figs', default='')
    ap.add_argument('--no-trace', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    pkg = Path(a.package); out = pkg / 'bitmaps'
    for d in ('png', 'svg', 'raw', 'sheets'): (out / d).mkdir(parents=True, exist_ok=True)
    for old in (out / 'sheets').glob('*'): old.unlink()
    # <package>/bitmaps_overrides.json {"icon": [bid, ...]}: bitmaps a reviewer found misclassified, traced as icons
    ov_p = pkg / 'bitmaps_overrides.json'
    forced_icons = set(json.load(open(ov_p, encoding='utf-8')).get('icon', [])) if ov_p.exists() else set()
    figs = json.load(open(pkg / 'figures.json', encoding='utf-8'))
    if a.figs: figs = [f for f in figs if f['id'] in set(a.figs.split(','))]
    occ, roots = collect(figs)
    print('image placements: %d in %d figures' % (len(occ), len({o['fig'] for o in occ})), flush=True)
    arrs = render_occurrences(occ, roots)
    keep = [(o, r) for o, r in zip(occ, arrs) if r is not None]
    for o, r in keep:
        o['triage'], o['stats'] = triage(r, o['disp_pt'], o['natural_px'], o['fmt'])
        o['cropped'] = hidden_content(o['_data'], r)
    groups = group([fingerprint(r) for _o, r in keep])
    entries, reps = [], {}
    for g in groups:
        members = [keep[i] for i in g]
        o0, r0 = max(members, key=lambda m: m[1].shape[0] * m[1].shape[1])
        bid = 'bm-' + hashlib.sha1(r0.tobytes()).hexdigest()[:10]
        tri = collections.Counter(m[0]['triage'] for m in members).most_common(1)[0][0]
        if bid in forced_icons: tri = 'icon'
        Image.fromarray(r0, 'RGBA').save(out / 'png' / (bid + '.png'))
        ext = o0['fmt'] if o0['fmt'] in ('png', 'jpeg', 'gif', 'webp', 'bmp', 'tiff') else 'bin'
        (out / 'raw' / ('%s.%s' % (bid, ext))).write_bytes(o0['_data'])
        reps[bid] = r0
        disp = sorted(m[0]['disp_pt'] for m in members)[len(members) // 2]
        entries.append({'bid': bid, 'triage': tri, 'stats': o0['stats'], 'occurrences': len(members),
                        'figures': sorted({m[0]['fig'] for m in members}), 'size_px': [int(r0.shape[1]), int(r0.shape[0])],
                        'disp_pt': disp, 'png': 'png/%s.png' % bid, 'raw': 'raw/%s.%s' % (bid, ext),
                        'cropped': any(m[0]['cropped'] for m in members), 'svg': None, 'trace': None, 'trace_ok': False,
                        'contexts': [{k: m[0][k] for k in ('fig', 'file', 'idx', 'bbox_pt', 'disp_pt', 'natural_px', 'fmt', 'data_sha1', 'texts')}
                                     for m in members][:30]})
    print('unique bitmaps: %d  %s' % (len(entries), dict(collections.Counter(e['triage'] for e in entries))), flush=True)
    traces = {}
    if not a.no_trace:
        icons = [e for e in entries if e['triage'] == 'icon']
        jobs = []
        for e in icons:
            svg, info = T.trace_rgba(reps[e['bid']], e['disp_pt'][0], e['disp_pt'][1])
            if not svg: e['trace'] = {'error': info.get('error')}; continue
            svg = svg.replace('data-traced="1"', 'data-traced="%s"' % e['bid'])
            (out / 'svg' / (e['bid'] + '.svg')).write_text(svg, encoding='utf-8')
            e['svg'] = 'svg/%s.svg' % e['bid']; e['trace'] = {'layers': info['layers'], 'colors': info['colors'], 'bytes': len(svg)}
            jobs.append((e, svg))
        rendered = render_svgs_to([(svg, tuple(e['size_px']), e['disp_pt'][0]) for e, svg in jobs])
        for (e, _svg), v in zip(jobs, rendered):
            traces[e['bid']] = v
            e['trace']['ssim'], e['trace']['mae'] = score(reps[e['bid']], v)
            e['trace_ok'] = e['trace']['ssim'] >= TRACE_SSIM_OK and e['trace']['mae'] <= TRACE_MAE_OK
        print('traced %d icons, %d pass (ssim >= %.2f, err <= %.0f)' % (len(jobs), sum(1 for e, _ in jobs if e['trace_ok']), TRACE_SSIM_OK, TRACE_MAE_OK), flush=True)
    order = {'icon': 0, 'gradient': 1, 'photo': 2, 'effect': 3, 'flat': 4, 'tiny': 5}
    entries.sort(key=lambda e: (order.get(e['triage'], 9), -e['occurrences'], e['bid']))
    icon_sheets = sheets([e for e in entries if e['triage'] == 'icon'], reps, traces, out / 'sheets', 'icons', True)
    other_sheets = sheets([e for e in entries if e['triage'] != 'icon'], reps, traces, out / 'sheets', 'other', False)
    idx = {'version': 1, 'package': pkg.name, 'placements': len(occ), 'unique': len(entries),
           'by_triage': dict(collections.Counter(e['triage'] for e in entries)),
           'traced_ok': sum(1 for e in entries if e['trace_ok']), 'sheets': {'icons': icon_sheets, 'other': other_sheets},
           'thresholds': {'ssim': TRACE_SSIM_OK, 'mae': TRACE_MAE_OK}, 'entries': entries}
    (out / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    print('done in %.1f min -> %s  (%d icon sheets, %d other sheets)' % ((time.time() - t0) / 60, out, len(icon_sheets), len(other_sheets)))


if __name__ == '__main__':
    main()
