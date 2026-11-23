#!/usr/bin/env python3
"""Turn ai_style_stats.py's summary.json into references/ai/style-thresholds.json (the AI-venue family).

    python3 figgenie-paper-diagram/scripts/distill/build_ai_thresholds.py [--summary ai-corpus/lab/distill/style/summary.json]
        [--out figgenie-paper-diagram/references/ai/style-thresholds.json]

What the file holds, and how lint.py / spec_validate.py read it for a spec with `meta.family: ai`:
  venues      the six venues' text width (pt) and, for the two-column venues, their column width; `columns[venue]`
              gives one band per `meta.column`: `double` = the full text width (89% of the good figures), `single` =
              one column of a two-column venue (7%; ICML, CVPR, ACL, AAAI only). The band is a page-fit constraint, not
              a quality signal: 0.85-1.08 x the text width for a full-width figure, 0.40-0.62 x for a column figure.
  metrics     every measured metric: the good figures' p5 / p25 / p50 / p75 / p95, the ok+bad median, Cliff's delta
              and the FDR q of the good-vs-(ok+bad) contrast, a severity and a note. `warn` = the contrast is real
              (|delta| >= 0.147 and q < 0.05) and the band good p5-p95 is worth a warning; `info` = descriptive only.
              Direction matters: `font.size_min` is a real contrast in the wrong direction for print (good figures
              use smaller type), so it stays `info` and the print floor of the shared lint parameters holds.
  by_kind     the same quantiles of the budget metrics per figure kind (text boxes, text runs, pictures, picture
              area, fills, height): what the lint's node budget and the drawing plan read for a kind.
  labelled    the pre-screen attributes on all designed figures: corpus / good / ok+bad shares with the contrast.
  lint        the parameters that differ from references/style-thresholds.json for this family (fill-colour and
              saturated-fill ceilings, stroke widths, the node budget by kind) and the `ai_pass` parameters of the
              advisory AI checks (references/ai/anti-patterns.md §5). Everything not listed is inherited.
Severities here are editorial (kept as code so the file can be regenerated when the corpus grows); the prose reading is
references/ai/style-rules.md.
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))
DEFAULT_SUMMARY = os.path.join(REPO, 'ai-corpus', 'lab', 'distill', 'style', 'summary.json')
DEFAULT_OUT = os.path.join(REPO, 'figgenie-paper-diagram', 'references', 'ai', 'style-thresholds.json')

# text width (pt) of the venues' templates, measured on the PDFs (ai_style_stats.py TEXT_W); column width for the
# two-column venues (ICML 234, CVPR 237, ACL 219, AAAI 239 pt: the single-column figures of the corpus, 2026-10-04)
VENUES = {'neurips': dict(text_width=396.0, layout='single-column'), 'iclr': dict(text_width=396.0, layout='single-column'),
          'icml': dict(text_width=486.0, layout='two-column', column_width=234.0), 'cvpr': dict(text_width=495.0, layout='two-column', column_width=237.0),
          'acl': dict(text_width=454.0, layout='two-column', column_width=219.0), 'aaai': dict(text_width=504.0, layout='two-column', column_width=239.0)}
FULL_BAND, COLUMN_BAND = (0.85, 1.08), (0.40, 0.62)
KINDS = ['stage-pipeline', 'model-anatomy', 'side-by-side-contrast', 'worked-walkthrough', 'concept-schematic', 'scope-overview', 'actor-interaction', 'contribution-mosaic']
BUDGET_METRICS = ['density.text_boxes', 'density.text', 'density.shapes', 'icons.images', 'icons.image_area', 'palette.n', 'size.h', 'arrows.heads']

NOTES = {
    'palette.n': "Distinct non-white / non-black fill colours. A real signal (delta +0.30, q ~ 0): good median 9 vs 6; the good p25 is 6. AI-venue figures carry more colours than systems figures (median 6) because samples, icons and role tints add up; below 2 colours is the look of a weak figure.",
    'palette.n_hues': "Hue families among the four largest fills (the measure caps at 4). Good median 4 vs 3 (delta +0.17): a one- or two-hue figure is the weaker look here, unlike the systems family.",
    'palette.gray_frac': "Share of the fill area that is grey. No usable signal (delta +0.12, below the small threshold).",
    'stroke.median': "Median stroke width, pt. No signal: 0.47 in good figures, 0.52 in the rest; AI figures draw slightly lighter than systems figures (0.55).",
    'stroke.widths': "Distinct stroke widths. Negligible effect (delta +0.11): good figures use 3 widths, the rest 2; up to 4 is unremarkable.",
    'arrows.heads': "Arrowheads. Small effect (delta +0.25) that tracks how much is drawn, not a target of its own: model anatomy has 16, a scope overview 2.",
    'arrows.lines': "Connector lines. Same reading as arrows.heads (delta +0.15).",
    'arrows.curved': "Curved connectors: rare at any rating (median 0).",
    'arrows.curved_ratio': "Share of curved connectors. No signal.",
    'arrows.heads_per_line': "Arrowheads per connector. No signal.",
    'icons.images': "Embedded raster images (samples, icons, thumbnails). Small effect (delta +0.16): good figures carry 8, the rest 6; a scope overview 18, a contribution mosaic 21, a concept schematic 4. A count, not a target: samples belong where the content is a sample.",
    'icons.image_area': "Share of the canvas covered by raster images. No signal (median 10%; 24-27% in overviews and mosaics).",
    'icons.glyph_paths': "Vector glyph paths standing for icons. No signal.",
    'steps.circled_count': "Circled step numbers: almost never drawn in this family (98% have none).",
    'steps.digits': "Plain step digits. Negligible effect (delta +0.10).",
    'font.size_min': "Smallest type, pt. A real contrast in the wrong direction for print: good figures go smaller (median 4.5 vs 5.0, delta -0.22) and 72% of the deep records name small type as a weakness. The skill keeps its 6 pt floor and reaches the density of good figures by other means (full text width, short labels, samples in place of sentences).",
    'font.size_med': "Median type size, pt: 6.0 in good figures, 6.5 in the rest (negligible). Labels at 6-7 pt are the family's norm.",
    'font.size_max': "Largest type, pt. No signal (median 9 either way); titles set into the figure run to 16 pt (p95).",
    'font.bold': "Share of bold text runs. No signal (median 19%).",
    'density.text': "Text runs. The strongest signal with density.shapes (delta +0.30, q ~ 0): good median 69 vs 42. Good figures are fuller, not emptier.",
    'density.shapes': "Drawn shapes. Small effect (delta +0.27): good median 204 vs 114.",
    'density.per_100pt2': "Shapes and text per 100 pt^2. Small effect (delta +0.23).",
    'density.text_boxes': "Text boxes (labelled things). Small effect (delta +0.21): good median 14 vs 8; by kind from 4 (concept schematic) to 24 (scope overview). The lint's node budget per kind comes from here (by_kind).",
    'density.text_per_100pt2': "Text runs per 100 pt^2. Small effect (delta +0.21).",
    'density.shapes_per_100pt2': "Shapes per 100 pt^2. Small effect (delta +0.20).",
    'size.w': "Width, pt. Good figures are more often full-width (89% vs 78%); the band in `columns` is the page-fit rule, by venue.",
    'size.h': "Height, pt: median 198 (p5 126, p95 317). Negligible effect; overviews and mosaics run taller (242, 227).",
    'size.aspect': "Width / height: median 2.24. No signal.",
    'size.width_frac': "Width as a share of the venue's text width: median 1.01 (the figure fills the text width). The 'partial' class (0.6-0.85) is the weaker look (4% of good vs 13%).",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--summary', default=DEFAULT_SUMMARY); ap.add_argument('--out', default=DEFAULT_OUT); a = ap.parse_args()
    s = json.load(open(a.summary, encoding='utf-8'))
    num = s['numeric']; cat = s['categorical']; cn = {r['metric']: r for r in s['contrast_numeric'] if r['slice'] == 'all'}
    q = lambda metric, sl='all', grp='good': next((r for r in num if r['metric'] == metric and r['slice'] == sl and r['group'] == grp), None)
    counts = s['counts']['all']
    g = lambda m: q(m)
    # ---- venues / columns
    venues, columns = {}, {}
    h = g('size.h'); fmin, fmed, fmax, smed, swid = g('font.size_min'), g('font.size_med'), g('font.size_max'), g('stroke.median'), g('stroke.widths')
    for v, d in VENUES.items():
        tw = d['text_width']; venues[v] = dict(d)
        base = dict(height_p50=round(h['p50'], 1), height_max_p95=round(h['p95'], 1), font_min_p50=fmin['p50'], font_median_p50=fmed['p50'], font_max_p95=fmax['p95'],
                    stroke_median_p50=smed['p50'], stroke_widths_p50=swid['p50'])
        columns[v] = {'double': dict(width_target=tw, width_p5_p95=[round(FULL_BAND[0] * tw, 1), round(FULL_BAND[1] * tw, 1)], **base,
                                     _note='full text width; 89% of the good figures of the family')}
        if 'column_width' in d:
            cw = d['column_width']
            columns[v]['single'] = dict(width_target=cw, width_p5_p95=[round(COLUMN_BAND[0] * tw, 1), round(COLUMN_BAND[1] * tw, 1)], **base,
                                        _note='one column of a two-column venue; 7% of the good figures (15% in ml-core)')
    # ---- metrics
    metrics = {}
    for m in sorted({r['metric'] for r in num}):
        gq, oq, c = g(m), q(m, grp='ok+bad'), cn.get(m, {})
        if not gq: continue
        real = abs(c.get('cliffs_delta', 0)) >= 0.147 and c.get('q', 1) < 0.05
        sev = 'warn' if real and m != 'font.size_min' else 'info'
        metrics[m] = dict(good_p5=gq['p5'], good_p25=gq['p25'], good_p50=gq['p50'], good_p75=gq['p75'], good_p95=gq['p95'], good_mean=gq['mean'], good_n=gq['n'],
                          okbad_p50=oq['p50'] if oq else None, effect_cliffs_delta=c.get('cliffs_delta'), effect_magnitude=c.get('magnitude'), mwu_q_fdr=c.get('q'),
                          severity=sev, rule={'min': gq['p5'], 'max': gq['p95']} if sev == 'warn' else None, note=NOTES.get(m, ''))
    by_kind = {k: {m: {kk: q(m, 'kind:' + k)[kk] for kk in ('n', 'p25', 'p50', 'p75', 'p95')} for m in BUDGET_METRICS if q(m, 'kind:' + k)} for k in KINDS}
    # ---- labelled attributes (corpus / good / ok+bad shares)
    labelled = {}
    for r in cat:
        if r['slice'] != 'all' or r['group'] not in ('corpus', 'good', 'ok+bad'): continue
        labelled.setdefault(r['source'], {}).setdefault(r['metric'], {}).setdefault(r['value'], {})[r['group']] = r['frac']
    for r in s['contrast_categorical']:
        if r['slice'] != 'all': continue
        cell = labelled.get(r['source'], {}).get(r['metric'], {}).get(r['value'])
        if cell is not None: cell.update(diff=r['diff'], q=r['q'], signal=bool(r['q'] < 0.05 and abs(r['diff']) >= 0.05))
    tb = by_kind
    lint = {
        '_doc': 'Overrides of the shared lint parameters (references/style-thresholds.json `lint`) for meta.family = ai, and the parameters of the advisory ai_pass checks (lint.py, references/ai/anti-patterns.md §5). Print floors (font_min_*), stroke band, alignment and image parameters are inherited unchanged.',
        'max_fill_colours': 16, 'max_saturated_fills': 4, 'max_stroke_widths': 4,
        'node_budget': {k: dict(q3=int(round(tb[k]['density.text_boxes']['p75'])), p90=int(round(tb[k]['density.text_boxes']['p95'])), n=tb[k]['density.text_boxes']['n']) for k in KINDS},
        'node_budget_doc': 'Labelled boxes (density.text_boxes of the good figures) per figure kind: q3 = p75, p90 = p95 (the measure available); the family-wide values are p75 28 / p95 57. A composite of several kinds is budgeted per kind.',
        'ai_pass': {
            'bare_text_runs': 20, 'bare_doc': 'a full-width figure with at most this many text runs: `ai.bare` (9% of good figures, 32% of bad); warn',
            'loud_ink_frac': 0.15, 'loud_doc': 'mid or strong fills covering at least this share of the canvas: `ai.loud-ink` (10% of good, 25% of bad); warn',
            'hue_families_key': 4, 'hue_doc': 'this many hue families or more with a meaning and neither a legend nor direct labels: `ai.hues-no-key`; info',
            'sample_kinds': ['scope-overview', 'contribution-mosaic', 'worked-walkthrough', 'side-by-side-contrast'],
            'sample_doc': 'kinds where most good figures carry a picture, a sample or a worked example; a spec of that kind with none: `ai.no-sample`; info',
        },
    }
    out = {
        'schema_note': f"Generated by figgenie-paper-diagram/scripts/distill/build_ai_thresholds.py from ai_style_stats.py's summary.json (AI-venue Figure 1s: measured {counts['measured/corpus']} figures, good {counts['measured/good']} / ok {counts['measured/ok']} / bad {counts['measured/bad']}; labelled {counts['labelled/corpus']}). Prose: references/ai/style-rules.md.",
        'family': 'ai', 'units': 'pt', 'pt_to_mm': 0.352778, 'pt_to_in': 1 / 72,
        'venues': venues, 'columns': columns,
        'contrast_method': "good vs ok+bad, measured figures (n = 844 vs 216); Cliff's delta (negligible < 0.147, small < 0.33, medium < 0.474) and Mann-Whitney U, Benjamini-Hochberg q across the metrics. 'warn' = |delta| >= 0.147 and q < 0.05, except font.size_min (real but reversed for print).",
        'metrics': metrics, 'by_kind': by_kind, 'labelled': labelled, 'lint': lint,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{a.out}: {len(metrics)} metrics ({sum(1 for m in metrics.values() if m['severity'] == 'warn')} warn), {len(columns)} venues, by_kind {len(by_kind)}")


if __name__ == '__main__':
    main()
