#!/usr/bin/env python3
"""Small coordinate edits on a contract SVG without hand-patching numbers: shift whole groups, snap edge ends.

  python3 scripts/svg_edit.py shift fig.svg --ids n:block,n:layers --dy -12 [--dx 0] [--with-edges] [--dry-run] [-o out.svg]
  python3 scripts/svg_edit.py bbox  fig.svg [--ids n:block,c:flash]          # measured boxes (pt) of groups, via Chromium

shift  moves every element inside the named groups (`n:`, `c:`, `l:`, `s:`, `a:`, `e:`, `legend`, or any id) by dx/dy:
       x/y/cx/cy/x1/y1/x2/y2 attributes, rect/text/circle/line/ellipse/image/use, polyline/polygon points, absolute path
       commands (M L H V C S Q T A; a leading relative m), and rotate(a cx cy) centres. Relative path segments and
       translate() transforms need no change. --with-edges also moves the touching end of every edge whose
       data-from / data-to names a shifted node (two-point `M x,y L x,y` paths and <line>s; anything else is listed for
       manual re-routing). Step badges (s:*) are not moved: pass their ids explicitly.
bbox   prints the boxes lint.py would use, so you can plan a shift in pt.
Always re-run check.py afterwards; the spec/plan must be updated by hand (the script edits the SVG only).
"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K
from lxml import etree

NS = 'http://www.w3.org/2000/svg'
NUM = K.NUM
CMD = re.compile(r'([MLHVCSQTAZmlhvcsqtaz])([^MLHVCSQTAZmlhvcsqtaz]*)')
ARITY = {'M': 2, 'L': 2, 'T': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'A': 7, 'Z': 0}


def fmt(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') if isinstance(v, float) else str(v)


def shift_d(d, dx, dy):
    out = []; first = True
    for cmd, body in CMD.findall(d):
        nums = [float(x) for x in NUM.findall(body)]
        up = cmd.upper(); n = ARITY.get(up, 0)
        if up == 'Z': out.append(cmd); first = False; continue
        if cmd.islower():
            if first and cmd == 'm' and len(nums) >= 2: nums[0] += dx; nums[1] += dy   # a leading relative m is absolute
            out.append(cmd + ' '.join(fmt(v) for v in nums)); first = False; continue
        if n and len(nums) >= n:
            for i in range(0, len(nums) - n + 1, n):
                if up in ('M', 'L', 'T', 'S', 'Q', 'C'):
                    for j in range(0, n, 2): nums[i + j] += dx; nums[i + j + 1] += dy
                elif up == 'H': nums[i] += dx
                elif up == 'V': nums[i] += dy
                elif up == 'A': nums[i + 5] += dx; nums[i + 6] += dy
        out.append(cmd + ' '.join(fmt(v) for v in nums)); first = False
    return ' '.join(out)


def shift_transform(t, dx, dy):
    def rot(m):
        parts = [float(x) for x in NUM.findall(m.group(1))]
        if len(parts) == 3: parts[1] += dx; parts[2] += dy
        return 'rotate(' + ' '.join(fmt(v) for v in parts) + ')'
    return re.sub(r'rotate\(([^)]*)\)', rot, t)


def shift_element(el, dx, dy):
    tag = etree.QName(el).localname
    for attr, d in (('x', dx), ('y', dy), ('cx', dx), ('cy', dy), ('x1', dx), ('y1', dy), ('x2', dx), ('y2', dy)):
        v = el.get(attr)
        if v is not None and NUM.fullmatch(v.strip()): el.set(attr, fmt(float(v) + d))
    if tag == 'path' and el.get('d'): el.set('d', shift_d(el.get('d'), dx, dy))
    if tag in ('polyline', 'polygon') and el.get('points'):
        nums = [float(x) for x in NUM.findall(el.get('points'))]
        el.set('points', ' '.join(f'{fmt(nums[i] + dx)},{fmt(nums[i + 1] + dy)}' for i in range(0, len(nums) - 1, 2)))
    if el.get('transform') and 'rotate' in el.get('transform'): el.set('transform', shift_transform(el.get('transform'), dx, dy))


def find(root, ident):
    hits = root.xpath(f'//*[@id="{ident}"]')
    return hits[0] if hits else None


def cmd_shift(a):
    p = Path(a.svg); tree = etree.parse(str(p), etree.XMLParser(huge_tree=True)); root = tree.getroot()   # huge_tree: inlined bitmaps
    ids = [i.strip() for i in a.ids.split(',') if i.strip()]
    moved_nodes = set(); n_el = 0
    for ident in ids:
        el = find(root, ident)
        if el is None: print(f'warning: no element with id "{ident}"', file=sys.stderr); continue
        for e in el.iter():
            if isinstance(e.tag, str): shift_element(e, a.dx, a.dy); n_el += 1
        if ident.startswith(('n:', 'c:', 'l:')): moved_nodes.add(ident[2:])
        print(f'shifted {ident} by ({a.dx:g}, {a.dy:g})')
    if a.with_edges and moved_nodes:
        for g in root.iter(f'{{{NS}}}g'):
            if g.get('data-kind') != 'edge': continue
            frm, to = g.get('data-from'), g.get('data-to')
            if frm not in moved_nodes and to not in moved_nodes: continue
            if g.get('id') in ids: continue                       # already moved as a whole
            main = next((c for c in g if isinstance(c.tag, str) and etree.QName(c).localname in ('path', 'line')), None)
            if main is None: continue
            tag = etree.QName(main).localname
            if tag == 'line':
                if frm in moved_nodes: main.set('x1', fmt(float(main.get('x1')) + a.dx)); main.set('y1', fmt(float(main.get('y1')) + a.dy))
                if to in moved_nodes: main.set('x2', fmt(float(main.get('x2')) + a.dx)); main.set('y2', fmt(float(main.get('y2')) + a.dy))
                print(f'  moved end(s) of {g.get("id")}')
            else:
                m = re.fullmatch(r'\s*M\s*([-\d.]+)[ ,]([-\d.]+)\s*L\s*([-\d.]+)[ ,]([-\d.]+)\s*', main.get('d') or '')
                if not m: print(f'  {g.get("id")} touches a moved node but is not a two-point path: re-route it by hand', file=sys.stderr); continue
                x1, y1, x2, y2 = (float(v) for v in m.groups())
                if frm in moved_nodes: x1 += a.dx; y1 += a.dy
                if to in moved_nodes: x2 += a.dx; y2 += a.dy
                main.set('d', f'M{fmt(x1)},{fmt(y1)} L{fmt(x2)},{fmt(y2)}'); print(f'  moved end(s) of {g.get("id")}')
    if a.dry_run: print(f'dry run: {n_el} element(s) would change; nothing written'); return
    out = Path(a.out) if a.out else p
    tree.write(str(out), encoding='utf-8', xml_declaration=False)
    print(f'wrote {out} ({n_el} element(s) changed); re-run check.py and update plan/spec')


def cmd_bbox(a):
    svg = Path(a.svg).read_text(encoding='utf-8'); data = K.measure(svg, base_dir=Path(a.svg).resolve().parent)
    want = {i.strip() for i in (a.ids or '').split(',') if i.strip()}
    for e in data['elements']:
        if e['tag'] != 'g' or not e.get('id'): continue
        if want and e['id'] not in want: continue
        print(f'{e["id"]:24s} x {e["x"]:7.1f}  y {e["y"]:7.1f}  w {e["w"]:6.1f}  h {e["h"]:6.1f}   (right {e["x"] + e["w"]:.1f}, bottom {e["y"] + e["h"]:.1f})')


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('shift'); s.add_argument('svg'); s.add_argument('--ids', required=True); s.add_argument('--dx', type=float, default=0.0); s.add_argument('--dy', type=float, default=0.0)
    s.add_argument('--with-edges', action='store_true'); s.add_argument('--dry-run', action='store_true'); s.add_argument('-o', '--out'); s.set_defaults(fn=cmd_shift)
    b = sub.add_parser('bbox'); b.add_argument('svg'); b.add_argument('--ids'); b.set_defaults(fn=cmd_bbox)
    a = ap.parse_args(); a.fn(a)


if __name__ == '__main__':
    main()
