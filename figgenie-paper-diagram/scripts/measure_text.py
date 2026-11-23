#!/usr/bin/env python3
"""Measure text widths in pt before drawing, so boxes are sized to their labels.

  python3 scripts/measure_text.py --font helvetica --size 7 "Span Parser" "Params Buffer" ...
  python3 scripts/measure_text.py --font source-sans --size 6.5 "KV 缓存" "请求解析"     # CJK measured with the CJK companion
  python3 scripts/measure_text.py --json labels.json          # [{"text": "...", "size": 7, "font": "arial", "bold": false}, ...]

Prints one line per label: width_pt height_pt  text  [font size]. Widths come from the font files (PIL / FreeType),
so they match what Chromium renders with the same faces embedded. Mixed text is split into script runs: Latin runs
use --font, CJK runs use --cjk (default: fonts.json `cjk_default`, resolved from the system; if the file is not
installed, CJK glyphs are estimated at 1 em each and the line is marked "~").
Rule of thumb for a box: width = text + 2*4 pt padding, height = 1.4 * size per line + 2*3 pt (--box prints it).
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K


def _face(key, bold=False, italic=False):
    files = K.font_files(key) if key else {}
    w = 'bolditalic' if bold and italic else 'bold' if bold else 'italic' if italic else 'regular'
    return files.get(w) or (files.get('bold') if bold else None) or files.get('regular')


def width_of(text, key, size, bold=False, italic=False, cjk_key=None):
    """(width_pt, estimated: bool) of one line; CJK runs measured with cjk_key, Latin runs with key."""
    from PIL import ImageFont
    total, estimated = 0.0, False
    for script, run in K.script_runs(text):
        k = cjk_key if script == 'cjk' else key
        p = _face(k, bold, italic)
        if p is None:
            estimated = True
            total += size * sum((1.0 if script == 'cjk' else 0.52) if not c.isspace() else 0.26 for c in run)
            continue
        font = ImageFont.truetype(str(p), size=int(round(size * 10)), index=0)   # 10x for precision
        total += font.getlength(run) / 10.0
    return total, estimated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('text', nargs='*'); ap.add_argument('--font', default=None); ap.add_argument('--size', type=float, default=7.0)
    ap.add_argument('--bold', action='store_true'); ap.add_argument('--json'); ap.add_argument('--cjk', default=None, help='font key for CJK runs (default: fonts.json cjk_default)')
    ap.add_argument('--no-cjk', action='store_true', help='measure CJK runs with --font too'); ap.add_argument('--box', action='store_true', help='also print the suggested box size')
    a = ap.parse_args()
    fonts = K.load_fonts(); key = a.font or fonts['default']
    if key not in fonts['families']: key = K.resolve_font(key)
    cjk = None if a.no_cjk else (a.cjk or K.cjk_default_key())
    if cjk and cjk not in fonts['families']: cjk = K.resolve_font(cjk)
    items = [dict(text=t, size=a.size, font=key, bold=a.bold) for t in a.text]
    if a.json: items += json.loads(Path(a.json).read_text(encoding='utf-8'))
    any_est = False
    for it in items:
        k = it.get('font') or key
        if k not in fonts['families']: k = K.resolve_font(k)
        lines = it['text'].split('\n'); size = it.get('size', a.size)
        ws = [width_of(l, k, size, it.get('bold', False), it.get('italic', False), cjk) for l in lines]
        w = max(x[0] for x in ws); est = any(x[1] for x in ws); any_est |= est
        h = 1.2 * size * len(lines)
        tag = f'{k}{"+" + cjk if cjk and K.has_cjk(it["text"]) else ""} {size}pt{" bold" if it.get("bold") else ""}'
        extra = f'  box ≥ {w + 8:.0f}×{1.4 * size * len(lines) + 6:.0f}' if a.box else ''
        print(f'{w:7.2f}{"~" if est else " "}{h:6.2f}  {it["text"]!r}  [{tag}]{extra}')
    if any_est:
        print('~ = estimated (font file not found: CJK 1 em/char, Latin 0.52 em/char); install the font or pick another key', file=sys.stderr)


if __name__ == '__main__':
    main()
