#!/usr/bin/env python3
"""Embed (or strip) the open fonts an SVG uses, and inline its bitmaps, so it renders identically everywhere.

  python3 scripts/embed_fonts.py fig.svg [-o fig.embedded.svg] [--font helvetica] [--cjk source-han-sans] [--no-cjk]
                                        [--no-subset] [--strip] [--strict]

* Finds every font-family the SVG references, maps it through assets/fonts/fonts.json (Arial -> Arimo,
  Calibri -> Carlito, Helvetica -> TeX Gyre Heros, Times -> Tinos, Computer Modern -> Latin Modern ...),
  rewrites the first family of each stack to the shipped font's css family (keeping the rest of the stack and
  adding the shipped fallbacks), and inserts one <style> block with @font-face data URIs inside <defs>.
* CJK: when the text contains CJK characters, the CJK companion (a `script: cjk` family named in a stack, else
  --cjk / fonts.json `cjk_default`, e.g. Source Han Sans resolved from the system) is subsetted, embedded, and its
  css family is inserted into every stack right after the Latin family, so the embedded face is the one that renders.
* With fonttools installed (`pip install fonttools`) each font is subsetted to the characters the figure
  uses (typically 15-40 KB per face instead of 100-800 KB; a CJK subset is ~20-60 KB). Without it the shipped
  files are embedded whole and system-resolved CJK faces are skipped with a note.
* Glyph coverage: after embedding, every character is checked against the embedded faces; uncovered ones are
  reported (exit 1 with --strict) because they would fall back to an arbitrary system font.
* --font KEY forces one Latin family for the whole figure (e.g. the spec's meta.font).
* Bitmaps (2026-09-28): every <image> linked to a local PNG / JPEG file (a path relative to the SVG, or a file: URL)
  is inlined byte for byte as a base64 data URI, the way the fonts are embedded, so the delivered SVG is one
  self-contained file; data URIs are kept. The link is written as xlink:href (xmlns:xlink declared on the root),
  the SVG 1.1 form that Office, Illustrator and older Inkscape read. Nothing is written, and the exit code is 1,
  while any image links to a URL, points at a missing or undecodable file, or is not PNG / JPEG.
* --strip removes a previously embedded font block (useful before hand-editing in an SVG editor); inlined bitmaps
  stay, they are content.
In-place when -o is omitted. Deliverable SVGs should be embedded; working copies need not be.
"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K

MARK_START = '<!-- figgenie-paper-diagram:fonts -->'; MARK_END = '<!-- /figgenie-paper-diagram:fonts -->'


def strip_block(svg):
    # also strips blocks written under the skill's earlier names (sys-arch-diagram, sys-paper-diagram)
    return re.sub(r'<!-- (figgenie-paper-diagram|sys-paper-diagram|sys-arch-diagram):fonts -->.*?<!-- /\1:fonts -->', '', svg, flags=re.S)


def _split_stack(raw):
    return [K.clean_family(p) for p in raw.split(',') if K.clean_family(p)]


def _join_stack(fams):
    out = []
    for f in fams:
        if f in out: continue
        out.append(f)
    return ', '.join(f"'{f}'" if (' ' in f or not f.isascii()) else f for f in out)


def rewrite_stacks(svg, mapping, cjk_key):
    """Replace the first family of every font-family stack by its shipped css family, keep the user's other
    families, insert the CJK css family after the first, and append the shipped fallbacks."""
    fonts = K.load_fonts()
    def repl(m):
        prefix, q, raw = m.group(1), m.group(2), m.group(3)
        fams = _split_stack(raw)
        if not fams: return m.group(0)
        first = fams[0]; key = mapping.get(first)
        new = list(fams)
        if key:
            fam = fonts['families'][key]; new[0] = fam['css_family']
            new += _split_stack(fam['stack'])
        if cjk_key:
            cjk_css = fonts['families'][cjk_key]['css_family']
            new = [n for n in new if n != cjk_css]; new.insert(1, cjk_css)
        generic = [g for g in re.split(r'\s*,\s*', raw) if K.clean_family(g).lower() in K.GENERIC]
        stack = _join_stack(new) + (', ' + K.clean_family(generic[-1]) if generic else '')
        return f'{prefix}{q}{stack}{q}'
    return re.sub(r'(font-family\s*[:=]\s*)(["\'])([^"\']*)\2', repl, svg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('-o', '--out'); ap.add_argument('--font', help='force one Latin font key for all text')
    ap.add_argument('--cjk', help='font key for CJK glyphs (default: a cjk family named in the SVG, else fonts.json cjk_default)')
    ap.add_argument('--no-cjk', action='store_true'); ap.add_argument('--no-subset', action='store_true'); ap.add_argument('--strip', action='store_true')
    ap.add_argument('--strict', action='store_true', help='exit 1 when some characters are not covered by the embedded faces')
    a = ap.parse_args()
    p = Path(a.svg); svg = strip_block(p.read_text(encoding='utf-8'))
    out = Path(a.out) if a.out else p
    if a.strip:
        out.write_text(svg, encoding='utf-8'); print(f'stripped embedded fonts -> {out}'); return
    svg, images, problems = K.inline_images(svg, base_dir=p.resolve().parent)
    if problems:
        for msg in problems: print(f'error: {msg}', file=sys.stderr)
        sys.exit(f'nothing written: a delivered figure carries every bitmap inside the SVG as a PNG / JPEG '
                 f'({len(problems)} image problem(s) above)')
    fonts = K.load_fonts()
    fams = K.families_in_svg(svg)
    mapping = {}
    for f in fams:
        key = a.font or K.resolve_font(f)
        if key and K.font_files(key) and K.font_is_shipped(key): mapping[f] = key
    keys = sorted({k for k in mapping.values()})
    if a.font and not fams: keys = [a.font]
    text = K.svg_text_content(svg)
    cjk_key = None
    if not a.no_cjk and K.has_cjk(text):
        cjk_key = a.cjk
        if not cjk_key:
            for f in K.all_families_in_svg(svg):
                k = K.resolve_font(f, default=False)
                if k and K.is_cjk_key(k): cjk_key = k; break
        cjk_key = cjk_key or K.cjk_default_key()
        if not K.font_files(cjk_key):
            print(f'warning: the text has CJK characters but no file for "{cjk_key}" was found in the system font dirs; '
                  f'install Source Han Sans / Noto Sans CJK or pass --cjk KEY. CJK text will use whatever the viewer has.', file=sys.stderr)
            cjk_key = None
        elif cjk_key not in keys: keys.append(cjk_key)
    svg = rewrite_stacks(svg, mapping, cjk_key)
    css = K.font_face_css(keys, text=None if a.no_subset else text)
    if cjk_key and a.no_subset:
        css += ('\n' if css else '') + K.font_face_css([cjk_key], text=text)   # CJK is always subsetted
    if not css:
        print('no shippable font found for', fams or 'no font-family attributes', file=sys.stderr)
    block = f'{MARK_START}<defs><style type="text/css">\n{css}\n</style></defs>{MARK_END}'
    if re.search(r'<svg\b[^>]*>', svg):
        svg = re.sub(r'(<svg\b[^>]*>)', lambda m: m.group(1) + block, svg, count=1)
    out.write_text(svg, encoding='utf-8')
    kb = len(css.encode()) / 1024
    print(f'embedded {", ".join(keys) or "nothing"} ({kb:.0f} KB{", subsetted" if not a.no_subset and _has_fonttools() else ", full files"}) -> {out}')
    if images:
        files = [f'{i["href"]} ({i["format"].upper()}, {i["bytes"] / 1024:.1f} KB)' for i in images if i['inlined']]
        kept = len(images) - len(files)
        print(f'bitmaps: {len(images)} <image>, all inside the SVG now'
              + (f'; inlined {", ".join(files)}' if files else '') + (f'; {kept} already a data URI' if kept else ''))
    unc, faces = K.glyph_coverage(svg, keys)
    if unc is None:
        print('glyph coverage not checked (pip install fonttools)')
    elif unc:
        shown = ' '.join(f'{c}(U+{ord(c):04X})' for c in unc[:12]) + (' …' if len(unc) > 12 else '')
        print(f'warning: {len(unc)} character(s) are in no embedded face and will fall back to a system font: {shown}', file=sys.stderr)
        if a.strict: sys.exit(1)
    else:
        print(f'glyph coverage: all {len(set(c for c in text if not c.isspace()))} distinct characters covered by the embedded faces')


def _has_fonttools():
    try:
        import fontTools  # noqa
        return True
    except ImportError:
        return False


if __name__ == '__main__':
    main()
