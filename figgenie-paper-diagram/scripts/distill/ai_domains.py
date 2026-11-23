#!/usr/bin/env python3
"""J. Sub-field differences of the AI family: what the Figure 1s of each sub-field do differently from the family as a
whole. This is the material of references/ai/domains.md (that file is written by hand from the report).

    python3 figgenie-paper-diagram/scripts/distill/ai_domains.py [--out ai-corpus/lab/distill/domains]

Samples, as in steps A-I:
  corpus  the pre-screen labels of all 3,274 designed Figure 1s (figure_class diagram / diagram-plus-results): kinds and
          variants, layout, pictures, icons, bubbles, formulas, sample data, step markers, ground, the objects drawn, the
          vocabulary entries tagged on the figure (typedisc/tagmerge/v2: explicit tags and text hits), the research
          topics of the paper (the TOPICS word list of rating_queue.py over title, keywords and sub-field note) and the
          secondary sub-field; plus the area-measured colour of the 2,470 with a vector source
  pool    the 336 figures with a semantic record: idioms, how the model is drawn, what the pictures and icons show, the
          layout (arrangement, direction, composition motifs of ai_layouts), ground and grouping, palette scheme and
          tone, and the encoding categories of ai_encoding (what colour, line style, shape, markers and emphasis say)
  parts   the parts library cut from the pool's figures (ai-parts/*/result/kept.jsonl): which part families each
          sub-field's figures supplied, against the library as a whole
A figure belongs to its primary sub-field (two thirds also carry a secondary one; they are not counted twice).
For every sub-field and binary feature: share in the sub-field, share in the family, difference in points, lift, and a
two-sided Fisher exact test of the sub-field against the rest of the family, with Benjamini-Hochberg q over all tests
of the sample. Notable: q < 0.01 and a difference of at least 6 points (corpus, colour); q < 0.10 and at least 15 points
(pool, where a sub-field has 21-69 figures). Objects drawn: weighted log-odds with an informative Dirichlet prior
(Monroe et al. 2008) over the words of the pre-screen object lists, z >= 3 and >= 6 figures. Parts: a family is listed
for a sub-field when the sub-field supplied at least 3 of its parts and its share of them is at least twice the
sub-field's share of the library (parts of one figure are not independent, so no test).
Exemplars: deep-record, rated-good, vector figures of the sub-field, ranked by how many of the sub-field's notable
features they carry (typicality), spread over kinds among the figures at least a quarter as typical as the top one.
Writes features.csv, objects.csv, parts.csv, pairs.csv, exemplars.json and domains.md under --out.
"""
import argparse, collections, csv, glob, json, math, os, re, sys
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ai_common import REPO, AI, LAB, DISTILL, KINDS, SHORT, SUBS, lst          # noqa: E402
from ai_encoding import FIELDS, CLAUSE, COLOUR_WORDS, cats_of                  # noqa: E402
sys.path.insert(0, os.path.join(AI, 'scripts'))
from rating_queue import topics_of                                             # noqa: E402

TM = os.path.join(AI, 'typedisc', 'tagmerge', 'v2')
LIBRARY = os.path.join(REPO, 'figgenie-paper-diagram', 'assets', 'exemplars', 'ai')
PARTS = os.path.join(REPO, 'ai-parts')
DESIGNED = ('diagram', 'diagram-plus-results')
SUB_NAME = {'llm-nlp': 'Language (LLM / NLP)', 'multimodal': 'Multimodal', 'vision': 'Vision', 'generative': 'Generative models',
            'agents': 'Agents', 'rl-robotics': 'RL and robotics', 'audio': 'Audio and speech', 'science-engineering': 'Science and engineering',
            'ml-core': 'Core ML (learning theory, optimisation, graphs, efficiency)'}
NOTABLE = {'corpus': (0.01, 6.0), 'colour': (0.01, 6.0), 'pool': (0.10, 15.0)}
ENC = {k: [(nm, w, re.compile(p, re.I)) for nm, w, p in rules] for k, _, rules in FIELDS}
ENC_SHORT = {'color_means': 'colour', 'line_style_means': 'line', 'shape_means': 'shape', 'marker_means': 'marker', 'emphasis': 'emphasis'}
STOP = set('a an the of and or with in on to from for by as at into over under its their his her one two three four five six seven eight nine ten '
           'each per via between small large big tiny short long left right top bottom middle centre center upper lower inner outer '
           'red orange yellow green blue purple pink grey gray black white teal cyan magenta brown violet beige gold light dark pale '
           'coloured colored labelled labeled dashed dotted solid thin thick rounded flat'.split())


def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def bh(ps):
    """Benjamini-Hochberg q-values, in input order."""
    n = len(ps); order = sorted(range(n), key=lambda i: ps[i]); q = [1.0] * n; prev = 1.0
    for rank in range(n, 0, -1):
        i = order[rank - 1]; prev = min(prev, ps[i] * n / rank); q[i] = prev
    return q


def label(f):
    """A readable name for a feature key."""
    k, _, v = f.partition(':')
    v_ = v.replace('-', ' ')
    names = {'kind': f'primary kind {SHORT.get(v, v)}', 'kind-any': f'kind {SHORT.get(v, v)} (primary or secondary)', 'variant': f'variant {v_}',
             'base': f'built as {v_}', 'arrangement': f'panels arranged as {v_}', 'reading_direction': f'reads {v_}', 'step_markers': f'step markers: {v_}',
             'ground': f'ground: {v_}', 'hues': f'{v_} hues', 'density': f'{v_}', 'icon_style': f'icons drawn {v_}', 'picture_role': f'pictures as {v_}',
             'picture_area': f'pictures take {v_} area', 'sample_data': f'sample data: {v_}', 'panels': f'{v} panels', 'pictures': {'any': 'has pictures', '5+': 'five or more pictures'}.get(v, v),
             'icons': {'any': 'has icons', 'many': 'many icons'}.get(v, v), 'idiom': f'idiom {v}', 'model': f'model drawn as {v_}',
             'picture': f'pictures of {v_}', 'picture-medium': f'pictures are {v}', 'icon': f'icons in {v_} style', 'icon-medium': f'icons are {v}',
             'examples': 'worked example with real values', 'state': f'state marked by {v_}', 'tag': f'tagged {v}', 'topic': f'topic {v}',
             'pair': f'secondary field {v}', 'layout': f'record layout {v_}', 'direction': f'record direction {v_}', 'start': f'reading starts {v_}',
             'motif': f'composition motif {v_}', 'text-share': f'text share {v_}', 'visual-density': f'visual density {v_}', 'rground': f'record ground {v_}',
             'grouping': f'grouping by {v_}', 'scheme': f'palette scheme {v_}', 'tone': f'palette tone {v_}', 'theme': f'palette theme {v_}'}
    if k == 'colour': return 'colour: ' + v
    if k.startswith('enc-'): return f'{k[4:]} says {v_}'
    if k in names: return names[k]
    return {'bubbles': 'speech / thought bubbles', 'formulas': 'formulas', 'serif_labels': 'serif labels', 'legend': 'legend', 'frozen_fire': 'frozen / trainable marks',
            'zoom': 'zoom call-out'}.get(f, f)


def corpus_features(r, tagged, kinds, topics):
    """kinds: the paper's kind list from fig1_table (pre-screen kinds plus the contribution-mosaic labels, primary first)."""
    f = set()
    if kinds: f.add('kind:' + kinds[0])
    for k in kinds: f.add('kind-any:' + k)
    if r.get('variant'): f.add('variant:' + r['variant'])
    for key in ('base', 'arrangement', 'reading_direction', 'step_markers', 'ground', 'hues', 'density', 'icon_style', 'picture_role', 'picture_area', 'sample_data'):
        v = r.get(key)
        if v not in (None, '', 'none', 'other'): f.add(f'{key}:{v}')
    try: n = int(r.get('panels') or 0)
    except (TypeError, ValueError): n = 0
    f.add('panels:1' if n <= 1 else 'panels:2-3' if n <= 3 else 'panels:4+')
    try: pics = int(r.get('pictures') or 0)
    except (TypeError, ValueError): pics = 0
    if pics > 0: f.add('pictures:any')
    if pics >= 5: f.add('pictures:5+')
    if r.get('icons') in ('few', 'many'): f.add('icons:any')
    if r.get('icons') == 'many': f.add('icons:many')
    for b in ('bubbles', 'formulas', 'serif_labels', 'legend', 'frozen_fire'):
        if r.get(b) is True: f.add(b)
    for t in tagged: f.add('tag:' + t)
    for t in topics: f.add('topic:' + t)
    if r.get('domain2') in SUBS: f.add('pair:' + r['domain2'])
    return f


def colour_features(area):
    a = area['area']; hues = a.get('hues') or {}
    chroma = a.get('pale', 0) + a.get('mid', 0) + a.get('strong', 0)
    tone = 'no colour field' if chroma < 0.02 else 'pale' if a.get('pale', 0) / chroma >= 0.6 else 'strong' if (a.get('mid', 0) + a.get('strong', 0)) / chroma >= 0.6 else 'mixed'
    f = {'colour:tone ' + tone}
    big = [h for h, v in hues.items() if v >= 0.01]
    f.add('colour:' + {0: '0-1 hue families', 1: '0-1 hue families', 2: '2 hue families', 3: '3 hue families'}.get(len(big), '4+ hue families'))
    for h in big: f.add('colour:uses ' + h)
    if hues: f.add('colour:largest hue ' + max(hues, key=hues.get))
    if a.get('pic', 0) >= 0.10: f.add('colour:pictures cover 10%+ of the canvas')
    return f


def pool_features(rec, cmap, lay, grd, pal):
    """rec: the semantic record; lay / grd / pal: the figure's rows of figures_layout / figures_ground / figures_palette.csv."""
    f = set(); c = rec['content']; st = rec.get('style') or {}
    for i in lst(c.get('idioms')):
        if i.get('concept'): f.add('idiom:' + cmap.get(i['concept'], i['concept']))
    md = st.get('model_depiction')
    if md and md not in ('none', 'other'): f.add('model:' + md)
    for p in lst(c.get('pictures')):
        if p.get('content') and p['content'] != 'other': f.add('picture:' + p['content'])
        if p.get('medium'): f.add('picture-medium:' + p['medium'])
    for i in lst(c.get('icons')):
        if i.get('style'): f.add('icon:' + i['style'])
        if i.get('medium'): f.add('icon-medium:' + i['medium'])
    if any(e.get('real_values') for e in lst(c.get('examples'))): f.add('examples:real')
    sm = st.get('state_marker')
    if sm and sm not in ('none', 'other'): f.add('state:' + sm)
    if lay:
        for key, pre in (('arrangement', 'layout'), ('direction', 'direction'), ('reading_start', 'start'), ('text_share', 'text-share'), ('visual_density', 'visual-density')):
            if lay.get(key) not in (None, '', 'none', 'other'): f.add(f'{pre}:{lay[key]}')
        if lay.get('zoom_callout') not in (None, '', 'none'): f.add('zoom')
        for m in (lay.get('motifs') or '').split(): f.add('motif:' + m)
    if grd:
        if grd.get('ground') not in (None, '', 'other'): f.add('rground:' + grd['ground'])
        for g in (grd.get('grouping') or '').split():
            if g != 'other': f.add('grouping:' + g)
    if pal:
        if pal.get('scheme'): f.add('scheme:' + pal['scheme'].replace(' ', '-'))
        if pal.get('tone') and pal['tone'] != 'not described': f.add('tone:' + pal['tone'])
        for t in (pal.get('themes') or '').split(): f.add('theme:' + t)
    enc = rec.get('encoding') or {}
    for k, _, _ in FIELDS:
        cats = cats_of(str(enc.get(k) or ''), ENC[k]) - {'none'}
        if k == 'color_means' and len([1 for m in CLAUSE.finditer(str(enc.get(k) or '')) if re.search(COLOUR_WORDS, m.group(1), re.I)]) >= 3: cats.add('per-part')
        for x in cats: f.add(f'enc-{ENC_SHORT[k]}:{x}')
    return f


def test(groups, feats_of, sample):
    """groups: {sub: [ids]}, feats_of: id -> set. Returns rows (q filled) and the number of figures tested."""
    everyone = [i for g in groups.values() for i in g]
    allf = collections.Counter(f for i in everyone for f in feats_of[i])
    N = len(everyone); rows = []
    for s in SUBS:
        g = set(groups.get(s, [])); n = len(g)
        if not n: continue
        cnt = collections.Counter(f for i in g for f in feats_of[i])
        for f, tot in allf.items():
            k = cnt.get(f, 0); rest_k = tot - k; rest_n = N - n
            if tot < 5 or f == 'pair:' + s: continue           # a sub-field is never its own secondary field
            p = fisher_exact([[k, n - k], [rest_k, rest_n - rest_k]])[1]
            sh, fam = 100 * k / n, 100 * tot / N
            rows.append(dict(sample=sample, sub=s, feature=f, label=label(f), n=n, k=k, share=round(sh, 1), family=round(fam, 1), diff=round(sh - fam, 1),
                             lift=round(sh / fam, 2) if fam else None, p=p))
    qs = bh([r['p'] for r in rows])
    for r, q in zip(rows, qs): r['q'] = q
    lim_q, lim_d = NOTABLE[sample]
    for r in rows: r['notable'] = r['q'] < lim_q and abs(r['diff']) >= lim_d
    return rows, N


IRREGULAR = {'series': 'series', 'matrices': 'matrix', 'vertices': 'vertex', 'indices': 'index', 'axes': 'axis', 'analyses': 'analysis', 'bias': 'bias', 'gaussians': 'gaussian'}


def singular(t):
    if t in IRREGULAR: return IRREGULAR[t]
    if len(t) > 4 and t.endswith('ies'): return t[:-3] + 'y'
    if len(t) > 4 and t.endswith(('xes', 'ches', 'shes', 'sses', 'zes')): return t[:-2]
    if len(t) > 3 and t.endswith('s') and not t.endswith(('ss', 'us', 'is')): return t[:-1]
    return t


def words(objs):
    out = set()
    for o in objs:
        toks = [t for t in re.findall(r"[a-z][a-z0-9+\-]*", (o or '').lower()) if t not in STOP and len(t) > 1]
        toks = [singular(t) for t in toks]
        out |= set(toks)
        out |= {f'{a} {b}' for a, b in zip(toks, toks[1:])}
    return out


def log_odds(groups, terms_of, a0=500.0, zmin=3.0, kmin=6):
    everyone = [i for g in groups.values() for i in g]
    tot = collections.Counter(t for i in everyone for t in terms_of[i]); ntot = sum(tot.values())
    out = []
    for s in SUBS:
        g = groups.get(s, [])
        if not g: continue
        ci = collections.Counter(t for i in g for t in terms_of[i]); ni = sum(ci.values()); nj = ntot - ni
        for t, y in tot.items():
            yi = ci.get(t, 0); yj = y - yi
            if yi < kmin: continue
            aw = a0 * y / ntot
            d = math.log((yi + aw) / (ni + a0 - yi - aw)) - math.log((yj + aw) / (nj + a0 - yj - aw))
            z = d / math.sqrt(1 / (yi + aw) + 1 / (yj + aw))
            if z >= zmin: out.append(dict(sub=s, term=t, figures=yi, share=round(100 * yi / len(g), 1), family=round(100 * y / len(everyone), 1), z=round(z, 2)))
    return sorted(out, key=lambda r: (SUBS.index(r['sub']), -r['z']))


def parts_table(parts):
    """Per sub-field: the part families it supplied, against the library (k >= 3 parts and lift >= 2 are 'specific')."""
    N = len(parts); fam_all = collections.Counter(p['family'] for p in parts); rows = []
    for s in SUBS:
        g = [p for p in parts if p.get('domain') == s]; n = len(g)
        if not n: continue
        c = collections.Counter(p['family'] for p in g)
        for fam, k in sorted(c.items(), key=lambda x: -x[1]):
            lift = (k / n) / (fam_all[fam] / N)
            rows.append(dict(sub=s, family=fam, parts=k, library=fam_all[fam], share=round(100 * k / n, 1), family_share=round(100 * fam_all[fam] / N, 1), lift=round(lift, 2),
                             specific=k >= 3 and lift >= 2, only_here=k == fam_all[fam]))
    return rows


def pick_exemplars(cards, s, feats, notable_pos, k=6):
    """Deep-record, rated-good, vector figures of the sub-field: the most typical ones (carrying most of the sub-field's
    notable features), spread over kinds, high-confidence records first on ties."""
    cand = []
    for c in cards:
        if not (c.get('subfield') == s and c.get('tier') == 1 and c.get('rating') == 'good' and c.get('vector')): continue
        have = feats.get(c['paper_id'], set())
        score = sum(1 for f in notable_pos if f in have)
        cand.append((c, score))
    cand.sort(key=lambda x: (-x[1], x[0].get('confidence') != 'high', x[0]['id']))
    if cand:                                   # spread over kinds only among figures that are at least a quarter as typical as the most typical one
        floor = max(1, round(0.25 * cand[0][1])); strong = [x for x in cand if x[1] >= floor]
        if len(strong) >= k: cand = strong
    picked, kinds = [], collections.Counter()
    while cand and len(picked) < k:
        best = min(cand, key=lambda x: (kinds[(x[0].get('kinds') or ['other'])[0]], -x[1], x[0].get('confidence') != 'high', x[0]['id']))
        picked.append(best); kinds[(best[0].get('kinds') or ['other'])[0]] += 1; cand.remove(best)
    return [dict(id=c['id'], kind=(c.get('kinds') or ['other'])[0], variant=c.get('variant'), title=c.get('title'), typical=sc) for c, sc in picked]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=os.path.join(DISTILL, 'domains')); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pre = [r for r in jl(os.path.join(AI, 'prescreen', 'prescreen_v2.jsonl')) if r.get('figure_class') in DESIGNED]
    tags = {o['id']: o for o in jl(os.path.join(TM, 'figure_tags_v2.jsonl'))}
    voc = {e['id']: e for e in json.load(open(os.path.join(TM, 'vocab_v2.json'), encoding='utf-8'))['entries']}
    usable = {t for t, e in voc.items() if e['cls'] in ('idiom', 'part', 'modifier')}
    cmap = {}
    for e in voc.values():
        for src in ('tags', 'idioms'):
            for al in e['aliases'][src]: cmap[al] = e['id']
        for ab in e.get('absorbs') or []: cmap[ab] = e['id']
        cmap[e['id']] = e['id']
    sub_of = {r['id']: (r.get('domain') if r.get('domain') in SUBS else 'other') for r in pre}
    groups = collections.defaultdict(list)
    for r in pre: groups[sub_of[r['id']]].append(r['id'])
    tab = {t['paper_id']: t for t in jl(os.path.join(LAB, 'fig1_table.jsonl'))}
    kinds_of = lambda r: [k for k in lst((tab.get(r['id']) or {}).get('kinds')) if k] or [k for k in (r.get('kind'), r.get('kind2'), r.get('kind3')) if k]
    tagged_of = lambda r: {t for src in ('tags', 'text', 'pre_text') for t in (tags.get(r['id'], {}).get(src) or []) if t in usable}
    feats = {r['id']: corpus_features(r, tagged_of(r), kinds_of(r), topics_of(r)) for r in pre}
    rows, N = test(groups, feats, 'corpus')
    # colour by area (vector sources)
    area = json.load(open(os.path.join(DISTILL, 'palettes', 'area_cache.json'), encoding='utf-8'))
    cg = collections.defaultdict(list)
    for pid, s in sub_of.items():
        if pid in area: cg[s].append(pid)
    cfeats = {pid: colour_features(area[pid]) for g in cg.values() for pid in g}
    crow, CN = test(cg, cfeats, 'colour')
    # pool: the semantic records joined with the per-figure rows of steps B, D, E
    recs = {r['paper_id']: r for r in jl(os.path.join(LAB, 'extracted', 'corpus_semantics.jsonl')) if r.get('kind') == 'ai'}
    per = {}
    for name, fn in (('lay', 'layouts/figures_layout.csv'), ('grd', 'grounds/figures_ground.csv'), ('pal', 'palettes/figures_palette.csv')):
        per[name] = {row['id']: row for row in csv.DictReader(open(os.path.join(DISTILL, fn), encoding='utf-8'))}
    pg = collections.defaultdict(list)
    for pid, r in recs.items():
        s = (r.get('system') or {}).get('subfield'); pg[s if s in SUBS else 'other'].append(pid)
    fid = lambda r: f"{r['paper_id']}_fig{r['fig']}"
    pfeats = {pid: pool_features(r, cmap, per['lay'].get(fid(r)), per['grd'].get(fid(r)), per['pal'].get(fid(r))) for pid, r in recs.items()}
    prow, PN = test(pg, pfeats, 'pool')
    allrows = rows + crow + prow
    with open(os.path.join(a.out, 'features.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['sample', 'sub', 'feature', 'label', 'n', 'k', 'share', 'family', 'diff', 'lift', 'p', 'q', 'notable'])
        w.writeheader(); [w.writerow({**r, 'p': f"{r['p']:.2e}", 'q': f"{r['q']:.2e}"}) for r in allrows]
    # objects
    terms = {r['id']: words(lst(r.get('objects'))) for r in pre}
    objs = log_odds(groups, terms)
    with open(os.path.join(a.out, 'objects.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['sub', 'term', 'figures', 'share', 'family', 'z']); w.writeheader(); [w.writerow(r) for r in objs]
    # secondary sub-fields
    pairs = []
    for s in SUBS:
        g = groups[s]; c = collections.Counter(next((f[5:] for f in feats[i] if f.startswith('pair:')), 'none') for i in g)
        for d2, k in c.most_common(): pairs.append(dict(sub=s, secondary=d2, figures=k, share=round(100 * k / len(g), 1)))
    with open(os.path.join(a.out, 'pairs.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['sub', 'secondary', 'figures', 'share']); w.writeheader(); [w.writerow(r) for r in pairs]
    # parts library
    parts = [dict(p, _pkg=os.path.basename(os.path.dirname(os.path.dirname(fn)))) for fn in sorted(glob.glob(os.path.join(PARTS, '*', 'result', 'kept.jsonl'))) for p in jl(fn)]
    prow_parts = parts_table(parts)
    with open(os.path.join(a.out, 'parts.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['sub', 'family', 'parts', 'library', 'share', 'family_share', 'lift', 'specific', 'only_here']); w.writeheader(); [w.writerow(r) for r in prow_parts]
    # exemplars: typicality = the number of the sub-field's notable positive corpus + pool features a figure carries
    cards = jl(os.path.join(LIBRARY, 'cards.jsonl'))
    allfeats = {pid: feats.get(pid, set()) | pfeats.get(pid, set()) for pid in set(feats) | set(pfeats)}
    ex = {}
    for s in SUBS:
        pos = {r['feature'] for r in allrows if r['sub'] == s and r['notable'] and r['diff'] > 0 and r['sample'] in ('corpus', 'pool') and not r['feature'].startswith(('pair:', 'topic:'))}
        ex[s] = pick_exemplars(cards, s, allfeats, pos)
    json.dump(ex, open(os.path.join(a.out, 'exemplars.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- report
    L = ['# J. What each sub-field draws differently', '',
         f'Corpus: {N} designed Figure 1s (pre-screen labels), colour: {CN} with a vector source (area-measured), pool: {PN} figures with a semantic record, '
         f'parts: {len(parts)} library parts. Each figure counts under its primary sub-field. "share / family" = share of the sub-field\'s figures vs share of all figures; '
         'only notable differences are listed (corpus and colour: q < 0.01 and at least 6 points; pool: q < 0.10 and at least 15 points). '
         'Full tables: features.csv, objects.csv, pairs.csv, parts.csv; exemplar picks: exemplars.json.', '']
    fam = collections.Counter(next((f[5:] for f in feats[r['id']] if f.startswith('kind:')), 'other') for r in pre)
    L += ['## Sub-fields and their primary kinds (corpus)', '', '| sub-field | n | ' + ' | '.join(SHORT[k] for k in KINDS) + ' |', '|---|---:|' + '---:|' * len(KINDS)]
    L.append(f'| family | {N} | ' + ' | '.join(f'{100 * fam[k] / N:.0f}%' for k in KINDS) + ' |')
    for s in SUBS:
        g = groups[s]
        ck = collections.Counter(next((f[5:] for f in feats[i] if f.startswith('kind:')), 'other') for i in g)
        L.append(f'| {s} | {len(g)} | ' + ' | '.join(f'{100 * ck[k] / len(g):.0f}%' for k in KINDS) + ' |')
    L.append('')
    L += ['## Secondary sub-fields (corpus)', '', '| sub-field | n | most common secondary fields | none |', '|---|---:|---|---:|']
    for s in SUBS:
        ps = [r for r in pairs if r['sub'] == s]; none = next((r['share'] for r in ps if r['secondary'] == 'none'), 0)
        L.append(f"| {s} | {len(groups[s])} | " + ', '.join(f"{r['secondary']} {r['share']:.0f}%" for r in ps if r['secondary'] != 'none')[:200] + f' | {none:.0f}% |')
    L.append('')
    by = collections.defaultdict(list)
    for r in allrows:
        if r['notable']: by[(r['sub'], r['sample'])].append(r)
    objs_by = collections.defaultdict(list)
    for o in objs: objs_by[o['sub']].append(o)
    parts_by = collections.defaultdict(list)
    for r in prow_parts: parts_by[r['sub']].append(r)
    for s in SUBS:
        nparts = sum(r['parts'] for r in parts_by[s])
        L += [f'## {s} — {SUB_NAME[s]}', '', f'corpus {len(groups[s])} figures ({100 * len(groups[s]) / N:.0f}% of the family), colour {len(cg[s])}, pool {len(pg[s])}, parts {nparts}', '']
        for sample, title in (('corpus', 'Corpus (pre-screen labels, tags, topics)'), ('colour', 'Colour by area (vector sources)'), ('pool', 'Pool (semantic records; small groups, read as indications)')):
            rs = by.get((s, sample), [])
            if not rs: continue
            more = sorted([r for r in rs if r['diff'] > 0], key=lambda r: -r['diff']); less = sorted([r for r in rs if r['diff'] < 0], key=lambda r: r['diff'])
            L += [f'**{title}**', '']
            if more: L += ['- more often: ' + '; '.join(f"{r['label']} {r['share']:.0f}% vs {r['family']:.0f}%" for r in more[:30])]
            if less: L += ['- less often: ' + '; '.join(f"{r['label']} {r['share']:.0f}% vs {r['family']:.0f}%" for r in less[:16])]
            L.append('')
        if objs_by[s]:
            L += ['**Objects that stand out** (word or word pair in the pre-screen object lists; figures, share vs family)', '',
                  ', '.join(f"{o['term']} ({o['figures']}, {o['share']:.0f}% vs {o['family']:.0f}%)" for o in objs_by[s][:24]), '']
        if parts_by[s]:
            spec = [r for r in parts_by[s] if r['specific']]; only = [r for r in parts_by[s] if r['only_here'] and r['parts'] >= 2]
            L += [f'**Parts** ({nparts} parts in {len(parts_by[s])} families; share of the family\'s parts that came from this sub-field, x lift over the sub-field\'s share of the library)', '',
                  'specific: ' + (', '.join(f"{r['family']} {r['parts']}/{r['library']} x{r['lift']:.1f}" for r in spec) or '-'),
                  'only from this sub-field (2+ parts): ' + (', '.join(f"{r['family']} {r['parts']}" for r in only) or '-'), '']
        if ex[s]:
            L += ['**Exemplars** (deep record, rated good, vector; `typical` = notable features carried)', ''] + [f"- `{e['id']}` {SHORT.get(e['kind'], e['kind'])} / {e['variant']} (typical {e['typical']}): {e['title']}" for e in ex[s]] + ['']
    open(os.path.join(a.out, 'domains.md'), 'w', encoding='utf-8').write('\n'.join(L))
    n_not = collections.Counter(r['sample'] for r in allrows if r['notable'])
    print(f'corpus {N}, colour {CN}, pool {PN}, parts {len(parts)}; tests {len(allrows)}, notable {dict(n_not)}; objects {len(objs)} -> {a.out}')


if __name__ == '__main__':
    main()
