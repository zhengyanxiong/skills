#!/usr/bin/env python3
"""Build the AI-family exemplar library: figgenie-paper-diagram/assets/exemplars/ai/.

Three tiers, all searchable with scripts/find_ai_exemplars.py:
  tier 1  the 336 figures with a deep semantic record (ai-corpus/lab/extracted/corpus_semantics.jsonl): a full pack
  tier 2  the other figures a human rated good: a full pack when the extracted vector figure is the gallery picture,
          otherwise a card and a thumbnail
  tier 3  every other designed Figure 1 of the corpus that was not rated bad or discarded (unrated, or rated ok, which
          the card says): a card and a thumbnail; its files stay in the local corpus when the corpus is present

Layout:
    ai/cards.jsonl                 one retrieval card per figure (all tiers): paper title, authors, link, abstract,
                                   figure kinds, sub-field, merged tags, layout, what is in it, objects, keywords, and
                                   for tier 1 the summary and the lesson of the semantic record
    ai/figures/<id>/print.webp     the figure as printed, from the publisher PDF at 150 dpi (WebP q90), cropped to the
                                   ink (the caption line the extractor's box reached into is cut off)
    ai/figures/<id>/source.svg     the same region as a PDF-extracted SVG, for reading how the figure is built: text
                                   kept as <text> with its font names and sizes, the embedded font files dropped, the
                                   embedded bitmaps reduced to small stand-ins (160 px, soft masks 96 px on the long
                                   side) with their placement unchanged; print.webp is the reference for how it looks
    ai/figures/<id>/semantics.json the semantic record (tier 1)
    ai/figures/<id>/manifest.json  provenance, attribution, tier, the card fields that matter when reading the figure
    ai/thumbs/<id>.webp            360 px wide, for the candidate sheets of the finder (every figure)
    ai/vocab.json                  kinds with variants, sub-fields, the tag vocabulary (v2: idioms, parts, modifiers) with definitions and counts
    ai/SOURCES.md                  where the figures come from, and their copyright

    python3 figgenie-paper-diagram/scripts/distill/build_ai_exemplars.py [--tiers 1,2,3] [--limit N] [--out DIR] [--workers 6]
        [--pack-ids FILE] [--architectures ai-parts/architectures/selection.json]

`--pack-ids` names figures (one id per line) that get a full pack whatever their tier: the whole-model architecture
figures of references/ai/model-architectures.md. A `<pid>_g1` id among them (a figure whose PDF extraction did not match
the published picture) is packed from the vector of its arXiv source (ai-corpus/lab/extracted/<pid>/src/fig1_*.svg + .png).
`--architectures` (the hand-picked selection, read when the file exists) adds `architecture: <type>` to the cards and
manifests of those figures. Re-runs skip a figure whose files are there and whose source box has not changed
(`--force` rebuilds). Nothing in ai-corpus/ or topconf-paper-figure-gallery/ is written.
"""
import argparse, base64, csv, hashlib, io, json, os, re, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent; SKILL = HERE.parent.parent; REPO = SKILL.parent
AI = REPO / 'ai-corpus'; LAB = AI / 'lab'; EXT = LAB / 'extracted'; WS = AI / 'workspace'; GALLERY = REPO / 'topconf-paper-figure-gallery'
GALLERY_RAW = 'https://raw.githubusercontent.com/qwdwqfwq/topconf-paper-figure-gallery/main/'
DEFAULT_OUT = SKILL / 'assets' / 'exemplars' / 'ai'
os.environ.setdefault('FIGCORPUS_WS', str(WS)); os.environ.setdefault('FIGCORPUS_OUT', str(LAB))
sys.path.insert(0, str(REPO / 'paper-figure-corpus' / 'scripts'))
DPI, THUMB_W, MAX_SIDE, MASK_SIDE = 150, 360, 160, 96
KINDS = ['stage-pipeline', 'model-anatomy', 'side-by-side-contrast', 'worked-walkthrough', 'concept-schematic', 'scope-overview', 'actor-interaction', 'contribution-mosaic']
COARSE = {'panels-row': 'row', 'pipeline-row': 'row', 'panels-column': 'stack', 'pipeline-column': 'stack', 'bands': 'stack', 'lanes': 'stack', 'chat-column': 'stack',
          'panels-grid': 'grid', 'cards-grid': 'grid', 'dashboard': 'grid', 'hub': 'radial', 'single': 'single', 'free': 'single', 'inset': 'single', 'layered': 'stack',
          'row': 'row', 'column': 'stack', 'grid': 'grid', 'nested': 'single'}


def lst(x): return x if isinstance(x, list) else ([] if x in (None, '') else [x])
def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


STATE = {}      # id -> {key: hash of the source box, box, w_pt, h_pt}; kept in <out>/.build_state.json (not needed at run time)


def _init(state):
    global STATE; STATE = state


# ---------------------------------------------------------------- figure files
def tight_box(page, rec):
    """The extractor's box with its bottom cut at the figure's own caption, then shrunk to the ink."""
    import fitz
    from PIL import Image
    from figure_regions import find_captions
    bb = fitz.Rect(rec['bbox']) & page.rect
    for c in find_captions(page):
        r = c['rect']
        if c['num'] == str(rec['fig']) and bb.y0 + 20 < r.y0 < bb.y1 + 2 and min(bb.x1, r.x1) - max(bb.x0, r.x0) > 20: bb.y1 = min(bb.y1, r.y0 - 0.5)
    pix = page.get_pixmap(clip=bb, dpi=DPI)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    ink = im.convert('L').point(lambda v: 255 if v < 244 else 0).getbbox()
    if not ink: return bb, im
    pad = 4; x0, y0, x1, y1 = max(0, ink[0] - pad), max(0, ink[1] - pad), min(im.width, ink[2] + pad), min(im.height, ink[3] + pad)
    s = 72 / DPI
    return fitz.Rect(bb.x0 + x0 * s, bb.y0 + y0 * s, bb.x0 + x1 * s, bb.y0 + y1 * s), im.crop((x0, y0, x1, y1))


IMG_RE = re.compile(r'((?:xlink:)?href)="data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=\s]+)"')


FONT_RE = re.compile(r'@font-face\{[^}]*\}')


def slim_bitmaps(svg):
    """Drop the embedded font files (the font-family names stay) and re-encode the embedded bitmaps small: at most
    MAX_SIDE px on the long side, soft masks (greyscale) MASK_SIDE, PNG when they have few colours or alpha, else JPEG
    q60. The <image> width / height stay, so the placement in the figure does not change; the pictures themselves are
    seen in print.webp."""
    from PIL import Image
    svg = FONT_RE.sub('', svg)

    def sub(m):
        raw = base64.b64decode(re.sub(r'\s', '', m.group(3)))
        if len(raw) < 3_000: return m.group(0)
        try: im = Image.open(io.BytesIO(raw)); im.load()
        except Exception: return m.group(0)
        if im.mode not in ('RGB', 'RGBA', 'L', 'LA', 'P', '1'): im = im.convert('RGB')
        w, h = im.size; s = min(1.0, (MASK_SIDE if im.mode in ('L', '1') else MAX_SIDE) / max(w, h))
        alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
        if s < 1: im = im.convert('RGBA' if alpha else 'RGB').resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
        buf = io.BytesIO()
        if alpha or im.convert('RGB').getcolors(256) is not None: im.save(buf, 'PNG', optimize=True); mime = 'png'
        else: im.convert('RGB').save(buf, 'JPEG', quality=60, optimize=True); mime = 'jpeg'
        new = buf.getvalue()
        if len(new) >= len(raw): return m.group(0)
        return f'{m.group(1)}="data:image/{mime};base64,{base64.b64encode(new).decode()}"'
    return IMG_RE.sub(sub, svg)


def thumb_of(im, path):
    from PIL import Image
    im = im.convert('RGB'); r = THUMB_W / im.width
    if r < 1: im = im.resize((THUMB_W, max(1, round(im.height * r))), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True); im.save(path, 'WEBP', quality=75, method=6)


def build_files(job):
    """job: (id, pid, fig, pdf, mode, out_dir, force) with mode 'pack' (print + svg + thumb), 'thumb-pdf' or 'thumb-gallery:<path>'."""
    eid, pid, fig, pdf, mode, out, force = job
    out = Path(out); figdir = out / 'figures' / eid; th = out / 'thumbs' / f'{eid}.webp'
    try:
        if mode.startswith('thumb-gallery:'):
            if th.exists() and not force: return eid, 'kept', None
            from PIL import Image
            thumb_of(Image.open(mode.split(':', 1)[1]), th); return eid, 'gallery', None
        if mode.startswith('pack-svg:'):
            # the vector of the arXiv source: print.webp from its PNG render, source.svg slimmed, the size from the viewBox
            from PIL import Image
            svg_p = Path(mode.split(':', 1)[1]); png_p = svg_p.with_suffix('.png')
            if not force and (figdir / 'print.webp').exists() and th.exists() and STATE.get(eid): return eid, 'kept', STATE[eid]
            figdir.mkdir(parents=True, exist_ok=True)
            im = Image.open(png_p).convert('RGB'); im.save(figdir / 'print.webp', 'WEBP', quality=90, method=6); thumb_of(im, th)
            svg = svg_p.read_text(encoding='utf-8'); (figdir / 'source.svg').write_text(slim_bitmaps(svg), encoding='utf-8')
            vb = re.search(r'viewBox="([^"]+)"', svg); w_pt = h_pt = None
            if vb:
                nums = [float(v) for v in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', vb.group(1))]
                if len(nums) == 4: w_pt, h_pt = round(nums[2], 1), round(nums[3], 1)
            return eid, 'pack-svg', dict(key='src:' + hashlib.md5(svg.encode()).hexdigest()[:10], box=None, w_pt=w_pt or im.width * 0.75, h_pt=h_pt or im.height * 0.75, source='arxiv-source')
        import fitz
        rec = next(f for f in json.loads((EXT / pid / 'figures.json').read_text())['figures'] if str(f.get('fig')) == str(fig) and f.get('file'))
        key = hashlib.md5(json.dumps(rec.get('bbox')).encode()).hexdigest()[:10]
        if not force and STATE.get(eid, {}).get('key') == key and (th.exists() and (mode != 'pack' or (figdir / 'print.webp').exists())): return eid, 'kept', STATE[eid]
        doc = fitz.open(pdf); page = doc[rec['page'] - 1]
        box, im = tight_box(page, rec)
        info = dict(key=key, box=[round(v, 1) for v in box], w_pt=round(box.width, 1), h_pt=round(box.height, 1))
        if mode == 'pack':
            from batch_extract import slim_svg
            from fix_svg_fonts import fix_svg
            figdir.mkdir(parents=True, exist_ok=True)
            im.save(figdir / 'print.webp', 'WEBP', quality=90, method=6)
            svg, _ = slim_svg(doc, rec['page'] - 1, box); svg, _ = fix_svg(doc, page, svg)
            (figdir / 'source.svg').write_text(slim_bitmaps(svg), encoding='utf-8')
        thumb_of(im, th); doc.close()
        return eid, mode, info
    except Exception as e:
        return eid, 'error', f'{type(e).__name__}: {e}'


# ---------------------------------------------------------------- cards
def coarse(arr): return COARSE.get(arr or '', 'other')


RUN = re.compile(r'\b([A-Z] [a-z0-9]+(?: [A-Z] [a-z0-9]+)*)(?: ([A-Z]{1,6})\b(?! [a-z]))?')


def clean_title(t, venue):
    """ACL titles come from the Anthology with their brace-protected capitals split off ('M ega A gent', 'LLM s',
    'KG -Agent'); join them back (MegaAgent, LLMs, KG-Agent). A few rare names stay imperfect."""
    if venue != 'ACL' or not t: return t
    t = re.sub(r'(?<=\w) - ?(?=[A-Z])', '-', t); t = re.sub(r'(?<=\w) -(?=\w)', '-', t); t = re.sub(r'(?<=\w)- (?=\w)', '-', t)
    t = re.sub(r'\b([A-Z]{2,}) s\b', r'\1s', t)
    t = RUN.sub(lambda m: m.group(1).replace(' ', '') + (m.group(2) or ''), t)
    return re.sub(r'\s+', ' ', re.sub(r' ([:;,!?])', r'\1', t)).strip()


def card_tier1(r, row, rec):
    c, lay, st, ret, les = rec['content'], rec['layout'], rec['style'], rec.get('retrieval') or {}, rec.get('lessons') or {}
    kinds = [k for k in lst(c.get('kinds')) if k in KINDS] or ['other']
    pics, icons = lst(c.get('pictures')), lst(c.get('icons'))
    return dict(kinds=kinds, variant=c.get('variant') or '', subfield=(rec.get('system') or {}).get('subfield') or row.get('domain') or 'other',
                subfield2=(rec.get('system') or {}).get('subfield2') or row.get('domain2') or '',
                tags=sorted(set(lst(ret.get('tags'))) | set(lst(row.get('tags')))),
                layout=dict(arrangement=lay.get('arrangement'), coarse=coarse(lay.get('arrangement')), panels=lay.get('panel_count'), direction=lay.get('direction'),
                            width=lay.get('width'), ground=st.get('ground'), legend=lay.get('legend'), note=lay.get('arrangement_note')),
                has=dict(pictures=bool(pics), icons=bool(icons), bubbles=any(i.get('concept') == 'chat-bubbles' for i in lst(c.get('idioms'))) or 'chat-column' == lay.get('arrangement'),
                         charts=any(p.get('content') in ('chart', 'schematic-plot') for p in pics) or any(e.get('type') == 'chart' for e in lst(c.get('elements'))),
                         formulas=any(e.get('type') == 'formula' for e in lst(c.get('elements'))), examples=bool(lst(c.get('examples')))),
                sample_data=ret.get('sample_data') or row.get('sample_data') or '', objects=lst(ret.get('objects')), keywords=lst(ret.get('keywords')),
                idioms=sorted({i.get('concept') for i in lst(c.get('idioms')) if i.get('concept')}),
                devices=[f"{t.get('name')}: {t.get('what')}" for t in lst(ret.get('new_tags')) if isinstance(t, dict) and t.get('name')]
                        + [f"{i.get('concept')}: {i.get('drawn_as')}" for i in lst(c.get('idioms')) if i.get('concept') and i.get('convention') == 'own'],
                picture_kinds=sorted({p.get('content') for p in pics if p.get('content')}), icon_styles=sorted({i.get('style') for i in icons if i.get('style')}),
                what=c.get('subject') or '', argues=c.get('argues') or '', summary=rec.get('summary') or '', summary_zh=rec.get('summary_zh') or '',
                lesson=les.get('what_to_learn') or '', suits=les.get('suits') or '', confidence=rec.get('confidence'))


def card_pre(r):
    p = r.get('pre') or {}
    pics = str(p.get('pictures') or '0'); icons = p.get('icons') or 'none'
    return dict(kinds=r['kinds'] or ['other'], variant=r.get('variant') or '', subfield=r.get('domain') or 'other', subfield2=r.get('domain2') or '', tags=sorted(set(lst(r.get('tags')))),
                layout=dict(arrangement=p.get('arrangement'), coarse='radial' if p.get('base') in ('loop', 'map-or-radial') else coarse(p.get('arrangement')), panels=p.get('panels'),
                            direction=p.get('reading_direction'), width=(r.get('style') or {}).get('size', {}).get('column', ''), ground=p.get('ground'), legend=p.get('legend'), base=p.get('base')),
                has=dict(pictures=pics not in ('0', ''), icons=icons != 'none', bubbles=bool(p.get('bubbles')), charts=p.get('figure_class') == 'diagram-plus-results' or p.get('picture_role') == 'result-render',
                         formulas=bool(p.get('formulas')), examples=(r.get('sample_data') or 'none') != 'none'),
                sample_data=r.get('sample_data') or '', objects=lst(r.get('objects')), keywords=lst(r.get('keywords')), idioms=[], picture_kinds=[], icon_styles=[],
                what=p.get('grammar') or '', argues=p.get('argues') or '', summary='', summary_zh='', lesson='', suits='', confidence='')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tiers', default='1,2,3'); ap.add_argument('--limit', type=int); ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--workers', type=int, default=6); ap.add_argument('--force', action='store_true'); ap.add_argument('--cards-only', action='store_true')
    ap.add_argument('--pack-ids', default=None, help='file of exemplar ids that get a full pack whatever their tier (one per line)')
    ap.add_argument('--architectures', default=str(REPO / 'ai-parts' / 'architectures' / 'selection.json'), help='hand-picked whole-model figures: adds architecture: <type> to their cards')
    a = ap.parse_args(); out = Path(a.out); want = {int(t) for t in a.tiers.split(',')}
    pack_ids = {l.strip() for l in open(a.pack_ids, encoding='utf-8') if l.strip()} if a.pack_ids else set()
    arch = {}
    if a.architectures and Path(a.architectures).exists():
        for t in json.load(open(a.architectures, encoding='utf-8'))['types']:
            for f in t['figures']: arch[f] = t['type']
    pack_ids |= set(arch)                                     # the architecture figures always get a pack
    tab = jl(LAB / 'fig1_table.jsonl')
    recs = {(r['paper_id'], str(r['fig'])): r for r in jl(EXT / 'corpus_semantics.jsonl') if r.get('kind') == 'ai'}
    pool = {pid for pid, _ in recs}
    man = {r['paper_id']: r for r in csv.DictReader(open(WS / 'manifest.csv', encoding='utf-8'))}
    gal = {g['image']: g for g in json.load(open(GALLERY / 'data' / 'figures.json', encoding='utf-8'))}
    abst = {a_['paper_id']: a_['abstract'] for a_ in jl(WS / 'abstracts.jsonl')}
    rows, jobs = [], []
    for r in tab:
        if not r['designed'] or r['rating'] in ('bad', 'discard'): continue
        pid = r['paper_id']; tier = 1 if pid in pool else 2 if r['rating'] == 'good' else 3
        if tier not in want: continue
        vec = r['fig1_status'] in ('match', 'match-other-fig') and bool(r.get('measure'))
        fig = str(r['our_fig'] or '1') if vec else '1'
        eid = f'{pid}_fig{fig}' if vec else f'{pid}_g1'
        if tier == 1:
            rec = recs.get((pid, fig)) or next(v for (p_, _), v in recs.items() if p_ == pid)
            eid = f"{pid}_fig{rec['fig']}"; fig = str(rec['fig'])
        rows.append((tier, eid, fig, vec, r))
    if a.limit:
        keep = []
        for t in sorted(want): keep += [x for x in rows if x[0] == t][:a.limit]
        rows = keep
    pdf = lambda pid: str(WS / man[pid]['pdf_path']) if man.get(pid, {}).get('pdf_path') else None
    for tier, eid, fig, vec, r in rows:
        src_svg = next(iter(sorted((EXT / r['paper_id'] / 'src').glob('fig1_*.svg'))), None) if eid.endswith('_g1') and eid in pack_ids else None
        if src_svg and src_svg.with_suffix('.png').exists(): jobs.append((eid, r['paper_id'], fig, None, f'pack-svg:{src_svg}', str(out), a.force))
        elif vec and pdf(r['paper_id']): jobs.append((eid, r['paper_id'], fig, pdf(r['paper_id']), 'pack' if (tier in (1, 2) or eid in pack_ids) else 'thumb-pdf', str(out), a.force))
        else: jobs.append((eid, r['paper_id'], fig, None, 'thumb-gallery:' + str(GALLERY / man[r['paper_id']]['topconf_image']), str(out), a.force))
    missing = sorted(pack_ids - {eid for _, eid, _, _, _ in rows})
    if missing: print('warn: pack ids not among the designed figures:', ', '.join(missing))
    sp = out / '.build_state.json'; state = json.loads(sp.read_text()) if sp.exists() else {}
    info, errors, t0 = {k: v for k, v in state.items()}, [], time.time()
    if not a.cards_only:
        with ProcessPoolExecutor(a.workers, initializer=_init, initargs=(state,)) as ex:
            for k, (eid, how, inf) in enumerate(ex.map(build_files, jobs, chunksize=4), 1):
                if how == 'error': errors.append((eid, inf))
                elif inf: info[eid] = inf
                if k % 500 == 0: print(f'  {k}/{len(jobs)} figures, {time.time() - t0:.0f}s', flush=True)
        out.mkdir(parents=True, exist_ok=True); sp.write_text(json.dumps(info))
    # ---- cards and manifests
    v2 = AI / 'typedisc' / 'tagmerge' / 'v2'                      # merged vocabulary: tags_merge v2 (ai-corpus/scripts/tagmerge_v2.py)
    vocab_tags = {t['id']: t for t in json.load(open(v2 / 'vocab_v2.json', encoding='utf-8'))['entries'] if t['cls'] in ('idiom', 'part', 'modifier')}
    ftags = {o['id']: o for o in jl(v2 / 'figure_tags_v2.jsonl')}
    cards = []
    for (tier, eid, fig, vec, r), job in zip(rows, jobs):
        pid = r['paper_id']; m = man.get(pid, {}); g = gal.get(m.get('topconf_image'), {})
        body = card_tier1(r, r, recs.get((pid, fig))) if tier == 1 else card_pre(r)
        ft = ftags.get(pid) or {}
        body['tags'] = [t for t in ft.get('tags', []) if t in vocab_tags]                 # explicit: record tags, mapped coined names, idioms, fields, pre-screen tags
        body['tags_text'] = [t for t in ft.get('text', []) if t in vocab_tags] if tier == 1 else []   # new entries found only in the record's drawing descriptions
        if tier == 1: body['idioms'] = [t for t in ft.get('idioms', []) if vocab_tags.get(t, {}).get('cls') in ('idiom', 'part')]
        figdir = out / 'figures' / eid; pack = (figdir / 'print.webp').exists()
        files = {'thumb': f'thumbs/{eid}.webp'}
        if pack: files.update({'print': f'figures/{eid}/print.webp', 'svg': f'figures/{eid}/source.svg'})
        if tier == 1: files['semantics'] = f'figures/{eid}/semantics.json'
        if vec and not pack: files.update({'corpus_svg': str(Path('ai-corpus/lab') / r['measure']), 'corpus_png': str(Path('ai-corpus/lab') / r['measure']).replace('.svg', '.png')})
        files.update({'gallery': str(Path('topconf-paper-figure-gallery') / m.get('topconf_image', '')), 'gallery_url': GALLERY_RAW + m.get('topconf_image', '')})
        size = (r.get('style') or {}).get('size') or {}
        card = dict(id=eid, paper_id=pid, fig=fig, tier=tier, rating=r['rating'], venue=r['venue'], year=int(r['year']), award=r.get('tier') or '',
                    title=clean_title(m.get('title') or r.get('title', ''), r['venue']), authors=lst(g.get('authors'))[:6], paper_url=g.get('paper') or m.get('page_url') or '',
                    abstract=(abst.get(pid) or '')[:1400], **body, mosaic=r.get('mosaic_variant') if r.get('mosaic') else '',
                    size=dict(w=size.get('w'), h=size.get('h'), aspect=size.get('aspect')) if size and vec else {}, vector=vec, files=files)
        if eid in info: card['size'] = dict(w=info[eid]['w_pt'], h=info[eid]['h_pt'], aspect=round(info[eid]['w_pt'] / max(1, info[eid]['h_pt']), 2))
        if eid in arch: card['architecture'] = arch[eid]          # a whole-model architecture figure (references/ai/model-architectures.md)
        if (info.get(eid) or {}).get('source') == 'arxiv-source': card['vector_from'] = 'arxiv-source'
        cards.append(card)
        if pack:
            if tier == 1: (figdir / 'semantics.json').write_text(json.dumps(recs[(pid, fig)], ensure_ascii=False, indent=1), encoding='utf-8')
            mf = {k: card[k] for k in ('id', 'paper_id', 'fig', 'tier', 'rating', 'venue', 'year', 'award', 'title', 'authors', 'paper_url', 'kinds', 'variant', 'subfield', 'subfield2', 'tags', 'layout', 'has', 'size')}
            if eid in arch: mf['architecture'] = arch[eid]
            mf.update(lesson=card['lesson'], files={k: v.replace(f'figures/{eid}/', '') for k, v in files.items() if k in ('print', 'svg', 'semantics')},
                      copyright='The figure belongs to its authors and publisher; kept here as a reference for study, with the link to the paper.',
                      provenance=dict(pdf=m.get('pdf_url') or '', box_pt=info.get(eid, {}).get('box'), print_dpi=DPI, bitmaps_max_side_px=MAX_SIDE,
                                      vector_from=(info.get(eid) or {}).get('source') or 'pdf'))
            (figdir / 'manifest.json').write_text(json.dumps(mf, ensure_ascii=False, indent=1), encoding='utf-8')
    out.mkdir(parents=True, exist_ok=True)
    order = {1: 0, 2: 1, 3: 2}
    with open(out / 'cards.jsonl', 'w', encoding='utf-8') as fh:
        for c in sorted(cards, key=lambda c: (order[c['tier']], c['id'])): fh.write(json.dumps(c, ensure_ascii=False) + '\n')
    kinds_v2 = json.load(open(AI / 'typedisc' / 'kinds_v2.json', encoding='utf-8'))['kinds']
    from collections import Counter
    tagc = Counter(t for c in cards for t in c['tags']); tagc1 = Counter(t for c in cards if c['tier'] == 1 for t in c['tags'])
    tagx = Counter(t for c in cards for t in c.get('tags_text') or [])
    vocab = dict(kinds=[dict(id=k['id'], definition=k['definition'], variants=[dict(id=v['id'], definition=v['definition']) for v in k['variants']]) for k in kinds_v2],
                 subfields=['llm-nlp', 'multimodal', 'vision', 'generative', 'agents', 'rl-robotics', 'audio', 'science-engineering', 'ml-core', 'other'],
                 layouts=dict(coarse=['row', 'stack', 'grid', 'radial', 'single'], arrangements=sorted({c['layout'].get('arrangement') for c in cards if c['layout'].get('arrangement')})),
                 has=['pictures', 'icons', 'bubbles', 'charts', 'formulas', 'examples'],
                 sample_data=sorted({c['sample_data'] for c in cards if c['sample_data']}),
                 tags=[dict(id=t, n=tagc[t], n_tier1=tagc1[t], n_text=tagx[t], cls=e['cls'], definition=e['definition'], see=e.get('see') or [])
                       for t, e in sorted(vocab_tags.items(), key=lambda kv: (-tagc1[kv[0]] - tagx[kv[0]], -tagc[kv[0]], kv[0]))])
    (out / 'vocab.json').write_text(json.dumps(vocab, ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'SOURCES.md').write_text(
        '# Sources of the AI-family exemplars\n\n'
        'Every figure here is the Figure 1 (or teaser) of a paper published at ICLR, ICML, NeurIPS, CVPR, ACL or AAAI, 2023-2026, '
        'taken from the paper list of the Top-Conf Figure Gallery by qwdwqfwq (https://github.com/qwdwqfwq/topconf-paper-figure-gallery, '
        "MIT-licensed index). The full figures were re-extracted from the publisher's PDF or the arXiv source; thumbnails of papers whose "
        "figure was not re-extracted were made from the gallery's own images. The figures belong to their authors and publishers (most proceedings are CC BY 4.0; AAAI keeps its own copyright); "
        'they are kept as references for study and are not to be reused as material. Each card in cards.jsonl and each manifest.json gives '
        'the paper title, the first authors and the link to the paper. Write to the maintainer of this skill to have a figure removed.\n', encoding='utf-8')
    tc = Counter(c['tier'] for c in cards); pk = sum(1 for c in cards if 'print' in c['files'])
    print(f'{len(cards)} cards (tier 1 {tc[1]}, tier 2 {tc[2]}, tier 3 {tc[3]}); packs {pk}; errors {len(errors)}; {time.time() - t0:.0f}s -> {out}')
    for e in errors[:10]: print('  error', *e)


if __name__ == '__main__':
    main()
