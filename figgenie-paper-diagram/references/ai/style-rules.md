# Style rules for AI-venue figures (family `ai`): what the corpus does, with how often

The counterpart of `../style-rules.md` for the Figure 1s of ICLR, ICML, NeurIPS, CVPR, ACL and AAAI (2023-2026).
Everything here is a description with a frequency; a figure drawn against a number below is a choice to make
knowingly, not a fault. The only rules that bind are print physics: the figure fits the venue's text width, type stays
at 6 pt or above, contrast is readable, nothing leaves the canvas.

## How to read this

- **Units.** pt at print size, measured on the Figure 1 extracted from the published PDF (1 pt = 0.3528 mm). The
  venues differ: NeurIPS and ICLR are single-column templates with a 396 pt text width; ICML (486), CVPR (495), ACL
  (454) and AAAI (504) are two-column templates whose Figure 1 almost always spans both columns. So "full width" is
  396-504 pt depending on the venue, and "a column" is 219-239 pt and exists only in the two-column venues.
- **Corpus.** 3,274 designed Figure 1s (one per paper; plots, tables and photo collages left out) carry the labels of
  a first pass over every figure; 2,470 of them have a vector Figure 1 that matches the published figure and were
  measured on the SVG. The user rated 1,158 figures: good 906, ok 197, bad 28, discard 27; of the measured figures
  good 844, ok 184, bad 32. The deep semantic records (336 figures) are a third source, quoted as *records*.
- **Contrast.** Good against ok + bad (844 vs 216 measured, 878 vs 215 labelled). Effect size is Cliff's delta
  (|δ| < 0.147 negligible, < 0.33 small, < 0.474 medium); significance a Mann-Whitney U or two-proportion test with
  Benjamini-Hochberg q within the table. Every effect in this family is small: the ratings separate a fuller, more
  worked figure from a plainer one, not two styles.
- **Severity.** **must** = page fit. **should** = a real contrast (|δ| ≥ 0.147 or a share difference ≥ 10 points, q <
  0.05); a default to deviate from with a reason. **not a signal** = good and weaker figures look alike, said so that
  it is not mistaken for an oversight. The machine-readable version is `style-thresholds.json` (bands, by kind, the
  lint parameters that differ from the systems family).
- **Two views.** Each table gives the family and the kinds; the sub-field columns are in §12 and in `domains.md`. Read
  the family and the field together; neither filters the other.
- **Headline.** Good AI-venue figures are *fuller*: full text width (89% vs 78%), more text (69 vs 42 runs), more
  shapes (204 vs 114), more colours (9 vs 6), more arrowheads (7 vs 3), dashed strokes (60% vs 40%), formulas (46% vs
  32%), a legend (30% vs 20%), frozen / trainable marks (8% vs 2%), labelled dense in 57% vs 31%. They are not cleaner,
  and they pay for density in type size: the smallest type is 4.5 pt (vs 5.0), which the skill does not copy (§8).
  The weaker figures are the sparse ones (17% vs 6%), the partial-width ones (13% vs 4%), the one- or two-hue ones
  (16% vs 8%), chat transcripts drawn as the whole figure (7% vs 2%) and tables drawn as figures.

## 1. Colours

- Distinct fill colours: good median 9 (p25 6, p75 14, p95 27) against 6 for the rest (δ +0.30) — **should** have at
  least 6. By kind: anatomy 12, scope overview and mosaic 11, pipeline 9, contrast 8, concept 7, walkthrough 6.
- Hue families among the largest fills: good median 4 (the measure's cap) against 3 (δ +0.17); the pre-screen counts
  3-5 hues in 62% of figures, 6 or more in 30% (good 33%), 1-2 in 8% (good 8%, weaker 16%) — **should** use three or
  more hue families; one accent among greys is the systems look, not this family's.
- Grey share of the fill area: median 14%; not a signal.
- Tone by area (`palettes.md` §0): pale fields in 52% of figures, strong in 26%, no colour field in 14%; the largest
  hue is blue in 33%, orange 25%, green 16%, teal 9%, red 7%.
- Office theme colours (the PowerPoint defaults) are recognisable in 9% of good figures and 4% of the rest; 42% of the
  good figures were drawn in PowerPoint.
- Red: used in 25% of figures; across the records its most common meaning is a verdict (wrong, failure), then
  highlight; `encoding.md` §1.

## 2. Fill

- Flat fills in 91% of good figures; hatching in 7% (anatomy 14%, ml-core and science 13%: masked or frozen parts,
  padding); gradients are rare and count against the figure in the records.
- Ground (pre-screen): white 61%, tinted regions 33% (agents 51%, mosaic 50%, scope 49%), grey panels 6%; not a
  signal (good 59 / 34 / 6%). Parts are set apart by tinted regions (60% of the records), framed boxes (59%), dashed
  boxes (45%) and white space (41%), usually two or three of these at once (`palettes.md` §2).

## 3. Strokes & dashes

- Median stroke 0.47 pt (p25 0.30, p75 0.66); lighter than the systems family's 0.55. Not a signal.
- Distinct stroke widths: good median 3 (p75 4) against 2; negligible effect. Two or three widths (box outline, arrow,
  emphasis) are the norm.
- At least one dashed stroke in 60% of good figures against 40% (**should**); in the records a dashed box groups parts
  or marks a scope in 42%, a dashed rule divides panels or halves in 17%, and a dashed arrow is a secondary flow
  (optional, feedback, gradient, training-only) in 9%.

## 4. Corners

- Mixed square and rounded in 42% of good figures (30% of the rest), rounded 41%, square 17% (26% of the rest):
  rounded modules with square panels and cards is the usual mix (**should**, a small signal).

## 5. Arrows & connectors

- Arrowheads: good median 7 (p75 17); anatomy 16, actors 8.5, pipeline and contrast 7, walkthrough 3.5, concept and
  mosaic 3, scope 2. Lines: median 9. Both grow with the content, not a target of their own.
- Curved connectors: median 0 at any rating; loops and rings are drawn with arcs in agent and RL figures (`layouts.md`
  §7).
- In the records, arrow colour says what kind of flow it is in 33%, the main flow is the solid one in 28%, line weight
  separates main from minor in 21%, curved arrows mark feedback or iteration in 17%, block arrows (hollow or fat) hand
  over between stages or panels in 12% (tagged on about a third of the records); `encoding.md` §2.

## 6. Icons, pictures, samples

This is where the family differs most from systems figures, which carry almost no pictures.

- Pictures (the pre-screen counts separate tiles): none in 47%, 1-2 in 12%, 3-5 in 15%, six or more in 26%. Roles:
  sample inputs and outputs 34%, data thumbnails 10%, rendered results 7%. Area: small in 35%, medium in 15%. Measured
  raster images: good median 8 (p25 3, p75 18), covering 10% of the canvas (p75 25%); scope overview 18 / 24%, mosaic
  21 / 27%, anatomy 5 / 6%. Good figures have slightly more images (δ +0.16) and the same area; the signal is the
  content, not the pictures.
- Icons: none in 46%, few 23%, many 30% (agents 75%, actor interaction 83%, scope and mosaic 49%); flat-colour icons
  29%, line art 12%, mixed styles 8% (good 11%, a small signal: a pasted icon set next to drawn ones is normal), emoji
  5%. *Records:* icons are bitmaps in 61% of the figures that have them; logo style 15%, cartoon 12%.
- Speech or thought bubbles in 25% (walkthrough 50%, actors 47%, scope 45%, llm-nlp 43%, multimodal and agents 55%);
  not a signal.
- A logo, wordmark or mascot (the model's, the paper's, a vendor's) appears in 8% of the figures (brand logos 4%,
  mascots 3%, the paper's own wordmark 1%); it is the paper's own material, never the library's (the parts keep grey
  slots for them).
- Bitmaps in the drawn figure follow the shared rule (SKILL.md "Bitmaps"): a local PNG / JPEG at ≥ 150 ppi (300 for
  photos), at its own aspect ratio, inlined at delivery. *Records:* 64% of the pictures are bitmaps; a vector-drawn
  sample (a token strip, a molecule, a waveform) is the other 36%.

## 7. Step and panel markers, legend, zoom

- Step markers (pre-screen): none 60% (good 55%, weaker 66%), letters heading panels 22% (good 23%, weaker 15% —
  **should**, when the figure has panels), plain numbers 10%, labelled arrows 5%, circled numbers 4%. Circled
  numbers, the systems habit, are almost absent here (98% of measured figures have none); letters (a), (b) are the
  norm for panels and plain digits for steps along a pipeline (20%) or a walkthrough (23%).
- Legend in 30% (good 30%, weaker 20% — a small signal): anatomy 39%, mosaic 36%; direct labels replace it in the rest.
- Zoom call-outs: 19% of the records (a wedge 7%, leader lines 7%, a title only 2%; anatomy 37%); `layouts.md` §5.
- Frozen / trainable marks (snowflake and fire, a padlock) in 9% of all figures, 17% of anatomy, 27% of audio; good 8%
  against 2% (**should** mark the state when training state is the point).

## 8. Fonts & sizes

- Type class (measured): sans 49% of good figures, serif 34% (anatomy 43%, vision 48%, generative 44%), mixed 12%,
  mono 3%; the pre-screen sees serif labels in 44%. Not a signal; follow the paper's own type.
- Sizes: median label 6.0 pt (p5 4.0, p95 9.0); the smallest type 4.5 pt (p25 3.5, p75 5.5); the largest 9 pt (p95
  16: titles set into the figure). Bold runs 19%.
- The reversed signal: good figures use smaller minimum type (4.5 vs 5.0, δ -0.22), because they are denser, and 72%
  of the deep records name small type as a weakness of the good figure they describe. The skill keeps its floor — 6 pt
  for labels, 5 pt for badge digits — and reaches the density of good figures by other means: the full text width,
  short labels, a sample in place of a sentence, one legend instead of repeated captions (`anti-patterns.md` §4).
- Formulas in 50% of figures (anatomy 78%, concept 64%, ml-core 75%; scope 7%); good 46% against 32% (**should**, when
  the paper's symbols name the parts).

## 9. Density

- Text runs: good median 69 (p25 40, p75 115) against 42 (δ +0.30, the strongest signal with shapes); shapes 204
  (p25 95, p75 416) against 114; labelled boxes 14 (p25 5, p75 28) against 8; 7.6 text runs and 23.6 shapes per 100
  pt². Labelled density: dense 57% of good against 31%, sparse 6% against 17%.
- By kind (good medians): text boxes concept 4, contrast and walkthrough 12, pipeline 15, anatomy 17, actors 18.5,
  mosaic 22, scope 24; text runs concept 57, actors 58, contrast 60, anatomy 70, pipeline 74, walkthrough 76, mosaic
  91, scope 96.
- *Records:* 13 elements (p25 11, p75 16) and 9 relations in the median figure; two thirds carry a worked example
  with real values.
- Budgets for the lint (`style-thresholds.json` `lint.node_budget`): the q3 / p90 of labelled boxes per kind (pipeline
  28 / 58, anatomy 31 / 56, contrast 26 / 59, walkthrough 24 / 68, concept 13 / 31, scope 34 / 85, actors 29 / 42,
  mosaic 32 / 70). A figure above its kind's p90 is asked whether it can merge, elide (xN, an ellipsis) or split.

## 10. Size by venue

- Width: 89% of good figures span the full text width (78% of the rest), 7% one column (ml-core 15%, concept 18%),
  4% something in between (13% of the rest — a figure that neither fills the width nor sits in a column is the
  weaker look). Width as a share of the text width: median 1.01 (p25 1.01, p75 1.04).
- Height: median 198 pt (p5 126, p25 164, p75 240, p95 317); by kind scope 242, mosaic 227, anatomy 209, pipeline
  202, walkthrough 195, contrast 186, actors 187, concept 168. Aspect 2.24 (p25 1.8, p75 2.7). Height carries no
  signal (δ +0.11).
- Measured width by sub-field (medians, pt): vision 501, generative 493, agents and audio 462, multimodal 461,
  llm-nlp 460, science 432, rl-robotics 407, ml-core 406 — the venues' mix, not a style.
- The bands the lint uses (`style-thresholds.json` `columns[venue]`): full width (`meta.column: double`) 0.85-1.08 ×
  the text width, target the text width; a column (`single`, two-column venues only) 0.40-0.62 × the text width,
  target 234 (ICML), 237 (CVPR), 219 (ACL), 239 (AAAI).

| venue | template | text width | column | good figures full / column |
|---|---|---:|---:|---|
| NeurIPS | single column | 396 | — | all full |
| ICLR | single column | 396 | — | all full |
| ICML | two columns | 486 | 234 | about 3 in 4 full |
| CVPR | two columns | 495 | 237 | almost all full |
| ACL | two columns | 454 | 219 | almost all full |
| AAAI | two columns | 504 | 239 | almost all full |

## 11. Tools

PowerPoint drew 42% of the good figures (good rate 88%, the highest of the common tools), Google Slides 5% (86%),
Keynote 5% (76%), WPS 4% (76%), draw.io 7% (75%), Quartz / macOS apps 7% (74%), Inkscape 2% (75%), TikZ 5% (66%),
Illustrator 3% (68%), OmniGraffle 1% (50%), Visio 2% (95%, 20 figures). The slide tools' habits are the family's
habits: Office tints, rounded modules, flat icons, pasted samples.

## 12. By sub-field (corpus shares, pre-screen; measured medians of the good figures)

| | family | llm-nlp | ml-core | vision | multimodal | science | rl-robotics | generative | agents | audio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| no pictures / six or more | 47 / 26% | 92 / 1% | 68 / 13% | 9 / 56% | 11 / 37% | 48 / 22% | 30 / 36% | 17 / 57% | 61 / 14% | 42 / 17% |
| pictures as sample i/o | 34% | 2% | 17% | 68% | 64% | 32% | 36% | 49% | 13% | 53% |
| many icons | 30% | 42% | 18% | 12% | 40% | 22% | 35% | 25% | 75% | 25% |
| bubbles | 25% | 43% | 3% | 9% | 55% | 5% | 15% | 21% | 55% | 12% |
| formulas | 50% | 44% | 75% | 51% | 27% | 60% | 56% | 57% | 19% | 49% |
| serif labels | 44% | 35% | 55% | 53% | 39% | 45% | 42% | 49% | 27% | 46% |
| six or more hues | 30% | 24% | 20% | 34% | 37% | 35% | 32% | 33% | 36% | 29% |
| tinted regions as ground | 33% | 29% | 27% | 35% | 39% | 27% | 30% | 39% | 51% | 29% |
| legend | 30% | 23% | 33% | 38% | 31% | 32% | 25% | 26% | 20% | 34% |
| frozen / trainable marks | 9% | 7% | 4% | 15% | 16% | 8% | 4% | 10% | 1% | 27% |
| built as boxes and arrows | 58% | 63% | 59% | 59% | 44% | 66% | 56% | 52% | 54% | 86% |
| reads left to right | 54% | 52% | 59% | 66% | 44% | 58% | 48% | 56% | 36% | 42% |
| letters head the panels | 22% | 14% | 18% | 31% | 24% | 30% | 20% | 23% | 12% | 19% |
| labelled dense | 52% | 47% | 40% | 57% | 63% | 59% | 42% | 55% | 55% | 54% |
| good figures measured | 844 | 171 | 86 | 84 | 122 | 84 | 64 | 41 | 55 | 43 |
| distinct fills | 9 | 8 | 7 | 10.5 | 9 | 11 | 10.5 | 10 | 12 | 9 |
| raster images / canvas share | 8 / 10% | 5 / 4% | 3.5 / 4% | 11 / 17% | 12 / 15% | 7.5 / 8% | 10 / 15% | 17 / 27% | 14 / 15% | 5 / 6% |
| text runs / text boxes | 69 / 14 | 71 / 14 | 60 / 7 | 52 / 11 | 85 / 18 | 78 / 12.5 | 60 / 13.5 | 73 / 11 | 73 / 26 | 65 / 18 |
| arrowheads | 7 | 7 | 6 | 11.5 | 4 | 10 | 7 | 8 | 5 | 15 |
| median stroke, pt | 0.47 | 0.50 | 0.38 | 0.46 | 0.48 | 0.43 | 0.51 | 0.44 | 0.50 | 0.55 |
| width x height, pt | 460 x 198 | 460 x 195 | 406 x 173 | 501 x 198 | 461 x 214 | 432 x 197 | 407 x 201 | 493 x 220 | 462 x 212 | 462 x 200 |

What each field does differently from the family, with the parts and exemplars it supplied, is in `domains.md`.

## 13. What is specific to this family (against the systems family)

- Content beyond boxes and arrows: samples, pictures, worked instances, icons, bubbles and small charts are part of
  53% of the figures; the brief asks for the paper's own material (its samples, screenshots, real numbers, logos) and
  the spec carries them as `image`, `text`, `bubble` and `chart` nodes (`../spec-guide.md` §9).
- Full width by default (`meta.column: double`, 89%) rather than a single column; the width is the venue's text width.
- Letters head panels; circled step numbers are rare (4%); plain digits mark steps along a chain.
- More colours and hues, tinted regions in a third, flat-colour icons; a legend only when categories need one.
- Formulas in half the figures; serif type in a third (the paper's own symbols and faces).
- Frozen / trainable state as snowflake and fire or a colour key where training state is the point.
- Many figures have two or three kinds at once; the spec lists them all and the budget follows the primary one.

## Quick checklist

**Must (page fit):** width inside the venue's band (full text width, or one column of a two-column venue); type ≥ 6 pt
(badge digits ≥ 5 pt); contrast readable; nothing outside the canvas; bitmaps local, ≥ 150 ppi, at their own aspect.

**Should (real signals, small effects; deviate with a reason):**
- Fill the text width (89% of good figures); a figure between a column and the full width is the weaker look.
- Six or more distinct fill colours and three or more hue families; one or two hues reads as unfinished here.
- Let the content be as full as the kind usually is (text boxes by kind in §9); sparse figures are the weaker ones.
- At least one dashed stroke with one meaning (a group, a scope, a secondary flow).
- Letters on panels; a legend when categories carry meaning; frozen / trainable marks when training state matters.
- Formulas where the paper's symbols name the parts (half the corpus).
- Mixed corners: rounded modules, square panels and cards.

**Not signals — do not over-index:** stroke width, number of stroke widths, curved connectors, sans vs serif, bold
share, largest type, picture area, icon count, grey share, legend placement, drawing tool.

**Reversed signal — do not copy:** good figures use smaller minimum type (4.5 pt); keep the 6 pt floor and earn density
with width, short labels and samples.

## Figure size table (good figures, p5 / p50 / p95)

| | full width | one column (two-column venues) |
|---|---|---|
| width, pt | the venue's text width (396 / 454 / 486 / 495 / 504); measured 402 / 460 / 548 across venues | 219-239 by venue; measured p5 242 |
| height, pt | 126 / 198 / 317 | the same bands (too few figures to split) |
| aspect | 1.2 / 2.2 / 3.5 | — |
| label size, pt | 4.0 / 6.0 / 9.0 (skill floor 6) | — |
| median stroke, pt | 0.0 / 0.47 / 1.0 | — |
| distinct fills | 2 / 9 / 27 | — |
| text runs | 13 / 69 / 230 | — |
| labelled boxes | 0 / 14 / 57 | — |

## Method notes

Measured metrics come from `svg_digest` over the extracted Figure 1 of each paper (`ai_style_stats.py`; the systems
family's metric definitions, `../style-rules.md` "Method notes"); labelled attributes from the pre-screen pass over the
gallery picture of every figure (`prescreen_v2.jsonl`), checked against the full figure for the 336 deep records. Per
kind and per sub-field tables use the figure's primary kind and primary field. The rated subset is stratified, not
proportional (small kinds, small fields and award papers were over-sampled), so frequencies are always taken over the
whole corpus and the ratings are used only for the good-vs-weaker contrast. Source tables: `ai-corpus/lab/distill/style/`
(`style_tables.md`, `summary.json`); thresholds built by `scripts/distill/build_ai_thresholds.py`.
