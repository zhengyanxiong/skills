#!/usr/bin/env python3
"""B. Grounds of the AI-family figures: what the figure stands on and how its parts are set apart.

    python3 figgenie-paper-diagram/scripts/distill/ai_grounds.py        # -> ai-corpus/lab/distill/grounds/

  grounds.md            the tables below
  figures_ground.csv    one row per figure: ground class, grouping devices, the region tints found in its palette
  region_tints.csv      one row per region tint: hex, hue family, lightness, saturation, what the record says it is behind

What is enumerated and what is mined
  * the ground class (`style.ground`), the grouping devices (`layout.grouping`), nesting depth and panel frames are
    enumerated fields of the semantic record; the ground class was also labelled by the pre-screen on all 3,274 designed
    figures, which is the corpus number printed beside the pool.
  * the region tints are MINED from the free-text `used_for` of `style.palette`: an entry counts as a region tint when it
    is light (HLS lightness >= 0.78), says it lies behind or fills a region / band / zone / lane / half / panel / area /
    background, and is not an outline, a title strip or a text colour. A tint the record does not describe this way is
    missed, so the counts are a floor.
"""
import os, re
from ai_common import *

OUT = os.path.join(DISTILL, 'grounds')
GROUNDS = ['white', 'tinted-regions', 'grey-panels']
DEVICES = ['tinted-regions', 'framed-boxes', 'dashed-boxes', 'whitespace', 'panel-frames', 'other']
PANEL_REF = re.compile(r'\b(in|of|on|inside)\s+(the\s+)?(panel|panels)?\s*\(?[a-hA-H]\)?(\s*(,|and|to|-)\s*\(?[a-hA-H]\)?)*\b|\bpanels?\s+\(?[a-hA-H0-9]\)?')
LINE = re.compile(r'\b(outline|outlines|stroke|strokes|border|borders|arrow|arrows|arrowheads?|lines?|edges?|text|labels?|headings?|words?|font|dashed|dotted|rules?|brackets?|curves?|letters|numbers|caption|titles?|header|headers|title strip|title bar|title band|tab|tabs|pill|pills|chip|chips|tag|tags|swatch|legend|key|bars?|dots?|nodes?|icons?|glyphs?)\b', re.I)
REGION = re.compile(r'\b(background|ground|backdrop|regions?|bands?|zones?|lanes?|half|halves|areas?|wash|panels?|containers?|sections?|quadrants?|behind|tinted (block|blocks|box|boxes|frame|frames)|stage (block|blocks|box|boxes|tint)|group (box|boxes|tint)|module group)\b', re.I)


def region_tints(d):
    out = []
    for e in lst(d['rec']['style'].get('palette')):
        hx = str(e.get('hex') or '').lower(); use = PANEL_REF.sub(' ', e.get('used_for') or '')
        if not HEX_RE.match(hx) or hx == '#ffffff': continue
        h, l, s = hls(hx)
        if l >= 0.78 and REGION.search(use) and not LINE.search(use): out.append(dict(hex=hx, hue=hue_family(hx), l=round(l, 3), s=round(s, 3), use=e.get('used_for') or ''))
    return out


def main():
    data = load(); n = len(data); L = ['# B. Grounds: what the figure stands on and how its parts are set apart', '', POOL_NOTE, '']
    for d in data:
        d['ground'] = d['rec']['style'].get('ground') or 'other'; d['dev'] = set(lst(d['rec']['layout'].get('grouping'))); d['tints'] = region_tints(d)
    # ---- 1. ground class
    cs = corpus_share('ground'); cg = corpus_share('ground', 'good')
    L += ['## 1. Ground class', '',
          '`white`: the page shows through and regions, if any, are outlined; `tinted-regions`: stages, panels or groups sit on pale colour fields; '
          '`grey-panels`: the fields are grey.', '',
          'Pre-screen label on all designed figures of the corpus: ' + ', '.join(f'{g} {100 * cs[g][0]:.0f}%' for g in GROUNDS if g in cs) + f' (n = {cs[GROUNDS[0]][1]}); '
          'among the figures rated good: ' + ', '.join(f'{g} {100 * cg[g][0]:.0f}%' for g in GROUNDS if g in cg) + f' (n = {cg[GROUNDS[0]][1]}).', '']
    L += share_table(data, GROUNDS + ['gradient', 'other'], lambda d: {d['ground']})
    # ---- 2. grouping devices
    L += ['## 2. How parts are set apart', '', 'A figure usually combines devices; a cell is the share of figures that use the device at all.', '']
    L += share_table(data, DEVICES, lambda d: d['dev'])
    combo = C(' + '.join(sorted(x for x in d['dev'] if x != 'other')) or '(none)' for d in data)
    L += ['Most common combinations: ' + '; '.join(f'{k} {pct(v, n)}' for k, v in combo.most_common(10)), '']
    L += ['Number of devices per figure: ' + ', '.join(f'{k}: {pct(v, n)}' for k, v in sorted(C(len(d['dev'] - {'other'}) for d in data).items())), '']
    L += ['### Devices by ground class', ''] + share_table(data, DEVICES, lambda d: d['dev'], vs=[(g, [d for d in data if d['ground'] == g]) for g in GROUNDS])
    L += ['### Nesting depth and panel frames', '']
    L += share_table(data, ['1', '2', '3', '4'], lambda d: {str(d['rec']['layout'].get('nesting_depth'))}, note='Nesting depth: 1 = flat, 2 = regions holding parts, 3 = regions inside regions.')
    # ---- 3. region tints
    tint_figs = [d for d in data if d['tints']]; ents = [(d, t) for d in data for t in d['tints']]
    L += ['## 3. Region tints (mined from the palette descriptions; a floor, see the header of the script)', '',
          f'{len(ents)} region tints found in {len(tint_figs)} figures: ' + ', '.join(f'{g} {sum(1 for d in tint_figs if d["ground"] == g)} of {sum(1 for d in data if d["ground"] == g)}' for g in GROUNDS) + '.', '']
    per = C(len({t['hex'] for t in d['tints']}) for d in tint_figs); hues_per = C(len({t['hue'] for t in d['tints']}) for d in tint_figs)
    L += ['- different tints per figure: ' + ', '.join(f'{k}: {pct(v, len(tint_figs))}' for k, v in sorted(per.items())),
          '- different hue families among them: ' + ', '.join(f'{k}: {pct(v, len(tint_figs))}' for k, v in sorted(hues_per.items())),
          '- hue family of a tint (share of tints): ' + ', '.join(f'{k} {pct(v, len(ents))}' for k, v in C(t['hue'] for _, t in ents).most_common()),
          '- lightness (HLS): p10 {:.2f}, median {:.2f}, p90 {:.2f}; saturation: p10 {:.2f}, median {:.2f}, p90 {:.2f}'.format(*(quant([t['l'] for _, t in ents], (0.1, 0.5, 0.9)) + quant([t['s'] for _, t in ents], (0.1, 0.5, 0.9)))),
          '- most used exact values: ' + ', '.join(f'`{k}` {v}' for k, v in C(t['hex'] for _, t in ents).most_common(16)), '']
    L += ['Tint hue family by ground class and by sub-field (share of the figures that have a mined tint):', '']
    hues = [k for k, _ in C(t['hue'] for _, t in ents).most_common()]
    L += share_table(tint_figs, hues, lambda d: {t['hue'] for t in d['tints']}, vs=[(g, [d for d in tint_figs if d['ground'] == g]) for g in GROUNDS] + [(s, [d for d in tint_figs if d['sub'] == s]) for s in SUBS if sum(1 for d in tint_figs if d['sub'] == s) >= 8])
    # ---- 4. examples
    L += ['## 4. Figures to look at', '']
    for g in GROUNDS:
        ex = sorted((d for d in data if d['ground'] == g), key=lambda d: (-len(d['tints']), d['id']))
        L += [f'- `{g}`: ' + ', '.join(d['id'] for d in ex[:10])]
    L += ['']
    write_md(os.path.join(OUT, 'grounds.md'), L)
    write_csv(os.path.join(OUT, 'figures_ground.csv'), ['id', 'kind', 'kinds', 'subfield', 'ground', 'grouping', 'nesting_depth', 'panel_count', 'region_tints'],
              [[d['id'], d['kind'], ' '.join(d['kinds']), d['sub'], d['ground'], ' '.join(sorted(d['dev'])), d['rec']['layout'].get('nesting_depth'), d['rec']['layout'].get('panel_count'), ' '.join(t['hex'] for t in d['tints'])] for d in data])
    write_csv(os.path.join(OUT, 'region_tints.csv'), ['id', 'kind', 'subfield', 'ground', 'hex', 'hue', 'lightness', 'saturation', 'used_for'],
              [[d['id'], d['kind'], d['sub'], d['ground'], t['hex'], t['hue'], t['l'], t['s'], t['use']] for d, t in ents])
    print(f'{n} figures -> {OUT}/grounds.md, figures_ground.csv, region_tints.csv ({len(ents)} tints in {len(tint_figs)} figures)')


if __name__ == '__main__':
    main()
