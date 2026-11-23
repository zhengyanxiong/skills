#!/usr/bin/env python3
"""Build the reusable-parts library (assets/symbols/) from reviewed candidates.

Inputs
  --pool     candidate pool produced by extract_parts.py (candidates.jsonl, svg/, thumbs/)
  --reviews  one or more review_*.jsonl files (one JSON line per candidate, see REVIEW_PROTOCOL.md):
             {"candidate_id","keep","kind","category","name","depicts","style","quality","tags",...}
  --original optional directory of hand-drawn originals (<name>.svg + originals.jsonl with the same
             fields; provenance "original")
  --out      library directory (default figgenie-paper-diagram/assets/symbols)

What it does
  * keeps every reviewed line with keep == true; resolves name collisions deterministically
    (sorted by candidate_id, suffix -2, -3 ...)
  * normalises each candidate SVG to PRINT size: the pool SVG has viewBox="x y w h" in the author's
    source units and a per-figure scale (print pt per source unit, from candidates.jsonl); the library
    file gets viewBox="0 0 W H" with W = w*scale, H = h*scale and a wrapper
    <g data-symbol="<name>" transform="scale(s) translate(-x,-y)"> around the original elements,
    plus <title>/<desc> with provenance.  Colours are kept as drawn (the agent recolours by role).
  * writes <out>/<kind>/<name>.svg, <out>/index.json, <out>/README.md and one catalog contact sheet
    per kind (<out>/catalog-<kind>.png, rendered with Playwright Chromium) so the parts can be browsed.

Re-run whenever reviews change:  python3 scripts/distill/build_symbols.py --pool <pool> --reviews <dir>/review_*.jsonl

Mechanism parts (mined by mech_pool.py / cut_parts.py / mech_merge.py and assembled by mech_final.py) are APPENDED
to an existing library, since the architecture pool the library was built from is gone:

  python3 scripts/distill/build_symbols.py --append-mech mech-parts/final/parts.jsonl [--out ...] [--no-catalog]

  * every part of parts.jsonl is normalised like a pool candidate (its `scale` is print pt per source unit) and
    written to <out>/<kind>/<name>.svg with kind icon / motif / shape / device (device = narrative devices of
    mechanism figures); names are made unique against the whole library (suffix -2, -3 ...)
  * index.json keeps the existing entries and gains the new ones with `subtype: "mechanism"`, `family`,
    `family_raw`, `variant`, `theme` and `figure_kinds` (the v3 groups the part serves); `families` (from the
    families.json next to parts.jsonl) lists the consolidated families with counts
  * re-running replaces the previously appended mechanism entries; the architecture entries are never touched
  * catalogs: the per-kind sheets stay architecture-only; mechanism parts get catalog-mech-<theme>.png
"""
import argparse, collections, json, math, os, re, sys, glob
from pathlib import Path
from lxml import etree

SVG_NS = 'http://www.w3.org/2000/svg'
KINDS = ('icon', 'motif', 'shape')
MECH_KINDS = ('icon', 'motif', 'shape', 'device')
LIB_NOTE = ('Colours are as drawn in the source figure; recolour by palette role when reusing. '
            'The library is a reference, not a limit: draw what the figure needs.')
NUM = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')
    return s or 'part'


def load_reviews(paths):
    rows = {}
    for p in paths:
        for i, line in enumerate(open(p, encoding='utf-8')):
            line = line.strip()
            if not line: continue
            try: r = json.loads(line)
            except json.JSONDecodeError as e:
                print(f'warn: {p}:{i+1} bad json: {e}', file=sys.stderr); continue
            cid = r.get('candidate_id')
            if not cid: continue
            r['_reviewer'] = Path(p).stem
            rows[cid] = r          # later files override earlier ones for the same candidate
    return rows


def normalise_svg(src_path, scale, name, meta):
    raw = open(src_path, 'rb').read()
    root = etree.fromstring(raw, parser=etree.XMLParser(recover=True, huge_tree=True, remove_comments=True))
    vb = [float(v) for v in NUM.findall(root.get('viewBox') or '')]
    if len(vb) != 4:
        w = float(NUM.findall(root.get('width') or '0')[0]); h = float(NUM.findall(root.get('height') or '0')[0]); vb = [0, 0, w, h]
    x, y, w, h = vb
    s = scale if scale and scale > 0 else 1.0
    W, H = round(w * s, 3), round(h * s, 3)
    out = etree.Element('{%s}svg' % SVG_NS, nsmap={None: SVG_NS})
    out.set('viewBox', f'0 0 {W} {H}'); out.set('width', f'{W}pt'); out.set('height', f'{H}pt')
    out.set('data-symbol', name); out.set('data-kind', meta['kind']); out.set('data-size-pt', f'{W}x{H}')
    t = etree.SubElement(out, '{%s}title' % SVG_NS); t.text = name
    d = etree.SubElement(out, '{%s}desc' % SVG_NS)
    d.text = (f"{meta.get('depicts') or ''} | source: {meta.get('source_figure')} ({meta.get('source_file')}) "
              f"| candidate {meta.get('candidate_id')} | units: pt at print size | colours as drawn, recolour by role")
    g = etree.SubElement(out, '{%s}g' % SVG_NS)
    g.set('data-symbol', name)
    tr = f'scale({s:.6g}) translate({-x:.4f},{-y:.4f})' if (s != 1.0 or x or y) else None
    if tr: g.set('transform', tr)
    for child in list(root):
        tag = child.tag.rsplit('}', 1)[-1] if isinstance(child.tag, str) else ''
        if tag in ('title', 'desc', 'metadata'): continue
        g.append(child)
    return etree.tostring(out, pretty_print=True, xml_declaration=False, encoding='unicode'), W, H


def render_catalog(entries, out_png, title, cols=8, tile=150):
    """Contact sheet of library SVGs with names, rendered in Chromium."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('warn: playwright missing, no catalog rendered', file=sys.stderr); return
    cells = []
    for e in entries:
        svg = open(e['_abs'], encoding='utf-8').read()
        svg = re.sub(r'<svg\b([^>]*)\bwidth="[^"]*"', r'<svg\1', svg, count=1)
        svg = re.sub(r'<svg\b([^>]*)\bheight="[^"]*"', r'<svg\1', svg, count=1)
        svg = svg.replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" style="max-width:100%;max-height:100%;width:auto;height:auto" ', 1)
        cells.append(f'<div class="c"><div class="im">{svg}</div><div class="n">{e["name"]}</div>'
                     f'<div class="m">{e["category"]} · {e["size_pt"][0]:.0f}×{e["size_pt"][1]:.0f}pt · ×{e.get("occurrences", 1)}</div></div>')
    rows = math.ceil(len(cells) / cols) or 1
    html = f'''<html><head><style>
    body{{margin:0;background:#fff;font-family:Helvetica,Arial,sans-serif}}
    h1{{font-size:16px;margin:10px 12px}}
    .g{{display:grid;grid-template-columns:repeat({cols},{tile}px);gap:8px;padding:0 12px 12px}}
    .c{{border:1px solid #ddd;padding:4px;height:{tile+34}px;box-sizing:border-box}}
    .im{{height:{tile-16}px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#fff}}
    .im svg{{max-width:{tile-14}px;max-height:{tile-20}px}}
    .n{{font-size:11px;font-weight:bold;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .m{{font-size:9px;color:#666;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    </style></head><body><h1>{title} ({len(cells)})</h1><div class="g">{''.join(cells)}</div></body></html>'''
    tmp = Path(out_png).with_suffix('.html'); tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': cols * (tile + 8) + 24, 'height': 400}, device_scale_factor=1)
        pg.goto('file://' + str(tmp.resolve())); pg.wait_for_timeout(300)
        pg.screenshot(path=out_png, full_page=True); b.close()
    tmp.unlink(missing_ok=True)


def write_readme(out, entries, idx, mech=None, ai=None):
    """README.md of the library; `mech` = (n_mech, n_families, themes) when mechanism parts are present, `ai` =
    (n_ai, n_families, themes, domains) when AI-venue parts are present."""
    kinds = MECH_KINDS if (mech or ai) else KINDS
    lines = ['# Reusable parts library (`assets/symbols/`)', '',
             f'{len(entries)} parts: ' + ', '.join(f'{k} {idx["by_kind"].get(k, 0)}' for k in kinds if idx['by_kind'].get(k)) + '.',
             'Each file is a standalone SVG in **print pt** (viewBox `0 0 W H`), wrapped in `<g data-symbol="name">`;',
             'copy the inner `<g>` into a figure (`<g data-symbol="name" transform="translate(x,y)">…`) and recolour fills/strokes',
             'by palette role. Colours are as drawn in the source paper. Parts with `provenance: corpus` were cut from',
             'published figures (see `source` in index.json) and are style references only; `original` parts were drawn for this skill.',
             '', '**The library is a reference, not a limit.** Draw any component the figure needs; match the stroke width,',
             'corner radius and colour roles of the rest of the figure (references/style-rules.md, references/parts-styles.md).', '']
    if mech:
        n_mech, n_fam, themes = mech
        lines += [f'**Mechanism parts** ({n_mech}, `subtype: "mechanism"` in index.json) were cut from mechanism figures (walkthroughs,',
                  'before/after sequences, state machines, comparisons, component anatomy). They carry a `family` (the drawing idiom,',
                  f'{n_fam} consolidated families listed under `families` in index.json), a `theme`, a `variant` note and',
                  '`figure_kinds` (which figure groups the idiom serves). The `device` kind holds the narrative devices of such figures:',
                  'ghost copies, frame arrows, delta highlights, check/cross marks, pointers into slots, step badges, lane dividers …',
                  'Browse them by theme: ' + ', '.join(f'`catalog-mech-{t}.png`' for t in themes) + '; search index.json by family / tags / depicts.', '']
    if ai:
        n_ai, n_fam, themes, domains = ai
        lines += [f'**AI-venue parts** ({n_ai}, `subtype: "ai"` in index.json) were cut from the Figure 1s of ICLR, ICML, NeurIPS, CVPR, ACL',
                  'and AAAI papers (references/ai/): the stock idioms of that family (an LLM, a Transformer block, a LoRA adapter, a token',
                  'strip, a diffusion chain, an agent loop, chat bubbles, benchmark cards, film strips of samples ...) and its devices (verdict',
                  f'marks, zoom call-outs, tab titles, block arrows). Each carries a `family` ({n_fam} families: the ids of the AI tag vocabulary,',
                  'plus `new:<slug>` families the cutting agents opened, listed under `families` with `subtype: "ai"`), a `theme`, a `domain`',
                  '(the sub-field of the figure it came from: ' + ', '.join(domains) + '), a `convention` (common / variant / own) and',
                  '`placeholders` (bitmaps of the source replaced by grey slots: a photo, an icon, a logo the paper supplied). Browse them by',
                  'theme: ' + ', '.join(f'`catalog-ai-{t}.png`' for t in themes) + '; search index.json by family / domain / tags / depicts.', '']
    lines += ['Browse: `catalog-icon.png`, `catalog-motif.png`, `catalog-shape.png` (architecture parts); search: `index.json` (name, category, tags, depicts).', '',
              '| kind | category | count |', '|---|---|---|']
    for (k, cat), n in sorted(collections.Counter((e['kind'], e['category']) for e in entries).items()):
        lines.append(f'| {k} | {cat} | {n} |')
    (out / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


CATALOG = {'mechanism': ('catalog-mech-{t}.png', 'mechanism parts: {t}'), 'ai': ('catalog-ai-{t}.png', 'AI-venue parts: {t}')}


def subtype_summary(entries, fams, subtype):
    """(n, n_families, themes[, domains]) of one subtype already in the library, for the README."""
    es = [e for e in entries if e.get('subtype') == subtype]
    if not es: return None
    themes = [t for t, _ in collections.Counter(e.get('theme') for e in es).most_common()]
    n_fam = len({e.get('family') for e in es})
    if subtype == 'ai':
        domains = [d for d, _ in collections.Counter(e.get('domain') for e in es if e.get('domain')).most_common()]
        return (len(es), n_fam, themes, domains)
    return (len(es), n_fam, themes)


def append_parts(a, subtype, parts_path):
    """Append the parts of one subtype -- `mechanism` (mech_final.py parts.jsonl) or `ai` (ai_final.py parts.jsonl) -- to
    the library: the previous entries of that subtype are replaced, every other entry is kept untouched."""
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    idx_p = out / 'index.json'
    idx = json.loads(idx_p.read_text(encoding='utf-8')) if idx_p.exists() else dict(version=1, units='pt at print size', entries=[], families=[])
    old = [e for e in idx['entries'] if e.get('subtype') == subtype]
    for e in old: (out / e['file']).unlink(missing_ok=True)          # re-run: replace the previous append
    entries = [e for e in idx['entries'] if e.get('subtype') != subtype]
    for e in entries: e['_abs'] = str(out / e['file'])
    used = collections.Counter(e['name'] for e in entries)
    parts = [json.loads(l) for l in open(parts_path, encoding='utf-8') if l.strip()]
    fam_p = Path(parts_path).parent / 'families.json'
    families = json.loads(fam_p.read_text(encoding='utf-8')).get('families', []) if fam_p.exists() else []
    print(f'library: {len(entries)} parts kept ({len(old)} {subtype} parts replaced); appending {len(parts)} {subtype} parts')
    new = []
    for r in parts:
        kind = r.get('kind') if r.get('kind') in MECH_KINDS else ('device' if subtype == 'mechanism' else 'motif')
        base = slug(r['name']); used[base] += 1
        name = base if used[base] == 1 else f'{base}-{used[base]}'
        (out / kind).mkdir(exist_ok=True)
        src = r.get('source') or {}
        meta = dict(kind=kind, depicts=r.get('depicts'), candidate_id=f"{src.get('package')}:{r.get('name_orig') or r['name']}",
                    source_figure=src.get('figure') or r.get('figure'), source_file=src.get('file'))
        svg_text, W, H = normalise_svg(r['svg'], r.get('scale') or 1.0, name, meta)
        dst = out / kind / f'{name}.svg'; dst.write_text(svg_text, encoding='utf-8')
        e = dict(name=name, kind=kind, category=r.get('category') or kind, file=f'{kind}/{name}.svg', depicts=r.get('depicts'),
                 tags=r.get('tags') or [], style=r.get('style'), quality=r.get('quality'), size_pt=[W, H], colors=r.get('colors') or [],
                 n_elements=r.get('n_elements'), occurrences=r.get('occurrences', 1), sources=[src.get('figure') or r.get('figure')],
                 source=dict(paper_id=src.get('paper_id'), fig=src.get('fig'), file=src.get('file'), tool=src.get('tool'), venue=src.get('venue'),
                             subtype=subtype, pool=src.get('package'), origin=src.get('origin') or 'cut'),
                 provenance='corpus', candidate_id=meta['candidate_id'], reviewer=src.get('agent'), notes=r.get('notes') or '',
                 subtype=subtype, family=r.get('family'), family_raw=r.get('family_raw'), variant=r.get('variant') or '',
                 theme=r.get('theme'), figure_kinds=r.get('figure_kinds') or [], varies=r.get('varies') or '', _abs=str(dst))
        if subtype == 'ai':
            e.update(domain=r.get('domain') or '', convention=r.get('convention') or '', family_status=r.get('family_status') or '',
                     placeholders=r.get('placeholders', 0))
        new.append(e)
    entries += new
    entries.sort(key=lambda e: (e['kind'], e.get('category') or '', e['name']))
    fam_count = collections.Counter(e['family'] for e in new)
    for f in idx.get('families', []): f.setdefault('subtype', 'mechanism')                     # families written before the subtype field existed
    fams = [f for f in idx.get('families', []) if f['subtype'] != subtype]                      # the other subtype's families stay
    fams += [dict(name=f['name'], subtype=subtype, theme=f.get('theme'), definition=f.get('definition', ''), established=f.get('established', False),
                  count=fam_count.get(f['name'], 0)) for f in families]
    by_family = {'mechanism': {}, 'ai': {}}
    for f in fams: by_family.setdefault(f.get('subtype', 'mechanism'), {})[f['name']] = f['count']
    idx = dict(version=3, units='pt at print size', n=len(entries),
               by_kind={k: sum(1 for e in entries if e['kind'] == k) for k in MECH_KINDS},
               by_subtype=dict(collections.Counter(e.get('subtype', 'architecture') for e in entries)),
               by_category=dict(collections.Counter(e['category'] for e in entries)),
               by_family=dict(sorted(by_family['mechanism'].items(), key=lambda kv: -kv[1])),        # as before: the mechanism families
               by_family_ai=dict(sorted(by_family['ai'].items(), key=lambda kv: -kv[1])),
               families=fams, note=LIB_NOTE, entries=[{k: v for k, v in e.items() if not k.startswith('_')} for e in entries])
    idx_p.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    themes = [t for t, _ in collections.Counter(e['theme'] for e in new).most_common()]
    write_readme(out, entries, idx, mech=subtype_summary(entries, fams, 'mechanism'), ai=subtype_summary(entries, fams, 'ai'))
    if not a.no_catalog:
        pat, title = CATALOG[subtype]
        for t in themes:
            es = sorted((e for e in new if e['theme'] == t), key=lambda e: (e['family'], e['name']))
            render_catalog(es, str(out / pat.format(t=t)), title.format(t=t), cols=10, tile=120)
    print('wrote', len(new), subtype, 'parts;', len(entries), 'parts in', out)
    print(json.dumps(idx['by_kind']), json.dumps(idx['by_subtype']))


def append_mech(a): return append_parts(a, 'mechanism', a.append_mech)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pool', nargs='+', help='one or more candidate pool dirs (candidates.jsonl + svg/)')
    ap.add_argument('--reviews', nargs='+')
    ap.add_argument('--original', default=None, help='dir with originals.jsonl and <name>.svg')
    ap.add_argument('--append-mech', default=None, help='parts.jsonl of mech_final.py: append mechanism parts to the existing library')
    ap.add_argument('--append-ai', default=None, help='parts.jsonl of ai_final.py: append AI-venue parts (subtype ai) to the existing library')
    ap.add_argument('--out', default=str(Path(__file__).resolve().parents[2] / 'assets' / 'symbols'))
    ap.add_argument('--no-catalog', action='store_true')
    a = ap.parse_args()
    if a.append_mech: return append_mech(a)
    if a.append_ai: return append_parts(a, 'ai', a.append_ai)
    if not a.pool or not a.reviews: ap.error('--pool and --reviews are required (or use --append-mech / --append-ai)')
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    cands = {}
    for pdir in a.pool:
        pool = Path(pdir)
        for line in open(pool / 'candidates.jsonl', encoding='utf-8'):
            if line.strip():
                r = json.loads(line); r['_pool'] = pool
                cands.setdefault(r['candidate_id'], r)   # first pool wins for a duplicated id
    reviews = load_reviews(a.reviews)
    kept = [r for r in reviews.values() if r.get('keep') is True]
    print(f'reviewed {len(reviews)}, kept {len(kept)}')
    # deterministic names
    used = collections.Counter(); entries = []
    for r in sorted(kept, key=lambda r: r['candidate_id']):
        c = cands.get(r['candidate_id'])
        if not c:
            print('warn: unknown candidate', r['candidate_id'], file=sys.stderr); continue
        kind = (r.get('kind') or 'icon').lower()
        if kind not in KINDS: kind = 'icon'
        base = slug(r.get('name') or r.get('depicts') or r['candidate_id'])
        used[(kind, base)] += 1
        name = base if used[(kind, base)] == 1 else f'{base}-{used[(kind, base)]}'
        (out / kind).mkdir(exist_ok=True)
        meta = dict(kind=kind, depicts=r.get('depicts'), candidate_id=r['candidate_id'],
                    source_figure=f"{c['paper_id']}_fig{c['fig']}", source_file=c['file'])
        svg_text, W, H = normalise_svg(c['_pool'] / c['svg_path'], c.get('scale') or 1.0, name, meta)
        dst = out / kind / f'{name}.svg'; dst.write_text(svg_text, encoding='utf-8')
        entries.append(dict(name=name, kind=kind, category=r.get('category') or kind, file=f'{kind}/{name}.svg',
                            depicts=r.get('depicts'), tags=r.get('tags') or [], style=r.get('style'), quality=r.get('quality'),
                            size_pt=[W, H], colors=c.get('colors_all') or c.get('colors') or [], n_elements=c.get('n_elements'),
                            occurrences=c.get('occurrences', 1), sources=c.get('sources', [])[:12],
                            source=dict(paper_id=c['paper_id'], fig=c['fig'], file=c['file'], tool=c.get('tool'), venue=c.get('venue'),
                                        subtype=c.get('subtype', 'architecture'), pool=c['_pool'].name),
                            provenance='corpus', candidate_id=r['candidate_id'], reviewer=r.get('_reviewer'), notes=r.get('notes') or '',
                            _abs=str(dst)))
    # originals
    if a.original and Path(a.original, 'originals.jsonl').exists():
        for line in open(Path(a.original, 'originals.jsonl'), encoding='utf-8'):
            if not line.strip(): continue
            r = json.loads(line); kind = r.get('kind', 'icon'); name = slug(r['name'])
            src = Path(a.original) / r.get('file', f'{name}.svg')
            if not src.exists(): print('warn: missing original', src, file=sys.stderr); continue
            (out / kind).mkdir(exist_ok=True)
            if any(e['name'] == name and e['kind'] == kind for e in entries): name = name + '-orig'
            dst = out / kind / f'{name}.svg'; dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
            root = etree.fromstring(dst.read_bytes(), parser=etree.XMLParser(recover=True))
            vb = [float(v) for v in NUM.findall(root.get('viewBox') or '0 0 24 24')]
            entries.append(dict(name=name, kind=kind, category=r.get('category') or kind, file=f'{kind}/{name}.svg', depicts=r.get('depicts'),
                                tags=r.get('tags') or [], style=r.get('style'), quality=r.get('quality', 'clean'), size_pt=[vb[2], vb[3]],
                                colors=r.get('colors', ['currentColor']), n_elements=None, occurrences=0, sources=[], source=None,
                                provenance='original', candidate_id=None, reviewer=r.get('author', 'original'), notes=r.get('notes', ''), _abs=str(dst)))
    entries.sort(key=lambda e: (e['kind'], e['category'], e['name']))
    idx = dict(version=1, units='pt at print size', n=len(entries),
               by_kind={k: sum(1 for e in entries if e['kind'] == k) for k in KINDS},
               by_category=dict(collections.Counter(e['category'] for e in entries)),
               note=LIB_NOTE,
               entries=[{k: v for k, v in e.items() if not k.startswith('_')} for e in entries])
    (out / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    write_readme(out, entries, idx)
    if not a.no_catalog:
        for k in KINDS:
            es = [e for e in entries if e['kind'] == k]
            if es: render_catalog(es, str(out / f'catalog-{k}.png'), f'{k} parts')
    print('wrote', len(entries), 'parts to', out)
    print(json.dumps(idx['by_category'], ensure_ascii=False))


if __name__ == '__main__':
    main()
