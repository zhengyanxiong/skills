#!/usr/bin/env python3
"""Assemble the final mechanism parts set from the mining packages, applying the human pass.

  python3 scripts/distill/mech_final.py --out mech-parts/final \
      [--packages pilot-evolution wave2 wave3 wave4 wave5] [--no-tiles] [--no-sheets]

Reads <mech-parts>/<package>/result/kept.jsonl (mech_merge.py output) of every package and, under --out:
  human_pass/drops.json                  parts the user's rules drop: {"drops": [{"pkg", "name", "why"}]}
  agents/agent_textfix_*/fixes.jsonl     corrected text leaves: {"pkg", "name", "fixes": [{"i", "old", "new"}], "verdict"}
  agents/agent_families/families.json    the consolidated family list and slug mapping (optional until it exists)
and writes:
  svg/<name>.svg    one copy per surviving part with its text fixes applied (source units as cut; `scale` = pt per unit)
  parts.jsonl       one record per part: the kept fields plus the final name (unique over all packages), family
                    (consolidated), family_raw, variant, theme, figure_kinds, source, svg (the copy), text_fixed
  rejected.jsonl    the dropped parts with the reason
  families.json     the consolidated families with per-family counts (when the mapping exists)
  stats.md          counts, drops, fixes, renames, the family table
  tiles/<name>.png and sheets/<theme>/<family>_N.png (+ .json) — one contact sheet per family for the review
Nothing here writes into the skill; build_symbols.py imports parts.jsonl after the review.
"""
import argparse, collections, json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mech_merge as MM            # noqa: E402  (theme_of, render_tiles, draw_theme_sheet)
import text_fix as TF              # noqa: E402
from lxml import etree             # noqa: E402

PACKAGES = ('pilot-evolution', 'wave2', 'wave3', 'wave4', 'wave5')
THEME_ORDER = ['steps-traces', 'frames-change', 'logic-time', 'structures', 'annotations', 'icons', 'graphs', 'containers',
               'data-flow', 'math-code', 'new-families', 'other']


def load_kept(root, packages):
    rows = []
    for pkg in packages:
        p = root / pkg / 'result' / 'kept.jsonl'
        if not p.exists():
            print('warn: no kept.jsonl in', pkg, file=sys.stderr); continue
        for i, line in enumerate(open(p, encoding='utf-8')):
            if line.strip():
                r = json.loads(line); r['_pkg'] = pkg; r['_order'] = (packages.index(pkg), i); rows.append(r)
    return rows


def load_fixes(out):
    fixes, verdicts = {}, collections.Counter()
    for p in sorted(out.glob('agents/agent_textfix_*/fixes.jsonl')):
        for line in open(p, encoding='utf-8'):
            if not line.strip(): continue
            rec = json.loads(line)
            verdicts[rec.get('verdict') or ('fixed' if rec.get('fixes') else 'ok')] += 1
            if rec.get('fixes'): fixes[(rec.get('pkg'), rec.get('name'))] = rec['fixes']
    return fixes, verdicts


def apply_fixes(svg_text, fixes, label):
    doc = etree.fromstring(svg_text.encode('utf-8'), parser=etree.XMLParser(huge_tree=True))
    lv = TF.leaves(doc); n = 0
    for f in fixes:
        i = int(f['i'])
        if i >= len(lv):
            print('warn: %s: leaf %d out of range (%d leaves), fix skipped' % (label, i, len(lv)), file=sys.stderr); continue
        cur = TF.content(lv[i])
        if f.get('old') is not None and f['old'] != cur:
            print('warn: %s: leaf %d reads %r, fix expected %r, applied anyway' % (label, i, cur, f['old']), file=sys.stderr)
        TF.set_content(lv[i], f['new']); n += 1
    return etree.tostring(doc, encoding='unicode'), n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='mech-parts/final')
    ap.add_argument('--packages', nargs='+', default=list(PACKAGES))
    ap.add_argument('--no-tiles', action='store_true'); ap.add_argument('--no-sheets', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    out = Path(a.out); root = out.parent
    (out / 'svg').mkdir(parents=True, exist_ok=True)
    rows = load_kept(root, a.packages)
    print('kept over %d packages: %d' % (len(a.packages), len(rows)), flush=True)

    # ---- human pass: drops -------------------------------------------------------------
    drops = {}
    dp = out / 'human_pass' / 'drops.json'
    if dp.exists():
        for d in json.load(open(dp, encoding='utf-8'))['drops']: drops[(d['pkg'], d['name'])] = d.get('why', '')
    rejected, kept = [], []
    for r in rows:
        why = drops.get((r['_pkg'], r['name']))
        if why is not None: rejected.append(dict(r, merge_reason='human-pass:trivial:' + why))
        else: kept.append(r)
    print('drops %d -> %d parts' % (len(rejected), len(kept)), flush=True)

    # ---- human pass: text fixes; families ---------------------------------------------------------
    fixes, verdicts = load_fixes(out)
    fam_json = None
    fp = out / 'agents' / 'agent_families' / 'families.json'
    if fp.exists():
        fam_json = json.load(open(fp, encoding='utf-8'))
        mapping = fam_json.get('mapping', {})
        theme_of_family = {f['name']: f['theme'] for f in fam_json.get('families', [])}
        print('families.json: %d families, %d slugs mapped' % (len(theme_of_family), len(mapping)), flush=True)
    else:
        mapping, theme_of_family = {}, {}
        print('no families.json yet: families kept as reviewed', flush=True)
    unmapped = collections.Counter()
    for r in kept:
        raw = r['family']; m = mapping.get(raw)
        r['family_raw'] = raw
        if m: r['family'] = m['family']; r['variant'] = m.get('variant') or ''
        else:
            r['variant'] = ''
            if fam_json and raw.startswith('new:'): unmapped[raw] += 1
        r['theme'] = theme_of_family.get(r['family']) or MM.theme_of(r['family'])
    if unmapped: print('warn: %d new: families not in the mapping (kept as is): %s' % (len(unmapped), ', '.join(list(unmapped)[:8])), file=sys.stderr)

    # ---- unique names over all packages ----------------------------------------------------
    used = collections.Counter(); renamed = []
    for r in sorted(kept, key=lambda r: r['_order']):
        r['name_orig'] = r['name']; used[r['name']] += 1
        if used[r['name']] > 1:
            r['name'] = '%s-%d' % (r['name_orig'], used[r['name_orig']]); renamed.append((r['_pkg'], r['name_orig'], r['name']))

    # ---- copies with the fixes applied ---------------------------------------------------------
    info_cache = {}
    n_fixed_parts = n_fixed_leaves = 0
    for r in kept:
        src = Path(r['svg']); text = src.read_text(encoding='utf-8')
        fx = fixes.get((r['_pkg'], r['name_orig']))
        n = 0
        if fx:
            text, n = apply_fixes(text, fx, '%s/%s' % (r['_pkg'], r['name_orig']))
            if n: n_fixed_parts += 1; n_fixed_leaves += n
        dst = out / 'svg' / (r['name'] + '.svg'); dst.write_text(text, encoding='utf-8')
        r['_svg_final'] = str(dst); r['_text_fixed'] = n
        ip = root / r['_pkg'] / 'figs' / r['figure'] / 'info.json'
        if ip not in info_cache:
            info_cache[ip] = json.load(open(ip, encoding='utf-8')) if ip.exists() else {}
        r['_info'] = info_cache[ip]
    print('text fixes: %d parts, %d leaves (verdicts %s)' % (n_fixed_parts, n_fixed_leaves, dict(verdicts)), flush=True)

    # ---- parts.jsonl / rejected.jsonl -------------------------------------------------------------
    kept.sort(key=lambda r: (THEME_ORDER.index(r['theme']) if r['theme'] in THEME_ORDER else 99, r['family'], r['kind'], r['name']))
    with open(out / 'parts.jsonl', 'w', encoding='utf-8') as fh:
        for r in kept:
            info = r['_info']
            d = {k: v for k, v in r.items() if not k.startswith('_')}
            d.update(package=r['_pkg'], svg=r['_svg_final'], svg_src=r['svg'], text_fixed=r['_text_fixed'],
                     figure_kinds=r.get('groups') or [], provenance='corpus', subtype='mechanism',
                     source=dict(paper_id=info.get('paper_id') or r['figure'].split('_fig')[0], fig=info.get('fig') or r['figure'].split('_fig')[-1],
                                 figure=r['figure'], file=r.get('source_file'), tool=info.get('tool'), venue=info.get('venue'),
                                 package=r['_pkg'], agent=r.get('agent'), origin='bitmap-trace' if r.get('source') == 'bitmap' else 'cut'))
            fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    with open(out / 'rejected.jsonl', 'w', encoding='utf-8') as fh:
        for r in rejected:
            d = {k: v for k, v in r.items() if not k.startswith('_')}; d['package'] = r['_pkg']
            fh.write(json.dumps(d, ensure_ascii=False) + '\n')

    # ---- families.json with counts ------------------------------------------------------------------
    fam_count = collections.Counter(r['family'] for r in kept)
    if fam_json:
        for f in fam_json['families']: f['count'] = fam_count.get(f['name'], 0)
        json.dump(fam_json, open(out / 'families.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- tiles + sheets ----------------------------------------------------------------------------------
    tiles = out / 'tiles'; sheets = out / 'sheets'
    if not a.no_tiles:
        print('rendering %d tiles...' % len(kept), flush=True)
        for s in range(0, len(kept), 250):
            MM.render_tiles([(r['name'], Path(r['_svg_final']).read_text(encoding='utf-8')) for r in kept[s:s + 250]], tiles)
    n_sheets = 0
    if not a.no_sheets:
        if sheets.exists():
            for old in sheets.rglob('*'):
                if old.is_file(): old.unlink()
        defs = {f['name']: f.get('definition', '') for f in (fam_json or {}).get('families', [])}
        by = collections.defaultdict(list)
        for r in kept:
            r['_meta'] = {'w_pt': r['size_pt'][0], 'h_pt': r['size_pt'][1]}; r['_agent'] = '%s/%s' % (r['_pkg'], r.get('agent'))
            by[(r['theme'], r['family'])].append(r)
        for (theme, fam), rs in sorted(by.items(), key=lambda kv: (THEME_ORDER.index(kv[0][0]) if kv[0][0] in THEME_ORDER else 99, -len(kv[1]), kv[0][1])):
            d = sheets / theme; d.mkdir(parents=True, exist_ok=True)
            for s in range(0, len(rs), 30):
                batch = rs[s:s + 30]; n = s // 30 + 1
                png = d / ('%s_%d.png' % (fam, n))
                MM.draw_theme_sheet(batch, tiles, str(png), '%s / %s  %d-%d of %d   %s' % (theme, fam, s + 1, s + len(batch), len(rs), defs.get(fam, '')[:90]))
                json.dump({'theme': theme, 'family': fam, 'sheet': n, 'tiles': {str(k + 1): {'name': r['name'], 'family_raw': r['family_raw'], 'kind': r['kind'],
                           'figure': r['figure'], 'package': r['_pkg']} for k, r in enumerate(batch)}},
                          open(str(png)[:-4] + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
                n_sheets += 1

    # ---- stats.md ----------------------------------------------------------------------------------
    L = ['# Final assembly — %s' % ', '.join(a.packages), '', 'generated in %.1f min' % ((time.time() - t0) / 60), '',
         '| stage | count |', '|---|---|', '| kept over the packages | %d |' % len(rows), '| dropped (human pass) | %d |' % len(rejected),
         '| final | %d |' % len(kept), '| renamed for a cross-package clash | %d |' % len(renamed),
         '| parts with corrected text | %d (%d leaves) |' % (n_fixed_parts, n_fixed_leaves), '']
    for title, key in (('package', lambda r: r['_pkg']), ('kind', lambda r: r['kind']), ('theme', lambda r: r['theme']),
                       ('source', lambda r: r.get('source') or 'cut')):
        L += ['## by %s' % title, '', ', '.join('%s %d' % kv for kv in sorted(collections.Counter(key(r) for r in kept).items(), key=lambda kv: -kv[1])), '']
    L += ['## text-fix verdicts', '', ', '.join('%s %d' % kv for kv in verdicts.items()) or '(no fixes.jsonl yet)', '']
    if renamed: L += ['## renamed', ''] + ['- %s: %s -> %s' % x for x in renamed] + ['']
    L += ['## dropped', ''] + ['- %s/%s: %s' % (r['_pkg'], r['name'], r['merge_reason'].split(':', 2)[-1]) for r in rejected] + ['']
    L += ['## families (%s)' % ('consolidated' if fam_json else 'as reviewed'), '', '| family | theme | parts | raw families | definition |', '|---|---|---|---|---|']
    raw_by = collections.defaultdict(set)
    for r in kept: raw_by[r['family']].add(r['family_raw'])
    defs = {f['name']: f.get('definition', '') for f in (fam_json or {}).get('families', [])}
    for fam, n in sorted(fam_count.items(), key=lambda kv: (THEME_ORDER.index(next(r['theme'] for r in kept if r['family'] == kv[0])) if True else 0, -kv[1], kv[0])):
        th = next(r['theme'] for r in kept if r['family'] == fam)
        L.append('| %s | %s | %d | %d | %s |' % (fam, th, n, len(raw_by[fam]), defs.get(fam, '').replace('|', '/')[:110]))
    if fam_json:
        L += ['', '## families in the mapping with no parts', '', ', '.join(f['name'] for f in fam_json['families'] if f['count'] == 0) or '(none)']
    L += ['', '## sheets', '', '%d sheets under sheets/<theme>/<family>_N.png' % n_sheets, '']
    (out / 'stats.md').write_text('\n'.join(L), encoding='utf-8')
    print('final %d parts, %d families, %d sheets -> %s (%.1f min)' % (len(kept), len(fam_count), n_sheets, out, (time.time() - t0) / 60))


if __name__ == '__main__':
    main()
