#!/usr/bin/env python3
"""E. Layouts of the AI-family figures: how the canvas is divided and read.

    python3 figgenie-paper-diagram/scripts/distill/ai_layouts.py        # -> ai-corpus/lab/distill/layouts/

  layouts.md             the tables below
  figures_layout.csv     one row per figure: every enumerated layout field, the measured size, the motifs found
  panel_sequences.csv    one row per multi-panel figure: what its panels are split by and their verdicts, in order

What is enumerated and what is mined
  * arrangement, direction, reading start, panel count, legend, markers, zoom call-out, densities and the panel list are
    enumerated fields of the semantic record; width and aspect are measured on the extracted SVG (fig1_table `style.size`).
  * the composition motifs are MINED with keyword rules from `layout.arrangement_note`, the agent's own description of
    the layout (median 45 words). A motif the note does not put in these words is missed: read the counts as "how often
    the description says so".
There is no template list in this family: `arrangement` is a coarse description, and the tables show that no value
holds more than about a quarter of the pool.
"""
import os, re
from ai_common import *

OUT = os.path.join(DISTILL, 'layouts')
MOTIFS = [   # (name, what it means, regex over the arrangement note)
    ('rows', 'stacked horizontal rows or bands', r'\b(top|bottom|upper|lower|middle) (row|band|strip|half|tier)|\b(two|three|four|five|2|3|4|5) (rows|bands|tiers)\b|\brow of\b|stacked (rows|bands)'),
    ('columns', 'side-by-side columns', r'\b(left|right|middle|centre|center|first|second|third) (column|half|third)\b|\b(two|three|four|five|2|3|4|5) (columns|halves|thirds)\b'),
    ('grid', 'a regular grid of units', r'\bgrid\b|\b\d\s?(x|by)\s?\d\b|\b(two|three|four) by (two|three|four)\b'),
    ('centre-piece', 'one unit in the centre that the rest refer to', r'\b(centre|center|central|middle|hub)\b'),
    ('side-panel', 'a narrower unit attached at one side', r'\b(side (panel|column|strip|bar)|sidebar|narrow(er)? (column|strip|panel)|(right|left)[- ]hand (strip|column|panel)|on the (far )?(right|left)(,| a| an| the| is| sits| stands))'),
    ('top-strip', 'a strip along the top: title, inputs, film strip or legend', r'\b(along|across|at|on) the top\b|\btop (strip|bar|banner|edge)\b|\bheader\b|\bbanner\b'),
    ('bottom-strip', 'a strip along the bottom: legend, results, examples or a summary', r'\b(along|across|at|on) the bottom\b|\bbottom (strip|bar|edge|line)\b|\bfooter\b|\bbelow (it|them|the)\b'),
    ('input-left-output-right', 'inputs at the left, outputs at the right', r'\binputs?\b[^.;]{0,60}\b(left)\b[^.;]{0,160}\b(outputs?|results?|predictions?)\b[^.;]{0,60}\bright\b|\bfrom (the )?inputs? (on|at) the left\b|\bleft to right\b|\bleft-to-right\b'),
    ('bottom-up', 'inputs at the bottom, outputs at the top', r'\bbottom[- ]up\b|\bfrom (the )?bottom to (the )?top\b|\binputs? (at|on|along) the bottom\b|\bupwards?\b'),
    ('top-down', 'reads from the top to the bottom', r'\btop[- ]down\b|\bfrom (the )?top to (the )?bottom\b|\bdownwards?\b'),
    ('zoom', 'a part enlarged elsewhere on the canvas', r'\bzoom|\binset\b|\benlarg|\bexpanded (view|into)|\bdetail (panel|view|box)|\bmagnif'),
    ('loop', 'a cycle or ring', r'\bloops?\b|\bcycle\b|\bring\b|\bcircular\b|\bclockwise\b|\bfeeds? back\b'),
    ('fan', 'one thing fans out to several, or several merge into one', r'\bfans? (out|in)\b|\bbranch(es|ing)?\b|\bsplits? into\b|\bmerge[sd]? into\b|\bconverg'),
    ('mirrored', 'two halves drawn as mirror images or in the same grammar', r'\bmirror|\bsymmetr|\bsame (layout|grammar|structure|arrangement)\b|\bparallel (rows|lanes|columns|tracks|pipelines)\b'),
    ('cards', 'units drawn as cards or tiles', r'\bcards?\b|\btiles?\b'),
    ('timeline', 'an explicit time or step axis', r'\btimeline\b|\btime axis\b|\bstep axis\b|\balong (a|the) (time|step|training)\b|\bturn(s)? (run|stack|follow)'),
    ('chart-attached', 'a chart or plot placed beside the drawing', r'\b(bar |line |radar |scatter )?(chart|plot|histogram|curve)s?\b'),
    ('title-in-figure', 'a title, claim or logo set into the figure', r'\btitle (strip|band|bar|banner|tile|line)\b|\bheadline\b|\blogo\b|\bclaim\b'),
]
MOTIFS_C = [(n, w, re.compile(p, re.I)) for n, w, p in MOTIFS]


def size(d): return (d['row'].get('style') or {}).get('size') or {}


def main():
    data = load(); n = len(data); L = ['# E. Layouts: how the canvas is divided and read', '', POOL_NOTE, '']
    for d in data:
        lay = d['rec']['layout']; d['lay'] = lay; d['arr'] = lay.get('arrangement') or 'other'
        note = lay.get('arrangement_note') or ''; d['motifs'] = {nm for nm, _, rx in MOTIFS_C if rx.search(note)}
        d['panels'] = lst(d['rec']['content'].get('panels')); pc = lay.get('panel_count') or 1; d['pc'] = pc if isinstance(pc, int) else 1
    arrs = [a for a, _ in C(d['arr'] for d in data).most_common()]
    # ---- 1. arrangement
    ca = corpus_share('arrangement')
    L += ['## 1. Arrangement', '',
          'The pre-screen labelled a coarser field on all designed figures of the corpus: ' + ', '.join(f'{k} {100 * v[0]:.0f}%' for k, v in sorted(ca.items(), key=lambda kv: -kv[1][0])) + '.', '']
    L += share_table(data, arrs, lambda d: {d['arr']})
    # ---- 2. size
    L += ['## 2. Size by arrangement (measured)', '']
    rows = []
    for a in arrs:
        g = [d for d in data if d['arr'] == a]
        if len(g) < 5: continue
        asp = quant([size(d).get('aspect') for d in g], (0.25, 0.5, 0.75)); w = quant([size(d).get('w') for d in g], (0.5,)); h = quant([size(d).get('h') for d in g], (0.5,))
        rows.append([a, len(g), pct(sum(1 for d in g if d['lay'].get('width') == 'full'), len(g)), f'{w[0]:.0f}' if w[0] else '-', f'{h[0]:.0f}' if h[0] else '-', ' / '.join(f'{x:.2f}' for x in asp if x)])
    L += md_table(['arrangement', 'n', 'full width', 'median width pt', 'median height pt', 'aspect p25 / median / p75'], rows)
    rows = []
    for name, g in views(data):
        asp = quant([size(d).get('aspect') for d in g], (0.25, 0.5, 0.75)); h = quant([size(d).get('h') for d in g], (0.5,))
        rows.append([name, len(g), pct(sum(1 for d in g if d['lay'].get('width') == 'full'), len(g)), f'{h[0]:.0f}' if h[0] else '-', ' / '.join(f'{x:.2f}' for x in asp if x)])
    L += md_table(['', 'n', 'full width', 'median height pt', 'aspect p25 / median / p75'], rows)
    # ---- 3. panels
    cp = corpus_share('panels')
    L += ['## 3. Panels', '', 'A panel is a separately framed, lettered or titled unit. Pre-screen on the corpus: ' + ', '.join(f'{k}: {100 * v[0]:.0f}%' for k, v in sorted(cp.items())) + '.', '']
    L += share_table(data, ['1', '2', '3', '4', '5+'], lambda d: {str(d['pc']) if d['pc'] < 5 else '5+'})
    axes = [a for a, _ in C(p.get('axis') for d in data for p in d['panels'] if p.get('axis')).most_common()]
    L += share_table([d for d in data if d['pc'] > 1], axes, lambda d: {p.get('axis') for p in d['panels']}, title='What the panels of a multi-panel figure are split by',
                     note='`narrative` = problem, method, result; `alternatives` = the same thing done differently; `stages` = steps of one process; `examples` = cases side by side; `zoom` = a part enlarged.')
    seqs = []
    for d in data:
        v = [str(p.get('verdict') or '-') for p in d['panels']]
        if d['pc'] > 1: seqs.append((d, v))
    def order(v):
        o = [x for x in v if x in ('ours', 'baseline', 'fails')]
        if 'ours' not in o or not ({'baseline', 'fails'} & set(o)): return None
        return 'prior first, ours last' if o[-1] == 'ours' and o[0] != 'ours' else 'ours first' if o[0] == 'ours' and o[-1] != 'ours' else 'mixed order'
    od = C(order(v) for _, v in seqs if order(v))
    L += [f'Figures whose panels carry both a prior or failing case and the proposed one: {sum(od.values())}. Order of the panels: ' + ', '.join(f'{k} {pct(v, sum(od.values()))}' for k, v in od.most_common()) + '.', '']
    write_csv(os.path.join(OUT, 'panel_sequences.csv'), ['id', 'kind', 'subfield', 'arrangement', 'panels', 'axes', 'verdicts', 'panel kinds'],
              [[d['id'], d['kind'], d['sub'], d['arr'], d['pc'], ' | '.join(str(p.get('axis') or '-') for p in d['panels']), ' | '.join(v), ' | '.join(str(p.get('kind') or '-') for p in d['panels'])] for d, v in seqs])
    # ---- 4. reading
    cd = corpus_share('reading_direction')
    L += ['## 4. Reading', '', 'Pre-screen on the corpus: ' + ', '.join(f'{k} {100 * v[0]:.0f}%' for k, v in sorted(cd.items(), key=lambda kv: -kv[1][0])) + '.', '']
    L += share_table(data, [a for a, _ in C(d['lay'].get('direction') for d in data).most_common()], lambda d: {d['lay'].get('direction')}, title='Direction')
    L += share_table(data, [a for a, _ in C(d['lay'].get('reading_start') for d in data).most_common()], lambda d: {d['lay'].get('reading_start')}, title='Where reading starts')
    L += share_table(data, ['lanes', 'no lanes'], lambda d: {'lanes' if d['lay'].get('lanes') else 'no lanes'}, title='Lanes',
                     note='Lanes are aligned tracks (per actor, modality, method or phase) that share one axis; they are not panels.')
    # ---- 5. markers and legend
    L += ['## 5. Markers, legend, call-outs', '']
    for k, t in (('panel_markers', 'Panel markers'), ('step_markers', 'Step markers'), ('legend', 'Legend'), ('zoom_callout', 'Zoom call-out')):
        L += share_table(data, [a for a, _ in C(str(d['lay'].get(k)) for d in data).most_common()], lambda d, k=k: {str(d['lay'].get(k))}, title=t)
    # ---- 6. density
    L += ['## 6. Density', '']
    for k, t in (('visual_density', 'Visual density'), ('text_density', 'Text density'), ('text_share', 'Share of the area that is text')):
        L += share_table(data, [a for a, _ in C(str(d['lay'].get(k)) for d in data).most_common()], lambda d, k=k: {str(d['lay'].get(k))}, title=t)
    rows = []
    for name, g in views(data):
        e = quant([len(lst(d['rec']['content'].get('elements'))) for d in g], (0.25, 0.5, 0.75)); r = quant([len(lst(d['rec']['content'].get('relations'))) for d in g], (0.5,))
        t = quant([(d['row'].get('style') or {}).get('text', {}).get('n') if isinstance((d['row'].get('style') or {}).get('text'), dict) else None for d in g], (0.5,))
        rows.append([name, len(g), ' / '.join(str(x) for x in e), r[0], t[0] if t[0] is not None else '-'])
    L += ['### Amount of content', ''] + md_table(['', 'n', 'elements p25 / median / p75', 'relations median', 'text items median (measured)'], rows)
    # ---- 7. motifs
    L += ['## 7. Composition motifs (mined from the layout descriptions)', '', 'Motifs are not exclusive; most figures show several.', '']
    L += ['| motif | meaning | figures | share |', '|---|---|---:|---:|'] + [f'| `{nm}` | {w} | {sum(1 for d in data if nm in d["motifs"])} | {pct(sum(1 for d in data if nm in d["motifs"]), n)} |'
                                                                                 for nm, w, _ in sorted(MOTIFS_C, key=lambda m: -sum(1 for d in data if m[0] in d['motifs']))] + ['']
    names = [nm for nm, _, _ in sorted(MOTIFS_C, key=lambda m: -sum(1 for d in data if m[0] in d['motifs']))]
    L += share_table(data, names[:9], lambda d: d['motifs'], title='Motifs by kind and sub-field (the nine most frequent)')
    L += share_table(data, names[9:], lambda d: d['motifs'], title='Motifs by kind and sub-field (the rest)')
    L += [f'Figures with none of the motifs: {sum(1 for d in data if not d["motifs"])}. Motifs per figure: median {quant([len(d["motifs"]) for d in data], (0.5,))[0]}.', '']
    # ---- 8. examples
    L += ['## 8. Figures to look at, per arrangement', '']
    for a in arrs: L += [f'- `{a}`: ' + ', '.join(d['id'] for d in sorted((d for d in data if d['arr'] == a), key=lambda d: d['id'])[:8])]
    L += ['']
    write_md(os.path.join(OUT, 'layouts.md'), L)
    keys = ['arrangement', 'panel_count', 'direction', 'reading_start', 'legend', 'panel_markers', 'step_markers', 'zoom_callout', 'width', 'text_density', 'visual_density', 'text_share', 'nesting_depth']
    write_csv(os.path.join(OUT, 'figures_layout.csv'), ['id', 'kind', 'kinds', 'subfield'] + keys + ['lanes', 'width_pt', 'height_pt', 'aspect', 'motifs', 'arrangement_note'],
              [[d['id'], d['kind'], ' '.join(d['kinds']), d['sub']] + [d['lay'].get(k) for k in keys] + [d['lay'].get('lanes') or '', size(d).get('w'), size(d).get('h'), size(d).get('aspect'),
                                                                                                    ' '.join(sorted(d['motifs'])), d['lay'].get('arrangement_note')] for d in data])
    print(f'{n} figures -> {OUT}/layouts.md, figures_layout.csv, panel_sequences.csv')


if __name__ == '__main__':
    main()
