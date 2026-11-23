#!/usr/bin/env python3
"""G. Anti-patterns of the AI family: what lower-rated figures do, and what goes wrong even in good ones.

    python3 figgenie-paper-diagram/scripts/distill/ai_antipatterns.py        # -> ai-corpus/lab/distill/antipatterns/antipatterns.md

Three sources, of different strength, kept apart in the output:
  1. MEASURED: properties of the extracted SVG (text items, shapes, painted area by tone, picture area) and pre-screen
     labels, compared across the human ratings good / ok / bad on every designed figure whose extracted Figure 1 is the
     gallery picture. These are rates with an n; the bad group is small (about 30), so its rates are rough.
  2. READ: lower_rated_labels.csv, one reading of all 35 figures rated bad and of 36 drawn at random from the 212 rated
     ok, by the main agent from the gallery pictures, knowing the rating. It names the fault types; it is not a rate
     in the population and has no base rate among good figures.
  3. NAMED IN GOOD FIGURES: the `weaknesses` of the 336 semantic records, sorted with the keyword rules of
     ai_encoding.py. They are what a close reader finds wrong in figures a human rated good.
  4. BLIND: lab/distill/antipatterns/blind/labels.jsonl (ai-corpus/scripts/antipattern_blind.py): vision agents labelled
     the same fault types on 245 figures (all rated bad, 105 rated ok, 105 rated good in the same mix of kinds) without
     seeing the ratings. This is the test of the reading: a fault type stays an anti-pattern only if its rate rises from
     good to bad. Two of the seven did not pass and are reported as such.
The descriptions and the "instead" lines in FAULTS and FIXES are a synthesis written on top of these; they are the
draft of references/ai/anti-patterns.md and carry no force beyond "this is what the evidence shows".
"""
import csv, json, os, re
from ai_common import *
import ai_encoding as E

OUT = os.path.join(DISTILL, 'antipatterns')
PROXIES = [   # (label, what it stands for, test over a measured row)
    ('at most 20 text items', 'bare', lambda x: x['text'] <= 20),
    ('at most 30 text items and at most 90 shapes', 'bare', lambda x: x['text'] <= 30 and x['shapes'] <= 90),
    ('pre-screen: sparse', 'bare', lambda x: x['pre'].get('density') == 'sparse'),
    ('no picture and no icon (pre-screen)', 'bare', lambda x: str(x['pre'].get('pictures')) == '0' and x['pre'].get('icons') == 'none'),
    ('mid or strong fills on at least 15% of the canvas', 'loud ink', lambda x: x['strong'] >= 0.15),
    ('mid or strong fills on at least 25% of the canvas', 'loud ink', lambda x: x['strong'] >= 0.25),
    ('strong fills (lightness under 0.55) on at least 10% of the canvas', 'loud ink', lambda x: x['strong_only'] >= 0.10),
    ('pre-screen: drawn as a chat transcript', 'wall of text', lambda x: x['pre'].get('base') == 'chat-transcript'),
    ('pictures on at least 40% of the canvas', '(no fault: pictures as such)', lambda x: x['pic'] >= 0.40),
    ('smallest type under 5 pt', '(tolerated: small type)', lambda x: 0 < x['fmin'] < 5),
    ('at least 120 text items', '(no fault: density as such)', lambda x: x['text'] >= 120),
]
FAULTS = [   # (label in lower_rated_labels.csv, title, what it looks like, instead)
    ('bare', 'The bare skeleton',
     'A handful of large boxes with one or two words each, joined by arrows; big type, wide gaps, nothing concrete. It says what a reader of the abstract already knows. Often a single panel in one or two hues.',
     'Put the content in: a real input and the output it becomes, the intermediate thing each stage produces, the one example that shows the claim. If the idea really is three boxes, draw it in a single column, or '
     'let it be one panel of a larger figure.'),
    ('garish', 'Loud ink',
     'Large areas in saturated or dark colour, gradient-filled blocks, heavy black frames, white text on colour, red banners. The fills shout over the content, and the figure reads as a slide.',
     'Keep large fields pale and spend strong colour on small things that must be found (an accent, a verdict, the proposed part). Outlines thin and dark, or none on a tinted field. Across the corpus the chromatic fills of a '
     'figure cover a median 12% of its canvas and strong ones almost nothing.'),
    ('clip-art', 'Clip-art as the content',
     'Oversized stock pictograms, emoji, silhouettes or cartoon characters standing where the content should be: a globe for "the world", a devil for "the attacker", a robot for "the model", with little else in the figure.',
     'An icon may name an actor at label size; it cannot carry the argument. Use it small and next to the thing it names, in one style across the figure, and show what the actor does with real material.'),
    ('text-wall', 'The wall of text',
     'A transcript, a prompt, a bullet list or a table pasted in full: several paragraphs of small coloured type, sometimes in three or four highlight colours, with nothing drawn.',
     'Quote the two or three lines that matter and mark the words that carry the point; elide the rest with an ellipsis. A list of items is a table in the text, not a figure.'),
    ('plots-screens', 'Plots and screenshots as the figure',
     'Result charts, heat maps on dark grounds, 3D surfaces or raw screenshots take most of the canvas, with a small or missing drawing. The figure shows evidence without saying what the method is.',
     'A result may sit beside the drawing as one tile or one inset with a headline number. A screenshot is a sample: crop it to the part that matters, give it a light frame, and keep it from setting the tone of the whole figure.'),
    ('small-content', 'Small content in a big frame',
     'The drawing is fine in itself but tiny: thin lines and small icons lost in large tinted panels or in white space, so the frame is what one sees.',
     'Size the canvas to the content, not the content to a preset canvas: shrink the panels to fit, or enlarge the parts until labels reach the size floor without leaving empty fields.'),
    ('clutter', 'The overloaded dashboard',
     'A dozen or more tiles, charts, photos and text blocks at one visual weight, each too small to read, in several unrelated styles. Nothing leads, and the reading order has to be guessed.',
     'Choose what the figure is for and give that the largest area; group the rest into two or three regions with one reading path. A contribution mosaic works when its tiles are few and unequal on purpose.'),
]
FIXES = {   # weakness category -> what to do, for the faults named in good figures
    'small-text': 'Hold the size floor of the skill at print size (it is a physical limit, not a preference) and win the space back elsewhere: full width, shorter labels, fewer words per box, fewer tiles.',
    'code-unexplained': 'Whatever a colour, a line style or a mark means, say it inside the figure: a small key, or better a direct label on the first instance. Two thirds of the pool have no legend, so the direct label is the usual way.',
    'link-not-drawn': 'If the reader must know that B comes from A, draw it: an arrow, a leader, a wedge to the zoomed part, or a shared colour with a label. Position and a shared name alone leave it to be guessed.',
    'caption-dependence': 'Write panel titles and the names of the parts into the figure; the caption explains, it should not be the only place where the parts are named.',
    'arrows': 'Route so that arrows do not cross; label the ones that are not plain data flow; keep one direction for one meaning.',
    'content-missing': 'Before drawing, list what the argument needs to be seen (the model, the data, the remedy, a number with its unit) and check that each is on the canvas.',
    'crowding': 'Cut before shrinking: fewer examples, fewer tiles, shorter text; then space evenly.',
    'labels': 'Name every part once in words; expand an abbreviation at first use or in the key; give every symbol a referent.',
    'placement': 'Put a label on or beside its object and a legend clear of the data; align repeated things on one line.',
    'faint': 'A mark that matters gets at least the line weight and contrast of the rest; pale leaders and thin dashed lines vanish in print.',
    'colour': 'One hue, one meaning across the figure; keep tints that must be told apart well apart; never let red against green be the only signal.',
    'bitmap-quality': 'Place bitmaps at 300 dpi or more at print size, crop them cleanly, and frame them alike.',
    'wording': 'Proof-read the labels; word the same category the same way everywhere.',
    'overlap-clipping': 'No label on a line, no shape cut by the canvas edge.',
}


def measured_rows():
    tab = [json.loads(l) for l in open(os.path.join(LAB, 'fig1_table.jsonl'), encoding='utf-8')]
    ar = json.load(open(os.path.join(DISTILL, 'palettes', 'area_cache.json'))); rows = []
    for r in tab:
        if not (r.get('measure') and r['designed'] and r['fig1_status'] in ('match', 'match-other-fig') and r['rating'] in ('good', 'ok', 'bad')): continue
        st = r.get('style') or {}; a = (ar.get(r['paper_id']) or {}).get('area')
        if not a or not st: continue
        d = st.get('density', {})
        rows.append(dict(pid=r['paper_id'], rating=r['rating'], text=d.get('text', 0), shapes=d.get('shapes', 0), strong=a.get('mid', 0) + a.get('strong', 0), strong_only=a.get('strong', 0), pic=a.get('pic', 0),
                         pre=r.get('pre') or {}, fmin=(st.get('font', {}).get('size') or [0])[0]))
    return rows


def main():
    data = load(); n = len(data); rows = measured_rows(); G = {k: [x for x in rows if x['rating'] == k] for k in ('good', 'ok', 'bad')}
    lab = list(csv.DictReader(open(os.path.join(OUT, 'lower_rated_labels.csv'), encoding='utf-8')))
    nb, no = sum(1 for r in lab if r['rating'] == 'bad'), sum(1 for r in lab if r['rating'] == 'ok')
    L = ['# G. Anti-patterns of the AI family (draft)', '',
         'What figures rated lower do, and what goes wrong even in figures rated good. Three sources of different strength (see the header of the script): **measured** rates across the ratings, '
         'a **reading** of the lower-rated figures, and the weaknesses **named in good figures** by the semantic records. Nothing here is a rule except where it restates a print limit; '
         'it is the evidence from which the reference page is written.', '',
         '## 1. What separates the ratings (measured)', '',
         f'Designed figures whose extracted Figure 1 is the gallery picture and that carry a rating: good {len(G["good"])}, ok {len(G["ok"])}, bad {len(G["bad"])}. '
         'With about thirty figures, a rate in the bad column moves by 3 to 4 points per figure.', '']
    L += md_table(['property', 'stands for', 'good', 'ok', 'bad'], [[t, w] + [pct(sum(1 for x in G[k] if f(x)), len(G[k])) for k in ('good', 'ok', 'bad')] for t, w, f in PROXIES])
    L += ['Read with the contrasts of the style tables (lab/distill/style/): figures rated good carry more text items (median 69 against 42), more shapes (204 against 114), more colours (9 against 6), are more '
          'often full width (89% against 78%) and have a legend more often (30% against 20%). The lower-rated figures are not the crowded ones: they are the empty ones and the loud ones. '
          'Small type is more frequent among the good figures, which is the tension of section 4.', '']
    # ---- 2. the fault types, tested blind
    bl = [json.loads(l) for l in open(os.path.join(OUT, 'blind', 'labels.jsonl'), encoding='utf-8')] if os.path.exists(os.path.join(OUT, 'blind', 'labels.jsonl')) else []
    BG = {g: [x for x in bl if x['rating'] == g] for g in ('good', 'ok', 'bad')}
    def wil(k, m, z=1.96):
        if not m: return '-'
        pr = k / m; dd = 1 + z * z / m; c = (pr + z * z / (2 * m)) / dd; h = z * (pr * (1 - pr) / m + z * z / (4 * m * m)) ** 0.5 / dd
        return f'{100 * pr:.0f}% ({100 * max(0, c - h):.0f}-{100 * min(1, c + h):.0f})'
    bkey = {'garish': 'loud'}
    def brate(k, g): return sum(1 for x in BG[g] if bkey.get(k, k) in x['faults']), len(BG[g])
    cnt = {r_: C(x for r in lab if r['rating'] == r_ for x in r['labels'].split()) for r_ in ('bad', 'ok')}
    L += ['## 2. Fault types of the lower-rated figures, tested blind', '',
          f'The types were first named by reading all {nb} figures rated bad and {no} of the 212 rated ok, knowing the rating. They were then labelled blind: vision agents that did not see the ratings marked the same types on '
          f'{len(bl)} figures (good {len(BG["good"])}, ok {len(BG["ok"])}, bad {len(BG["bad"])}; the good sample in the same mix of kinds as the lower-rated one). A cell is the share of the group with the fault and its Wilson 95% interval. '
          'The agents were told to mark a fault only when it is plain and prominent, so the rates are conservative.', '']
    order = sorted(FAULTS, key=lambda f: -(brate(f[0], 'bad')[0] / max(1, brate(f[0], 'bad')[1]) - brate(f[0], 'good')[0] / max(1, brate(f[0], 'good')[1])))
    L += md_table(['fault', 'good', 'ok', 'bad', f'first reading: bad (of {nb})', f'ok (of {no})'], [[t] + [wil(*brate(k, g)) for g in ('good', 'ok', 'bad')] + [cnt['bad'][k], cnt['ok'][k]] for k, t, _, _ in order])
    anyf = lambda x: any(y != 'cropped' for y in x['faults'])
    L += ['At least one of the seven: ' + ', '.join(f'{g} {wil(sum(1 for x in BG[g] if anyf(x)), len(BG[g]))}' for g in BG) + '. Faults per figure: '
          + ', '.join(f'{g} {sum(len([y for y in x["faults"] if y != "cropped"]) for x in BG[g]) / max(1, len(BG[g])):.2f}' for g in BG) + '.', '',
          'What the blind check says:', '',
          '- **Loud ink** is the clearest divider: no figure of the good sample shows it, a tenth of those rated ok and a third of those rated bad do. The measured rates of section 1 point the same way.',
          '- **Clip-art as the content** separates the figures rated bad from the rest.',
          '- **The bare skeleton** and **the wall of text** are about twice as frequent among the lower-rated figures; the intervals overlap, and for bareness the measured rates of section 1 are the stronger evidence.',
          '- **Small content in a big frame** is rare everywhere; the direction is as expected and nothing more can be said from these numbers.',
          '- **Plots and screenshots as the figure** does not separate the ratings.',
          '- **The overloaded dashboard** runs the other way: figures with many tiles at one weight are more frequent among the good ones. The rater rewards rich, many-part figures; what the first reading took for a fault was density. '
          'These two are kept below as cautions, not as anti-patterns.',
          '- The first reading, which knew the ratings, marked bareness, small content, text walls and plots about twice as often as the blind labels on the figures both saw (blind/results.md): it looked for faults where it expected them.', '',
          f'The agents\' own overall verdict follows the human rating only loosely (called weak: ' + ', '.join(f'{g} {100 * sum(1 for x in BG[g] if x["overall"] == "weak") / max(1, len(BG[g])):.0f}%' for g in BG)
          + '; called strong: ' + ', '.join(f'{g} {100 * sum(1 for x in BG[g] if x["overall"] == "strong") / max(1, len(BG[g])):.0f}%' for g in BG) + '), which is worth remembering when a model is asked to judge a drawn figure.', '',
          'The gallery picture itself is cut off or carries stray page text in ' + ', '.join(f'{g} {wil(sum(1 for x in BG[g] if "cropped" in x["faults"]), len(BG[g]))}' for g in BG)
          + ' of the samples; that is a fault of the crop, not of the design, but it may have cost a few figures their rating.', '']
    confirmed = [f for f in order if f[0] not in ('plots-screens', 'clutter')]; caution = [f for f in order if f[0] in ('plots-screens', 'clutter')]
    for k, t, looks, instead in confirmed:
        ex = [x['id'] for x in bl if bkey.get(k, k) in x['faults'] and x['rating'] != 'good'] or [r['paper_id'] for r in lab if k in r['labels'].split()]
        L += [f'### {t}', '', looks, '', f'**Instead.** {instead}', '', 'Lower-rated figures the blind labels put here: ' + ', '.join(ex[:10]), '']
    L += ['### Cautions the blind check did not confirm', '']
    for k, t, looks, instead in caution:
        L += [f'**{t}.** {looks} {instead}', '']
    # ---- 3. named in good figures
    weak_c = [(nm, w, re.compile(p, re.I)) for nm, w, p in E.WEAK]
    for d in data:
        d['weak_txt'] = [str(w) for w in lst((d['rec'].get('encoding') or {}).get('weaknesses'))]; d['weak'] = set()
        for w in d['weak_txt']: d['weak'] |= E.cats_of(w, weak_c)
    L += ['## 3. Faults named in figures rated good', '',
          f'{sum(len(d["weak_txt"]) for d in data)} weakness statements in the {n} semantic records, sorted by keyword rules (a floor; about a fifth of the statements match no rule). '
          'These are faults a figure can carry and still be rated good, so they are polish, not what sinks a figure; '
          + str(sum(1 for nm, _, _ in weak_c if sum(1 for d in data if nm in d['weak']) >= n / 4)) + ' of them are each found in more than a quarter of the pool.', '']
    rows3 = []
    for nm, w, rx in sorted(weak_c, key=lambda c: -sum(1 for d in data if c[0] in d['weak'])):
        g = [d for d in data if nm in d['weak']]
        if len(g) < 12 or nm not in FIXES: continue
        byk = sorted(((pct(sum(1 for d in v if nm in d['weak']), len(v)), name) for name, v in views(data)[1:9]), key=lambda t: -int(t[0][:-1]))
        rows3.append([f'`{nm}`', w, pct(len(g), n), ', '.join(f'{name} {p}' for p, name in byk[:2]), FIXES[nm]])
    L += md_table(['fault', 'what it is', 'share of the pool', 'most frequent in', 'instead'], rows3)
    for nm in ('code-unexplained', 'link-not-drawn', 'caption-dependence', 'content-missing'):
        rx = next(rx for k, _, rx in weak_c if k == nm); ex = [(d['id'], t) for d in data for t in d['weak_txt'] if rx.search(t)][:5]
        L += [f'Examples of `{nm}`: ' + ' | '.join(f'{t} ({i})' for i, t in ex), '']
    # ---- 4. the tension
    L += ['## 4. Dense yet legible', '',
          f'Figures rated good are denser, and they pay for it in type size: the smallest type is under 5 pt in {pct(sum(1 for x in G["good"] if 0 < x["fmin"] < 5), len(G["good"]))} of them '
          f'(ok {pct(sum(1 for x in G["ok"] if 0 < x["fmin"] < 5), len(G["ok"]))}), and "text too small" is named in {pct(sum(1 for d in data if "small-text" in d["weak"]), n)} of the pool. '
          'A reader at a screen zooms in; a reader of the printed page cannot. The skill keeps its size floor, so it has to reach the density of good figures by other means: the full text width, '
          'short labels, real examples in place of sentences, pictures and icons in place of words, and fewer, larger tiles. An empty figure with large type is not the safe choice: it is the first fault of section 2.', '',
          '## 5. What a check could flag (warn or info only)', '',
          '- at most 20 text items on a full-width figure: `bare?` (9% of good, 32% of bad);',
          '- mid or strong fills on at least 15% of the canvas: `loud ink?` (10% of good, 25% of bad); at 25% the rates are 4% and 14%;',
          '- no picture, icon or worked example in a kind and sub-field where most figures have one: info;',
          '- four or more hue families with meaning and neither a key nor direct labels: info;',
          '- type under the size floor: the existing hard check of the skill.',
          'Nothing above can be decided by a script alone except the last; the others ask the drawing agent to look again.', '']
    write_md(os.path.join(OUT, 'antipatterns.md'), L)
    print(f'-> {OUT}/antipatterns.md (measured: good {len(G["good"])}, ok {len(G["ok"])}, bad {len(G["bad"])}; read: bad {nb}, ok {no})')


if __name__ == '__main__':
    main()
