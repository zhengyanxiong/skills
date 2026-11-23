# Visual encoding vocabulary

What each visual variable is allowed to mean in an OSDI/NSDI/SOSP/ASPLOS architecture
diagram, mined from **727 semantic records** (all human-labelled `good`) plus measured
style facts for **1,055 architecture figures**.

How to read the counts:

- `n=727` counts are **regex hits over model-written prose** describing each figure. A
  convention the record does not mention is invisible, so these are floors, not truth.
- Numbers marked **[measured]** come from the SVG measured at print size and are exact.
- Regenerate everything with `scripts/distill/encoding_mine.py`.

Corpus baseline **[measured, n=727]**: flat fill 90.1%, hatch 8.3%, no fill 1.7%
(gradient fill: **0 of 1,055**). Corners mixed 39.9% / square 37.0% / rounded 23.1%.
Some dashed stroke present 60.2%. Arrowheads present 80.9%. Sans 75.8% / serif 17.7%.
Palette size median 6 fills (p25 4, p75 9, p90 13); gray share of palette median 0.17.
Stroke width median 0.56pt. Smallest text median 5.5pt, median text 6.5pt.
Aspect median 1.82. Single-column 79.1%.

---

## Part A — one section per visual variable

### A1. Fill colour

| meaning | n | share |
|---|---|---|
| component / module identity (which subsystem this box is) | 259 | 35.6% |
| layer / tier / plane / phase membership | 163 | 22.4% |
| existing / reused / baseline (gray or white) | 77 | 10.6% |
| kind or state of a datum (precision, hot/cold, plaintext/ciphertext) | 72 | 9.9% |
| **novel / ours** (accent fill on the contribution) | 51 | 7.0% |
| status: red = error/bottleneck, green = ok/accepted | 30 | 4.1% |
| no colour semantics (monochrome, decorative) | 27 | 3.7% |
| colour reused per numbered step, or to track one entity across stages | 10 | 1.4% |

Mining the `"<colour> = <phrase>"` clauses separately shows the hues are **not**
interchangeable:

| colour | dominant bucket | share of that colour's clauses |
|---|---|---|
| red (159 clauses) | error / failure / bottleneck 21.4%, highlight / focus 11.9% | 33% "something is wrong or important here" |
| gray (193) | component / module 26.9%, existing / reused / passive 23.8% | existing/reused share is still roughly 3× the rate of any hue |
| white (19) / black (16) | existing / baseline 42.1% / 25.0% | — |
| blue (305) | component identity 32.1%, layer 20.7% | neutral workhorse |
| green (236) | component identity 30.9%, layer 25.0%, ok/success 3.4% | neutral, mildly positive |
| orange (126), purple (57), pink (55), teal (19) | component identity 26–42% | neutral |

**Recommended default.** Two channels only:

1. **Role channel** — `module` (one neutral hue, default blue), `module-alt` (a second
   hue for a genuinely different kind of component), `container` and `lane` (very light
   tints), `canvas` white. Neutral hues per role, never per box.
2. **Contribution channel** — `accent` fill on exactly the components the paper
   contributes; everything pre-existing stays `module`-neutral or gray/white. This is the
   dominant emphasis idiom (novel-vs-existing is stated by 109 of 727 figures, 15.0%) and
   it is what distinguishes a figure that argues from one that only describes.

Reserve **red** for failure / bottleneck / the thing being called out; do not use red as
a plain module fill. Reserve **gray** for existing-and-unmodified. Cap semantic fills at
about 6 (corpus median); every fill past that needs a legend row.

**Conflicts to avoid.**
- One hue meaning two things. `nsdi26-010_fig3` uses orange for both a component fill and
  the replicated-write arrows; `asplos25-004_figtex9` reuses the label `temp` for two
  buffers "distinguishable only by fill color".
- Two variables carrying the same meaning: do not mark the contribution with accent fill
  *and* a thick border *and* a dashed box. Pick one; the others become noise.
- Colour as the only channel. 16 records flag "fails when desaturated". Every colour
  distinction needs a redundant cue (label, position, border, or shape).

Exemplars: `asplos25-034_fig8` (coloured augmentations vs uncoloured baseline pipeline),
`asplos26-060_fig8` (green = HILOS's own three components, white = conventional),
`sosp23-015_fig1` (filled = Turbo, transparent = unmodified host system).

### A2. Stroke / outline colour

| meaning | n |
|---|---|
| coloured outline marks the contribution | 15 |
| coloured (usually red) outline marks a fault or one example instance | 8 |
| thick / bold border = the focal box | 7 |

Rare on its own — outline colour is a **second-order** device, used when the fill is
already spent on roles. `sosp24-040_fig5` and `sosp24-040_fig8` outline Tenplex's two
components in red against an otherwise black/gray stack; `nsdi23-084_fig3` uses a dashed
orange box for "this is Zeus"; `sosp23-013_fig3` red-dashes the one failing node among
identical repeats.

**Recommended default.** All boxes get the same `stroke` colour at 0.5–0.75pt
(**[measured]** median 0.56pt). Change stroke *colour* only for: (a) the fault/example
instance (red), or (b) the contribution when accent fill is unavailable. Never vary
stroke colour per module.

### A3. Line style — solid / dashed / dotted

| meaning | n | share |
|---|---|---|
| **dashed = logical grouping / container boundary** | 224 | 30.8% |
| dashed = region / plane / phase divider | 75 | 10.3% |
| dashed = zoom / callout leader line | 60 | 8.3% |
| dashed = control / metadata path (solid = data) | 60 | 8.3% |
| dashed = feedback / async / side path | 13 | 1.8% |
| dashed = repetition / partition boundary | 11 | 1.5% |
| dashed = optional / conditional / speculative | 10 | 1.4% |
| dotted used as a distinct third, weaker channel | 9 | 1.2% |
| solid = main data / request flow | 153 | 21.0% |
| no line-style distinction at all in the figure | 19 | 2.6% |

**Recommended default.** Dashed does **one** job per figure, and the default job is
**boundary** — a dashed rectangle around a logical grouping, a system boundary, or a
plane/phase divider (299 of 727 records combined, 41.1%). If the figure instead needs
control-vs-data on its *edges*, then use dashed for control edges and draw every
container with a **solid** light border, and say so in a legend.

Dotted is a third channel only when a fourth is genuinely needed (weak "uses" links,
telemetry). `asplos26-132_fig6` flags its own dotted "uses" arrows as "light dotted lines
that are easy to miss" — if you use dotted, weight it at least as heavily as the solids.

**Conflicts to avoid.** Dashed-for-boundary and dashed-for-control in the same figure is
the single most common ambiguity in the corpus. `osdi24-024_fig6` names it directly:
"controller-to-stage dashed links are visually similar to data arrows".

Exemplars: `asplos25-002_fig5` (dashed = Agent vs Backend groupings),
`asplos25-140_fig7` (solid = data, dashed = control, stated in an in-figure legend),
`asplos25-077_figtex1` (dashed vertical line = control plane / data plane split).

### A4. Line width

**[measured, n=727]** stroke width median 0.56pt (p25 0.4, p75 0.72). Number of distinct
stroke widths per figure: 1 → 19.5%, 2 → 37.7%, 3 → 25.6%, 4 → 10.7%, ≥5 → 4.7%.

So the corpus norm is **two or three widths**: a hairline for container/lane borders, a
normal weight for component boxes and ordinary edges, and a heavier weight for the main
path or a focal box. Only 7 records explicitly use a thick border as the emphasis device,
so weight is a supporting cue, not a primary one.

**Recommended default.** container 0.5pt · box 0.75pt · main-path arrow 1.0–1.25pt.
Never exceed 3 widths — beyond that the reader stops reading weight as meaning.

### A5. Arrow heads

**[measured, n=727]** 80.9% of figures have arrowheads at all; 19.1% have none.
From the prose: filled triangular heads 235 (32.3%), block / hollow arrows 18 (2.5%),
open / line (V-shaped) heads 7 (1.0%), "some connectors have no heads" 32 (4.4%).

| meaning | n |
|---|---|
| double-headed = bidirectional protocol / interface | 87 |
| arrow colour encodes flow or link type | 69 |
| self-loop or loop-back arrow = iteration / feedback | 58 |
| labelled arrow names the payload | 49 |
| fan-out / fan-in = one-to-many | 19 |
| arrow thickness encodes traffic volume | 4 |

**Recommended default.** One head style: a small **filled triangle** on every directed
edge. A **double head** only for a genuinely bidirectional interface (a request/response
protocol, a shared bus) — not as shorthand for "these two talk". **No head** only for a
physical link or containment line, and only if the figure has an explicit heads/no-heads
distinction. Arrow thickness for volume is a real idiom (`nsdi26-054_figtex3`) but rare —
use it only when volume is the point of the figure.

**Conflicts to avoid.** Do not use both arrow colour *and* line style to split control
from data unless the legend spells out both; and do not leave heads off some edges while
other edges have them (32 records self-flag this; it is 28.1% of `bad` figures vs 12.9% of
`good` — see anti-patterns).

### A6. Curved vs orthogonal connectors

**[measured, n=727]** curved arrows present in 37.7% of figures.
From `style.arrows` prose: orthogonal / right-angle 164 (22.6%), curved / spline 200
(27.5%), straight-diagonal 175 (24.1%).

**Recommended default.** **Orthogonal** routing for the structural skeleton — it aligns
with box edges and survives being redrawn, even though the corpus prose now names
curved/spline routing slightly more often overall (27.5% of figures, vs 24.1%
straight-diagonal and 22.6% orthogonal). Reserve **curves** for edges that deliberately
break the grid: feedback loops back to an earlier stage, cross-lane exchanges, callout
leaders. `asplos25-002_fig5` and `asplos26-028_fig2` both use straight orthogonal forward
paths with a single curved loop-back.

**Conflict:** a bundle of many curves converging on one node reads as a smear
(`sosp23-033_fig1`, 12+ crossing arcs). Above ~4 edges into one node, replace the fan with
an orthogonal bus line or one arrow into a group boundary.

### A7. Circled numbers, letters, labelled arrows

**[layout field, n=727]** none 64.8% · circled-numbers 24.6% · labelled-arrows 5.2% ·
letters 5.0% · bare digits 0.4%.
**[measured]** circled glyphs actually detected in 8.7% (the detector is conservative).

| idiom | n | what it does |
|---|---|---|
| circled numbers = ordered end-to-end walkthrough | 124 | walks one request/job through the whole figure |
| step colour matched to the component it acts on | 24 | ties step k to the module that performs it |
| letters (A/B/C, I/II/III) = variants or callout tags | 17 | labels alternatives, not an order |
| §-section tags on boxes | 28 | maps each box to the paper section that describes it |
| labelled arrows instead of numbers | 18 | names the transformation between stages |

**Recommended default.** Use **circled numbers** when and only when the figure narrates a
path: one request, one job, one recovery — typically 3–8 steps. Steps must lie along the
path in reading order (`asplos25-077_fig3`, `sosp25-020_fig3`, `asplos26-008_fig3`).
Use **letters** when the marks label *alternatives or callouts* rather than an order
(`osdi26-108_figtex4` deliberately contrasts numbered = expected events vs lettered =
unexpected). Use **§ tags** to tie boxes to sections — a distinctly systems-paper idiom
that costs nothing and buys navigability (`asplos25-131_fig2`, `nsdi24-056_fig3`).

**Conflicts to avoid.** Do not mix circled numbers and circled letters for the same kind
of thing. Do not use numbers as component IDs and as step order in one figure. Only 31.8%
of circled-number figures also carry a legend — if the numbers are not self-evident from
the path, spell them out in the caption (`nsdi25-062_fig7` flags "numbered steps are not
fully self-explanatory without the caption").

### A8. Stacked / offset rectangles, ellipsis, "×N"

| idiom | n |
|---|---|
| stacked / offset rectangles = N identical copies | 97 |
| ellipsis (`...`) between two instances = elided repetition | 35 |

**Recommended default.** For a pool of identical instances, draw **one** detailed
instance plus a **stacked/offset outline behind it**, and label the count (`×N`,
`Worker 1 … Worker N`). `osdi26-046_fig8` uses a stacked-card icon on every box to say
"many parallel instances"; `osdi24-050_fig6` stacks instances into a pool.

**Conflict:** 12 records flag "implied repetition without a count" — a stack or an
ellipsis without an `N` or a range leaves the reader guessing
(`asplos25-043_fig5`: "rely on '...' ellipses rather than an explicit count label").
Never draw the same box three times when a stack plus `×3` will do (both
`asplos26-048_fig1` and `nsdi26-039_fig5` waste half their area this way).

### A9. Shape idioms

| shape | meaning | n |
|---|---|---|
| grid of small cells | memory / tensor / matrix / bitmap layout | 122 |
| cylinder or drum | persistent store / database | 42 |
| circle | arithmetic operator or processing unit | 6 |
| diamond | decision / branch with Yes-No labels | 5 |
| nested box-in-box | containment hierarchy | 25 |
| status glyph (check, cross, star, lock, fire) | outcome or property of the thing next to it | 55 |

**Recommended default.** **Rectangles for everything that is a component.** Deviate only
for the three idioms readers already know: cylinder = persistent store, grid of cells =
memory/tensor layout, diamond = a real branch with labelled outcomes. Corner radius
should be one value for the whole figure (`corners` is `mixed` in 39.9% of the corpus,
which is a laxity to avoid, not a norm to copy).

**Conflict — the shape zoo.** `asplos26-018_fig4` (`bad`) uses a cloud, a cylinder, a
diamond and a barred rectangle for four ordinary components, none with its conventional
meaning. Every non-rectangle shape is a promise about semantics; if you cannot state the
promise, use a rectangle.

### A10. Dashed container vs solid container

Both exist. Solid containers dominate when the container is a *physical* thing (a host, a
chip, a switch); dashed dominates when it is a *logical* thing (a system boundary, a
phase, a scope). 224 records use dashed specifically for logical grouping.

**Recommended default.** Physical enclosure → thin **solid** border, very light tint.
Logical grouping or "this is our system" → **dashed** border, no fill or the faintest
tint, title set at the top-left inside the box. No fill is the corpus norm for containers of either kind (356 of 726 good
figures with records draw every container as an outline only): the `*-outline` palettes in palettes.md
carry `container: null` for exactly this, and a grey or tinted slab is the deliberate exception. `asplos26-018_fig3` labels its solid
"Syncopate" box; `nsdi23-084_fig3` uses a dashed orange box for the same purpose. Nesting
depth in the corpus is 2 in 50.9% of figures and 3 in 37.6% — **stop at depth 3**.

### A11. Background bands / lanes

**[layout field]** lanes present in 39.3% of figures; swimlane/tinted-band idiom named in
96 records (13.2%).

**Recommended default.** Use a full-width tinted band per **layer / plane / phase**
(control / data, offline / online, host / device, user space / kernel space) with the
band name set at the left edge or as a title bar. Band tints must be lighter than every
box that sits on them — `nsdi23-037_fig2` (`bad`) inverts this and the gray Host container
reads as more prominent than the coloured boxes inside it. A band and a dashed container
should not both group the same set of boxes.

Exemplars: `asplos25-038_fig3` (Control / Scaling / Serving planes),
`osdi26-030_figtex2` (user space vs kernel space rule), `nsdi26-030_fig1` (three tiers).

### A12. Text styling

| styling | meaning | n |
|---|---|---|
| **bold** | box and group titles | 252 (34.7%) |
| bold or coloured text | contribution term / annotation callout | 164 (22.6%) |
| *italic* | annotation, example value, commentary | 102 (14.0%) |
| `monospace` | code, API names, signal names | 51 (7.0%) |

**[measured]** sans 75.8%, serif 17.7%. Smallest text median 5.5pt, median text 6.5pt,
largest 8.0pt — i.e. a **three-level type scale within about a 1.5× range**.

**Recommended default.** One sans family. Three sizes: group/band title (bold, largest),
box label (regular), annotation (smallest, `text-muted`). Bold for titles only. Italic
grey for commentary that is not a component name (`asplos25-146_fig3`: italic grey
annotations explaining temporal overlap). Monospace only for literal identifiers.
Coloured text only for the accent — and **not** if accent colour is already carrying
fills or arrows (`nsdi26-126_fig5` uses red for both section tags and the request path).

Floor: **nothing below 6pt at print size** for anything a reader must read. The corpus
median smallest text is 5.5pt and 20.8% of records complain about it — copy the median,
not the tail.

### A13. Icons

| icons | n | share |
|---|---|---|
| none at all | 268 | 36.9% |
| vector glyphs (actors, hardware, storage) | 264 | 36.3% |
| bitmap / photo panel mixed in | 106 | 14.6% |

**[measured, 1,055 figures]** bitmap present 43.6% of `good`; bitmap covering >10% of the
figure 12.1% of `good`, 6.2% of `bad`.

**Recommended default.** Prefer **no icons**. Where an icon helps the reader recognise a
part (user, GPU, disk, switch), a small monochrome vector glyph from the parts library in
the boxes' stroke weight matches the line work, and a bitmap icon works as well. Bitmaps of
any kind — a sample input or output, a photo, a screenshot, a rendered result, an icon — are
drawn as an `<image>` from a local PNG / JPEG, ≥ 150 ppi at print size, and inlined at
delivery (`spec-guide.md` §4 "Bitmaps").

### A14. Hatch / shading

**[measured]** hatch fill 8.3% of figures (0% gradient across all 1,055).
Prose mentions of hatch/watermark/zebra: 74 (10.2%).

**Recommended default.** Flat fill. Use hatch **only** as a second channel on top of a
fill that is already saying something else — e.g. `nsdi26-017_fig5` (red *hatch* = hung
operator on top of colour = operator type), `osdi26-047_fig5` (hatch = completed chunk).
Never use hatch merely to make boxes look different, and never use gradients or 3D
extrusion: the corpus contains **zero** gradient-filled architecture figures.

### A15. Box size

Size is read as importance. 103 records (14.2%) name size or centrality as the emphasis
device: "drawn large and central" (`nsdi26-090_fig4`), "the largest, most central block"
(`asplos26-076_fig10`), "panel (c) is visually the largest, reflecting the paper's focus"
(`osdi23-048_fig1`).

**Recommended default.** Boxes of the same kind get the same size. Give extra area only to
(a) the contribution, or (b) a box whose internals you are actually showing. An oversized
box with nothing in it (`nsdi26-126_fig5`'s empty "File Stores") reads as a broken
promise.

---

## Part B — emphasis: how figures argue for the contribution

Counted over the `encoding.emphasis` field (n=727):

| technique | n | share |
|---|---|---|
| numbered walkthrough (circled steps) | 120 | 16.5% |
| size / centrality (largest, central, anchoring box) | 103 | 14.2% |
| repetition / replication (stacks, `×N`, ellipsis) | 97 | 13.3% |
| red annotation / callout label | 93 | 12.8% |
| side-by-side comparison / before-after panels | 81 | 11.1% |
| layout position (bands, symmetry, left-right split) | 61 | 8.4% |
| accent colour on the novel component | 52 | 7.2% |
| zoom callout into the block of interest | 49 | 6.7% |
| gray / white / plain background for the existing parts | 30 | 4.1% |
| bounding box marking "this is our system" | 27 | 3.7% |
| shaded region / tinted band behind the novel part | 19 | 2.6% |
| §-section tags tying boxes to the text | 18 | 2.5% |
| explicit legend used as the emphasis device | 18 | 2.5% |
| status glyph (check / cross / star / fire) | 17 | 2.3% |
| thick / bold border on the focal box | 3 | 0.4% |

Derived: **109 of 727 (15.0%)** figures explicitly mark which parts are novel, by accent
colour or by an equivalent callout.

**Recommended hierarchy — apply in this order, stop when the contribution is obvious.**

1. **Accent fill on the contribution, neutral/gray on everything else.** Cheapest,
   strongest, survives greyscale printing badly so pair it with (2) or a label.
   `asplos26-066_fig7`: blue = FuseFlow's own passes, yellow = reused prior work.
2. **A named boundary around the system.** A dashed or solid box titled with the system
   name, so a reader can see at a glance where the paper starts and the world ends.
   `nsdi23-084_fig3`, `asplos26-018_fig3`.
3. **A numbered walkthrough** if the figure's message is a *path* rather than a
   *structure*. 3–8 circled steps along the actual edges.
4. **Position and size**: put the contribution centre or at the convergence point, and
   give it more area than its neighbours.
5. **One red callout** naming the thing the reader must not miss (a stall, a failure, a
   bottleneck, a saved round-trip). One, not five.
6. **A comparison panel** — baseline on the left/top, ours on the right/bottom, sharing
   identical geometry so only the difference moves. Only when the contribution is a
   *replacement*, not an addition.

Do **not** stack 1+2+3+4+6 on one figure. When every element is emphasised nothing is;
`asplos25-038_fig3` self-reports "dense combination of numbered steps, colored arrows and
nested sub-boxes may be hard to trace at a glance".

---

## Part C — legend conventions

**[layout field, n=727]** none 73.2% · inside 13.9% · below 7.4% · right 5.5%.
So **26.8% of figures carry a legend**, and legend rate rises with palette size:

| distinct named fills | figures | with a legend |
|---|---|---|
| 1–3 | 140 | 19 (13.6%) |
| 4–6 | 527 | 157 (29.8%) |
| 7–9 | 50 | 14 (28.0%) |
| 10+ | 10 | 5 (50.0%) |

The corpus is **under-legended**: 159 records (21.9%) list "colour/icon coding with no
legend" as a weakness, and 14 records say the coding is only stated in the caption. This
is a defect to fix, not a convention to copy.

**When a legend is required.**
- More than **4 semantic fills**, or any fill whose meaning is not written inside the box.
- Any time **line style or arrow colour carries meaning** (control vs data, link type).
  `asplos25-140_fig7`, `asplos25-100_fig5`, `sosp25-053_fig4` and `osdi26-047_fig5` all
  do this correctly with an in-figure key.
- Any **icon or glyph** whose meaning is not universal. `asplos25-055_fig1` self-flags
  "icons (funnel, magnifying glass, pickaxe) are not explained by an in-figure legend".
- **Not** required when the only encoding is accent-vs-neutral and the accent boxes are
  already the paper's named components.

**Placement.** `inside` is the majority of legends (101 of 195) and is preferred: a small
keyed block in an empty corner of the drawing, within the same visual frame. `below` (54
figures) and `right` (40 figures) are where the "legend far from what it explains"
complaint comes from (20 records; e.g. `asplos26-089_fig2`: "legend for FP8/FP4 color
coding is placed below the diagram rather than next to the precision panels it explains";
`nsdi23-004_fig1`: "the legend for M/U circles sits far above the traces it explains").
Rule: the legend must sit within roughly one box-width of at least one thing it decodes.

**Circled numbers.** Only 57 of 179 circled-number figures (31.8%) also carry a legend.
The corpus convention is that steps are decoded **in the caption prose**, in order
("Steps: (a) compile script region; (b) …"), and the figure only carries the glyphs. That
works if and only if the glyphs sit on the path in reading order. Write the caption step
list whenever you draw circled numbers.

---

## Part D — default encoding table

Apply unless the user says otherwise.

| variable | default meaning | notes |
|---|---|---|
| fill `accent` | **the paper's contribution** | one accent hue, used nowhere else |
| fill `module` / `module-alt` | component role, ≤2 neutral hues | never one hue per box |
| fill `container` / `lane` | grouping / layer, lightest tints | always lighter than its contents |
| fill gray, white | existing, reused, unmodified | the "not ours" signal |
| fill red / pink | error, failure, bottleneck, stall | never a plain module fill |
| fill green (when red is in play) | success, valid, accepted | only as red's counterpart |
| hatch | a **second** state on top of an already-meaningful fill | ≤1 hatch pattern |
| gradient, 3D | never | 0 of 1,055 figures |
| stroke colour | uniform `stroke` for all boxes | change only for a fault/example instance |
| stroke width | 0.5pt container · 0.75pt box · 1.0–1.25pt main path | ≤3 widths |
| **dashed** border | logical grouping / system boundary / plane divider | one job per figure |
| **solid** border | physical enclosure and every ordinary box | — |
| **dashed** edge | control / metadata path — *only if* containers are solid | declare in legend |
| **solid** edge | data / request path | — |
| dotted edge | weak "uses"/telemetry link, fourth channel only | weight it visibly |
| arrowhead | small filled triangle on every directed edge | — |
| double arrowhead | genuinely bidirectional interface | not "they talk" |
| no arrowhead | physical link or containment only | never mixed in silently |
| routing | orthogonal for structure, curved for feedback / cross-lane | — |
| arrow colour | flow type, only with a legend | else keep all arrows `arrow` grey/black |
| arrow `arrow-accent` | the one path the figure is about | at most one |
| ①②③ circled numbers | ordered walkthrough of one request/job, 3–8 steps | list them in the caption |
| A/B/C letters | alternatives or callout tags, not order | — |
| §x.y tag | the paper section describing that box | cheap, encouraged |
| stacked / offset rect | N identical instances | always add `×N` or `1 … N` |
| `...` ellipsis | elided repeats | always with a count nearby |
| cylinder | persistent store | — |
| grid of cells | memory / tensor / matrix layout | — |
| diamond | real branch, with labelled outcomes | otherwise use a rectangle |
| every other shape | rectangle | — |
| tinted band / lane | layer, plane, or phase | name it at the left edge |
| **bold** | box and group titles | — |
| *italic* grey | commentary, not component names | — |
| `mono` | code, API and signal identifiers | — |
| accent text | the one contribution term | not if accent already fills boxes |
| type scale | 3 sizes within ~1.5×, floor **6pt** at print size | sans |
| icons | none by default; a monochrome vector glyph or a bitmap icon where it helps recognition | — |
| bitmap (sample, photo, screenshot, rendered result, icon) | a picture the figure needs, as `<image>` | local PNG / JPEG, ≥ 150 ppi, inlined at delivery; a photo or screenshot gets a thin frame and a caption |
| legend | required at >4 semantic fills, or any meaningful line style / arrow colour / glyph | place `inside`, near what it decodes |
| nesting | depth ≤3 | 51% of the corpus stops at 2 |
