#!/usr/bin/env python3
"""Turn style_stats.py's summary.json into references/style-thresholds.json.

This is where the *editorial* judgment calls live (severity, which metrics
get a tightened rule vs. a purely descriptive band, the human-readable
notes) -- kept as code, not hand-typed JSON, so the thresholds file can be
regenerated after the corpus grows without re-deriving every number by hand.

Severity mapping (md uses must/should; the linter JSON uses error/warn/info):
  error = a hard layout constraint (fits the printed column) -- not derived
          from the good/bad contrast, from the physical page.
  warn  = a real good-vs-(ok+bad) signal: FDR-adjusted Mann-Whitney p<0.05
          (numeric) or two-proportion p<0.05 (categorical) AND a
          non-negligible effect (|Cliff's delta|>=0.147 numeric, or
          >=0.10 absolute frequency difference categorical) in the pooled
          (column_split == 'all') contrast in contrast_numeric.csv /
          contrast_categorical.csv -- ADDITIONALLY required to replicate
          (same bar) within the single-column split alone (n=586 good / 243
          ok+bad, the best-powered slice), because good figures skew
          disproportionately double-column vs ok+bad (20.4% vs 9.0%), which
          on its own inflates the pooled contrast for size/font-scale
          metrics. arrows.heads, arrows.lines and font.size_max all clear
          the pooled bar but fail the single-column check, so they are
          hand-set to 'info' below despite a 'warn'-looking pooled p-value --
          see their notes for the single-vs-double breakdown that shows why.
  info  = no signal at this bar (or fails the single-column replication
          check above) -- band is descriptive only, not enforced.

Default rule = good p5-p95 (numeric) / all observed good values (categorical),
per column_split == 'all'; a metric whose by_column bands differ materially
also gets a "by_column" sub-object. A metric can override the default via
RULE_OVERRIDE below (used only for size.w, which is bounded by the physical
column width rather than by the good-figure percentile band).

Usage: python3 build_thresholds.py [--summary PATH] [--out PATH] [--auto --kind mechanism]

--auto derives the severities and notes from the contrast tables with the same bar (used for the
mechanism-figure kind, whose style-rules.md carries the editorial reading instead); without it the
hand-written NUMERIC_META / CATEGORICAL_META below apply and describe the architecture figures.
"""
import argparse
import json
import os

DEFAULT_SUMMARY = 'distill-out/step1/style_stats/summary.json'
DEFAULT_OUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'references', 'style-thresholds.json'))

# severity + human note for every metric. 'warn' is asserted here only for
# metrics that actually cleared the bar in contrast_numeric.csv / _categorical.csv
# ('signal' column) at column_split == 'all' -- see style_stats.py. Cross-checked
# against contrast_numeric_bad_only.csv for direction consistency before writing.
NUMERIC_META = {
    'palette.n': dict(severity='warn', note=(
        "Distinct non-white/non-black fill colors. Real signal (Cliff's delta +0.29 small, "
        "FDR p~0): good median 6 vs ok+bad median 4, bad-only median 1.5. <=1 color is the single "
        "strongest visual tell of a bad figure (25% of bad figures have 0-1). Target >=4 (good p25).")),
    'palette.gray_frac': dict(severity='info', note=(
        "Fraction of colored fill area that is gray. NOT a signal (delta +0.14, just under the "
        "0.147 negligible cutoff; not FDR-significant). Good figures range from fully saturated to "
        "nearly all-gray alike (p5=0, p95=0.97) -- gray-dominant is not itself a quality problem.")),
    'palette.n_hues': dict(severity='warn', note=(
        "Distinct hue families among fill colors, CAPPED AT 4 by the extractor (it only records the "
        "top 4 hues by pixel count) -- p95=4 is a measurement ceiling, not a stylistic one; do not "
        "read this as 'never use more than 4 hues'. Real signal (delta +0.22 small, FDR p~0): good "
        "median 4 (at the cap) vs ok+bad median 3, bad-only median 1. Target >=3.")),
    'stroke.median': dict(severity='info', note=(
        "Median stroke width in pt. NOT a signal (delta +0.03, p=0.53) -- good, ok and bad figures "
        "use essentially the same line weight (medians 0.56 / 0.54 / 0.44 pt). Band is descriptive.")),
    'stroke.widths': dict(severity='info', note=(
        "Count of distinct stroke widths (rounded to 0.25pt) used in the figure. Borderline: raw "
        "p=0.01 but FDR p=0.10, not significant, delta +0.11 negligible. Not an actionable rule.")),
    'arrows.heads': dict(severity='info', note=(
        "Small filled-triangle arrowheads. The pooled contrast shows a small uptick (delta +0.18, "
        "FDR p=4.5e-5: good median 8 vs ok+bad median 6) but this does NOT replicate within either "
        "column split alone -- single-column delta drops to +0.14 (negligible, fails FDR after "
        "correction, p=0.003) and double-column delta is +0.16 but not significant (n=24, "
        "underpowered). Good figures are also disproportionately double-column (20.4% vs 9.0% of "
        "ok+bad), and double-column figures have more room for connectors regardless of rating -- so "
        "the pooled effect is at least partly a column-mix artifact, not a validated independent "
        "signal. Treat as tracking overall diagram complexity (see density.*), not a target itself.")),
    'arrows.curved': dict(severity='info', note=(
        "Count of curved (bezier) connector lines. NOT a signal -- median is 0 in every group "
        "(good/ok/bad alike). Straight/orthogonal connectors dominate regardless of quality.")),
    'arrows.lines': dict(severity='info', note=(
        "Straight connector segments. Same pattern as arrows.heads: a pooled effect (delta +0.17, "
        "FDR p=6.2e-5: good median 10 vs ok+bad median 6) that does not replicate within either "
        "column split alone (single delta +0.12, FDR p=0.009, fails the magnitude bar; double delta "
        "+0.17 but not significant, n=24) -- likely a column-mix artifact (see arrows.heads) plus a "
        "side effect of overall content density (see density.*), not an independent signal.")),
    'arrows.curved_ratio': dict(severity='info', note=(
        "curved / (curved + lines). NOT a signal (delta -0.002, p=0.97, essentially flat) -- median "
        "0 in every group. Whether connectors are curved or straight does not correlate with rating.")),
    'arrows.heads_per_line': dict(severity='info', note=(
        "arrows.heads / arrows.lines, i.e. roughly what fraction of connectors carry a directional "
        "arrowhead vs a plain line. Borderline (delta +0.10 negligible, raw p=0.04 but FDR p=0.28 "
        "over both contrasts) -- too small to act on.")),
    'icons.images': dict(severity='info', note=(
        "Embedded raster images (photos/logos/icons). NOT a signal (delta -0.02, p=0.70). Most "
        "figures in every group have 0 (median 0); presence is optional either way.")),
    'icons.image_area': dict(severity='info', note=(
        "Fraction of the figure's area covered by embedded raster images. NOT a signal (delta -0.05, "
        "p=0.22). Median 0 in every group.")),
    'icons.glyph_paths': dict(severity='info', note=(
        "Small curved vector shapes (pictogram-style icons drawn as paths, not raster). NOT a "
        "positive signal -- if anything trends the other way (delta -0.07 negligible; a figure has "
        "at least one in 53% of bad vs 36% of good). Decorative icons are not a substitute for "
        "structure; do not add them expecting a quality boost.")),
    'steps.circled_count': dict(severity='info', note=(
        "Count of circled-digit glyphs (e.g. ①②③). NOT a signal by count (delta +0.03, "
        "p=0.17, median 0 everywhere) though presence skews toward good (8.7% of good vs 0% of the "
        "32 bad figures have any) -- too small a base rate to set a band on.")),
    'steps.digits': dict(severity='warn', note=(
        "Standalone digit labels (e.g. a lone '1', '2', '3' next to a step). Real signal (delta "
        "+0.18 small, FDR p=1e-6) despite median 0 in every group (it's an optional device): among "
        "figures that depict an ordered sequence, 43.8% of good figures use some digit/circled step "
        "marker vs 28.5% of ok and only 9.4% of bad. Use step numbers when there is a genuine "
        "sequence to label; skip them otherwise -- most good figures (57%) have none.")),
    'font.size_min': dict(severity='info', note=(
        "Smallest text size in the figure, pt. NOT a signal, and the direction is if anything "
        "reversed (delta -0.13 negligible): good median 5.5pt vs bad median 6.0pt. Good figures "
        "pack in more small print (more text boxes/labels), not less -- do not read a small minimum "
        "font size as a defect, and do not 'fix' bad figures by enlarging their smallest label alone.")),
    'font.size_med': dict(severity='info', note=(
        "Median text size, pt. NOT a signal -- literally identical across groups (good/ok/bad all "
        "6.5pt median). Still a useful descriptive target (see size table); just not a rating lever.")),
    'font.size_max': dict(severity='info', note=(
        "Largest text size in the figure (usually a title or section-header call-out), pt. The "
        "pooled contrast looks real (delta +0.16 small, FDR p=2.1e-4: good median 8.0pt vs ok+bad "
        "7.5pt) but splitting by column shows why it's misleading: single-column good median is "
        "7.5pt -- identical to the pooled ok+bad figure (delta +0.14, negligible, fails FDR after "
        "correction) -- and double-column good (9.0pt) is if anything slightly BELOW double-column "
        "ok+bad (9.5pt, delta -0.08, not significant, n=24). The pooled effect is mostly explained "
        "by good having more double-column figures (20.4% vs 9.0% of ok+bad), and double-column "
        "figures run a bigger max label regardless of rating (good median 9.0pt double vs 7.5pt "
        "single). Not a validated quality lever -- descriptive only.")),
    'font.bold': dict(severity='info', note=(
        "Fraction of characters set in bold. NOT a signal (delta +0.04, p=0.37). Ranges from 0 to "
        "~1 within good figures alike (p5=0, p95=0.96) -- both all-bold and no-bold labeling schemes "
        "appear among good figures.")),
    'density.text': dict(severity='warn', note=(
        "Count of text runs. The single strongest signal in the corpus (Cliff's delta +0.41, "
        "MEDIUM, FDR p~0): good median 40.5 vs ok+bad median 27; bad-only median just 14.5 (delta "
        "+0.71, large). More labeled components is the clearest good/bad separator measured.")),
    'density.shapes': dict(severity='warn', note=(
        "Count of drawn vector shapes (boxes, lines, paths...). Real signal (delta +0.26 small, FDR "
        "p~0): good median 151 vs ok+bad median 101. Weaker once normalized by area (see "
        "density.shapes_per_100pt2, not significant) -- partly just reflects good figures being "
        "somewhat larger (see size.h), not shape count for its own sake.")),
    'density.per_100pt2': dict(severity='warn', note=(
        "(text + shapes) per 100 sq-pt of figure area -- overall content density, size-normalized. "
        "Real signal (delta +0.18 small, FDR p=3.2e-5): good median 46.7 vs ok+bad median 34.6.")),
    'density.text_boxes': dict(severity='warn', note=(
        "Count of rectangles/boxes that contain a text label (i.e. distinct labeled components). "
        "Strong signal (delta +0.36 medium, FDR p~0; bad-only delta +0.54 large): good median 21 vs "
        "ok+bad median 11, bad-only median 6. Confirmed visually (see style-rules.md sanity checks): "
        "bad figures are frequently minimal, sparsely-labeled outline diagrams.")),
    'density.text_per_100pt2': dict(severity='warn', note=(
        "Text-run count per 100 sq-pt, i.e. label density corrected for figure size. Real signal "
        "(delta +0.28 small, FDR p~0): good median 9.6 vs ok+bad median 7.1. This -- not raw shape "
        "count -- is the more robust 'richness' signal once size is controlled for.")),
    'density.shapes_per_100pt2': dict(severity='info', note=(
        "Shape count per 100 sq-pt. Borderline (delta +0.14, just under the 0.147 cutoff; raw "
        "p=0.001 but not the clean signal density.text_per_100pt2 is). Treat as not actionable.")),
    'size.w': dict(severity='error', note=(
        "Figure width in pt at print size, i.e. how much of the column it fills. This is a page-"
        "layout constraint, not a rating signal: the small pooled effect (delta +0.15, FDR p=7.3e-4) "
        "vanishes within either column split alone (single delta +0.05, double delta -0.04, both "
        "not significant) -- it is fully explained by good figures skewing more double-column than "
        "ok+bad (20.4% vs 9.0%), not by good figures being drawn wider within their own column. "
        "Flagged 'error' purely because exceeding the column breaks the layout. Single-column: "
        "target the 240 pt column width (good p25-p75 = 244.6-251.8, i.e. figures sit right at the "
        "column width); double-column: target 504 pt (good p25-p75 = 505.6-514.2)."),
        rule_override=dict(by_split=True)),
    'size.h': dict(severity='warn', note=(
        "Figure height in pt. Real signal within single-column (delta +0.20 small, FDR p=3.5e-5: "
        "good median 152.6pt vs ok+bad 133.0pt, n=586 good/243 ok+bad) -- consistent with good "
        "figures showing more (taller stacks of) content, not just wider ones. Does NOT replicate "
        "in double-column (delta -0.11, good median 168.3pt vs ok+bad 184.8pt -- direction reverses, "
        "not significant, n=24 ok+bad is likely just underpowered/noisy). Treat this as single-"
        "column evidence primarily; the pooled 'all' number (delta +0.19) is corroborated by the "
        "single-column split specifically, not by double.")),
    'size.aspect': dict(severity='info', note=(
        "width/height. NOT a signal (delta -0.04, p=0.37; good median 1.82 vs ok+bad median 1.90). "
        "Aspect ratio by itself does not predict quality -- but differs a lot by column (see "
        "by_column): single-column good figures cluster near-square-ish (median 1.69), double-"
        "column figures are much wider (median 3.01) simply because width roughly doubles while "
        "height does not.")),
    'font.size_med_over_colwidth': dict(severity='info', note=(
        "font.size_med / canonical column width (240pt single, 504pt double) -- a scale-relative "
        "version of font size. NOT a signal (delta -0.09, p=0.056, borderline) AND not even stable "
        "across columns (single median 0.027 vs double median 0.013): that gap exists precisely "
        "because absolute median font size stays flat (~6.5pt) while column width doubles. Takeaway: "
        "target the same absolute 5.5-7.5pt (good p25-p75) label size regardless of column -- do not "
        "scale font size up for a double-column figure.")),
}

CATEGORICAL_META = {
    'palette.named': dict(severity='info', allowed=['', 'office', 'gradient_na'], note=(
        "Whether the fill palette matches a known named default. tab10 (matplotlib's default "
        "categorical palette) is essentially absent from this corpus regardless of rating (0/736 "
        "good, 1/267 ok+bad) -- these are hand-drawn diagrams, not python-plotted charts, so its "
        "near-absence reflects genre fit more than a measured quality effect (n too small either way "
        "to claim a contrast). 'office' (PowerPoint/Office theme colors) appears in 6.0% of good "
        "figures and is fine. Not FDR-significant (p=0.24-0.56 across values) -- informational only.")),
    'fill': dict(severity='warn', allowed=['flat', 'hatch', 'gradient'], note=(
        "How shapes are filled. 'none' (bare unfilled outlines as the dominant look) is "
        "significantly rarer in good figures: 1.9% vs 7.5% of ok+bad (p_fdr=1.0e-4) -- confirmed "
        "visually (both inspected bad examples, nsdi23-059 fig9 and osdi23-006 fig1, were pure "
        "black-and-white outline diagrams with 0 fill colors). 'flat' dominates every group (~88-"
        "90%) and is always safe. 'hatch' pattern fill appears in 8.2% of good vs 0% of the 32 bad "
        "figures (small n, suggestive not conclusive). 'gradient' is unused in this corpus either "
        "way (0/1055) -- no verdict, allowed by default.")),
    'stroke.dashed': dict(severity='warn', allowed=[True, False], prefer=True, note=(
        "Whether the figure uses any dashed stroke. Real signal (frequency diff +16.0pp, p_fdr="
        "6.5e-5): 60.2% of good figures use a dashed stroke somewhere (typically to mark an "
        "optional/logical/secondary relationship, e.g. asplos25-012 fig2's dashed MoE routing box) "
        "vs 44.2% of ok+bad. This is a soft preference, not a requirement -- 40% of good figures use "
        "solid strokes only.")),
    'corners': dict(severity='info', allowed=['square', 'rounded', 'mixed'], note=(
        "Box corner style. Weak/borderline: 'rounded'-only is somewhat less common in good (23.4%) "
        "than ok+bad (32.6%, diff -9.2pp, p_fdr=0.016) and 'mixed' somewhat more common in good "
        "(39.7% vs 30.7%, p_fdr=0.038) -- but both fall under the 10pp practical-difference bar used "
        "elsewhere in this file, and 'square' alone is exactly as common in both groups (37.0% vs "
        "36.7%). All three styles appear across roughly a third of good figures each -- no single "
        "corner style is required.")),
    'steps.circled_present': dict(severity='info', allowed=[True, False], note=(
        "Whether the figure has >=1 circled-digit glyph. NOT FDR-significant (diff +3.1pp, "
        "p_fdr=0.24) though directionally consistent with steps.digits -- base rate too low (8.7% "
        "of good) to set a band on; see steps.digits for the more reliable version of this signal.")),
    'font.cls': dict(severity='info', allowed=['sans', 'serif', 'mono', 'mixed:sans', 'mixed:serif', 'mixed:mono'], note=(
        "Dominant font class. NOT significant in the primary good-vs-(ok+bad) contrast (all diffs "
        "p_fdr>0.29) -- sans dominates everywhere (75.8% good, 80.1% ok+bad). A mixed-class pattern "
        "(e.g. serif captions with sans labels) is more common in the bad-only subset (mixed:sans "
        "9.4% + mixed:serif 6.2% = 15.6% of the 32 bad figures vs 4.3% of good) but this washes out "
        "once diluted by the much larger ok group and n=32 is too small to confirm -- exploratory, "
        "not a rule.")),
}


# ----------------------------------------------------------------------------
# --auto: derive severity and notes from the contrast tables instead of the hand-written
# NUMERIC_META / CATEGORICAL_META above (which describe the architecture figures).  Used for the
# mechanism-figure kind: same bar as documented in the module docstring -- 'warn' needs the pooled
# signal (FDR p<0.05, non-negligible effect / >=10pp) AND the same signal within the single-column
# split alone; size.w is 'error' (physical column width) with a by-split rule; everything else 'info'.
# ----------------------------------------------------------------------------

def _fmt(x, nd=2):
    if x is None: return 'n/a'
    return f'{x:.{nd}f}' if isinstance(x, float) else str(x)


def auto_meta(summary):
    nd = summary['numeric_distributions']
    num = {sp: {r['metric']: r for r in summary['contrast_numeric_okbad'][sp]} for sp in ('all', 'single', 'double')}
    cat = {}
    for r in summary['contrast_categorical']:
        cat.setdefault(r['metric'], {}).setdefault(r['column_split'], []).append(r)
    num_meta, cat_meta = {}, {}
    for m in summary['meta']['numeric_metrics']:
        a, s1 = num['all'].get(m, {}), num['single'].get(m, {})
        pooled, repl = bool(a.get('signal')), bool(s1.get('signal'))
        g = nd[m]['good']['all']
        desc = (f"good median {_fmt(g['p50'])} vs ok+bad median {_fmt(a.get('okbad_p50'))} (Cliff's delta "
                f"{_fmt(a.get('cliffs_delta'), 3)} {a.get('magnitude') or 'n/a'}, FDR p={_fmt(a.get('mwu_p_fdr'), 4)}); "
                f"single-column split alone: delta {_fmt(s1.get('cliffs_delta'), 3)}, FDR p={_fmt(s1.get('mwu_p_fdr'), 4)}. "
                f"Descriptive band = good p5-p95 [{_fmt(g['p5'])}, {_fmt(g['p95'])}].")
        if m == 'size.w':
            info = dict(severity='error', rule_override=dict(by_split=True, clamp_double=1.2), note=(
                'Figure width in pt, bounded by the physical column width (single ~240 pt, double ~504 pt), '
                'not by the good-figure percentile band; rule is per column split, and the double-column maximum is '
                'clamped to 1.2 x 504 pt = 604.8 pt because author-source canvases measured off print scale (and the '
                'blank-column inference that files every wide canvas as double) inflate the raw p95 far past the page. ' + desc))
        elif pooled and repl:
            info = dict(severity='warn', note='Real good-vs-(ok+bad) signal, replicated within the single-column split: ' + desc)
        elif pooled:
            info = dict(severity='info', note='Pooled contrast clears the bar but does NOT replicate within the single-column split '
                        '(column mix, not quality, may explain it) -- descriptive only: ' + desc)
        else:
            info = dict(severity='info', note='No significant good-vs-(ok+bad) signal -- descriptive band only: ' + desc)
        if a.get('low_power') or s1.get('low_power'):
            info['note'] += ' (low power: fewer than the minimum n on one side.)'
        num_meta[m] = info
    for m in summary['meta']['categorical_metrics']:
        rows_all = cat.get(m, {}).get('all', []); rows_single = {str(r['value']): r for r in cat.get(m, {}).get('single', [])}
        hits = []
        for r in rows_all:
            s1 = rows_single.get(str(r['value']), {})
            if r['signal'] and abs(r['diff']) >= 0.10 and s1.get('signal') and abs(s1.get('diff') or 0) >= 0.10:
                hits.append(r)
        # allowed = values good figures actually use, minus '(unknown)' (a measurement gap, not a style) and minus
        # values significantly RARER in good figures (a negative hit, e.g. fill 'none' in the architecture file)
        rarer = {str(r['value']) for r in hits if r['diff'] < 0} if len(rows_all) > 2 else set()   # a boolean keeps both values + prefer
        allowed = [r['value'] for r in sorted(rows_all, key=lambda r: -r['good_frac'])
                   if r['good_frac'] > 0 and str(r['value']) != '(unknown)' and str(r['value']) not in rarer]
        freq = ', '.join(f"{r['value']}: good {r['good_frac']*100:.1f}% vs ok+bad {r['okbad_frac']*100:.1f}% "
                         f"(diff {r['diff']*100:+.1f}pp, FDR p={_fmt(r['z_p_fdr'], 4)})" for r in sorted(rows_all, key=lambda r: -r['good_frac']))
        info = dict(severity='warn' if hits else 'info', allowed=allowed, note=(
            ('Real signal, replicated within the single-column split, on value(s) ' + ', '.join(str(r['value']) for r in hits) + '. '
             if hits else 'No value clears the bar (FDR p<0.05 and >=10pp in the pooled AND single-column contrasts) -- descriptive only. ')
            + 'Frequencies: ' + freq + '.'))
        if hits and len(rows_all) == 2:
            best = max(hits, key=lambda r: r['diff'])
            if best['diff'] > 0: info['prefer'] = best['value']
        cat_meta[m] = info
    return num_meta, cat_meta


def auto_contrast_method(summary, num_meta):
    meta = summary['meta']; nd = summary['numeric_distributions']
    n1g = nd['size.w']['good']['single']['n']; n1o = nd['size.w']['okbad']['single']['n'] if 'okbad' in nd['size.w'] else None
    single = {r['metric']: r for r in summary['contrast_numeric_okbad']['single']}
    n1o = n1o or next((r['okbad_n'] for r in summary['contrast_numeric_okbad']['single']), 'n/a')
    failed = [m for m, r in {r['metric']: r for r in summary['contrast_numeric_okbad']['all']}.items()
              if r['signal'] and not single.get(m, {}).get('signal')]
    col = meta.get('column_eff_counts', {})
    return ("good vs (ok+bad); Cliff's delta magnitude: negligible<0.147, small<0.33, medium<0.474, large>=0.474; "
            "Mann-Whitney U p-values Benjamini-Hochberg FDR-corrected across the %d numeric metrics tested within each "
            "column split. 'warn' requires FDR p<0.05 AND non-negligible effect (numeric) or >=10pp frequency difference "
            "(categorical) AND both groups n>=%d in the pooled (column_split=='all') contrast, PLUS the same bar met within "
            "the single-column split alone (n=%s good/%s ok+bad), so that a different column mix between good and ok+bad "
            "cannot masquerade as a quality signal (column_eff counts: %s). Metrics that clear the pooled bar but fail the "
            "single-column replication and are therefore 'info': %s. bad alone is only %d rows -- see "
            "contrast_numeric_bad_only.csv for that diagnostic; it is not the rule source. Severities were assigned by "
            "build_thresholds.py --auto (no hand-set overrides)." % (
                len(meta['numeric_metrics']), meta['min_n_for_power'], n1g, n1o, col, ', '.join(failed) or 'none',
                meta['aesthetic_counts'].get('bad', 0)))


def band(stats, keys=('p5', 'p50', 'p95')):
    return {k: stats.get(k) for k in keys}


def build(summary, num_meta=None, cat_meta=None, kind='architecture'):
    auto = num_meta is not None
    num_meta = NUMERIC_META if num_meta is None else num_meta
    cat_meta = CATEGORICAL_META if cat_meta is None else cat_meta
    meta = summary['meta']
    nd = summary['numeric_distributions']
    cd = summary['categorical_distributions']
    contrast_num = {row['metric']: row for row in summary['contrast_numeric_okbad']['all']}
    contrast_cat = {}
    for row in summary['contrast_categorical']:
        if row['column_split'] == 'all':
            contrast_cat.setdefault(row['metric'], []).append(row)

    out_metrics = {}

    for m, info in num_meta.items():
        good_all = nd[m]['good']['all']
        okbad_c = contrast_num.get(m, {})
        entry = dict(
            good_p5=good_all['p5'], good_p50=good_all['p50'], good_p95=good_all['p95'],
            good_mean=good_all['mean'], okbad_p50=okbad_c.get('okbad_p50'),
            effect_cliffs_delta=okbad_c.get('cliffs_delta'), effect_magnitude=okbad_c.get('magnitude'),
            mwu_p_fdr=okbad_c.get('mwu_p_fdr'),
            severity=info['severity'], note=info['note'],
        )
        override = info.get('rule_override')
        if override and override.get('by_split'):
            entry['rule'] = {
                'single': {'min': nd[m]['good']['single']['p5'], 'max': nd[m]['good']['single']['p95']},
                'double': {'min': nd[m]['good']['double']['p5'], 'max': nd[m]['good']['double']['p95']},
            }
            if override.get('clamp_double'):   # --auto: physical page bound for the double split (see the note)
                cap = round(override['clamp_double'] * 504, 2)
                if entry['rule']['double']['max'] > cap:
                    entry['rule']['double']['raw_p95'] = entry['rule']['double']['max']
                    entry['rule']['double']['max'] = cap
        else:
            entry['rule'] = {'min': good_all['p5'], 'max': good_all['p95']}
        by_col = {sp: band(nd[m]['good'][sp]) for sp in ('single', 'double')}
        if by_col['single'] != by_col['double']:
            entry['by_column'] = by_col
        out_metrics[m] = entry

    for m, info in cat_meta.items():
        good_all = cd[m]['good']['all']
        rows = contrast_cat.get(m, [])
        entry = dict(
            # str(value) to match good_all's keys, which style_stats.py also builds via str(value) --
            # needed because Python bool keys (stroke.dashed, steps.circled_present) would otherwise
            # serialize through two different paths: json.dump stringifies a bare bool key as
            # lowercase "true"/"false", while style_stats.py's str(True) is capitalized "True".
            good_freq={k: v['frac'] for k, v in good_all.items()},
            okbad_freq={str(r['value']): r['okbad_frac'] for r in rows},
            diff={str(r['value']): r['diff'] for r in rows},
            severity=info['severity'], note=info['note'],
            rule={'allowed': info['allowed']},
        )
        if 'prefer' in info:
            entry['rule']['prefer'] = info['prefer']
        out_metrics[m] = entry

    n_good_single = nd['size.w']['good']['single']['n']
    n_good_double = nd['size.w']['good']['double']['n']
    thresholds = {
        'schema_note': (
            "Generated by figgenie-paper-diagram/scripts/distill/build_thresholds.py from "
            "style_stats.py's summary.json (n=%d %s figures: %d good / %d ok / %d bad / "
            "%d discard, out of a %d-row corpus index). See the style-rules.md next to this file "
            "for the prose version and full method." % (
                meta['n_architecture_rows'], kind, meta['aesthetic_counts'].get('good', 0),
                meta['aesthetic_counts'].get('ok', 0), meta['aesthetic_counts'].get('bad', 0),
                meta['aesthetic_counts'].get('discard', 0), meta['n_index_rows'])),
        'units': 'pt',
        'pt_to_mm': 0.352778, 'pt_to_in': 1 / 72,
        'columns': {
            'single': {
                'width_target': 240, 'width_p5_p95': [nd['size.w']['good']['single']['p5'], nd['size.w']['good']['single']['p95']],
                'height_p50': nd['size.h']['good']['single']['p50'], 'height_max_p95': nd['size.h']['good']['single']['p95'],
                'font_min_p50': nd['font.size_min']['good']['single']['p50'], 'font_median_p50': nd['font.size_med']['good']['single']['p50'],
                'font_max_p95': nd['font.size_max']['good']['single']['p95'],
                'stroke_median_p50': nd['stroke.median']['good']['single']['p50'],
                'stroke_widths_p50': nd['stroke.widths']['good']['single']['p50'], 'n': n_good_single,
            },
            'double': {
                'width_target': 504, 'width_p5_p95': [nd['size.w']['good']['double']['p5'], nd['size.w']['good']['double']['p95']],
                'height_p50': nd['size.h']['good']['double']['p50'], 'height_max_p95': nd['size.h']['good']['double']['p95'],
                'font_min_p50': nd['font.size_min']['good']['double']['p50'], 'font_median_p50': nd['font.size_med']['good']['double']['p50'],
                'font_max_p95': nd['font.size_max']['good']['double']['p95'],
                'stroke_median_p50': nd['stroke.median']['good']['double']['p50'],
                'stroke_widths_p50': nd['stroke.widths']['good']['double']['p50'], 'n': n_good_double,
            },
        },
        'contrast_method': (
            "good vs (ok+bad); Cliff's delta magnitude: negligible<0.147, small<0.33, medium<0.474, "
            "large>=0.474; Mann-Whitney U p-values Benjamini-Hochberg FDR-corrected across the %d "
            "numeric metrics tested within each column split. 'warn' requires FDR p<0.05 AND "
            "non-negligible effect (numeric) or >=10pp frequency difference (categorical) AND both "
            "groups n>=%d in the pooled (column_split=='all') contrast, PLUS the same bar met within "
            "the single-column split alone (n=586 good/243 ok+bad) -- good figures are "
            "disproportionately double-column (20.4%% vs 9.0%% of ok+bad), which by itself inflates "
            "the pooled contrast for size/font-scale metrics; arrows.heads, arrows.lines and "
            "font.size_max clear the pooled bar but fail this replication check and are 'info', not "
            "'warn' -- see their notes. bad alone is only %d rows (1 in the double-column subset) -- "
            "see contrast_numeric_bad_only.csv for that diagnostic; it is not the rule source." % (
                len(meta['numeric_metrics']), meta['min_n_for_power'], meta['aesthetic_counts'].get('bad', 0))),
        'metrics': out_metrics,
    }
    if auto:
        thresholds['kind'] = kind
        thresholds['contrast_method'] = auto_contrast_method(summary, num_meta)
    return thresholds


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--summary', default=DEFAULT_SUMMARY)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--auto', action='store_true', help='derive severities/notes from the contrast tables (for a kind other than architecture)')
    ap.add_argument('--kind', default='architecture', help='figure kind named in the schema note (with --auto)')
    args = ap.parse_args()
    with open(args.summary, encoding='utf-8') as f:
        summary = json.load(f)
    if args.auto:
        num_meta, cat_meta = auto_meta(summary)
        thresholds = build(summary, num_meta, cat_meta, kind=args.kind)
    else:
        missing_num = set(NUMERIC_META) ^ set(summary['meta']['numeric_metrics'])
        missing_cat = set(CATEGORICAL_META) ^ set(summary['meta']['categorical_metrics'])
        if missing_num or missing_cat:
            raise SystemExit(f'metric list mismatch vs summary.json -- numeric diff={missing_num} categorical diff={missing_cat}')
        thresholds = build(summary)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(thresholds, f, indent=1)
    print(f'wrote {args.out}')


if __name__ == '__main__':
    main()
