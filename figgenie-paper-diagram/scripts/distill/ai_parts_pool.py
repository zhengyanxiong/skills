#!/usr/bin/env python3
"""Build an AI-figure PARTS-MINING package for the cutting sub agents (AI family, distillation step I).

Same layout as a mechanism package (mech_pool.py), so cut_parts.py, mech_bitmaps.py and mech_merge.py work on it, plus
what the AI corpus has that the mechanism corpus had not: every figure here has a deep semantic record that names its
idioms, devices, icons and pictures, and the merged vocabulary v2 gives the family ids. So for each figure:

  <out>/figs/<fig_id>/info.json       as mech_pool.py writes it (+ kinds, subfield, vocabulary tags)
  <out>/figs/<fig_id>/render_0.png    the PDF-extracted SVG at print size with a labelled pt grid (scale 1: pt = pt)
  <out>/figs/<fig_id>/geom_0.json     Chromium geometry of every element (also the cut tool's cache)
  <out>/figs/<fig_id>/brief.md        the record, condensed: what to cut (idioms with the vocabulary id and how they are
                                      drawn, devices, icons, pictures and their treatment, elements, reusable patterns)
  <out>/figs/<fig_id>/anchors.json    text elements of the SVG matched to the record's element names and idiom parts:
  <out>/figs/<fig_id>/anchors.png     the grid render with those anchors boxed and numbered (where the named things are)
  <out>/figures.json, agents/<name>/figures.json, checklist.md (the vocabulary as a family list), family_themes.json
  (family -> contact-sheet theme, read by mech_merge.py), library_summary.md (what the library already has)

  python3 scripts/distill/ai_parts_pool.py --out ai-parts/pilot --select-pilot 16 --agents agent_haiku,agent_sonnet --same-for-all
  python3 scripts/distill/ai_parts_pool.py --out ai-parts/wave1 --select-cover 3 --done ai-parts/pilot --agents 4
  python3 scripts/distill/ai_parts_pool.py --out ai-parts/wave2 --select-cover 3 --by-parts --yield 0.5 --done ai-parts/pilot,ai-parts/wave1 \
      --skip problem-only,saliency-heatmap,mascot-character --agents 4
  python3 scripts/distill/ai_parts_pool.py --out ai-parts/wave3 --select-rest --done ai-parts/pilot,ai-parts/wave1,ai-parts/wave2 --agents 16
"""
import argparse, collections, csv, json, os, re, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import mech_pool as MP             # noqa: E402  (grid render, element parsing)
import mech_svg as M               # noqa: E402  (geometry)

ROOT = HERE.parents[2]; AI = ROOT / 'ai-corpus'; LAB = AI / 'lab'; TM = AI / 'typedisc' / 'tagmerge' / 'v2'
KINDS = ['stage-pipeline', 'model-anatomy', 'side-by-side-contrast', 'worked-walkthrough', 'concept-schematic', 'scope-overview', 'actor-interaction', 'contribution-mosaic']
THEMES = {  # vocabulary id -> theme of the contact sheets (mech_merge.py); anything else: idioms / devices by class, new-families, other
    'things-models': {'llm', 'vlm', 'transformer-block', 'attention', 'encoder-decoder', 'mlp-head', 'cnn-stack', 'vit-patchify', 'unet', 'vae-codebook', 'lora-adapter',
                      'frozen-trainable', 'loss-gradient', 'teacher-student', 'dual-encoder', 'neuron-network', 'trapezoid-module', 'skip-connection', 'operator-nodes',
                      'diffusion-chain', 'contrastive-pair', 'layer-probe-taps', 'checkpoint-chain', 'model-pictogram', 'brand-logo-icon', 'mascot-character'},
    'things-data': {'token-strip', 'embedding-space', 'attention-map', 'attention-mask-grid', 'saliency-heatmap', 'vector-cells', 'matrix-cell-grid', 'masked-input', 'dataset-card',
                    'database-cylinder', 'stacked-cards', 'annotated-record-card', 'prompt-box', 'benchmark-card', 'filmstrip', 'audio-waveform', 'point-cloud', 'camera-frustums',
                    'gridworld-map', 'code-snippet-box', 'pseudocode-box', 'gui-screen', 'distribution-glyph', 'embedding-scatter-plot', 'support-query-sets'},
    'things-agents': {'agent-loop', 'tool-use', 'rl-loop', 'memory-store', 'retrieval-store', 'multi-agent', 'federated-round', 'human-in-loop', 'chat-bubbles', 'thought-bubble',
                      'judge-evaluator', 'typed-trace-blocks', 'chain-of-thought', 'cycle-ring'},
    'things-charts-structures': {'radar-chart', 'schematic-plot', 'sunburst-taxonomy', 'taxonomy-tree', 'leaderboard-table', 'comparison-table', 'loss-landscape', 'method-timeline',
                                 'level-ladder', 'search-tree', 'knowledge-graph', 'gnn-graph', 'small-multiples', 'before-after-pair', 'schedule-lanes'},
    'devices-titles-notes': {'frame-border-titles', 'tab-titled-panels', 'pill-title-headers', 'rotated-labels', 'margin-row-labels', 'claim-banner', 'title-branding', 'icon-led-titles',
                             'step-notes', 'notation-key', 'equation-boxes', 'task-definition'},
    'devices-marks': {'verdict-marks', 'error-callouts', 'status-badges', 'cost-badges', 'plot-callouts', 'leader-callouts', 'zoom-callout', 'brace-grouping', 'toy-values-inline',
                      'condition-insets', 'picture-overlays'},
    'devices-arrows-colour': {'block-arrows', 'loop-back-arrow', 'flow-type-arrows', 'colour-coded-groups', 'module-state-coding', 'accent-on-ours', 'highlighted-text-spans',
                              'positive-negative-pairs'},
    'devices-layout': {'state-snapshots', 'mirrored-layout', 'spanning-shared-block', 'size-as-value', 'option-catalog', 'pictogram-chain', 'visual-metaphor', 'illustration-style',
                       'problem-only', 'prediction-vs-data'},
}


def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
def lst(x): return x if isinstance(x, list) else ([] if x in (None, '') else [x])


def norm(s): return re.sub(r'[^a-z0-9α-ωσ⊙⊕×+ ]+', ' ', (s or '').lower()).strip()


def load_all():
    recs = {r['paper_id']: r for r in jl(LAB / 'extracted' / 'corpus_semantics.jsonl')}
    tab = {r['paper_id']: r for r in jl(LAB / 'fig1_table.jsonl')}
    ftags = {o['id']: o for o in jl(TM / 'figure_tags_v2.jsonl')}
    voc = {e['id']: e for e in json.load(open(TM / 'vocab_v2.json', encoding='utf-8'))['entries']}
    index = {}
    csv.field_size_limit(10 ** 9)
    for r in csv.DictReader(open(LAB / 'extracted' / 'corpus_index.csv', encoding='utf-8')): index[(r['paper_id'], r['fig'])] = r
    return recs, tab, ftags, voc, index


def select_pilot(n, recs, tab, ftags, voc):
    """Greedy coverage: clean vector figures rich in idioms, spread over kinds and sub-fields, covering many entries."""
    cand = []
    for pid, r in recs.items():
        t = tab[pid]
        if t['fig1_status'] not in ('match', 'match-other-fig') or not t.get('measure'): continue
        if float(t['raster_frac'] or 0) > 0.3 or len(lst(r['content'].get('idioms'))) < 3: continue
        cand.append(pid)
    covered, picked, per_kind, per_sub = set(), [], collections.Counter(), collections.Counter()
    n_vec_icons = n_pics = 0
    while len(picked) < n and cand:
        best, bs = None, -1
        for pid in cand:
            r = recs[pid]; c = r['content']; k = (c.get('kinds') or ['other'])[0]; sf = (r.get('system') or {}).get('subfield') or 'other'
            if per_kind[k] >= 3 or per_sub[sf] >= 3: continue
            ents = set(ftags[pid]['tags']) - covered
            s = len(ents) + (1.5 if n_vec_icons < 6 and any(i.get('medium') == 'vector' for i in lst(c.get('icons'))) else 0) \
                + (1.0 if n_pics < 8 and lst(c.get('pictures')) else 0) + 0.2 * len(lst(c.get('idioms')))
            if s > bs: best, bs = pid, s
        if best is None: break
        picked.append(best); cand.remove(best); c = recs[best]['content']
        covered |= set(ftags[best]['tags']); per_kind[(c.get('kinds') or ['other'])[0]] += 1; per_sub[(recs[best].get('system') or {}).get('subfield') or 'other'] += 1
        n_vec_icons += any(i.get('medium') == 'vector' for i in lst(c.get('icons'))); n_pics += bool(lst(c.get('pictures')))
    return picked, covered


def select_cover(target, done_pkgs, recs, tab, ftags, voc, max_raster=0.6, parts=False, part_yield=1.0, skip=()):
    """Greedy cover: add figures until every vocabulary entry (idiom / part / modifier) has `target` figures among the
    packages already cut (`done_pkgs`) and the new selection, or has no more cuttable carriers. A figure counts for an
    entry when it carries it explicitly or in its record text. Cuttable = extracted vector Figure 1 with at most
    `max_raster` of its area in bitmaps. Ties: more record idioms, then id (deterministic).
    parts=True counts what was really cut instead: the parts kept so far (<package>/result/kept.jsonl of the done
    packages) against a target of `target` parts per entry, each new figure expected to add `part_yield` parts for every
    entry it carries (after the pilot and wave 1 about half the entries a cut figure carried came out as a part).
    `skip`: entries not to select for, because a vector part cannot carry them (a property of the whole figure such as
    problem-only, or a drawing that is a bitmap in practice such as a saliency heat map or a cartoon mascot)."""
    tags_of = lambda p: {t for t in ftags[p]['tags'] + (ftags[p].get('text') or []) if t in voc and voc[t]['cls'] in ('idiom', 'part', 'modifier')}
    usable = sorted(p for p in recs if tab[p]['fig1_status'] in ('match', 'match-other-fig') and tab[p].get('measure') and float(tab[p]['raster_frac'] or 0) <= max_raster)
    done = set()
    for pk in done_pkgs:
        done |= {f['paper_id'] for f in json.load(open(Path(pk) / 'figures.json', encoding='utf-8'))}
    carriers = collections.Counter(t for p in usable for t in tags_of(p))
    if parts:
        have = collections.Counter(json.loads(l)['family'] for pk in done_pkgs for l in open(Path(pk) / 'result' / 'kept.jsonl', encoding='utf-8') if l.strip())
        need = {t: max(0, target - have[t]) for t in voc if voc[t]['cls'] in ('idiom', 'part', 'modifier')}
    else:
        have = collections.Counter(t for p in done for t in tags_of(p))
        need = {t: max(0, min(target, carriers[t]) - have[t]) for t in carriers}
    for t in skip: need.pop(t, None)
    rest, picks, why = [p for p in usable if p not in done], [], {}
    while True:
        best, key = None, None
        for p in rest:
            gain = [t for t in tags_of(p) if need.get(t, 0) > 0]
            k = (len(gain), len(lst(recs[p]['content'].get('idioms'))))
            if gain and (key is None or k > key): best, key, bg = p, k, gain
        if best is None: break
        picks.append(best); rest.remove(best); why[best] = sorted(bg)
        for t in bg: need[t] -= part_yield if parts else 1
    short = sorted(t for t in need if need[t] > 0)
    return picks, why, short


def select_rest(done_pkgs, recs, tab, max_raster=0.6):
    """Every cuttable figure (the test of select_cover) that no package in `done_pkgs` has cut yet, in id order."""
    usable = sorted(p for p in recs if tab[p]['fig1_status'] in ('match', 'match-other-fig') and tab[p].get('measure') and float(tab[p]['raster_frac'] or 0) <= max_raster)
    done = set()
    for pk in done_pkgs:
        done |= {f['paper_id'] for f in json.load(open(Path(pk) / 'figures.json', encoding='utf-8'))}
    return [p for p in usable if p not in done]


def brief_md(r, t, ft, voc, cmap):
    c, lay, st, ret = r['content'], r['layout'], r['style'], r.get('retrieval') or {}
    sysm = r.get('system') or {}
    L = [f"# {r['paper_id']} Figure {r['fig']} — {t.get('title', '')}", '',
         f"**Kinds**: {', '.join(lst(c.get('kinds')))} (variant of the first: {c.get('variant') or '-'}; {c.get('variant_note') or ''}). "
         f"**Sub-field**: {sysm.get('subfield')}{' / ' + sysm['subfield2'] if sysm.get('subfield2') else ''}. **Venue**: {r.get('venue')}.", '',
         f"**What it shows**: {r.get('summary') or ''}", '',
         f"**Layout**: {lay.get('arrangement')}; {lay.get('arrangement_note') or ''}", '',
         f"**Style**: ground {st.get('ground')}, fill {st.get('fill')}, corners {st.get('corners')}, rendering {st.get('rendering')}; arrows: {st.get('arrows')}; font: {st.get('font')}", '']
    things = [x for x in ft['tags'] if voc[x]['cls'] != 'modifier']; mods = [x for x in ft['tags'] if voc[x]['cls'] == 'modifier']
    L += ['## Vocabulary entries this figure carries (from its record; the family ids to use)', '',
          '- things: ' + ', '.join(f'`{x}`' for x in things), '- devices: ' + ', '.join(f'`{x}`' for x in mods),
          '- found only in the record text (unconfirmed): ' + (', '.join(f'`{x}`' for x in ft.get('text') or []) or '-'), '']
    L += ['## Idioms recorded (cut each one; `family` = the vocabulary id in brackets)', '', '| concept [family] | convention | drawn as | parts |', '|---|---|---|---|']
    for i in lst(c.get('idioms')):
        fam = cmap.get(i.get('concept'), i.get('concept')); mark = '' if fam == i.get('concept') else f' [{fam}]'
        L.append(f"| {i.get('concept')}{mark} | {i.get('convention')} | {(i.get('drawn_as') or '').replace('|', '/')} | {'; '.join(lst(i.get('parts'))).replace('|', '/')} |")
    nt = [x for x in lst(ret.get('new_tags')) if isinstance(x, dict)]
    L += ['', '## Devices and coined names (the record agent named these; cut the ones that are drawn things)', '']
    for x in nt: L.append(f"- `{x.get('name')}` → family `{cmap.get(x.get('name'), 'one-off (new:<slug> if reusable)')}`: {x.get('what')}")
    pats = lst((r.get('encoding') or {}).get('reusable_patterns'))
    if pats: L += ['', 'Reusable patterns noted: ' + '; '.join(pats)]
    L += ['', '## Icons recorded', '', '| depicts | stands for | style | medium | count |', '|---|---|---|---|---|']
    for i in lst(c.get('icons')): L.append(f"| {(i.get('depicts') or '').replace('|', '/')} | {(i.get('stands_for') or '').replace('|', '/')} | {i.get('style')} | {i.get('medium')} | {i.get('count')} |")
    L += ['', '## Pictures recorded (samples, results, screenshots) and how they are framed', '', '| what | content | role | medium | count | treatment |', '|---|---|---|---|---|---|']
    for p in lst(c.get('pictures')): L.append(f"| {(p.get('what') or '').replace('|', '/')} | {p.get('content')} | {p.get('role')} | {p.get('medium')} | {p.get('count')} | {(p.get('treatment') or '').replace('|', '/')} |")
    L += ['', '## Elements (name — type — drawn as — container); anchors.png boxes the ones whose label was found in the SVG', '']
    for e in lst(c.get('elements')): L.append(f"- {e.get('name')} — {e.get('type')} — {(e.get('drawn_as') or '')} — in: {e.get('container') or '-'}{' — CONTRIBUTION' if e.get('is_contribution') else ''}")
    m = lst(c.get('markers'))
    if m: L += ['', 'Markers: ' + '; '.join(f"{x.get('marker')} ({x.get('kind')}) at {x.get('at')}: {x.get('what')}" for x in m)]
    return '\n'.join(L) + '\n'


def find_anchors(geom, queries, scale, frame):
    """queries: [(label, query_text)] -> anchors [{n, query, text, box_pt, els}] (best text elements per query, up to 3)."""
    texts = [(e, norm(e.get('t'))) for e in geom['els'] if e['tag'] == 'text' and e.get('t') and e.get('v')]
    out, seen = [], set()
    for label, q in queries:
        qn = norm(q)
        if len(qn) < 2: continue
        hits = []
        for e, tn in texts:
            if not tn: continue
            if tn == qn: sc = 3
            elif len(qn) >= 3 and (tn.startswith(qn) or qn.startswith(tn)) and min(len(tn), len(qn)) >= 3: sc = 2
            elif len(qn) >= 4 and (qn in tn or (len(tn) >= 4 and tn in qn)): sc = 1
            else: continue
            hits.append((sc, -abs(len(tn) - len(qn)), e))
        hits.sort(key=lambda h: (-h[0], h[1]))
        for sc, _, e in hits[:3]:
            key = e['i']
            box = [round((e['x'] - frame[0]) * scale, 1), round((e['y'] - frame[1]) * scale, 1), round((e['x'] + e['w'] - frame[0]) * scale, 1), round((e['y'] + e['h'] - frame[1]) * scale, 1)]
            if key in seen:
                for a in out:
                    if a['el'] == key and label not in a['for']: a['for'].append(label)
                continue
            seen.add(key); out.append(dict(n=len(out) + 1, for_=None, el=key, text=e.get('t'), box_pt=box, score=sc))
            out[-1]['for'] = [label]; del out[-1]['for_']
    return out


def draw_anchors(render_png, anchors, pxpt, out_png, font):
    im = Image.open(render_png).convert('RGB'); d = ImageDraw.Draw(im)
    for a in anchors:
        x0, y0, x1, y1 = [(v * pxpt) + MP.MARGIN * pxpt for v in a['box_pt']]
        d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], outline='#e8731a', width=2)
        tag = str(a['n']); tw = d.textlength(tag, font=font) + 6
        d.rectangle([x0 - 2, y0 - 16, x0 - 2 + tw, y0 - 2], fill='#e8731a'); d.text((x0 + 1, y0 - 15), tag, fill='white', font=font)
    im.save(out_png)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True); ap.add_argument('--ids', default=None); ap.add_argument('--select-pilot', type=int, default=None)
    ap.add_argument('--agents', default='2', help='a number, or comma-separated agent names'); ap.add_argument('--same-for-all', action='store_true', help='every agent gets every figure')
    ap.add_argument('--select-cover', type=int, default=None, help='greedy: every vocabulary entry on N figures, counting --done packages')
    ap.add_argument('--done', default='', help='comma-separated packages already cut (their figures.json)')
    ap.add_argument('--by-parts', action='store_true', help='--select-cover N = N kept parts per entry, counted in the --done packages\' result/kept.jsonl')
    ap.add_argument('--yield', dest='part_yield', type=float, default=1.0, help='with --by-parts: parts a new figure is expected to add per entry it carries')
    ap.add_argument('--select-rest', action='store_true', help='every cuttable figure the --done packages have not cut yet')
    ap.add_argument('--skip', default='', help='comma-separated vocabulary entries not to select for (no vector part can carry them)')
    ap.add_argument('--no-render', action='store_true'); a = ap.parse_args()
    t0 = time.time(); out = Path(a.out); figs_dir = out / 'figs'; figs_dir.mkdir(parents=True, exist_ok=True)
    recs, tab, ftags, voc, index = load_all()
    # coined name -> vocabulary id (so the brief can say which family an idiom or coined tag belongs to)
    cmap = {}
    for e in voc.values():
        for src in ('tags', 'idioms'):
            for al in e['aliases'][src]: cmap[al] = e['id'] if e['cls'] in ('idiom', 'part', 'modifier') else (e['id'] if e['cls'] in ('field', 'content') else 'one-off')
        for ab in e.get('absorbs') or []: cmap[ab] = e['id']
        cmap[e['id']] = e['id']
    if a.select_pilot: ids, cov = select_pilot(a.select_pilot, recs, tab, ftags, voc); print(f'pilot: {len(ids)} figures cover {len(cov)} vocabulary entries')
    elif a.select_cover:
        ids, why, short = select_cover(a.select_cover, [x for x in a.done.split(',') if x], recs, tab, ftags, voc, parts=a.by_parts, part_yield=a.part_yield, skip=[x for x in a.skip.split(',') if x])
        print(f'cover {a.select_cover}{" parts" if a.by_parts else ""}: {len(ids)} figures; entries still short: {short or "none"}')
        out.mkdir(parents=True, exist_ok=True)
        sel = dict(target=a.select_cover, done=a.done, figures=[dict(paper_id=p, fills=why[p]) for p in ids], short=short)
        if a.by_parts: sel.update(mode='kept parts per entry', part_yield=a.part_yield)
        if a.skip: sel.update(skip=a.skip.split(','))
        (out / 'selection.json').write_text(json.dumps(sel, ensure_ascii=False, indent=1), encoding='utf-8')
    elif a.select_rest:
        ids = select_rest([x for x in a.done.split(',') if x], recs, tab)
        print(f'rest: {len(ids)} cuttable figures not cut yet')
        out.mkdir(parents=True, exist_ok=True)
        (out / 'selection.json').write_text(json.dumps(dict(mode='rest', done=a.done, figures=[dict(paper_id=p) for p in ids]), ensure_ascii=False, indent=1), encoding='utf-8')
    else: ids = [x.strip() for x in (a.ids or '').split(',') if x.strip()]
    try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
    except Exception: font = ImageFont.load_default()
    figures, grid_jobs, anchor_jobs = [], [], []
    for pid in ids:
        r, t, ft = recs[pid], tab[pid], ftags[pid]
        fig = str(t['our_fig'] or '1'); fid = f'{pid}_fig{fig}'; svg = LAB / t['measure']
        row = index.get((pid, fig), {})
        d = figs_dir / fid; d.mkdir(exist_ok=True)
        vb = MP.source_viewbox(str(svg)); els = MP.parse_elements(str(svg)); cb = MP.content_bbox(els, vb); scale = 1.0; pad = 2.0
        frame = (max(cb[0] - pad, vb[0]), max(cb[1] - pad, vb[1]), min(cb[2] + pad, vb[0] + vb[2]), min(cb[3] + pad, vb[1] + vb[3]))
        Wp, Hp = (frame[2] - frame[0]) * scale, (frame[3] - frame[1]) * scale
        pxpt = max(2.0, min(6.0, 1700.0 / max(Wp + MP.MARGIN, Hp + MP.MARGIN, 1.0)))
        finfo = [{'index': 0, 'rel': svg.name, 'path': str(svg.resolve()), 'scale_pt_per_unit': 1.0, 'scale_note': 'pdf', 'scale_confidence': 'good',
                  'viewBox': [round(v, 3) for v in vb], 'frame_src': [round(v, 3) for v in frame], 'print_w_pt': round(Wp, 1), 'print_h_pt': round(Hp, 1),
                  'n_elements': len(els), 'render': 'render_0.png', 'render_px_per_pt': round(pxpt, 3)}]
        hi = LAB / 'review' / 'semantics' / 'hi' / (fid + '.png'); clean = hi if hi.exists() else svg.with_suffix('.png')
        c = r['content']; sysm = r.get('system') or {}
        info = {'id': fid, 'paper_id': pid, 'fig': fig, 'venue': r.get('venue'), 'caption': row.get('caption', ''), 'title': t.get('title', ''), 'tool': row.get('tool', ''),
                'panels': row.get('panels', ''), 'column': row.get('column', ''), 'aesthetic': t.get('rating', ''),
                'kinds': lst(c.get('kinds')), 'primary': (lst(c.get('kinds')) or ['other'])[0], 'variant': c.get('variant'), 'subfield': sysm.get('subfield'), 'subfield2': sysm.get('subfield2'),
                'tags': ft['tags'], 'tags_text': ft.get('text') or [], 'groups': lst(c.get('kinds')), 'base': None, 'patterns': None, 'grammar': r.get('summary'),
                'frames': None, 'steps': r['layout'].get('step_markers'), 'flags': {}, 'source_kind': 'pdf', 'files': finfo,
                'clean_png': str(clean.resolve()) if clean.exists() else None, 'brief': 'brief.md', 'anchors': 'anchors.json', 'dir': str(d.resolve())}
        (d / 'info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        (d / 'brief.md').write_text(brief_md(r, t, ft, voc, cmap), encoding='utf-8')
        if not a.no_render:
            gsvg, _w, _h = MP.grid_svg(str(svg), scale, frame); grid_jobs.append((gsvg, d / 'render_0.png', pxpt))
        queries = []
        for e in lst(c.get('elements')):
            for part in re.split(r'\s*/\s*', e.get('name') or ''):
                if part.strip(): queries.append((f"element: {e.get('name')}", part.strip()))
        for i in lst(c.get('idioms')):
            for part in lst(i.get('parts')):
                w = re.sub(r'\b(box|circle|arrow|icon|block|label|strip|card|node|cells?|row|column)\b', '', part, flags=re.I).strip()
                if len(w) >= 2: queries.append((f"idiom {i.get('concept')}: {part}", w))
        anchor_jobs.append((fid, d, finfo[0], frame, scale, pxpt, queries))
        figures.append(info)
    if grid_jobs: print(f'rendering {len(grid_jobs)} grid images...', flush=True); MP.render_grids(grid_jobs)
    geoms = M.measure_files([(f[2]['path'], str(f[1] / 'geom_0.json')) for f in anchor_jobs])
    for (fid, d, fi, frame, scale, pxpt, queries), g in zip(anchor_jobs, geoms):
        an = find_anchors(g, queries, scale, frame)
        (d / 'anchors.json').write_text(json.dumps(dict(figure=fid, note='box_pt in the grid units of render_0.png; el = element id for cut_parts --probe/only', anchors=an), ensure_ascii=False, indent=1), encoding='utf-8')
        if (d / 'render_0.png').exists(): draw_anchors(d / 'render_0.png', an, pxpt, d / 'anchors.png', font)
        print(f'  {fid}: {len(g["els"])} elements, {len(an)} anchors for {len(queries)} names')
    # agents
    names = [x.strip() for x in a.agents.split(',')] if not a.agents.isdigit() else [f'agent_{i + 1}' for i in range(int(a.agents))]
    order = sorted(figures, key=lambda f: (f['primary'], f['subfield'] or '', f['id']))
    buckets = {n: [] for n in names}
    for i, f in enumerate(order):
        for n in (names if a.same_for_all else [names[i % len(names)]]): buckets[n].append(f)
        f['agent'] = 'all' if a.same_for_all else names[i % len(names)]
    for n, lst_ in buckets.items():
        ad = out / 'agents' / n; (ad / 'requests').mkdir(parents=True, exist_ok=True); (ad / 'cuts').mkdir(exist_ok=True)
        (ad / 'figures.json').write_text(json.dumps([{k: f[k] for k in ('id', 'dir', 'primary', 'kinds', 'subfield', 'title', 'tags')} for f in sorted(lst_, key=lambda f: f['id'])], ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'figures.json').write_text(json.dumps(figures, ensure_ascii=False, indent=1), encoding='utf-8')
    # checklist = the vocabulary; themes; library summary
    fam_theme = {}
    for th, ids_ in THEMES.items():
        for i in ids_: fam_theme[i] = th
    L = ['# Families = the vocabulary v2 of the AI corpus (a floor, not a ceiling)', '',
         'Use these ids as `family`. `things` are drawn objects (idioms: well-known concepts with a usual drawing; parts: building blocks); `devices` are things done to a figure or its elements. '
         'pool = how many of the 336 recorded figures carry it. When a part is none of these, open `new:<slug>` and define it in discoveries.md.', '']
    S = {s['id']: s for s in json.load(open(TM / 'stats_v2.json', encoding='utf-8'))}
    for title, classes in (('Things (idioms and parts)', ('idiom', 'part')), ('Devices (modifiers)', ('modifier',))):
        L += [f'## {title}', '', '| family | theme | pool | definition |', '|---|---|---|---|']
        for e in sorted([e for e in voc.values() if e['cls'] in classes], key=lambda e: -S[e['id']]['pool'] - S[e['id']]['pool_text']):
            L.append(f"| `{e['id']}` | {fam_theme.get(e['id'], 'other')} | {S[e['id']]['pool']} | {e['definition'][:260].replace('|', '/')} |")
        L.append('')
    (out / 'checklist.md').write_text('\n'.join(L), encoding='utf-8')
    (out / 'family_themes.json').write_text(json.dumps(fam_theme, indent=0), encoding='utf-8')
    (out / 'groups.json').write_text(json.dumps(KINDS), encoding='utf-8')
    try:
        lib = json.load(open(ROOT / 'figgenie-paper-diagram' / 'assets' / 'symbols' / 'index.json', encoding='utf-8'))
        ents = lib['entries'] if isinstance(lib['entries'], list) else list(lib['entries'].values())
        icons = sorted(e['name'] for e in ents if e['kind'] == 'icon')
        fams = collections.Counter(e.get('family') for e in ents if e.get('subtype') == 'mechanism' and e.get('family'))
        L = [f'# What the parts library already holds ({len(ents)} parts)', '', f'## Icons ({len(icons)}; do not cut the same icon in the same style again, a different style is welcome)', '', ', '.join(icons), '',
             f'## Mechanism-figure device families ({len(fams)}; AI figures reuse many of these: a check/cross, a step badge, a brace, a zoom wedge is only worth cutting in a new style)', '',
             ', '.join(f'{k} ({v})' for k, v in fams.most_common()), '']
        (out / 'library_summary.md').write_text('\n'.join(L), encoding='utf-8')
    except Exception as exc:  # noqa: BLE001
        print('library summary skipped:', exc)
    print(f'done in {(time.time() - t0) / 60:.1f} min: {len(figures)} figures, agents {names} -> {out}')
    print('by kind:', dict(collections.Counter(f['primary'] for f in figures)), '| by sub-field:', dict(collections.Counter(f['subfield'] for f in figures)))


if __name__ == '__main__':
    main()
