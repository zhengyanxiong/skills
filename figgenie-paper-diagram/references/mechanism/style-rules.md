# Style rules: systems-conference mechanism figures

Data-derived drawing rules for **mechanism figures** — the second figure kind of this skill:
figures that show how *one part* of a system works (walkthroughs, before/after frames,
side-by-side comparisons, state machines, timelines, component internals), as opposed to the
whole-system overview covered by `figgenie-paper-diagram/references/style-rules.md`. Every number below
comes from `figgenie-paper-diagram/scripts/distill/style_stats.py --subtype mechanism` run over 986
human-rated mechanism figures (713 good / 203 ok / 37 bad / 33 discard) extracted as vector SVG
from the published PDFs (and, for a minority, from the authors' own source files). Full tables:
`figgenie-paper-diagram/references/mechanism/style-thresholds.json` (machine-readable) and the CSVs the
script writes to its `--out` directory.

## How to read this

- **Units.** All sizes are pt, measured on the extracted SVG **at print size** — the literal size
  the figure appears at on the printed page. 1 pt = 1/72 in = 0.3528 mm; a single (one-column)
  figure is ≈240 pt (3.33 in / 84.7 mm) wide, a double (full-width) figure ≈504 pt (7 in /
  177.8 mm). One caveat specific to this corpus: a tail of figures was measured from the author's
  *source* canvas rather than a PDF render, and those are not at print scale (18 good figures
  measure >600 pt wide) — see §10.
- **Corpus.** 986 rows with `type == diagram, subtype == mechanism` from
  `lab/extracted/corpus_index.csv` (a 12,577-row index). Aesthetic groups are human ratings from the
  review app: good 713, ok 203, bad 37, discard 33 (broken crop / not-a-figure — excluded from every
  comparison below). 832 figures are single-column, 154 double-column; 53 had a blank `column` field
  and were inferred (double if `size.w>=380pt` else single). `good_src` (n=273), the good figures
  that also have the author's editable source SVG, matches the full good group on most metrics
  (`density.text` median 38 vs 38, `font.size_med` 6.5 vs 6.5, `size.h` 129.0 vs 130.9), runs richer
  on two (`palette.n` 5 vs 4, `density.shapes` 158 vs 126) and reports *fewer* labelled boxes
  (`density.text_boxes` 4 vs 6) — representative, slightly skewed to the elaborate end.
- **Contrast.** "Good vs ok+bad" (n=713 vs n=240) is the primary contrast. Effect size is
  **Cliff's delta** (δ∈[-1,1], sign = direction good is shifted from ok+bad): |δ|<0.147
  negligible, <0.33 small, <0.474 medium, ≥0.474 large. Significance is a **Mann-Whitney U
  p-value**, Benjamini-Hochberg **FDR-corrected** across the 29 numeric metrics tested per column
  split (with this many metrics tested, raw p-values are not trustworthy on their own — use
  `mwu_p_fdr` in the CSVs). **Bad alone is only 37 rows** (6 double-column), so the good-vs-bad
  contrast in `contrast_numeric_bad_only.csv` is a diagnostic only: directionally consistent with
  every "should" below, usually with a larger effect, but too small to be a rule source.
- **Severity.** **must** — a hard page-layout constraint, not derived from the good/bad contrast
  (only figure width fitting the column). **should** — a real, FDR-significant,
  non-negligible-effect signal from good-vs-(ok+bad) that also replicates within the single-column
  split; a default to deviate from with a reason. **not a signal** — good and ok/bad look the same,
  stated explicitly so it isn't mistaken for an oversight. These map onto `error` / `warn` / `info`
  in `style-thresholds.json`; where a section disagrees with an auto-assigned severity it keeps the
  JSON's verdict and adds a marked caveat, never a different bar.
- **Column-mix confound.** Good figures are somewhat more likely to be double-column: 16.8% of good
  (120/713) vs 12.1% of ok+bad (29/240). Double-column figures are wider and hold more, so this can
  inflate a pooled ("all") contrast with no real within-column effect; a "should" is therefore only
  asserted when the effect **replicates within the single-column split** (n=593 good / 211 ok+bad,
  the best-powered slice). Here that was cheap insurance rather than a filter — the mix is much
  closer than for architecture figures (against 20.4% vs 9.0% there) and **every metric clearing the
  pooled bar also clears the single-column bar**, so nothing was demoted. It bites once the other
  way (`size.aspect`, §10): significant within single-column alone but not pooled, so it stays "not
  a signal".
- **Headline finding.** Good mechanism figures **draw more of the mechanism**. The strongest metric
  is raw drawn-shape count (`density.shapes`, good median 126 vs 62 for ok+bad, δ=+0.391 **medium**;
  43 for bad alone, δ=+0.584 large), and unlike the architecture corpus it **survives normalisation
  by figure area** (`density.shapes_per_100pt2` δ=+0.257, a signal here, not one there). Colour
  (§1), connector segments (§5), a dashed stroke (§3), mixed corner shapes (§4) and a taller canvas
  (§10) move with it. Text matters too but less: labelled component boxes are the *weakest* density
  signal here (δ=+0.166) at a median of 6, under a third of the architecture median. The actionable
  version is **"draw the internal structure at a size where it is visible, and colour-code it"** —
  not "add another box" and, notably, **not** "number the steps" (§7).

---

## 1. Colours (palette)

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `palette.n` (distinct fill colors, excl. black/white) | 1 – **4** – 12 | 3 (bad-only: 2) | δ=+0.29 small, FDR p≈0; single δ=+0.28 | **should** |
| `palette.gray_frac` (share of fill area that's gray) | 0 – 0.08 – 0.87 | 0.00 | δ=+0.13 negligible, FDR p=0.005 | not a signal |
| `palette.n_hues` (distinct hue families) | 0 – **3** – 4 | 2 (bad-only: 1) | δ=+0.22 small, FDR p=1e-6; single δ=+0.21 | **should** |
| `palette.named` (`tab10`/`office`/none) | 95.4% none, 3.9% office, 0.7% tab10 | 95.4% / 4.2% / 0.4% | all FDR p>0.8 | not a signal |

**Rule.** Use **≥3 distinct fill colors** (good p25=3); the typical good figure uses **4** (p50),
p75 is 6 and even p95 only 12, with double-column figures richer (p50 5, p95 16) than single-column
(p50 4, p95 11). **Drawing with no fill colour at all is the strongest single tell of a bad
figure**: the bad p25 is exactly 0 — at least a quarter of the 37 bad figures have no filled shape
anywhere — against a good median of 4 (bad-only δ=+0.55, **large**, second only to
`density.shapes` in that diagnostic). Use **≥2 hue families**, typically 3.

Two caveats on `palette.n_hues`. The extractor records only the *top 4* hues by pixel count, so
"good p95 = 4" is a measurement ceiling, not a stylistic one — read it as "good figures reach the
reportable maximum while ok/bad plateau at 2 (bad-only median 1)". And the good **p5 is 0** here (it
was 1 for architecture): a real slice of good mechanism figures is pure black-and-white line work,
some of it very good (§2) — a strong default with a respectable exception.

`palette.gray_frac` is **not a signal** (δ=+0.13, below the negligible cutoff) despite the medians
differing (good 0.08 vs ok+bad 0.00): single-column replication fails (FDR p=0.065) and the
double-column-only flag (δ=+0.32) rests on 29 ok+bad rows. Good mechanism figures are much less gray
than good architecture ones (0.08 vs 0.17). `palette.named` is **not a signal** either — `tab10` in
5 of 713 good figures and 1 of 240 ok+bad, `office` ~4% either way; as for architecture figures,
treat a `tab10` default as a genre smell rather than a measured defect.

**Sanity check (visual).** The two lowest-`palette.n` **bad** figures inspected — `asplos25-121`
fig 4 (PhasePrint path-delay sensor, `palette.n=0`, `fill=none`, `density.text_boxes=0`) and
`nsdi26-129` fig 15 (a packet-state FSM, `palette.n=0`, `fill=none`) — are both pure outline
drawings: a black-on-white carry chain of solid black buffer triangles and D-flip-flop boxes with
one thin gray dashed grouping rectangle, and a ring of unfilled circles with hand-labelled
transitions where the *only* colour is in the state-bit text, never in a fill. Both are legible;
both read as unfinished next to the good exemplars in §9.

---

## 2. Fill

| value | good | ok+bad | diff | FDR p | severity |
|---|---|---|---|---|---|
| `flat` | 88.8% | 82.1% | +6.7pp | 0.023 | (default, always safe) |
| `hatch` | 7.1% | 2.1% | +5.1pp | 0.016 | allowed, mildly good-leaning (0 of the 37 bad figures use it) |
| `none` (no fill at all) | **3.9%** | **15.8%** | **-11.9pp** | **≈0** | **should avoid as the dominant look** |
| `gradient` | 0% | 0% | — | — | unused either way (0/986) — no verdict |

**Rule.** Default to **flat fill** (88.8% of good figures use it as the dominant mode); hatch is a
fine occasional alternative and never appears in a bad figure. Treat an all-outline, no-fill drawing
as a **should-avoid**: **4x rarer in good (3.9%) than in ok+bad (15.8%)**, the sharpest prevalence
ratio of any categorical value here, replicated within single-column (3.7% vs 16.6%, -12.9pp) and
blunter still in the bad-only diagnostic (**12 of 37 bad figures, 32.4%, are fill=none**). Both
`flat` (+6.7pp) and `hatch` (+5.1pp) favour good with FDR significance but fall under the
10-percentage-point practical bar, so the actionable statement is one-directional: avoid no-fill,
rather than "prefer flat over hatch". Mechanism figures live closer to this line than architecture figures (3.9% vs 1.9%), which
fits the genre — automata, circuits and proof-style diagrams are conventionally outline.

**Sanity check (visual, a good figure that breaks the rule).** `osdi26-136` fig 7 (good, single,
`palette.n=0`, `fill=none`, `density.text=74`, `density.shapes=160`) is a four-panel
automaton-construction walkthrough — "(a) Input DFA" through "(d) Result NFA" — entirely
black-on-white: double-ringed accept states, curved transition arcs, `b / b` and `ε` edge labels, a
sub-caption per panel. No colour at all, rated good; what it has is the structure the density rules
describe (four frames of the same object, every edge labelled, 160 shapes). Read §1 and §2 as
"colour is how most good figures carry role information", not "an uncoloured figure cannot be
good".

---

## 3. Strokes & dashes

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `stroke.median` (pt) | 0.15 – 0.55 – 1.12 | 0.55 (bad-only: 0.50) | δ=-0.02, FDR p=0.63 | not a signal |
| `stroke.widths` (distinct widths used) | 1 – 2 – 4 | 2 | δ=+0.07, FDR p=0.16 | not a signal |
| `stroke.dashed` (any dashed stroke present) | **51.2%** | 37.5% | diff +13.7pp, FDR p=0.0013 | **should (soft preference)** |

**Rule.** Line weight is not a quality lever — every group sits at **~0.55 pt** (p50) and the good
range (0.15–1.12 pt, p5–p95) covers ok/bad too. Use 1–4 distinct stroke widths; 2 is typical in both
groups. What separates them is dashing: **51% of good figures use a dashed stroke somewhere** vs
37.5% of ok+bad (+13.7pp, FDR p=0.0013), replicated within single-column (50.4% vs 37.0%), with a
monotone gradient across rating groups (good 51.2%, ok 39.4%, bad 27.0%) — the reassuring shape for
a soft preference. It is exactly that: 49% of good figures are solid-only.

Mechanism figures dash less than architecture figures (51.2% vs 60.2% of good), consistent with
what dashes are *for* in each kind: an architecture figure dashes a grouping boundary, a mechanism
figure often has nothing to group. In the figures inspected here, dashes appeared as zoom/leader
lines from an overview to a detail panel (`osdi26-100` fig 4), as a callout box around an annotated
region (`nsdi25-073` fig 12), and as the not-taken path in a before/after frame.

---

## 4. Corners

| value | good | ok+bad | diff | FDR p | severity |
|---|---|---|---|---|---|
| `square` | 51.7% | 57.1% | -5.3pp | 0.30 | (the mechanism default) |
| `mixed` | **30.7%** | **17.1%** | **+13.6pp** | **0.00045** | **should (soft preference)** |
| `rounded` | 17.4% | 25.8% | -8.4pp | 0.016 | under the 10pp bar — no verdict |

**Rule — and this is where mechanism figures differ sharply from architecture figures**, for which
corner style was explicitly *not* a rule (all three styles appeared in about a third of good
figures; the trends fell under the practical bar). Here `corners=mixed` clears both bars: +13.6pp
pooled (FDR p=0.00045) and +12.0pp within single-column alone (FDR p=0.0042). The bad-only picture
is stark: **28 of 37 bad figures (75.7%) are all-square and only 2 (5.4%) mix**, against 30.7% of
good.

The reading is not "round some corners": square is still the most common style in good mechanism
figures (51.7%, well above architecture's 37.0%) and pure-rounded the least common (17.4% vs 23.4%,
-8.4pp against good but under the bar, so not forbidden). What carries the signal is **using more
than one shape vocabulary in the same figure** — a rounded pill for an operation, a square cell for
a buffer slot, a circle for a state; a figure built from identical square boxes has encoded nothing
in shape.

**Sanity check (visual).** `osdi26-100` fig 4 (good, single, `corners=mixed`, `palette.n=10`,
`density.shapes=127`, `density.text_boxes=46`, dashed) draws a pipelined-execution walkthrough with
three shape vocabularies at once: rounded pill nodes for the dataflow (`Mat → Vec1 → Vec2`), square
grid cells for the matrix/timeline panels, and rounded blue bands of square `k-body` / `load A` /
`store C` cells, tied back by dashed leader lines. Each shape family means something different.

---

## 5. Arrows & connectors

| metric | good p5 – p50 – p95 (all) | ok+bad p50 | pooled effect | single-column effect | severity |
|---|---|---|---|---|---|
| `arrows.lines` (straight connector segments) | 0 – **11** – 80 | 6 (bad-only: 7) | δ=+0.22 small, FDR p=2e-6 | δ=+0.21 small, FDR p=1.6e-5 | **should (with caveat)** |
| `arrows.heads` (filled-triangle arrowheads) | 0 – 5 – 34 | 4 | δ=+0.06, FDR p=0.18 | δ=+0.04, FDR p=0.52 | not a signal |
| `arrows.curved` (bezier connectors) | 0 – 0 – 12 | 0 | δ=+0.09, FDR p=0.024 | δ=+0.08, FDR p=0.095 | not a signal |
| `arrows.curved_ratio` curved/(curved+lines) | 0 – 0 – 1.0 | 0 | δ=+0.05, FDR p=0.30 | — | not a signal |
| `arrows.heads_per_line` | 0 – 0.31 – 5.41 | 0.50 | δ=-0.06, FDR p=0.25 | — | not a signal (reversed) |

**Rule.** `arrows.lines` is a real, replicated signal — good median **11** straight connector
segments vs 6 for ok+bad, holding inside the single-column split (δ=+0.21). This is the mirror image
of the architecture corpus, where `arrows.heads`/`arrows.lines` looked significant pooled but
evaporated inside either column split and were written off as a column-mix artifact; here the column
mix is milder and the effect survives it.

**Caveat on what `arrows.lines` counts (severity kept, reading adjusted).** The extractor counts
straight connector *segments*, not "arrows" — a timeline rule, a table gridline, a circuit wire and
a swimlane divider all land here. Read the rule as **"a good mechanism figure has visible connective
structure: lanes, wires, edges, timelines"**, not "add more arrows". The companion metrics back that
up: **arrowhead count is not a signal at all** (good median 5 vs 4, δ=+0.06 — architecture's median
was 8) and **heads-per-line is if anything reversed** (good 0.31 vs ok+bad 0.50), so good mechanism
figures draw proportionally *fewer* connectors as directed arrows. Curved connectors are **not a
signal** either (median 0 in every group, as for architecture); straight/orthogonal routing
dominates regardless of rating. Don't add curves for polish.

**Sanity check (visual).** `asplos26-047` fig 7 (good, single, `arrows.lines=405` — the highest in
the single-column good group — `arrows.heads=0`, `density.shapes=618`) is a three-panel
quantum-circuit walkthrough. Every one of those 405 "lines" is a qubit wire or a vertical control
line, there is not a single arrowhead in the figure, and the step structure is carried by a
"Step 1…8" ruler and pale band highlights — the cleanest demonstration that this signal is about
connective structure, not arrows.

---

## 6. Icons & images

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `icons.images` (embedded raster images) | 0 – 0 – 13 | 0 | δ=+0.10 negligible, FDR p=0.011 | not a signal |
| `icons.image_area` (fraction of area) | 0 – 0 – 0.21 | 0 | δ=+0.06, FDR p=0.10 | not a signal |
| `icons.glyph_paths` (small vector pictograms) | 0 – 0 – 64 | 0 | δ=+0.05, FDR p=0.21 | not a signal |

**Rule: not a quality lever — do not add decorative icons expecting a boost.** The median is 0 in
every group for all three metrics. The direction here is mildly *positive* (good means 2.3 vs 2.1
embedded images, 12.0 vs 6.7 glyph paths) where the architecture corpus was mildly negative, but
neither reaches the significance or effect-size bar: icons are fine when they carry real meaning and
irrelevant to the rating when they don't. Mechanism figures do use pictograms in ways architecture
figures don't — in the figures inspected here, document icons standing for records in a storage
walkthrough (`osdi25-025` fig 11), a bug icon on the faulty frame, a red lightning bolt marking the
crash point in a recovery timeline (`osdi24-040` fig 3) — but that is genre, not rating.

One diagnostic not to act on: in the good-vs-bad-only contrast `icons.images` does cross the line
(δ=+0.21 small, FDR p=0.029; good mean 2.3 vs bad 0.7) — with n=37 bad and both other contrasts
flat, most plausibly the "bad figures are sparse in *everything*" effect (§9).

---

## 7. Step markers

| metric | good p5 – p50 – p95 | ok+bad p50 | effect | severity |
|---|---|---|---|---|
| `steps.digits` (standalone digit labels, e.g. a lone "3") | 0 – 0 – 36.4 (mean 8.2) | 0 (mean 4.8) | δ=+0.08 negligible, FDR p=0.076 | not a signal |
| `steps.circled_count` (circled-digit glyphs, e.g. ①②③) | 0 – 0 – 3 (mean 0.34) | 0 | δ=+0.03, FDR p=0.071 | not a signal |
| `steps.circled_present` (any circled marker) | 5.9% of good | 2.5% (ok 3.0%, bad 0%) | +3.4pp, FDR p=0.083 | not a signal |

**Rule: not a signal — the most counter-intuitive result in the corpus.** Mechanism figures are
exactly the kind you would expect to depend on step numbering, and for *architecture* figures
numbering was a genuine "should" (δ=+0.18, FDR p=1e-6). Here the same metric clears neither the
pooled bar (δ=+0.08, FDR p=0.076) nor the single-column one (δ=+0.065, FDR p=0.21), and circled
markers are rare in every group (5.9% of good, 2.5% of ok+bad, 0 of 37 bad).

When mechanism figures do number, they number heavily: good p75 is 7 standalone digits and p95 is
**36.4** (architecture: 14.0), mean 8.2 vs 3.5. With a good median of 0 and p75 of 7, **between a
quarter and a half of good mechanism figures carry at least one digit marker** — a common device,
just not a discriminating one. Number an ordered walkthrough when the order isn't obvious from the
layout and pair the numbers with a legend sentence; don't force it onto a comparison or a state
machine with no linear order. An unnumbered mechanism figure is not a defect here.

**Sanity check (visual).** `sosp23-014` fig 1 (good, single, `steps.circled_count=16`,
`steps.digits=12`, `palette.n=2`) stacks three frames — in-place update with a redo log, with an
undo log, and out-of-place — each with an index triangle, a tuple table, a log box, circled ①②③
dropped exactly where the action happens and a numbered legend sentence underneath; a good figure
with only **2** fill colours (grey plus a red accent), a counterweight to over-reading §1. Against
it, `osdi25-025` fig 11 (**ok**, `density.shapes=59`, `density.text=21`, `density.text_boxes=5`)
*also* uses circled ❶-❹ and a Normal-vs-Buggy layout with a red `semantic violation` callout, and is
rated only ok — it sits near the ok+bad medians on every density metric (§9). The markers are not
the variable.

---

## 8. Fonts & sizes

| metric | good p5 – p50 – p95 (all) | single column p50 | double column p50 | ok+bad p50 | effect |
|---|---|---|---|---|---|
| `font.cls` (dominant class) | 67.0% sans, 22.0% serif, 6.2% mixed:sans | — | — | 65.0% / 23.3% | not a signal, FDR p≥0.053 for every value |
| `font.size_min` (pt) | 3.0 – 5.5 – 8.7 | 5.5 | 5.5 | 5.5 (bad-only: 6.0) | δ=-0.07, FDR p=0.18 — not a signal |
| `font.size_med` (pt) | 4.5 – 6.5 – 9.5 | 6.5 | 6.75 | **6.5** (identical) | δ=-0.02, FDR p=0.71 — not a signal |
| `font.size_max` (pt) | 5.0 – 8.0 – 14.0 | 8.0 | 8.75 | **8.0** (identical) | δ=+0.02, FDR p=0.71 — not a signal |
| `font.bold` (share of chars bold) | 0 – 0.07 – 0.98 | 0.07 | 0.075 | 0.02 | δ=+0.05, FDR p=0.30 — not a signal |
| `font.size_med / column_width` | 0.011 – 0.027 – 0.038 | 0.027 | 0.013 | 0.027 | δ=-0.04, FDR p=0.45 — not a signal |

**Rule: nothing in the type is a quality signal.** Sans-serif dominates (67.0% of good figures) but
serif is common (22.0%), and no `font.cls` value comes near the bar (smallest FDR p = 0.053, for
`mixed:serif`, a 2.9pp difference). **Median and maximum label sizes are literally identical across
good and ok+bad (6.5 pt and 8.0 pt).** Minimum size is flat too, with the same mild reversal
architecture showed (bad-only 6.0 pt vs good 5.5 pt) — good figures pack in more small print because
they have more to label, so don't read a small minimum label as a defect.

This is a cleaner null than architecture produced: there, `font.size_max` cleared the pooled bar and
had to be explained away as a column-mix artifact; here there is nothing to explain away (δ=+0.017,
FDR p=0.71). Mechanism figures run their largest label slightly bigger within single-column (8.0 pt
vs 7.5 pt) and are markedly less bold (0.07 vs 0.13), but neither tracks quality.

**Font size does not scale with column width.** The ratio `font.size_med / column_width` is not a
signal (δ=-0.04, FDR p=0.45) *and* is not stable across columns — single 0.027, double 0.013 —
because absolute median size barely moves (6.5 vs 6.75 pt) while the column width doubles. **Target
the same absolute 5.5–7.5 pt (p25–p75) label size in either column.** One underpowered exception,
not to be acted on: within double-column alone, good figures have a *smaller* minimum font than
ok+bad (5.5 vs 7.0 pt, δ=-0.37 medium, FDR p=0.025, 29 ok+bad rows) — same direction as the
bad-only reversal, so most likely the fine-print effect again.

---

## 9. Density (how much is on the page)

This is where the good/ok/bad gap is largest and most consistent — as with architecture figures, but
with a different metric in the lead.

| metric | good p5 – p50 – p95 | ok+bad p50 | bad-only p50 | effect (good vs ok+bad) | severity |
|---|---|---|---|---|---|
| `density.shapes` (drawn shape count) | 31 – **126** – 618 | 62 | 43 | **δ=+0.39 medium**, FDR p≈0 | **should** |
| `density.text` (text-run count) | 6.6 – **38** – 159 | 25 | 19 | δ=+0.27 small, FDR p≈0 | **should** |
| `density.shapes_per_100pt2` | 7.3 – 33.3 – 173.7 | 21.7 | 15.0 | δ=+0.26 small, FDR p≈0 | **should** |
| `density.per_100pt2` (text+shapes / 100 sq-pt) | 14.4 – 46.9 – 183.9 | 36.0 | 24.7 | δ=+0.25 small, FDR p≈0 | **should** |
| `density.text_boxes` (labeled components) | 0 – **6** – 48.8 | 4 | 0 | δ=+0.17 small, FDR p=0.0003 | **should** |
| `density.text_per_100pt2` (labels / 100 sq-pt) | 1.9 – 10.4 – 34.5 | 8.3 | 8.2 | δ=+0.16 small, FDR p=0.0008 | **should** |

**Rule.** All six are replicated signals, and **`density.shapes` is the strongest single metric
measured in this corpus** (δ=+0.39, *medium*): good median **126 drawn shapes** vs 62 for ok+bad and
43 for bad alone (δ=+0.58, *large*). Crucially the per-area version survives too
(`density.shapes_per_100pt2` δ=+0.26): good mechanism figures are not bigger canvases holding the
same drawing, they are **denser drawings** — the opposite of the architecture result, where shape
count normalised by area was the one density metric that failed (δ=+0.14) and label density carried
the story. Practical targets from the good p25/p50: **≥65 drawn shapes, typically 126**; **≥22 text
runs, typically 38**; **≥17 shapes and ≥6 text runs per 100 sq-pt**. Within single-column those read
60 / 109 shapes and 19 / 34 text runs.

**Caveat on `density.shapes` (severity kept, reading adjusted).** The metric counts vector
primitives, so a figure assembled from many small repeated cells — a memory grid, a circuit, a
timeline ruler — accumulates shapes fast without being harder to read (`asplos26-047` fig 7 in §5
reaches 618 this way). Read the rule as "draw the mechanism's internal structure rather than one
opaque box", not "maximise the shape counter"; the area-normalised metric is the sanity-check and
points the same way.

**Caveat on `density.text_boxes`.** A real signal (δ=+0.17) but the weakest of the six, and far
below architecture's absolute level (good median **6** vs **21**). The extractor counts a shape that
*contains* a text label, and mechanism figures put much of their text outside boxes — edge labels,
step legends under a frame, annotations pointing at a region — so it systematically under-reads them
(good p25 is 1, and 0 within single-column). Use `density.text` and `density.text_per_100pt2` as the
labelling targets for this kind; read `density.text_boxes` mainly through its bad-only median of
**0**, i.e. at least half of bad mechanism figures carry no labelled box at all.

**Sanity check (visual, good vs ok at the medians).** `nsdi25-073` fig 12 (good, single,
`density.shapes=128`, `density.text=38`, `density.text_boxes=19`, `palette.n=7`) sits almost exactly
on the good medians and looks it: two panels side by side — a colour-coded incast-control timeline
(blue/orange/green request boxes, a Done/Transmitting/Delayed bar, red italic callouts in a dashed
box) and a two-lifeline negotiation sequence diagram with labelled arrows and phase brackets.
`osdi25-025` fig 11 (ok, `density.shapes=59`, `density.text=21`, `density.text_boxes=5`) sits on the
ok+bad medians and is a competent Normal-vs-Buggy comparison — not "bad", just sparser: most of its
area is repeated grey document pictograms rather than drawn or labelled structure. A *degree*
difference in how much is actually drawn.

---

## 10. Size & aspect ratio by column

| metric | single p5 – p50 – p95 | double p5 – p50 – p95 | pooled effect (all) | single-col effect | double-col effect |
|---|---|---|---|---|---|
| `size.w` (pt) | 223 – 247 – 309 | 407 – 510 – 880 | δ=+0.08 negligible, FDR p=0.089 | δ=+0.04, FDR p=0.50 | δ=+0.15, FDR p=0.29 |
| `size.h` (pt) | 73 – **125** – 236 | 84 – 168 – 349 | δ=+0.22 small, FDR p=2e-6 | **δ=+0.20 small, FDR p=9e-5** | δ=+0.22, FDR p=0.18 (n.s.) |
| `size.aspect` (w/h) | 1.08 – 2.02 – 3.42 | 1.91 – 3.07 – 6.05 | δ=-0.11 negligible, FDR p=0.019 | δ=-0.16 small, FDR p=0.0010 | δ=-0.21, FDR p=0.19 (n.s.) |

**Rule (must — page layout, not a quality signal).** Single-column figures must fit the ≈240 pt
column, double-column figures the ≈504 pt column. This is **must** purely because exceeding it
breaks the printed layout — **`size.w` shows no quality effect at all**, not even pooled (δ=+0.08,
FDR p=0.089, weaker than architecture's pooled effect and failing outright). Good figures cluster
tightly at p25–p75 = 246.0–252.8 pt (single) and 509.8–535.6 pt (double), i.e. drawn right at the
column width.

**Caveat on the width band in `style-thresholds.json`.** The raw double-column p95 of good width is
**879.55 pt** — not a printable width on a 504 pt column. That tail is figures measured on the
author's *source* canvas rather than a PDF render (18 good figures exceed 600 pt wide; e.g.
`asplos25-067` fig 3 measures 1572 x 613 pt), and the blank-`column` inference (`size.w>=380pt →
double`) funnels every such canvas into the double bucket, inflating its p95 for width (880 pt) and
height (349 pt) alike. The JSON therefore clamps the double-column ceiling to **604.8 pt** (1.2 × 504,
the same bound the architecture rule lands on at its p95 of 602.8 pt) and keeps the raw value as
`raw_p95`. Treat **504 pt** as the constraint and the p75 (535.6 pt) as the outer bound worth quoting.

**Rule (should — height, single-column evidence).** Height is a real, replicated signal: good median
**125.4 pt** vs 112.0 pt for ok+bad within single-column (δ=+0.20, FDR p=9e-5, n=593/211), δ=+0.22
pooled; within double-column the direction is the same (167.6 vs 136.0 pt) but n=29 ok+bad leaves it
non-significant (FDR p=0.18). Taller skews good — consistent with "more drawn structure" from §9 —
so don't fight to compress a walkthrough that needs the room; the p95 (236 pt) is a soft ceiling.

**Aspect ratio: not a signal by the documented bar — with a caveat.** The JSON assigns `info`
because the pooled effect is negligible (δ=-0.11), and that verdict stands. But this is the one
metric where the single-column split alone *does* clear the bar (δ=-0.16 small, FDR p=0.0010, good
median 2.02 vs ok+bad 2.23), with the bad-only contrast agreeing (bad median 2.43, δ=-0.23, FDR
p=0.048). Pooling kills it: single-column figures sit at ~2.0 and double-column at ~3.1, so mixing
them dilutes a within-column difference. The direction is the mirror of the height rule — good
single-column figures are less elongated because they are taller, not because width varies. Treat
aspect as descriptive; the lever is height. As a genre these figures are wider-than-tall:
single-column good median **2.02** vs 1.69 for architecture figures, double-column 3.07 vs 3.01.
**Don't scale height proportionally with width when moving from single- to double-column** — width
roughly doubles (247 → 510 pt) while height grows ~34% (125 → 168 pt).

**Sanity check (visual).** `osdi24-040` fig 3 (good, single, `size.h=524.2 pt`, `size.w=238.9 pt`,
`aspect=0.46`, `density.text=155`) is the tallest single-column good figure with a PDF-extracted
render: five stacked sub-panels (b)–(f), each a `Th 1 / Kernel / State` swimlane timeline for a
different power-failure case, with thick blue bypass arrows, a green `resume` arrow, a red lightning
`crash` marker, circled ①–④ steps and greyed-out not-taken boxes. It is column-height because it is
five frames of the same skeleton — the idiom the height signal picks up — and well past the 236 pt
p95, so treat that ceiling as soft. `nsdi25-040` fig 11 (good, **double**, `circled=12`,
`palette.n=7`) shows the double-column idiom instead: a central two-host mechanism panel of nested
pastel boxes flanked by six key/value cache tables, circled ①②③④ tying each table row to the step
that fills it. Width buys flanking state tables, not a bigger drawing.

---

## 11. Tools

`tool` cross-tab by aesthetic (mechanism figures only, tools with n≥10):

| tool | n | good% | ok+bad% |
|---|---|---|---|
| unknown (metadata didn't match a known tool) | 336 | 67.6% | 31.2% |
| powerpoint | 293 | 77.1% | 20.5% |
| omnigraffle | 102 | 65.7% | 32.4% |
| drawio | 63 | 77.8% | 19.0% |
| tikz | 57 | 70.2% | 10.5% |
| quartz | 41 | 61.0% | 31.7% |
| google-slides | 18 | 88.9% | 11.1% |
| inkscape | 15 | 66.7% | 13.3% |
| chrome | 13 | 92.3% | 7.7% |

(Percentages don't sum to 100 because `discard` rows are excluded from both columns — tikz has 11 of
them, which is why its two columns leave the largest gap.)

**Not a strong rule.** The well-populated tools (n≥40) sit in a 61–78% good-rate band with no clear
winner: powerpoint and drawio lead the big buckets at ~77%, omnigraffle and quartz trail at 61–66%,
and the spread is small relative to the sample sizes. As with architecture figures this most likely
reflects author care rather than tool capability. Venue good-rates range from 50.0% (OSDI24, n=44)
to 88.9% (SOSP24, n=27), larger venues clustered at 65–77%; reported in `venue_by_aesthetic.csv` for
reference, not turned into a rule.

---

## 12. What is specific to mechanism figures

Measured differences between the two kinds, comparing **good-group medians** (mechanism n=713 vs
architecture n=736) unless noted. Descriptions of what the two kinds *are*, not extra rules.

- **Far fewer labelled component boxes.** `density.text_boxes` median **6 vs 21**; ok+bad 4 vs 11.
  Mechanism text lives on edges, in step legends and in annotations rather than inside boxes, so the
  metric also under-reads them (§9).
- **Slightly less text overall, denser per unit area.** `density.text` **38 vs 40.5**, while
  `density.text_per_100pt2` is **10.4 vs 9.6** — the same writing in a smaller figure.
- **Shape count, not label count, leads.** `density.shapes` δ=**+0.39** (*medium*, the strongest
  metric here) vs **+0.26** (*small*) there, medians 126 vs 151; and area-normalised
  `density.shapes_per_100pt2` is a replicated signal here (δ=+0.26) where it failed there (+0.14).
- **Shorter and more elongated.** Single-column height median **125.4 vs 152.6 pt**, single-column
  aspect **2.02 vs 1.69** — a band across the column rather than a square block.
- **A leaner palette.** `palette.n` median **4 vs 6**, hue families **3 vs 4**, much less gray
  (`palette.gray_frac` **0.08 vs 0.17**).
- **More connector segments, fewer arrowheads.** `arrows.lines` **11 vs 10** (a replicated signal
  here, an artifact there) but `arrows.heads` **5 vs 8** and heads-per-line **0.31 vs 0.55** — lanes,
  wires and rulers rather than directed arrows.
- **Step numbering is heavier but no longer discriminating.** `steps.digits` good p95 **36.4 vs
  14.0**, mean **8.2 vs 3.5**, yet δ=+0.08 n.s. here against +0.18 ("should") there; circled markers
  in **5.9% vs 8.7%** of good figures.
- **Corner style flips meaning.** Square is the mechanism default (**51.7% vs 37.0%**) and
  pure-rounded rarer (**17.4% vs 23.4%**), but `corners=mixed` is a replicated signal here
  (**+13.6pp**) where it stayed under the bar there (**+9.0pp**).
- **Dashes matter, but less.** A dashed stroke appears in **51.2% vs 60.2%** of good figures
  (gap +13.7pp vs +16.0pp).
- **Type is identical, weight isn't.** Median label size **6.5 pt in both** (min 5.5, max 8.0 in
  both), but less sans-dominated (**67.0% vs 75.8%** sans, **22.0% vs 17.5%** serif) and much less
  bold (**0.07 vs 0.13**).

---

## Sanity checks performed (visual confirmation)

| # | figure | aesthetic | what the numbers said | what the PNG shows |
|---|---|---|---|---|
| 1 | `asplos25-121` fig 4 | bad | `palette.n=0`, `fill=none`, `text_boxes=0` | Black-on-white carry chain: solid black buffer triangles, D-flip-flop boxes, one thin gray dashed grouping box; no fill colour anywhere |
| 2 | `nsdi26-129` fig 15 | bad | `palette.n=0`, `fill=none` | Outline-only packet-state FSM; unfilled circles, plain labelled transitions; the only colour is in the state-bit text, never a fill |
| 3 | `osdi26-136` fig 7 | good | `fill=none`, `palette.n=0`, `density.text=74`, `shapes=160` | Four-panel automaton construction (DFA → FST → product → NFA), all black-on-white, every edge labelled, a sub-caption per panel — a good figure that breaks §1/§2 |
| 4 | `nsdi25-073` fig 12 | good | at the good medians: `shapes=128`, `text=38`, `text_boxes=19`, `palette.n=7` | Two panels: colour-coded incast timeline with a dashed red callout, plus a two-lifeline sequence diagram with labelled arrows and phase brackets |
| 5 | `osdi25-025` fig 11 | ok | at the ok+bad medians: `shapes=59`, `text=21`, `text_boxes=5` | Competent Normal-vs-Buggy before/after with circled ❶-❹ and a red violation callout — not bad, just sparser; mostly repeated grey document pictograms |
| 6 | `osdi26-100` fig 4 | good | `corners=mixed`, `palette.n=10`, `shapes=127`, dashed | Three shape vocabularies at once: rounded pill nodes, square grid cells, rounded bands of square k-body/load/store cells, linked by dashed zoom lines |
| 7 | `osdi24-040` fig 3 | good | tallest single-column good with a render: `size.h=524 pt`, `aspect=0.46`, `text=155` | Five stacked swimlane-timeline frames (one power-failure case each) with blue bypass / green resume arrows, red crash bolts, circled ①-④, greyed not-taken path |
| 8 | `sosp23-014` fig 1 | good | `circled=16`, `digits=12`, `palette.n=2` | Three before/after frames (redo log / undo log / out-of-place) with index triangle, tuple table, circled steps at the point of action, numbered legend sentence; grey + one red accent |
| 9 | `asplos26-047` fig 7 | good | `arrows.lines=405`, `arrows.heads=0`, `shapes=618` | Three-panel quantum circuit; all 405 "lines" are qubit wires/control lines, zero arrowheads, order carried by a Step 1–8 ruler and pale band highlights |
| 10 | `nsdi25-040` fig 11 | good | double column, `circled=12`, `palette.n=7` | Central two-host stack of nested pastel boxes with packet arrows, flanked by six key/value cache tables cross-linked by circled ①-④ |

All ten match their measured numbers. §1 (`palette.n`), §2 (`fill=none`, including the good
exception), §4 (`corners=mixed`), §5 (what `arrows.lines` actually counts), §7 (markers in a good
*and* an ok figure), §9 (density medians, good vs ok) and §10 (single-column height, double-column
layout) are each directly confirmed by at least one of these.

---

## Quick checklist

**Must (page layout — not a quality signal, just a fit constraint):**
- Figure width fits the column: single ≈240 pt (target 246–253 pt, p25–p75); double ≈504 pt (target
  510–536 pt). Width does **not** predict quality here — the pooled contrast isn't even significant
  (FDR p=0.089). Ignore the JSON's double-column p95 of 880 pt as a ceiling; source-canvas artifact
  (§10).

**Should (real signals that replicate within the single-column split):**
- Draw the mechanism's internal structure: **≥65 drawn shapes (good p25), typically 126** — the
  strongest signal here (δ=+0.39 medium; bad-only median 43) — and it holds per unit area
  (**≥17 shapes / 100 sq-pt**, typically 33).
- Label it: **≥22 text runs (good p25), typically 38**; **≥6 per 100 sq-pt**, typically 10.4. Aim
  for ~6 labelled boxes (good p50) but don't chase it — most mechanism text isn't in boxes (§9).
- Use **≥3 distinct fill colors** (good p25), typically 4, across **≥2 hue families** (typically 3);
  at least a quarter of bad figures use no fill colour at all.
- Use flat fill (88.8% of good); avoid an all-outline/no-fill look as the dominant style (good 3.9%
  vs ok+bad 15.8%, 32.4% of bad) unless the genre demands it, as in automata or circuits.
- Use at least one dashed stroke — a zoom/leader line, a callout box, a not-taken path (good 51.2%
  vs ok+bad 37.5%; monotone at 51/39/27% across good/ok/bad).
- Don't draw everything from one shape vocabulary: `corners=mixed` is a replicated signal (good
  30.7% vs ok+bad 17.1%; 75.7% of bad figures are all-square). Square is still the most common
  single style — the point is encoding something in shape, not rounding corners.
- Give the connective structure room: **≥3 connector segments (good p25), typically 11** lanes /
  wires / edges. Segments, not arrows — arrowhead count is *not* a signal.
- For single-column figures don't fight a taller canvas: good median 125 pt vs 112 pt (δ=+0.20, well
  powered); ~236 pt (p95) is a soft ceiling that real multi-frame walkthroughs exceed.

**Not quality signals at all — don't over-index on these:**
- **Step numbering** (`steps.digits` δ=+0.08 n.s.; circled markers 5.9% vs 2.5% n.s.) — the big
  difference from architecture figures, where numbering *was* a "should". Number a walkthrough when
  the order isn't otherwise clear; it is not a quality checkbox.
- Arrowhead count, heads-per-line (reversed: 0.31 vs 0.50), curved vs straight connectors (median 0
  curved everywhere), curved ratio.
- Stroke width (~0.55 pt median in every group) and number of distinct stroke widths.
- Icons, pictograms and embedded images (median 0 everywhere; direction mildly positive, nowhere
  near significant).
- Font class, boldness and every font size: median 6.5 pt and max 8.0 pt are *identical* between
  good and ok+bad; minimum size is mildly reversed (bad 6.0 vs good 5.5 pt), so small print is a
  symptom of having more to say, not a defect.
- Gray fraction of the palette; `tab10`/`office` named-palette match.
- Aspect ratio as a standalone number — it tracks column (2.02 single, 3.07 double), and the
  within-single-column effect that exists is the height signal seen sideways (§10).
- Drawing tool (61–78% good-rate band across every tool with n≥40).

---

## Figure size table

Recommended targets for a **new** mechanism figure, derived from the good-figure distribution
(p5–p50–p95 unless noted). pt is the unit that matters for drawing at print size; mm/in for
reference.

### Single column (≈240 pt / 84.7 mm / 3.33 in target width, n=593 good)

| | pt | mm | in |
|---|---|---|---|
| width — target | 240 | 84.7 | 3.333 |
| width — typical range (p25–p75) | 246 – 253 | 86.8 – 89.2 | 3.42 – 3.51 |
| width — outer bound (p5–p95) | 223 – 309 | 78.7 – 109.0 | 3.10 – 4.29 |
| height — median | 125 | 44.2 | 1.74 |
| height — typical range (p25–p75) | 98 – 163 | 34.6 – 57.4 | 1.36 – 2.26 |
| height — soft max (p95) | 236 | 83.3 | 3.28 |
| font size — min (p50) | 5.5 | 1.94 | 0.076 |
| font size — median (p50) | 6.5 | 2.29 | 0.090 |
| font size — max, typical (p50) / occasional emphasis (p95) | 8.0 / 12.0 | 2.82 / 4.23 | 0.111 / 0.167 |
| stroke width — median (p50) | 0.54 | 0.19 | 0.008 |
| stroke width — range (p5–p95) | 0.15 – 1.06 | 0.05 – 0.37 | 0.002 – 0.015 |
| distinct stroke widths | 1 – 2 – 4 (p5–p50–p95) | — | — |

### Double column (≈504 pt / 177.8 mm / 7.0 in target width, n=120 good)

| | pt | mm | in |
|---|---|---|---|
| width — target | 504 | 177.8 | 7.000 |
| width — typical range (p25–p75) | 510 – 536 | 179.8 – 188.9 | 7.08 – 7.44 |
| width — outer bound (p5–p75; see §10 on the p95) | 407 – 536 | 143.5 – 188.9 | 5.65 – 7.44 |
| height — median | 168 | 59.1 | 2.33 |
| height — typical range (p25–p75) | 128 – 199 | 45.2 – 70.3 | 1.78 – 2.77 |
| height — soft max (p95) | 349 | 123.3 | 4.85 |
| font size — min (p50) | 5.5 | 1.94 | 0.076 |
| font size — median (p50) | 6.75 | 2.38 | 0.094 |
| font size — max, typical (p50) / occasional emphasis (p95) | 8.75 / 20.1 | 3.09 / 7.08 | 0.122 / 0.279 |
| stroke width — median (p50) | 0.62 | 0.22 | 0.009 |
| stroke width — range (p5–p95) | 0.18 – 1.50 | 0.06 – 0.53 | 0.003 – 0.021 |
| distinct stroke widths | 1 – 2 – 4 (p5–p50–p95) | — | — |

The double-column width p95 (879.6 pt, clamped to 604.8 pt in the JSON) and, less severely, the height
p95 (349.4 pt) are inflated by author-source canvases measured off print scale (§10), so the p75 is
quoted as the outer width bound here. Font size and stroke width barely change between single and double column (median 6.5 vs
6.75 pt, 0.54 vs 0.62 pt) — **don't scale type or line weight with figure width**; only the canvas
grows, and mostly in width (247 → 510 pt) rather than height (125 → 168 pt).

---

## Method notes

- Script: `figgenie-paper-diagram/scripts/distill/style_stats.py --index lab/extracted/corpus_index.csv
  --subtype mechanism --out <dir>` — same script, metric definitions and `--self-test` as the
  architecture document, so the two sets of numbers are directly comparable.
- `mechanism/style-thresholds.json` is generated from the same run's `summary.json` by
  `build_thresholds.py --auto --kind mechanism`, which derives severities from the contrast tables
  with no hand-set overrides; regenerate both after the corpus grows. This document is the editorial
  reading of that JSON, and where the two differ in emphasis (`size.aspect` in §10, `arrows.lines` in §5, `density.shapes` and `density.text_boxes` in §9,
  `palette.n_hues`'s extractor cap in §1) the JSON's severity is authoritative and the caveat is
  marked in the text.
- Multiple-comparison caveat: 29 numeric metrics per column split; FDR controls the expected
  false-discovery rate at 5% across that family, but with n_bad=37 (6 double-column) and n_okbad=29
  in the double-column split, the bad-only diagnostic and every double-column-only result are
  suggestive, not confirmatory.
- Measurement caveat: most figures were extracted from the published PDF and are at print size, but
  a minority carry the author's source-canvas dimensions instead — the >600 pt-wide tail (18 good
  figures), all classified double-column because the blank-`column` inference keys off
  `size.w>=380pt`. §10 and the double-column size table are read with that in mind.
- Figures cited (paper_id + fig number) can be viewed at `lab/extracted/<paper_id>/<stem>.png`, e.g.
  `lab/extracted/osdi24-040/osdi24-040_fig3_p7_vector.png`; author-source figures have no render.
