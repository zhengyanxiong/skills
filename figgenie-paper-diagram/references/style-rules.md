# Style rules: systems-conference architecture diagrams

Data-derived drawing rules for "system overview" / architecture diagrams in the style of
OSDI, NSDI, SOSP and ASPLOS 2023-2026 papers. Every number below comes from
`figgenie-paper-diagram/scripts/distill/style_stats.py` run over 1,055 human-rated architecture
diagrams (736 good / 235 ok / 32 bad / 52 discard) extracted as vector SVG from the published
PDFs. Full tables: `figgenie-paper-diagram/references/style-thresholds.json` (machine-readable) and
the CSVs the script writes to its `--out` directory.

## How to read this

- **Units.** All sizes are pt, measured on the PDF-extracted SVG **at print size** — i.e. these
  are the literal sizes the figure appears at on the printed page, not screen pixels or
  drawing-canvas units. 1 pt = 1/72 in = 0.3528 mm. A single (one-column) figure is ≈240 pt
  (3.33 in / 84.7 mm) wide; a double (full-width) figure is ≈504 pt (7 in / 177.8 mm) wide.
- **Corpus.** 1,055 rows with `type == diagram, subtype == architecture` from
  `lab/extracted/corpus_index.csv`. Aesthetic groups are human ratings from the review app:
  good 736, ok 235, bad 32, discard 52 (broken crop / not-a-figure — reported for completeness
  but excluded from every comparison below, per instructions). 870 figures are single-column,
  158 double-column, 27 had a blank `column` field and were inferred (double if `size.w>=380pt`
  else single) — 20 came out double, 7 single. `good_src` (n=273) is the subset of good figures
  that also has the author's editable source SVG (used by the next distillation step); it is
  reported alongside `good` throughout to confirm it is representative — on every metric checked,
  its median matches the full `good` group's median exactly or within a few percent (e.g.
  `palette.n` median 6 vs 6, `density.text_boxes` median 24 vs 21, `font.size_med` 6.5 vs 6.5).
- **Contrast.** "Good vs ok+bad" (n=736 vs n=267) is the primary contrast. Effect size is
  **Cliff's delta** (rank-biserial correlation, δ∈[-1,1], sign = direction good is shifted from
  ok+bad): |δ|<0.147 negligible, <0.33 small, <0.474 medium, ≥0.474 large. Significance is a
  **Mann-Whitney U p-value**, Benjamini-Hochberg **FDR-corrected** across the ~29 numeric metrics
  tested per column split (with this many metrics tested, raw p-values are not trustworthy on
  their own — use the FDR-adjusted one, `mwu_p_fdr` in the CSVs). **Bad alone is only 32 rows**
  (and just 1 in the double-column subset), so a second good-vs-bad-only contrast is reported as
  a diagnostic in `contrast_numeric_bad_only.csv` — it is directionally consistent with every
  "should" rule below (usually with a larger effect size, as expected from a more extreme
  subgroup) but is too small to be a rule source by itself.
- **Severity.** **must** — a hard page-layout constraint, not derived from the good/bad
  contrast (only used for figure width fitting the column). **should** — a real,
  FDR-significant, non-negligible-effect-size signal from the good-vs-(ok+bad) contrast; treat
  as a default, deviate with a reason. **not a signal** — good and ok/bad figures look the same
  on this metric; stated explicitly so it isn't mistaken for an oversight.
- **Column-mix confound.** Good figures are disproportionately double-column: 20.4% of good
  (150/736) vs only 9.0% of ok+bad (24/267) are double-column. Since double-column figures are
  inherently wider and tend to run bigger "largest label" text just from having more room, this
  *inflates* the pooled ("all") contrast for size- and font-scale metrics even when there's no
  real effect within either column on its own. So a "should" is only asserted below when the
  effect **replicates within the single-column split specifically** (n=586 good / 243 ok+bad,
  by far the best-powered slice) — not merely in the pooled number. Two metrics that looked like
  signals when pooled but turned out to be mostly/entirely this artifact (`arrows.heads/lines`,
  `font.size_max`) are called out explicitly in their sections rather than silently dropped.
- **Headline finding.** The most consistent story in the data — and the part that survives the
  column-mix check above — is that **good figures are richer in color and labeling, not
  necessarily "cleaner"**: more distinct fill colors, more labeled components, denser text, and
  (within single-column) somewhat taller. This held up in the good-vs-(ok+bad) contrast, more
  strongly in the good-vs-bad-only diagnostic, and was confirmed visually (see the sanity checks
  embedded in each section). It is specifically **label/color richness that separates them, not
  raw shape count or figure width** (shape density is not significant once normalized by area —
  see §9; width shows no real within-column effect at all — see §10) — so the actionable version
  is "label your components and use a real palette," not "add more boxes" or "draw it bigger."
  Many "ok" figures are not obviously bad, just plainer than "good" ones (see §2's sanity check).

---

## 1. Colours (palette)

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `palette.n` (distinct fill colors, excl. black/white) | 1 – **6** – 16 | 4 (bad-only: 1.5) | δ=+0.29 small, FDR p≈0 | **should** |
| `palette.gray_frac` (share of fill area that's gray) | 0 – 0.17 – 0.97 | 0.08 | δ=+0.14, just under the negligible cutoff | not a signal |
| number of hues (`len(palette.hues)`) | 1 – **4** – 4 | 3 (bad-only: 1) | δ=+0.22 small, FDR p≈0 | **should** |
| `palette.named` (`tab10`/`office`/none) | 94% none, 6.0% office, 0% tab10 | 95% / 4.5% / 0.4% | too rare to test (1/1055 total is tab10) | not a signal (but see note) |

**Rule.** Use **≥4 distinct fill colors** (good p25) for a full architecture diagram; the
typical good figure uses **6** (p50), and even the 95th percentile is only 16 — don't feel
pressure to use more than that. **≤1 color is the strongest single visual tell of a bad figure**:
25% of the 32 bad figures use 0 or 1 fill color at all, vs a good-figure p5 of exactly 1. Use
**≥3 distinct hue families** — note this field is capped at 4 by the extractor (it only records
the *top* 4 hues by pixel count), so "good p95 = 4" is a measurement ceiling, not a stylistic
one; don't read it as "never use a 5th hue," read it as "good figures reach the reportable
maximum (median 4) while ok/bad plateau lower (median 3, bad-only median 1)."

`palette.named` never showed matplotlib's `tab10` default in a good figure (0/736) and it's
essentially unseen corpus-wide (1 occurrence in 1,055 architecture figures) — expected, since
these are hand-drawn diagrams from PowerPoint/OmniGraffle/TikZ, not python-plotted charts, so
this is a genre-fit observation rather than a measured quality effect (n=1 can't support a
contrast). If a tool defaults to `tab10`, treat it as a smell anyway: it signals "chart palette
on a hand-drawn diagram," a mismatch even without formal significance here.

**Sanity check (visual).** The two lowest-`palette.n` **bad** figures inspected —
`nsdi23-059` fig 9 ("Gemel architecture," `palette.n=0`) and `osdi23-006` fig 1 ("Nimble's
architecture," `palette.n=0`) — are both pure black-and-white outline diagrams: plain
rectangles/circles, no fill color anywhere, 5-6 text boxes. Contrast with the **good** exemplars
below (§2), which use 5-7 colors to encode component roles.

---

## 2. Fill

| value | good | ok+bad | diff | FDR p | severity |
|---|---|---|---|---|---|
| `flat` | 90.0% | 88.0% | +1.9pp | 0.47 | (default, always safe) |
| `hatch` | 8.2% | 4.5% | +3.7pp | 0.16 | allowed, mildly good-leaning (0% of the 32 bad figures use it) |
| `none` (no fill at all) | **1.9%** | **7.5%** | **-5.6pp** | **1.0e-4** | **should avoid as the dominant look** |
| `gradient` | 0% | 0% | — | — | unused either way (0/1,055) — no verdict |

**Rule.** Default to **flat fill** (90% of good figures use it as the dominant mode). Hatch
pattern fill is a fine, occasional alternative. Treat an all-outline, no-fill diagram as a
**should-avoid**: it's ~4x rarer in good (1.9%) than in ok+bad (7.5%), a highly significant gap
(p_fdr=1.0e-4) even though the absolute swing is modest — confirmed by the same two bad examples
above, both of which are exactly this pattern (fill=none, black-and-white outlines only).

**Sanity check (visual, "ok" isn't the same as "bad").** `asplos25-036` fig 8 (ok,
`palette.n=3`, no dashed strokes) is a clean, competently-drawn flowchart with pale-yellow fill
boxes — it is not visually "bad," just plainer than the good exemplars (fewer colors, no
grouping/dashed device). This matches the data: most of the ok+bad gap from good is a *degree*
difference (richness), not a defect.

---

## 3. Strokes & dashes

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `stroke.median` (pt) | 0.20 – 0.56 – 1.04 | 0.54 (bad-only: 0.44) | δ=+0.03, p=0.53 | not a signal |
| `stroke.widths` (distinct widths used) | 1 – 2 – 4 | 2 | δ=+0.11, FDR p=0.10 | not a signal (borderline) |
| `stroke.dashed` (any dashed stroke present) | **60.2%** | 44.2% | diff +16.0pp, p_fdr=6.5e-5 | **should (soft preference)** |

**Rule.** Line weight itself is not a quality lever — good, ok and bad figures use essentially
the same **~0.55 pt** (p50) stroke, and the full good range (0.20-1.04 pt, p5-p95) covers
ok/bad too. What *does* separate them: **60% of good figures use a dashed stroke somewhere**
(typically to mark an optional/logical/secondary relationship — e.g. `asplos25-012` fig 2 uses a
dashed box to group the Mixture-of-Experts router's active experts) vs 44% of ok+bad. This is a
soft preference, not a requirement: 40% of good figures are solid-only. Use 1-4 distinct stroke
widths (good p5-p95); 2 is typical.

---

## 4. Corners

| value | good | ok+bad | diff | FDR p |
|---|---|---|---|---|
| `square` | 37.0% | 36.7% | +0.3pp | 0.94 |
| `rounded` | 23.4% | 32.6% | -9.2pp | 0.016 |
| `mixed` | 39.7% | 30.7% | +9.0pp | 0.038 |

**Rule: not a strong signal, no restriction.** All three corner styles appear in roughly a third
of good figures each. There's a mild trend — pure-rounded corners are somewhat less common in
good (23% vs 33%) and mixed styles somewhat more common (40% vs 31%) — but both differences are
under the 10-percentage-point practical bar used elsewhere in this document, so treat corner
style as a free choice, not a rule.

---

## 5. Arrows & connectors

| metric | good p5 – p50 – p95 (all) | ok+bad p50 | pooled effect | single-column effect | severity |
|---|---|---|---|---|---|
| `arrows.heads` (filled-triangle arrowheads) | 0 – 8 – 39 | 6 | δ=+0.18 small, FDR p=4.5e-5 | δ=+0.14 negligible, FDR p=0.003 | not robust (see note) |
| `arrows.lines` (straight connector segments) | 0 – 10 – 119 | 6 | δ=+0.17 small, FDR p=6.2e-5 | δ=+0.12 negligible, FDR p=0.009 | not robust (see note) |
| `arrows.curved` (bezier connectors) | 0 – 0 – 10 | 0 | δ=+0.03, p=0.53 | — | not a signal |
| curved/(curved+lines) ratio | 0 – 0 – 0.78 | 0 | δ=-0.002, p=0.97 | — | not a signal |
| heads per line (heads/lines) | 0 – 0.55 – 10.4 | 0.50 | δ=+0.10, FDR p=0.28 combined | — | not a signal |

**Rule: not a robust independent signal — a column-mix artifact.** The pooled contrast looks
real for `arrows.heads`/`arrows.lines` (good median 8 heads / 10 lines vs ok+bad 6 / 6, both
FDR-significant), but **neither replicates within the single-column split alone**
(heads δ=+0.14, just under the negligible cutoff, and fails FDR at p=0.003; lines δ=+0.12,
same). The double-column split shows a similarly-sized effect (δ≈0.16-0.17) but isn't
significant there either (n=24 ok+bad, underpowered). Combined with the column-mix confound
above (good is 20.4% double-column vs ok+bad's 9.0%, and double-column figures simply have more
room for connectors), the honest read is: **arrow/line count tracks overall diagram complexity
(§9), not an independent "use more arrows" lever** — don't add connectors for their own sake.
Heads-per-line (the fraction of connectors that carry a directional arrowhead vs a plain line)
is not a signal either way — good and ok/bad diagrams draw roughly the same proportion of
directional-vs-plain connectors (~0.5). Curved vs straight connector style is **not a signal at
all** — median is 0 curved connectors in every group; straight/orthogonal routing dominates
regardless of rating. Don't add curves for polish; they're not associated with quality here.

---

## 6. Icons & images

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `icons.images` (embedded raster images) | 0 – 0 – 14.25 | 0 | δ=-0.02, p=0.70 | not a signal |
| `icons.image_area` (fraction of area) | 0 – 0 – 0.39 | 0 | δ=-0.05, p=0.22 | not a signal |
| `icons.glyph_paths` (small vector pictograms) | 0 – 0 – 50.5 | 0 | δ=-0.07, p=0.10 | not a signal (reversed direction) |

**Rule: not a quality lever — do not add decorative icons expecting a boost.** Median is 0 in
every group for all three metrics (icons are optional either way). If anything, the direction is
mildly reversed for vector pictogram icons: **53% of bad figures have ≥1 `glyph_paths` icon vs
36% of good** (raw presence rate; the formal effect size is negligible at δ=-0.07). Icons are
fine when they carry real meaning (e.g. a disk icon for storage), but they are not what makes a
figure read as "good" in this corpus — structure and labeling are (§1, §9).

---

## 7. Step markers

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `steps.digits` (standalone digit labels, e.g. a lone "3") | 0 – 0 – 14 | 0 | δ=+0.18 small, FDR p=1e-6 | **should (when applicable)** |
| `steps.circled_count` (circled-digit glyphs, e.g. ①②③) | 0 – 0 – 5 | 0 | δ=+0.03, p=0.17 | not a signal by count |
| any step marker present (digits>0 or circled>0) | 43.8% | ok 28.5%, bad 9.4% | — | supporting evidence |

**Rule.** The median is 0 in every group — most good figures (56%) use **no** step numbering at
all, so this is an optional device, not a default. But when a diagram genuinely depicts an
ordered sequence, good figures are far more likely to number it: **43.8% of good figures have
some digit or circled-number step marker, vs 28.5% of ok and only 9.4% of bad.** Use plain digit
labels or circled numbers to mark an actual sequence of steps (e.g. `asplos25-140` fig 7 uses
circled ①-⑧ to number its request-handling pipeline); don't force numbering onto a diagram that
isn't sequential.

---

## 8. Fonts & sizes

| metric | good p5 – p50 – p95 (all) | single column p50 | double column p50 | ok+bad p50 | effect |
|---|---|---|---|---|---|
| `font.cls` (dominant class) | 75.8% sans, 17.5% serif | — | — | 80.1% / 14.2% | not a signal, FDR p>0.29 for every value |
| `font.size_min` (pt) | 3.0 – 5.5 – 8.0 | 5.5 | 5.5 | 5.5 (bad-only: **6.0**) | δ=-0.13, **reversed**, not a signal |
| `font.size_med` (pt) | 4.5 – 6.5 – 8.5 | 6.5 | 6.5 | **6.5** (identical) | δ=+0.01, p=0.75 | not a signal |
| `font.size_max` (pt) | 5.5 – 8.0 – 14.0 | 8.0 | 9.0 | 7.5 | δ=+0.16 small, FDR p=2.1e-4 | not robust (see note) |
| `font.bold` (share of chars bold) | 0 – 0.13 – 0.96 | — | — | 0.12-0.14 | δ=+0.04, p=0.37 | not a signal |

**Rule.** Sans-serif dominates (76% of good figures) but serif is common too (18%) — font
family/class is not itself a quality signal (every `font.cls` value has FDR p>0.29). **Median
font size is literally identical across good/ok/bad (6.5 pt)** — do not treat median label size
as a lever. **Minimum font size is, if anything, reversed**: good figures have a slightly
*smaller* p50 minimum (5.5 pt) than bad ones (6.0 pt) — because good figures pack in more small
print (more text boxes; see §9), not less. Don't read a small minimum label as a defect, and
don't "fix" a bad figure by enlarging only its smallest label.

**`font.size_max` is not a robust signal once column is controlled for — another column-mix
artifact (see "How to read this").** The pooled contrast looked real (good median 8.0 pt vs
ok+bad 7.5 pt, δ=+0.16 small, FDR p=2.1e-4), but splitting by column shows why it's misleading:
**single-column good median is 7.5 pt** — identical to the pooled ok+bad figure, and the
within-split effect is negligible (δ=+0.14, fails FDR after correction) — while **double-column
good (9.0 pt) is if anything slightly below double-column ok+bad (9.5 pt)** (δ=-0.08, not
significant, n=24). The pooled "good runs it bigger" effect is mostly explained by good having
more double-column figures (20.4% vs 9.0%), and double-column figures naturally use a bigger max
label regardless of rating (9.0 pt double vs 7.5 pt single, for good *and* ok+bad alike). Treat
`font.size_max` as descriptive only — the single-column good p50 of 7.5 pt (p95 12.4 pt) and
double-column good p50 of 9.0 pt (p95 20.0 pt) are reasonable targets, just not a lever.

**Font size does not scale with column width.** The derived ratio `font.size_med / column_width`
is not a signal (p=0.056, borderline) *and* is not even stable across columns — single-column
median is 0.027, double-column median is 0.013 — precisely *because* absolute median font size
stays flat (6.5 pt both) while the column width roughly doubles. **Takeaway: target the same
absolute 5.5-7.5 pt (p25-p75) label size whether the figure is single- or double-column; don't
scale text up just because there's more horizontal room.**

---

## 9. Density (how much is on the page)

This is where the good/ok/bad gap is largest and most consistent.

| metric | good p5 – p50 – p95 | ok+bad p50 | bad-only p50 | effect (good vs ok+bad) | severity |
|---|---|---|---|---|---|
| `density.text` (text-run count) | 14 – **40.5** – 135 | 27 | 14.5 | **δ=+0.41 medium**, FDR p≈0 | **should** |
| `density.text_boxes` (labeled components) | 0 – **21** – 71 | 11 | 6 | **δ=+0.36 medium**, FDR p≈0 | **should** |
| `density.text_per_100pt2` (labels / 100 sq-pt) | 3.1 – 9.6 – 24.8 | 7.1 | 5.3 | δ=+0.28 small, FDR p≈0 | **should** |
| `density.shapes` (drawn shape count) | 38 – 151 – 872 | 101 | 95 | δ=+0.26 small, FDR p≈0 | **should** |
| `density.per_100pt2` (text+shapes / 100 sq-pt) | 14.8 – 46.7 – 202 | 34.6 | 33.0 | δ=+0.18 small, FDR p=3.2e-5 | **should** |
| `density.shapes_per_100pt2` | 8.9 – 34.5 – 181 | 26.6 | 28.9 | δ=+0.14, just under cutoff | not a signal (borderline) |

**Rule.** `density.text` is **the single strongest signal measured in this corpus**
(medium effect, δ=+0.41): good figures have a median of **40.5 text runs**, vs 27 for ok+bad and
just **14.5 for bad alone** (δ=+0.71, *large*, against bad specifically). `density.text_boxes`
(distinct labeled components — i.e. boxes/nodes that actually carry a text label) tells the same
story (good 21, ok+bad 11, bad-only 6). Raw shape count (`density.shapes`) is also up, but once
you normalize by figure area, it's **`density.text_per_100pt2` that stays significant and
`density.shapes_per_100pt2` that doesn't** (δ=0.14, just under the negligible cutoff) — so the
real driver is **label/component density, not shape count for its own sake**. Practical target:
aim for **≥10 text runs per 100 sq-pt** of figure area (good p25=6.4, p50=9.6) and **don't ship
a diagram with fewer than ~5-6 labeled components** unless it's genuinely simple (good p25 for
`density.text_boxes` is 11; the bad-only p50 is 6).

**Sanity check (visual).** `asplos25-012` fig 2 (good, MoE architecture: `palette.n=7`,
`density.text_boxes=26`, dashed=true) and `asplos25-056` fig 3 (good, pulse overview:
`palette.n=7`, `density.text_boxes=19`, dashed=true) both read as visually "finished" —
colorful, every component labeled, dashed grouping box, section references (`§3`, `§4.1`) next
to the relevant stage. Compare with the two bad, zero-fill, 5-8-text-box examples from §1/§2.

---

## 10. Size & aspect ratio by column

| metric | single p5 – p50 – p95 | double p5 – p50 – p95 | pooled effect (all) | single-col effect | double-col effect |
|---|---|---|---|---|---|
| `size.w` (pt) | 210 – 246 – 309 | 430 – 510 – 603 | δ=+0.15 small, FDR p=7.3e-4 | δ=+0.05 negligible, p=0.34 | δ=-0.04 negligible, p=0.81 |
| `size.h` (pt) | 85 – 153 – 257 | 103 – 168 – 313 | δ=+0.19 small, FDR p=2.3e-5 | **δ=+0.20 small, FDR p=3.5e-5** | δ=-0.11 negligible, p=0.67 (reversed) |
| `size.aspect` (w/h) | 0.99 – 1.69 – 2.89 | 1.77 – 3.01 – 5.44 | δ=-0.04, p=0.37 | — | not a signal either way |

**Rule (must — page layout, not a quality signal).** Single-column figures must fit the ≈240 pt
column; double-column figures the ≈504 pt column. This is flagged **must** purely because
exceeding it breaks the printed layout — **`size.w` shows no real within-column quality effect
at all** (single δ=+0.05, double δ=-0.04, neither significant): the pooled δ=+0.15 is fully
explained by the column-mix confound above (good is 20.4% double-column vs ok+bad's 9.0%, and
double-column figures are ~2x wider by definition), not by good figures being drawn wider
*within* their own column. In practice good figures cluster tightly at p25-p75 = 244.6-251.8 pt
(single) and 505.6-514.2 pt (double) — i.e. drawn right at the column width — with a long tail
out to 309 pt / 603 pt (p95). Target the canonical width; treat the p95 as the outer bound seen
in practice, not something to aim for; don't read a wider figure as "better."

**Rule (should — height, single-column evidence).** Height *is* a real signal, but primarily
within single-column: good median 152.6 pt vs ok+bad 133.0 pt (δ=+0.20 small, FDR p=3.5e-5,
n=586/243 — well-powered). **This does not replicate in double-column** — good median there
(168.3 pt) is actually *below* ok+bad (184.8 pt), δ=-0.11, though not significant and n=24 is
likely just too small/noisy to trust either way. Read this as: for single-column figures, taller
(within reason) skews good, consistent with "more content" from §9 — don't fight to compress a
figure that legitimately needs the room, use the p95 (257 pt) as a soft ceiling. For
double-column figures, height is not a validated lever either direction; use the descriptive
range (131-212 pt p25-p75, 313 pt p95) as sizing guidance, not a rule.

**Aspect ratio is not a quality signal** (good and ok+bad look the same, δ=-0.04) but **does
depend heavily on column**, which matters for layout planning: single-column good figures are
close to square-ish (median 1.69, i.e. a bit wider than tall), double-column figures are much
wider (median 3.01) — simply because width roughly doubles while height grows much less
(153→168 pt median, +10%, vs width 246→510 pt, +107%). **Don't scale height proportionally with
width when moving a figure from single- to double-column** — widen it, but only grow the height
modestly.

**Sanity check (visual).** `asplos25-140` fig 7 (good, double-column, `size.w=510pt`,
`aspect=3.02`) is a wide banner-shaped pipeline diagram spanning the full double column at a
photo-confirmed ~3:1 aspect — legend at top, circled step numbers, a dashed red grouping box —
matching both the size-table numbers and the arrows/steps/dashes rules above in one figure.

---

## 11. Tools

`tool` cross-tab by aesthetic (architecture figures only, tools with n≥10):

| tool | n | good% | ok+bad% |
|---|---|---|---|
| powerpoint | 277 | 74.7% | 22.4% |
| omnigraffle | 118 | 72.0% | 25.4% |
| tikz | 51 | 76.5% | 19.6% |
| quartz | 44 | 79.5% | 18.2% |
| drawio | 26 | 65.4% | 19.2% |
| inkscape | 14 | 85.7% | 14.3% |
| google-slides | 13 | 61.5% | 38.5% |
| chrome | 12 | 66.7% | 8.3% |
| keynote | 12 | 91.7% | 8.3% |
| unknown (metadata didn't match a known tool) | 446 | 63.9% | 29.1% |

**Not a strong rule.** The well-populated tools (n≥40: powerpoint, omnigraffle, tikz, quartz)
all sit in a fairly tight 73-80% good-rate band — no single common tool clearly outperforms the
others. The lowest good-rate bucket is `unknown` (64%, but this is 446 rows of PDF metadata that
didn't match a known signature, not a real "tool" choice, so it's not actionable). This likely
reflects author care more than tool choice per se. Venue good-rates range from 51% (NSDI23) to
84% (ASPLOS26) — plausibly reviewer-standard drift over time rather than a style rule; reported
in `venue_by_aesthetic.csv` for reference, not turned into a rule.

---

## Sanity checks performed (visual confirmation)

| # | figure | aesthetic | what the numbers said | what the PNG shows |
|---|---|---|---|---|
| 1 | `nsdi23-059` fig 9 | bad | `palette.n=0`, `fill=none` | Pure black/white outline diagram, no color, 5 text boxes |
| 2 | `osdi23-006` fig 1 | bad | `palette.n=0`, `fill=none` | Pure black/white outline diagram, no color, 6 text boxes, dashed box border only |
| 3 | `asplos25-036` fig 8 | ok | `palette.n=3`, `stroke.dashed=false` | Clean but plain flowchart, pale-yellow fill only, no dashed lines |
| 4 | `asplos25-012` fig 2 | good | `palette.n=7`, `density.text_boxes=26`, `stroke.dashed=true` | Colorful (blue/orange/purple/green), every block labeled, dashed grouping box |
| 5 | `asplos25-056` fig 3 | good | `palette.n=7`, `density.text_boxes=19`, `stroke.dashed=true` | Colorful, section refs (§3/§4.1/§4.2) next to stages, dashed/dotted grouping |
| 6 | `asplos25-140` fig 7 | good | double column, `size.w=510pt`, `aspect=3.02`, circled steps | Wide banner spanning double column, legend, circled ①-⑧ steps, dashed red box |

All six match their measured numbers. Rules in §1 (palette.n), §2 (fill=none), §3 (dashed
strokes), §9 (text-box density) and §10 (double-column size/aspect) are each directly confirmed
by at least one of these.

---

## Quick checklist

**Must (page layout — not a quality signal, just a fit constraint):**
- Figure width fits the column: single-column ≈240 pt (target 245-252 pt, i.e. p25-p75); double-column ≈504 pt (target 506-514 pt). Width itself does **not** predict quality (see §10) — this is purely about not breaking the layout.

**Should (real signals that replicate within the single-column split, not just when pooled — see the column-mix note in "How to read this"):**
- Use ≥4 distinct fill colors (good p25), typically 6 (p50); ≤1 color is the single strongest tell of a bad figure.
- Use ≥3 distinct hue families (out of the top 4 the extractor can report; good p50=4, the cap).
- Use flat fill by default; avoid an all-outline/no-fill look as your dominant style (good 1.9% vs ok+bad 7.5%, even stronger within single-column alone: 1.9% vs 8.2%).
- Use at least one dashed stroke somewhere, typically to mark an optional/secondary/logical path (good 60% vs ok+bad 44%; strongest within single-column, 60% vs 43%).
- Label components with text: ≥11 labeled boxes (`density.text_boxes` good p25), typically 21 (p50); ≥6.4 text runs per 100 sq-pt (good p25), typically 9.6 (p50). This is the single strongest signal measured (`density.text`, medium effect).
- Don't skimp on shape count either: good median 151 drawn shapes (p25=87), but this mostly follows from labeling density above, not a separate target.
- If the diagram shows a genuine sequence, number the steps (digits or circled numbers): 44% of good figures do vs 9% of bad — but most good figures (56%) have no numbering at all, so only do this when there's a real order.
- For single-column figures specifically, don't be afraid of a taller figure if the content needs it: good median height 153 pt vs 133 pt ok+bad (well-powered, δ=+0.20); keep under ~257 pt (p95) as a soft ceiling. (Double-column height is not a validated lever either direction — see §10.)

**Looked like signals but turned out to be a column-mix artifact (good skews 20.4% double-column vs ok+bad's 9.0%, which alone inflates these when pooled) — treat as descriptive, not rules:**
- Arrowhead count / connector-line count (`arrows.heads`, `arrows.lines`) — pooled effect vanishes within either column split alone; tracks overall complexity (§9), not an independent target.
- Largest label size (`font.size_max`) — single-column good (7.5 pt) is identical to pooled ok+bad; double-column good (9.0 pt) is if anything *below* double-column ok+bad (9.5 pt).
- Figure width (`size.w`) — no measurable within-column effect at all (single δ=+0.05 ns, double δ=-0.04 ns); still a **must** for layout-fit reasons, just not a quality lever.
- When widening a figure from single- to double-column, grow width ~2x but height only modestly (~+10-20%, not proportionally) — aspect ratio moves from ~1.7 to ~3.0 as a description of what good figures look like, not because wider/taller itself scores better.

**Not quality signals at all — don't over-index on these:**
- Stroke width/line weight (~0.55 pt median everywhere), number of distinct stroke widths.
- Corner style (square/rounded/mixed all appear in ~a third of good figures each; a very mild trend against pure-rounded, too small to act on).
- Curved vs straight connectors (curved is rare — median 0 — regardless of quality); arrowhead-to-line ratio.
- Icons/pictograms and embedded images (median 0 everywhere; vector-icon presence is if anything *more* common in bad figures — don't add icons expecting a quality boost).
- Font class (sans/serif), font boldness, median font size (literally identical, 6.5 pt, across good/ok/bad).
- Minimum font size — direction is reversed (good p50=5.5 pt < bad p50=6.0 pt); don't read small print as a defect.
- Gray fraction of the palette, `tab10`/`office` named-palette match (near-absent corpus-wide either way).
- Aspect ratio as a standalone number (depends heavily on column, not on quality).
- Drawing tool (powerpoint/omnigraffle/tikz/quartz all land in a similar 73-80% good-rate band).

---

## Figure size table

Recommended targets for a **new** figure, derived from the good-figure distribution (p5-p50-p95
unless noted). pt is the unit that matters for drawing at print size; mm/in given for reference.

### Single column (≈240 pt / 84.7 mm / 3.33 in target width, n=586 good)

| | pt | mm | in |
|---|---|---|---|
| width — target | 240 | 84.7 | 3.333 |
| width — typical range (p25-p75) | 245 - 252 | 86.3 - 88.8 | 3.40 - 3.50 |
| width — outer bound (p5-p95) | 210 - 309 | 74.0 - 109.0 | 2.91 - 4.29 |
| height — median | 153 | 53.8 | 2.12 |
| height — typical range (p25-p75) | 123 - 188 | 43.5 - 66.2 | 1.71 - 2.61 |
| height — soft max (p95) | 257 | 90.7 | 3.57 |
| font size — min (p50) | 5.5 | 1.94 | 0.076 |
| font size — median (p50) | 6.5 | 2.29 | 0.090 |
| font size — max, typical (p50) / occasional emphasis (p95) | 7.5 / 12.4 | 2.65 / 4.37 | 0.104 / 0.172 |
| stroke width — median (p50) | 0.55 | 0.19 | 0.008 |
| stroke width — range (p5-p95) | 0.20 - 1.02 | 0.07 - 0.36 | 0.003 - 0.014 |
| distinct stroke widths | 1 - 2 - 4 (p5-p50-p95) | — | — |

Note: `font.size_max` and `size.w` are reported here as descriptive targets only — §8 and §10
explain why neither is actually a validated quality signal (both looked significant only because
good figures skew more double-column; see "Column-mix confound" above).

### Double column (≈504 pt / 177.8 mm / 7.0 in target width, n=150 good)

| | pt | mm | in |
|---|---|---|---|
| width — target | 504 | 177.8 | 7.000 |
| width — typical range (p25-p75) | 506 - 514 | 178.4 - 181.4 | 7.02 - 7.14 |
| width — outer bound (p5-p95) | 430 - 603 | 151.8 - 212.7 | 5.98 - 8.37 |
| height — median | 168 | 59.4 | 2.34 |
| height — typical range (p25-p75) | 131 - 212 | 46.3 - 74.8 | 1.82 - 2.94 |
| height — soft max (p95) | 313 | 110.3 | 4.34 |
| font size — min (p50) | 5.5 | 1.94 | 0.076 |
| font size — median (p50) | 6.5 | 2.29 | 0.090 |
| font size — max, typical (p50) / occasional emphasis (p95) | 9.0 / 20.0 | 3.18 / 7.06 | 0.125 / 0.278 |
| stroke width — median (p50) | 0.57 | 0.20 | 0.008 |
| stroke width — range (p5-p95) | 0.22 - 1.34 | 0.08 - 0.47 | 0.003 - 0.019 |
| distinct stroke widths | 1 - 3 - 5 (p5-p50-p95) | — | — |

Note font size and stroke width barely change between single and double column (median 6.5 pt /
0.55-0.57 pt either way) — **don't scale type or line weight with figure width**; only the
canvas grows.

---

## Method notes

- Script: `figgenie-paper-diagram/scripts/distill/style_stats.py --index lab/extracted/corpus_index.csv --out <dir>`. Self-test (`--self-test`) cross-checks the scipy Mann-Whitney p-value against a hand-written normal-approximation fallback (tie-corrected) and Cliff's delta against its brute-force O(n·m) definition on 20 synthetic trials; both passed (max |Δp|<0.02, exact delta match) at the time of writing, with scipy 1.13.1 available.
- `style-thresholds.json` is generated from the same run's `summary.json` by `figgenie-paper-diagram/scripts/distill/build_thresholds.py`, which also carries the severity/note text above as code (not hand-typed JSON) — regenerate both by re-running `style_stats.py` then `build_thresholds.py` after the corpus grows.
- Multiple-comparison caveat: ~29 numeric metrics were tested per column split; the FDR correction controls the expected false-discovery rate at 5% across that family, but with n_bad=32 (n=1 for double-column) the bad-only diagnostic in particular should be read as suggestive, not confirmatory.
- All specific figures cited (paper_id + fig number) can be viewed at `lab/extracted/<paper_id>/<pdf_svg stem>.png`, e.g. `lab/extracted/nsdi23-059/nsdi23-059_fig9_p8_mixed.png`.
