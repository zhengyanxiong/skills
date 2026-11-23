#!/usr/bin/env python3
"""D. Palettes of the AI-family figures: how many hues, which ones together, how strong, and on what.

    python3 figgenie-paper-diagram/scripts/distill/ai_palettes.py        # -> ai-corpus/lab/distill/palettes/

  palettes.md            the tables below
  figures_palette.csv    one row per figure: its fills, lines and text colours by role, hue families, tone class, scheme
  entries.csv            one row per palette entry: hex, role, hue family, lightness, saturation, the record's description
  swatches.csv           per hue family and tone: the median colour and the most used exact values

Where the numbers come from
  * `style.palette` of the semantic record: up to about 16 entries per figure, each an exact hex read from the SVG and a
    sentence saying what the colour is used for. The hex values are measured; the ROLE of an entry (fill, line, text,
    region tint) is MINED from that sentence with keyword rules, and a few entries serve two roles (a dark blue used for
    both outlines and headings counts once, under the first role the sentence names).
  * the hue count of the pre-screen (all 3,274 designed figures) and the named palette found by measurement (Office,
    tab10) are printed beside the pool as the corpus-level check.
A scheme here is a description of how many hue families the fills use, not a recipe: 9 figures in 10 give each part its
own colour (see the encoding tables), so what recurs is the TONE (pale fills, dark lines) far more than any fixed set.
"""
import json, os, re
from ai_common import *
from ai_grounds import region_tints
sys.path.insert(0, os.path.join(REPO, 'paper-figure-corpus', 'scripts'))

OUT = os.path.join(DISTILL, 'palettes')
TEXT = re.compile(r'\b(text|texts|labels?|headings?|titles?|words?|captions?|font|lettering|type|names?|numbers?|digits?|keywords?|spans?|sentences?|formulas?|symbols?|letters?|annotations?)\b', re.I)
LINEW = re.compile(r'\b(outline[sd]?|strokes?|borders?|arrows?|arrowheads?|lines?|edges?|dashed|dotted|rules?|brackets?|braces?|curves?|frames?|contours?|wedges?|leaders?|connectors?|links?|axes|axis|grid lines?|ticks?)\b', re.I)
FILLW = re.compile(r'\b(fills?|filled|box|boxes|cards?|cells?|bars?|blocks?|tiles?|nodes?|circles?|chips?|pills?|bubbles?|tokens?|squares?|bands?|strips?|regions?|panels?|background|ground|tints?|shad(e|ed|ing)|swatch|slabs?|cubes?|trapezoids?|cylinders?|stacks?|areas?|zones?|lanes?|dots?|polygons?|capsules?|tags?|badges?|highlights?|wash)\b', re.I)
HUES = ['blue', 'orange', 'green', 'red', 'yellow', 'purple', 'teal', 'pink']
OFFICE = {'#4472c4', '#ed7d31', '#a5a5a5', '#ffc000', '#5b9bd5', '#70ad47', '#44546a', '#e7e6e6', '#deebf7', '#fbe5d6', '#ededed', '#fff2cc', '#ddebf7', '#e2f0d9', '#dae3f3', '#c00000', '#ff0000', '#00b050', '#0070c0', '#7030a0',
          '#f2f2f2', '#d9d9d9', '#bfbfbf', '#7f7f7f', '#595959', '#9dc3e6', '#f4b183', '#a9d18e', '#ffd966', '#8faadc', '#c5e0b4', '#bdd7ee', '#f8cbad', '#ffe699', '#b4c7e7', '#2f5597', '#c55a11', '#548235', '#bf9000', '#1f4e79',
          '#0e2841', '#156082', '#e97132', '#196b24', '#0f9ed5', '#a02b93', '#4ea72e', '#dceaf7', '#fbe3d6', '#d9f2d0', '#caeefb', '#f2cfee', '#c1e5f5', '#f6c6ad', '#b4e5a2', '#83cbeb', '#e59edd', '#8ed973'}      # Office 2013 and 2023 themes with their tints
DRAWIO = {'#dae8fc', '#6c8ebf', '#d5e8d4', '#82b366', '#ffe6cc', '#d79b00', '#fff2cc', '#d6b656', '#f8cecc', '#b85450', '#e1d5e7', '#9673a6', '#f5f5f5', '#666666', '#60a917', '#1ba1e2', '#b1ddf0', '#10739e', '#fad7ac', '#b46504',
          '#fad9d5', '#ae4132', '#b0e3e6', '#0e8088', '#d0cee2', '#56517e', '#bac8d3', '#23445d', '#ffff88', '#36393d', '#cdeb8b', '#ffcc99', '#cce5ff', '#eeeeee'}


def area_of(path):
    """Painted area by tone, as shares of the canvas, from the SVG itself (svg_digest: overlapping shapes add up; a translucent
    fill counts by its opacity; pictures are reported separately and their colours are not in here)."""
    import svg_digest
    d = svg_digest.digest(path)
    if not d: return None
    cls, hue_area = C(), C()
    for hx, op, a in d['fills']:
        hx = str(hx).lower()
        if not HEX_RE.match(hx) or (op is not None and op < 0.1): continue
        h, l, s = hls(hx); a = a * min(1.0, op or 1.0)
        if hue_family(hx) == 'grey': cls['white' if l >= 0.97 else 'light-grey' if l >= 0.80 else 'mid-grey' if l >= 0.35 else 'dark'] += a
        else: cls['pale' if l >= 0.80 else 'mid' if l >= 0.55 else 'strong'] += a; hue_area[hue_family(hx)] += a
    return dict(pic=d.get('picture_area') or 0.0, hues={k: round(v, 4) for k, v in hue_area.items()}, **{k: round(v, 4) for k, v in cls.items()})


def area_table():
    """paper_id -> area record for every designed figure whose extracted Figure 1 is the gallery picture (cached)."""
    cache_p = os.path.join(OUT, 'area_cache.json'); cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    rows = [json.loads(l) for l in open(os.path.join(LAB, 'fig1_table.jsonl'), encoding='utf-8')]
    rows = [r for r in rows if r.get('measure') and r['designed'] and r['fig1_status'] in ('match', 'match-other-fig')]
    new = 0
    for r in rows:
        key = r['paper_id'] + '|' + str((r.get('style') or {}).get('size'))          # a re-cropped figure gets measured again
        if cache.get(r['paper_id'], {}).get('key') != key:
            a = area_of(os.path.join(LAB, r['measure'])); cache[r['paper_id']] = dict(key=key, area=a); new += 1
    if new: os.makedirs(OUT, exist_ok=True); json.dump(cache, open(cache_p, 'w'))
    out = {}
    for r in rows:
        a = cache[r['paper_id']]['area']
        if not a: continue
        chroma = a.get('pale', 0) + a.get('mid', 0) + a.get('strong', 0)
        a = dict(a, chroma=chroma, rating=r['rating'], n_hues=sum(1 for v in a['hues'].values() if v >= 0.01), lead=max(a['hues'], key=a['hues'].get) if a['hues'] and chroma >= 0.02 else '',
                 tone=('no colour field' if chroma < 0.02 else 'pale' if a.get('pale', 0) / chroma >= 0.6 else 'strong' if (a.get('mid', 0) + a.get('strong', 0)) / chroma >= 0.6 else 'mixed'))
        out[r['paper_id']] = a
    return out


def role_of(use):
    """fill | line | text | other, by the first role word in the sentence (a sentence that names both a box and its outline starts with what the colour is)."""
    cand = [(m.start(), r) for r, rx in (('text', TEXT), ('line', LINEW), ('fill', FILLW)) for m in [rx.search(use)] if m]
    return min(cand)[1] if cand else 'other'


def tone(l, s):
    if s < 0.08: return 'grey'
    return 'pale' if l >= 0.80 else 'mid' if l >= 0.55 else 'strong'


def entries_of(d):
    out = []; reg = {t['hex'] for t in region_tints(d)}
    for e in lst(d['rec']['style'].get('palette')):
        hx = str(e.get('hex') or '').lower()
        if not HEX_RE.match(hx): continue
        use = e.get('used_for') or ''; h, l, s = hls(hx); hue = hue_family(hx); r = role_of(use)
        if hx in reg and r in ('fill', 'other'): r = 'region'
        if hx == '#ffffff' and r in ('fill', 'other', 'region'): r = 'white'
        out.append(dict(hex=hx, role=r, hue=hue, l=round(l, 3), s=round(s, 3), tone=tone(l, s) if hue != 'grey' else ('dark-neutral' if l < 0.35 else 'grey'), use=use, opacity=e.get('opacity'), approx=bool(e.get('approx'))))
    return out


def main():
    data = load(); n = len(data); L = ['# D. Palettes: how many hues, which ones together, how strong, and on what', '', POOL_NOTE, '']
    for d in data:
        E = d['ent'] = entries_of(d)
        d['fills'] = [e for e in E if e['role'] in ('fill', 'region', 'other') and e['hue'] != 'grey']        # chromatic fills
        d['hues'] = sorted({e['hue'] for e in d['fills']}); d['nh'] = len(d['hues'])
        tones = C(e['tone'] for e in d['fills']); k = sum(tones.values())
        d['tone'] = ('no chromatic fill' if not k else 'pale' if tones['pale'] / k >= 0.6 else 'strong' if (tones['strong'] + tones['mid']) / k >= 0.6 and tones['strong'] >= tones['pale'] else 'mixed')
        d['lines'] = [e for e in E if e['role'] == 'line']; d['texts'] = [e for e in E if e['role'] == 'text']
        d['line_col'] = 'coloured' if any(e['hue'] != 'grey' for e in d['lines']) else 'neutral only' if d['lines'] else 'not described'
        d['text_col'] = 'coloured' if any(e['hue'] != 'grey' for e in d['texts']) else 'neutral only' if d['texts'] else 'not described'
        d['scheme'] = ('neutral' if d['nh'] == 0 else 'one hue' if d['nh'] == 1 else 'two hues' if d['nh'] == 2 else 'three hues' if d['nh'] == 3 else 'four or five hues' if d['nh'] <= 5 else 'six or more hues')
        hx = {e['hex'] for e in E}; d['theme'] = {'office' if len(hx & OFFICE) >= 3 else None, 'drawio' if len(hx & DRAWIO) >= 3 else None} - {None}
    ents = [(d, e) for d in data for e in d['ent']]
    # ---- 0. painted area, measured
    AR = area_table(); pool_ids = {d['rec']['paper_id'] for d in data}
    groups = [('corpus', list(AR.values())), ('rated good', [a for a in AR.values() if a['rating'] == 'good']), ('rated ok or bad', [a for a in AR.values() if a['rating'] in ('ok', 'bad')]),
              ('exemplar pool', [AR[p] for p in pool_ids if p in AR])]
    L += ['## 0. Painted area (measured on the SVG of every designed figure whose extracted Figure 1 is the gallery picture)', '',
          'Shares of the canvas covered by flat fills, by tone: `pale` (HLS lightness >= 0.80), `mid` (0.55 to 0.80), `strong` (below 0.55); greys and pictures apart. Overlapping shapes add up, '
          'so read the columns as amounts of ink rather than as parts of a whole. Colours inside pasted bitmaps are not in these numbers.', '']
    def q(g, k): v = quant([a.get(k, 0) for a in g], (0.25, 0.5, 0.75)); return ' / '.join(f'{100 * x:.0f}%' for x in v)
    L += md_table(['', 'n', 'chromatic fills p25 / median / p75', 'pale', 'mid', 'strong', 'light grey', 'pictures'],
                  [[nm, len(g), q(g, 'chroma'), q(g, 'pale'), q(g, 'mid'), q(g, 'strong'), q(g, 'light-grey'), q(g, 'pic')] for nm, g in groups])
    tones = ['pale', 'mixed', 'strong', 'no colour field']
    L += ['Tone of the colour fields by area (`pale`: at least 60% of the chromatic area is pale; `strong`: at least 60% is mid or strong; `no colour field`: chromatic fills cover under 2% of the canvas):', '']
    L += md_table(['', 'n'] + tones, [[nm, len(g)] + [pct(sum(1 for a in g if a['tone'] == t), len(g)) for t in tones] for nm, g in groups])
    L += ['Hue families that each cover at least 1% of the canvas:', '']
    L += md_table(['', 'n', '0', '1', '2', '3', '4', '5+'], [[nm, len(g)] + [pct(sum(1 for a in g if (a['n_hues'] if a['n_hues'] < 5 else 5) == k), len(g)) for k in range(6)] for nm, g in groups])
    L += ['The hue family with the largest area (figures with a colour field):', '']
    L += md_table(['', 'n'] + HUES, [[nm, sum(1 for a in g if a['lead'])] + [pct(sum(1 for a in g if a['lead'] == h), sum(1 for a in g if a['lead'])) for h in HUES] for nm, g in groups])
    for d in data: d['area'] = AR.get(d['rec']['paper_id'])
    L += share_table([d for d in data if d['area']], tones, lambda d: {d['area']['tone']}, title='Tone by area, exemplar pool by kind and sub-field')
    # ---- 1. size of the palette
    ch = corpus_share('hues')
    L += ['## 1. How many colours', '',
          f'Palette entries per record: p10 {quant([len(d["ent"]) for d in data], (0.1,))[0]}, median {quant([len(d["ent"]) for d in data], (0.5,))[0]}, p90 {quant([len(d["ent"]) for d in data], (0.9,))[0]} '
          '(the measured count of distinct colours in the SVG is higher: median 9, p90 22, because of anti-aliased and near-duplicate values).', '',
          'Hue families among the chromatic fills of a figure (blue, orange, green, red, yellow, purple, teal, pink). The pre-screen counted hues by eye on all designed figures of the corpus: '
          + ', '.join(f'{k}: {100 * v[0]:.0f}%' for k, v in sorted(ch.items())) + '. That count is of colours seen, tints and the colours of icons included; the table below counts hue '
          'families (eight bins) among the flat fills the record lists, so it runs lower. Section 0 gives the count by area.', '']
    schemes = ['neutral', 'one hue', 'two hues', 'three hues', 'four or five hues', 'six or more hues']
    L += share_table(data, schemes, lambda d: {d['scheme']})
    # ---- 2. which hues
    L += ['## 2. Which hues', ''] + share_table(data, HUES, lambda d: set(d['hues']), note='Share of figures that use the hue family for a fill at all.')
    pairs = C(); trip = C()
    for d in data:
        hs = d['hues']
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)): pairs[(hs[i], hs[j])] += 1
    two = C(' + '.join(d['hues']) for d in data if d['nh'] == 2); three = C(' + '.join(d['hues']) for d in data if d['nh'] == 3)
    L += ['- hue pairs that occur together most often (any figure): ' + ', '.join(f'{a} + {b} {pct(v, n)}' for (a, b), v in pairs.most_common(10)),
          f'- the two-hue figures ({sum(two.values())}): ' + ', '.join(f'{k} {v}' for k, v in two.most_common(8)),
          f'- the three-hue figures ({sum(three.values())}): ' + ', '.join(f'{k} {v}' for k, v in three.most_common(8)), '']
    # ---- 3. tone
    L += ['## 3. How strong the listed colours are (by count of palette entries, not by area: section 0 is the measure of how a figure looks)', '',
          '`pale`: at least 60% of the chromatic fills are pale (HLS lightness >= 0.80); `strong`: at least 60% are mid or strong and the strong ones outnumber the pale; `mixed`: the rest.', '']
    L += share_table(data, ['pale', 'mixed', 'strong', 'no chromatic fill'], lambda d: {d['tone']})
    ft = C(e['tone'] for d in data for e in d['fills'])
    L += ['Tone of a chromatic fill (share of all such entries): ' + ', '.join(f'{k} {pct(v, sum(ft.values()))}' for k, v in ft.most_common()) + '.', '']
    rows = []
    for hue in HUES:
        for tn in ('pale', 'mid', 'strong'):
            g = [e for d in data for e in d['fills'] if e['hue'] == hue and e['tone'] == tn]
            if len(g) < 8: continue
            l = quant([e['l'] for e in g], (0.5,))[0]; s = quant([e['s'] for e in g], (0.5,))[0]
            rows.append([hue, tn, len(g), f'{l:.2f}', f'{s:.2f}', ', '.join(f'`{k}` {v}' for k, v in C(e['hex'] for e in g).most_common(6))])
    L += ['### Swatches: the values actually used, per hue family and tone', ''] + md_table(['hue', 'tone', 'entries', 'median lightness', 'median saturation', 'most used exact values'], rows)
    write_csv(os.path.join(OUT, 'swatches.csv'), ['hue', 'tone', 'entries', 'median_lightness', 'median_saturation', 'top_values'], rows)
    # ---- 4. lines and text
    L += ['## 4. Lines and text', '']
    L += share_table(data, ['neutral only', 'coloured', 'not described'], lambda d: {d['line_col']}, title='Outlines and arrows', note='`coloured`: at least one outline or arrow colour is not a grey or black.')
    L += share_table(data, ['neutral only', 'coloured', 'not described'], lambda d: {d['text_col']}, title='Text', note='`coloured`: at least one text colour is not a grey or black (coloured headings, highlighted words, labels in the colour of their part).')
    ln = [e for d in data for e in d['lines']]; tx = [e for d in data for e in d['texts']]
    L += ['- most used line colours: ' + ', '.join(f'`{k}` {v}' for k, v in C(e['hex'] for e in ln).most_common(14)),
          '- hue of a coloured line (share of coloured line entries): ' + ', '.join(f'{k} {pct(v, sum(1 for e in ln if e["hue"] != "grey"))}' for k, v in C(e['hue'] for e in ln if e['hue'] != 'grey').most_common()),
          '- most used text colours: ' + ', '.join(f'`{k}` {v}' for k, v in C(e['hex'] for e in tx).most_common(12)),
          '- hue of a coloured text (share of coloured text entries): ' + ', '.join(f'{k} {pct(v, sum(1 for e in tx if e["hue"] != "grey"))}' for k, v in C(e['hue'] for e in tx if e['hue'] != 'grey').most_common()), '']
    dark = [e for e in ln + tx if e['hue'] == 'grey' and e['l'] < 0.35]
    L += ['- the dark neutral of lines and text: ' + ', '.join(f'`{k}` {v}' for k, v in C(e['hex'] for e in dark).most_common(8)) + f'; pure black in {pct(sum(1 for d in data if any(e["hex"] == "#000000" for e in d["lines"] + d["texts"])), n)} of the figures', '']
    # ---- 5. where the values come from
    named = C((d['row'].get('style') or {}).get('palette', {}).get('named') or '(none)' for d in data)
    L += ['## 5. Tool themes', '',
          'A figure counts under a theme when at least three of its palette values are exact theme colours or theme tints (PowerPoint / Office 2013 and 2023; draw.io fill and stroke pairs).', '']
    L += share_table(data, ['office', 'drawio'], lambda d: d['theme'])
    L += ['The measurement pass, which looks for the six accents of a named palette, found: ' + ', '.join(f'{k} {pct(v, n)}' for k, v in named.most_common()) + '.', '',
          'Most used exact values over all roles: ' + ', '.join(f'`{k}` {v}' for k, v in C(e['hex'] for _, e in ents if e['hex'] not in ('#ffffff', '#000000')).most_common(28)), '']
    # ---- 6. opacity and bitmap-only colours
    L += ['## 6. Notes', '',
          f'- {sum(1 for _, e in ents if e["opacity"] not in (None, 1, 1.0))} entries in {sum(1 for d in data if any(e["opacity"] not in (None, 1, 1.0) for e in d["ent"]))} figures are drawn with opacity below 1 (translucent washes and overlays).',
          f'- {sum(1 for _, e in ents if e["approx"])} entries in {sum(1 for d in data if any(e["approx"] for e in d["ent"]))} figures are marked approximate: the colour exists only inside a pasted bitmap and was read off the picture.',
          f'- role of an entry as mined: ' + ', '.join(f'{k} {pct(v, len(ents))}' for k, v in C(e['role'] for _, e in ents).most_common()) + '.', '']
    # ---- 7. examples
    L += ['## 7. Figures to look at', '']
    for sc in schemes: L += [f'- {sc}: ' + ', '.join(d['id'] for d in sorted((d for d in data if d['scheme'] == sc), key=lambda d: d['id'])[:8])]
    for tn in ('pale', 'mixed', 'strong'): L += [f'- {tn} fills: ' + ', '.join(d['id'] for d in sorted((d for d in data if d['tone'] == tn), key=lambda d: d['id'])[:8])]
    L += ['']
    write_md(os.path.join(OUT, 'palettes.md'), L)
    write_csv(os.path.join(OUT, 'figures_palette.csv'), ['id', 'kind', 'subfield', 'ground', 'scheme', 'hues', 'tone', 'line_colour', 'text_colour', 'themes', 'fills', 'lines', 'texts'],
              [[d['id'], d['kind'], d['sub'], d['rec']['style'].get('ground'), d['scheme'], ' '.join(d['hues']), d['tone'], d['line_col'], d['text_col'], ' '.join(sorted(d['theme'])),
                ' '.join(e['hex'] for e in d['fills']), ' '.join(e['hex'] for e in d['lines']), ' '.join(e['hex'] for e in d['texts'])] for d in data])
    write_csv(os.path.join(OUT, 'entries.csv'), ['id', 'kind', 'subfield', 'hex', 'role', 'hue', 'tone', 'lightness', 'saturation', 'opacity', 'approx', 'used_for'],
              [[d['id'], d['kind'], d['sub'], e['hex'], e['role'], e['hue'], e['tone'], e['l'], e['s'], e['opacity'], int(e['approx']), e['use']] for d, e in ents])
    print(f'{n} figures, {len(ents)} palette entries -> {OUT}/palettes.md, figures_palette.csv, entries.csv, swatches.csv')


if __name__ == '__main__':
    main()
