"""Shared loader and table helpers of the AI-family distillation scripts (ai_grounds / ai_palettes / ai_layouts / ai_encoding).

The sample is the exemplar pool of the AI family: the figures with a semantic record of kind `ai`
(ai-corpus/lab/extracted/corpus_semantics.jsonl, schema paper-figure-corpus/references/semantics-schema-ai.md), joined with the
per-paper table (ai-corpus/lab/fig1_table.jsonl: venue, year, rating, measured style, mosaic label). The pool was chosen for
coverage among figures rated good, so every share computed here is a share of the pool; where the pre-screen labelled the same
attribute on all 3,274 designed figures, `corpus_share()` gives that number to put next to it.

Views: every table is printed for the whole pool, per figure kind and per sub-field (the two-view rule of the family: the
general table and the sub-field column are always read together). A figure counts under its FIRST kind in the per-kind rows;
kinds overlap (88% of the pool carry two or more), so `any_kind()` is there for the tables that want every figure of a kind.
"""
import collections, csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))
AI = os.path.join(REPO, 'ai-corpus'); LAB = os.path.join(AI, 'lab'); DISTILL = os.path.join(LAB, 'distill')
sys.path.insert(0, HERE)
from palette_cluster import rgb, hls, is_grey, hue_family, rel_lum, contrast          # colour helpers shared with the systems family
C = collections.Counter
KINDS = ['stage-pipeline', 'model-anatomy', 'side-by-side-contrast', 'worked-walkthrough', 'concept-schematic', 'scope-overview', 'actor-interaction', 'contribution-mosaic']
SHORT = {'stage-pipeline': 'pipeline', 'model-anatomy': 'anatomy', 'side-by-side-contrast': 'contrast', 'worked-walkthrough': 'walkthrough', 'concept-schematic': 'concept',
         'scope-overview': 'scope', 'actor-interaction': 'actors', 'contribution-mosaic': 'mosaic', 'other': 'other'}
SUBS = ['llm-nlp', 'multimodal', 'vision', 'generative', 'agents', 'rl-robotics', 'audio', 'science-engineering', 'ml-core']
HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def lst(x): return x if isinstance(x, list) else ([] if x in (None, '') else [x])
def pct(n, d): return f'{100 * n / d:.0f}%' if d else '-'
def as_set(x): return set(x) if isinstance(x, (set, frozenset, list, tuple)) else (set() if x in (None, '') else {x})


def load():
    """One dict per pool figure: rec (the semantic record), row (fig1_table), id, kinds, kind (first), sub (sub-field)."""
    tab = {r['paper_id']: r for r in (json.loads(l) for l in open(os.path.join(LAB, 'fig1_table.jsonl'), encoding='utf-8'))}
    out = []
    for line in open(os.path.join(LAB, 'extracted', 'corpus_semantics.jsonl'), encoding='utf-8'):
        r = json.loads(line)
        if r.get('kind') != 'ai': continue
        ks = [k for k in lst(r['content'].get('kinds')) if k in KINDS] or ['other']
        sub = (r.get('system') or {}).get('subfield') or 'other'
        out.append(dict(rec=r, row=tab.get(r['paper_id'], {}), id=f"{r['paper_id']}_fig{r['fig']}", kinds=ks, kind=ks[0], sub=sub if sub in SUBS else 'other'))
    return out


def views(data, min_n=8):
    """[(label, figures)]: the pool, then one row per first kind, then one per sub-field (groups under min_n are left out)."""
    v = [('all', data)]
    v += [(SHORT[k], [d for d in data if d['kind'] == k]) for k in KINDS]
    v += [(s, [d for d in data if d['sub'] == s]) for s in SUBS]
    return [(n, g) for n, g in v if len(g) >= min_n]


def any_kind(data, k): return [d for d in data if k in d['kinds']]


def md_table(head, rows):
    return ['| ' + ' | '.join(map(str, head)) + ' |', '|' + '|'.join('---' if i == 0 else '---:' for i in range(len(head))) + '|'] + ['| ' + ' | '.join(map(str, r)) + ' |' for r in rows] + ['']


def share_table(data, cats, has, title=None, note=None, vs=None, counts=False):
    """Rows = views, columns = categories; a cell is the share of the view's figures for which has(d) contains the category
    (has returns a set, so categories may overlap and rows need not add up to 100%)."""
    out = ([f'### {title}', ''] if title else []) + ([note, ''] if note else [])
    rows = []
    for name, g in (vs or views(data)):
        hs = [as_set(has(d)) for d in g]
        rows.append([name, len(g)] + [(f'{sum(1 for h in hs if c in h)}' if counts else pct(sum(1 for h in hs if c in h), len(g))) for c in cats])
    return out + md_table(['', 'n'] + list(cats), rows)


def top_cats(data, has, n=10, floor=0.0):
    c = C(x for d in data for x in as_set(has(d)))
    return [k for k, v in c.most_common(n) if v / max(1, len(data)) >= floor and k not in (None, '')]


def quant(vals, qs=(0.1, 0.25, 0.5, 0.75, 0.9)):
    v = sorted(x for x in vals if isinstance(x, (int, float)))
    return [v[min(len(v) - 1, int(q * len(v)))] for q in qs] if v else [None] * len(qs)


def corpus_share(metric, group='corpus', sl='all'):
    """value -> share among the pre-screened designed figures (lab/distill/style/categorical_distributions.csv, source `labelled`)."""
    p = os.path.join(DISTILL, 'style', 'categorical_distributions.csv'); out = {}
    if not os.path.exists(p): return out
    for r in csv.DictReader(open(p, encoding='utf-8')):
        if r['source'] == 'labelled' and r['metric'] == metric and r['slice'] == sl and r['group'] == group: out[r['value']] = (float(r['frac']), int(r['n']))
    return out


def write_csv(path, head, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(head); w.writerows(rows)


def write_md(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


POOL_NOTE = ('Shares are shares of the exemplar pool (figures rated good, chosen for coverage), read off the semantic records; they describe what good '
             'figures do, not what a figure must do. Rows: the whole pool, then by first figure kind, then by sub-field.')


BINS = {'pictures': ((0, '0'), (2, '1-2'), (5, '3-5'), (10 ** 9, '6+')), 'panels': ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (10 ** 9, '5+'))}      # as in ai_style_stats.py


def pre_value(d, m):
    v = (d['row'].get('pre') or {}).get(m)
    if m in BINS:
        try: return next(lab for hi, lab in BINS[m] if int(v) <= hi)
        except (TypeError, ValueError): return ''
    return str(v)


def pool_vs_corpus():
    """How the exemplar pool differs from the corpus, on the attributes the pre-screen labelled for every designed figure:
    the pool's own pre-screen labels against all designed figures and against those rated good (like for like, so a
    difference is selection, not a change of definition)."""
    data = load(); n = len(data); rows = []
    metrics = ['base', 'panels', 'arrangement', 'reading_direction', 'step_markers', 'pictures', 'picture_role', 'picture_area', 'icons', 'icon_style', 'bubbles', 'formulas', 'serif_labels',
               'hues', 'ground', 'legend', 'frozen_fire', 'density']
    L = ['# Exemplar pool against the corpus', '',
         f'The pool ({n} figures) was chosen for coverage among figures rated good; the kinds with few candidates and the contribution mosaics are over-represented on purpose. '
         'This table says by how much that shifts each attribute the pre-screen labelled on all designed figures. Read a pool share from the other tables with the shift of its nearest attribute in mind.', '',
         '| attribute | value | corpus | rated good | pool | pool - corpus |', '|---|---|---:|---:|---:|---:|']
    for m in metrics:
        cs, cg = corpus_share(m), corpus_share(m, 'good')
        for v in sorted(cs, key=lambda v: -cs[v][0]):
            if cs[v][0] < 0.03: continue
            p = sum(1 for d in data if pre_value(d, m) == v) / n
            L.append(f'| {m} | {v} | {100 * cs[v][0]:.0f}% | {100 * cg.get(v, (0, 0))[0]:.0f}% | {100 * p:.0f}% | {100 * (p - cs[v][0]):+.0f} |'); rows.append([m, v, round(cs[v][0], 3), round(cg.get(v, (0, 0))[0], 3), round(p, 3)])
    kinds = C(d['kind'] for d in data); subs = C(d['sub'] for d in data)
    L += ['', 'First kind in the pool: ' + ', '.join(f'{SHORT[k]} {pct(v, n)}' for k, v in kinds.most_common()) + '. Sub-field: ' + ', '.join(f'{k} {pct(v, n)}' for k, v in subs.most_common()) + '.', '']
    write_md(os.path.join(DISTILL, 'pool_vs_corpus.md'), L); write_csv(os.path.join(DISTILL, 'pool_vs_corpus.csv'), ['attribute', 'value', 'corpus', 'good', 'pool'], rows)
    return L


if __name__ == '__main__':
    print('\n'.join(pool_vs_corpus()))
