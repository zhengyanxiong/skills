#!/usr/bin/env python3
"""Find AI-family exemplars for the figure about to be drawn, show the user a numbered sheet, list the files to read.

    python3 scripts/find_ai_exemplars.py search --kind stage-pipeline,actor-interaction --subfield agents,llm-nlp \
        --layout row --panels 3 --want icons,bubbles,examples --tags highlighted-text-spans,verdict-marks \
        --objects "LLM agent, tool calls, memory store, web page screenshot" \
        --text "<paper title>. <two or three sentences of the abstract>. <what Figure 1 must show>"
    python3 scripts/find_ai_exemplars.py search --like iclr25-0013_fig1        # more like a figure the user liked
    python3 scripts/find_ai_exemplars.py sheet ID ID ... --out candidates.png   # numbered sheet to show the user
    python3 scripts/find_ai_exemplars.py files ID ID ...                        # what to LOOK at and read for each pick
    python3 scripts/find_ai_exemplars.py card ID                                # one card in full
    python3 scripts/find_ai_exemplars.py vocab                                  # kinds + variants, sub-fields, layouts, tags

The library, assets/exemplars/ai/ (built by scripts/distill/build_ai_exemplars.py), holds one card per Figure 1 of the
AI corpus (ICLR, ICML, NeurIPS, CVPR, ACL, AAAI 2023-2026) in three tiers:
  tier 1  336 figures with a deep semantic record: print.webp, source.svg, semantics.json (what to learn, idioms, ...)
  tier 2  638 more figures a human rated good: print.webp and source.svg when the vector figure could be extracted
  tier 3  2,236 other designed figures (unrated, or rated ok, which the card says): a card and a thumbnail; their SVG
          and a larger picture are read from the local corpus when it is present, else from the gallery link

How a candidate is scored (search). Nothing is filtered out except by --tiers / --exclude; every term only adds:
  kind        the first kind given equals the card's first kind +3, is among its kinds +2; each further kind +0.75
  sub-field   the card's sub-field is the first given +2, another given +1.5; its second sub-field matches +1
  layout      --layout an arrangement name (panels-row, bands, cards-grid, ...) equal +1, same coarse class
              (row / stack / grid / radial / single) +0.6; --panels within one +0.2, equal +0.4
  content     --want / --avoid pictures, icons, bubbles, charts, formulas, examples: +0.5 / -0.5 each
  tags        --tags ids of the tag vocabulary (things that are drawn: idioms and parts; devices: modifiers; `vocab`
              lists them): +0.6 per tag the card carries, +0.3 when the tag was only found in the record's text
              (shown with a ?), at most +1.8; --sample-data equal +0.5
  meaning     BM25 of --objects and --text against four fields of the card (objects and keywords x2, what the figure
              shows and argues x1.5, paper title x1.2, abstract x0.8), scaled so the best candidate gets +4;
              a multi-word phrase of --objects found whole +0.3 (at most +0.9)
  tier        tier 1 +1.5, tier 2 +0.75; rated ok -0.5; no extracted vector figure -0.3
The script ranks; choosing by meaning is the drawing agent's job (see references/ai/exemplar-retrieval.md).
"""
import argparse, json, math, os, re, sys, urllib.request
from collections import Counter
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
LIB = SKILL / 'assets' / 'exemplars' / 'ai'
REPO = SKILL.parent                                  # where the local corpus lives when this skill sits in its build repository
CACHE = Path(os.environ.get('FIGGENIE_CACHE', Path.home() / '.cache' / 'figgenie')) / 'ai-exemplars'
KINDS = ['stage-pipeline', 'model-anatomy', 'side-by-side-contrast', 'worked-walkthrough', 'concept-schematic', 'scope-overview', 'actor-interaction', 'contribution-mosaic']
SUBS = ['llm-nlp', 'multimodal', 'vision', 'generative', 'agents', 'rl-robotics', 'audio', 'science-engineering', 'ml-core', 'other']
HAS = ['pictures', 'icons', 'bubbles', 'charts', 'formulas', 'examples']
COARSE = {'panels-row': 'row', 'pipeline-row': 'row', 'panels-column': 'stack', 'pipeline-column': 'stack', 'bands': 'stack', 'lanes': 'stack', 'chat-column': 'stack',
          'panels-grid': 'grid', 'cards-grid': 'grid', 'dashboard': 'grid', 'hub': 'radial', 'single': 'single', 'free': 'single', 'inset': 'single', 'layered': 'stack',
          'row': 'row', 'stack': 'stack', 'column': 'stack', 'grid': 'grid', 'radial': 'radial', 'nested': 'single'}
STOP = set('a an and are as at be by for from in into is it its of on or that the this to with via their each one two which when where how what who than then '
           'them they these those our we us figure fig shows show shown using used use per all any both let make makes can may also so not only we propose '
           'paper method approach based new model models first such more most over under between while within without across'.split())
TIER_NAME = {1: 'tier 1: deep semantic record', 2: 'tier 2: rated good', 3: 'tier 3: other corpus figures'}


def norm(w):
    for suf in ('ies', 'es', 's'):
        if len(w) > 4 and w.endswith(suf) and not w.endswith('ss'): return w[:-len(suf)] + ('y' if suf == 'ies' else '')
    return w


def toks(text): return [norm(w) for w in re.findall(r'[a-z0-9]+', (text or '').lower().replace('-', ' ')) if w not in STOP and len(w) > 1]
def lst(x): return x if isinstance(x, list) else ([] if x in (None, '') else [x])
def csv_(s): return [x.strip() for x in (s or '').split(',') if x.strip()]


def load():
    p = LIB / 'cards.jsonl'
    if not p.exists(): sys.exit(f'no exemplar library at {LIB} (build it with scripts/distill/build_ai_exemplars.py)')
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


class BM25:
    def __init__(self, docs, k1=1.2, b=0.75):
        self.tf = [Counter(d) for d in docs]; self.len = [len(d) for d in docs]; self.N = len(docs); self.k1, self.b = k1, b
        self.df = Counter(t for c in self.tf for t in c); self.avg = sum(self.len) / max(1, self.N)

    def idf(self, t): return math.log(1 + (self.N - self.df.get(t, 0) + 0.5) / (self.df.get(t, 0) + 0.5))

    def score(self, i, q):
        tf, L, s = self.tf[i], self.len[i], 0.0
        for t in q:
            f = tf.get(t)
            if f: s += self.idf(t) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * L / self.avg))
        return s


FIELDS = {'obj': (2.0, lambda c: ' '.join(lst(c['objects']) + lst(c['keywords']) + lst(c.get('picture_kinds')) + [c.get('sample_data') or ''] + [t.replace('-', ' ') for t in c['tags'] + lst(c.get('tags_text'))]
                                         + [d.replace('-', ' ') for d in lst(c.get('devices'))])),
          'fig': (1.5, lambda c: ' '.join([c.get('what') or '', c.get('argues') or '', c.get('summary') or '', c.get('lesson') or '', c.get('suits') or '', (c.get('layout') or {}).get('note') or '',
                                           (c.get('variant') or '').replace('-', ' '), (c.get('mosaic') or '').replace('-', ' ')])),
          'title': (1.2, lambda c: c.get('title') or ''),
          'abs': (0.8, lambda c: c.get('abstract') or '')}


def query_from_card(c):
    return dict(kind=c['kinds'], subfield=[c['subfield']] + ([c['subfield2']] if c.get('subfield2') else []), layout=(c.get('layout') or {}).get('arrangement') or (c.get('layout') or {}).get('coarse'),
                panels=(c.get('layout') or {}).get('panels'), want=[k for k in HAS if (c.get('has') or {}).get(k)], avoid=[], tags=c['tags'], sample_data=c.get('sample_data'),
                objects=', '.join(lst(c['objects']) + lst(c['keywords'])), text=' '.join([c.get('title') or '', c.get('what') or '', c.get('argues') or '']), variant=c.get('variant') or '')


def score_all(cards, q):
    fields = {k: BM25([toks(fn(c)) for c in cards]) for k, (_, fn) in FIELDS.items()}
    qt = list(dict.fromkeys(toks(q.get('objects')) + toks(q.get('text'))))
    phrases = [p.lower() for p in csv_(q.get('objects')) if len(p.split()) > 1]
    K, S, tags = q.get('kind') or [], q.get('subfield') or [], set(q.get('tags') or [])
    lay = q.get('layout') or ''; lay_c = COARSE.get(lay, lay if lay in ('row', 'stack', 'grid', 'radial', 'single') else '')
    out, text_scores = [], []
    for i, c in enumerate(cards):
        why, s = [], 0.0
        ck = c['kinds']
        if K:
            if K[0] == ck[0]: s += 3; why.append(f'kind {K[0]} (first)')
            elif K[0] in ck: s += 2; why.append(f'kind {K[0]}')
            for k in K[1:]:
                if k in ck: s += 0.75; why.append(f'+{k}')
        if S:
            if c['subfield'] in S: s += 2 if c['subfield'] == S[0] else 1.5; why.append(c['subfield'])
            elif c.get('subfield2') in S: s += 1; why.append(f"{c['subfield2']} (second)")
        L = c.get('layout') or {}
        if lay:
            if L.get('arrangement') == lay: s += 1; why.append(lay)
            elif lay_c and L.get('coarse') == lay_c: s += 0.6; why.append(f'{lay_c} layout')
        if q.get('panels') and isinstance(L.get('panels'), int):
            d = abs(L['panels'] - int(q['panels'])); s += 0.4 if d == 0 else 0.2 if d == 1 else 0
        h = c.get('has') or {}
        for k in q.get('want') or []:
            if h.get(k): s += 0.5; why.append(k)
        for k in q.get('avoid') or []:
            if h.get(k): s -= 0.5
        tg = sorted(tags & set(c['tags'])); tg2 = sorted((tags & set(c.get('tags_text') or [])) - set(tg))
        if tg or tg2: s += min(1.8, 0.6 * len(tg) + 0.3 * len(tg2)); why.append('tags ' + ','.join(tg + [t + '?' for t in tg2]))
        if q.get('sample_data') and c.get('sample_data') == q['sample_data']: s += 0.5
        if q.get('variant') and q['variant'] in (c.get('variant'), c.get('mosaic')): s += 0.75; why.append(q['variant'])
        s += {1: 1.5, 2: 0.75, 3: 0.0}[c['tier']] - (0.5 if c.get('rating') == 'ok' else 0) - (0.3 if not c.get('vector') else 0)
        t = sum(w * fields[k].score(i, qt) for k, (w, _) in FIELDS.items()) if qt else 0.0
        if phrases:
            blob = ' '.join(fn(c) for _, fn in FIELDS.values()).lower(); ph = [p for p in phrases if p in blob]
            if ph: s += min(0.9, 0.3 * len(ph)); why.append('phrases ' + '; '.join(ph[:3]))
        text_scores.append(t); out.append([s, t, why, c])
    mx = max(text_scores) if text_scores and max(text_scores) > 0 else 1.0
    for r in out: r[0] += 4.0 * r[1] / mx
    return out, qt


def matched_words(c, qt, n=7):
    bag = set(toks(' '.join(fn(c) for _, fn in FIELDS.values())))
    return [w for w in qt if w in bag][:n]


def first_sentence(t, n=220):
    t = (t or '').strip(); m = re.match(r'(.{40,}?[.!?])\s', t + ' ')
    t = m.group(1) if m else t
    return t if len(t) <= n else t[:n - 1].rstrip() + '…'


def fmt(rank, r, qt):
    s, _, why, c = r; L = c.get('layout') or {}
    has = ', '.join(k for k in HAS if (c.get('has') or {}).get(k)) or '-'
    lines = [f"{rank}. `{c['id']}`  score {s:.1f} · {', '.join(c['kinds'])} · {c['subfield']}{' / ' + c['subfield2'] if c.get('subfield2') else ''} · "
             f"{L.get('arrangement') or L.get('coarse')}, {L.get('panels') or '?'} panel(s) · has {has} · {c['venue']} {c['year']}"
             + (f" · {c['award']}" if c.get('award') else '') + (' · rated ok' if c.get('rating') == 'ok' else '') + ('' if c.get('vector') else ' · bitmap only'),
             f"   {c['title']}"]
    if c['tier'] == 1:
        lines += [f"   shows: {first_sentence(c.get('summary'))}", f"   to learn: {first_sentence(c.get('lesson'), 200)}"]
    else:
        lines += [f"   shows: {first_sentence(c.get('what'))}"] + ([f"   argues: {first_sentence(c.get('argues'), 160)}"] if c.get('argues') else [])
    mw = matched_words(c, qt)
    lines.append('   matched: ' + '; '.join(why + (['words ' + ' '.join(mw)] if mw else [])))
    return '\n'.join(lines)


def cmd_search(a):
    cards = load()
    if a.like:
        base = next((c for c in cards if c['id'] == a.like), None)
        if not base: sys.exit(f'no card {a.like}')
        q = query_from_card(base); excl = {a.like}
    else:
        q = dict(kind=csv_(a.kind), subfield=csv_(a.subfield), layout=a.layout, panels=a.panels, want=csv_(a.want), avoid=csv_(a.avoid), tags=csv_(a.tags),
                 sample_data=a.sample_data, objects=a.objects, text=a.text, variant=a.variant); excl = set()
    bad = [k for k in q['kind'] if k not in KINDS] + [s for s in q['subfield'] if s not in SUBS] + [h for h in q['want'] + q['avoid'] if h not in HAS]
    known = {t['id'] for t in json.load(open(LIB / 'vocab.json', encoding='utf-8'))['tags']}
    bad += [t for t in q['tags'] if t not in known]
    if bad: print(f'note: not in the vocabulary (see `vocab`): {", ".join(bad)}', file=sys.stderr)
    excl |= set(csv_(a.exclude)); tiers = {int(t) for t in csv_(a.tiers)}
    scored, qt = score_all(cards, q)
    scored = [r for r in scored if r[3]['id'] not in excl and r[3]['tier'] in tiers]
    scored.sort(key=lambda r: -r[0])
    per = {1: a.n1, 2: a.n2, 3: a.n3}
    picked = {t: [r for r in scored if r[3]['tier'] == t][:per[t]] for t in (1, 2, 3)}
    shown = {r[3]['id'] for t in picked for r in picked[t]}
    other = []
    if q['subfield'] and q['kind']:
        other = [r for r in scored if r[3]['subfield'] not in q['subfield'] and r[3].get('subfield2') not in q['subfield'] and q['kind'][0] in r[3]['kinds'] and r[3]['id'] not in shown][:a.nx]
    if a.json:
        print(json.dumps({'query': q, 'candidates': {f'tier{t}': [dict(id=r[3]['id'], score=round(r[0], 2), why=r[2]) for r in picked[t]] for t in picked},
                          'other_fields': [dict(id=r[3]['id'], score=round(r[0], 2), why=r[2]) for r in other]}, ensure_ascii=False, indent=1)); return
    head = ', '.join(f'{k}={v}' for k, v in q.items() if v and k not in ('text', 'objects'))
    print(f'# Exemplar candidates ({head})\n')
    print('Choose 9-12 of these BY MEANING for the sheet: what the figure must show, how its content is laid out, its field. Lean on tier 1, add some tier 2, '
          'one or two tier 3 when they fit better, and at least one from another sub-field with the same kind. Skip near-duplicates.\n')
    for t in (1, 2, 3):
        n_all = sum(1 for c in cards if c['tier'] == t)
        print(f'## {TIER_NAME[t]} ({len(picked[t])} best of {n_all})\n')
        for k, r in enumerate(picked[t], 1): print(fmt(k, r, qt) + '\n')
    if other:
        print(f'## Same kind, other sub-fields ({len(other)})\n')
        for k, r in enumerate(other, 1): print(fmt(k, r, qt) + '\n')


def best_image(c, fetch=False):
    """The largest picture of the figure available here: print.webp, then the local corpus, then the gallery (cached), then the thumbnail."""
    f = c['files']
    for key, root in (('print', LIB), ('corpus_png', REPO), ('gallery', REPO)):
        if f.get(key) and (root / f[key]).exists(): return root / f[key]
    if fetch and f.get('gallery_url'):
        dst = CACHE / (c['id'] + Path(f['gallery_url']).suffix)
        if not dst.exists():
            try:
                dst.parent.mkdir(parents=True, exist_ok=True); urllib.request.urlretrieve(f['gallery_url'], dst)
            except Exception as e: print(f'  (could not fetch {f["gallery_url"]}: {e})', file=sys.stderr)
        if dst.exists(): return dst
    return LIB / f['thumb']


def wrap(text, font, width, lines):
    """Break a title into at most `lines` lines that fit `width` px, by words; the last line ends with … when cut."""
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if font.getlength(t) <= width: cur = t; continue
        out.append(cur); cur = w
        if len(out) == lines: break
    if len(out) < lines and cur: out.append(cur); cur = ''
    if cur or len(' '.join(out)) < len(text.strip()):
        last = out[-1]
        while last and font.getlength(last + '…') > width: last = last[:-1]
        out[-1] = last.rstrip() + '…'
    return out


def cmd_sheet(a):
    from PIL import Image, ImageDraw, ImageFont
    cards = {c['id']: c for c in load()}; ids = a.ids
    miss = [i for i in ids if i not in cards]
    if miss: sys.exit('unknown ids: ' + ', '.join(miss))
    fdir = SKILL / 'assets' / 'fonts'
    F = lambda n, s: ImageFont.truetype(str(fdir / n), s)
    big, mid, small = F('DejaVuSans-Bold.ttf', 30), F('DejaVuSans-Bold.ttf', 15), F('DejaVuSans.ttf', 14)
    cols = a.cols or (3 if len(ids) > 4 else 2); W, H, HEAD, FOOT = 540, 330, 40, 44
    rows = math.ceil(len(ids) / cols)
    im = Image.new('RGB', (cols * (W + 16) + 16, rows * (H + HEAD + FOOT + 16) + 16 + 34), 'white'); dr = ImageDraw.Draw(im)
    badge = {1: ('★', '#b45309'), 2: ('✓', '#15803d'), 3: ('', '#6b7280')}
    for k, i in enumerate(ids):
        c = cards[i]; x = 16 + (k % cols) * (W + 16); y = 16 + (k // cols) * (H + HEAD + FOOT + 16)
        dr.rounded_rectangle([x - 6, y - 6, x + W + 6, y + HEAD + H + FOOT + 2], 8, outline='#d4d4d4', width=1)
        dr.text((x, y), str(k + 1), fill='#111111', font=big)
        b, col = badge[c['tier']]
        if b: dr.text((x + 46, y + 6), b, fill=col, font=F('DejaVuSans-Bold.ttf', 22))
        dr.text((x + 78, y + 12), f"{c['kinds'][0]} · {c['subfield']} · {c['venue']} {c['year']}", fill='#374151', font=mid)
        try:
            pic = Image.open(LIB / c['files']['thumb'] if a.small else best_image(c, a.fetch)).convert('RGB')
        except Exception:
            pic = Image.open(LIB / c['files']['thumb']).convert('RGB')
        r = min(W / pic.width, H / pic.height); pic = pic.resize((max(1, int(pic.width * r)), max(1, int(pic.height * r))), Image.LANCZOS)
        im.paste(pic, (x + (W - pic.width) // 2, y + HEAD + (H - pic.height) // 2))
        for j, line in enumerate(wrap(c['title'], small, W, 2)): dr.text((x, y + HEAD + H + 6 + 18 * j), line, fill='#111111', font=small)
    dr.text((16, im.height - 30), '★ deep semantic record   ✓ rated good   (no mark) other corpus figure', fill='#6b7280', font=small)
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); im.save(out)
    print(f'sheet -> {out.resolve()}\n')
    print('| # | id | tier | kind | sub-field | paper |\n|---|---|---|---|---|---|')
    for k, i in enumerate(ids, 1):
        c = cards[i]; print(f"| {k} | `{i}` | {c['tier']} | {', '.join(c['kinds'][:2])} | {c['subfield']} | {c['title'][:80]} ({c['venue']} {c['year']}) |")


def cmd_files(a):
    cards = {c['id']: c for c in load()}
    for k, i in enumerate(a.ids, 1):
        c = cards.get(i)
        if not c: print(f'## {k}. {i}: unknown id\n'); continue
        f = c['files']; L = c.get('layout') or {}
        print(f"## {k}. `{i}`: {c['title']} ({c['venue']} {c['year']}, {TIER_NAME[c['tier']]})\n\n- paper: {c.get('paper_url')}")
        img = best_image(c, a.fetch)
        print(f'- LOOK at: {img}' + ('  (a thumbnail only; open the paper link for a larger picture)' if img.parent.name == 'thumbs' else ''))
        svg = LIB / f['svg'] if f.get('svg') and (LIB / f['svg']).exists() else (REPO / f['corpus_svg'] if f.get('corpus_svg') and (REPO / f['corpus_svg']).exists() else None)
        print(f'- READ how it is built: {svg}' if svg else '- no SVG here: the figure is a bitmap, or its vector file is not in this installation')
        if f.get('semantics'): print(f"- semantic record: {LIB / f['semantics']}  (lessons, idioms, encoding, weaknesses)")
        print(f"- kinds: {', '.join(c['kinds'])}{' (' + c['variant'] + ')' if c.get('variant') else ''} · sub-field {c['subfield']}{' / ' + c['subfield2'] if c.get('subfield2') else ''}"
              f" · layout {L.get('arrangement') or L.get('coarse')}, {L.get('panels') or '?'} panel(s), {L.get('direction') or '?'} · size {(c.get('size') or {}).get('w')} x {(c.get('size') or {}).get('h')} pt")
        if c.get('lesson'): print(f"- to learn: {c['lesson']}")
        print(f"- shows: {c.get('summary') or c.get('what')}")
        if c.get('argues'): print(f"- argues: {c['argues']}")
        print()


def cmd_card(a):
    c = next((c for c in load() if c['id'] == a.id), None)
    if not c: sys.exit(f'no card {a.id}')
    print(json.dumps(c, ensure_ascii=False, indent=1))


def cmd_vocab(a):
    v = json.load(open(LIB / 'vocab.json', encoding='utf-8'))
    print('# Kinds (overlap; first = primary)\n')
    for k in v['kinds']: print(f"- `{k['id']}`: {k['definition'][:160]}\n  variants: " + ', '.join(x['id'] for x in k['variants']))
    print('\n# Sub-fields\n\n' + ', '.join(v['subfields']))
    print('\n# Layout\n\ncoarse: ' + ', '.join(v['layouts']['coarse']) + '\narrangements: ' + ', '.join(v['layouts']['arrangements']))
    print('\n# What a figure holds (--want / --avoid)\n\n' + ', '.join(v['has']))
    print('\n# Sample data\n\n' + ', '.join(v['sample_data']))
    for title, classes in (('Tags: things that are drawn (idioms and parts)', ('idiom', 'part')), ('Tags: devices applied to the figure or its elements (modifiers)', ('modifier',))):
        print(f'\n# {title}; (cards carrying it, of them tier 1; +n = further tier-1 cards where only the record text names it)\n')
        for t in [t for t in v['tags'] if t['cls'] in classes][:a.n]:
            print(f"- `{t['id']}` ({t['n']}, {t['n_tier1']}" + (f"; +{t['n_text']}" if t.get('n_text') else '') + f"): {t['definition'][:a.width]}" + (f"  [see {', '.join(t['see'])}]" if t.get('see') else ''))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('search')
    for k, h in (('kind', 'kinds, first = primary'), ('subfield', 'sub-fields, first = primary'), ('layout', 'arrangement or coarse class'), ('want', 'pictures,icons,...'), ('avoid', ''),
                 ('tags', 'merged tag ids'), ('sample-data', 'image, text, video, ...'), ('objects', 'the things to be drawn, comma separated'), ('text', 'title, abstract, what the figure must show'),
                 ('variant', 'a variant slug'), ('like', 'an id: search for figures like it'), ('exclude', 'ids to leave out')):
        s.add_argument('--' + k, help=h)
    s.add_argument('--panels', type=int); s.add_argument('--tiers', default='1,2,3'); s.add_argument('--json', action='store_true')
    s.add_argument('--n1', type=int, default=12); s.add_argument('--n2', type=int, default=8); s.add_argument('--n3', type=int, default=6); s.add_argument('--nx', type=int, default=4)
    s.set_defaults(fn=cmd_search)
    s = sp.add_parser('sheet'); s.add_argument('ids', nargs='+'); s.add_argument('--out', default='exemplar_candidates.png'); s.add_argument('--cols', type=int)
    s.add_argument('--small', action='store_true', help='use the thumbnails only'); s.add_argument('--fetch', action='store_true', help='download gallery pictures that are not here'); s.set_defaults(fn=cmd_sheet)
    s = sp.add_parser('files'); s.add_argument('ids', nargs='+'); s.add_argument('--fetch', action='store_true'); s.set_defaults(fn=cmd_files)
    s = sp.add_parser('card'); s.add_argument('id'); s.set_defaults(fn=cmd_card)
    s = sp.add_parser('vocab'); s.add_argument('-n', type=int, default=200, help='tags per group'); s.add_argument('--width', type=int, default=150); s.set_defaults(fn=cmd_vocab)
    a = ap.parse_args()
    if a.cmd == 'search': a.sample_data = getattr(a, 'sample_data', None)
    a.fn(a)


if __name__ == '__main__':
    main()
