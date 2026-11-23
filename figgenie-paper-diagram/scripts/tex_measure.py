#!/usr/bin/env python3
"""Measure TeX formulas (and mixed text + formula lines) in pt before drawing, like measure_text.py.

  python3 scripts/tex_measure.py --size 6.5 '\\hat{J}(\\theta)' 'B_t'          # width / ascent / descent per formula
  python3 scripts/tex_measure.py --size 6.5 --box 'w_i=\\frac{a}{b}'           # + the box that holds it (w+8, h+6)
  python3 scripts/tex_measure.py --mixed 'Sampler $p_\\theta(x)$' --size 6.5 --bold \\
          --x 54 --y 24 --anchor middle --emit                                     # a label with inline formulas → SVG snippet

Numbers come from MathJax's own metrics (scripts/mathjax, TeX fonts), so they match what tex_fill.py draws.
A mixed line is split on $…$; text runs are measured with measure_text.py's fonts (--font / --cjk keys from
assets/fonts/fonts.json), formula runs with MathJax, and --gap pt (default 1.5) is left between runs.
--emit prints the <text> and <g data-symbol="tex"> elements to paste into the node's group; run tex_fill.py
afterwards to render the placeholders.
"""
import argparse, html, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _texkit as T
import measure_text as MT
import _svgkit as K


def measure_formulas(texs, size, display=False):
    jobs = {str(i): {'tex': t, 'display': display} for i, t in enumerate(texs)}
    res = T.render_svg(jobs)
    out = []
    for i, t in enumerate(texs):
        r = res[str(i)]
        if 'error' in r:
            out.append(dict(tex=t, error=r['error']))
        else:
            xoff, w, asc, desc = T.metrics(r['svg'], size)
            out.append(dict(tex=t, w=w, asc=asc, desc=desc))
    return out


def split_mixed(line):
    """'text $tex$ text' → [('t', text), ('f', tex), …] with outer whitespace trimmed from text runs."""
    parts, pos = [], 0
    for m in re.finditer(r'\$(.+?)\$', line):
        if m.start() > pos:
            t = line[pos:m.start()].strip()
            if t: parts.append(('t', t))
        parts.append(('f', m.group(1)))
        pos = m.end()
    tail = line[pos:].strip()
    if tail: parts.append(('t', tail))
    return parts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tex', nargs='*', help='TeX formulas (MathJax syntax)')
    ap.add_argument('--size', type=float, default=6.5, help='font size in pt (the em of the formula)')
    ap.add_argument('--display', action='store_true', help='display style (\\sum limits above/below, larger fractions)')
    ap.add_argument('--box', action='store_true', help='also print the box that holds it: width + 8, height + 6')
    ap.add_argument('--mixed', help="a label with inline formulas, e.g. 'Sampler $p_\\theta(x)$'")
    ap.add_argument('--font', default=None, help='Latin font key for text runs (default: helvetica)')
    ap.add_argument('--cjk', default=None, help='CJK font key for text runs (default: fonts.json cjk_default)')
    ap.add_argument('--bold', action='store_true', help='text runs in bold')
    ap.add_argument('--gap', type=float, default=1.5, help='gap in pt between runs of a mixed line')
    ap.add_argument('--x', type=float, default=0.0, help='anchor x of the mixed line')
    ap.add_argument('--y', type=float, default=0.0, help='baseline y of the mixed line')
    ap.add_argument('--anchor', default='start', choices=['start', 'middle', 'end'])
    ap.add_argument('--fill', default=None, help='colour for the emitted elements (default: inherit)')
    ap.add_argument('--emit', action='store_true', help='print the SVG elements of the mixed line')
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    a = ap.parse_args()

    if a.mixed:
        parts = split_mixed(a.mixed)
        fkey = a.font or K.load_fonts().get('default', 'helvetica')
        ckey = a.cjk or K.cjk_default_key()
        fm = measure_formulas([p[1] for p in parts if p[0] == 'f'], a.size, a.display)
        widths, fi, bad = [], 0, False
        for kind, s in parts:
            if kind == 't':
                widths.append(MT.width_of(s, fkey, a.size, bold=a.bold, cjk_key=ckey)[0])
            else:
                r = fm[fi]; fi += 1
                if 'error' in r:
                    print(f'ERROR  {r["tex"]!r}: {r["error"]}', file=sys.stderr); bad = True; widths.append(0)
                else:
                    widths.append(r['w'])
        total = sum(widths) + a.gap * (len(parts) - 1)
        x = {'start': a.x, 'middle': a.x - total / 2, 'end': a.x - total}[a.anchor]
        rows, snippets = [], []
        fill = f' fill="{a.fill}"' if a.fill else ''
        for (kind, s), w in zip(parts, widths):
            rows.append(dict(kind='text' if kind == 't' else 'tex', text=s, x=round(x, 2), w=round(w, 2)))
            if kind == 't':
                bold = ' font-weight="bold"' if a.bold else ''
                # font-size is always written: the run was measured at --size, and the root font-size may differ
                snippets.append(f'<text x="{x:.2f}" y="{a.y:.2f}" font-size="{a.size:g}"{bold}{fill}>{html.escape(s)}</text>')
            else:
                snippets.append(f'<g data-symbol="tex" data-tex="{html.escape(s, quote=True)}" data-x="{x:.2f}" data-y="{a.y:.2f}" '
                                f'data-size="{a.size:g}" data-anchor="start"{(" data-fill=" + chr(34) + a.fill + chr(34)) if a.fill else ""}/>')
            x += w + a.gap
        if a.json:
            print(json.dumps(dict(total=round(total, 2), runs=rows, svg=snippets), ensure_ascii=False, indent=1))
        else:
            print(f'mixed line: total width {total:.1f} pt at {a.size:g} pt, anchor {a.anchor} at x={a.x:g}  (box ≥ {total + 8:.0f}×{1.4 * a.size + 6:.0f})')
            for r in rows:
                print(f'  {r["kind"]:4s} x={r["x"]:7.2f}  w={r["w"]:6.2f}  {r["text"]}')
            if a.emit:
                print('\n'.join(snippets))
        sys.exit(1 if bad else 0)

    if not a.tex:
        ap.error('give at least one TeX formula, or --mixed')
    res = measure_formulas(a.tex, a.size, a.display)
    bad = False
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    for r in res:
        if 'error' in r:
            print(f'ERROR  {r["tex"]!r}: {r["error"]}'); bad = True; continue
        line = f'{r["w"]:7.2f} w  {r["asc"]:5.2f} asc  {r["desc"]:5.2f} desc  {r["tex"]!r}  [{a.size:g}pt{" display" if a.display else ""}]'
        if a.box:
            line += f'  box ≥ {r["w"] + 8:.0f}×{r["asc"] + r["desc"] + 6:.0f}'
        if not a.json:
            print(line)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
