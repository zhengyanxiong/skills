#!/usr/bin/env python3
"""Render an SVG figure to PNG with headless Chromium (fonts from assets/fonts injected automatically; bitmaps
linked by a relative path are loaded from the SVG's folder, URLs are never fetched).

  python3 scripts/render.py fig.svg [-o fig.png] [--scale 3] [--crop x0,y0,x1,y1] [--bbox fig.bbox.json] [--no-fonts]

--scale   pixels per pt (3 = 216 dpi, good for looking at the figure; use 6 for zooming into details)
--crop    keep only the region x0,y0,x1,y1 (pt, viewBox units): the way to LOOK closely at one crossing or one
          label without the whole figure — e.g. `--scale 6 --crop 220,110,296,176` around a divider
--bbox    also write the per-element geometry Chromium measured (what lint.py uses)
Exit code 0 on success. The PNG is what the agent LOOKS AT during self-check: open it with your image-viewing tool.
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('-o', '--out'); ap.add_argument('--scale', type=float, default=3.0)
    ap.add_argument('--crop', help='x0,y0,x1,y1 in pt: crop the PNG to that region'); ap.add_argument('--bbox', help='write element geometry JSON'); ap.add_argument('--no-fonts', action='store_true')
    a = ap.parse_args()
    svg = Path(a.svg).read_text(encoding='utf-8')
    out = Path(a.out) if a.out else Path(a.svg).with_suffix('.png')
    crop = None
    if a.crop:
        v = [float(x) for x in K.NUM.findall(a.crop)]
        if len(v) != 4 or v[2] <= v[0] or v[3] <= v[1]: raise SystemExit('--crop needs x0,y0,x1,y1 in pt with x1 > x0 and y1 > y0')
        crop = tuple(v)
    K.render_png(svg, out, scale=a.scale, embed_fonts=not a.no_fonts, crop=crop, base_dir=Path(a.svg).resolve().parent)
    vb = K.parse_viewbox(svg)
    what = f'{crop[0]:g},{crop[1]:g}–{crop[2]:g},{crop[3]:g} pt of ' if crop else ''
    print(f'wrote {out}  ({what}{vb[2]:.1f} x {vb[3]:.1f} pt at {a.scale} px/pt)' if vb else f'wrote {out}')
    if a.bbox:
        data = K.measure(svg, embed_fonts=not a.no_fonts, base_dir=Path(a.svg).resolve().parent)
        Path(a.bbox).write_text(json.dumps(data, indent=1), encoding='utf-8')
        missing = [f for f, ok in data['fonts'].items() if not ok and f.lower() not in ('sans-serif', 'serif', 'monospace')]
        print(f'measured {len(data["elements"])} elements; fonts not resolved: {missing or "none"}')


if __name__ == '__main__':
    main()
