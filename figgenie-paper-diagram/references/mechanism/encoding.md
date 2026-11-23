# Visual encoding vocabulary — mechanism figures

What colour, line style, ghosting, markers, badges, highlights and legends are allowed to
*mean* in an OSDI/NSDI/SOSP/ASPLOS **mechanism** figure — the second figure kind of this skill:
how one part of a system works. Walkthroughs, successive frames, alternatives side by side,
control logic, one component opened up.

The architecture counterpart is `../encoding.md`. The measured style envelope (palette size,
stroke, type, density, canvas) is `style-rules.md` and is **not repeated here**. Palette role
names (`module`, `accent`, `container`, `lane`, `arrow-accent`, `text-muted`, …) are the ones in
`../palettes.md`; spec field names are the ones in `../spec-guide.md` §7 and `../spec-schema.json`.

## How to read this

**Sources.**

- **[stats]** — the per-group tables in `mech-prescreen/semantics/stats/report.md` and `stats.json`,
  over **152 mechanism semantic records** (exemplar candidates: good figures, ~30 per group —
  comparison 36, evolution 29, logic 29, walkthrough 26, anatomy 32).
- **[tally]** — counts made by this document over the free text of the same 152 records
  (`.../stats/texts.md`: `color_means`, `line_style_means`, `state_means`, `marker_means`,
  `emphasis`, `values`, `weakness`). These are **regex hits over model-written prose**: a convention
  a record does not mention is invisible, so every [tally] number is a floor.
- **Figures.** Every claim about how something is drawn names the figure id; ids resolve through
  `mech-prescreen/semantics/stats/exemplars.md` (corpus provenance, not shipped). Inside the skill, look at
  `assets/exemplars/figures/<id>/print.png` — 146 of the 152 are there (`references/mechanism/layouts.md`
  lists the starred ones per group).

**The non-rigidity principle** (corpus owner, non-negotiable). Mechanism figures vary far more than
architecture figures do, so this document records **observed conventions with their shares**, not
rules. "Must" appears only for print physics (contrast, minimum type size) and for the one genuinely
ambiguous case (one meaning per dashed style in a figure). Everywhere else the form is *"the corpus
usually …, N of M records"*, then **deviate when …**. Departing from a default for a stated reason
is not a defect: 39 of 152 records mark no delta at all, 33 use no line-style distinction whatever,
and 8 are deliberately monochrome — all good figures.

---

# Part A — Telling states and alternatives apart

The problem specific to this figure kind: the reader sees the *same thing twice* — two
alternatives, two moments, before and after — and must see in one glance what is different.

## A0. What the corpus marks the difference with

`layout.delta_marking` **[stats, n=152]**:

| marking | all | comparison | evolution | logic | walkthrough | anatomy |
|---|---|---|---|---|---|---|
| **colour** | 80 (53%) | 20 (56%) | 20 (69%) | 13 (45%) | 16 (62%) | 11 (34%) |
| none | 39 (26%) | 4 (11%) | 2 (7%) | 13 (45%) | 5 (19%) | 15 (47%) |
| callout | 16 (10%) | 7 (19%) | – | – | 4 (15%) | 5 (16%) |
| badge | 10 (7%) | 4 (11%) | 3 (10%) | 1 (3%) | 1 (4%) | 1 (3%) |
| dashed-ghost | 5 (3%) | – | 3 (10%) | 2 (7%) | – | – |
| strike | 1 (1%) | 1 (3%) | – | – | – | – |
| bold-stroke | 1 (1%) | – | 1 (3%) | – | – | – |

**Colour is the delta channel** in the three groups that have a delta (evolution 69%, walkthrough
62%, comparison 56%); **`none` is legitimate** exactly where there is nothing to mark — anatomy
(47%) and logic (45%) are static figures. The other half of the same fact:
`element_highlighted_share` = **0.228** **[stats]** (comparison 0.171, evolution 0.244, logic
0.220, walkthrough 0.259, anatomy 0.254) — roughly **one element in four or five** carries the
emphasis. Highlight half the elements and there is no emphasis left.

## A1. Colour on the changed element — the default

The changed, added or active element takes a saturated fill or stroke; everything else keeps the
neutral template.

- `osdi26-024_fig9` (evolution, looked at) is the tightest realisation: the same 4-node tree
  redrawn in ~10 frames at identical positions, only the node fill (grey = explored, yellow = main
  branch, green = speculative) and the `V:`/`C:` numbers changing — and the numbers that changed
  **in this frame** are set in red while unchanged ones stay black.
- `asplos25-147_fig6`: the same 20 MB edge is red in the left panel and green in the right.
  `nsdi23-008_fig5`: one red dashed arrow for the migrated P2→C2 binding amid black steady-state
  bindings. `asplos25-006_fig1`: thick blue bars mark AllGather, the one operation FSDP adds.
- `sosp23-030_fig8` (walkthrough, looked at): the figure is grey; **gold** on the chosen Eviction
  Victim and **pink** on Miss Key are the only saturated fills, sitting exactly on the two decision
  points the text discusses.

**Deviate when** the delta is structural rather than per-element — a box present in one panel and
not the other, a lane that appears, an extra state between two states. Then geometry is the delta
and colour adds nothing: `osdi25-010_fig7` tells F2FSJ from JBD2/EXT4 by how many dirty-state boxes
sit between Uptodate and Dirty; `osdi23-048_fig4` by the presence of a Switch lane;
`osdi26-040_fig1` by whether two boxes are stacked, side by side, or merged.

## A2. Dashed ghost of the old state

Only **5 of 152 [stats]** set `delta_marking: dashed-ghost` figure-wide (evolution 3, logic 2),
but **17 [tally]** use a dashed outline *somewhere* for a state that is old, lost, vacated,
pending or not-yet-there. It is a local device.

- `nsdi23-065_fig2` (evolution, looked at): a **dashed circle at the vacated slot** in Machine 0
  plus a blue curved arrow labelled `Migration` in red to the solid circle in Machine 1 — before
  and after overlaid in one frame. The record names the price: it "reads correctly only if the
  viewer follows the numbered captions".
- `asplos25-082_fig2` (evolution, looked at): the interrupted third checkpoint is an **empty dashed
  box** where completed ones are solid green; the reloaded `ckpt 2` is redrawn in blue — two
  devices, two different facts (lost vs reused).
- `sosp24-035_fig2`: dashed white outline = an empty/pending slot, solid grey = already resident.
  `osdi26-024_fig3`: dashed = branches not yet expanded and the `wait` point, which panel (b) fills
  with solid green speculative boxes.
- `nsdi25-027_fig1` (logic, looked at) inverts the channel: solid purple = Raft's original states
  and transitions, **dashed gold = CCF's additions** — the ghost marks the new layer over a known
  skeleton.

**Deviate when** dashed is already spent on panel borders or on a second relation kind (C4).
**One meaning per dashed style — this is the one place this document says *must*.**

## A3. Strike, callout, badge

**Strike.** **12 records [tally]** cross something out, almost always as a **red X over the
element** rather than a line through a label; `delta_marking: strike` is the figure-wide default in
exactly **1 of 152 [stats]**, so treat it as a per-element badge. `nsdi24-029_fig6` (comparison,
looked at) puts a **red X** over each preempted instance and collects the instances left idle in a
separate **dashed green hatched box** — two negatives, two markings. `sosp24-011_fig7` /
`sosp24-011_figtex2`: a GPU icon overlaid with an X = failed worker, with the `W_x_y` label
recoloured red as a redundant cue. `nsdi24-023_fig5`: a crossed-out packet, and the tensor cells it
mapped to turn white in the same grid positions. `sosp25-039_fig3`: a red strikethrough on the one
discarded ballot. `asplos26-094_fig3` reuses the glyph for a *blocked* concurrent access — "cannot"
rather than "removed".

**Callout.** **16 records [stats]** set `delta_marking: callout` (comparison 7, anatomy 5,
walkthrough 4, and **zero** in evolution and logic); **17 [tally]** name a callout, bracket or brace
as the emphasis device. `nsdi25-037_fig4`: a **red box** around the repeated sub-structure in (a)
and the merged one in (c) — the only accent in an otherwise black-and-white figure, mapping onto the
text's node-count argument. `osdi24-015_fig3` (looked at): a brace plus bold `Long interruption
time` over panel (c) and `Live migration` with a curved arrow in (d), and nothing else annotated.
`nsdi26-023_fig9`: the same **dashed red box** redrawn smaller in the with-ours panel — a callout
whose *size* is the claim — closed by a boxed `23% Faster Recovery`. `asplos25-082_fig2` (looked at):
dashed double-headed span arrows labelled `O_save` / `O_lost` / `O_restart`, brackets that quantify
rather than name. **Deviate when** there are more than about two: one red callout naming what must
not be missed is the idiom; five is noise.

**Badge.** **10 records [stats]** use `delta_marking: badge`; **11 [tally]** hang a status glyph on
an element — padlock (`nsdi23-079_fig1`, `osdi23-031_figtex1`, `osdi24-020_fig4`,
`osdi24-051_fig4`), crown for the current leader (`osdi26-068_fig6`, `nsdi26-043_fig9`), burst for a
crash (`osdi26-068_fig6`), red bolt for a fault (`asplos25-082_fig2`), bug for a wrong result
(`osdi23-022_fig1`, `osdi23-022_fig14`), devil face for an untrusted owner (`osdi24-051_fig4`),
no-phone prohibition (`sosp25-039_fig1`). `nsdi23-079_fig1` (logic, looked at) is the clean pattern:
a **gold padlock on exactly the two steps that need a lock**, a pink fill on the same two, and a
one-line in-figure legend (`Use locks to serialize concurrent executions.`) inside the drawing —
three redundant cues on one fact, which is why it survives at 5 pt.

## A4. Position — the same slot in every frame

**26 records [tally]** say positions are held fixed across frames; the layout field agrees: of the
81 multi-panel records, `frame_template` is **aligned 38 (47%)**, free 26 (32%), **identical 17
(21%) [stats]** — and within comparison, **aligned 25 of 36 (69%)**. This is the cheapest encoding
here and the one **15 records [tally]** name as their emphasis: *keep everything identical so the
only thing that moves is the change.*

- `nsdi25-040_fig10` (evolution, looked at): three frames `(a) Original` / `(b) Masqed` /
  `(c) Restored`, the same three stacked rows in the same order and colours (green IP Header,
  orange MAC Header, grey Payload). **Only the italic text inside the rows changes**, and the grey
  payload row is deliberately untouched in all three so the eye goes to the headers.
- `nsdi26-074_fig4`: "keeping every black background number and the green path identical between
  (c) and (d) isolates the red/orange numbers as the only thing that changed".
- `osdi24-015_fig3` (looked at): four policy panels on one S1/S2 lane template with one dashed
  vertical reference line at the same x in all four, so bar lengths compare by eye.
  `osdi25-013_fig2`: the same 4-row table redrawn per time-step, a receiver's state being just how
  many of its yellow cells are filled in that frame.

**Deviate when** the mechanism *is* a relocation — an oblivious sort, a reshuffle, a migration.
`nsdi23-003_fig7` says it directly: records move to different enclave slots at every stage, so
identity is carried by a **hex `priv_label` plus a header fill colour**, not by position. Colour
then does position's job, and must be introduced before the first move.

## A5. How comparison panels signal the verdict

**[stats]** `panels_with_verdict_share` = **0.421** overall; **0.596 in comparison**, 0.247 in
evolution, **0.0 in logic and anatomy**. **[tally]** 82 of 195 recorded panel lines carry an
explicit `-> verdict`, over 39 records; the wording splits into *ours/preferred/correct* 21,
*baseline/prior/original* 14, *wrong/bug/gap/slow* 19, other 28.

Four devices, usually stacked two deep:

1. **Check / cross glyphs** — 11 records [tally]. `asplos26-026_fig10` (looked at) puts a two-line
   scorecard under every panel (`Mem: 1× ✓` / `Throughput: 1× ✗`); panel (c), the paper's own
   design, is the only row with **two green checks**. `osdi25-031_fig11` marks each search step with
   a check or cross against the target slowdown.
2. **Red vs green** — rarer than you would guess: **14 records [tally]** use red for the wrong case,
   **10** green for the right one, and only **2 use both as an opposed pair**
   (`asplos26-026_fig10`, `sosp25-060_fig4`). Red-green is an idiom, not the norm.
3. **A face, icon or word** — `sosp25-060_fig4` (looked at) ends each lettered branch in a face plus
   text: two yellow sad faces with `No hit`, one green smiling face with `Hit: Hello`. Three
   redundant channels for one binary, which is why it also reads in greyscale.
4. **An "ours" accent, or simply the panel name** — `asplos26-047_figtex2` gives panel (d) a solid
   pink `Parallel Toffoli via Fanout` block where (a)–(c) have crossing SWAP wires;
   `osdi26-040_fig1` merges two boxes and labels the arrow `Generalization`; `nsdi26-082_fig4` keeps
   every candidate's framing identical so the one differing operator box is the verdict.

**The greyscale counter-example.** `osdi24-015_fig3` (looked at) is entirely black and white: the
Performance column reads `A Latency: ✓  B Latency: ✗` in plain black glyphs and only panel (d) gets
two checks. Its recorded weakness is honest ("greyscale-only encoding with small 5 pt labels makes
the four policies hard to tell apart"), but the *verdict* channel survives — a glyph is not a hue.

## A6. Conflicts seen in the corpus

- **One channel, two meanings** — 20 records [tally] flag this themselves. `nsdi24-029_fig6`: `→` vs
  `⇒` in the rule box mean same-stage vs cross-stage swap with nothing explaining which;
  `osdi26-024_fig9`: circled node ids 1–5 restart across three examples; `asplos25-082_fig2`: the
  nested checkpoint-composition legend reuses the main timeline's palette for a different purpose.
- **A ghost that looks like a blank** — `sosp24-024_fig3`: "the Shift sub-frame's dashed placeholder
  tiles look visually similar to the plain white 'not yet computed' output cells". **Two negatives
  that look alike** — `osdi26-068_fig6`: plain grey (stale) vs grey-plus-burst (crashed) is "subtle
  at this figure's size".
- **A delta with no marking** — `sosp25-001_fig11`: "no arrows or colour highlighting mark exactly
  which block moved … so the reader must compare the two per-device block lists by hand". That is
  what `delta_marking: none` costs when there *is* a delta.
- **A verdict only in the caption** — `sosp24-011_fig7` prints no `(a)`/`(b)` label on the figure.

## A7. Recommended default per group

| group | default delta marking | share behind it [stats] | deviate when |
|---|---|---|---|
| `comparison` | aligned shared template + **colour on what differs** + a per-panel verdict line | colour 20/36 (56%); aligned 25/36 (69%); verdict 0.596 | the difference is structural (a lane appears, boxes merge) → let geometry carry it; or the paper takes no side → omit the verdict rather than invent one |
| `evolution` | **identical frame template** + colour on the changed element only | colour 20/29 (69%); identical-or-aligned 18/27 | the structure relocates (sort, reshuffle) → track identity by colour + a stable id; or both states must share one frame → dashed ghost for the old slot |
| `logic` | **no delta marking**; states and guards are the content | none 13/29 (45%) | an extension is layered over a known protocol → solid = original, dashed + second hue = added (`nsdi25-027_fig1`); or one path is a worked example → two non-solid styles for its two segments (`nsdi24-079_fig7`) |
| `walkthrough` | **colour on the traced path** + markers along it | colour 16/26 (62%) | the structure is grey scaffolding and only the decision points matter → two saturated fills total (`sosp23-030_fig8`) |
| `anatomy` | **no delta**; a highlighted subset instead | none 15/32 (47%); highlighted share 0.254 | one region is the point → colour-vs-grey it (`asplos26-148_fig4`) or ring it (`nsdi25-037_fig4`) |

---

# Part B — Order and markers

## B0. The numbers

`layout.step_markers` **[stats, n=152]**:

| marker | all | comparison | evolution | logic | walkthrough | anatomy |
|---|---|---|---|---|---|---|
| none | 93 (61%) | 26 (72%) | 15 (52%) | 22 (76%) | – | 30 (94%) |
| circled-numbers | 30 (20%) | 5 (14%) | 7 (24%) | 5 (17%) | **13 (50%)** | – |
| plain-numbers | 11 (7%) | – | 1 (3%) | – | **8 (31%)** | 2 (6%) |
| letters | 10 (7%) | 4 (11%) | 4 (14%) | 1 (3%) | 1 (4%) | – |
| labelled-arrows | 7 (5%) | – | 2 (7%) | 1 (3%) | 4 (15%) | – |
| timeline-ticks | 1 (1%) | 1 (3%) | – | – | – | – |

`step_marker_style`: digits **29 (81%)**, letters-or-other 7 (19%) **[stats]**.
`relations_with_step_share` — the fraction of a figure's relations carrying a step number:
**0.184** overall, **0.612 walkthrough**, 0.256 evolution, 0.063 logic, 0.044 comparison, 0.023
anatomy **[stats]**.

Three things follow. **(i) Markers are a walkthrough device** — every walkthrough record has them,
94% of anatomy records have none. **(ii) Digits beat letters four to one.** **(iii) Even in a
walkthrough only about six relations in ten carry a number**; the rest of the path is read by
position. And `style-rules.md` §7 finds step numbering is **not** a quality signal here (δ=+0.08
n.s.; circled glyphs in 5.9% of good vs 2.5% of ok+bad) — the opposite of the architecture result.
Number when the order is not obvious from the layout, not as a checkbox.

## B1. Circled numbers vs plain numbers vs letters

**Circled numbers** (30 records [stats]) carry an **ordered traversal** and sit *on* the thing that
acts. `sosp23-030_fig8` (looked at) puts ①–⑤ directly on the arrows and junctions — propose
candidates → pick a weighted victim → log it → look up a miss → adjust weights.
`asplos26-021_fig1` (looked at) uses black filled discs with white digits ❶ ❷a ❷b ❸, where **2a and
2b are two halves of one physical step** (multiply along rows, accumulate down columns) —
sub-numbering instead of inventing a fifth step. `nsdi23-089_fig2` (looked at) draws ①–⑥ each **in
the colour of the channel they mark** — black for the request path, red for trigger and breadcrumb
traversal, blue for lazy reporting.

**Plain numbers** (11) do the same job at lower weight, and dominate where the surface is a circuit,
ruler or table: `asplos26-030_fig9` numbers five tick columns 1–5; `asplos26-047_fig7` lays a `1`–`8`
step ruler over a quantum circuit; `nsdi25-034_fig6` numbers four request/reply arrows.

**Letters** (10) index **panels or alternatives**, not order — `(a)/(b)/(c)` per panel is the
commonest use (`nsdi25-037_fig4`, `osdi24-015_fig3`, `sosp25-060_fig4`). Where letters do order
something they order *frames*: `osdi26-068_fig6` letters ten replay frames, `asplos26-094_fig2` six
construction stages. Roman numerals appear once, as a third level inside a panel
(`asplos26-026_fig10`: i/ii/iii for the three optimisations building panel (c)).

**Labelled arrows** (7) replace the number with the operation's name — strictly more informative
when there are only two or three transitions. `nsdi25-040_fig10` (looked at) labels the two
inter-frame arrows `Egress-Prog` / `Ingress-Prog` with a gear glyph; `sosp25-047_fig11` uses a bold
grey block arrow labelled `Vec.`; `nsdi26-074_fig2` one labelled `Optimize f_ABC, f_ABB`. **13
records [tally]** put a chevron or named-operation block arrow between frames as the separator — it
doubles as the order cue. **Timeline ticks** appear once (`osdi23-048_fig4`): where a time axis
supplies the order, the corpus lets position do the work and numbers nothing.

## B2. Numbers that are IDs, not order — a recorded trap

**7 records [tally]** state that their digits are identities, not a sequence:

- `osdi26-024_fig9` (looked at): "circled numbers 1-7 are persistent node identities, not step
  order" — circled, the glyph that promises order.
- `nsdi23-076_fig23`: the integers 0–15 in each node are collective ranks. `osdi26-024_fig3`: the
  printed 0.9 / 0.8 / 0.5 are reward values. `asplos26-013_fig8`: numbers on ellipses are Gaussian
  ids held constant across frames. `nsdi24-023_fig5`: digits 1–9 are tensor-element positions.
- `asplos26-074_fig4`: "the circled 1 / 2 label which panel is which design … not a sequence of
  steps" — a circled digit used as a panel tag.
- `sosp25-042_fig3` names the collision itself: "the small circled 1/2/3 job-ID labels … visually
  resemble the red Step 1/2a/2b markers but encode a different thing".

`types_v3.md` draws the same line: "Numbers that are only node IDs or phase names do not make a
walkthrough."

**Default.** If a figure needs both, give them different glyphs — filled circled digits for order,
bare digits or a prefixed id (`W_1_2`, `S1`, `GS2`) for identity — and never let a circled digit
mean an id.

## B3. Marker-to-caption pairing

Glyphs sit on the figure and the **step sentences live in the caption**, in order. Only **3 records
[tally]** draw a side legend listing the steps: `osdi26-079_fig6` (the five-step
lock/copy/stitch/unlock recipe at the right, so ①–⑤ can be replayed per frame);
`asplos26-006_fig8` (dotted-border boxes spelling out conditions `A/B/C` and action codes
`1.1/1.2/2.1/2.2`); `asplos26-091_fig2` (looked at — a key inside panel (b) declaring the two arrow
conventions). Where the caption does not carry them, records complain: `nsdi23-089_fig1` — "steps
4-7 are not directly narrated"; `osdi26-048_fig2` — "with 10 lettered steps across 4 regions … the
causal order across the B/H/X/L letter families is not made explicit".

**Default.** 3–8 markers; write the caption's step list at the same time as the markers. Use a side
legend instead when the same marker set repeats in several frames, or when a marker stands for a
*code* (a condition name, an action class) rather than a step.

## B4. `carries` — following one object

**[stats]** `steps_with_carries_share` = **0.976**: essentially every recorded step names *what is
being carried* (comparison 1.0, walkthrough 1.0, anatomy 1.0, evolution 0.96, logic 0.5). A
mechanism walkthrough is nearly always the journey of one identified object, not an abstract
sequence of stage names — so a marker usually comes with a **noun**. `asplos25-033_fig4` traces
pink = transaction A and blue = transaction B through TxTable → Write Log → TxLog → Flash;
`nsdi23-003_fig7` follows two records by hex `priv_label` plus header fill across four stages;
`osdi23-020_fig9` carries a ghost/physical value pair as two boxes travelling together down a
swimlane. Fill `steps[].carries` whenever the walkthrough follows one request, packet, page or
tuple — the drawer uses it to give that object one colour for its whole journey.

## B5. Default and deviations

**Default.** `walkthrough` → circled digits, 3–8, on the edges along the path in reading order, with
the caption step list written. `evolution` → letters or a named block arrow between frames, not
numbers inside them. `comparison` → `(a)/(b)/(c)` panel tags only. `logic` → no markers; guards
carry the meaning (C5). `anatomy` → none (94% of records).

**Deviate when**: the same procedure repeats in several frames (number once, legend at the side —
`osdi26-079_fig6`); a step splits physically but not logically (`2a`/`2b` — `asplos26-021_fig1`);
the transitions are few and nameable (labelled arrows beat numbers); or the surface already supplies
order (a time axis, a circuit's left-to-right, a table's columns) — then numbering is redundant, and
61% of the corpus omits it.

---

# Part C — Colour, line, shape

## C0. How much colour

**[stats]** `palette_entries_per_record`: median **5**, q3 6, p90 7, max 13. **[tally]** distinct
colour words named per record's `color_means`: median **3**, p25 2, p75 4, max 8.
`style-rules.md` §1 measures the same thing on the SVG: `palette.n` median **4**, hue families
**3**, and having *no* fill colour at all is the strongest single tell of a bad mechanism figure.

So: **three to five meanings across three to four hue families.** Past that, a legend row is owed
(C8).

## C1. What colour means here

Sorted by how often the records' `color_means` describe it **[tally]**:

| meaning | n | note |
|---|---|---|
| **category / identity** — one hue per component, lane, or tracked value | ~10 named explicitly; the dominant reading across all 152 | "its own colour purely to keep them distinct" (`nsdi24-031_fig9`, `nsdi26-043_fig9`, `asplos25-034_fig1`) |
| **state** — the fill *is* the state | the whole `logic` group and much of `evolution` | `osdi26-076_fig8` white/blue/green = I/S/A; `nsdi23-079_fig7` orange Hot, blue Cold, near-black Swapped-out |
| grey = inactive / unchanged / not-in-play | **20** | C2 |
| **ours vs baseline / the addition** | **17** | `nsdi24-086_fig11` red = the added NN-PD path over a blue baseline chain; `asplos26-057_fig9` red reserved for the two new PIPM states |
| red = wrong / failed / error | **14** | C3 |
| red as a pure highlight (not error) | **11** | `nsdi25-037_fig4` red box = the sub-structure under discussion; `osdi26-024_fig9` red numerals = just changed |
| green = good / correct / success | **10** | C3 |
| monochrome — colour carries nothing | **8** | `osdi26-136_fig7`, `osdi25-038_fig9`, `asplos26-030_fig9`, `nsdi24-061_fig3` |

One habit worth copying: **domain tinting applied to every panel at once** — `asplos26-067_fig5`
uses pink = local-protocol domain, yellow = global-protocol domain, on region shading, arrows *and*
message text across all four panels. One decision, applied everywhere.

## C2. Grey

**20 records [tally]** give grey a job, always some flavour of *not the point right now*: idle,
unchanged, already-explored, elsewhere in the scene, crashed, generic/external.
`asplos26-148_fig4` (anatomy, looked at) is the extreme case — dozens of **grey** ellipses fill the
scene and the four Gaussians inside the camera frustum are the only coloured ones, inside a
pale-yellow tinted box; colour-vs-grey *is* the figure. `nsdi24-095_fig3` greys elements "faded
because they are not part of the current computation step", fading their arrows to match.
`osdi26-024_fig9` (looked at): grey = already explored. `nsdi24-023_figtex23`: sky blue = GRACE's
own sub-blocks, grey = generic external components — the architecture novel/existing split inside a
mechanism figure.

**Deviate when** grey is already the page's structural neutral (outlines, rulers, lanes). Two greys
at different lightness doing two jobs is a recorded failure (`osdi26-068_fig6`).

## C3. Red and green

Red-green as an opposed pair is **rare**: 14 records use red for wrong/failed, 10 green for
right/ok, **2 use both** [tally]. Far more often red is *the highlight* and green is *a category*.

When the pair is used, it comes with a redundant cue: `asplos26-026_fig10` (looked at) green check
+ green text vs red cross + red text, with the words `Mem` / `Throughput` present regardless;
`sosp25-060_fig4` (looked at) green happy face + `Hit`, yellow sad face + `No hit`;
`nsdi24-067_fig5` (looked at) green `Y` and red `N` beside every branch — the letters survive
desaturation and the hue is a bonus; `nsdi26-095_fig3` a green check next to `BAR-SAV` and a red X
at the AS that would wrongly drop the packet, with the three defeated policy names also in red.

**Must (print physics).** A red/green distinction with no second channel fails for ~8% of male
readers and in every greyscale reprint. Pair it with a glyph, a word, or a position. Only 3 records
[tally] flag colour-only encoding as a weakness — because good figures already add the second cue,
and `osdi24-015_fig3` proves the glyph alone is enough.

## C4. Line style

**[tally]** 102 of 152 records use a dashed/dotted/hatched channel; **33 say explicitly that line
style carries no distinction** ("all edges are plain solid"). Among the 102:

| dashed/dotted job | n [tally] |
|---|---|
| grouping / panel boundary / region divider | 52 |
| a **second relation kind** (control vs data, lookup vs invalidate, ghost vs real) | 57 |
| ruler, gridline, cycle boundary, threshold line | 12 |
| ghost / old / pending / not-yet-resolved state | 9 |
| zoom or callout leader | 6 |
| **two or more of the above in one figure** | **36** |

That last row is the recurring ambiguity. It survives when the two jobs land on **different kinds of
object** — a dashed *box border* and a dashed *arrow* are rarely confused (`asplos25-033_fig4`:
dashed vertical rule = host/firmware split, solid arrows = actions). It fails when both land on
arrows.

The relation kinds to tell apart **[stats, relation_kinds]**: data 363 (36%), control 287 (28%),
**transition 186 (18%; 120 of them in `logic`, 45% of that group's relations)**, mapping 62 (6%),
dependency 48 (5%), timeline-message 45 (4%), pointer 22 (2%). Worked conventions:

- `asplos26-091_fig2` (logic, looked at): **solid blue = CPU-triggered, dashed magenta =
  hardware-triggered** transition, with a two-line key inside the panel. Colour and dash are
  redundant, which is why it is legible; `nsdi25-027_fig1` (looked at) does the same with solid
  purple = Raft original, dashed gold = CCF addition.
- `osdi23-020_fig9`: **dashed teal outline = a ghost (specification) value, solid black = the
  physical value**. `sosp25-063_fig2`: solid horizontal = same-level `Transition`, dashed diagonal =
  cross-level `Refines` mapping — the cleanest `mapping`-kind encoding in the corpus.
- `nsdi23-089_fig2` (looked at): solid black = the request's own path, **dotted blue** = span
  reporting, **dotted red** = backward breadcrumb traversal — three channels separated by colour
  first, dash second. `sosp25-039_fig1` pushes it furthest: the **frame border's dash pattern** is
  the code (dashed = supervised public, solid = supervised private, dash-dot = unsupervised), and
  it works only because a legend below declares it.

**Default.** Solid for the main data/request/transition path; dashed gets **one** job. If the figure
needs both a grouping boundary and a control channel, make containers solid-and-light, dash the
control edges, and say so in a legend (`../encoding.md` §A3 reaches the same rule from the
architecture corpus).

## C5. Guards on transitions

**[stats]** `logic_guard_share` = **0.853** over the 31 records with a logic block (0.836 within
the `logic` group); 20 of 31 have decision nodes. **[tally]** 12 records describe the convention
explicitly, 11 of them in `logic`.

Every branch is labelled, with the trigger or condition *in the paper's words*: `Recv Pause` /
`Recv Resume` / `Recv Merge` / `Empty IQ` (`nsdi25-043_fig6`); `Write dTable`, `PB not empty`,
`Timeout` (`nsdi24-031_fig9`); `Hit` / `Miss` / `Enough local memory` / `Otherwise`
(`nsdi23-079_fig1`, looked at); green `Y` / red `N` at every diamond (`nsdi24-067_fig5`, looked at);
`low` / `high` on every threshold check (`nsdi25-016_fig7`). Two recorded failure modes: an
**unlabelled** transition (`nsdi23-079_fig7`: "the diagonal 1->3 and 1->2 arrows … carry no guard
text") and **the same guard on two different edges**, leaving source/target position as the only
disambiguator (`nsdi24-031_fig9`, `osdi25-038_fig9`). Spec field: `edges[].guard`, on every
`decision` exit and every `transition`.

## C6. Shape

**[stats]** `style.corners`: square 56 (37%), mixed 54 (36%), rounded 35 (23%). `style-rules.md` §4
finds `mixed` is a *replicated quality signal* here (good 30.7% vs ok+bad 17.1%) — the point being
that shape encodes something, not that corners should be rounded.

**[stats]** `element_kinds` shows what a mechanism figure needs: label 415 (27%), box 364 (23%),
node 222 (14%), **state 118 (8%, of which 90 are in `logic` — 32% of that group's elements)**, row
105 (7%), icon 84 (5%), lane 84 (5%), cell 83 (5%), port 43 (3%), actor 22, slot 12.

**16 records [tally]** give shape an explicit semantic job, 12 in `logic`:

| shape | meaning | figures |
|---|---|---|
| rounded box or circle | a named **state** | `nsdi25-027_fig1`, `osdi26-076_fig8`, `nsdi24-031_fig9` |
| **double** circle | accepting state | `nsdi24-079_fig7`, `osdi26-136_fig7` |
| diamond | a real branch, both exits labelled | `nsdi24-067_fig5`, `asplos26-006_fig8`, `osdi26-122_fig12`, `asplos26-091_fig2` |
| ellipse / stadium | entry and exit pseudo-states | `nsdi23-079_fig1`, `sosp25-053_fig5` |
| rectangle | an **action** the system takes | `sosp24-014_fig6`, `sosp25-053_fig5` |
| dotted box inside a solid box | **substate** in a superstate | `asplos26-091_fig2` |
| record / table box | a state defined by its **flag values** | `osdi25-038_fig9` (occupied/complete = 0/1) |
| grid of cells | memory, tensor, table, packet layout | `sosp23-016_fig5`, `osdi25-013_fig2`, `nsdi25-040_fig10` |

Per `base` **[stats, content.base]**, node kinds follow the surface: `state-machine` (18 records,
13 logic) → `state` + `transition`; `flowchart` (10, 8 logic) → `decision` + guarded branches;
`data-structure` (11) → `slot` / `cell` with `pointer` edges; `timeline` (19) → `lifeline` lanes +
`message` edges; `component` (26) → boxes and `port`s.

**Deviate when** the paper's domain has a glyph the reader already knows — a CNOT dot-and-⊕, a
comparator dot pair, an `H` box, a store cylinder. `nsdi24-068_figtex18` (looked at) draws the
comparator as a dot pair with a downward arrow and defines it in a two-line `Comparator` key at the
right. Borrow the domain glyph and define it once.

## C7. Icons

**[stats]** `style.icons` = `none` in **62 of 152 (41%)**; the remaining 90 values are one-off
free-text descriptions, i.e. no icon vocabulary recurs, and `style-rules.md` §6 finds icon and image
counts are **not** a quality signal (median 0 in every group). Where icons earn their place they are
**status badges**, not decoration (A3): padlock (locked / security-critical step), crown (current
leader), burst or bolt (crash / fault), X over a unit (failed worker, lost packet), bug (wrong
result), check/cross (verdict), clock, face.

**Deviate when** the icon replaces a label the reader would otherwise have to read — a GPU, switch,
camera, person. `asplos26-148_fig4` (looked at) has *no text at all*; a hand-drawn camera glyph with
sight lines carries the whole viewpoint concept, at the recorded cost that the colour-vs-grey
convention then "rel[ies] entirely on the caption".

## C8. Legends

**[stats]** `layout.legend`: none **106 (70%)**, inside 23 (15%), right 12 (8%), below 9 (6%), above
1, per-panel 1 — so **30% carry a legend** and half of those put it *inside* the drawing.
**[tally]** 25 records name an in-figure legend; **22 name a missing or distant legend as a
weakness** — 14% of the corpus complaining about its own key. As in the architecture corpus, that is
a defect to fix, not a convention to copy.

**Carry one when:**

- more than about **four semantic fills**, or any fill whose meaning is not written inside the
  element — `osdi26-024_fig9` (looked at) opens with a three-swatch bar (`Explored Node`,
  `Exploring Node on Main Branch`, `Speculative Exploring Node`) plus `V: Value  C: Visit Count`,
  without which the ten frames are unreadable;
- **line style or arrow colour carries meaning** — `asplos26-091_fig2` (looked at),
  `nsdi23-085_fig1` (explicit solid = invocation / dashed = data-flow key), `sosp25-039_fig1` (the
  three frame-border dash patterns), `sosp23-002_fig5` (dashed = async RPC — and the record flags
  that this is declared only in the caption, not on the figure);
- **any non-universal glyph, or a worked example's colour key** — `nsdi24-068_figtex18` (looked at)
  defines its comparator symbol, `asplos26-026_fig10` (looked at) defines `V` and `D` in a
  dashed-bordered key, `asplos25-082_fig2` (looked at) puts an `Expert` / `Non-Expert` swatch pair
  at top-left.

**Placement.** `inside` (23) outnumbers `right` (12) and `below` (9) combined: an empty corner of
the drawing, within about one box-width of something it decodes. **Not needed** when the only
encoding is accent-vs-neutral with named accent elements, or when every branch already carries its
guard word.

---

# Part D — Worked values

**[stats]** `content.worked_example` is true in **50 of 152 (33%)**; 49 records carry a `values`
block (comparison 14, evolution 14, anatomy 12, walkthrough 7, logic 2). The marker means *the
values are the content* — remove them and nothing is left. Values written beside a box are
annotations, not a worked example.

## D1. How values are linked

`values_linked_by` **[stats]**, primary channel per record: **colour 21 (43%)** plus 5 recorded as
`colour:` and 1 as `colour-coded` — **27 of 49 (55%)**; **position 18 (37%)** plus 3 as `position:`
— **21 (43%)**; dashed 1 (2%). **[tally]**, counting every mention in the link clause rather than
the primary channel: colour **41 of 49**, position **30 of 49**, arrows or leaders **8 of 49**.
Most records use **both** colour and position; a pure-arrow link is rare.

**Colour** — one hue per value, held everywhere that value appears.

- `nsdi24-068_figtex18` (anatomy, looked at): four inputs 9/6/4/8 get red/green/blue/orange and
  **keep that colour as they move between wires** through five comparators, so the sorted output
  4-6-8-9 is verifiable by eye. The structure is pure black line art; only the values are coloured.
- `asplos26-021_fig1` (walkthrough, looked at): every matrix and vector entry has its own hue,
  carried from the crossbar's conductance labels into the verification equations below —
  `2 × 5 + 7 × 8 = 66`, each operand in the colour of the wire it came from.
- `asplos26-094_fig2`: red marks **every occurrence of the value 3** (counter match, spike, captured
  register) and blue a second example value, across six construction panels. `nsdi23-003_fig7`: pale
  orange and purple header fills track two records whose *positions* change at every stage.

**Position** — the same row, column or slot in every frame or panel. `osdi25-013_fig2`: the same
four receiver rows in all five time-steps with a dedicated count column at the right.
`nsdi23-076_fig23`: "the same node slot across the three panels" is the only link — and the record
flags the cost, "spotting exactly which numbers differ … requires reading every node".
`sosp23-016_fig5` (looked at): each token sits in its block's row in left-to-right order, and the
blank white rows between filled blocks are what argues non-contiguity.

**Arrows and leaders** (8 records): `asplos25-018_fig6` links a chosen reference image to the day it
is compared against with **dashed arrows colour-matched to the source satellite** — both channels at
once; `osdi25-031_fig11` drops dashed zoom-callout lines from `Step 19` of the coarse table into the
fine-grained one.

## D2. Result cells

**38 of 49 [tally]** value records have an explicit result cell, row or line; **7** say there is
none (the values themselves are the answer). The recurring forms:

- **An `= result` line** — `asplos26-021_fig1` (looked at): `2 × 5 + 7 × 8 = 66` under the crossbar,
  matching the black result boxes in reference panel (a). **A dedicated result column** —
  `osdi25-013_fig2`: the rightmost **green** cell per row is the cumulative ack, "the value the
  receiver actually acts on".
- **A scorecard or verdict row under each panel** — `asplos25-038_fig1`: `Occupied GPUs: 4 / 3 / 2`,
  the one number compared across panels; `asplos26-026_fig10` (looked at): `Mem` and `Throughput`
  with check/cross; `osdi25-031_fig11`: a check or cross above each step against the target.
- **An annotated edge** — `nsdi26-074_fig2`, `nsdi26-074_fig4`: every edge labelled `used/capacity`,
  and the maximum across edges *is* the result. **No result at all** — `nsdi23-076_fig23`,
  `sosp24-011_fig7`: the pattern of values is the example.

## D3. Tabular alignment

**41 of 49 [tally]** worked-example records name a table, grid, row or column. The discipline that
makes values checkable is the one Part A asks of frames: **one value per cell, cells aligned across
frames and panels, tabular figures so digits line up** — `osdi25-013_fig2`, `osdi25-031_fig11`,
`nsdi24-029_fig6` (looked at), `asplos25-053_fig4`. The cost when density runs away is
self-reported: `osdi25-031_fig11` ("335 text runs … many small ~4.5 pt numbers") and
`asplos25-053_fig4` ("extremely dense small 4-9 pt numerals with only colour to group them").
**46 of 152 records [tally]** name smallness or density as a weakness — the most common complaint in
the corpus.

**Must (print physics).** Nothing a reader has to read below **5.5 pt** at print size
(`style-rules.md` §8: good median min 5.5 pt, median 6.5 pt). If the values will not fit, cut the
example, not the type size.

---

# Part E — Default encoding table

Apply unless the figure or the user says otherwise. "Share" is the evidence; "deviate when" is the
recorded exception — and the recorded exceptions are not the only ones allowed: the table is a starting
point for your own encoding decisions, which follow from what this figure must make visible, not a
checklist to satisfy.

| variable | default meaning | share [source] | deviate when |
|---|---|---|---|
| fill colour, changed element | **the delta**: what this panel/frame changes | 80/152 (53%) `delta_marking: colour` [stats] | the delta is structural (a box appears, a lane vanishes) — geometry carries it |
| fill colour, unchanged element | the template; leave it exactly as in the other panels | aligned/identical 55 of 81 multi-panel [stats] | the structure relocates → link by colour + a stable id |
| fill colour, `logic` node | **the state**, one hue per state wherever it appears | 90 of 118 `state` elements are in logic [stats] | the genre is monochrome (automata, circuits) — 8 records [tally] |
| grey | inactive, unchanged, already-done, elsewhere, external | 20 [tally] | grey is already the structural neutral (rules, lanes) |
| red | the thing called out **or** wrong/failed — one, not both | 14 wrong / 11 highlight [tally] | — |
| green | correct / success, only as red's counterpart | 10 [tally]; both together only 2 | green is already a category hue |
| red ⟷ green pair | verdict | 2 records [tally] | **always** add a glyph or word (print physics) |
| accent on one panel | "ours" | verdict share 0.596 in comparison [stats] | the paper takes no side |
| dashed outline on an element | the **old / lost / pending / not-yet** state | 17 [tally]; 5 as figure default [stats] | dashed is already spent on boundaries or a relation kind |
| strike / red X on an element | removed, failed, blocked, preempted | 12 [tally] | — |
| status glyph (lock, crown, bolt, bug, face) | a property of the element it sits on | 11 [tally] | it needs a legend row if not universal |
| callout + leader | the one change the reader must not miss | 16/152 [stats]; 17 name it as emphasis [tally] | more than ~2 per figure |
| bracket / brace | a span: a duration, a scope, a repeated block | `asplos25-082_fig2`, `nsdi25-035_fig1`, `osdi24-015_fig3` | — |
| same slot, every frame | element identity across frames | aligned 47% / identical 21% of multi-panel [stats] | the mechanism *is* a relocation |
| solid edge | main data / request / transition path | data 363 + transition 186 of 1013 relations [stats] | — |
| dashed edge | **one** job per figure: control **or** boundary **or** ghost | 102 use it; 36 give it ≥2 jobs [tally] | two jobs survive only on different object kinds (box border vs arrow) |
| dotted edge | a weak third channel (telemetry, lazy path, uses) | `nsdi23-089_fig2`, `sosp24-035_fig2` | weight it visibly or it disappears |
| dashed vertical rule | a divider: host/device, phase, clock tick, panel split | 12 ruler/gridline uses [tally] | — |
| guard text on a branch | the trigger or condition, in the paper's words | guard share 0.853 [stats] | never omit on a `decision` exit |
| diamond | a real branch with both exits labelled | 12 of 16 shape-semantic records are logic [tally] | — |
| rounded box / circle | a named state; **double circle** = accepting | `nsdi24-079_fig7`, `osdi26-136_fig7` | — |
| dotted box inside a solid box | substate inside a superstate | `asplos26-091_fig2` | — |
| grid of cells | memory / table / packet / tensor layout | cell 83 + row 105 elements [stats] | — |
| ①②③ circled digits | **ordered** traversal, 3–8 steps, on the path | 30/152; 13/26 of walkthrough [stats] | never for identities — 7 records warn [tally] |
| bare digits / `S1`, `W_1_2`, `GS2` | identity, rank, address | 11 plain-number records [stats] | — |
| (a)(b)(c) letters | panels or alternatives; frames when there are many | 10/152 [stats] | — |
| labelled block arrow between frames | the operation producing the next frame | 7 labelled-arrows [stats]; 13 chevron separators [tally] | — |
| step marker colour | inherits the colour of the channel it marks | `nsdi23-089_fig2` | — |
| side legend of steps | the same recipe replayed in several frames | 3 records [tally] | otherwise the step list goes in the caption |
| one colour per worked value | links that value across every place it appears | 27/49 primary, 41/49 mentioned [tally] | values never move → link by position |
| `= result` row / result column / scorecard | the answer the reader checks | 38/49 [tally] | the pattern of values is itself the result (7/49) |
| legend | required above ~4 semantic fills, or for any meaningful line style, arrow colour or glyph | 30% carry one; 22 records complain of a missing one [tally] | accent-vs-neutral only, or every branch already labelled |
| legend placement | `inside`, in an empty corner near what it decodes | inside 23 vs right 12 + below 9 [stats] | — |
| zoom callout | a magnified region linked by dashed leaders or brackets | 9/152 (6%) [stats] | — |
| type floor | ≥5.5 pt at print size for anything read | `style-rules.md` §8 | **never** — cut the example instead |

---

# What the corpus does *not* do

Short list; the anti-patterns document covers failures in depth.

1. **No gradients, no 3D extrusion.** `style.fill` is `flat` in **129 of 152 [stats]**, `hatch` in
   3, `none` in 4, gradient in **0**. The one bevelled figure is recorded as a one-off description,
   not a convention.
2. **No tinted canvas.** `style.background` is white in **146 of 152 [stats]** (plus 3 recorded as
   `#ffffff`). The three exceptions tint a *band* or an *inset panel*, never the page.
3. **No step numbers on a figure with no order.** 30 of 32 anatomy records carry no markers
   **[stats]**, and 7 records go out of their way to say their digits are ids rather than steps
   **[tally]**. Numbering a static figure promises a path that is not there.
4. **No per-box hue.** Palette entries per record: median 5, p90 7 **[stats]**; distinct colour
   words per record: median 3 **[tally]**. Hues name *kinds* — a state, a domain, a tracked value —
   never individual boxes.
5. **No red for a plain component.** All 25 records that give red a job give it either the
   error/failure role (14) or the called-out-here role (11) **[tally]**. Red is never a neutral
   fill in this corpus.
6. **No verdict without a word.** Of the 82 panel lines carrying a verdict **[tally]**, the verdict
   is always readable as text — a panel title, a scorecard line, a `Hit`/`No hit`, an `ours`. The
   glyph and the hue are the second and third channels, never the only one.
