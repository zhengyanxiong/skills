# Anti-patterns

Two different failure populations, mined separately.

- **§1 residual flaws** — 959 weakness items recorded across the **727 `good`
  architecture figures** (608 records list at least one; 119 are clean). These are the
  things that still go wrong in figures that got published and were judged good.
- **§2 hard failures** — what makes a figure `ok` or `bad`. From measured discriminators
  over all **1,055** architecture figures (736 good / 235 ok / 32 bad) plus a direct look
  at 10 `ok`/`bad` previews.

**Surprise worth internalising:** density and small type are *not* what makes a figure
bad. `bad` figures are **less** dense and have **larger** minimum type than `good` ones
(min font <4.5pt: 21.9% of good vs 9.4% of bad; >100 elements/100pt²: 16.4% vs 15.6%).
What separates `bad` is **under-investment**: no colour system, no arrowheads, no step
markers. Density is the failure mode of *ambitious* figures; poverty is the failure mode
of *lazy* ones. Both lists below are needed.

`[AUTO]` = checkable from the SVG geometry/style. `[LOOK]` = needs a rendered look.

---

## §1 Residual flaws of good figures (ordered by frequency)

### 1. Over-dense — too many elements for the area — 272/727 (37.4%)

> "very dense text and overlapping tables at this size" (`asplos25-002_fig5`)
> "high information density with several nested sub-panels may be hard to parse at a
> glance" (`asplos25-025_fig3`)

**Looks like.** Every square centimetre is occupied; nested sub-panels three deep; two or
three sub-diagrams (a pipeline, a timeline, a table) sharing one frame.
**Hurts because.** The reader cannot find an entry point, and no single message survives.
**Detect.** `[AUTO]` labelled elements per 100pt²: corpus good median 48, p75 76, p90 147;
warn >80, error >150. Also total `text_boxes` (good median 24, p90 ~60). Raw *shape*
count is a bad proxy — `sosp23-033_fig1` has 2,138 shapes and ~11 labels and reads as
simple. `[LOOK]` can you name the figure's one message in 5 seconds?
**Fix.** Cut to one message. Move the second sub-diagram to its own figure. Replace
repeated instances with one instance + `×N`. Collapse a nested sub-panel to a black box
and detail it elsewhere. Raise the column width from single to double before shrinking type.

### 2. Colour / icon coding with no legend — 159/727 (21.9%)

> "color coding (green/gold/red/blue) is not explained by an in-figure legend"
> (`asplos25-002_fig5`)
> "no in-figure legend explicitly mapping yellow/blue to FR vs. workload-imbalance,
> relying on the caption" (`asplos25-034_fig8`)

**Looks like.** Six pastel fills, or icon glyphs, doing semantic work with nothing keying
them.
**Hurts because.** The encoding exists only in the author's head; the reader guesses.
**Detect.** `[AUTO]` count distinct semantic fills (excluding white/canvas); if >4 and no
legend group exists, flag. Same if ≥2 stroke dash patterns or ≥2 arrow colours are used
and no legend exists. Corpus legend rate is only 23.8% at 4–6 fills, so this fires often —
which is the point.
**Fix.** Add a small keyed block **inside** the drawing, or cut the palette to ≤4 fills so
no legend is needed. See `encoding.md` Part C.

### 3. Text too small to read at print size — 151/727 (20.8%)

> "very dense, with many small sub-blocks and labels at small font sizes"
> (`asplos25-032_fig6`)
> "dense multi-panel figure with many small labeled boxes may be hard to read at print
> size" (`asplos25-051_fig3`)

**Looks like.** Sub-labels, table cells and inset annotations set 2–4pt while the box
titles are 8pt.
**Hurts because.** Anything under ~5pt is unreadable in a printed two-column proceedings.
**Detect.** `[AUTO]` minimum rendered font size at print size. Median smallest text is 5.5pt across all 736 `good` figures (5.0pt across the 272 with semantic records);
figures whose own record complains have median 4.5pt vs 5.5pt for the rest. Warn <6pt,
error <5pt. Also flag a type range wider than ~2.5× (title 10pt + annotation 3.5pt).
**Fix.** Set a 6pt floor and re-flow. If a label will not fit at 6pt, the box is too small
or the label is too long — shorten the label, widen the box, or move the detail out.
**Reconciles with `style-rules.md`.** That file correctly reports that minimum font size
does *not* discriminate good from bad (good figures pack in more small print, so their
minimum is if anything smaller). Both are true: small type is not what makes a figure bad,
but it is the third-most-cited residual flaw *within* good figures. So do not enlarge the
smallest label to "fix" a weak figure — but do keep a 6pt floor on anything you draw.

### 4. Arrows missing, or connection / direction unclear — 61/727 (8.4%)

> "no arrows visibly connect the left pipeline (Generator/Leakage Model/Executor) to the
> right-hand trace-comparison diagram" (`asplos25-096_fig1`)
> "no arrowheads on datapath lines reduces directional clarity" (`asplos26-029_fig10`)

**Looks like.** Two halves of a figure floating side by side with no edge between them;
bare lines where every other edge has a head; a return/feedback edge easy to miss among
denser forward traffic (`asplos25-142_fig5`: "the feedback arrow (4) back to Frontend is
easy to miss among the forward arrows").
**Hurts because.** The reader cannot reconstruct the flow, which is the whole point.
**Detect.** `[AUTO]` (a) connected-component analysis: a labelled box with degree 0 is a
strong flag; (b) marker-end present on some edges but absent on others; (c) any edge with
stroke-width < 60% of the median edge width.
**Fix.** Every box either has an edge or sits inside a container that has one. Uniform
arrowheads. Bring auxiliary edges up to at least the container stroke weight.

### 5. Ambiguous or duplicated labels — 50/727 (6.9%)

> "the small 'Coordinator' node box and the outer 'Coordinator' container share the same
> name, which can read as ambiguous" (`asplos25-039_fig3`)
> "reusing the label 'Model' for three distinct boxes across phases relies on phase
> headers for disambiguation" (`asplos26-026_fig4`)

**Looks like.** The same word naming a container and one of its children; identical labels
on boxes that mean different things.
**Hurts because.** Steps and prose references can no longer be matched to boxes.
**Detect.** `[AUTO]` exact-duplicate text strings on boxes at different nesting levels, or
duplicate strings where the shapes have different sizes/fills.
**Fix.** Qualify one of them (`Coordinator (global)` / `Coordinator node`), or, if the
boxes really are identical instances, replace them with one instance + `×N`.

### 6. Terse notation / unexplained abbreviations — 31/727 (4.3%)

> "abbreviated labels (inst1, inst2, S1, S2) require the caption/text to be understood"
> (`asplos26-006_fig2`)
> "dense abbreviated labels (e.g. Aut phi_x, evk manager) require caption/text context"
> (`asplos26-004_fig6`)

**Looks like.** `Xk-stub`, `SFU`, `Inter. Engine`, `f()`, `S^T` as box labels.
**Hurts because.** The figure stops being scannable; it becomes a decoder ring.
**Detect.** `[LOOK]` mostly. `[AUTO]` weak proxy: labels ≤4 characters, or labels
containing `_`/`^`/digits-only, that never appear expanded anywhere in the figure.
**Fix.** Spell out at least once, in the box or as a one-line annotation. Abbreviate only
after the full form has appeared in the same figure.

### 7. Too many panels / mixed visual languages in one figure — 25/727 (3.4%)

> "four sub-panels of different sizes and layouts packed into one figure can be visually
> busy" (`asplos25-101_fig1`)
> "combines a code listing, a data table, and two flowcharts in one dense figure"
> (`asplos25-117_fig2`)

**Looks like.** An architecture box diagram + a Gantt timeline + a bar chart + a code
snippet, all in one frame.
**Hurts because.** Each language needs its own reading protocol; switching costs attention
the reader does not have.
**Detect.** `[LOOK]` mainly. `[AUTO]` proxy: >3 top-level sibling groups with disjoint
bounding boxes and no shared axis or connector between them.
**Fix.** Two visual languages maximum per figure, and only when one *feeds* the other
(diagram + the timeline it produces). Otherwise split.

### 8. Meaning only recoverable from the caption / body text — 23/727 (3.2%)

> "figure text is compact and relies on the caption/prose to explain that the three dark
> boxes are the unit's 'main components'" (`asplos25-077_figtex1`)
> "reused generic labels (RF, SMEM, mma) without per-instance qualifiers require
> cross-referencing the caption/text to fully disambiguate" (`asplos25-114_fig5`)

**Looks like.** The colour convention, the icon meaning or the step semantics live only in
the caption.
**Hurts because.** Readers skim figures before captions; a figure that cannot be read
standalone loses its skim-time argument.
**Detect.** `[LOOK]`. Cover the caption: can you still say what the colours mean?
**Fix.** Push one line of the caption into the drawing as a legend row or an inline label.
Captions should *narrate the steps*, not *define the encoding*.

### 9. Legend placed far from what it explains — 20/727 (2.8%)

> "legend for FP8/FP4 color coding is placed below the diagram rather than next to the
> precision panels it explains" (`asplos26-089_fig2`)
> "the legend for M/U circles sits far above the traces it explains" (`nsdi23-004_fig1`)

**Detect.** `[AUTO]` distance from the legend group's bbox to the nearest element carrying
one of the encodings it defines; flag if greater than ~1 box-width (or if the legend is
outside the main drawing frame while `inside` placement was available).
**Fix.** Move the legend into an empty corner of the drawing, next to at least one thing
it decodes.

### 10. Awkward aspect ratio for the column — 17/727 (2.3%)

> "single-column layout makes the figure very tall (aspect 0.67)" (`asplos25-064_fig1`)
> "very dense (309 shapes, 64 text boxes) packed into a wide, short aspect ratio (3.02)"
> (`asplos25-140_fig7`)

**Detect.** `[AUTO]` aspect = w/h. Corpus good: median 1.8, p10 1.14, p90 3.39. Flag <1.0
(taller than wide — burns a whole column) and >4.0 (a letterbox strip that forces tiny
type). Cross-check against `column`: 74.3% of the corpus is single-column.
**Fix.** Re-flow the layout direction (a tall pipeline becomes a wide one), or promote to
a double-column figure, or split.

### 11. Colour-only distinction — 16/727 (2.2%)

> "the generic label 'temp' is reused for both private- and shared-memory ciphertext,
> distinguishable only by fill color" (`asplos25-004_figtex9`)
> "quality/latency labels rely on colored text (red/green) which may not be
> distinguishable if desaturated" (`asplos26-019_fig1`)

**Hurts because.** Proceedings get printed and photocopied in greyscale, and ~8% of male
readers cannot separate red from green.
**Detect.** `[AUTO]` (a) two semantic fills whose greyscale luminance differs by <10%;
(b) a red/green pair used as the only difference between two elements; (c) any pair of
boxes with identical text and different fill only.
**Fix.** Add a redundant channel: a distinct label, a border style, a position, or a
luminance gap. Choose accent hues that also differ in lightness.

### 12. Implied repetition without a count — 12/727 (1.7%)

> "repeated near-identical processing-engine and MAC-unit boxes rely on '...' ellipses
> rather than an explicit count label in-panel" (`asplos25-043_fig5`)
> "replicated core stack drawn only with a partial outline, relying on the reader to infer
> repetition" (`asplos26-029_fig9`)

**Detect.** `[AUTO]` an ellipsis glyph (`...`/`…`) or a stacked/offset rectangle group with
no nearby text matching `×N`, `x N`, `1 … N`, or a digit.
**Fix.** Always annotate the count or the range next to the stack or the ellipsis.

*(27 further weakness items are extraction artifacts — truncated captions, missing source
palette metadata — not design flaws. Ignore them.)*

---

## §2 Hard failure modes (what makes a figure `ok` or `bad`)

Measured over all 1,055 architecture figures. Rates are **good / ok / bad**.

"Palette" below means `style.palette.n`, the count of distinct fill colours measured from
the SVG excluding black and white.

| signal | good | ok | **bad** |
|---|---|---|---|
| palette ≤1 fill (no colour system) | 5.8% | 15.7% | **50.0%** (16/32) |
| palette ≤2 fills | 11.7% | 26.0% | **56.2%** |
| ≥95% of palette is gray | 5.6% | 8.9% | **25.0%** |
| `fill: none` (outline-only line art) | 1.9% | 6.8% | **12.5%** |
| zero arrowheads with >5 connector lines | 12.9% | 15.3% | **28.1%** |
| has circled step numbers | 8.7% | 6.4% | **0.0%** |
| >60 labelled elements | 7.5% | 0.9% | 0.0% |
| min font <4.5pt | 21.9% | 15.3% | 9.4% |
| gradient fill | 0.0% | 0.0% | 0.0% |

### A. No colour system — the top `bad` signal (50% of bad figures)

**Looks like.** Every box white or the same gray; the only colour in the figure is on a
boundary or a callout label. `asplos25-169_fig3` (`bad`, 1 fill): three identical white
stage boxes inside a magenta dashed frame — the frame is the only colour, so the accent
carries no meaning about the content. `osdi23-006_fig1` (`bad`, 0 fills, `fill: none`):
pure black line art; caption reads "see text for details".
**Hurts because.** With no fill channel there is no way to say which component is the
contribution, which is reused, and which is context — the figure describes but does not
argue.
**Detect.** `[AUTO]` distinct non-white fills ≤1, or `gray_frac` ≥0.95, or `fill: none`.
**Fix.** At minimum: two neutral module hues + one accent for the contribution + gray for
existing parts. Even one accent hue on the right two boxes moves a figure out of this class.

### B. No arrowheads / undirected spaghetti — 28.1% of bad vs 12.9% of good

**Looks like.** `osdi23-006_fig1`: clients fan into an ellipse on bare diagonal lines with
heads on some links and not others; `nsdi24-008_fig5`: an entire topology drawn in light
dashed blue with no heads anywhere.
**Hurts because.** Direction *is* the content of an architecture figure.
**Detect.** `[AUTO]` `marker-end` count == 0 while connector-line count > 5; or heads
present on <70% of non-containment edges.
**Fix.** Put a filled triangular head on every directed edge; use headless lines only for
physical links or containment, and only if the figure clearly distinguishes them.

### C. Traffic-light palette / colour used per box instead of per role

**Looks like.** `asplos26-048_fig1` (`bad`): pure saturated blue / green / red boxes with
white bold text, red used for both "Cache" and "CXL Shared Memory Node" — two unrelated
things, in the colour that conventionally means danger. `nsdi26-126_fig5` (`bad`, 9 fills):
one fill per named module, no rule, no legend; red doing double duty as section tags *and*
the request-path arrows. `nsdi23-037_fig2` (`bad`): green/purple/orange saturated fills
adjacent, with only the *arrow* legend supplied.
**Hurts because.** N boxes with N colours conveys exactly as much as N boxes with one
colour, minus the reader's patience — and it burns the accent so the real contribution
cannot stand out.
**Detect.** `[AUTO]` distinct fills > 6 with no legend; any fully-saturated fill (S>0.8,
V>0.8); red or green used on a box whose label has no error/success semantics; the accent
hue appearing on >30% of boxes.
**Fix.** Assign colour to **roles**, not boxes. Desaturate to tints. Reserve red.

### D. Everything drawn N times instead of once with `×N`

**Looks like.** `asplos26-048_fig1`: three identical Compute Node columns (12 boxes for 4
concepts) plus two identical CXL memory nodes. `nsdi26-039_fig5`: three "Game Application"
boxes, two of them empty. `nsdi26-126_fig5`: a second MNode drawn as an unlabelled clone.
**Hurts because.** It spends the figure's area on redundancy, forcing the type down.
**Detect.** `[AUTO]` near-identical subtrees (same shape geometry + same or empty text)
repeated ≥3 times, or ≥2 empty clones of a detailed group.
**Fix.** One detailed instance + a stacked outline behind it + `×N`.

### E. Shape zoo — flowchart shapes with no stated meaning

**Looks like.** `asplos26-018_fig4` (`bad`): a cloud ("Target Program"), a cylinder holding
a *model*, a diamond that is not a decision ("Logger"), and a barred rectangle — four
shapes, four components, zero conventions honoured. `nsdi26-010_fig3` mixes skewed
"document" parallelograms in among rectangles.
**Hurts because.** Readers apply the standard meanings; wrong shapes actively mislead.
**Detect.** `[AUTO]` count distinct shape classes (rect / rounded-rect / ellipse /
cylinder / polygon / cloud path); flag >3, or any diamond without ≥2 labelled outgoing
edges, or any cylinder whose label is not storage-like.
**Fix.** Rectangles unless the shape is one of the three conventions in `encoding.md` A9.

### G. Floating callouts with no leader lines

**Looks like.** `nsdi23-037_fig2`: four dashed boxes of API names (`ibv_post_send`, …)
scattered around the diagram with nothing tying each to its box. `nsdi24-008_fig5`: three
orange technique labels floating over the topology, one overlapping the links.
**Hurts because.** An annotation whose anchor is ambiguous is worse than no annotation.
**Detect.** `[AUTO]` a text/box group that has no edge and whose nearest neighbour is
>0.5 box-width away; `[LOOK]` for the actual ambiguity.
**Fix.** A thin leader line to the exact element, or move the text inside/adjacent to it.

### H. Oversized type in undersized boxes

**Looks like.** `nsdi25-068_fig2` (`bad`): 9.5–10.5pt serif labels that wrap to three lines
and nearly fill their boxes; box widths differ arbitrarily; one box hangs past its row.
**Hurts because.** Labels larger than the body text invert the figure/text hierarchy, and
wrapping in a small box destroys alignment.
**Detect.** `[AUTO]` any label >10pt at print size; any text bbox occupying >80% of its
box area; any label wrapping to ≥3 lines.
**Fix.** Type scale below body size (6–8pt); shorten labels; size boxes to their content.

### I. Text colliding with lines or overflowing its shape

**Looks like.** `asplos26-018_fig4`: "Target Program" spills past the cloud outline, and
"Scheduler Control" / "Perf Info" sit *on* the connector lines. `asplos26-048_fig1`: a
rotated "bypass" label wedged into the gap between a box and its arrow; "CXL Interconnect"
sitting on the bus line.
**Detect.** `[AUTO]` this is the most mechanically checkable defect: text bbox ∩ path bbox
non-empty, text bbox extending outside its parent shape, or any element outside the figure
viewBox.
**Fix.** Reserve a text band inside each box; route connectors around labels; put edge
labels in a small opaque canvas-coloured rectangle on the line.

### J. Misalignment

**Looks like.** Boxes in a row with 1–3pt differences in top edge or height; container
titles at different insets; nothing sharing a gridline.
**Hurts because.** Near-alignment reads as sloppiness and defeats the reader's attempt to
group by row/column.
**Detect.** `[AUTO]` cluster the left/right/top/bottom edge coordinates; flag clusters
whose members differ by 0 < Δ ≤ 3pt (near-misses are worse than deliberate offsets). Same
for box heights within a row and for corner radii across the figure (`corners: mixed`
occurs in 41.5% of the corpus — do not copy it).
**Fix.** Snap to a grid; one corner radius; equal heights within a row.

### K. Inverted hierarchy — containers louder than their contents

**Looks like.** `nsdi23-037_fig2`: the gray "Host" container is darker than several boxes
inside it. `nsdi26-126_fig5`: an empty "File Stores" box as large as the detailed MNode.
**Detect.** `[AUTO]` a container fill darker (lower luminance) than any child fill; a
container/group with zero labelled children occupying >8% of the figure area.
**Fix.** Containers get the lightest tint and the thinnest border. Empty boxes get deleted
or shrunk to a label.

### L. Legend that only covers part of the encoding

**Looks like.** `nsdi26-010_fig3`: the legend defines dashed = control / solid = data, but
the figure also uses blue-vs-orange arrows, a teal dash variant, and six pastel fills,
none of them keyed — and the legend sits in the middle of the drawing where it reads as
content.
**Detect.** `[AUTO]` enumerate the distinct encodings actually used (fills, dash patterns,
arrow colours, glyph classes) and compare with the number of legend rows; flag any encoding
class with zero legend coverage. `[LOOK]` for the legend competing with content.
**Fix.** Either key every encoding class or remove the unkeyed ones. Put the legend in an
empty corner, not between two clusters.

---

## §3 Linter checklist (compact)

Ordered by expected hit rate. Everything here is `[AUTO]` unless marked.

| # | check | warn | error |
|---|---|---|---|
| 1 | min font size at print size | <6pt | <5pt |
| 2 | labelled elements per 100pt² | >80 | >150 |
| 3 | distinct semantic fills without a legend | >4 | >6 |
| 4 | text bbox ∩ connector bbox, or text outside its shape | any | any |
| 5 | element outside the figure viewBox | — | any |
| 6 | edge-coordinate near-misses (0 < Δ ≤ 3pt) | ≥3 pairs | — |
| 7 | arrowheads on <70% of directed edges | yes | 0 heads with >5 edges |
| 8 | labelled box with degree 0 (no edge, no container) | any | — |
| 9 | distinct non-white fills ≤1, or gray share ≥0.95, or `fill: none` | yes | — |
| 10 | fully saturated fill (S>0.8 and V>0.8) | any | — |
| 11 | accent hue used on >30% of boxes | yes | — |
| 12 | distinct shape classes | >3 | — |
| 13 | distinct stroke widths | >3 | >5 |
| 14 | distinct corner radii | >1 | — |
| 15 | bitmap `<image>`: < 150 ppi at print size, stretched or letterboxed | yes | a URL, a missing file, not PNG / JPEG, no width / height |
| 16 | gradient or filter in the defs | — | any |
| 17 | ellipsis or stacked group with no `×N` / count nearby | any | — |
| 18 | duplicate label strings across nesting levels | any | — |
| 19 | ≥3 near-identical repeated subtrees | yes | — |
| 20 | nesting depth | >3 | >4 |
| 21 | aspect ratio | <1.0 or >4.0 | — |
| 22 | legend bbox farther than 1 box-width from anything it decodes | yes | — |
| 23 | any label >10pt, or text filling >80% of its box | yes | — |
| 24 | container fill darker than a child fill | yes | — |
| 25 | two semantic fills within 10% greyscale luminance | yes | — |

Needs a `[LOOK]` pass, not a linter: can you state the figure's one message in five
seconds; can you read it with the caption covered; is the contribution obvious without
being told; do the circled numbers actually lie along the path in order; do the shape and
colour choices honour their conventional meanings; is any panel a different visual
language from its neighbours.
