#!/usr/bin/env python3
"""pptx_check.py — sanity checks on a deck made by svg2pptx.py (or hand-edited afterwards).

  python3 scripts/pptx_check.py fig.pptx [--svg fig.svg] [--scale 1]

Reports, and exits 1 on errors:
  * paint order: every connector / freeform line that a later, opaque shape covers (the classic
    "background over the arrows" mistake — groups appended on top of the containers);
  * inventory: shapes, connectors, text boxes, native equations, pictures, groups, typefaces, slide size;
  * with --svg: text elements vs text boxes, formula placeholders vs equations, primitives vs shapes,
    <image> elements vs pictures, slide size vs viewBox × scale — anything the export dropped.
A picture counts as opaque for the covering check (a bitmap hides what is under it).
Reads the slide XML directly, so it also understands decks PowerPoint has re-saved (equations hoisted
into mc:AlternateContent) and groups PowerPoint has resized (chOff/chExt mapping).
"""
import argparse, re, sys, zipfile
from lxml import etree

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
EMU = 12700.0


def q(tag):
    p, t = tag.split(':'); return '{%s}%s' % (NS[p], t)


def xfrm_of(el):
    x = el.find('.//' + q('a:xfrm'))
    if x is None: return None
    off, ext = x.find(q('a:off')), x.find(q('a:ext'))
    if off is None or ext is None: return None
    r = dict(x=float(off.get('x')) / EMU, y=float(off.get('y')) / EMU, w=float(ext.get('cx')) / EMU, h=float(ext.get('cy')) / EMU,
             fh=x.get('flipH') == '1', fv=x.get('flipV') == '1', rot=float(x.get('rot') or 0) / 60000.0)
    cho, che = x.find(q('a:chOff')), x.find(q('a:chExt'))
    if cho is not None and che is not None:
        r.update(cx=float(cho.get('x')) / EMU, cy=float(cho.get('y')) / EMU, cw=float(che.get('cx')) / EMU, ch=float(che.get('cy')) / EMU)
    return r


def solid_fill(sp):
    spPr = sp.find(q('p:spPr'))
    if spPr is None: return None
    for ch in spPr:
        t = etree.QName(ch).localname
        if t == 'noFill': return None
        if t == 'solidFill':
            c = ch.find(q('a:srgbClr'))
            return (c.get('val') if c is not None else 'theme')
    # no explicit fill on an autoshape → theme fill (opaque) unless it is a text box
    nv = sp.find('.//' + q('p:cNvSpPr'))
    if nv is not None and nv.get('txBox') == '1': return None
    return 'theme' if sp.tag == q('p:sp') and spPr.find(q('a:custGeom')) is None else None


def line_points(sp, geo):
    """Polyline vertices (pt) of a connector or an open custom-geometry path; None for other shapes."""
    if sp.tag == q('p:cxnSp'):
        x, y, w, h = geo['x'], geo['y'], geo['w'], geo['h']
        p0, p1 = (x, y), (x + w, y + h)
        if geo['fh']: p0, p1 = (x + w, p0[1]), (x, p1[1])
        if geo['fv']: p0, p1 = (p0[0], y + h), (p1[0], y)
        return [p0, p1]
    cg = sp.find('.//' + q('a:custGeom'))
    if cg is None: return None
    path = cg.find('.//' + q('a:path'))
    if path is None: return None
    pw, ph = float(path.get('w') or 1), float(path.get('h') or 1)
    pts = []
    for node in path:
        for pt in node.findall(q('a:pt')):
            pts.append((geo['x'] + float(pt.get('x')) / pw * geo['w'], geo['y'] + float(pt.get('y')) / ph * geo['h']))
    return pts if len(pts) >= 2 else None


def flatten(parent, out, depth, gmap, gname):
    for ch in parent:
        tag = etree.QName(ch).localname
        if tag == 'AlternateContent':
            choice = ch.find(q('mc:Choice'))
            if choice is not None:
                flatten(choice, out, depth, gmap, gname)
            continue
        if tag not in ('sp', 'cxnSp', 'grpSp', 'pic', 'graphicFrame'): continue
        nv = ch.find('.//' + q('p:cNvPr')); name = nv.get('name') if nv is not None else ''
        geo = xfrm_of(ch)
        if geo and gmap:
            geo = remap(geo, gmap)
        if tag == 'grpSp':
            m = None
            if geo and 'cw' in geo and geo['cw'] and geo['ch']:
                m = dict(sx=geo['w'] / geo['cw'], sy=geo['h'] / geo['ch'], ox=geo['x'] - geo['cx'] * geo['w'] / geo['cw'], oy=geo['y'] - geo['cy'] * geo['h'] / geo['ch'])
            flatten(ch, out, depth + 1, compose(gmap, m), name)
            continue
        rec = dict(idx=len(out), tag=tag, name=name, group=gname, geo=geo, depth=depth,
                   text=''.join(t.text or '' for t in ch.iter(q('a:t'))), math=bool(list(ch.iter(q('m:oMath')))),
                   fill=solid_fill(ch) if tag == 'sp' else None)
        rec['pts'] = line_points(ch, geo) if geo else None
        rec['fonts'] = {l.get('typeface') for l in ch.iter(q('a:latin'))} | {l.get('typeface') for l in ch.iter(q('a:ea'))}
        out.append(rec)


def compose(outer, inner):
    if inner is None: return outer
    if outer is None: return inner
    return dict(sx=outer['sx'] * inner['sx'], sy=outer['sy'] * inner['sy'],
                ox=outer['ox'] + inner['ox'] * outer['sx'], oy=outer['oy'] + inner['oy'] * outer['sy'])


def remap(geo, m):
    g = dict(geo); g['x'] = m['ox'] + geo['x'] * m['sx']; g['y'] = m['oy'] + geo['y'] * m['sy']
    g['w'] = geo['w'] * m['sx']; g['h'] = geo['h'] * m['sy']
    return g


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pptx'); ap.add_argument('--svg'); ap.add_argument('--scale', type=float, default=1.0)
    a = ap.parse_args()
    z = zipfile.ZipFile(a.pptx)
    pres = etree.fromstring(z.read('ppt/presentation.xml'))
    sz = pres.find(q('p:sldSz')); sw, sh = float(sz.get('cx')) / EMU, float(sz.get('cy')) / EMU
    slide = etree.fromstring(z.read('ppt/slides/slide1.xml'))
    tree = slide.find('.//' + q('p:cSld')).find(q('p:spTree'))
    recs = []
    flatten(tree, recs, 0, None, '')
    errors, warns, notes = [], [], []

    def gid_of(name):
        return (name or '').split(' ')[0]

    def top_id(r):
        return gid_of(r['group'] or r['name'])

    def fold(seq):                       # legend rows are one deck group; collapse repeats
        out = []
        for g in seq:
            g = 'legend' if g.startswith('legend') else g
            if not out or out[-1] != g: out.append(g)
        return out

    # 0. the SVG's own paint order (document order of the top-level groups)
    svg_root, rank = None, None
    if a.svg:
        svg_root = etree.parse(a.svg, etree.XMLParser(huge_tree=True)).getroot()   # huge_tree: inlined bitmaps
        svg_ids = [g.get('id') for g in svg_root if isinstance(g.tag, str) and etree.QName(g).localname == 'g' and g.get('id')]
        rank = {g: i for i, g in enumerate(fold(svg_ids))}
        deck_ids = []
        for c in tree:
            t = etree.QName(c).localname
            if t in ('nvGrpSpPr', 'grpSpPr', 'extLst'): continue
            if t == 'AlternateContent':
                ch = c.find(q('mc:Choice')); c = ch[0] if ch is not None and len(ch) else c
            nv = c.find('.//' + q('p:cNvPr'))
            deck_ids.append(gid_of(nv.get('name')) if nv is not None else '?')
        d, s_ = fold(deck_ids), fold(svg_ids)
        s_ = [g for g in s_ if g in set(d)]
        d = [g for g in d if g in rank]
        if d != s_:
            first = next((i for i, (x, y) in enumerate(zip(d, s_)) if x != y), min(len(d), len(s_)))
            errors.append(f'paint order differs from the SVG at position {first}: deck has {d[first:first + 3]}, SVG has {s_[first:first + 3]}')

    # 1. lines covered by later opaque shapes (an error only when the SVG draws them the other way round)
    lines = [r for r in recs if r['pts']]
    opaque = [r for r in recs if ((r['tag'] == 'sp' and r['fill']) or r['tag'] == 'pic') and r['geo'] and not r['pts']]
    for l in lines:
        hit = None
        for (x0, y0), (x1, y1) in zip(l['pts'], l['pts'][1:]):
            for t in [k / 20 for k in range(2, 19)]:
                px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                for o in opaque:
                    g = o['geo']
                    if o['idx'] > l['idx'] and g['x'] + 0.6 < px < g['x'] + g['w'] - 0.6 and g['y'] + 0.6 < py < g['y'] + g['h'] - 0.6:
                        hit = (o, px, py); break
                if hit: break
            if hit: break
        if hit:
            o, px, py = hit
            msg = f'line "{l["name"]}" is covered at ({px:.1f},{py:.1f}) by "{o["name"]}" drawn later'
            li, oi = top_id(l), top_id(o)
            if rank is not None and li in rank and oi in rank:
                (errors if rank[oi] < rank[li] else notes).append(('paint order: ' if rank[oi] < rank[li] else 'as in the SVG: ') + msg)
            else:
                warns.append('paint order: ' + msg)

    # 2. inventory
    n_math = sum(1 for r in recs if r['math']); n_text = sum(1 for r in recs if r['tag'] == 'sp' and r['text'] and not r['math'] and not r['pts'])
    n_cxn = sum(1 for r in recs if r['tag'] == 'cxnSp'); n_ff = sum(1 for r in recs if r['pts'] and r['tag'] == 'sp')
    n_shape = sum(1 for r in recs if r['tag'] == 'sp' and not r['pts'] and not r['text'] and not r['math'])
    n_pic = sum(1 for r in recs if r['tag'] == 'pic')
    groups = sorted({r['group'] for r in recs if r['group']})
    fonts = sorted({f for r in recs for f in r['fonts'] if f})
    print(f'{a.pptx}: slide {sw:g}×{sh:g} pt; {len(recs)} shapes = {n_shape} boxes/icons + {n_cxn} connectors + {n_ff} freeforms + '
          f'{n_text} text boxes + {n_math} equations' + (f' + {n_pic} pictures' if n_pic else '')
          + f'; {len(groups)} groups; typefaces {", ".join(fonts) or "-"}')
    top = [etree.QName(c).localname for c in tree if etree.QName(c).localname not in ('nvGrpSpPr', 'grpSpPr')]
    print(f'  top-level paint order: {len(top)} elements, first {tree[2].find(".//" + q("p:cNvPr")).get("name") if len(tree) > 2 else "?"!r}')

    # 3. against the SVG: nothing dropped, slide size right
    if svg_root is not None:
        SVGNS = '{http://www.w3.org/2000/svg}'
        vb = svg_root.get('viewBox')
        if vb:
            _, _, vw, vh = map(float, re.split(r'[\s,]+', vb.strip()))
            if abs(vw * a.scale - sw) > 0.5 or abs(vh * a.scale - sh) > 0.5:
                errors.append(f'slide {sw:g}×{sh:g} pt ≠ viewBox {vw:g}×{vh:g} × {a.scale:g}')

        def hidden(el):                  # inside <defs>/<marker> or inside a rendered formula
            p = el.getparent()
            while p is not None:
                if p.tag in (SVGNS + 'defs', SVGNS + 'marker') or (p.tag == SVGNS + 'g' and p.get('data-symbol') == 'tex'):
                    return True
                p = p.getparent()
            return False
        n_tex = sum(1 for g in svg_root.iter(SVGNS + 'g') if g.get('data-symbol') == 'tex' and not hidden(g))
        n_txt = sum(1 for t in svg_root.iter(SVGNS + 'text') if not hidden(t) and ''.join(t.itertext()).strip(' \t\r\n'))
        prim = {}
        for t in ('rect', 'circle', 'ellipse', 'path', 'line', 'polyline', 'polygon'):
            prim[t] = sum(1 for e in svg_root.iter(SVGNS + t) if not hidden(e))
        prim_total = sum(prim.values())
        n_img = sum(1 for e in svg_root.iter(SVGNS + 'image') if not hidden(e))
        n_math_text = sum(1 for r in recs if r['text'] and not r['math'] and '公式' in r['name'])
        if n_math + n_math_text < n_tex:
            errors.append(f'{n_tex} formula placeholders in the SVG but only {n_math + n_math_text} in the deck')
        elif n_math_text:
            warns.append(f'{n_math_text} of {n_tex} formulas are plain text, not native equations (no mathml2omml.xsl, or --math text)')
        if n_text < n_txt:
            warns.append(f'{n_txt} <text> elements in the SVG, {n_text} text boxes in the deck')
        got = n_shape + n_cxn + n_ff
        if got < prim_total:
            warns.append(f'{prim_total} SVG primitives ({", ".join(f"{k} {v}" for k, v in prim.items() if v)}) but {got} drawn shapes')
        if n_pic < n_img:
            warns.append(f'{n_img} <image> elements in the SVG, {n_pic} pictures in the deck')
        print(f'  svg: {n_txt} text, {n_tex} formulas, {prim_total} primitives' + (f', {n_img} images' if n_img else '')
              + f' → deck: {n_text} text, {n_math} equations' + (f' (+{n_math_text} as text)' if n_math_text else '')
              + f', {got} shapes' + (f', {n_pic} pictures' if n_img or n_pic else ''))
    for n in notes: print('  [note ]', n)
    for w in warns: print('  [warn ]', w)
    for e in errors: print('  [error]', e)
    print('  ✓ nothing covered, inventory complete' if not errors and not warns else f'  {len(errors)} error(s), {len(warns)} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
