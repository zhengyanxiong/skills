#!/usr/bin/env python3
"""Style statistics of the AI-venue Figure 1s (family `ai`) - the counterpart of style_stats.py, read from the Figure 1
table (ai-corpus/lab/fig1_table.jsonl, written by ai-corpus/scripts/fig1_table.py) instead of the corpus index.

    python3 figgenie-paper-diagram/scripts/distill/ai_style_stats.py [--table PATH] [--out DIR] [--min-n 15]

Two sources of numbers, kept apart in the output:

  measured    the `style` record the corpus builder measured on the figure's SVG at print size (fonts, strokes, colours,
              arrows, density, size; style_stats.build_metrics defines every metric), plus the width as a share of the
              venue's text width and the drawing tool. Exists for a figure with a vector Figure 1 from the PDF.
  labelled    the attributes of the pre-screen record (prescreen_v2.jsonl: base, panels, reading direction, pictures,
              icons, hues, ground, legend ...), written by a model that looked at the gallery picture. Exists for every
              figure, the bitmap ones included.

Populations
  corpus      every designed figure (figure_class diagram / diagram-plus-results); for the measured metrics those whose
              extracted SVG is the gallery picture (fig1 status match / match-other-fig)
  good, ok, bad, ok+bad   the human ratings (discard is left out). The good-vs-(ok+bad) contrast of the measured metrics
              uses every rated figure with an SVG: the rating was given to that very figure. Everything that is sliced
              by a label (kind, subfield) or contrasts a labelled attribute uses only the figures whose SVG is the
              gallery picture, because the labels describe the gallery picture.

Slices: the whole family, the 8 figure kinds, the 9 subfields - one column each, so a slice is read against the family.
Kinds overlap: the seven pre-screen kinds are sliced by a figure's primary kind; the contribution mosaics (labelled by a
later pass, fig1_table `mosaic`) are one more slice that cuts across them.

The rated set is a stratified sample (thin kinds, thin subfields and oral / spotlight papers are over-drawn), so
frequencies are quoted from the corpus population, never from the rated one; the rated groups serve the contrast.

Contrast: Cliff's delta with a Mann-Whitney p (numeric), difference of shares with a two-proportion p (categorical),
Benjamini-Hochberg adjusted within each slice. A slice with fewer than --min-n figures in a group is not contrasted.

Outputs in --out: numeric_distributions.csv, contrast_numeric.csv, categorical_distributions.csv, contrast_categorical.csv
(measured and labelled attributes, column `source`), tool_by_rating.csv, summary.json and style_tables.md (the tables a
person reads: whole family with the contrast, then medians / shares per kind and per subfield).
"""
import argparse, collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))
sys.path.insert(0, HERE)
from style_stats import build_metrics, pct_stats, cliffs_delta, delta_magnitude, mwu_p, two_prop_p, bh_fdr, write_csv

KINDS = ['stage-pipeline', 'model-anatomy', 'side-by-side-contrast', 'concept-schematic', 'scope-overview', 'worked-walkthrough', 'actor-interaction', 'contribution-mosaic']
DOMAINS = ['llm-nlp', 'ml-core', 'vision', 'multimodal', 'science-engineering', 'rl-robotics', 'generative', 'agents', 'audio']
TEXT_W = {'NeurIPS': 396.0, 'ICLR': 396.0, 'ICML': 486.0, 'CVPR': 495.0, 'ACL': 454.0, 'AAAI': 504.0}     # text width, pt
TWO_COLUMN = {'ICML', 'CVPR', 'ACL', 'AAAI'}
DROP_NUM = {'font.size_med_over_colwidth'}                # tied to the systems venues' column widths
LABELLED = ['base', 'panels', 'arrangement', 'reading_direction', 'step_markers', 'pictures', 'picture_role', 'picture_area', 'icons', 'icon_style',
            'bubbles', 'formulas', 'serif_labels', 'hues', 'ground', 'legend', 'frozen_fire', 'density']
GROUPS = ['corpus', 'good', 'ok', 'bad', 'ok+bad']
C = collections.Counter


def width_class(venue, w):
    tw = TEXT_W.get(venue)
    if not tw or not w: return None, '(unknown)'
    f = w / tw
    return round(f, 3), ('column' if venue in TWO_COLUMN and f <= 0.6 else 'full' if f >= 0.85 else 'partial')


def load(path):
    recs = []
    for line in open(path, encoding='utf-8'):
        r = json.loads(line)
        if not r['designed'] and not r['rating']: continue
        rec = dict(paper_id=r['paper_id'], venue=r['venue'], year=r['year'], tier=r['tier'], kind=r['kind'], mosaic=bool(r.get('mosaic')), domain=r['domain'], rating=r['rating'],
                   designed=r['designed'], verified=r['fig1_status'] in ('match', 'match-other-fig'), measured=bool(r['measure'] and r['style']),
                   in_index=r['fig1_status'] in ('match', 'match-other-fig', 'mismatch'), num={}, cat={}, lab={})
        if rec['measured']:
            num, cat = build_metrics(r['style'], 'double')
            rec['num'] = {k: v for k, v in num.items() if k not in DROP_NUM}
            rec['num']['size.width_frac'], cat['size.width_class'] = width_class(r['venue'], num.get('size.w'))
            cat['tool'] = r.get('tool') or 'unknown'; rec['cat'] = cat
        pre = r.get('pre') or {}
        rec['lab'] = {k: (str(pre[k]) if k in pre and pre[k] is not None and pre[k] != '' else '(none)') for k in LABELLED} if pre else {}
        for k, bins in (('pictures', ((0, '0'), (2, '1-2'), (5, '3-5'), (10 ** 9, '6+'))), ('panels', ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (10 ** 9, '5+')))):
            if rec['lab'].get(k, '').isdigit(): rec['lab'][k] = next(name for top, name in bins if int(rec['lab'][k]) <= top)      # counts -> bands
        recs.append(rec)
    return recs


def in_group(r, g):
    if g == 'corpus': return r['designed']
    if g == 'ok+bad': return r['rating'] in ('ok', 'bad')
    return r['rating'] == g


def slices():
    # kinds overlap: the seven pre-screen kinds are sliced by the primary one, the contribution mosaics are a slice across them
    return [('all', lambda r: True)] + [('kind:' + k, (lambda k: lambda r: r['mosaic'] if k == 'contribution-mosaic' else r['kind'] == k)(k)) for k in KINDS] + \
           [('subfield:' + d, (lambda d: lambda r: r['domain'] == d)(d)) for d in DOMAINS]


def population(recs, source, sl, g):
    """The figures a (source, slice, group) cell is computed on (see the module docstring)."""
    out = []
    for r in recs:
        if not in_group(r, g): continue
        if source == 'measured':
            if not r['measured']: continue
            if (g == 'corpus' or sl != 'all') and not r['verified']: continue
        else:
            if not r['lab']: continue
            if g != 'corpus' and r['in_index'] and not r['verified']: continue      # rated on an extracted figure that is not the labelled picture
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--table', default=os.path.join(REPO, 'ai-corpus', 'lab', 'fig1_table.jsonl'))
    ap.add_argument('--out', default=os.path.join(REPO, 'ai-corpus', 'lab', 'distill', 'style')); ap.add_argument('--min-n', type=int, default=15)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    recs = load(a.table)
    num_keys = [k for k in build_metrics({}, 'double')[0] if k not in DROP_NUM] + ['size.width_frac']
    cat_keys = list(build_metrics({}, 'double')[1]) + ['size.width_class', 'tool']
    nd, cn, cd, cc, counts = [], [], [], [], {}
    for sl, f in slices():
        pop = {(src, g): [r for r in population(recs, src, sl, g) if f(r)] for src in ('measured', 'labelled') for g in GROUPS}
        counts[sl] = {f'{src}/{g}': len(v) for (src, g), v in pop.items()}
        # numeric, measured
        rows = []
        for k in num_keys:
            vals = {g: [r['num'].get(k) for r in pop[('measured', g)]] for g in GROUPS}
            for g in GROUPS: nd.append(dict(metric=k, slice=sl, group=g, **pct_stats(vals[g])))
            ga, gb = [v for v in vals['good'] if v is not None], [v for v in vals['ok+bad'] if v is not None]
            if len(ga) >= a.min_n and len(gb) >= a.min_n:
                d, n1, n2 = cliffs_delta(ga, gb); p, how = mwu_p(ga, gb)
                rows.append(dict(metric=k, slice=sl, n_good=n1, n_other=n2, median_good=pct_stats(ga)['p50'], median_other=pct_stats(gb)['p50'],
                                 cliffs_delta=round(d, 4), magnitude=delta_magnitude(d), p=p, p_method=how))
        for r, q in zip(rows, bh_fdr([r['p'] for r in rows])): r['q'] = q
        cn += rows
        # categorical: measured and labelled
        rows = []
        for src, keys, field in (('measured', cat_keys, 'cat'), ('labelled', LABELLED, 'lab')):
            for k in keys:
                cnt = {g: C(r[field].get(k, '(none)') for r in pop[(src, g)]) for g in GROUPS}
                tot = {g: sum(cnt[g].values()) for g in GROUPS}
                for v in sorted(set().union(*[set(c) for c in cnt.values()]), key=lambda v: -cnt['corpus'][v]):
                    for g in GROUPS:
                        if tot[g]: cd.append(dict(source=src, metric=k, value=str(v), slice=sl, group=g, n=tot[g], count=cnt[g][v], frac=round(cnt[g][v] / tot[g], 4)))
                    if tot['good'] >= a.min_n and tot['ok+bad'] >= a.min_n and cnt['good'][v] + cnt['ok+bad'][v] >= 5:
                        fg, fo = cnt['good'][v] / tot['good'], cnt['ok+bad'][v] / tot['ok+bad']
                        rows.append(dict(source=src, metric=k, value=str(v), slice=sl, n_good=tot['good'], n_other=tot['ok+bad'], frac_good=round(fg, 4), frac_other=round(fo, 4),
                                         diff=round(fg - fo, 4), p=two_prop_p(cnt['good'][v], tot['good'], cnt['ok+bad'][v], tot['ok+bad'])))
        for r, q in zip(rows, bh_fdr([r['p'] for r in rows])): r['q'] = q
        cc += rows
    write_csv(os.path.join(a.out, 'numeric_distributions.csv'), ['metric', 'slice', 'group', 'n', 'mean', 'p5', 'p25', 'p50', 'p75', 'p95'], nd)
    write_csv(os.path.join(a.out, 'contrast_numeric.csv'), ['metric', 'slice', 'n_good', 'n_other', 'median_good', 'median_other', 'cliffs_delta', 'magnitude', 'p', 'p_method', 'q'], cn)
    write_csv(os.path.join(a.out, 'categorical_distributions.csv'), ['source', 'metric', 'value', 'slice', 'group', 'n', 'count', 'frac'], cd)
    write_csv(os.path.join(a.out, 'contrast_categorical.csv'), ['source', 'metric', 'value', 'slice', 'n_good', 'n_other', 'frac_good', 'frac_other', 'diff', 'p', 'q'], cc)
    tools = C((r['cat'].get('tool', 'unknown'), r['rating']) for r in recs if r['measured'] and r['rating'])
    tool_rows = [dict(tool=t, **{g: tools[(t, g)] for g in ('good', 'ok', 'bad', 'discard')}) for t in sorted({t for t, _ in tools}, key=lambda t: -sum(tools[(t, g)] for g in ('good', 'ok', 'bad', 'discard')))]
    write_csv(os.path.join(a.out, 'tool_by_rating.csv'), ['tool', 'good', 'ok', 'bad', 'discard'], tool_rows)
    json.dump(dict(counts=counts, numeric=nd, contrast_numeric=cn, categorical=cd, contrast_categorical=cc, tools=tool_rows, text_width=TEXT_W, two_column=sorted(TWO_COLUMN)),
              open(os.path.join(a.out, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    # ---- the tables a person reads -------------------------------------------------------------------------------
    N = {(r['metric'], r['slice'], r['group']): r for r in nd}; CN = {(r['metric'], r['slice']): r for r in cn}
    CD = {(r['source'], r['metric'], r['value'], r['slice'], r['group']): r for r in cd}; CC = {(r['source'], r['metric'], r['value'], r['slice']): r for r in cc}
    def fmt(v):
        if v is None: return '-'
        v = float(v); return f'{v:.0f}' if abs(v) >= 100 else f'{v:.1f}' if abs(v) >= 10 else f'{v:.2f}'
    sig = lambda q: '' if q is None else ' **' if q < 0.01 else ' *' if q < 0.05 else ''
    c0 = counts['all']
    md = ['# AI-family Figure 1s: style statistics', '',
          f"Measured on the SVG: corpus {c0['measured/corpus']} figures, good {c0['measured/good']}, ok {c0['measured/ok']}, bad {c0['measured/bad']}. "
          f"Labelled (pre-screen): corpus {c0['labelled/corpus']}, good {c0['labelled/good']}, ok {c0['labelled/ok']}, bad {c0['labelled/bad']}.",
          'Contrast = good against ok + bad; `*` q < 0.05, `**` q < 0.01 (Benjamini-Hochberg within the slice). A dash: fewer than '
          f'{a.min_n} figures.', '', '## 1. Measured metrics, whole family', '',
          '| metric | corpus p50 | good p5 | good p50 | good p95 | ok+bad p50 | Cliff delta | |', '|---|---|---|---|---|---|---|---|']
    for k in num_keys:
        g, o, c, ct = N[(k, 'all', 'good')], N[(k, 'all', 'ok+bad')], N[(k, 'all', 'corpus')], CN.get((k, 'all'))
        md.append(f"| {k} | {fmt(c['p50'])} | {fmt(g['p5'])} | {fmt(g['p50'])} | {fmt(g['p95'])} | {fmt(o['p50'])} | {fmt(ct['cliffs_delta']) if ct else '-'} | {(ct['magnitude'] + sig(ct['q'])) if ct else ''} |")
    for title, names in (('## 2. Measured metrics, median of the good figures per kind', ['kind:' + k for k in KINDS]),
                         ('## 3. Measured metrics, median of the good figures per subfield', ['subfield:' + d for d in DOMAINS])):
        md += ['', title, '', '| metric | family | ' + ' | '.join(n.split(':')[1] for n in names) + ' |', '|---|---|' + '---|' * len(names),
               '| n good | ' + str(c0['measured/good']) + ' | ' + ' | '.join(str(counts[n]['measured/good']) for n in names) + ' |']
        for k in num_keys:
            md.append(f"| {k} | {fmt(N[(k, 'all', 'good')]['p50'])} | " + ' | '.join(fmt(N[(k, n, 'good')]['p50']) if N[(k, n, 'good')]['n'] >= a.min_n else '-' for n in names) + ' |')
    def cat_tables(src, keys, group, head):
        out = []
        for title, names in ((f'{head}, whole family with the contrast', None), (f'{head}, share per kind ({group})', ['kind:' + k for k in KINDS]),
                             (f'{head}, share per subfield ({group})', ['subfield:' + d for d in DOMAINS])):
            out += ['', '## ' + title, '']
            if names is None: out += ['| attribute | value | corpus | good | ok+bad | diff | |', '|---|---|---|---|---|---|---|']
            else: out += ['| attribute | value | family | ' + ' | '.join(n.split(':')[1] for n in names) + ' |', '|---|---|---|' + '---|' * len(names)]
            for k in keys:
                vals = [v for v in dict.fromkeys(r['value'] for r in cd if r['source'] == src and r['metric'] == k and r['slice'] == 'all')
                        if (CD.get((src, k, v, 'all', 'corpus')) or {}).get('frac', 0) >= 0.03 or (CD.get((src, k, v, 'all', 'good')) or {}).get('frac', 0) >= 0.03]
                for v in vals:
                    pc = lambda sl, g: (f"{100 * CD[(src, k, v, sl, g)]['frac']:.0f}%" if (src, k, v, sl, g) in CD else ('0%' if counts[sl][f'{src}/{g}'] >= a.min_n else '-'))
                    if names is None:
                        ct = CC.get((src, k, v, 'all'))
                        out.append(f"| {k} | {v} | {pc('all', 'corpus')} | {pc('all', 'good')} | {pc('all', 'ok+bad')} | {(f'{100 * ct['diff']:+.0f}') if ct else '-'} | {sig(ct['q']).strip() if ct else ''} |")
                    else:
                        out.append(f"| {k} | {v} | {pc('all', group)} | " + ' | '.join(pc(n, group) if counts[n][f'{src}/{group}'] >= a.min_n else '-' for n in names) + ' |')
        return out
    md += cat_tables('measured', cat_keys, 'good', 'Measured categorical attributes') + cat_tables('labelled', LABELLED, 'corpus', 'Labelled attributes')
    md += ['', '## Drawing tool by rating (measured figures)', '', '| tool | good | ok | bad | discard | good share |', '|---|---|---|---|---|---|']
    md += [f"| {t['tool']} | {t['good']} | {t['ok']} | {t['bad']} | {t['discard']} | {100 * t['good'] / max(1, t['good'] + t['ok'] + t['bad']):.0f}% |" for t in tool_rows if t['good'] + t['ok'] + t['bad'] >= 5]
    open(os.path.join(a.out, 'style_tables.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(f"{len(recs)} figures; measured: corpus {c0['measured/corpus']}, good {c0['measured/good']}, ok+bad {c0['measured/ok+bad']}; "
          f"labelled: corpus {c0['labelled/corpus']}, good {c0['labelled/good']}, ok+bad {c0['labelled/ok+bad']} -> {a.out}")


if __name__ == '__main__':
    main()
