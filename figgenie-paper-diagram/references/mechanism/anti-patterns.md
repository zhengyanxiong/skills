# Anti-patterns: mechanism figures

What goes wrong in the **second figure kind** of this skill — figures that show how *one part* of a
system works: a walkthrough through a structure, successive frames of one structure, alternatives
side by side, control logic, or one component opened up. The whole-system overview is the other
kind; §5 says which of its anti-patterns also apply here.

## How to read this

**Sources.** (1) **Residual faults**: `mech-prescreen/semantics/stats/texts.md`, the 152 mechanism
semantic records (comparison 36, evolution 29, logic 29, walkthrough 26, anatomy 32), whose
`weakness:` lines were written by the describing model *while looking at the figure and reading the
paper around it*. **145 of 152 carry at least one** (`report.md`, `records_with_weakness_share`
0.954), never more than two, for **215 lines — my own tally of `texts.md`**; every count below is
that tally unless it names a stats file. The 152 were sampled as exemplars (`candidates.json`:
"good, not doubted, with a render"), so **§1–§4 are residual faults of work already judged good, not
what makes a figure bad.** (2) **The good-vs-bad contrast**: `mechanism/style-rules.md` over 986
rated figures (713 good / 203 ok / 37 bad); entries cite its sections rather than repeat the tables.
(3) **The kind boundary**: `mech-prescreen/typedisc/types_v3.md`, plus the 2026-09-18 pass in
`mech-prescreen/README.md` that re-classed 8 figures out of the corpus (§4). The corpus paths are
provenance only; inside the skill a cited figure is at `assets/exemplars/figures/<id>/print.png` (146 of
the 152 are shipped; the five the reviewer dropped and `nsdi25-043_fig6` are not).

**Non-rigidity — the rule that governs this file.** A quantum circuit, a Raft frame sequence, a
decision tree and a memory-layout worked example are all this kind, so an anti-pattern here is **a
recorded failure with a stated reason**, not a style preference. Every entry says why it hurts the
reader and when the same device is fine, because most are weaknesses only in a specific context:
repeated letters a–l across panels are ambiguous when nothing else separates the panels and fine
when the panel frame does. If a device does real work in your figure and the entry's reason does not
apply, the entry does not apply.

**Severity.** **never** — a hard failure with no working counter-example; four entries only (3, 5,
6, 7). **avoid** — wrong by default; needs a reason you could state out loud. **watch** —
context-dependent; the entry names the context. `[AUTO]` = checkable from the SVG. Figures marked
*(looked at)* were opened as PNGs while writing this.

---

## §1 Failures of the story

### 1. The change between frames or panels is not marked — 9 lines / 9 figures — **avoid**

> "no arrows or colour highlighting mark exactly which block moved between the current-method and
> DCP placements, so the reader must compare the two per-device block lists by hand" (`sosp25-001_fig11`)

**Looks like.** Two or more instances of one template, identical except for some cell contents, with
nothing saying which cells those are. `sosp25-001_fig11` *(looked at)* draws four device rows of
`Q/C/KV/O` cells under two placement policies and points at nothing; `nsdi23-076_fig23` *(looked
at)* draws three identically-shaped grey binary trees whose only difference is the digit inside each
of 32 nodes.
**Seen in.** `asplos26-076_fig9`, `nsdi23-008_fig5`, `nsdi24-095_fig3`, `osdi25-013_fig2`,
`osdi26-068_fig6`, `sosp24-024_fig3`, `nsdi23-076_fig23`, `sosp25-001_fig11`, `osdi23-029_fig3`.
**Hurts because.** The delta *is* the message; making the reader diff two grids by eye spends the
whole attention budget on a job the author could have done once.
**Do instead.** Mark it — the corpus overwhelmingly does. `layout.delta_marking`: **only 4 of 36
comparison and 2 of 29 evolution records use `none`** (11%, 7%) against colour 56%/69%, plus
callout, badge, dashed-ghost, strike. Colour on the changed cell by default; a badge or callout when
the change is a position.
**Fine when.** Nothing differs but one parameter named in the panel title. `logic`/`anatomy` sit at
`none` 45%/47% — correctly, having no delta to mark.

### 2. Alternatives that are not parallel, or not named — 8 lines / 8 figures — **avoid**

> "the two panels do not share a template (different node counts and topology), so a viewer cannot
> compare them position-by-position" (`nsdi23-085_fig1`)

**Looks like.** *Not parallel*: `nsdi23-085_fig1` *(looked at)* puts a 3×3 dashed crossbar labelled
"Shuffle" beside two boxes and a clock labelled "Batched data processing", under one caption, as if
comparable; also `osdi23-031_figtex1` (panel (b) silently switches to different transactions) and
`sosp24-017_fig9`. *Not named*: `sosp24-011_fig7` ("panel (b) has no '(a)'/'(b)' label printed on
the figure itself"), `osdi26-040_fig1`, `sosp25-047_fig11`, `asplos26-047_figtex2`, `nsdi24-023_fig5`.
**Hurts because.** Side-by-side layout promises that position means the same in both panels; break
it silently and every apparent difference is ambiguous — the design, or the drawing?
**Do instead.** Fix one panel's geometry and reuse it: `layout.frame_template` has **25 of 36
comparison records `aligned` and 7 more `identical` — 89%**; only 4 are `free`. Give each panel a
short tag *and* a short name, as `nsdi24-029_fig6` *(looked at)* does inside each dashed frame.
**Fine when.** The panels are explicitly not parallel — an (a) that sets up the scenario and (b)/(c)
that are the two policies (`asplos25-018_fig6`). Say so in the title.

### 3. Markers that are not an order — 7 lines / 7 figures — **never**

> "the small circled 1/2/3 job-ID labels … visually resemble the red Step 1/2a/2b markers but encode
> a different thing (which job, not which step)" (`sosp25-042_fig3`)

**Looks like.** Circled digits used as identity in a figure that also uses them for order; step
numbers restarting in every frame with no frame index — `osdi26-079_fig6` *(looked at)* reuses red
①–⑤ in frames i, ii and iii, so "step 3" names three different moments; ID sequences with gaps that
read as omissions (`asplos26-013_fig8`: numbering "jumps from 2 to 5"); one badge set reused for two
guard sets (`nsdi23-073_fig4`); figure and prose numbering each other's reverse (`osdi26-082_fig3`,
*looked at*). Also `osdi26-024_fig9`, `sosp23-030_fig8`.
**Hurts because.** This is the one device in the kind that carries a *contract*: a number promises
"read me third". `types_v3.md` makes it definitional — "Numbers that are only node IDs or phase
names do not make a walkthrough." A false contract is worse than none: the reader follows it before
discovering it is false.
**Do instead.** One numbering scheme per figure, one visual style, increasing along one path, with a
legend line per step past four. Put identity in another channel — letters, colour, a name. If frames
repeat a cycle, index the frame (`i-1 … i-5`) or number continuously across frames. Check against
the prose: 2 of these 7 are figure-vs-text disagreements, not figure faults.

### 4. No order marker where the reader needs one — 9 lines — **watch**

> "with 20+ labelled elements and two interleaved sub-pipelines (Monitor left-to-right, Reroute
> right-to-left) sharing the same vertical space, the reading order is not immediately obvious"
> (`nsdi24-018_fig4`)

**Looks like.** Two flows in opposite directions through the same boxes; a caption narrating "(1)
route the inputs … (2) accumulate …" with nothing numbered in the drawing (`asplos26-074_fig4`);
panels running right-to-left against convention (`nsdi25-047_fig5`, *looked at*: Scenario 3
leftmost, Scenario 1 rightmost). Also `asplos26-030_fig4`, `asplos25-142_fig6`, `asplos26-021_fig1`,
`nsdi24-068_figtex18`, `osdi26-024_fig3`, `osdi26-048_fig2`.
**Do instead.** Number the path, or let the layout carry the order — one direction, one lane per
actor, a ruler across the top (style-rules §5: `asplos26-047` fig 7 carries an eight-step order with
a "Step 1…8" ruler and zero arrowheads).
**Fine when — the big difference from architecture figures.** Step numbering is **not a quality
signal here**: style-rules §7 measures δ=+0.08 (FDR p=0.076), circled markers in 5.9% of good vs
2.5% of ok+bad and **0 of the 37 bad**. `layout.step_markers`: **93 of 152 (61%) have `none`**,
including 22 of 29 `logic` and 30 of 32 `anatomy`. An unnumbered comparison, state machine or
cutaway is not a defect. Number when the layout does not already give the order.

### 5. A transition its label does not identify — 13 lines / 12 figures — **never** (unlabelled) / **avoid** (shared)

> "the diagonal 1->3 and 1->2 arrows and the vertical 2<->3 arrow carry no guard text, so the figure
> alone does not say what triggers them" (`nsdi23-079_fig7`)

**Looks like.** *Unlabelled* (8 lines, **never** in a `logic` figure): `nsdi23-079_fig7` *(looked
at)* is the clearest case — a five-state page lifecycle where `swap-out`, `lock-free swap-out`,
`swap-in` and `frequent access` sit in italics near four edges while the three edges among states 1,
2 and 3 carry nothing at all. Also `asplos26-091_fig2` (bare `0`/`1` diamond branches),
`asplos26-006_fig8`, `nsdi24-079_fig7` (unexplained self-loops), `asplos26-057_fig9`,
`osdi25-038_fig9`, `nsdi24-023_figtex7`, `nsdi24-061_fig3`. *Shared* (5 lines, **avoid**):
`nsdi24-031_fig9` *(looked at)* puts `Timeout` and `PB not empty` on two edges each, crossing the
middle of the drawing; `osdi25-038_fig9` *(looked at)* puts `Fill` on two edges and `Invalidate` on
three; also `nsdi24-067_fig5`, `nsdi25-027_fig1`, `nsdi23-073_fig4`.
**Hurts because.** A state machine without guards is a picture of a graph, not a mechanism: it
cannot answer the only question it exists to answer, *under what condition does this happen?* A
shared label pushes that answer into the geometry — which crossing edges destroy (17).
**Do instead.** Label every transition with its event or guard, beside the arrowhead.
`logic_guard_share` is **0.853 overall, 0.836 within `logic`** — one transition in six is already
unlabelled, and these are that tail made visible. For a genuine duplicate, qualify (`Timeout
(waiting)`) or make the *source* unmissable: route the edges apart, colour by source, merge at a
junction.
**Fine when.** Not a `logic` figure — an unlabelled arrow in an `anatomy` datapath means "data flows
here", which the box names already say (`transition` is 45% of `logic` relations, 3% of `anatomy`).
And one event genuinely can have two effects: both `osdi25-038_fig9` `Fill` edges are correct as
protocol; the record only says telling them apart takes work.

### 6. A branch, state or arrow that goes nowhere — 5 lines / 5 figures — **never**

> "the N branch out of the RC[BLK_tgt] % itv. == 0? diamond has no drawn continuation, leaving what
> happens on a non-interval read only implicit" (`asplos26-041_fig7`)

**Looks like.** `asplos26-041_fig7` *(looked at)* routes the `Y` branch of its interval check into
the next stage and simply stops on `N`. `nsdi25-016_fig7` *(looked at)* is the mirror image: a
seven-level Z-score cascade where **every** `high` branch lands on an orange `Abnormal` leaf and the
final `low` branch has no `Normal` leaf at all, so the outcome that occurs most of the time is never
drawn. Also `nsdi23-073_fig4` (an action box with no outgoing arrow), `osdi26-076_fig8` (an
`Allocate` entry arrow with no source), `osdi26-136_fig7` (a state with no transitions either way).
**Hurts because.** A drawn decision node asserts that both outcomes matter. Drawing one is an `if`
with no `else`: is the other path trivial, unreachable, or forgotten?
**Do instead.** Terminate every branch — a leaf box, a back-edge, or an explicit `(no-op)` /
`unreachable` label; give every entry arrow a start marker or a source. `[AUTO]` a diamond with <2
outgoing edges; any edge with a free endpoint; any node of degree 0.
**Fine when.** The dead state is the point — `osdi26-136_fig7` draws `B/E` precisely to show an
unreachable product state. Then label it as such *in the figure*, which that one does not.

### 7. A worked example whose values cannot be checked — 10 lines / 9 figures — **never**

> "the caption itself warns that memory and throughput values are illustrative, not measured, so the
> numbers cannot be read as real benchmark results" (`asplos26-026_fig10`)

**Looks like.** Four variants. **(a)** Numbers the caption disowns (`osdi24-004_fig2`). **(b)** A
curve with no scale — `osdi26-122_fig12` *(looked at)* plots per-page survival ratio against time
with `Threshold` and `Turning point` annotated and not one tick value, so neither can be located.
**(c)** Symbols where values should be (`osdi25-031_fig8`: bucket boundaries as `b0^k, b1^k` only;
`sosp23-016_fig5`: block size drawn as four columns, never written as a number). **(d)** A step
dropped so the arithmetic cannot be replayed (`asplos26-094_fig2`, `sosp25-008_fig3`,
`nsdi23-003_fig7`, which reassigns `entry_id` between columns "without an explicit note").
**Hurts because.** `types_v3.md` defines the marker as "the concrete values *are* the content … If
the values were removed, nothing would be left." An unverifiable value is decoration in the space of
content, and invites readers to quote a number the authors did not mean. **50 of 152 records (33%)
carry the marker**, so this is not rare.
**Do instead.** Make every number reachable: show inputs, the operation, and the result as its own
row or cell; link a value across its appearances by one colour or position (`values_linked_by`:
colour 43%, position 37%). `asplos25-053_fig4` *(looked at)* links well — join keys red wherever
they appear, index offsets olive, result tables drawn out — and fails only on the legend (9).
**Fine when.** The figure is a *schematic* and says so, with no digits at all. A curve with `99p`
marked on an unscaled axis (`nsdi25-047_fig5`, *looked at*) is halfway into the trap.

### 8. Too many frames or panels — 5 lines / 5 figures — **watch**

> "ten densely lettered frames with five server rows each pack in a great deal of state, so tracking
> one specific replica across the full sequence takes careful attention" (`osdi26-068_fig6`)

**Looks like.** `osdi26-068_fig6` *(looked at)* is two Raft cases of six and four frames — ten in
one double-column strip — each five server rows of circles, boxes, term labels, crowns and burst
icons, under a seven-entry legend bar. `asplos26-094_fig3` *(looked at)* packs nine sub-panels in
three visual languages into one double-column figure. Also `asplos26-094_fig2`, `osdi23-020_fig9`,
and `asplos25-151_fig13`, which redraws sub-trees identically in every panel "even though they are
never the ones acted on, adding visual repetition without new information".
**Hurts because.** Past about five frames the per-frame drawing is too small to carry its own labels.
**Do instead.** `layout.panel_count` is the budget: **70 records (46%) single-panel, 36 at 2, 24 at
3, 15 at 4 — only 7 of 152 (4.6%) exceed four.** `evolution` pushes hardest (median 3, p90 5.2, max
9). Show the first frame, the frame where the interesting thing happens, and the last.
**Fine when.** The frames are simple enough that the skeleton carries itself — style-rules §10
records `osdi24-040` fig 3 as the tallest good single-column figure *because* it is five stacked
frames of one swimlane skeleton. The variable is per-frame complexity, not frame count.

---

## §2 Failures of encoding

### 9. Colour, dash or symbol semantics with no in-figure legend — 25 lines / 25 figures — **avoid**

The largest family after legibility.

> "no explicit legend defines what the red/green/purple/olive numbers mean" (`asplos25-053_fig4`)

**Looks like.** Five channels do it. **Fills** — `asplos25-151_fig13` (blue "active" vs grey "idle"
router centres explained nowhere), `osdi26-086_fig1`. **Dashes** — `sosp23-002_fig5` (async vs sync
RPC "explained only in the caption text"), `asplos26-132_fig2`. **Notation** — `asplos26-074_fig4`
(`Des`), `asplos26-067_fig5` (`S,SM^D`), `nsdi24-067_fig5` (`NA`), `nsdi24-029_fig6` (the `→` vs `⇒`
rule box). **Hatch** — `osdi26-122_fig12` *(looked at)*, a hatched band in the `To space` bar with
nothing keying it. The extreme is `asplos26-148_fig4` *(looked at)*: a frustum-culling scene with
**zero text anywhere** — camera glyph, yellow frustum, grey ellipses outside, four coloured ones
inside — so every convention lives in the caption. Also `asplos25-038_fig1`, `asplos25-046_fig16`,
`asplos25-151_fig12`, `asplos26-041_fig7`, `asplos26-047_figtex2`, `nsdi24-023_figtex23`,
`nsdi26-043_figtex18`, `sosp23-016_fig5`, `sosp24-011_fig7`, `sosp24-014_fig6`, `sosp25-063_fig2`.
**Pictures** — the encoding lives inside a bitmap with nothing keying it: `sosp24-035_fig2` ("busy vs idle
must be read from colour and fill density rather than a legend"), `asplos25-018_fig6` (satellite icons
carrying the colour-to-satellite mapping), `asplos25-047_fig4`. The picture is not the fault; the missing
key is — key it as for any fill.
**Hurts because.** Readers skim figures before captions: an encoding defined only there loses its
skim-time argument, and one defined nowhere is a private note.
**Do instead.** A small keyed block inside the drawing. Under-used: `layout.legend` shows **106 of
152 (70%) with no legend**, `inside` only 23 (15%) — which is why the family is this large. Two good
examples among those looked at: `nsdi23-085_fig1` keys solid = function-invocation flow, dashed =
data flow in its bottom-right corner; `nsdi24-095_fig3` keys the gold outline as "switch storage" in
panel (b)'s empty corner.
**Fine when.** The palette is ≤2–3 fills whose meaning is written into the shapes they colour — a
legend for a two-colour figure is noise. Also a discipline's standard notation among its own
readers, though `asplos26-047_figtex2` shows even quantum-gate symbols drawing the complaint.

### 10. The same letter or number reused across panels — 17 lines / 17 figures — **watch**

**This is the entry the non-rigidity principle exists for.** Both figures here were looked at and do
the same thing with opposite results. `nsdi24-029_fig6` repeats the identical `1 2 3 4` /
`a b c … j k l` template in three panels — but each carries a bold `(a)/(b)/(c)` title inside its own
dashed frame, so the reader never gets lost. `nsdi26-126_figtex7` repeats `/`, `a`, `b` in green
circles in every panel — and the container band (`MNode 0`, `MNode 1`, `Coordinator`) disambiguates
them, the same solution. Both records complain because the disambiguation is *positional*, not
because it fails.

**It fails when nothing else separates the instances.** `sosp25-024_fig1`: node names repeat so
"without the dashed panel boundaries and captions the three examples could be misread as one
connected graph". `nsdi23-042_fig13`: "the middle and final chunk boxes are both labelled c23, so
the figure alone cannot show that the middle one should read c22" — a real error the reuse hides.
`sosp24-007_fig3`: `Ramp_2` and `Ramp_3` both read `2 samples exit`. `osdi24-003_fig11` reuses
`A/B/C` for both task owners *and* a comparison node. Also `nsdi26-131_fig7`, `sosp25-060_fig4`,
`osdi26-024_fig9`, `osdi26-079_fig6`, `nsdi24-023_figtex23`, `nsdi24-086_fig7`, `nsdi26-075_fig11`,
`sosp23-030_fig8`, `sosp25-053_fig5`, `osdi26-024_fig3`, `asplos26-013_fig8`.
**Do instead.** Reuse freely **across** panels when the frame is visible and named; never reuse
**within** one panel for two different things. When redrawing another figure's graph, keep or change
the IDs deliberately — `nsdi26-131_fig7` reuses `r0–r11` from Figure 4 in a differently-annotated
redraw, and the record flags the collision risk.

### 11. Colour as the only distinction — 14 lines / 14 figures — **avoid**

> "colour is the only cue tying an ellipsoid to its projected ellipse, which would not reproduce in
> greyscale" (`asplos25-034_fig1`)

**Looks like.** **(a) Greyscale death** — `asplos25-034_fig1`; `osdi24-015_fig3` ("greyscale-only
encoding with small 5pt labels makes the four policies hard to tell apart"); `sosp25-001_fig12`.
**(b) Colour with no rule**, a hue per instance instead of per role — `nsdi26-043_fig9` ("every
transaction gets a different colour rather than colour marking the baseline-vs-speculative contrast
directly"); `asplos26-148_fig4` *(looked at)* gives four in-frustum Gaussians four colours "with no
stated reason". **(c) Accidental collisions** — `asplos26-021_fig1` reuses red "for both the '7'
input pointer and the unrelated 1/9 conductance"; `nsdi24-095_fig3` carries two blues one hex digit
apart (`#6c8ebf` / `#6d8ebf`); `nsdi24-079_fig7`'s caption says "dashed brown" where the render reads
orange. Also `asplos25-082_fig2`, `asplos25-147_fig6`, `asplos26-026_fig9`, `nsdi25-043_fig6`,
`osdi24-051_fig4`, `sosp25-039_fig3`.
**Hurts because.** Proceedings are printed and photocopied grey, and ~8% of male readers cannot
separate red from green. Colour with no rule also burns the accent: colour eight things and none is
the one that matters.
**Do instead.** Add a redundant channel — a letter, a border style, a position, a luminance gap —
and assign colour to **roles**, not instances. Style-rules §1 puts the good median at **4 fills
across 3 hue families** (p25 = 3), so there is little budget for per-instance colour anyway.
**Fine when.** Colour redundantly reinforces something already distinguishable (`sosp25-039_fig3`'s
`R`/`F` letters are the real encoding). And style-rules §2 records `osdi26-136` fig 7 as a *good*,
entirely black-and-white automaton construction — no colour at all is respectable for automata,
circuits and proof diagrams, as long as nothing depends on colour.

### 12. An element, edge or icon with no label at all — 13 lines / 12 figures — **watch**

> "arrows are not labelled, so the figure alone does not show which mesh links carry the evicted KV
> data or propagated weights versus idle interconnect" (`asplos26-076_fig9`)

**Looks like.** An unnamed row (`asplos25-018_fig6`: "the ground-station row itself is not
explicitly labelled"); a bare cloud glyph (`nsdi24-023_fig5`); arrows with no operation name
(`sosp25-017_fig8`, `nsdi24-086_fig11`, `asplos26-053_fig1`); ports implied by wire position only
(`asplos26-030_fig9`). Also `osdi25-050_fig5`, `osdi26-076_fig8`, `sosp24-011_figtex2`,
`sosp24-035_fig2`, `sosp25-039_fig1`.
**Hurts because.** An unlabelled arrow among labelled ones reads as a different kind of relation.
**Do instead.** Be consistent within a channel: if some arrows carry operation names, all should —
or the unlabelled ones should be a different visual class (thinner, greyer, dashed) with that class
keyed. Mechanism text lives outside boxes (style-rules §9: good median **6 labelled boxes** against
**38 text runs**), so edge labels and annotations are the normal place for it.
**Fine when.** The unlabelled thing is context the figure does not argue about (a cloud = "the
network") *and* nothing else is in the same visual class. Style-rules §5 is explicit that undirected,
unlabelled connective structure — lanes, wires, rulers — is the mechanism idiom (heads-per-line 0.31
vs 0.50 for ok+bad).

### 13. Blanks that read as damage: ghosts, placeholders, ellipses — 17 lines / 16 figures — **watch**

> "panel (b)'s greyed-out ev_{t+1} and its arrow are cut off at the panel's dashed border, which
> could read as a truncation error rather than an intentional 'continues beyond this frame' cue"
> (`nsdi24-095_fig3`)

**Looks like.** *Ghosts* (5 lines): `nsdi24-095_fig3` *(looked at)* pales out the previous and next
timesteps in panel (b) to say "context" — which works, the grey is far lighter than the live black —
but the right-hand ghost is sliced by the panel divider. `sosp24-024_fig3` uses a dashed blank and a
plain blank for two kinds of emptiness; `asplos26-103_figtex7`'s empty `Expert 1` and
`osdi25-050_fig10`'s empty cloud "could be misread as an omission"; `nsdi23-008_fig5` overlays old
and new bindings in one frame. *Elisions* (12 lines): `osdi25-050_fig5` ("only two of each server's
GPUs are drawn explicitly"); `osdi25-031_fig8` ("ellipses hide most of the 32 buckets, so only 5 are
individually labelled"); a tree pruned with no stated rule (`asplos26-026_fig9`); a panel showing
only part of an operation (`asplos26-026_fig10`); plus `asplos26-030_fig9`, `nsdi26-037_fig3`,
`nsdi25-035_fig1`, `osdi23-022_fig14`, `sosp24-007_fig3`.
**Hurts because.** A reader's first hypothesis for a faint or empty thing is a rendering failure,
not an encoding; and an unannotated `…` leaves open whether the hidden instances are more of the
same or something different.
**Do instead.** Ghost by opacity *and* dash, keep the ghost inside its frame, and name the
convention once (`before`, `not modelled`) — `dashed-ghost` appears in only **5 of 152 records**, so
there is no convention to lean on. Annotate the count or range beside every ellipsis:
`… (32 buckets)`, `×8`, `b0 … b31`; if the elision is a *rule*, say the rule in one word.
**Fine when.** There is exactly one kind of blank and it is named, or the count is written
unmissably elsewhere in the figure (a `P = 4` under the row, an axis running `0 … 15`).

### 14. The accent on the wrong thing — 4 lines — **watch**

> "case A and case B are only distinguished by a small grey dashed tag, easy to miss next to the much
> bolder gold highlighting" (`osdi26-079_fig6`)

**Looks like.** The loudest mark is not what the paragraph is about. `osdi26-079_fig6` *(looked at)*
highlights the new subtree in bold gold — right — while the `case A` / `case B` distinction the
protocol turns on is a tiny grey dashed tag in the corner. `asplos25-147_fig6`: the newly-crossing
edge "is not given its own callout even though it is the trade-off the text discusses".
`sosp25-047_fig14`: the `θ` marking step 3 has no arrow of its own. `asplos25-034_fig1`: an
unhighlighted ellipse sits close enough to the highlighted tile to read as highlighted itself.
**Do instead.** Decide what one element the caption's verb acts on and give it the strongest mark.
`element_highlighted_share` is **0.228** — one element in four is already highlighted, a lot of
accent; spend it on the subject.
**Fine when.** Two things are genuinely co-equal — then mark them the same way, not one loudly and
one quietly.

---

## §3 Failures of legibility at print size

Judged **at print size**: single-column ≈240 pt wide, double ≈504 pt (style-rules §10). Render at
that size before judging.

### 16. Tiny type on a dense grid — 26 lines / 26 figures — **watch**

The largest family in the tally, and the one most in need of the non-rigidity caveat.

> "very small (2.5pt) annotation text and 23 overlapping icons make the diagram dense and hard to
> read at print size" (`osdi24-020_fig4`)

**Looks like.** `osdi24-020_fig4` *(looked at)* is a two-lifeline TLS-relay exchange whose message
and party annotations are hairline-sized between ~23 padlock and key glyphs. `asplos25-053_fig4`
*(looked at)* is a join-layout worked example of ~150 individual 4–9 pt numerals in six grids,
grouped only by colour. Recurring shapes: 4.5–5.5 pt labels crowding box interiors
(`asplos25-006_fig1`, `asplos25-033_fig4`, `osdi23-049_fig10`); symbol sets needing a magnifier
(`nsdi25-064_fig4`, `osdi25-031_fig11` at 335 text runs); two numeric labels on one short edge
segment (`nsdi26-074_fig4`). Spread across every group — comparison 6, walkthrough 6, anatomy 9,
logic 3, evolution 2 — with `layout.text_density` at **81 of 152 (53%) `dense`**, 23 `sparse`.

**Reconciles with style-rules §8 — read this before acting.** Font size is **not** a quality signal
here: good and ok+bad figures have *identical* median (6.5 pt) and maximum (8.0 pt) label sizes, and
the minimum is mildly *reversed* (good 5.5 pt vs bad-only 6.0 pt) because good figures have more to
label. Density agrees — §9 makes `density.shapes` **the strongest single metric in the corpus** (good
median 126 vs 43 for bad, δ=+0.39), area-normalised version included. **Good mechanism figures are
denser and carry more fine print than bad ones.**
**Do instead.** Do *not* enlarge the smallest label to "fix" a weak figure, and do not thin it out.
Do keep a **6 pt floor**; when a label will not fit at 6 pt, fix it upstream — shorten the label,
widen the cell, drop a frame (8), split out a second mechanism (21), or move to double column (19).
**Fine when.** The small print is an index the reader consults, not prose they read: matrix cell
values, ruler ticks, per-node IDs. Those can sit at 5 pt if structural labels are 6.5–8 pt.

### 17. Labels and notation that do not survive the render — 10 lines / 10 figures — **avoid**

> "the loop-back condition text runs along the bottom edge of the figure rather than beside its
> arrowhead, so it takes a moment to associate it with the Undrain()→Drain() arrow" (`nsdi24-061_fig3`)

**Looks like.** *Placement* (6 lines): edge text parked at the figure boundary; two labels sharing
one short segment (`nsdi26-074_fig4`); a guard between two crossing arrows so it could belong to
either (`osdi26-136_fig7`, `nsdi26-022_fig4`, `sosp24-014_fig6`); `nsdi23-079_fig7` *(looked at)*
floats `swap-out / allocate swap-entry` a full box width from the arrow it annotates. *Notation* (4
lines): `sosp25-047_fig15`, where "phi and phi^-1 look nearly identical at this size (an
inverse-exponent superscript)"; bracketed tuples repeated on every edge (`nsdi26-082_fig4`);
subscripted names needing the paper to parse (`asplos26-041_fig7`); a display font whose digits blur
at 5 pt (`asplos25-091_fig2`, a 6×6 Comic Sans matrix).
**Hurts because.** An annotation whose anchor is ambiguous is worse than none — the reader attaches
it to the wrong edge and believes a wrong guard. And at 6.5 pt a `^-1` is three or four pixels.
**Do instead.** Put each label within half a box-width of its arrowhead, in a small canvas-coloured
rectangle if it must sit on a line; route crossing edges apart *before* labelling them. Carry a
notational distinction in a second channel — arrow direction, colour, a word (`fwd`/`inv`) — and set
formulas as vector TeX at ≥6 pt. `[AUTO]` text bbox ∩ path bbox; edge-label distance to its own
path's midpoint.
**Fine when.** A single global condition reads as a caption line — then it is not an edge label. And
the paper's own notation is fine if it appears once at readable size with its expansion.

### 18. Long legend strips, and legends far from what they decode — 3 lines — **watch**

**Looks like.** `osdi26-068_fig6` *(looked at)* runs a seven-entry legend bar the full width above
ten frames — witness instance, Raft log instance, Raft leader, client request, getRecoveryData, end
& start, replication — so decoding one frame means travelling to the top and back, seven times.
`osdi25-016_fig6` packs "three unrelated use cases and a dense legend … into one double-column
figure at 4-5.5pt text". `asplos25-082_fig2` has a second legend reusing the first's colours for a
different meaning.
**Hurts because.** A legend is a lookup table; its cost is eye-travel per lookup, times lookups.
**Do instead.** Key in place where you can — label the first instance of each class inline and let
the legend cover only what repeats. Put the legend in an empty corner next to at least one thing it
decodes: `layout.legend` has `inside` (23) as the commonest non-empty placement, ahead of `right`
(12) and `below` (9).
**Fine when.** Many instances of few classes (40 nodes in 4 roles) — one legend beats 40 inline labels.

### 19. Wider than the column, or crammed into the wrong one — **avoid** (layout constraint)

**Looks like.** An SVG authored on a free canvas and scaled down until the type is unreadable; or a
five-panel figure squeezed into single-column when it needed double.
**Hurts because.** Exceeding the column breaks the printed layout, and scaling to fit takes the type
under the 6 pt floor — which is how most of family 16 happens.
**Do instead.** From style-rules §10, a **must**: single-column **≈240 pt** (good p25–p75
246–253 pt), double **≈504 pt** (510–536 pt). Then use the freedom the same section documents:
**width does not predict quality at all** (δ=+0.08, FDR p=0.089, n.s.) while **height does** — good
single-column median 125 pt vs 112 pt (δ=+0.20), p95 236 pt a *soft* ceiling real multi-frame
walkthroughs exceed. So **do not fight a tall figure; fight a wide one.** Single → double doubles
width (247 → 510 pt) but good height grows only ~34% (125 → 168 pt): the extra width buys flanking
state tables, not a bigger drawing. `index.column` has **128 of 152 (84%) single-column**, `anatomy`
97% — double is the exception you argue for.

---

## §4 Failures of scope

### 20. A figure that is really a chart, table, code listing or photo — 3 lines + 8 re-classed — **avoid**

**Looks like.** `osdi23-022_fig1` *(looked at)*: two dashed panels of multi-line SQL with inline
result comments plus two schema tables, where the whole mechanism — which statement reorders, which
row changes — lives in the text of the listing ("dense multi-line SQL with inline comments requires
careful line-by-line reading to see exactly where the two schedules diverge"; same for `_fig14` and
`_fig6`). For charts, `osdi26-122_fig12` and `nsdi25-047_fig5` *(both looked at)* are axis-and-curve
drawings whose argument is about shape, not measurement.
**Seen in.** Here: `osdi23-022_fig1`, `osdi23-022_fig6`, `nsdi25-047_fig5`. In the wider corpus,
decisively: on **2026-09-18 eight figures were re-classed out of the mechanism corpus**
(`mech-prescreen/README.md`) — 2 line charts, 2 table-figures, a bar chart, an unspecified chart, a
code listing and a photo — after three labelling agents raised `subtype_doubt` on 18 records. Three
doubted ones stayed, and the reason is the test: `nsdi26-139_fig5`, `nsdi24-097_fig1` and
`nsdi25-047_fig5` "are drawn illustrations" — hand-authored schematics that happen to use axes.
**Hurts because.** Charts and tables have their own conventions (axes with units, alignment, sort
order) and their own quality bar; none of this skill's drawing rules apply. A listing is typeset.
**Do instead.** Apply the owner's test: **is it drawn, or plotted/typeset?** If the marks come from
data or a text buffer, set it as a listing or plot it. If it is drawn by hand to argue about shape,
it is a mechanism figure and §1–§3 all apply.
**Fine when.** A chart or listing is a *panel inside* a mechanism figure that feeds or is fed by the
drawn part. One embedded language feeding the other — see 21.

### 21. One figure carrying two mechanisms — 13 lines / 13 figures — **avoid**

> "the top covisibility-comparison arrows and the bottom mapping pipeline are drawn separately
> without an explicit connecting line, so the reader must infer that one produces the label the other
> consumes" (`asplos26-013_fig8`)

**Looks like.** Two independent drawings sharing a frame and nothing else. The tell is always the
same: **the link between them is not drawn.** `asplos25-092_fig5`: the abstract circuit in (a) and
the concrete states in (b) are "not explicitly drawn with arrows". `asplos26-091_fig2`: register
bit-fields and a state machine "not explicitly linked by arrows or shared numbering".
`asplos26-094_fig3` *(looked at)*: panels (a)–(e) are an abstract LUT-splitting scheme and (f)/(h) a
concrete circuit, joined only by shared `S-M-E` notation. `nsdi25-062_fig12`: four diagram types
where matching a schedule block to its DFG node "relies entirely on remembering the colour code".
Also `asplos25-047_fig4`, `asplos26-047_fig7`, `asplos26-132_fig2`, `nsdi24-086_fig7`,
`nsdi25-044_fig7`, `osdi25-010_fig7`, `osdi25-016_fig6`, `osdi26-086_fig1`.
**Hurts because.** Each visual language needs its own reading protocol. When the link is only
implied, the reader must invent the very correspondence that is the figure's contribution.
**Do instead.** Two visual languages maximum, and only when one *feeds* the other — then **draw the
feeding**: arrows, shared numbering, or one colour used in both halves for the same object.
Otherwise split.
**Fine when.** The second language is a legend-scale inset — a mini-example, a zoom callout, a key.
`layout.zoom_callout` records this in only **9 of 152 records (6%)**: deliberate, not a habit.

### 22. A mechanism figure that is really a whole-system overview — **avoid** (boundary rule)

**Looks like.** Every subsystem as a named box, one arrow per interface, a dashed boundary round
"our system" — the figure answers *what are the parts* rather than *how does this part work*.
**Hurts because.** Nothing here or in `mechanism/style-rules.md` is calibrated for it, and the
architecture rules that are point elsewhere: labelled component boxes at a median of **21**
(mechanism 6), palette **6** fills (mechanism 4), step numbering a "should" there and a null here.
**Do instead.** The boundary, from `types_v3.md` and the owner's 2026-09-14 ruling: **`architecture`
means the whole-system overview and nothing else.** A hardware datapath, the internals of one
component, one port, one controller, one worked example — all mechanism. The near miss the other
way: "a design-space overview that names alternatives without showing the mechanism in each panel …
is subtype `concept`, not a mechanism figure."
**Fine when.** It genuinely is an overview — then switch to the architecture `style-rules.md` and
`anti-patterns.md` and draw it as one.

---

## §5 What carries over from the architecture anti-patterns

**Transfers unchanged.** Arch §1.2 *colour/icon coding with no legend* → 9; §1.5 *duplicated labels*
→ 10; §1.8 *meaning only in the caption* → 9; §1.9 *legend placed far away* → 18; §1.11 *colour-only
distinction* → 11; §1.12 *implied repetition without a count* → 13; §2.G *floating callouts* → 14/17;
§2.I *text colliding with lines* → 17; §2.L *partial legend* → 9.

**Transfers with a different number.** Arch §2.A *no colour system* is still the top hard-failure
signal — style-rules §1/§2 put `fill: none` in **3.9% of good vs 15.8% of ok+bad and 32.4% of bad**,
and the bad p25 for `palette.n` is exactly **0** — but the target is leaner: **≥3 fills, typically 4,
across 2–3 hue families**, not architecture's 6; §2.C *traffic-light palette* applies on that smaller
budget. Arch §1.1 *over-dense* and §1.3 *text too small* become 16 but are **inverted in diagnostic
value**: density is a *positive* signal here (`density.shapes` good 126 vs bad 43) and font size a
null, so treat both as craft floors, never as evidence a figure is weak. Arch §1.10 *aspect ratio*
becomes 19, where the lever is **height, not aspect**.

**Reverses — do not carry these over.**

- **Arch §2.B *no arrowheads*.** Not a defect here. Style-rules §5: arrowhead count is **not a
  signal** (good median 5 vs 4) and heads-per-line is *reversed* (0.31 vs 0.50). Good mechanism
  figures draw lanes, wires and rulers, not directed arrows. What is a signal is having connective
  structure at all: `arrows.lines` good median **11** vs 6.
- **Arch §2.E *shape zoo* and §2.J *one corner radius*.** Style-rules §4 finds the opposite:
  `corners=mixed` is a replicated good signal (**+13.6pp**, FDR p=0.00045) and **75.7% of bad
  mechanism figures are all-square**. More than one shape vocabulary — a pill for an operation, a
  square cell for a buffer slot, a circle for a state — is how this kind encodes role in shape. Keep
  arch's real point (a diamond is a decision, a cylinder is storage) and drop "one shape class".
- **Arch's step-numbering "should"** (δ=+0.18, FDR p=1e-6 there) is a null here. See 3 and 4.
- **Arch §2.D *everything drawn N times*.** Half applies: redrawing one template per frame *is* the
  evolution idiom. What the corpus dislikes is redrawing parts never acted on (`asplos25-151_fig13`).

---

## §6 Self-check: ask these of your own SVG

Render at print size first. Each question names the entry that explains it. These are questions to make you
look, not gates to pass: a "no" that you can justify from the figure's content is a legitimate answer — write
the justification in the plan, so a reviewer sees a decision rather than an oversight.

1. Can I name the one mechanism in five seconds, and is it **one** mechanism? (21, 22)
2. Is this **drawn**, or plotted / typeset? Marks from data or a text buffer are not this kind. (20)
3. Frames or panels: **is what changed marked** — colour, badge, callout, arrow? Only 4/36
   comparison and 2/29 evolution records leave it unmarked. (1)
4. Do the panels share one template, direction and set of lanes — and does each carry its own short
   tag and name **inside** the figure? (2)
5. More than four frames? Only 4.6% of the corpus exceeds four; can three carry the argument? (8)
6. Does every number mean "read me n-th", and only that — no ID, job, node or phase name dressed as
   a step marker — and do the figure's numbers agree with the prose? (3)
7. If the order is not obvious from the layout, is it marked; and if it *is* obvious, did I resist
   numbering it anyway? Numbering is not a quality checkbox here. (4)
8. Does every branch and transition carry its own guard, and end somewhere? No bare diamond edge, no
   free endpoint, no degree-0 state, no guard shared by two edges without a qualifier. (5, 6)
9. Is any label used for two different things **inside one panel**? Across panels is fine when the
   frame is visible and named. (10)
10. Can every value in a worked example be traced from input to result inside the figure? If a
    number cannot be checked, delete it or make it checkable. (7)
11. Is every colour, dash, hatch and non-obvious symbol keyed **inside** the drawing, not in the
    caption? 70% of the corpus keys nothing; be the exception. (9)
12. Would it still work photocopied in grey, and is colour assigned to roles, not instances? (11)
13. Is the loudest mark on the thing the caption's verb acts on? (14)
14. Does every `…`, pruned branch, ghost and empty placeholder carry a count, a rule or a name? (13)
15. At 240 pt (or 504 pt): anything below 6 pt, any label on a line, any edge label nearer a
    different edge than its own? If a label will not fit, fix the layout upstream. (16, 17, 19)
16. Does the figure have a fill palette at all (≥3 fills, 2–3 hue families) and more than one shape
    vocabulary? No-fill outline work and all-square boxes are the loudest bad-figure signals. (§5)

---

*Not design flaws.* **15 of the 215 weakness lines are extraction or sourcing artifacts** a drawing
agent cannot cause: truncated captions (`osdi26-040_fig1`, `osdi26-024_fig9`, `nsdi26-043_figtex18`,
`asplos26-057_fig9`), missing source-SVG palette metadata (`nsdi26-023_fig9`, `nsdi26-036_fig8`), a
crop bleeding in the neighbouring figure (`osdi26-037_fig5` ×2), a two-file figure of which only one
panel survived extraction (`asplos25-091_fig2`), figures with no body text to read against
(`sosp24-017_fig9`, `asplos26-103_figtex7`, `nsdi23-089_fig1`, `nsdi23-089_fig2`), a prose typo
(`sosp24-011_figtex2`), a schema-vocabulary limitation (`sosp24-024_fig3`), and one figure whose
PDF-extracted labels are worse than the author's original (`sosp23-002_fig5`). Ignore them when
reading the counts above.
