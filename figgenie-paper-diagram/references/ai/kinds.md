# The eight kinds of AI-venue Figure 1 (and how each one is drawn)

A *kind* is how a Figure 1 is organised to make its point: what the reader does with it (follow a process, learn
what a model is built from, compare alternatives, watch one example, grasp an idea, see the extent of a benchmark,
see who talks to whom, read a list of contributions). The kinds were found by clustering the first 384 labelled
figures and then labelled on every designed Figure 1 of ICLR, ICML, NeurIPS, CVPR, ACL and AAAI 2023-2026 (3,274
figures); the eighth, the contribution mosaic, was promoted from a tag on 2026-10-04 because AI papers use it often.

Three things to hold on to:

- **Kinds overlap.** 1,120 figures carry one kind, 1,908 two, 246 three or four. A spec lists every kind that applies,
  primary first (`meta.ai.kinds`); the primary one is the kind the caption's first sentence describes. A figure whose
  tiles hold a pipeline and a results chart is `contribution-mosaic` + `stage-pipeline`.
- **A kind is not a template.** It sets the reader's job and the spec blocks that carry it; the arrangement comes from
  the content and the exemplars (`layouts.md`), the field's habits from `domains.md`. The numbers below are what the
  corpus does, with how often, so that a choice is made knowingly. `other` is a value for the kind and the variant.
- **The kind and the sub-field are read together** (the two-view rule of the family): the same kind looks different
  in vision and in agents, and `domains.md` says how.

## Choosing

Ask in this order and keep every yes:

1. Does the reader follow one process from input to output, stage by stage? **stage-pipeline**
2. Do they learn what a model is built from and where the new part plugs in? **model-anatomy**
3. Is the point a difference between alternatives drawn in the same grammar? **side-by-side-contrast**
4. Is one concrete instance redrawn after each step, with real or toy values? **worked-walkthrough**
5. Is an idea made visible without drawing the system (a space, a formal object, an analogy, a phenomenon on
   examples)? **concept-schematic**
6. Does it map the extent of a benchmark, dataset, taxonomy or model family? **scope-overview**
7. Is it a cast of actors and what they exchange? **actor-interaction**
8. Is it tiles, each carrying one contribution, with no process running through them? **contribution-mosaic**

When two kinds are equally primary, the one whose block structure holds the other wins (a mosaic holds a pipeline
tile; a contrast holds two anatomies). Say in the brief which kinds the figure is and why; "none exactly" is allowed.

## At a glance

| kind (`meta.ai.kinds`) | primary | any | usual second kind | top sub-fields | the reader | the figure usually holds |
|---|---:|---:|---|---|---|---|
| `stage-pipeline` | 26% | 44% | walkthrough 25%, anatomy 20% | llm-nlp 34%, science 13%, multimodal 10% | follows the stages | 2-5 titled stages, hand-offs named, icons or samples inside stages |
| `model-anatomy` | 27% | 41% | pipeline 27% | science 23%, vision 21%, ml-core 14% | learns the parts | encoders, blocks, heads, losses; tensors and tokens between them; frozen marks |
| `side-by-side-contrast` | 22% | 30% | anatomy 25%, pipeline 19% | llm-nlp 24%, vision 21%, multimodal 15% | compares lanes | mirrored lanes or (a)-(d) panels, verdict marks, the same input repeated |
| `worked-walkthrough` | 3% | 16% | pipeline 34%, concept 21% | llm-nlp 38%, multimodal 23% | watches one example | the same object redrawn per step, screenshots, text turns, an outcome |
| `concept-schematic` | 10% | 21% | contrast 24% | ml-core 35%, science 16%, llm-nlp 15% | grasps the idea | axes, blobs, vectors, formal diagrams, formulas; few boxes |
| `scope-overview` | 5% | 10% | pipeline 16% | multimodal 40%, llm-nlp 19% | surveys the space | equal cards with samples, a taxonomy, a sunburst, counts |
| `actor-interaction` | 3% | 7% | pipeline 38%, walkthrough 19% | agents 35%, ml-core 20%, llm-nlp 16% | sees who does what | icons as nodes, labelled two-way or cyclic arrows, bubbles, role tints |
| `contribution-mosaic` | 4% | 5% | scope 60%, pipeline 17% | multimodal 35%, rl-robotics 11% | reads a list | tiles of unlike content: schematic, chart, outputs, headline number |

Shares are of the 3,274 designed Figure 1s (primary = first kind; any = primary or secondary).

## Numbers by kind

What the pre-screen labelled on every figure (corpus shares) and what the SVGs of the good figures measure (medians):

| | family | pipeline | anatomy | contrast | concept | scope | walkthrough | actors | mosaic |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| built as boxes and arrows | 58% | 79% | 90% | 34% | 19% | 4% | 26% | 67% | 9% |
| built as panels | 30% | 15% | 9% | 57% | 55% | 49% | 32% | 9% | 71% |
| one panel / four or more | 16% / 21% | 17% / 23% | 26% / 12% | 3% / 22% | 19% / 17% | 11% / 49% | 18% / 20% | 29% / 3% | 0% / 57% |
| reads left to right | 54% | 62% | 59% | 54% | 55% | 21% | 44% | 29% | 31% |
| no step markers / letters / numbers | 60 / 22 / 10% | 52 / 13 / 20% | 71 / 20 / 3% | 52 / 37 / 6% | 59 / 30 / 5% | 77 / 16 / 5% | 52 / 6 / 23% | 50 / 3 / 7% | 62 / 24 / 9% |
| no pictures / six or more | 47% / 26% | 51% / 26% | 43% / 21% | 46% / 31% | 59% / 19% | 25% / 47% | 46% / 22% | 61% / 10% | 21% / 50% |
| pictures as sample i/o / thumbnails / results | 34 / 10 / 7% | 28 / 12 / 6% | 48 / 5 / 4% | 35 / 6 / 11% | 21 / 9 / 9% | 25 / 36 / 7% | 36 / 6 / 5% | 14 / 8 / 2% | 28 / 27 / 19% |
| many icons / none | 30% / 46% | 42% / 30% | 10% / 66% | 36% / 42% | 16% / 65% | 49% / 31% | 31% / 48% | 83% / 7% | 49% / 25% |
| speech or thought bubbles | 25% | 33% | 7% | 29% | 13% | 45% | 50% | 47% | 40% |
| formulas | 50% | 44% | 78% | 36% | 64% | 7% | 28% | 33% | 21% |
| six or more hues | 30% | 29% | 34% | 24% | 21% | 57% | 17% | 32% | 58% |
| tinted regions as ground | 33% | 37% | 34% | 28% | 17% | 49% | 20% | 40% | 50% |
| legend | 30% | 21% | 39% | 30% | 33% | 24% | 26% | 19% | 36% |
| frozen / trainable marks | 9% | 8% | 17% | 9% | 1% | 1% | 0% | 3% | 8% |
| labelled dense | 52% | 54% | 64% | 43% | 28% | 74% | 32% | 41% | 79% |
| good figures measured | 844 | 187 | 171 | 147 | 77 | 87 | 40 | 48 | 101 |
| text boxes (median) | 14 | 15 | 17 | 12 | 4 | 24 | 12 | 18.5 | 22 |
| text runs | 69 | 74 | 70 | 60 | 57 | 96 | 76 | 58 | 91 |
| raster images / share of canvas | 8 / 10% | 9 / 9% | 5 / 6% | 8 / 11% | 4 / 13% | 18 / 24% | 7 / 10% | 9.5 / 8% | 21 / 27% |
| distinct fill colours | 9 | 9 | 12 | 8 | 7 | 11 | 6 | 9 | 11 |
| arrowheads | 7 | 7 | 16 | 7 | 3 | 2 | 3.5 | 8.5 | 3 |
| width x height, pt | 460 x 198 | 460 x 202 | 474 x 209 | 460 x 186 | 404 x 168 | 461 x 242 | 460 x 195 | 460 x 187 | 466 x 227 |

The lint's budget of labelled boxes per kind (q3 / p90 of the good figures' text boxes) is in `style-thresholds.json`
`lint.node_budget`: pipeline 28 / 58, anatomy 31 / 56, contrast 26 / 59, walkthrough 24 / 68, concept 13 / 31, scope
34 / 85, actors 29 / 42, mosaic 32 / 70. These are counts of what good figures hold at full text width; a figure
over the p90 is asked to merge or split, never told to.

## stage-pipeline — the method as ordered stages

**What it is.** The method drawn as a sequence of stages (collection or synthesis, filtering, training, retrieval,
inference, verification) joined by arrows that hand data or artifacts on. Boxes are named by what they do; models stay
black boxes or icons inside a stage. Cues: 2-5 titled stage boxes, shaded columns or bands, often numbered or
lettered; one dominant reading path (left to right in 62%); mixed content per stage (an LLM, a database, a robot or
person icon, a small table, a text snippet, thumbnails at the input and output ends); named hand-offs (dataset,
pseudo-labels, trajectories, checkpoint).

**Variants** (share of the kind's 861 primary figures): `stage-chain` 51% (one row or column, perhaps one loop-back),
`phase-bands` 18% (stacked bands for phases that share components: training / inference, offline / online),
`closed-loop` 11% (generate-verify-correct or act-store-train drawn as a cycle or as iteration snapshots),
`data-construction` 11% (sources, filtering, annotation, verification, then the dataset; funnels, counts, one example
record), `fan-out` 8% (one pipeline fans out to tasks or applications, each ending in an example),
`decision-flowchart` 1%.

**Spec.** `nodes[]` per stage and per thing inside it (icons `kind: icon`, samples `kind: image` with a role, text
snippets `kind: text`), `containers[]` for the stages or bands, `edges[]` for the hand-offs with their labels,
`steps[]` when the stages are numbered (plain numbers 20%, letters 13%, circled 7%); phase bands are `lanes[]` or
`panels[]` with `axis: stages`.

**When it differs.** A pipeline whose stages open a model's internals is anatomy as well (20%); one that follows a
real example through the stages is a walkthrough as well (25%). A data-construction pipeline carries counts and one
record, not module boxes.

**Exemplars** (deep record, rated good): `aaai25-0102_fig1` closed loop · `aaai25-0119_fig1` data construction ·
`aaai26-0001_fig1` data construction (audio); `find_ai_exemplars.py search --kind stage-pipeline ...` for more.

## model-anatomy — the inside of a learned model

**What it is.** Encoders, layers, attention and fusion blocks, heads and loss terms wired together, with tensors,
tokens or embeddings flowing between them; the reader learns what is shared, frozen or trained and where the new
component plugs in. Cues: blocks named after network parts (encoder, decoder, Transformer, GCN, Mamba, U-Net, MLP,
projector, head), often trapezoids; tensor and token glyphs (rows of small squares, feature-map stacks, matrices) and
operators (sum, product, concat); loss nodes at the ends of branches; frozen or trainable badges; repeated blocks
(xN, t-1 / t / t+1), skip connections, a zoomed inset of the new block; few icons (none in 66%); formulas in 78%.

**Variants** (889): `end-to-end-network` 33%, `overview-plus-zoom` 30% (the network plus an enlarged inset or
lettered sub-panels of the new block), `multi-branch-fusion` 18% (parallel encoders merged by a fusion block),
`objective-graph` 14% (the training objective is the structure: views, encoders, embeddings, loss terms),
`unrolled-chain` 5% (one block repeated over steps, layers or devices).

**Spec.** `nodes[]` for blocks (`kind: module`, with `idiom` when the block is a known drawn form: `transformer-block`,
`lora-adapter`, `encoder-decoder`, `vae-codebook`, `diffusion-chain`), `kind: compute` for operators, tensors as
`token-strip` / `vector-cells` parts, `edges[]` of `kind: data`, `gradient` or `attention`, `multiplicity` for xN,
`state` (frozen / trainable) on nodes with a `snowflake-fire` or colour key in the legend; a zoom as `panels[]` with
`axis: zoom` or an inset annotation. The 86 whole-model figures by model type are in `model-architectures.md`.

**When it differs.** When the figure is one process with the model opened only at one stage, it is a pipeline with an
anatomy inset. Audio and science figures draw anatomy as plain boxes bottom-up; vision as encoder-decoder pairs around
pictures (`domains.md`).

**Exemplars:** `aaai25-0124_fig1` overview plus zoom (audio) · `aaai24-0047_fig1` objective graph (multimodal) ·
`aaai23-0023_fig1` overview plus zoom (recommendation).

## side-by-side-contrast — alternatives in the same grammar

**What it is.** Two or more alternatives drawn in the same visual grammar in parallel lanes or panels so that the
difference is the message: prior vs proposed, naive vs fixed, a family of design variants, several methods' outputs on
one input. Cues: mirrored rows or columns with an identical layout, only the differing element highlighted; lane
labels (existing, previous, naive vs ours, proposed); sibling schematics (a)-(d) with the proposed one last; verdict
marks at lane ends (red cross, green tick, sad and happy faces, a star, a short consequence label); the same input
repeated at the head of each lane. Letters head the panels in 37%, more than any other kind.

**Variants** (723): `paired-lanes` 49%, `design-family` 32% (three or more siblings, sometimes a tick / cross feature
table), `problem-then-fix` 10% (a failure diagnosed on an example, then the remedy), `output-comparison` 10% (one
input, several methods' outputs aligned).

**Spec.** `panels[]` with `axis: alternatives` (one per lane, `verdict` ours / baseline / fails), the shared template
drawn once and repeated (`frame_template: identical` or `aligned`), `deltas[]` for what each lane changes, verdict marks
as `annotations[]` of `kind: verdict`; an output comparison puts the outputs as `kind: image` nodes per panel.

**When it differs.** A contrast whose lanes are anatomies or pipelines carries that kind too (anatomy 25%, pipeline
19%); when the alternatives are two columns of one table, draw the table.

**Exemplars:** `aaai25-0013_fig1` design family (vision) · `acl23-0022_fig1` output comparison (llm-nlp) ·
`acl26-0047_fig1` paired lanes (audio).

## worked-walkthrough — one instance followed through the steps

**What it is.** One concrete run: a specific image, graph, conversation or GUI session followed through numbered steps
and redrawn after each, so the reader watches the method act on real or toy values. The instance is the protagonist;
operations shrink to arrow labels or small boxes. Cues: the same object drawn three or more times with the change
highlighted; step numbers (plain numbers 23%, labelled arrows 13%) or lettered panels in narrative order; real
screenshots, frames, text turns or cartoon characters rather than module boxes (bubbles in 50%); the run ends in an
outcome (an answer bubble, a verdict, a final state). Primary in only 3% of figures but secondary in 13% more: "with an
example running through it" is mostly a modifier.

**Variants** (104): `real-io-trace` 46% (an agent or model run with its real inputs and outputs), `state-snapshots` 37%
(the same object redrawn after each step at the same position), `scenario-narrative` 9% (characters act out a story),
`iteration-rounds` 8% (the same update for rounds 1..k).

**Spec.** `steps[]` along the structure (with `carries` when one object is followed), or `panels[]` with `axis: time`
for snapshots and `deltas[]` per frame; real text as `kind: text` or `kind: bubble` nodes with the actual words; real
pictures as `kind: image` with `role: sample-input` / `sample-output`; `values[]` when the numbers are the content
(`worked_example: true`).

**When it differs.** A walkthrough over a pipeline is both; one that contrasts two runs is a contrast. The text of real
examples sets the size of everything else: measure it first.

**Exemplars:** `acl24-0005_fig1` state snapshots (ml-core) · `acl25-0013_fig1` iteration rounds (llm-nlp) ·
`acl25-0080_fig1` iteration rounds (multimodal).

## concept-schematic — the idea without the system

**What it is.** An abstract idea made visible: a geometric picture (manifold, contour landscape, embedding space,
vectors, methods' trajectories), a formal diagram (graphical model, automaton, derivation chain, game, matrix
decomposition), an analogy scene, or a phenomenon shown on a few examples or an annotated curve. Cues: few or no
processing boxes; axes, contours, blobs, surfaces, vectors; circles for variables with plates, state circles with
labelled transitions, boxed claims chained into a derivation; formulas and the paper's symbols as the main labels
(formulas in 64%); a sparse palette (white ground 75%, one or two hues 16%, the highest share) and 1-3 panels in a row;
the fewest labelled boxes of any kind (median 4) and the most text per box.

**Variants** (323): `formal-diagram` 37%, `phenomenon-on-examples` 31%, `geometric-intuition` 27%, `analogy` 5%.

**Spec.** Mostly `nodes[]` of `kind: other` or `note` with formulas (`tex`), `annotations[]` with leaders, a drawn
space as a `data-scale="data"` group or a `schematic-plot` part, `edges[]` of `kind: mapping` or `transition`; a
graphical model uses `kind: state` nodes. The spec is thin here; the drawing plan carries the geometry.

**When it differs.** When the idea is shown by contrasting two cases it is a contrast too (24%); a formal diagram of a
model's parts is anatomy.

**Exemplars:** `acl23-0002_fig1` phenomenon on examples (llm-nlp) · `iclr23-0107_fig1` geometric intuition (vision) ·
`iclr24-0044_fig1` phenomenon on examples (multimodal).

## scope-overview — the extent of a benchmark, dataset or family

**What it is.** A map of a space: the tasks, categories, domains or sources a benchmark, dataset or general model
covers, or the family of prior methods and where the work sits. Drawn as a gallery of example cards, a taxonomy (tree,
sunburst, radial genealogy, nested sets), a hub with spokes, or a dashboard of these with statistics. Cues: repeated
equal-size cards, each with a title band, a real sample and a prompt or answer; categorical colour (six or more hues in
57%) with labelled groups; grid arrangement 47%; no single reading path (mixed or centre-out; left to right only 21%);
the most pictures (six or more in 47%, thumbnails 36%) and text (median 96 runs, 24 text boxes) of any kind; the
tallest figures (median 242 pt).

**Variants** (154): `example-gallery` 35%, `benchmark-dashboard` 25%, `taxonomy-map` 22%, `hub-and-spoke` 17%.

**Spec.** `panels[]` with `axis: examples` (one card per task or category) or a `grid` of card nodes, each card a
`container` with a title and `kind: image` / `kind: text` children; a taxonomy as nested `containers[]` or a
`sunburst-taxonomy` / `taxonomy-tree` part; counts as `values[]` or a `data-scale` chart; a legend for the category
colours (`legend` 24%, usually direct labels instead).

**When it differs.** A scope overview with a method tile is a mosaic; a dataset pipeline with counts is a pipeline
(`data-construction`). Multimodal benchmarks are the home of this kind (40%).

**Exemplars:** `acl24-0062_fig1` example gallery (agents) · `acl25-0093_fig1` example gallery (multimodal) ·
`acl25-0154_fig1` example gallery (llm-nlp).

## actor-interaction — who does what

**What it is.** The method as a cast of actors (agents, users, environment, tools, server and clients, cloud and
device) and the messages, actions and feedback they exchange; the reader learns who does what and how the exchanges
repeat rather than following one input to one output. Cues: character, robot, person, computer or cloud icons as the
main nodes (many icons in 83%); labelled two-way or cyclic arrows (request, observation, action, feedback, model
update); role colours, a role legend, tinted role regions (40%); chat or thought bubbles with sample messages (47%);
loops, hierarchies of agents, facing columns for two parties; left to right only 29%, labelled arrows as step markers
29%.

**Variants** (89): `multi-party-exchange` 45% (agent and user, cloud and device, server and clients),
`single-agent-loop` 35% (one agent with environment, tools, memory or user), `multi-agent-organization` 20% (a
hierarchy, teams, a debate).

**Spec.** `nodes[]` of `kind: actor` or `icon` (vector icon parts, or a bitmap the user supplies as `kind: image`),
`edges[]` of `kind: message` or `interaction` with labels and `order` for a sequence, `kind: bubble` nodes for sample
messages, tinted `containers[]` per role; `meta.ai.arrangement: hub` or a loop in the plan; colour by actor (64% of
agent figures, `encoding.md`).

**When it differs.** When the exchange is drawn as stages in time it is a pipeline too (38%); when a real session is
replayed it is a walkthrough too (19%). Logos and mascots for the models are the paper's own material.

**Exemplars:** `aaai24-0061_fig1` single agent loop (agents) · `aaai25-0083_fig1` multi-party exchange (ml-core:
LLM-guided architecture search) · `cvpr25-0092_fig1` single agent loop (optics).

## contribution-mosaic — tiles, one per contribution

**What it is.** Figure 1 as separate tiles or titled sections, each carrying one contribution, finding, capability or
deliverable (a headline number, a mini chart, sample outputs, a mini schematic, a small pipeline), read as a list of
what the paper offers; no process runs through them. Cues: a bento grid of rounded tiles, often around a title or logo
tile; sections titled by the paper's parts (Task / Model / Data, Framework / Benchmark, Analysis / Implication);
numbered or titled panels with no arrows between them or one loose "leads to" arrow; tiles of unlike content; a
headline claim or the paper's name set large. Four or more panels in 57%; grid 58%; six or more hues 58%; the most
raster images (median 21, 27% of the canvas); dense in 79%. Always with a second kind (scope overview 60%, pipeline
17%) because each tile has a kind of its own.

**Variants** (131): `bento-highlights`, `paper-roadmap`, `deliverables-triptych`, `capability-cards`, `finding-cards`
(the pre-screen recorded the tiles' own variants: benchmark dashboard 34%, example gallery 17%, fan-out 7%).

**Spec.** `panels[]` with `axis: narrative` (or `part`, when the tiles are a composite in the systems sense), each with
its own `kind` and budget; a title tile as `annotations[]` of `kind: label` with the paper's name (`title-branding`,
the paper's logo is its own material); charts as `data-scale="data"` groups or `kind: chart` nodes; headline numbers as
`values[]` with `highlight`.

**Boundaries.** A scope overview surveys one subject (what a dataset covers); a mosaic lists the paper's separate
contributions. A contrast shows alternatives of one thing in aligned panels; mosaic tiles are different things. A
pipeline with phase bands runs one process through its bands; mosaic tiles have no process between them.

**Exemplars:** `aaai25-0059_fig1` deliverables triptych (generative) · `aaai26-0009_fig1` capability cards
(rl-robotics) · `acl23-0041_fig1` capability cards (llm-nlp).

## Where the kind sits in the workflow

- Brief (step 1): name the kinds, primary first, with the variant when one fits, and say what the reader does with the
  figure; the sub-field next to it (`domains.md`).
- Exemplars (step 3): `find_ai_exemplars.py search --kind <primary>,<secondary> --subfield ...` ranks candidates by
  kind, field, tags and meaning (`exemplar-retrieval.md`); at least one pick should share the kind but not the field.
- Spec (step 2): `meta.ai.kinds`, `meta.ai.variant`, the blocks named above (`spec-guide.md` §9); the validator only
  warns about kind structure, and `meta.ai.arrangement` describes the drawing you decided on (`layouts.md`).
- Plan and check (steps 4, 6): the budget and the picture, text and formula habits of the kind (`style-rules.md`,
  `style-thresholds.json` `by_kind`); the advisory checks name the kind they compare against (`anti-patterns.md` §5).
