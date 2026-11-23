#!/usr/bin/env python3
"""Render the TeX placeholders of a figure into vector paths (MathJax), in place.

  python3 scripts/tex_fill.py fig.svg                 # fill / refresh every <g data-symbol="tex"> from its data-tex
  python3 scripts/tex_fill.py fig.svg --check         # + overflow / overlap report for the formulas (exit 1 on errors)
  python3 scripts/tex_fill.py fig.svg -o out.svg      # write elsewhere
  python3 scripts/tex_fill.py fig.svg --strip         # back to bare placeholders (small diffs, re-fill later)

Placeholder contract (see references/formulas.md):
  <g data-symbol="tex" data-tex="\\hat{J}(\\theta)" data-x="54" data-y="24" data-size="6.5" data-anchor="middle"/>
Re-running is idempotent: the paths are regenerated from data-tex, the recorded box (data-w/asc/desc/baseline)
is refreshed, and nothing else in the file is touched. Run it before check.py whenever placeholders were added
or their TeX edited; the linter then sees the real ink.
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _texkit as T
import measure_text as MT
import _svgkit as K
from lxml import etree

SVG = '{%s}' % T.SVG_NS


def contract_group(el):
    """Nearest ancestor group carrying a contract id (n:, c:, a:, legend …)."""
    p = el.getparent()
    while p is not None:
        if p.tag == SVG + 'g' and p.get('id'):
            return p
        p = p.getparent()
    return None


def first_rect(g):
    for ch in g:
        if ch.tag == SVG + 'rect':
            try:
                x, y, w, h = (float(ch.get(k)) for k in ('x', 'y', 'width', 'height'))
                return (x, y, x + w, y + h)
            except (TypeError, ValueError):
                return None
    return None


def text_boxes(g, root, fkey, ckey):
    """Approximate ink boxes of the <text> children of a group (0.75 em above / 0.25 em below the baseline)."""
    out = []
    rs = float(root.get('font-size') or 6.5)
    for t in g.iter(SVG + 'text'):
        if t.get('transform'):
            continue
        s = ''.join(t.itertext())
        try:
            x, y = float(t.get('x')), float(t.get('y'))
        except (TypeError, ValueError):
            continue
        size = float(t.get('font-size') or T.inherited(t, 'font-size') or rs)
        w = MT.width_of(s, fkey, size, bold=(t.get('font-weight') == 'bold'), cjk_key=ckey)[0]
        anc = t.get('text-anchor') or 'start'
        x0 = {'start': x, 'middle': x - w / 2, 'end': x - w}.get(anc, x)
        out.append((s, (x0, y - 0.75 * size, x0 + w, y + 0.25 * size)))
    return out


def inter(a, b, pad=0.0):
    return a[0] < b[2] - pad and b[0] < a[2] - pad and a[1] < b[3] - pad and b[1] < a[3] - pad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('svg')
    ap.add_argument('-o', '--out')
    ap.add_argument('--check', action='store_true', help='report formulas that leave their box or collide with labels')
    ap.add_argument('--strip', action='store_true', help='remove the rendered paths, keep the placeholders')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    tree = T.parse(a.svg); root = tree.getroot()
    out = a.out or a.svg
    groups = T.placeholders(root)
    if not groups:
        print(f'{a.svg}: no <g data-symbol="tex"> placeholders')
        if a.out: T.write(tree, out)
        return 0
    if a.strip:
        for g in groups: T.strip_group(g)
        T.write(tree, out); print(f'stripped {len(groups)} formula(s) → {out}')
        return 0

    params = [T.params(g, root) for g in groups]
    jobs = {str(i): {'tex': p['tex'], 'display': p['display']} for i, p in enumerate(params)}
    res = T.render_svg(jobs)
    errors, boxes = 0, []
    for i, (g, p) in enumerate(zip(groups, params)):
        r = res[str(i)]
        cg = contract_group(g); where = cg.get('id') if cg is not None else '(top level)'
        if 'error' in r:
            errors += 1
            print(f'  [error] {where}: TeX {p["tex"]!r}: {r["error"]}')
            boxes.append(None); continue
        box = T.fill_group(g, r['svg'], p)
        boxes.append(box)
        if not a.quiet:
            print(f'  {where:18s} {p["tex"][:46]!r:50s} w={box[2]-box[0]:6.2f} asc={float(g.get("data-asc")):5.2f} '
                  f'desc={float(g.get("data-desc")):5.2f} @{p["size"]:g}pt {p["anchor"]}' + (' valign=middle' if p['valign'] == 'middle' else ''))
    T.write(tree, out)
    print(f'filled {len(groups) - errors}/{len(groups)} formula(s) → {out}')

    if a.check:
        keys = K.keys_for_svg(etree.tostring(root, encoding='unicode'))
        fkey = next((k for k in keys if not K.is_cjk_key(k)), None) or K.load_fonts().get('default', 'helvetica')
        ckey = next((k for k in keys if K.is_cjk_key(k)), None) or K.cjk_default_key()
        warns = 0
        for g, p, box in zip(groups, params, boxes):
            if box is None: continue
            cg = contract_group(g)
            if cg is None: continue
            gid = cg.get('id')
            rect = first_rect(cg)
            if rect is not None and (cg.get('data-kind') in ('node', 'container', 'annotation', 'legend') or gid.startswith(('n:', 'c:', 'a:'))):
                x0, y0, x1, y1 = rect
                if box[0] < x0 - 0.5 or box[1] < y0 - 0.5 or box[2] > x1 + 0.5 or box[3] > y1 + 0.5:
                    errors += 1; print(f'  [error] tex.overflow  {p["tex"][:40]!r} leaves the box of {gid} '
                                       f'(formula {box[0]:.1f}–{box[2]:.1f} × {box[1]:.1f}–{box[3]:.1f}, box {x0:.0f}–{x1:.0f} × {y0:.0f}–{y1:.0f})')
                elif box[0] < x0 + 1.5 or box[1] < y0 + 1.5 or box[2] > x1 - 1.5 or box[3] > y1 - 1.5:
                    warns += 1; print(f'  [warn ] tex.padding   {p["tex"][:40]!r} has < 1.5 pt padding inside {gid}')
            for s, tb in text_boxes(cg, root, fkey, ckey):
                if inter(box, tb, 0.3):
                    errors += 1; print(f'  [error] tex.overlap   {p["tex"][:40]!r} overlaps label "{s[:30]}" in {gid}')
        n = len(groups)
        for i in range(n):
            for j in range(i + 1, n):
                if boxes[i] and boxes[j] and contract_group(groups[i]) is contract_group(groups[j]) and inter(boxes[i], boxes[j], 0.3):
                    errors += 1; print(f'  [error] tex.overlap   {params[i]["tex"][:30]!r} overlaps {params[j]["tex"][:30]!r}')
        print(f'check: {errors} error(s), {warns} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
