# Layouts: mechanism figures

How systems papers actually organise **mechanism figures** — the second figure kind of this skill:
figures that show how *one part* of a system works (a walkthrough, successive frames, alternatives
side by side, control logic, one component opened up), as opposed to the whole-system overview
covered by [`../layouts.md`](../layouts.md).

**This file is not a template library, and it must not become one.** Architecture figures collapse
into twenty recurring templates because they all answer the same question ("what sits where"). These
do not. Five groups × a dozen drawn bases × 1–10 panels, frames and steps produce figures that are
almost never alike: of the 152 records below, the single most common *complete* shape
(`single`, one panel, base `component`) accounts for fewer than one in ten. What follows is a **menu
of observed devices with their frequencies**, not a set of moulds. Take the group's drawing plan,
then pick devices; deviate whenever the figure argues for it, and say so in `notes`.

---

## How to read this

**The records.** Every number here comes from the **152 mechanism semantic records** in
`lab/extracted/corpus_semantics.jsonl` (rows with `"kind": "mechanism"`), aggregated in
`mech-prescreen/semantics/stats/report.md` and `stats.json`; the free text is `texts.md`, the
per-record index `exemplars.md`. The 152 are **exemplar candidates**, not a random sample: good
figures with a render, about 30 per group (logic: all that qualified), chosen to spread drawn bases,
author-source availability and venues (ASPLOS 25/26, NSDI 23–26, OSDI 23–26, SOSP 23–25). Read every
share below as *"among good mechanism figures a labeller picked as worth learning from"*, not as the
population rate. Group definitions and the 706-figure population counts are in
[`mech-prescreen/typedisc/types_v3.md`](../../../mech-prescreen/typedisc/types_v3.md).

**How the shares were computed.** Each record's `layout.*` and `content.*` fields were tallied whole,
per primary group; percentages are over the records that *recorded a value* for that field, which is
152 for most fields but 81 for `frame_template` (single-panel figures record none), 67 for
`panels_per_record`, 36 for `steps_per_record` and 49 for `values`. Counts per record are quoted as
median / q3 / p90 / max. Nothing here was recomputed for this file.

**Two kinds of citation.** A figure id in `code font` points at a record in `exemplars.md`, which
carries its PNG path. Ids marked **★** were opened and looked at while this file was written, so
claims about how those are *drawn* are first-hand; unmarked ids carry claims taken from that
record's own `reusable_patterns`, `encoding` and `panels[].differs` text. Open the PNG before you
borrow a device. **Inside the skill**, 146 of the 152 live in `assets/exemplars/figures/<id>/` (`print.png`,
`preview.png` when the author SVG exists, `source.svg`, `semantics.json`, `manifest.json`); the corpus paths
quoted above are provenance only and are not shipped with the skill.

**What is a "must" here.** Only print physics: **width fits the column** (single ≈240 pt, target
246–253; double ≈504 pt, target 510–536) and **no type below 5 pt**, body 5.5–7.5 pt.

Everything else in this file is "the corpus usually…". The numbers that *are* quality signals
(shape count, text runs, fill colours, dashes, mixed corners, connector segments, single-column
height) live in [`style-rules.md`](style-rules.md) — §7 for step markers, §8 for type, §9 for
density, §10 for size and aspect, §12 for what separates the two kinds. **Do not repeat them here;
cross-reference.** Colours come from [`../palettes.md`](../palettes.md), encodings from
[`../encoding.md`](../encoding.md), the spec fields from [`../spec-guide.md`](../spec-guide.md) §7.
Pitfall bullets in this file are pointers only; the diagnoses and fixes belong in `anti-patterns.md`.

---

## Choosing the group, the base, the arrangement

*Everything in this section is a reference to check your own idea against, not a decision procedure to obey.
Start from what the figure must make the reader see; then use the questions and tables to name the nearest
common shape, borrow what helps, and keep whatever the content needs that the corpus does not show. A figure
that is none of the five groups is allowed (`group: other`) — describe its reading path in `notes` instead.*

### The five questions, in priority order

Ask them in order and keep every yes. **The first yes is the primary group**; later yeses go in
`meta.mechanism.groups`. The order is not arbitrary: panels contain frames, frames contain a
structure, and a structure carries the numbered overlay.

1. **Are alternatives drawn side by side in a shared template?** → `comparison` (36 records, 24%).
2. **Is the same instance drawn in successive states?** → `evolution` (29, 19%).
3. **Is the main drawn structure a state machine or a decision flow?** → `logic` (29, 19%).
4. **Does an ordered numbered trace run through a structure drawn once?** → `walkthrough` (26, 17%).
5. **None of the above?** → `anatomy` (32, 21%).

Then: **are the concrete values the content** (tables, matrices, rows of numbers the reader checks)?
If yes, set `worked_example: true` — 50 of 152 (33%) do. Values written beside boxes are
annotations, not a worked example.

Groups combine. 30 of the 152 carry a secondary group; the commonest secondary tag by far is
**walkthrough (17 of 30, 57%)** — a numbered trace laid over a comparison, an evolution or a state
machine. All five logic records with a second group take walkthrough. Counting any membership:
walkthrough 43 (24%), comparison 40 (22%), evolution 34 (19%), anatomy 33 (18%), logic 32 (18%).

### Then the drawn base

`meta.mechanism.base` names the surface the story sits on and picks the parts
(`assets/symbols/index.json` → `by_subtype.mechanism`). Across the 152: component 26 (17%),
timeline 19 (12%), state-machine 18 (12%), mixed 13 (9%), topology 12 (8%), graph 12 (8%),
tree 12 (8%), data-structure 11 (7%), flowchart 10 (7%), table 8 (5%), scene 5 (3%), code 5 (3%).
See [Drawn bases](#drawn-bases). One record (`nsdi24-068_figtex18` ★) recorded `circuit`, which the
spec enum does not have — put a circuit under `mixed` and say so in `notes`.

### Then the arrangement

`meta.mechanism.arrangement` is the mechanism counterpart of `meta.template`
(`meta.template` is then `"mechanism"`).

| arrangement | all | comparison | evolution | logic | walkthrough | anatomy |
|---|---|---|---|---|---|---|
| `single` | 69 (45%) | – | 3 (10%) | 22 (76%) | 20 (77%) | 24 (75%) |
| `panels-row` | 38 (25%) | 25 (69%) | 5 (17%) | 2 (7%) | 4 (15%) | 2 (6%) |
| `panels-grid` | 14 (9%) | 2 (6%) | 9 (31%) | 1 (3%) | 1 (4%) | 1 (3%) |
| `panels-column` | 13 (9%) | 8 (22%) | 1 (3%) | 2 (7%) | – | 2 (6%) |
| `frames-row` | 8 (5%) | 1 (3%) | 7 (24%) | – | – | – |
| `inset` | 3 (2%) | – | – | 1 (3%) | 1 (4%) | 1 (3%) |
| `stacked-timeline` | 3 (2%) | – | 1 (3%) | 1 (3%) | – | 1 (3%) |
| `frames-column` | 2 (1%) | – | 2 (7%) | – | – | – |
| `other` | 2 (1%) | – | 1 (3%) | – | – | 1 (3%) |

| panels | all | comparison | evolution | logic | walkthrough | anatomy |
|---|---|---|---|---|---|---|
| 1 | 70 (46%) | – | 3 (10%) | 23 (79%) | 20 (77%) | 24 (75%) |
| 2 | 36 (24%) | 17 (47%) | 6 (21%) | 5 (17%) | 3 (12%) | 5 (16%) |
| 3 | 24 (16%) | 12 (33%) | 7 (24%) | 1 (3%) | 2 (8%) | 2 (6%) |
| 4 | 15 (10%) | 5 (14%) | 8 (28%) | – | 1 (4%) | 1 (3%) |
| 5–10 | 7 (5%) | 2 (6%) | 4 (14%) | – | – | – |

Read the two tables together: **the group decides whether there are panels at all, and the
arrangement then follows almost mechanically.** Comparison never draws one panel; logic, walkthrough
and anatomy draw one three times out of four. Panels per multi-panel record: median 3 (q3 3, p90 4,
max 9 for evolution, 10 for one comparison). Panel axis: `alternatives` 102, `time` 93 — and they
do not mix, `alternatives` is 100% of comparison's panels, `time` is 96% of evolution's.

**Double column: 24 of 152 (16%)** by the index (`index.column`); the records' own `layout.column`
field says 27 (18%), the gap being five records that left it blank. By group: walkthrough 7/26
(27%), evolution 6/29 (21%), comparison 7/36 (19%), logic 3/29 (10%), **anatomy 1/32 (3%)**. Go
double only when something physically does not fit at 240 pt — many frames (`osdi26-068_fig6` ★ at
10, `asplos26-094_fig3` at 9), a long lifeline set (`osdi23-020_fig9`), a wide escalation chain
(`sosp25-053_fig5` ★), or a dense wide graph (`asplos25-142_fig6`). A static anatomy almost never
needs it. Size and aspect targets: style-rules §10 and its figure-size table.

### Other defaults worth knowing before you start

- **Direction** left-right 76 (50%), mixed 46 (30%), top-down 29 (19%), bottom-up 1. "Mixed" is not
  sloppiness — it is the normal reading of a grid of frames or an FSM.
- **Delta marking** colour 80 (53%), none 39 (26%), callout 16 (10%), badge 10 (7%), dashed-ghost 5
  (3%), strike 1, bold-stroke 1. **Frame template** (over the 81 multi-panel records that recorded
  one) aligned 38 (47%), free 26 (32%), identical 17 (21%).
- **Step markers** none 93 (61%), circled-numbers 30 (20%), plain-numbers 11 (7%), letters 10 (7%),
  labelled-arrows 7 (5%), timeline-ticks 1. Note `meta.step_markers` has no `plain-numbers` or
  `timeline-ticks` value — record the intent in `notes` when the drawing wants bare digits.
- **Legend** none 106 (70%), inside 23 (15%), right 12 (8%), below 9 (6%), above 1, per-panel 1.
  **Nesting depth** 1 → 101 (66%), 2 → 35 (23%), 0 → 15 (10%), 3 → 1. **Lanes** in 59 (39%).
  **Zoom callout** in 9 (6%). **Text density** dense 81 (53%), moderate 48 (32%), sparse 23 (15%).
- **Budget per record:** elements median 10 (q3 12, p90 15, max 32), relations median 6 (q3 8,
  p90 11, max 30), palette entries median 5 (q3 6, p90 7, max 13). Count the template once — a label
  repeated in four aligned panels is one element. Highlighting is normal: 22.8% of all elements
  across the 152 are flagged `highlighted`.

---

## comparison — 36 records (24%)

*Reference, not recipe: the plan, numbers and variants below describe what these 36 good figures did.
Use them to strengthen a layout that comes from your figure's content; when the content asks for something
else, draw that and say why in the plan.*

The same template drawn two or more times, once per alternative (a design, a policy, a
configuration, a case), so the reader can compare outcomes. Panels are parallel alternatives, **not
moments in time**. `depicts` is "a design comparison" in 34 of 36 (94%) — if it is not, check you
have not mislabelled an evolution.

### Drawing plan

1. **Fix the panel template first**, on paper, before drawing anything: the boxes, lanes or cells
   every alternative shares, and where each sits.
2. **Decide what differs, in one sentence per panel** (`panels[].differs`). If you cannot write that
   sentence, the panels are not comparable and the figure is really two figures.
3. **Lay the panels out.** Row 25/36 (69%); column 8 (22%) when the template is wide or the
   alternatives are two software stacks read top-down; grid 2 (6%).
4. **Align them.** `frame_template: aligned` in 25 (69%) — same skeleton, contents differ;
   `identical` in 7 (19%) when even positions are fixed; `free` in only 4 (11%). Add `constraints`
   for same-row / same-column across panels.
5. **Name each panel.** A title above or a bold caption below; `(a)/(b)/(c)` tags are common but not
   universal.
6. **Mark the difference once, the same way in every panel.** Colour 20 (56%), callout 7 (19%),
   badge 4 (11%), none 4 (11%), strike 1.
7. **Give the verdict** when the figure takes sides — **59.6% of comparison panels carry one**.
8. Last: cut. Comparison has the *lowest* element and relation counts of the five groups — elements
   median 8.5 (q3 11, p90 13), relations median 4 (q3 5, p90 9). A comparison earns its width by
   repeating little, not by showing much.

### Numbers

Panels 2 → 17 (47%), 3 → 12 (33%), 4 → 5 (14%), 5 → 1, 10 → 1; median 2 (q3 3, max 5).
Direction left-right 17 (47%), top-down 11 (31%), mixed 7 (19%), bottom-up 1 (3%) — the only group
where top-down reaches a third, because stacked alternatives are read downward.
Step markers none 26 (72%), circled 5 (14%), letters 4 (11%), timeline-ticks 1.
Legend none 27 (75%). Lanes 18 (50%) — the highest of the five, tied with nothing.
Nesting 1 → 21 (58%), 2 → 12 (33%). Text density dense 22 (61%). Worked example 14 (39%).
Bases: component 8 (22%), timeline 6 (17%), graph 4 (11%), then tree / table / data-structure 3 each.
Relations skew hard to `data` — 105 of 181 (58%), vs 36% corpus-wide.

### Variants

- **Two-way, baseline vs ours — 17 records (47%), the modal comparison.** `asplos25-006_fig1` ★
  stacks two dashed Device pairs on one fwd/bwd/update template and lets the added thick blue
  AllGather bars plus the red collective names be the whole delta — no panel letters at all.
  `osdi23-048_fig4` ★ is two 3-lane and 2-lane swimlanes where the difference *is* the extra lane.
  Also `asplos26-030_fig4`, `sosp24-035_fig2`, `osdi25-010_fig7`, `asplos26-074_fig4`.
- **Three or more, escalating to a verdict — 12 at three panels, 5 at four.** `asplos25-038_fig1` ★
  runs the identical request→function→GPU-bar chain under three allocation policies and closes each
  panel with the same bold line, `Occupied GPUs: 4 / 3 / 2`; a shared legend spans the full width
  above all three. `osdi26-040_fig1` ★ separates its three software stacks with **dashed vertical
  rules rather than boxes** and titles each with a two-line bold caption below. `nsdi25-037_fig4`
  redraws one worked example as three decision-diagram encodings so node counts can be compared;
  `asplos26-047_figtex2` gives each of four circuits a derived-cost caption (depth, GHZ width).
- **A key or baseline panel that is not an alternative.** `nsdi24-095_fig3` opens with the plain RNN
  cell, then two solutions; `sosp24-024_fig3` opens with the whole un-partitioned MatMul; 
  `asplos25-018_fig6` opens with the constellation setup; `asplos26-021_fig1` puts plain arithmetic
  in (a) and the circuit that realises it in (b). Declare the key panel in `panels[]` with an empty
  `verdict` so the drawer does not score it.
- **Fan from one shared state.** `sosp25-060_fig4` ★ draws the starting cache once at the left and
  three diagonal labelled arrows `(a)/(b)/(c)` out to three result grids, each closed by a
  green/amber face icon and a `Hit` / `No hit` line. Recorded as `panels-column`; it is really a fan
  (see [Inventing an arrangement](#inventing-an-arrangement)). `nsdi24-029_fig6` runs
  before-grid → labelled rule box → after-grid *inside* each of three dashed panels.
- **A panel that is itself a sequence — 5 records also carry `evolution`.** `osdi26-068_fig6` ★ is
  two case rows of 6 and 4 lettered frames over one fixed 5-server roster; `sosp25-047_fig11` is five
  before/after pairs, one per case of a rule's case split; `sosp24-024_fig3`'s panel (c) nests a
  Step 0 / Shift / Step 1 micro-sequence, which that record's own weakness field flags as something
  the flat `panels[]` vocabulary cannot express.
- **Free layout — 4 records (11%).** Use it when the alternatives genuinely have different shapes:
  `nsdi24-097_fig7` pairs one phase-plane plot with two stacked waveform panels; `osdi25-003_fig4`
  puts two unlike sub-figures either side of a dashed divider.
- **Verdict devices:** a repeated score line (`asplos25-038_fig1` ★ "Occupied GPUs: N"); a
  check/cross scorecard (`asplos26-026_fig10`, Mem and Throughput rows under every panel); a word in
  the panel title (`osdi26-040_fig1` ★); a face icon (`sosp25-060_fig4` ★); a derived-cost caption
  (`asplos26-047_figtex2`); a bug icon on the wrong result (`osdi23-022_fig1`, `osdi23-022_fig14`);
  a dashed callout ringing the failure (`sosp24-011_fig7`).

### Exemplars

`assets/exemplars/mechanism/comparison/index.json` lists all 35 (starred first, one-line notes); each figure lives in `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed; `preview.png` is the author render when there is one), then `manifest.json` and `semantics.json`. They are reference and reinforcement: borrow the device that serves your figure; the layout itself follows what this mechanism has to show, and may look like none of them.

| id | base | arrangement | what to learn |
|---|---|---|---|
| `asplos25-018_fig6` ★ | scene | panels-row ×3 | Keep the satellite-row/day-column grid, colours and callout box identical across panels, and change only each dashed arrow's source row (same satellite vs. any satellite) so the drop in change-% reads on its own — but satellite icons stay unlabelled. |
| `asplos25-038_fig1` ★ | component | panels-row ×3 | One full-width legend above three panels; identical icon chain inside each; one bold verdict line at the same y in every panel |
| `asplos26-026_fig10` ★ | table | panels-column ×3 | A two-line check/cross scorecard under every alternative; roman numerals for the sub-steps that build the winner |
| `asplos26-067_fig5` ★ | state-machine | panels-row ×4 | Draw the synthesized protocol and both source protocols with the same lifeline-plus-boxed-state notation so states and messages line up panel to panel, and carry one two-colour domain tint through every panel. |
| `asplos26-074_fig4` ★ | component | panels-column ×2 | Stack both variants on one aligned input row, colour every occurrence of the same weight value identically in both, so sixteen boxes shrinking to four reads as a colour count — but the routing order still needs tracing. |
| `nsdi24-029_fig6` ★ | data-structure | panels-row ×3 | before-grid → labelled rule box → after-grid, repeated per panel; a dashed hatched box holds whatever falls out |
| `nsdi24-095_fig3` ★ | component | panels-row ×3 | Redraw the same GRU box as a diagonal staircase across time, grey out steps outside focus, and wrap only what must persist in constrained storage with one yellow halo — small around one hidden state, wide around every raw input. |
| `nsdi24-097_fig7` ★ | graph | panels-row ×2 | Fan two trajectories from one shared origin in a phase-plane panel, then stack the matching good/bad time-series beneath shared dashed reference lines so amplitude differences line up visually — but (a)'s colours don't match (b)/(c)'s. |
| `nsdi25-035_fig1` ★ | component | panels-row ×2 | Colour-code each step type once (orange = context ops, blue = request/poll) and reuse those colours in both panels, then bracket the idle span the async version fills with useful work instead of a thread switch. |
| `nsdi26-074_fig4` ★ | graph | panels-grid ×4 | Define each alternate path's colour once in a legend table, redraw the identical background graph per solution, and change only the numbers stacked on each coloured edge — but two stacked numbers per short segment make the graph dense. |
| `nsdi26-082_fig4` ★ | graph | panels-row ×4 | Give each small reusable unit a number badge once (① Linear with its tensor-state tags on every edge), then build every candidate by stacking two numbered units and swapping only the one connecting communication operator between them. |
| `osdi23-029_fig3` ★ | table | panels-row ×2 | Keep one colour per model across both panels; draw it as a whole tile under replication and subdivide that tile into shards under model parallelism, sharing one 1x/2x/4x row axis across the divider — but identical shard groups go unnoticed. |

Starred 12 of 35; the other 23 are in `index.json` with one-line notes (9 further starred ones included).

### Pitfalls

- Panels that do not share a template are not a comparison — the reader cannot diff them
  position-by-position (`nsdi23-085_fig1`'s own weakness note).
- No highlight on what moved: `sosp25-001_fig11` leaves the reader to compare two block lists by hand.
- Reused labels across panels (`a`–`l`, `1`–`4`, `Hello`/`World`) so elements are identifiable only
  by panel + position — `nsdi24-029_fig6`, `sosp25-060_fig4` ★.
- A notation introduced but never legended (`→` vs `⇒` in `nsdi24-029_fig6`).
- Titles so long they replace the panel tags, breaking every automated and human index
  (`osdi26-040_fig1` ★).

---

## evolution — 29 records (19%)

*Reference, not recipe: the plan, numbers and variants below describe what these 29 good figures did.
Use them to strengthen a layout that comes from your figure's content; when the content asks for something
else, draw that and say why in the plan.*

The same instance of a structure drawn in successive frames to show how its state changes.
`depicts` is "one algorithm run" in 21 of 29 (72%). The axis is **time**: 93 of evolution's 97
declared panels use `axis: time`.

### Drawing plan

1. **Draw the frame template once**, with every element that survives the whole sequence.
2. **Fix positions across frames.** `identical` 8 (30%), `aligned` 10 (37%), `free` 9 (33%) — but
   the `free` third is mostly figures whose frames are deliberately *different kinds of picture*
   (below), not sloppy ones. When one instance is being followed, keep it identical.
3. **Write one delta list per frame** (`deltas[]`, `change` = added / removed / changed /
   highlighted / moved / replaced). This is the discipline that keeps the frames aligned.
4. **Mark the change the same way everywhere.** Colour 20 (69%) — the strongest colour preference of
   any group; then badge 3, dashed-ghost 3, none 2, bold-stroke 1.
5. **Say what happens between frames**: a chevron or block arrow, a named-operation arrow, or a
   numbered stage box. See the variants.
6. **Caption each frame** where it sits — `(a) Original Packet`, `Rollout iter i+1`, `Time-step 3`.
7. **Choose the layout by frame count.** 2–3 frames in a row; 4+ usually wrap into a grid.
8. If values change frame to frame, set `worked_example` — **52% of evolution records do**, the
   highest of the five groups.

### Numbers

Arrangement `panels-grid` 9 (31%), `frames-row` 7 (24%), `panels-row` 5 (17%), `single` 3 (10%),
`frames-column` 2 (7%), then one each of `panels-column`, `stacked-timeline`, `other`.
Panels 4 → 8 (28%), 3 → 7 (24%), 2 → 6 (21%), 1 → 3 (10%), 5 → 2, then 6, 7, 9 once each;
median 3 (q3 4, p90 5.2, max 9).
Direction left-right 14 (48%), mixed 12 (41%), top-down 3 (10%).
Step markers none 15 (52%), circled 7 (24%), letters 4 (14%), labelled-arrows 2 (7%), plain 1.
Legend none 18 (62%), inside 4, right 4, below 3. Lanes 12 (41%). Zoom callout 3 (10%).
Elements median 10 (q3 11, p90 13, max 14) — the tightest ceiling of the five; relations median 5
(q3 7, p90 8.2, max 13). Panels with a verdict: 24.7%. Relations carrying a step: 25.6%.
Bases: mixed 6 (21%), tree 4 (14%), then component / timeline / topology / table 3 each (10%).

### Variants

- **Before/after pair — 6 records at two panels (21%).** `nsdi24-023_fig5` mirrors the tensor grid
  either side of one simulated packet loss; `nsdi24-086_fig11` stacks the baseline block chain above
  the augmented one (`frames-column`); `asplos25-147_fig6` puts the two topologies side by side with
  an open chevron between them and recolours one edge red→green.
- **Step sequence in a row — `frames-row` 7 (24%).** `nsdi25-040_fig10` ★ is the clean case: three
  identical stacked-header frames, `(a) Original / (b) Masqed / (c) Restored`, with the operation
  name written *along the connecting arrow* (Egress-Prog, Ingress-Prog) and only the italic text
  inside the coloured rows changing. `nsdi23-003_fig7` puts **numbered stage-name boxes between the
  columns** rather than inside them. `sosp25-039_fig1` runs four stage frames along one bold Time
  arrow and encodes the environment in each frame's **border dash pattern**.
- **Grid of frames — `panels-grid` 9 (31%), the group's modal arrangement.** `osdi25-013_fig2`
  replays one 4×8 table for five time-steps, recomputing a green derived-count column each frame;
  `asplos26-094_fig2` ★ packs six lettered construction stages into one column, each tagged
  `(a)`–`(f)` top-left with its waveform directly under its circuit; `asplos25-092_fig5` lays out 7
  enumerated states grouped by **nested coloured boundary boxes** standing for two bounds on a
  parameter; `osdi26-136_fig7` is a 2×2 progression from two automata to their product.
- **Frames as rows inside a panel.** `osdi26-024_fig9` ★ draws two boxed panels (a) DFS and (b) BFS;
  inside each, frames run left to right separated by **pale chevron block arrows**, a dashed
  rectangle groups the speculative sub-sequence, each frame has its own caption below, and the delta
  is **red numerals on the V/C values that just changed** against black ones that did not.
- **Frames along a timeline / stacked timeline — 3 records.** `osdi23-020_fig9` stacks five time
  columns of one swimlane and hatches the instant of the atomic transition; `asplos25-082_fig2` is a
  *single* Gantt-style timeline where the evolution is periodic checkpoint boxes, a dashed lost one,
  a fault bolt and a curved recovery arrow.
- **Before/after overlaid in one frame — `single` 3 (10%).** `nsdi23-065_fig2` ★ shows the migrated
  proclet as a **dashed ghost circle at the vacated slot** plus a curved blue arrow with a red
  `Migration` label; `nsdi23-008_fig5` keeps the old binding solid and draws the new one as a red
  dashed arrow, with numbered captions carrying the order. Cheap and compact — but it reads
  correctly only if the numbers or the caption tell the reader which state came first.
- **Construction, where each frame adds a part rather than changes a value.** `asplos26-094_fig2` ★
  (a)–(f) each bolt one more block onto a running worked example; `nsdi25-062_fig12` chains four
  numbered stages that are four *different diagram types* (graph, table, algorithm box, timeline),
  unified only by per-component colour. Here `frame_template: free` is correct.
- **What separates the frames**, ranked by what the records describe: a chevron or block arrow
  (`asplos25-147_fig6`, `osdi26-024_fig9` ★, `nsdi23-003_fig7`); a named-operation arrow
  (`nsdi25-040_fig10` ★, `sosp25-047_fig11`'s bold grey `Vec.` arrow, `nsdi26-074_fig2`'s
  `Optimize f_ABC, f_ABB`); a plain gap with per-frame captions (`osdi25-013_fig2`); a dashed box
  grouping a sub-sequence (`osdi26-024_fig9` ★).

### Exemplars

`assets/exemplars/mechanism/evolution/index.json` lists all 33 (starred first, one-line notes); each figure lives in `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed; `preview.png` is the author render when there is one), then `manifest.json` and `semantics.json`. They are reference and reinforcement: borrow the device that serves your figure; the layout itself follows what this mechanism has to show, and may look like none of them.

| id | base | arrangement | what to learn |
|---|---|---|---|
| `asplos25-047_fig4` ★ | mixed | frames-row ×4 | Let each phase's container shape mimic its tournament format — grid of pools, two-region blob, cyclic graph, simple pair — but keep the winner dot's colour and transition-icon arrow identical everywhere so the eye tracks one shrinking population. |
| `asplos25-092_fig5` ★ | state-machine | panels-grid ×7 | Repeat the same small sub-diagram once per state, varying only its token values, and nest the tighter bound's states inside the looser bound's box as a literal subset — but draw no arrow back to the source circuit. |
| `asplos25-147_fig6` ★ | topology | panels-row ×2 | Redraw the identical topology before and after, joined by one open chevron arrow; recolour only the edges whose island-crossing status changed (red = crosses, green = doesn't), keeping every data-volume label in place so the swap reads by colour alone. |
| `asplos26-094_fig2` ★ | mixed | panels-grid ×6 | Six construction stages inside one column, each adding a block to one running example; waveform under its circuit |
| `nsdi23-008_fig5` ★ | component | single | Draw the old binding in plain solid lines, overlay just the changed link as one accent dashed arrow in the same frame, and number callouts 1-4 for rule-change, reroute, drop, pickup — but it only reads right in that order. |
| `nsdi24-023_fig5` ★ | data-structure | frames-row ×2 | Number and colour-group the same grid tensor identically on both sides (sub-tensor = colour = packet); mark one packet lost with a red X, then blank only the grid cells that packet owned in the reconstructed tensor. |
| `nsdi25-040_fig10` ★ | data-structure | frames-row ×3 | Three identical frames; the operation name rides the arrow between them; only the text inside the fixed coloured rows changes |
| `nsdi25-062_fig12` ★ | mixed | other ×4 | Keep one colour per logical item across four different diagram types (graph, table, algorithm box, timeline), and outline in red just the table rows the search picked — but two DFG nodes share the same green, blurring their schedule blocks. |
| `nsdi26-023_fig9` ★ | timeline | panels-grid ×4 | Redraw the same dashed scope box smaller so it wraps only the recovering worker, swap the now-excluded neighbours for their log-table stand-ins, and pair full-width Gantt bars before/after so the blank rows and a bracketed percentage argue the speedup directly. |
| `osdi26-024_fig9` ★ | tree | frames-row ×2 | Chevrons between frames, a dashed box around a speculative sub-sequence, red numerals for just-changed values, a legend strip on top |
| `osdi26-079_fig6` ★ | tree | frames-column ×3 | One numbered 1–5 recipe listed in a side legend and replayed identically at each of three tree levels |
| `osdi26-086_fig1` ★ | flowchart | frames-row ×3 | Alternate process and artifact boxes in one row, reuse the same artifact template each time and change one bold coloured word to mark progress, and hang a dashed worked-equation callout under each artifact — but never legend the colour code. |

Starred 12 of 33; the other 21 are in `index.json` with one-line notes (2 further starred ones included).

### Pitfalls

- Near-identical frames with nothing marking the change — five tables the reader must diff by hand
  (`osdi25-013_fig2`'s own weakness).
- Too many frames for the column: 9 and 10 frames only work double-column and still lose labels
  (`asplos26-094_fig3`, `osdi26-068_fig6` ★).
- Node identities that restart per frame or per example, so "node 2" means two things
  (`osdi26-024_fig9` ★, `osdi26-079_fig6`).
- Only before and after, no intermediate state, when the mechanism *is* the intermediate
  (`asplos26-076_fig9` ★).
- Frames drawn in different visual metaphors without warning the reader (`asplos25-047_fig4`).

---

## logic — 29 records (19%)

*Reference, not recipe: the plan, numbers and variants below describe what these 29 good figures did.
Use them to strengthen a layout that comes from your figure's content; when the content asks for something
else, draw that and say why in the plan.*

The drawn structure *is* control logic: named states with transitions labelled by event or guard, or
a decision flowchart / decision tree with labelled branches. `depicts` is "one policy decision" in
15 (52%) and "one algorithm run" in 6 (21%).

### Drawing plan

1. **Pick one shape per node kind** and keep it: state vs decision vs action vs terminal. This is
   where `corners: mixed` earns its keep (style-rules §4).
2. **Draw the node-link graph in one layout** — layered, circular, or a left-to-right cascade.
   `single`, one panel, in 22 of 29 (76%).
3. **Label every edge with its trigger or guard.** 84% of logic transitions carry a guard — an
   unlabelled transition is the group's signature defect.
4. **Minimise crossings.** Logic carries the highest relation count of the five groups: median 8
   (q3 11, p90 15.2, max 17) against 6 corpus-wide, on median 9 elements.
5. **Use colour for node role, not decoration** — and legend it if it means anything. Logic has the
   highest in-figure legend rate: `inside` 7 (24%) against 15% corpus-wide.
6. **Add numbers only if there is a real order to add**; 22 of 29 (76%) use none.
7. Keep it spare: logic is the only group where `moderate` text density leads (14, 48%) over
   `dense` (10, 34%), and where `worked_example` almost never applies (2, 7%).

### Numbers

Bases state-machine 13 (45%), flowchart 8 (28%), tree 3 (10%), component 2, mixed 2, timeline 1.
Logic sizes: states median 3 (q3 5, p90 7.4, max 12); transitions median 5 (q3 8, p90 9.2, max 15);
20 of 29 records declare decisions; guard share 0.836.
Element kinds are dominated by `state` — 90 of 284 (32%) against 8% corpus-wide.
Relations: transition 120 (45%) and control 116 (43%) together are 88%; `data` is just 22 (8%).
Delta marking colour 13 (45%) and none 13 (45%) split evenly — half of logic figures mark nothing,
because there is nothing changing.
Direction left-right 13 (45%), mixed 12 (41%), top-down 4 (14%). Lanes only 6 (21%), the lowest.
Nesting 1 → 22 (76%). Double column 3 (10%).
Author-source availability is lowest here (0.31; `index.tool` is `unknown` for 14 of 29, 48%), so
the style fields of logic records lean on the PDF render more than elsewhere.

### Variants

- **Finite state machine — base `state-machine` 13 (45%).** `nsdi23-079_fig7` ★ is the instructive
  one: five numbered states drawn as small folded-corner boxes, one fill colour per role, guards in
  *italic on long curved arrows*, and the **state names written outside the nodes as underlined
  headings** so the box itself only has to hold a digit. `nsdi24-031_fig9` gives each state an accent
  colour and paints its adjoining arrows to match. `osdi25-038_fig9` draws its four states as
  repeated **record boxes in a 2×2 grid** with the two flag bits inside, so the flag values *are* the
  state. `osdi24-051_fig4` badges each state with an icon pair (trust glyph + lock glyph) instead of
  a fill, letting two independent attributes be read off one node.
- **Flowchart — base `flowchart` 8 (28%).** `asplos26-041_fig7` ★ colours by functional stage
  (count / check / act / clean up), labels every branch `Y`/`N`, and nests a `for every WL_i in
  BLK_tgt` loop box holding its own decision and action. `nsdi23-079_fig1` arcs two long bypass
  arrows over the top of the chain for fast paths, and marks the two lock-needing steps with pink
  fill, a padlock icon and a legend. `sosp24-014_fig6` uses three colours as a role code (component /
  condition / action); `nsdi26-030_fig8` drops a concrete `D D O O D` event row *inside* each
  processing box, grounding an abstract loop.
- **Decision tree or cascade.** `nsdi24-068_fig5` ★ leaves the two decision boxes white and gives
  each of four terminal recommendations its own pastel fill, so the eye lands on the outcome; branch
  conditions are written in full words on the edges, and one node fans out three ways rather than
  two. `nsdi24-067_fig5` chains three diamonds left to right, dropping each `Y` straight down to a
  terminal box and running `N` onward, so the hardest unhandled case ends up at the far right.
  `nsdi25-016_fig7` cascades seven threshold checks, grouped into dashed subsystem lanes.
- **FSM plus a numbered overlay — 5 of 29 also carry `walkthrough`.** `nsdi25-027_fig1` ★ puts
  circled ①–④ on exactly the four transitions the prose discusses, while every other edge stays
  unnumbered; `nsdi23-073_fig4` uses circled 1–3 for **priority order of guard evaluation, not
  time**, and reuses the same three badges inside a nested sub-loop (which its weakness field flags
  as confusable). `sosp25-053_fig5` ★ numbers nine guarded edges of an escalation chain, the circled
  number sitting *under* the guard label on each edge.
- **Marking an extension over a known protocol.** `nsdi25-027_fig1` ★ draws vanilla Raft in solid
  purple and CCF's added state and edges in **dashed gold**, so the familiar skeleton stays readable
  under the contribution. `asplos26-057_fig9` inverts it (dashed = the default MSI transitions,
  solid = the six new ones) and reserves red for the two new states. `asplos26-091_fig2` uses
  solid vs dashed for CPU-triggered vs hardware-triggered transitions and carries a small
  arrow-colour legend inside the diagram.
- **The machine beside the thing it governs.** `osdi26-076_fig8` pairs an annotated concrete cache
  structure (a) with the abstract I/S/A machine (b) under one colour key; `asplos26-091_fig2` stacks
  register bit-fields over the state model; `osdi26-122_fig12` puts a decision diamond at the centre
  of the figure and an **inset cost curve** beside it that justifies where the threshold sits.
- **Two-level / refinement chains.** `sosp25-063_fig2` runs two parallel horizontal state chains at
  different abstraction levels and links them with dashed many-to-one `Refines` arrows.

### Exemplars

`assets/exemplars/mechanism/logic/index.json` lists all 31 (starred first, one-line notes); each figure lives in `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed; `preview.png` is the author render when there is one), then `manifest.json` and `semantics.json`. They are reference and reinforcement: borrow the device that serves your figure; the layout itself follows what this mechanism has to show, and may look like none of them.

| id | base | arrangement | what to learn |
|---|---|---|---|
| `nsdi23-073_fig4` ★ | state-machine | single | Put the shared hub state at the centre with peer actions fanning out on numbered, guarded arrows that all loop back to it; draw one action's internal loop as a smaller copy of that exact hub-and-spoke shape inside its box. |
| `nsdi23-079_fig7` ★ | state-machine | single | Keep the node small (a digit), put the state's name outside it as a heading, guards in italic on curved arrows |
| `nsdi24-105_fig5` ★ | state-machine | single | Bracket the loop with dashed start/end pseudo-states; fan out from start into parallel same-shaped classification branches, one per case, each running its own action box before rejoining the end state and looping back to start. |
| `nsdi25-027_fig1` ★ | state-machine | single | Solid = the known protocol, dashed = this paper's addition, for both nodes and edges; circle only the transitions the text discusses |
| `nsdi25-044_fig9` ★ | mixed | panels-grid ×3 | Repeat one small template, a running history feeding a state-checker box with a red terminal outcome, once for the traced value and once for its frequency; number both ①② and combine their verdicts in a third numbered checker. |
| `nsdi26-022_fig4` ★ | flowchart | single | Chain the diamonds vertically and route every NO arrow into one shared fallback box instead of a separate box per branch, then tie the flowchart to the candidate-pool icon cluster with a single bracket leader line, not repeated arrows. |
| `nsdi26-030_fig8` ★ | flowchart | single | Put a real buffer of coloured event tiles inside each box, and loop its gate diamond back into that box on 'no' but forward to the next box on 'yes' — but three stacked diamonds stay dense to trace. |
| `osdi23-032_fig8` ★ | flowchart | panels-row ×2 | Bracket the delegate's one memory round-trip as a 'Time Window,' with dashed arrows fanning back to queued duplicate requests instead of repeating the trip; draw the bypass path looping visibly under every memory-side phase box. |
| `osdi24-003_fig11` ★ | component | single | Compute the verdict once at the top and re-draw its two accent colours plus Prioritize/Abort text at every layer below, even as each layer's queue icon changes shape — but reused bare letters force reading by position, not name. |
| `sosp24-014_fig6` ★ | flowchart | single | Give every box one of three shape+colour roles (blue rounded = component, violet diamond = condition, tan dashed = action), and feed each side-car database with a dashed 'Update' arrow kept separate from its plain read arrow. |
| `sosp25-017_fig8` ★ | mixed | panels-column ×2 | Embed the literal small state-lookup table inside the decision diamond itself, reuse that exact diamond+table shape for both the source and destination check, and bracket the two halves in one accent colour to name the phases. |

Starred 11 of 31; the other 20 are in `index.json` with one-line notes.

### Pitfalls

- Unlabelled transitions — the figure cannot say what fires them (`nsdi23-079_fig7` ★'s own weakness
  on its 1→3 and 1→2 arrows).
- The same guard text on two different edges, so source and target position are the only
  disambiguator (`nsdi24-031_fig9`, `osdi25-038_fig9`).
- A branch with no drawn continuation (`asplos26-041_fig7` ★'s `N` exit; `nsdi25-016_fig7`'s missing
  `Normal` leaf).
- Entry and exit arrows with no source or sink state (`osdi26-076_fig8`'s `Allocate`).
- Calling a two-row sequential flowchart a state machine in the caption (`nsdi24-061_fig3`).

---

## walkthrough — 26 records (17%)

*Reference, not recipe: the plan, numbers and variants below describe what these 26 good figures did.
Use them to strengthen a layout that comes from your figure's content; when the content asks for something
else, draw that and say why in the plan.*

One structure drawn **once**, with numbered or lettered markers tracing one request, packet or
operation through it in reading order. The numbers must give **order along a path** — node IDs or
phase names do not make a walkthrough. `depicts`: one algorithm run 16 (62%), one protocol exchange
8 (31%).

### Drawing plan

1. **Draw the structure once**, at the size it needs. Walkthrough carries the heaviest element load
   of the five: median 10 but q3 14.8 and p90 16.5 (corpus q3 is 12), and `box` + `label` alone are
   69% of its elements.
2. **Pick the path** and make it visually distinct: an accent colour, a heavier stroke, a shaded
   band, or a wavy line through the boxes.
3. **Place the markers along it in order.** Every walkthrough record has markers:
   circled-numbers 13 (50%), plain-numbers 8 (31%), labelled-arrows 4 (15%), letters 1 (4%);
   `none` is 0. Digits 20 (77%) beat letters-or-other 6 (23%).
4. **Keep 3–8 steps.** Median 4 (q3 6, p90 8.5, max 10). **61% of a walkthrough's relations carry a
   step number** — so the steps live mostly on the edges, not on the nodes.
5. **Say what each step carries** (`steps[].carries`) — **100% of walkthrough steps do**, against
   97.6% overall. This is what lets the drawer colour one object along the path.
6. **Add a side legend only if the steps need sentences.** Legend none 19 (73%), inside 4 (15%),
   right 2 (8%), below 1.
7. **Write the caption to list the steps in prose.** Numbers that the caption does not narrate are a
   recurring weakness in this group.

### Numbers

Arrangement `single` 20 (77%), `panels-row` 4 (15%), `panels-grid` 1, `inset` 1.
Direction left-right 16 (62%) — the strongest of the five groups. Lanes 11 (42%). Nesting 1 → 15
(58%), 2 → 7 (27%). Delta marking colour 16 (62%), none 5 (19%), callout 4 (15%), badge 1.
Relations median 6.5 (q3 8.8, p90 11, max 20). Text density dense 16 (62%). Worked example 7 (27%).
**Double column 7 of 26 (27%)** — the widest group. Confidence is lowest here: high 18 (69%),
medium 7 (27%), because the step semantics often come from the caption rather than the paper body.
Bases: component 7 (27%), timeline 4 (15%), data-structure 4 (15%), topology 3 (12%), code 3 (12%),
graph 2, then tree / state-machine / mixed 1 each.

### Variants

- **On a component row or a small topology — 10 records (38%).** `nsdi25-034_fig6` ★ is the textbook
  shape: `Client | Switch | Server` in a row, four plain numerals `1–4` sitting *on* alternating
  arrows with the message name in italic beside each, and a small key table hung off the Client with
  the colliding row highlighted salmon. `nsdi23-089_fig1` ★ threads a **bold wavy black line**
  through the process boxes as the request's own path, drops circled ①–⑦ along it, and runs a
  separate dotted blue channel underneath into a grey `Backend Trace Collectors` band;
  `nsdi23-089_fig2` then redraws the *same* base with one new red channel layered on — a
  sibling-figure device worth stealing.
- **On a data structure — 4 (15%).** `asplos25-033_fig4` walks circled 1–3 (persist / commit /
  flush) across a dashed host/firmware divider, colour-tagging each transaction so it can be followed
  through every structure; `osdi25-031_fig8` uses a dashed **zoom callout** into one chunk where
  three circled sub-steps live; `sosp25-039_fig3` gives each of four phases its own numbered
  sub-steps.
- **On a timeline or lifelines — 4 (15%).** `nsdi26-043_figtex18` crosses two lanes with five
  numbered, differently-coloured diagonal arrows; `asplos26-030_fig9` uses plain numerals 1–5 as
  **dashed tick columns** over a circuit; `osdi24-020_fig4` deliberately uses **no numerals at all**
  — three lifelines read top-down, with teal vs green marking the two protocol phases. A timeline
  that reads top-down does not need numbers, and this is the honest exception to the "always number"
  instinct.
- **On a graph or tree, with the step state spelled out beside it.** `osdi26-082_fig3` ★ pairs a
  graph carrying a shaded expansion path and bold orange arrows with an adjoining
  `Candidate Pool (Sorted)` table that grows `step1 / step2 / step3 / result`, plus a four-swatch
  legend in the bottom-left corner — all inside one single-column strip. `nsdi26-037_fig3` walks
  circled 1–5 through one root-to-leaf trace of a branch-and-bound tree and parks the evidence-set
  table in the corner.
- **On code — 3 (12%).** `osdi23-049_fig10` tags code listing lines `func0/func1/func2` and matches
  them to a node chain; `osdi26-037_fig5` runs one **bold vertical code-flow arrow** with circled ①
  and ② marking two calls; `osdi25-016_fig6` links IR lines to a timeline with curved `Correspond`
  arrows defined in a legend.
- **With a side legend.** `osdi26-079_fig6` lists the numbered 1–5 recipe once at the right and
  replays the same circled numbers inside each of three frames; `sosp25-053_fig5` ★ puts a
  **dashed-border legend box in the bottom-left corner** mapping four fills to four node roles
  (entrypoint / eviction / policy / diagnosis result) and shapes to kinds (ellipse = check or result,
  rounded rectangle = action).
- **Where the marker sits.** On the arrow (`nsdi25-034_fig6` ★); at the node, exactly where the
  action happens (`asplos25-033_fig4`); under the guard label on the edge (`sosp25-053_fig5` ★); as
  a lettered family per subsystem, `B1/H2/X1/L4` (`osdi26-048_fig2` — whose own weakness is that the
  causal order across letter families is then not explicit).

### Exemplars

`assets/exemplars/mechanism/walkthrough/index.json` lists all 43 (starred first, one-line notes); each figure lives in `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed; `preview.png` is the author render when there is one), then `manifest.json` and `semantics.json`. They are reference and reinforcement: borrow the device that serves your figure; the layout itself follows what this mechanism has to show, and may look like none of them.

| id | base | arrangement | what to learn |
|---|---|---|---|
| `asplos25-033_fig4` ★ | data-structure | single | Colour-tag the object being followed so it stays identifiable in every structure it passes through |
| `asplos25-046_fig16` ★ | timeline | panels-row ×2 | Encode 'sum' as stacked blocks and 'take-the-max' as overlaid/multiplexed blocks in the same bar, so the arithmetic operator is legible from the drawing; carry each numbered sub-segment from the source bars into the same spot in the combined bar. |
| `asplos25-142_fig6` ★ | graph | single | Keep one fixed colour per primitive type across the graph, overlay a second layer of dashed pass-labelled boxes to narrate which rewrite touched which subgraph — but repeating the same Pass-3 label three times leaves 'why the same pass' unanswered. |
| `nsdi26-037_fig3` ★ | tree | single | Colour every terminal node the same blue but caption each with the specific reason it stopped (Learned, Dedupe, Non-minimal), and collapse a proven-bounded subtree into a flat labelled shelf instead of drawing its boxes. |
| `nsdi26-075_fig11` ★ | component | single | Merge labelled inputs into one prediction box with a single bracket, then draw the next step's bound as two horizontal rails (max_ratio, min_ratio) with the value's box nested between them — but the two outcome labels differ only by capitalization. |
| `osdi24-024_fig9` ★ | data-structure | single | Reduce the full heatmap to one colour-matching summary row inside the process box, hand off Top-K as a literal dashed 'Selected Idx' box, then reuse those exact numbers as column headers on a new, differently-coloured matrix. |
| `osdi25-031_fig8` ★ | data-structure | inset ×2 | A dashed zoom callout from one element of the overview into the numbered sub-steps that happen inside it |
| `osdi26-048_fig2` ★ | mixed | single | Give each subsystem its own colour and its own lettered step count (B/H/X/L) instead of one global number, and draw the causal jump as one arrow crossing straight from the stalled thread's timeline into the box that resolves it. |
| `osdi26-082_fig3` ★ | graph | single | Pair the walked structure with a small table that spells out the state after each step; corner legend; ❶/❷ used for roles, not order |
| `sosp23-030_fig8` ★ | component | single | Run one numbered step-path across both dashed phase boxes without renumbering at the boundary, saturate the decision boxes' colour, and fold the weight-feedback loop into the victim-pick step's arrow instead of its own number — easy to miss that dependency. |
| `sosp25-008_fig3` ★ | component | panels-row ×3 | Definitions column, per-party identical computation boxes, message-order ring; one worked numeric example highlighted throughout |
| `sosp25-042_fig3` ★ | component | single | Draw the worked example (jobs routed to lettered on-prem/cloud nodes) directly above the component diagram that generates those routes, marking only the pipeline stages with red 'Step 1/2a/2b' labels, distinct from the small circled job-ID numbers. |

Starred 12 of 43; the other 31 are in `index.json` with one-line notes (1 further starred ones included).

### Pitfalls

- Two interleaved sub-pipelines in one figure so the reading order is not obvious without the
  numbers (`nsdi24-018_fig4`).
- A feedback or dependency edge that a numbered step depends on but is not itself numbered
  (`sosp23-030_fig8`'s Weights arrow).
- The same marker glyph used for two different things in one figure — step index and job ID
  (`sosp25-042_fig3`), or two parallel "1"s read as two steps (`sosp23-030_fig8`).
- Figure and prose numbering the same two acts in opposite order (`osdi26-082_fig3` ★).
- Steps whose meaning exists only in the caption, never in the figure (`nsdi23-089_fig1` ★ steps 4–7).

---

## anatomy — 32 records (21%)

*Reference, not recipe: the plan, numbers and variants below describe what these 32 good figures did.
Use them to strengthen a layout that comes from your figure's content; when the content asks for something
else, draw that and say why in the plan.*

A static figure where none of the above applies: one structure opened up and explained at a single
moment. It is the residual class, and it is the **largest** one — expect variety, not a shape.
`depicts`: one algorithm run 15 (47%), one component 8 (25%), one data structure 6 (19%).

### Drawing plan

1. **Choose the one moment** the figure depicts and commit to it. 30 of 32 (94%) carry no step
   markers at all; 15 (47%) mark no delta either.
2. **Show sub-structure by containment**, not by arrows: nesting 1 → 23 (72%), 2 → 7 (22%).
3. **Keep one reading direction.** left-right 16 (50%), then mixed 8 and top-down 8 (25% each).
4. **Emphasise the part the text discusses** — colour 11 (34%), callout 5 (16%), badge 1; and 25.4%
   of anatomy elements are flagged `highlighted`, the second-highest rate of the five.
5. **Label everything.** `label` is 96 of 344 anatomy elements (28%), `node` 65 and `box` 75 — the
   text is the figure.
6. **Draw it single-column.** 31 of 32 (97%) are; anatomy is the one group where a double-column
   canvas is almost certainly the wrong answer.
7. If the values are the point, set `worked_example` — 12 (38%) do.

### Numbers

Arrangement `single` 24 (75%), then `panels-row` 2, `panels-column` 2, and one each of
`panels-grid`, `inset`, `stacked-timeline`, `other`.
Relations: data 96 (44%), control 54 (25%), **mapping 25 (12%)** and **pointer 10 (5%)** — the
highest shares of those two kinds anywhere, because anatomy figures explain correspondences.
Elements median 10 (q3 13, p90 14.9, max 21); relations median 6.5 (q3 8.2, p90 10.9, max 16).
Legend none 24 (75%). Lanes 12 (38%). Zoom callout 3 (9%). Text density dense 17 (53%).
Bases: component 6 (19%), graph 5 (16%), timeline 5 (16%), topology 4 (12%), mixed 3 (9%), then
data-structure / table / scene 2 each, tree / flowchart / circuit 1 each.
Author-source availability is highest here (0.844), so anatomy's recorded style fields are the most
trustworthy of the five. Every anatomy record carries at least one recorded weakness (median 2).

### Variants

- **Component internals — 6 (19%).** `asplos26-053_fig1` ★ rings the contribution in a **dashed
  green region box** labelled `Verified` against `Unverified` outside, names the boundary in matching
  caption colours below, and draws `ExprHigh`/`ExprLow` twice to make the rewrite loop visible.
  `sosp24-007_fig3` ★ repeats a `Layer_i` / `Ramp_i` pair, writes the **running count on the arrows
  between stages** (`15 samples`, `13 samples`, …) and compresses the middle of a 12-stage chain with
  an ellipsis. `sosp23-002_fig5` draws each stage as a `1 … N` pair with crossing arrows;
  `nsdi24-023_figtex23` mirrors two grey sender/receiver containers of blue sub-blocks.
- **Data structure at one moment.** `sosp23-016_fig5` ★ fans three arrows from a small green query
  box to three highlighted rows of an otherwise empty table — **the blank rows are the argument**
  (non-contiguity), which is why the table must be drawn bigger than the data.
  `nsdi26-043_fig5` and `nsdi26-043_fig9` are node × round grids with pointer arrows and one
  more-saturated cell marking the running example.
- **Placement map** — identical containers filled differently. `sosp24-011_figtex2` colours a worker
  grid on **two independent axes** (icon outline = pipeline stage, arrow colour = data-parallel row)
  so one red-X'd cell and its fork-then-merge reroute stand out against both; `osdi25-050_fig10`
  zooms one node of a leaf-spine cloud into its NIC/GPU/NVLink internals.
- **Graph or tree with a highlighted subset.** `asplos26-026_fig9` colours blue exactly the eight
  tokens sent for verification inside a larger drafted tree; `asplos26-103_figtex7` draws one expert
  pipeline in full operator detail and **leaves its sibling as an empty grey box**;
  `sosp25-047_fig15` keeps the original graph inside a dashed `SDG` box and attaches every new node
  outside it; `sosp25-001_fig12` overlaps translucent hyperedge regions so one vertex visibly
  belongs to three at once.
- **Worked computation.** `nsdi24-068_figtex18` ★ traces four numbers through a five-comparator
  sorting network, **each value keeping one colour across every wire**, with a small comparator
  legend set off to the right; `asplos25-053_fig4` groups a join's four regions in dashed boxes and
  fans many probe arrows between them; `asplos25-151_fig12` keys a coloured grid schedule to a small
  reference tree at the left margin.
- **Minimal sketch or scene — 5 records use base `scene`.** `asplos26-148_fig4` has **no text at
  all**: colour vs grey separates the in-frustum Gaussians from the rest, the frustum tinted pale
  yellow. `asplos25-034_fig1` matches upper-case 3D objects to lower-case 2D projections by colour
  and a projection ray. `nsdi24-023_figtex7` annotates a sawtooth curve with speech-bubble callouts
  either side of a threshold line.
- **Two panels that are not a comparison.** `nsdi25-064_fig4` is `inset` — a mesh topology above, one
  node's pipeline zoomed below; `nsdi23-085_fig1` sets two unlike serverless patterns side by side
  and its own weakness note says the lack of a shared template is the cost.

### Exemplars

`assets/exemplars/mechanism/anatomy/index.json` lists all 33 (starred first, one-line notes); each figure lives in `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed; `preview.png` is the author render when there is one), then `manifest.json` and `semantics.json`. They are reference and reinforcement: borrow the device that serves your figure; the layout itself follows what this mechanism has to show, and may look like none of them.

| id | base | arrangement | what to learn |
|---|---|---|---|
| `asplos26-053_fig1` ★ | component | single | A dashed region boundary naming what is and is not the contribution, with matching caption colours; draw a loop by drawing its stages twice |
| `asplos26-103_figtex7` ★ | graph | single | Collapse the repeated sibling into an empty placeholder and draw one instance in full; annotate every edge with the shape it carries |
| `asplos26-132_fig2` ★ | component | single | Colour-match each inline sentence icon to its encoder and token run, bracket every run with its count, and neck the backbone between many inputs and two decoders — but the output row drops that colour link. |
| `nsdi24-023_figtex23` ★ | component | single | Mirror sender/receiver as matching grey boxes of blue sub-blocks; give bitrate control and fast re-sync each a bent-back feedback arrow, plus one arrow crossing the network to request re-sync — but identical labels leave only position telling sides apart. |
| `nsdi24-086_fig7` ★ | component | single | Chain two dashed-outline layer boxes left to right; draw only the fully-connected layer's surviving connections as individual weight-labelled arrows, skipping the dense mesh — but the same +1 label repeats across three arrows, so colour alone tells them apart. |
| `nsdi25-047_fig5` ★ | graph | other ×4 | Draw several identical small curve panels side by side, mark the one value harvested from each with a dot, then run a dashed arrow from each dot into the matching point on one larger derived curve below. |
| `nsdi25-064_fig4` ★ | mixed | inset ×2 | Topology above, one node's pipeline zoomed below, joined by one bold arrow; a bracket naming which stages a timeout covers |
| `nsdi26-043_fig5` ★ | timeline | single | Colour every grid cell by its shard chain, leave others blank, and draw pointer arrows only between same-colour cells, with leader cells in a third colour where several chains converge — but dense crossings blur exact endpoints. |
| `nsdi26-043_fig9` ★ | timeline | single | Overlay both chains on one round grid and arrow each transaction up to the crowned round that commits it, so latency reads as column count — but four separate colours blur which pair is the fast path. |
| `sosp23-002_fig5` ★ | component | single | Give every stage an identical '1...N' box pair and fully cross-connect neighboring stages so any replica can reach any replica — but the dashed-vs-solid arrow meaning (async vs sync RPC) is explained only in the caption, never on the figure. |
| `sosp24-007_fig3` ★ | component | single | Running counts written on the arrows between repeated stages; an ellipsis to compress the middle; a dashed box naming the pre-existing part |
| `sosp24-011_figtex2` ★ | topology | single | A grid coloured on two independent axes, a red X for the failure, fork-then-merge arrows for the reroute, a taught-once legend |

Starred 12 of 33; the other 21 are in `index.json` with one-line notes (2 further starred ones included).

### Pitfalls

- Colour as the *only* correspondence cue, so the figure dies in greyscale (`asplos25-034_fig1`).
- A colour code used without any legend or caption gloss (`asplos25-053_fig4`, `osdi26-086_fig1`).
- Labels reused for sender-side and receiver-side instances, distinguishable only by position
  (`nsdi24-023_figtex23`).
- An intentional omission (an empty cloud, a collapsed sibling, blank rows) that reads as a mistake
  (`osdi25-050_fig10`, `asplos26-103_figtex7`, `sosp23-016_fig5` ★).
- Density without a reason: anatomy is dense in 53% of records and every record carries a weakness,
  most often small type. See style-rules §9 before adding one more label.

---

## Drawn bases

The base picks the default node and edge kinds and the parts subset. Only bases with ≥5 records
are listed; `scene` (5) and `mixed` (13) have no fixed vocabulary by definition.

| base | n | how the corpus draws it | spec kinds | see |
|---|---|---|---|---|
| **component** | 26 (17%) | Named boxes, sometimes with ports, wired by labelled arrows; sub-blocks by containment; a dashed box names the region that is the contribution. Leads in comparison (8) and walkthrough (7). | nodes `module` / `compute` / `store` / `queue` / `port`; containers `solid` / `dashed`; edges `data`, `control`, `feedback` | `asplos26-053_fig1` ★, `sosp24-007_fig3` ★, `nsdi25-034_fig6` ★ |
| **timeline** | 19 (12%) | One lane per actor with a lifeline, messages as diagonal or horizontal arrows read top-to-bottom, phase brackets over intervals; or Gantt-style bars on a shared axis. | lanes `lifeline` (+ one `time` ruler); edges `message` with `order`; annotations `bracket` | `osdi23-048_fig4` ★, `osdi24-020_fig4`, `asplos25-082_fig2` |
| **state-machine** | 18 (12%) | Named states (circle, box or record) plus guarded transitions; colour per state role; 45% of logic records use it, and it appears in all five groups. | nodes `state`; edges `transition` with `guard` | `nsdi23-079_fig7` ★, `nsdi25-027_fig1` ★, `osdi25-038_fig9` |
| **topology** | 12 (8%) | Nodes as icons or circles with physical links, often no arrowheads; bandwidths, route lists or failure marks annotate the links. | nodes `module` / `external` / `icon`; edges `data`, `dependency` | `nsdi23-089_fig1` ★, `sosp24-011_figtex2`, `osdi25-050_fig5` |
| **graph** | 12 (8%) | A real node-link DAG or hypergraph; edges annotated with shapes, weights or mappings; a subset highlighted. | nodes `module` / `other`; edges `dependency`, `data`, `mapping` | `osdi26-082_fig3` ★, `sosp25-001_fig12`, `asplos26-103_figtex7` |
| **tree** | 12 (8%) | Root at the top or left, children fanning out; node fill encodes status; leaves carry the outcome. Used for search trees and decision trees alike. | nodes `module` / `decision`; edges `control` with `guard` for a decision tree | `nsdi24-068_fig5` ★, `osdi26-024_fig9` ★, `nsdi26-037_fig3` |
| **data-structure** | 11 (7%) | Slots and cells in a grid, pointers between them, a highlighted cell or row; empty cells often carry meaning. | nodes `slot` / `cell` with `grid` hints; edges `pointer` | `sosp23-016_fig5` ★, `nsdi25-040_fig10` ★, `asplos25-033_fig4` |
| **flowchart** | 10 (7%) | Diamonds for decisions, boxes for actions, `Y`/`N` on every branch, loop-back arrows, colour by functional stage. | nodes `decision` + `module`; edges `control` with `guard` | `asplos26-041_fig7` ★, `nsdi23-079_fig1`, `sosp24-014_fig6` |
| **table** | 8 (5%) | A grid of cells read row by row, one derived column, cell fill encoding state; almost always a worked example. | nodes `cell` / `slot`; `values[]` for the contents | `osdi25-013_fig2`, `sosp25-060_fig4` ★, `asplos25-053_fig4` |
| **code** | 5 (3%) | A listing beside a diagram, tied line-for-line by leader lines, tags or a vertical code-flow arrow. | nodes `note` for the listing; edges `mapping` to the diagram | `osdi23-049_fig10`, `osdi26-037_fig5`, `osdi23-022_fig1` |

**Element-kind mapping.** The records use a slightly wider vocabulary than the spec's `nodes[].kind`
enum. `box` and `node` → `module` (or `compute` / `store` when the role is clear); `state` → `state`;
`row` → `cell` or a `lane`, depending on whether it holds values or groups them; `slot` / `cell` /
`port` / `icon` / `actor` map directly; `label` is not a node at all — it belongs in `annotations[]`.
Relation kinds map one-to-one except `timeline-message` → `message`.

Across the 152, elements run label 415 (27%), box 364 (23%), node 222 (14%), state 118 (8%),
row 105 (7%), icon 84 (5%), lane 84 (5%), cell 83 (5%), port 43 (3%), actor 22, slot 12, table 2.
Relations run data 363 (36%), control 287 (28%), transition 186 (18%), mapping 62 (6%),
dependency 48 (5%), timeline-message 45 (4%), pointer 22 (2%).

---

## Worked examples

**50 of 152 records (33%)** are marked `worked_example`; 49 carry a `values` block (one marked
record recorded none). By group: evolution 15 (52%), comparison 14 (39%), anatomy 12 (38%),
walkthrough 7 (27%), logic 2 (7%). `values.linked_by` is recorded as colour 21 (43%) and
position 18 (37%), with a further 5 "colour: …", 3 "position: …", 1 "colour-coded" and 1 "dashed" —
so in round terms **colour links about 27 of 49 and position about 21**, and almost nothing else is
used.

Four devices carry most of it.

- **One colour per tracked value, held across every representation of it.** `asplos26-094_fig2` ★
  paints the value 3 red at the counter match, at the spike, and inside the captured register, and a
  second example value 1 blue, so one number can be traced through six increasingly complex circuit
  panels. `nsdi24-068_figtex18` ★ gives each of four inputs (9, 6, 4, 8) its own colour and lets the
  colours' final order *be* the proof that the network sorts. `nsdi23-003_fig7` combines a coloured
  header fill with a hex `priv_label` to track two records across four columns whose row positions
  deliberately change.
- **Position, in a table whose cells refill per frame.** `osdi25-013_fig2` replays one 4×8 receiver
  table over five time-steps with a green cumulative-ack column recomputed each frame;
  `osdi25-031_fig11` replays a per-layer table step by step with a running `Sum` row and a
  check/cross verdict against a fixed target. Position-linked values need `frame_template:
  identical` — the reader's eye is doing the linking.
- **Explicit result cells.** `asplos26-021_fig1` puts the two black result boxes (66, 67) in the
  plain-arithmetic panel and re-derives them under the crossbar panel, so the circuit is *checked*;
  `sosp25-008_fig3` highlights the reconstruction row `4 = 31 xor 63 xor 36` in orange;
  `asplos25-038_fig1` ★ uses one bold `Occupied GPUs: N` line per panel; `asplos26-026_fig10` uses a
  green-check / red-cross pair per panel. Set `values[].role: "result"` on these.
- **Values on the edges rather than in cells.** `nsdi26-074_fig2` and `nsdi26-074_fig4` annotate
  every edge `used/capacity` and keep every background number identical between panels, so the two
  or three numbers that change are the whole argument; `asplos25-147_fig6` writes MB beside each
  arrow; `osdi25-050_fig5` writes the bandwidth beside each link.

A fifth, smaller device: **a reference table in a corner** supplying the data every node's
computation refers back to — `nsdi26-037_fig3`'s evidence sets, `nsdi25-062_fig12`'s profiling table
with red outlines on the rows the search selected, `nsdi26-074_fig4`'s panel (a).

Alignment and tabular figures belong to [`../encoding.md`](../encoding.md); the caution from
`types_v3.md` still stands — the `worked-example` marker is labeller-sensitive (7–21% across four
labellers, about three in four holding up on inspection), so **look at the figure before trusting
the flag**.

---

## Inventing an arrangement

The nine `arrangement` values do not cover the corpus, and the corpus knows it. Two records are
already recorded `other` (`nsdi25-062_fig12`, `nsdi25-047_fig5`), and several more are recorded
under a value that does not really describe them:

- `sosp25-060_fig4` ★ is recorded `panels-column ×3` but is drawn as a **fan** — one shared start at
  the left, three diagonal labelled arrows out to three outcomes.
- `osdi26-068_fig6` ★ is recorded `frames-row ×10` but is drawn as **two case rows** of 6 and 4
  frames; its own `panels[]` lists two entries, so the record disagrees with itself.
- `nsdi25-047_fig5` converges three small plots **downward** into one composite plot below — neither
  a row nor a grid, and its own weakness note says the panels read right to left.
- `sosp24-024_fig3`'s weakness field states outright that a nested evolution inside a comparison
  panel is something "the flat `panels` vocabulary of this schema record cannot fully separate".

So: **invent the arrangement when the figure asks for one.** That is not a failure mode; it is the
ordinary answer for the figures the nine values do not fit. What you may not do is invent
*unstructured*.

**Keep these four regardless of shape:**

1. **One stated reading order.** Write it down in `notes` in one sentence ("outer ring clockwise
   from the top-left node, then down into the inset"). Every record in the corpus has a
   `reading_order`; a figure whose order cannot be stated in one sentence is a figure that has not
   been designed.
2. **One template repeated.** If anything repeats — a panel, a frame, a party, a lane — draw it once
   and repeat it exactly. Put the shared elements in the spec *without* a `panel` field and let the
   drawer replicate them.
3. **Changes marked once, and the same way.** Fill `deltas[]` even when the arrangement is exotic;
   the delta list is what makes any arrangement legible.
4. **The two print musts:** column width and ≥5 pt type. An invented arrangement that needs 300 pt
   of width at single column is not an invention, it is a mis-sized figure.

**What to write in the spec:**

```jsonc
"meta": { "kind": "mechanism", "template": "mechanism", "mechanism": {
  "group": "comparison", "base": "table", "arrangement": "other",
  "frame_template": "aligned", "delta_marking": "badge",
  "notes": "Fan, not a column: one shared 'current cache' at the left, three lettered diagonal arrows out to three outcome grids, each closed by a pass/fail face. Reading order: start box, then (a)/(b)/(c) top to bottom. panels-row/column/grid were all rejected because the panels share one drawn origin instead of sitting in a strip."
}}
```

Still declare `panels[]` with `order` and `axis` (the drawer needs the reading order and whether the
panels are alternatives or moments), still use `constraints` for the alignments you want, and still
write `panels[].differs` per panel.

**How the self-check treats it.** `arrangement: "other"` is a claim, not an escape hatch. The check
is: *can `notes` name the shape and say why each of the nine standard values was rejected?* If it
can, `other` passes. If `notes` is empty, or says only "custom layout", the figure almost certainly
wants `panels-row` or `panels-grid` and has drifted. Two further checks that apply to any invented
arrangement: the reading order in `notes` must match the `order` fields, and every repeated element
must appear once in the spec, not once per panel.

---

## Spec mapping

Field-by-field semantics are in [`../spec-guide.md`](../spec-guide.md) §7 and
`../spec-schema.json`; this table only says which blocks each group needs.

| group | required blocks | typical `meta.mechanism` | also usually |
|---|---|---|---|
| `comparison` | `panels[]` (≥2, `axis: alternatives`) with `differs`; `deltas[]`; `verdict` on the panels the figure scores | `arrangement: panels-row`, `frame_template: aligned`, `delta_marking: colour` | `constraints` for same-row/same-column; `legend` rarely (75% none) |
| `evolution` | `panels[]` (≥2, `axis: time`) in `order`; one `deltas[]` list per frame | `arrangement: panels-grid` or `frames-row`, `frame_template: identical`, `delta_marking: colour` | `values[]` (52% are worked examples); `annotations` of kind `label` between frames |
| `logic` | nodes `kind: state` / `decision`; edges `kind: transition` (or `control`) with `guard` on **every** branch | `arrangement: single`, `frame_template: none`, `delta_marking: none` | `legend` inside (24%, the highest rate); `corners: mixed` for the shape code |
| `walkthrough` | `steps[]` (3–8, contiguous `n`, each with `attached_to` and `carries`); `meta.step_markers` | `arrangement: single`, `delta_marking: colour` | `annotations` of kind `callout`; a `legend` only when steps need sentences |
| `anatomy` | nodes, containers and edges only — no panels, steps or logic block | `arrangement: single`, `frame_template: none`, `delta_marking: none` | `emphasis: accent` on the part the text discusses; `values[]` when 38% applies |
| marker `worked-example` | `values[]` with `role` (input / intermediate / result / key / index) and `links` between recurrences | `worked_example: true` | one colour per linked set; `= result` cells; `highlight` on the cell the text names |

`meta.template` is `"mechanism"` for every one of them. `base` selects the parts subset
(`assets/symbols/index.json` → `by_subtype.mechanism`); `arrangement` replaces the architecture
template id. Panels wrap in `<g id="p:<id>" data-kind="panel">`; template elements repeated inside a
panel get `data-panel` and an `@<panel>` id suffix; a changed element carries `data-delta`; values
are `v:<id>` with `data-kind="value"`. Routing a user's feedback to the field that changes ("align
the two columns", "mark the change in red", "add a before frame") is in spec-guide §7's last
paragraph.
