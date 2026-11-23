#!/usr/bin/env python3
"""Re-export corpus parts of the parts library with the faithful subtractive cut, where the old leaf-by-leaf export
(extract_parts.export_candidate_svg) lost something: gradient or pattern fills written as the invalid paint
fill="url", group opacity, masks or clip paths on ancestor groups, CSS-hidden elements.

  python3 scripts/distill/repair_symbols.py [--library figgenie-paper-diagram/assets/symbols] --report <dir> [--apply]

For every corpus entry of index.json:
  1. the library file's wrapper <g data-symbol transform="scale(s) translate(-x,-y)"> gives the source-space frame;
  2. each exported element is matched to its source leaf by tag + geometry attributes + text + the baked transform
     (the old export deep-copied the node and wrote transform=matrix(CTM));
  3. the part is reproducible when every exported element matched and every matched anchor (<use> glyph groups
     included) is complete; it is then cut again subtractively into the same frame and wrapped the same way;
  4. old and new are rendered with the text hidden and compared (share of inked pixels that differ).
A part is a repair candidate when it is reproducible and (differs by more than --threshold or holds an invalid
fill/stroke="url"). --apply rewrites those files (the originals are copied to <report>/before/) and re-renders the
catalog sheet of each kind that changed. Connector-style samples (synthetic) and original drawings are skipped.
Writes <report>/repair_report.json and <report>/before_after_NN.png.
"""
import argparse, collections, json, math, re, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_parts as X          # noqa: E402
import mech_svg as M               # noqa: E402

SVG_NS = M.SVG_NS
GEOM = {'path': ('d',), 'rect': ('x', 'y', 'width', 'height', 'rx', 'ry'), 'circle': ('cx', 'cy', 'r'),
        'ellipse': ('cx', 'cy', 'rx', 'ry'), 'line': ('x1', 'y1', 'x2', 'y2'), 'polygon': ('points',),
        'polyline': ('points',), 'text': ('x', 'y'), 'image': ('x', 'y', 'width', 'height')}
ROOT = HERE.parents[2]


def key_of(tag, node, transform):
    txt = ''.join(node.itertext()).strip() if tag == 'text' else ''
    return (tag, tuple(node.get(a) for a in GEOM.get(tag, ())), txt, transform)


def parse_wrapper(lib_root):
    g = next((c for c in lib_root if M.local(c) == 'g' and c.get('data-symbol')), None)
    if g is None: return None, None
    tr = g.get('transform') or ''
    s = re.search(r'scale\(\s*([-\d.eE+]+)', tr); t = re.search(r'translate\(\s*([-\d.eE+]+)[\s,]+([-\d.eE+]+)', tr)
    return g, (float(s.group(1)) if s else 1.0, -float(t.group(1)) if t else 0.0, -float(t.group(2)) if t else 0.0)


def rebuild(entry, lib_root, lib_g, scale_xy, src_path):
    """-> (status, new_svg_text or None, detail)."""
    s, x, y = scale_xy
    vb = M.viewbox_of(lib_root)
    frame = (x, y, vb[2] / s, vb[3] / s)
    exported = [c for c in lib_g if M.local(c) in GEOM]
    if not exported: return 'no-elements', None, '', None
    if any(c.get('transform') is None or not c.get('transform').startswith('matrix(') for c in exported):
        return 'synthetic', None, 'children without baked transforms', None
    root = M.parse(src_path); M.anchors(root)
    leaves, anc = M.walk_anchored(root)
    by_key = collections.defaultdict(list)
    leaves_per_anchor = collections.Counter()
    for e, a in zip(leaves, anc):
        i = int(a.get(M.IDX)); leaves_per_anchor[i] += 1
        by_key[key_of(e.tag, e.node, X.mat_str(e.ctm))].append(i)
    keep, missing, matched_per_anchor = set(), 0, collections.Counter()
    for c in exported:
        hits = by_key.get(key_of(M.local(c), c, c.get('transform')))
        if not hits: missing += 1; continue
        for i in set(hits):
            keep.add(i); matched_per_anchor[i] += hits.count(i)
    if missing: return 'unmatched', None, '%d of %d elements not found in the source' % (missing, len(exported)), None
    partial = [i for i in keep if matched_per_anchor[i] < leaves_per_anchor[i]]
    if partial: return 'partial-anchor', None, '%d anchors only partly in the part' % len(partial), None
    cut = M.subtractive_cut(root, keep, frame, prefix='%s-' % entry['name'])
    truth = M.hidden_reference(root, keep, frame, prefix='t-%s-' % entry['name'])
    cut_root = M.etree.fromstring(cut.encode('utf-8'))
    out = M.etree.Element('{%s}svg' % SVG_NS, nsmap={None: SVG_NS})
    for k in ('viewBox', 'width', 'height', 'data-symbol', 'data-kind', 'data-size-pt'):
        if lib_root.get(k) is not None: out.set(k, lib_root.get(k))
    for c in lib_root:
        if M.local(c) in ('title', 'desc'): out.append(M.copy.deepcopy(c))
    g = M.etree.SubElement(out, '{%s}g' % SVG_NS)
    for k, v in lib_g.attrib.items(): g.set(k, v)
    for k in ('style', 'fill', 'stroke', 'font-family', 'opacity', 'fill-rule'):   # root-level presentation of the source
        if cut_root.get(k) is not None: g.set(k, cut_root.get(k))
    for c in list(cut_root): g.append(c)
    return 'ok', M.etree.tostring(out, encoding='unicode'), '%d anchors' % len(keep), (truth if len(truth) <= 3_000_000 else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--library', default=str(HERE.parents[1] / 'assets' / 'symbols'))
    ap.add_argument('--extracted-dir', default=str(ROOT / 'lab' / 'extracted'))
    ap.add_argument('--report', required=True); ap.add_argument('--apply', action='store_true')
    ap.add_argument('--threshold', type=float, default=0.01)
    a = ap.parse_args()
    t0 = time.time()
    lib = Path(a.library); rep = Path(a.report); rep.mkdir(parents=True, exist_ok=True)
    index = json.load(open(lib / 'index.json', encoding='utf-8'))
    rows, old_items, new_items, truth_items = [], [], [], []
    for old in rep.glob('*.png'): old.unlink()
    for e in index['entries']:
        src = e.get('source') or {}
        row = {'name': e['name'], 'kind': e['kind'], 'file': e['file'], 'provenance': e.get('provenance'),
               'source': '%s_fig%s' % (src.get('paper_id'), src.get('fig')) if src else None}
        rows.append(row)
        if e.get('provenance') != 'corpus' or not src.get('file'):
            row['status'] = 'skipped-original'; continue
        lib_text = (lib / e['file']).read_text(encoding='utf-8')
        row['invalid_paint'] = bool(re.search(r'\b(fill|stroke)="url"', lib_text))
        src_path = Path(a.extracted_dir) / src['paper_id'] / src['file']
        if not src_path.exists(): row['status'] = 'no-source'; continue
        lib_root = M.etree.fromstring(lib_text.encode('utf-8'))
        lib_g, sxy = parse_wrapper(lib_root)
        if lib_g is None: row['status'] = 'no-wrapper'; continue
        try:
            status, new_svg, detail, truth = rebuild(e, lib_root, lib_g, sxy, src_path)
        except Exception as exc:  # noqa: BLE001
            status, new_svg, detail, truth = 'error', None, repr(exc)[:200], None
        row['status'], row['detail'] = status, detail
        if new_svg and truth:
            row['_new'] = new_svg
            k = len(old_items)
            old_items.append(('o%d' % k, lib_text)); new_items.append(('n%d' % k, new_svg)); truth_items.append(('t%d' % k, truth)); row['_k'] = k
        elif new_svg:
            row['status'] = 'no-reference'
    print('rebuilt %d of %d corpus parts; rendering comparisons...' % (len(new_items), sum(1 for r in rows if r.get('provenance') == 'corpus')), flush=True)
    old_nt, new_nt, tru_nt, old_t, new_t, tru_t = M.render_fit_groups(
        [(old_items, M.HIDE_TEXT_CSS), (new_items, M.HIDE_TEXT_CSS), (truth_items, M.HIDE_TEXT_CSS),
         (old_items, ''), (new_items, ''), (truth_items, '')], size=180)
    cands, worse = [], []
    for r in rows:
        if '_k' not in r: continue
        k = r['_k']
        r['diff_old'] = round(M.diff_ratio(old_nt['o%d' % k], tru_nt['t%d' % k]), 4)
        r['diff_new'] = round(M.diff_ratio(new_nt['n%d' % k], tru_nt['t%d' % k]), 4)
        r['diff'] = r['diff_old']
        # rewrite only when the re-export matches the source and the current file does not (or is invalid); a part
        # whose source rendering is (nearly) empty is a phantom -- content clipped away in the paper -- and is flagged
        # for the human instead of being replaced by a blank file
        import numpy as np
        ink_truth = int((np.asarray(tru_t['t%d' % k].convert('L')) < 245).sum())
        r['phantom'] = ink_truth < 40
        r['repair'] = bool(not r['phantom'] and r['diff_new'] <= a.threshold and (r['diff_old'] > a.threshold or r.get('invalid_paint')))
        if r['diff_new'] > a.threshold: worse.append(r)
        if r['repair']: cands.append(r)
    cands.sort(key=lambda r: -r['diff_old']); worse.sort(key=lambda r: -r['diff_new'])
    from PIL import Image, ImageDraw
    F = X._fonts(); cols = 3; tw, th = 3 * 180 + 32, 180 + 34
    sheets = []
    for label, group in (('repair', cands), ('reexport_differs', worse)):
        for s in range(0, len(group), 18):
            batch = group[s:s + 18]
            img = Image.new('RGB', (cols * tw, math.ceil(len(batch) / cols) * th + 30), '#ffffff'); dr = ImageDraw.Draw(img)
            dr.text((8, 6), '%s %d-%d of %d   current file | re-export | source (other elements hidden)' % (label, s + 1, s + len(batch), len(group)), fill='#111', font=F['lbl'])
            for i, r in enumerate(batch):
                rr, c = divmod(i, cols); x, y = c * tw, 30 + rr * th; k = r['_k']
                for j, (im, col) in enumerate(((old_t['o%d' % k], '#cc3333'), (new_t['n%d' % k], '#33aa33'), (tru_t['t%d' % k], '#3366cc'))):
                    img.paste(im, (x + 4 + j * 184, y)); dr.rectangle([x + 4 + j * 184, y, x + 184 + j * 184, y + 180], outline=col)
                dr.text((x + 4, y + 183), '%d %s  old %.0f%% new %.0f%%%s' % (s + i + 1, r['name'][:26], 100 * r['diff_old'], 100 * r['diff_new'],
                                                                             '  fill=url' if r.get('invalid_paint') else ''), fill='#000', font=F['txt'])
            p = rep / ('%s_%02d.png' % (label, s // 18 + 1)); img.save(p); sheets.append(p.name)
    applied = []
    if a.apply and cands:
        for r in cands:
            dst = lib / r['file']; bak = rep / 'before' / r['file']
            bak.parent.mkdir(parents=True, exist_ok=True)
            if not bak.exists(): shutil.copy2(dst, bak)
            dst.write_text(r['_new'], encoding='utf-8'); applied.append(r['file'])
        import build_symbols as B
        for kind in sorted({r['kind'] for r in cands}):
            es = [dict(e, _abs=str(lib / e['file'])) for e in index['entries'] if e['kind'] == kind]
            B.render_catalog(es, str(lib / ('catalog-%s.png' % kind)), '%s parts' % kind)
    summary = dict(collections.Counter(r.get('status') for r in rows))
    report = {'summary': summary, 'rebuilt': len(new_items), 'identical_or_below_threshold': sum(1 for r in rows if '_k' in r and not r['repair']),
              'repair_candidates': len(cands), 'reexport_differs_from_source': len(worse),
              'current_differs_from_source': sum(1 for r in rows if r.get('diff_old', 0) > a.threshold),
              'phantoms': [r['name'] for r in rows if r.get('phantom')],
              'invalid_paint_total': sum(1 for r in rows if r.get('invalid_paint')),
              'invalid_paint_reproducible': sum(1 for r in cands if r.get('invalid_paint')), 'applied': applied, 'sheets': sheets,
              'threshold': a.threshold, 'minutes': round((time.time() - t0) / 60, 1),
              'parts': [{k: v for k, v in r.items() if not k.startswith('_')} for r in rows]}
    (rep / 'repair_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('summary', 'rebuilt', 'identical_or_below_threshold', 'repair_candidates', 'reexport_differs_from_source',
                                              'current_differs_from_source', 'invalid_paint_total', 'invalid_paint_reproducible', 'sheets', 'minutes')}, ensure_ascii=False))
    print('applied %d files' % len(applied) if a.apply else 'dry run (use --apply to rewrite the candidates)')


if __name__ == '__main__':
    main()
