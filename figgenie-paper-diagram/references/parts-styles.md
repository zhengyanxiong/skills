<!-- Generated from the 272-figure corpus (step 5b review D); numbers from candidates.jsonl. Companion of style-rules.md and encoding.md. -->
# Parts styles — connectors, containers, legends and decorations

Measured style reference for the reusable-parts library. Everything below is measured
from the candidate pool in `step5/candidates/candidates.jsonl`, not estimated.

**Corpus.** 273 architecture figures (type=diagram, subtype=architecture, aesthetic=good)
were parsed; the surviving candidate pool references **270 distinct figures**. Per family:

| family | representative styles | Σ occurrences | figures that use the family |
|---|---:|---:|---:|
| connector-style | 228 | 965 | 245 |
| container-title | 119 | 122 | 77 |
| stacked cards | 89 | 186 | 107 |
| legend blocks | 66 | 116 | 84 |
| cylinder | 23 | 67 | 47 |
| arrowhead | 14 | 183 | 107 |
| step badge | 13 | 61 | 53 |

**Units.** Every length is in **print points** (1 pt = 1/72 in) at the size the figure is
actually printed in a two-column ACM/USENIX paper — i.e. what a reader sees, not the
source SVG's user units. `occurrences` = the number of *distinct figures* in which that
style appears; a style that occurs in 124 figures is used by 45% of the corpus.

**Caveat.** ~13% of container-title records and 4 connector records come from multi-panel
figures whose print scale was mis-inferred (stroke widths of 3–11 pt, 16 pt titles). They
are excluded from every numeric median below (share-of-population percentages still count
them) and are rejected in `review_D.jsonl` as `low-quality`.

---

## 1. Connectors

The single biggest style family (245 of 270 figures). Each record is a real
`(colour, width, dash, cap, head, curvature)` combination sampled from one figure and
redrawn as a 56 pt sample line.

**Population shape** (occurrence-weighted, 224 records / 961 occurrences):

| axis | distribution |
|---|---|
| colour | black 60%, blue 14%, red 11%, grey 9%, green 4%, light grey 2% |
| dash | solid 76%, dashed 20%, dotted 3%, long-dash 1% |
| head on the path | no head 80%, filled head 20% |
| path | straight 70%, curved/orthogonal 30% |
| line cap | butt 86%, round 12%, square 3% |
| stroke width | p10 0.33, p25 0.57, **median 0.72**, p75 0.87, p90 1.28 pt |
| head length | median 4.0 pt = **4.7 × the stroke width** |
| dash on/off | dotted 0.8/0.7 · dashed 2.5/2.0 · long-dash 6.2/3.8 pt |

The "no head 80%" figure is a measurement artefact worth knowing: in PowerPoint, Keynote
and drawio exports the arrowhead is usually a *separate filled polygon* rather than a
marker on the path, so it lands in the arrowhead family (§5) instead. Read it as
"80% of sampled *path* records carry no marker", not "80% of arrows have no head".

### Named variants

| name | colour | width pt | dash pt | cap | head | path | figures | representative |
|---|---|---:|---|---|---|---|---:|---|
| `connector-solid-thin` | `#000000` | 0.72 | – | butt | – | straight | **124** | `asplos25-004_figtex9_91` |
| `connector-solid-medium` | `#191919` | 0.87 | – | butt | – | straight | 62 | `asplos25-002_fig9_94` |
| `connector-solid-thick` | `#000000` | 1.50 | – | butt | – | straight | 8 | `asplos25-096_figtex5_90` |
| `connector-hairline` | `#000000` | 0.22 | – | butt | – | straight | 17 | `asplos25-043_fig5_91` |
| `connector-curved-thin` | `#000000` | 0.44 | – | butt | – | curved | 57 | `asplos25-043_fig5_93` |
| `connector-solid-filled-head` | `#191919` | 0.87 | – | butt | filled, 4.2 pt (4.8×w) | straight | 23 | `asplos25-002_fig9_92` |
| `connector-hairline-filled-head` | `#000000` | 0.28 | – | butt | filled, 2.2 pt (7.9×w) | straight | 36 | `asplos25-041_fig1_90` |
| `connector-curved-filled-head` | `#141414` | 0.57 | – | butt | filled, 5.5 pt | curved | 5 | `asplos25-077_figtex2_91` |
| `connector-open-head` | `#000000` | 0.69 | – | butt | hollow (`fill:#fff`), 8.0 pt | straight | 2 | `nsdi24-043_fig1_91` |
| `connector-dashed-thin` | `#000000` | 0.63 | 2.5, 1.9 | butt | – | straight | 27 | `asplos25-012_fig2_91` |
| `connector-dashed-thick` | `#000000` | 0.95 | 2.8, 3.8 | round | – | straight | 23 | `asplos25-100_fig7_95` |
| `connector-dotted-fine` | `#000000` | 0.33 | 1.3, 1.3 | round | – | straight | 22 | `asplos25-051_fig2_94` |
| `connector-dashed-filled-head` | `#000000` | 0.54 | 3.8, 2.7 | round | filled, 4.5 pt | straight | 3 | `asplos25-031_fig1_92` |
| `connector-grey-thin` | `#868686` | 0.57 | – | butt | – | straight | 24 | `asplos25-002_fig5_90` |
| `connector-grey-dashed` | `#bdbdbd` | 0.72 | 2.2, 0.72 | butt | – | straight | 6 | `asplos26-089_fig6_90` |
| `connector-accent-navy` | `#172c51` | 0.63 | – | butt | – | straight | 20 | `asplos25-100_fig7_92` |
| `connector-accent-red` | `#c00000` | 0.71 | – | butt | – | curved | 5 | `asplos25-109_fig4_92` |
| `connector-accent-green` | `#439922` | 0.69 | – | butt | – | straight | 7 | `asplos25-002_fig5_92` |

Semantic reading of the colour roles as they are actually used in the corpus: **black =
data/primary flow**, **grey = de-emphasised or background link**, **navy/blue = a second
labelled path (control, or a second tenant)**, **red = error / critical / highlighted
path**, **green = success or an alternate data route**. Dashing means "control, optional,
logical or deferred" far more often than it means a second colour role.

Double-headed connectors exist in the corpus but the extractor records only the head at
one end, so no measured double-head variant is offered here; draw one by putting the same
head at both ends of `connector-solid-filled-head`.

### Snippet — the default line and the default arrow

```svg
<!-- connector-solid-thin: the default link -->
<path d="M8 20 H92" fill="none" stroke="#000000" stroke-width="0.72" stroke-linecap="butt"/>

<!-- connector-solid-filled-head: default arrow.
     head length 4.2 = 4.8 x stroke; base 4.85 = 1.155 x length (equilateral) -->
<path d="M8 44 H87.8" fill="none" stroke="#191919" stroke-width="0.87"/>
<path d="M92 44 L87.8 41.58 L87.8 46.42 Z" fill="#191919"/>

<!-- connector-dashed-thin: control / optional flow -->
<path d="M8 68 H92" fill="none" stroke="#000000" stroke-width="0.63" stroke-dasharray="2.5 1.9"/>
```

---

## 2. Container titles

A "container" is the dashed or grey rectangle that groups several boxes and carries a
title on its top edge. 119 style records over 77 figures; each record is a 110 × 34 pt
crop of the container's top edge.

**Population shape.** Shares are over all 119 records; the numeric medians are over the
104 records whose print scale is plausible.

| axis | distribution |
|---|---|
| stroke style | dashed 66%, solid 20%, dotted 10%, long-dash 3% |
| stroke colour | black 50%, grey 27%, blue 16%, red 3%, light grey 3%, green 1% |
| title position | top-centre 48%, top-left 32%, top-right 20% |
| stroke width | **median 0.66 pt** (p25 0.45, p75 0.87) |
| title font size | **median 7.3 pt** (p25 6.0, p75 8.2) |
| corner radius | median 0.70 pt; 56% are effectively square (< 0.8 pt) |
| box size | median 128 × 75 pt |
| fill | `none` in **119 / 119** records — containers are never filled |

The title always sits *on or just inside* the top edge — the extractor only accepts a
title whose top is between 2 pt above the frame and 30% of the frame's height below it, and
every kept candidate lands inside. No candidate puts the title in a tab or clearly above the
frame, and no container in the pool is filled.

### Named variants

| name | stroke | width pt | dash pt | corner r | title | title pt | share of 119 | representative |
|---|---|---:|---|---:|---|---:|---:|---|
| `container-dashed-title-centre` | `#000000` | 0.81 | 3.2, 2.4 | 0.6 | top-centre | 7.5 | **19%** | `nsdi24-029_fig7_10` |
| `container-dashed-title-topleft` | `#000000` | 1.08 | 4.3, 3.3 | 0.8 | top-left | 7.7 | 16% | `osdi23-003_fig4_14` |
| `container-solid-grey-title-centre` | `#7f7f7f`-ish | 0.83 | – | 0.6 | top-centre | 7.6 | 10% | `nsdi23-085_fig8_6` |
| `container-solid-grey-title-topleft` | `#7f7f7f` | 0.50 | – | 1.4 | top-left | 6.0 | 7% | `sosp23-013_fig4_109` |
| `container-dashed-title-topright` | `#000000` | 0.58 | 2.3, 1.7 | 0.4 | top-right | 7.8 | 7% | `nsdi26-082_fig2_20` |
| `container-dashed-blue-title-centre` | blue | 1.04 | 3.1, 1.0 | 2.1 | top-centre | 7.3 | 6% | `nsdi24-043_fig1_7` |
| `container-dotted-title-centre` | `#000000` | 0.58 | 0.58, 0.58 | 1.8 | top-centre | 7.4 | 4% | `asplos25-147_fig2_19` |
| `container-dashed-grey-title-centre` | grey | 1.45 | 1.4, 1.4 | 1.0 | top-centre | 7.6 | 3% | `asplos26-089_fig6_1` |
| `container-dashed-red-title-topright` | `#cc0000` | 0.88 | 2.6, 2.6 | 0.6 | top-right | 7.0 | 2% | `asplos26-132_fig7_16` |
| `container-solid-lightgrey-title-centre` | `#d0cece` | 0.45 | – | 0.3 | top-centre | 8.1 | 1% | `asplos25-151_fig1_4` |
| `container-longdash-title-centre` | `#868686` | 1.03 | 6.2, 4.1 | 0.7 | top-centre | 7.2 | 1% | `asplos25-002_fig5_20` |

Rule of thumb from the medians: **dash length ≈ 4 × stroke width, gap ≈ 3 × stroke width.**

### Snippet — the default container

```svg
<!-- container-dashed-title-centre -->
<rect x="4" y="10" width="137" height="40" rx="0.6"
      fill="none" stroke="#000000" stroke-width="0.81" stroke-dasharray="3.2 2.4"/>
<!-- title baseline ~7pt below the top edge, i.e. inside the frame -->
<text x="72.5" y="17" text-anchor="middle" font-size="7.5"
      font-family="Helvetica, Arial, sans-serif" fill="#000000">Migration</text>
```

(Set `x`/`text-anchor` to `6`/`start` for the top-left variant, `139`/`end` for top-right.)

---

## 3. Legends

66 legend blocks over 84 figures. Legends are small: **median block 37 × 22 pt**, median
**3 items** (44% carry exactly 2). They sit at the **right** of the figure in 37 of 66
cases and along the **bottom** in 29 — never at the top or left.

### Named variants

| name | layout | swatch / key | swatch–label gap | label pt | row/item pitch | representative |
|---|---|---|---|---:|---|---|
| `legend-row-swatch-label` | horizontal, 1 key + label | filled rounded rect 17.3 × 7.7 pt, 0.52 pt outline | ≈ 4 pt | 7.2 | – | `asplos26-008_fig1_3` |
| `legend-row-outline-swatches` | horizontal row of keys | unfilled square 15.4 × 16.1 pt, 0.58 pt stroke | ≈ 3 pt | 7.6 | 90.6 pt between items | `asplos26-088_fig8_11` |
| `legend-column-fills` | vertical column | flat fill 11.9 × 5.7 pt, no stroke | ≈ 3 pt | 4.8 | 15.1 pt | `nsdi26-017_fig5_6` |
| `legend-column-outline` | vertical column | unfilled 11.95 × 5.73 pt, 0.48 pt stroke | ≈ 3 pt | 4.8 | 12.2–15.1 pt | `nsdi26-017_fig5_5` |
| `legend-column-arrows` | vertical, line-style key | 15.2 pt line, 0.57 pt, open head 2.6 pt tall | ≈ 2 pt | 5.2 (bold) | 6.7 pt | `asplos25-031_fig9_17` |
| `legend-markers-circle` | horizontal marker pair | circle ⌀ 13.4 pt, 0.79 pt stroke (one solid, one dashed) | ≈ 3 pt | 7.1 | 5.0 pt between markers | `sosp25-047_fig1_20` |
| `legend-column-icons` | vertical, pictogram keys | icon ≈ 11 pt | ≈ 3 pt | 6.8 | 10.7 pt | `asplos25-138_fig17_6` |
| `legend-mixed-swatch-arrow` | swatch + arrow in one key | 3 × (3.8 × 11.1 pt) cells + two 0.6 pt arrows | ≈ 3 pt | 5.5 | – | `asplos26-129_fig2_10` |

Swatch geometry is consistent across the corpus: colour swatches are **wide rectangles of
roughly 2 : 1**, about 11–17 pt wide and 6–8 pt tall — i.e. one label line tall — and the
label baseline is aligned to the swatch's vertical centre. Label sizes run 4.8–7.6 pt
across the eight blocks; use 5–7 pt. Swatch→label gaps are derived from block widths and
are accurate to ≈ ±1 pt.

### Snippet — the default legend

```svg
<!-- legend-column-fills: two rows, swatch 12 x 6 pt, pitch 15 pt -->
<g font-family="Helvetica, Arial, sans-serif" font-size="4.8" fill="#000000">
  <rect x="0" y="0"  width="11.9" height="5.7" fill="#fcccb2"/>
  <text x="15" y="4.6">Single-GPU</text>
  <rect x="0" y="15" width="11.9" height="5.7" fill="#c5e5e5"/>
  <text x="15" y="19.6">Multi-GPU</text>
</g>
```

---

## 4. Step badges

Circled step numbers ①②③ that key a narrative to the diagram. 13 style records over
**53 figures** — one figure in five uses them.

Two thirds of the badge occurrences are not drawn at all: the two highest-occurrence
records (`osdi26-020_figtex7_3` ×29, `asplos25-002_fig5_4` ×2) are the Unicode glyphs
`②` / `①` typeset as text. The drawn badges split into a filled disc with a reversed
digit and an outlined circle with a black digit.

| name | circle | stroke | digit | digit / ⌀ | figures | representative |
|---|---|---:|---|---:|---:|---|
| `badge-circle-filled` | ⌀ 9.8 pt, fill `#000000` | 0.99 pt `#000000` | white, 9.1 pt | 0.93 | 17 | `osdi26-063_fig8_1` |
| `badge-circle-outline` | ⌀ 11.0 pt, fill `#ffffff` | 0.76 pt `#000000` | black, 9.6 pt | 0.87 | 2 (+3 siblings) | `asplos25-107_fig1_2` |
| `badge-circle-outline` (small) | ⌀ 5.1 pt, fill `#ffffff` | 0.33 pt | black, 3.4 pt | 0.68 | 1 | `osdi25-050_fig6_6` |
| (typeset glyph) | – | – | `②` at ~10 pt | – | 29 | `osdi26-020_figtex7_3` |

Only `osdi25-050_fig6_6` falls on this reviewer's sheets (033–050); the other twelve badge
candidates sit on `sheet_032` and belong to another reviewer's `keep` decisions, so
`badge-circle-filled` is described here but named in their review file, not in
`review_D.jsonl`.

Measured badge diameters run **5.4 – 13.5 pt, median 11.7 pt**; the digit's font size is
**0.85–0.95 × the diameter** (cap height ≈ 0.65 × diameter, so it fills the disc without
touching it). Badges are always circular — no square or rounded-rect step badge appears in
the pool.

### Snippet

```svg
<!-- badge-circle-filled (default) -->
<circle cx="5" cy="5" r="4.9" fill="#000000"/>
<text x="5" y="8.2" text-anchor="middle" font-size="9.1"
      font-family="Helvetica, Arial, sans-serif" fill="#ffffff">2</text>

<!-- badge-circle-outline -->
<circle cx="20" cy="5" r="5.1" fill="#ffffff" stroke="#000000" stroke-width="0.76"/>
<text x="20" y="8.4" text-anchor="middle" font-size="9.6" fill="#000000">1</text>
```

---

## 5. Arrowheads

14 distinct head shapes (deduped orientation-free) over **107 figures**, 183 occurrences.
Two shapes account for 58% of all use.

| name | shape | size (w × h) pt | on stroke | head / stroke | figures (% of 183) | representative |
|---|---|---|---:|---:|---:|---|
| `arrowhead-filled-triangle` | solid equilateral triangle, straight back | 9.97 × 8.63 | 1.00 | 8.6 | **77 (42%)** | `asplos25-110_fig1_11` |
| `arrowhead-barbed-chevron` | triangle with a shallow V notched out of the back (notch = 25% of head length) | 6.20 × 6.20 | 0.88 | 7.0 | 29 (16%) | `asplos26-132_fig6_18` |
| `arrowhead-barbed-sharp` | deep notch, long barbs, very pointed | 6.34 × 6.40 | 0.64 | 10.0 | 20 (11%) | `asplos26-113_fig8_22` |
| `arrowhead-barbed-slim` | barbed but flatter, wider than tall | 5.42 × 3.96 | 1.06 | 5.1 | 4 (2%) | `osdi26-018_fig7_1` |
| `arrowhead-narrow-triangle` | narrow filled triangle | 2.61 × 5.22 | 0.65 | 8.0 | 2 (1%) | `nsdi26-037_fig2_53` |
| `arrowhead-diamond` | filled rhombus terminator | 8.24 × 8.24 | 0.87 | 9.5 | 1 | `asplos25-002_fig9_13` |
| `arrowhead-half` | right triangle / harpoon, one flat side on the line | 3.77 × 1.77 | 0.70 | 5.4 | 1 | `nsdi26-032_fig1_5` |

Across the family the head length is **5–10 × the line's stroke width, median ≈ 4.7×**
when measured on path-attached heads (§1). The default triangle is *equilateral*: base
9.97 pt, height 8.63 pt, apex 60°. An **open (hollow) head** — same outline, `fill:#ffffff`
— exists but only as a path marker; see `connector-open-head`.

### Snippet

```svg
<!-- arrowhead-filled-triangle: tip at (8.63,0), base 9.97, pointing right, for a ~1pt line -->
<path d="M0 -4.99 L8.63 0 L0 4.99 Z" fill="#000000"/>

<!-- arrowhead-barbed-chevron: notch cuts 25% back from the base -->
<path d="M6.2 0 L0 -3.1 L1.55 0 L0 3.1 Z" fill="#000000"/>
```

---

## 6. Cylinders (database / storage drums)

23 candidates were flagged as cylinders, but only **4 are true drums** — the detector also
catches rounded rectangles, and the corpus really does use rounded rectangles for storage
far more than it uses drums. All four true drums are **silhouettes**: a convex top cap,
straight vertical sides and a convex bottom cap, drawn as one closed path. None of them
draws the separate top rim arc that the classic database symbol has; add it if you want the
conventional look.

| name | size pt | aspect w/h | stroke | fill | figures | representative |
|---|---|---:|---|---|---:|---|
| `db-cylinder-filled` | 27.2 × 34.0 | 0.80 | none | `#ffff99` | **13** | `asplos25-046_fig13_2` |
| `db-cylinder-outline` | 60.5 × 76.8 | 0.79 | 0.55 pt `#000000` | none | 1 | `osdi26-053_fig3_6` |
| `db-cylinder-outline-thick` | 28.4 × 22.9 | 1.24 | 0.57 pt `#36393d` | none | 1 | `sosp25-047_fig4_13` |
| `db-cylinder-wide` | 65.5 × 36.8 | 1.78 | 0.82 pt `#d6b656` | none | 1 | `sosp25-032_fig4_5` |

Cap depth is **0.15–0.25 × the width** (the extractor's accepted band is 0.04–0.40 w; a
deeper cap becomes a pill, a shallower one reads as a plain rectangle). Portrait drums sit
near **aspect 0.8**; landscape "registry/catalogue" drums near **1.2–1.8**.

### Snippet

```svg
<!-- db-cylinder-outline: w=28, h=36, cap depth 5.6 (0.2w) -->
<path d="M2 7.6 C2 4.5 8.3 2 16 2 C23.7 2 30 4.5 30 7.6
         V30.4 C30 33.5 23.7 36 16 36 C8.3 36 2 33.5 2 30.4 Z"
      fill="none" stroke="#000000" stroke-width="0.55"/>
<!-- optional classic rim: -->
<path d="M2 7.6 C2 10.7 8.3 13.2 16 13.2 C23.7 13.2 30 10.7 30 7.6"
      fill="none" stroke="#000000" stroke-width="0.55"/>
```

---

## 7. Stacked cards ("N copies")

89 style records over **107 figures**. Card counts, occurrence-weighted:
**3 cards 46%, 2 cards 26%, 5 cards 15%, 4 cards 10%, 7 cards 3%**. Median group size
24.7 × 20.3 pt — stacks are small.

The idiom is always the same: identical cards translated by a small **diagonal** offset.
(`n_cards` in the pool counts drawn paths, so a filled card plus its outline counts as two;
the *cards* column below is the number of cards a reader sees.)
The measured offsets cluster at **2–7 pt, most commonly ≈ 2 pt for deep stacks and
4–7 pt for two-card stacks**; the extractor only accepts offsets in the 1.5–8 pt band, and
the whole corpus stays inside it.

| name | cards | card size pt | offset pt | fill | stroke | figures | representative |
|---|---:|---|---|---|---|---:|---|
| `stacked-cards-2-rounded-filled` | 2 | 74 × 24 (rounded) | 3.9 up-left | `#2e75b6` | inner white 0.42 pt | **39** | `nsdi26-017_fig2_12` |
| `stacked-cards-3-filled-shadow` | 3 | 72 × 71 | 5.6 × 5.8 down-right | `#eeeeee` | hairline `#595959` | 14 | `osdi24-050_fig6_8` |
| `stacked-cards-4-outlined-grey` | 4 | 79 × 65 | 2.6 × 3.8 | `#e7e6e6` | 0.32 pt black | 12 | `nsdi26-087_fig3_1` |
| `stacked-cards-accent-front` | 5 | 53 × 32 | 2.5 × 2.1 | `#fce5cd` | front 1.12 pt `#ff0000`, back 0.28 pt black | 11 | `sosp23-015_fig1_8` |
| `stacked-cards-5-filled` | 5 | 34.6 × 60.3 | 2.9 × 2.6 | `#cfe2f3` | 0.64 pt black | 7 | `osdi26-065_fig2_5` |
| `stacked-cards-2-rounded-outline` | 2 | 44 × 25 (rounded) | 4.2 up-right | `#e3f2d9` | `#588e32` | 5 | `asplos26-139_fig7_1` |
| `stacked-cards-2-outline` | 2 | 66.7 × 55.4 | 7.2 × 6.8 up-left | none | 0.61 pt black | 2 | `asplos25-101_fig5_8` |
| `stacked-cards-many-thin` | 7 | 46.4 × 16.9 | 2.1 × 2.2 | `#d8f3dc` | 0.61 pt black | 2 | `asplos26-088_fig13_6` |
| `stacked-cards-4-outline-heavy` | 4 | 27.7 × 27.7 | 1.9 × 1.9 | `#ffffff` | 0.58 pt black | 1 | `asplos26-088_fig14_4` |
| `stacked-cards-diagonal-fade` | 4 | 9.9 × 10.2 | 6.5 diagonal step | `#4472c4`, falling opacity | none | 1 | `asplos25-148_fig5_2` |

Two idioms hide in this table. The first eight are *piles* — the offset is smaller than the
card, so the copies read as "more of the same thing". `stacked-cards-diagonal-fade` is a
*sequence* — the step is comparable to the card size, so it reads as "over time / one after
another". Do not mix them.

### Snippet

```svg
<!-- stacked-cards-3-filled-shadow: back copies first, front card last -->
<g stroke="#595959" stroke-width="0.32">
  <rect x="11.2" y="11.6" width="72" height="71" fill="#eeeeee"/>
  <rect x="5.6"  y="5.8"  width="72" height="71" fill="#eeeeee"/>
  <rect x="0"    y="0"    width="72" height="71" fill="#eeeeee"/>
</g>
```

---

## 8. Defaults

When nothing else is specified, use these. Every choice is the most frequent variant in
its family (ties broken by legibility at 8 pt figure scale).

| element | default variant | key numbers | why |
|---|---|---|---|
| link between boxes | `connector-solid-thin` | `#000000`, 0.72 pt, butt, no dash | used in 124 / 270 figures (46%) — twice the next style |
| directed arrow | `connector-solid-filled-head` + `arrowhead-filled-triangle` | 0.87 pt line, head 4.2 pt ≈ 4.8 × stroke | commonest head (42% of heads) on the commonest weight |
| secondary / background link | `connector-grey-thin` | `#868686`, 0.57 pt | grey is 9% of connector use, all of it de-emphasis |
| control / optional link | `connector-dashed-thin` | 0.63 pt, dash 2.5 / 1.9 | dashed is 20% of connector use; this is its median form |
| accent link | `connector-accent-navy` | `#172c51`, 0.63 pt | most common non-black colour (20 figures) |
| group frame | `container-dashed-title-centre` | 0.81 pt black, dash 3.2 / 2.4, r 0.6 pt, `fill:none` | largest single container group (19% of 119); dashed is 66% overall |
| container title | 7.3 pt, top-centre, inside the frame | – | medians of the plausible-scale population |
| legend | `legend-column-fills`, placed right of the figure | swatch 12 × 6 pt, pitch 15 pt, label 5–7 pt | "right" beats "bottom" 37 : 29; column beats row |
| step badge | `badge-circle-filled` | ⌀ 11.7 pt (median), digit 0.9 × ⌀, white on black | 17 figures drawn + 29 more typeset as `②` |
| arrowhead | `arrowhead-filled-triangle` | equilateral, length 8.6 pt ≈ 8.6 × stroke | 42% of all heads |
| storage symbol | `db-cylinder-filled` | aspect 0.80, cap depth 0.2 w, flat fill, no stroke | 13 figures — the only cylinder with real reuse |
| "N copies" | `stacked-cards-3-filled-shadow` | 3 cards, offset ≈ 5.5 pt down-right, hairline outline | 3 cards is 46% of stack use; the shadow form reads at small size |
| stroke width, anything | 0.72 pt | median across 961 connector occurrences | – |
| body text in a part | 7.3 pt | median container title size | – |

## 9. Mechanism figures — the parts they add

The defaults in §8 (line, arrow, container, legend, badge, cylinder, ×N stack) apply unchanged to mechanism
figures. What those figures add is a set of *narrative* parts — devices that say "this changed", "this is
old", "this is wrong", "read in this order" — cut from 705 mechanism figures into `assets/symbols/`
(`subtype: "mechanism"`, 2,261 parts in 155 families under 11 themes; browse `catalog-mech-<theme>.png`,
search `index.json` by `family`, `theme`, `figure_kinds`, `depicts`; the last column names real families
with their part counts). Frequencies below are over the 152 mechanism semantic records; `references/mechanism/encoding.md` says when each device is the right one.

| device | what it says | how it is drawn by default | theme / families to look in |
|---|---|---|---|
| changed element | "this is the difference" (53 %) | same shape as its neighbours, the one saturated fill or a 1.2–1.5 pt stroke; nothing else changes | `frames-change` → `delta-highlight` (39) |
| ghost | "this was here / is gone / is pending" | the element redrawn in `#d9d9d9` dashed 0.5 pt, no fill, same size and place | `frames-change` → `ghost-copy` (23), `dashed-placeholder-slot` (7) |
| strike / cross | "wrong, removed, failed" | a red (`#b85450`) × or a diagonal 0.8 pt stroke over the element; never the only marking of a *state* | `frames-change` → `strike-removed` (11); `annotations` → `error-event-mark` (9) |
| verdict glyph | "✓ this one / ✗ not that" under a panel (42 % of recorded panels carry a verdict) | 8–10 pt ✓ / ✗ in green / red, or a bold one-word line at the same y in every panel | `annotations` → `check-cross` (53); `frames-change` → `compare-marker` (24) |
| badge | a role or a status pinned to an element (7 %) | a 8–12 pt circle or pill at the element's corner: lock, bolt, crown, digit | `annotations` → `access-badge-marker` (8); `containers` → `labelled-container-with-badge` (17); `icons` → `misc-icon` |
| step marker | reading order along a path | circled numbers ⌀ 8–12 pt (20 %), plain digits (7 %) or letters (7 %) at the arrow's upper-left; one style per figure | `steps-traces` → `step-badge` (48), `step-arrow-label` (47), `trace-path` (30) |
| frame divider | "then" between frames | 8–12 pt gap, a pale chevron or block arrow between frames, or nothing when frames are labelled t₀ / t₁ | `frames-change` → `frame-arrow` (45), `frame-border` (18) |
| panel tag | which alternative / moment | (a) (b) 7.5 pt bold top-left inside the panel, or a name; one convention per figure | `annotations` → `panel-label` (14); `frames-change` → `frame-border` |
| lifeline / ruler | an actor over time; the time axis | a 0.5 pt vertical (or horizontal) line per actor with its name at the head; a ruler with tick labels when times matter | `logic-time` → `lane-divider` (23), `timeline-axis` (12), `time-span` (34), `message-arrow` (27) |
| slot row / cell grid | a data structure at one moment | equal cells 10–14 pt, 0.5 pt strokes, occupied cells filled, the addressed cell accented | `structures` → `slot-array` (134), `matrix-cells` (73), `pointer-cursor` (32), `hash-bucket` (8), `list-node` (6) |
| guard label | the condition on a transition | 6–6.5 pt italic beside the edge, near its tail; every branch of a decision gets one (85 % of transitions do) | `logic-time` → `guarded-edge` (41), `state-node` (50), `decision-diamond` (34) |
| value cell | a number the reader checks | monospace or the label font at 6.5 pt inside its cell; one colour per recurring value; results as "= result" | `math-code` → `block-matrix-equation` (19), `formula-callout` (31); `structures` → `matrix-cells` |

None of these is required: a comparison can live on a shared start and three labelled arrows without any panel
tag, a walkthrough can trace its path with a single bold wavy line instead of numbers. Use the device the story
needs, draw it in the same line weight as the rest, and keep one meaning per device within a figure.

## 10. AI-venue figures — the parts they add

The defaults of §8 hold for the AI family too (line, arrow, container, legend, badge, cylinder, ×N stack), with three
shifts the corpus makes: lighter strokes (median 0.47 pt), pale Office tints for modules and regions instead of grey
scaffolding, and letters (a) (b) on panels rather than circled step numbers (`references/ai/style-rules.md`). What the
family adds is the stock drawn forms of AI papers and the devices around samples, cut from 271 Figure 1s into
`assets/symbols/` (`subtype: "ai"`, 998 parts in 183 families under 9 themes; browse `catalog-ai-<theme>.png`, search
`index.json` by `family` / `by_family_ai`, `domain`, `tags`, `depicts`; `placeholders` says how many bitmaps of the
source became grey slots). Frequencies are over the 336 AI semantic records; `references/ai/encoding.md` says when each
device is the right one.

| form or device | what it says | how it is drawn by default | theme / families to look in |
|---|---|---|---|
| the model | an LLM, a network, an encoder | a rounded box named for the model (29% of records), a trapezoid for an encoder / decoder (6%; anatomy 17%), a layer stack (6%); a robot or brain icon only where the figure is about actors (robot 11%) | `things-models` → `llm` (20), `trapezoid-module`, `transformer-block` (14), `model-pictogram` |
| a block opened up | attention, feed-forward, a LoRA branch, a codebook | the standard sub-blocks stacked with `×N`, residual lines around them; the paper's change the one coloured block | `things-models` → `transformer-block`, `lora-adapter`, `vae-codebook`, `unet`, `skip-connection`, `attention` |
| tokens, embeddings, patches | a sequence or a vector | a strip of small equal cells (20% of records; anatomy 50%), coloured by role or type, an ellipsis for the rest | `things-data` → `token-strip` (35), `vector-cells` (15), `vit-patchify`, `matrix-cell-grid` |
| a sample | the input, the output, a data item | a picture at its own aspect in a thin frame (`image.role`), a quoted text card of two or three lines, a film strip of frames, stacked cards for a batch | `things-data` → `filmstrip`, `stacked-cards`, `dataset-card`, `benchmark-card` (16), `masked-input`; a `text` node |
| a message | what an actor says or thinks | a speech or thought bubble with a short text, its tail to the actor (10% of records; agents 30%) | `things-agents` → `chat-bubbles` (16), `thought-bubble`, `typed-trace-blocks` |
| an actor | a user, an agent, a tool, the environment | an icon at label size (8-12 pt) in one style, next to its name; a role tint behind its lane; a grey slot where the paper's logo goes | `things-agents` → `agent-loop` (11), `tool-use`, `memory-store`, `gui-screen`, `rl-loop` |
| training state | trained against frozen | a snowflake and a flame glyph at the box's corner (6%), a padlock (1%), or the palette's two state colours; a key either way | `devices-marks` → `frozen-trainable`, `module-state-coding` |
| a verdict | right against wrong, ours against theirs | a green tick and a red cross (15%) at the lane's end, a one-word label; never colour alone | `devices-marks` → `verdict-marks` (12), `error-callouts` |
| a zoom | the part opened up | a wedge or two leader lines from the small box to the enlarged one (19%), the enlarged one framed; or a lettered sub-panel named in the main drawing | `devices-layout` → `zoom-callout` (15), `new:dashed-group-boxes` |
| a title or a claim | the figure's own headline | a bold line set into the figure, a pill or tab title on a panel (6%; scope overviews 19%) | `devices-titles-notes` → `frame-border-titles`, `pill-title-headers`, `tab-titled-panels`, `claim-banner` |
| a hand-over | from one stage or panel to the next | a block arrow (12%; a third of the records tag it) or a plain arrow between bands, colour-coded by flow kind (33%) | `devices-arrows-colour` → `block-arrows` (27), `flow-type-arrows` (24), `colour-coded-groups` (20) |
| a region | a stage, a role, a panel | a pale tint (`#f2f2f2`, `#fff2cc`, `#fbe3d6`, `#d9f2d0`, `#deebf7`; lightness ≈ 0.9) with a title, framed or not | `devices-layout` → `option-catalog`, `notation-key`; `references/ai/palettes.md` §7 |

None of these is required. A part is copied as the inner `<g>`, recoloured by role, and sized to the figure's own line
weight; a bitmap the part replaced with a grey slot is the paper's to supply (`image` node) or stays a slot.
