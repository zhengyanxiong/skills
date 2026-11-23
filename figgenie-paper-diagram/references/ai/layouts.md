# Layouts of AI-venue Figure 1s: how the canvas is divided and read

There is no template list for this family. An AI-venue Figure 1 is arranged by what it holds — stages, panels,
cards, lanes, a hub, a chat column — and the same kind of figure is laid out several ways. This page gives the
vocabulary of arrangements, how often each is used, by which kinds and fields, with what size, panels, reading
direction, markers and density, so that an arrangement is chosen for this figure's content and the choice is a
knowing one. `meta.ai.arrangement` *describes* the arrangement decided on; it does not pick it.

## How to read this

- **Sources.** The 336 figures with a deep semantic record (good figures chosen for coverage; shares are of that pool)
  for arrangement, panels, reading, markers, legend, zoom, density and composition motifs; the pre-screen labels of all
  3,274 designed Figure 1s for the coarse facts (base, panel count, reading direction, step markers, ground); the
  measured SVGs for sizes. Each table gives the pool, the eight kinds and the nine sub-fields: the two views.
- **The kinds** (`kinds.md`) decide what the panels or stages carry; this page says how they are placed. The field
  (`domains.md`) shifts the habits: audio reads bottom-up, science-engineering stacks rows, agents loop.
- Nothing here is required; the print rules are in `style-rules.md` and SKILL.md.

## 1. Choosing the arrangement

Ask, in this order:

1. **Is it one drawing or several units?** One drawing (`single`, `free`, `hub`) in 7% of the pool; the rest are units
   in a row, column, grid, bands or lanes. The pre-screen counts one panel in 16% of all figures, two in 31%, three in
   32%, four in 13%, five or more in 8%.
2. **What do the units vary along?** Stages of one process → `pipeline-row` / `pipeline-column` or `bands` (phases);
   alternatives → `panels-row` / `panels-column` with the same grammar in each; examples or categories → `cards-grid`
   / `panels-grid`; actors or modalities that run in parallel → `lanes`; a part enlarged → `inset`; a dataset summed up
   → `dashboard`; a dialogue → `chat-column`.
3. **Which way does the reader go?** Left to right is the pre-screen's majority (54%) and the records' plurality
   inside a mixed figure (31% pure); top-down for a column of frames or a flowchart; bottom-up for a network stack
   (anatomy 23%, audio 36%); radial or none for a hub or a gallery.
4. **What sits around the main unit?** A strip along the top (title, inputs, a film strip: 24%) or the bottom (legend,
   results, examples: 24%), a side panel (11%), an attached chart (17%, mosaics 52%), a zoom (7%).

| arrangement (`meta.ai.arrangement`) | pool | full width | median w x h, pt | aspect | most in | what it is |
|---|---:|---:|---:|---:|---|---|
| `panels-row` | 27% | 97% | 460 x 190 | 2.4 | contrast 35%, mosaic 33%, actors 32%, anatomy 31%; audio 50% | two to four framed units side by side, lettered or titled |
| `panels-grid` | 23% | 96% | 482 x 219 | 2.1 | mosaic 38%, contrast 33%, concept 32%; science 48% | units in two rows or more |
| `bands` | 13% | 91% | 460 x 235 | 1.9 | actors 29%, walkthrough 17%, pipeline 16%; science 29% | full-width horizontal layers (phases, tiers, modalities) |
| `lanes` | 8% | 89% | 476 x 194 | 2.6 | actors 18%, contrast 13%; llm-nlp 16%, agents 15% | parallel aligned tracks sharing one axis (per actor, method, modality) |
| `pipeline-row` | 7% | 100% | 463 x 179 | 2.7 | pipeline 18%, anatomy 13%; audio 14% | one chain of stages left to right, no panel frames |
| `free` | 4% | 100% | 495 x 211 | 2.4 | walkthrough 14%, actors 7%; vision 9%, multimodal 7% | a scene or a composed drawing with no grid |
| `panels-column` | 4% | 42% | 309 x 225 | 1.4 | walkthrough 7%, contrast 6% | units stacked; the one arrangement that often sits in a column |
| `hub` | 3% | 73% | 404 x 207 | 1.8 | scope 11%, actors 7%, mosaic 7%; multimodal 10% | one unit in the centre, the rest around it |
| `cards-grid` | 3% | 90% | 465 x 284 | 2.0 | scope 13%; multimodal 12% | equal cards with a title band and a sample each; the tallest arrangement |
| `dashboard` | 2% | 100% | 501 x 242 | 1.9 | scope 15%; generative 12% | a taxonomy plus statistics charts plus examples in one composite |
| `pipeline-column` | 1% | 60% | 402 x 164 | 2.1 | pipeline 3% | a chain read top-down |
| `inset` | 1% | — | — | — | anatomy 6%; multimodal 5% | the whole plus one enlarged part tied by a wedge or leaders |
| `single` | 1% | 60% | 402 x 163 | 1.6 | concept 12% | one unframed drawing |
| `chat-column` | 1% | — | — | — | walkthrough 7% | a transcript as the spine, with drawings beside the turns |
| `other` | 1% | — | — | — | — | say what it is in `notes` |

The pre-screen's coarser count over all figures: row 47%, grid 21%, column 15%, single 12%, nested 2%, other 3%.
Panels in a column fit a single column of a two-column venue; everything else wants the full text width (`style-rules.md`
§10).

## 2. Panels

A panel is a separately framed, lettered or titled unit. Pool: one panel 25%, two 23%, three 24%, four 15%, five or more
14%; a contribution mosaic never has one (three in 45%, five or more in 29%), a walkthrough or an actor figure is one
drawing half the time (52%, 50%), a contrast has two to four (12% one), a scope overview five or more in 36%; science-
engineering figures run to five or more in 43%.

**What the panels are split by** (figures with more than one panel, 253; a figure may use two axes):

| axis (`panels[].axis`) | pool | where it dominates |
|---|---:|---|
| `narrative` — problem, method, result; task, model, data | 34% | concept 61%, mosaic 60%, science 53%, actors 43% |
| `alternatives` — the same thing done differently | 27% | contrast 83%, generative 55%, rl-robotics 40% |
| `stages` — steps of one process | 24% | pipeline 67%, walkthrough 50%, rl-robotics 44%, audio 44% |
| `examples` — cases side by side | 20% | scope 49%, multimodal 47%, mosaic 33% |
| `overview` — the whole next to its parts | 19% | anatomy 49%, audio 50% |
| `zoom` — a part enlarged | 9% | anatomy 46%, audio 31% |
| `time` — successive states | 3% | concept 17%, ml-core 13% |
| `modalities` | 2% | scope 7% |

49 figures carry a prior or failing case next to the proposed one: prior first and ours last in 76%, mixed order 14%,
ours first 10%.

**Panel markers:** titles 39%, none 29%, letters and titles 24%, letters alone 5%, numbers 3%. Scope overviews title
their cards (60%); contrasts letter and title theirs (40%); walkthroughs and actor figures mostly mark nothing (62%,
57%); science-engineering figures almost always mark (none 5%).

## 3. Reading

**Direction** (pool): mixed 45%, left to right 31%, top-down 14%, bottom-up 5%, none 4%, radial 2% — "mixed" means a
left-to-right main path with stacks, loops or columns inside it. By kind: pipelines left-right 44% (mixed 52%);
anatomy bottom-up 23%; contrasts top-down 19%; walkthroughs top-down 31%; scope overviews none 23%, radial 9%; actors
mixed 68%; mosaics mixed 64%. By field: audio bottom-up 36%, vision left-right 47%, multimodal none 12%. The pre-
screen over all figures: left-right 54%, mixed 29%, top-down 11%, circular 3%, none 2%, centre-out 2%.

**Where reading starts:** top-left 75%, left 12%, top 5%, centre 2%, other 6%. Anatomy starts top-left only in 50%
(a quarter start elsewhere: the input at the bottom, the centre of a zoom); audio 36%; contrasts 88%.

**Lanes** (aligned tracks that are not panels: per actor, modality, method or phase) in 41% of the pool; contrasts
56%, walkthroughs 48%, mosaics 17%.

## 4. Markers, legend, zoom

**Step markers** (pool): none 68%, labelled arrows 11%, plain numbers 7%, circled numbers 7%, in-text 2%, letters 1%.
Pipelines mark steps in half the figures (labelled arrows 20%, plain numbers 15%); walkthroughs in two thirds (21% /
21% / circled 10%); actor figures use labelled arrows 32% and circled numbers 21%; anatomy, contrast and scope almost
never (87%, 83%, 96% none). The pre-screen over all figures: none 60%, letters 22%, plain numbers 10%, labelled arrows
5%, circled numbers 4% — the circled number of systems figures is rare here; plain digits and lettered panels do the
work. Markers that are identities (h1 ... hn, L0 ... L9) are not steps: `encoding.md` Part D.

**Legend** (pool): none 59%, inside the figure 23%, caption only 7%, per panel 6%, below 4%, right 1%. Anatomy and
contrast carry one in 56%; pipelines 28%, actor figures 25%. A direct label on the first instance is the usual
substitute, and "a code the figure does not explain" is the second most named weakness of good figures
(`anti-patterns.md` §3).

**Zoom call-out:** none 81%, a wedge 7%, leader lines 7%, a title only 2%, other 3%; anatomy 37% (wedge 15%, title
only 12%: the lettered sub-panel named in the main drawing), science-engineering 33%, walkthrough 7%. Tie the enlarged
part to its source by a wedge or leaders: "no leader ties the zoom to its box" is a recorded weakness.

## 5. Density

- **Visual density** (pool): dense 65%, moderate 34%, sparse 1%. Scope 77%, mosaic 76%, anatomy 73% dense; concept
  44%, walkthrough 45%. The pre-screen over all figures: dense 52%, medium 41%, sparse 7%; good figures 57% dense,
  weaker ones 31%.
- **Text density:** moderate 58%, dense 25%, sparse 17%; walkthroughs 41% dense (real turns and prompts), agents 45%,
  multimodal 43%; vision and generative 29-36% sparse.
- **Share of the area that is text:** small 68%, medium 23%, large 9%. Anatomy 94% small, vision 97%; walkthroughs
  41% large; agents 45% medium.
- **Amount of content:** 13 elements (p25 11, p75 16) and 9 relations in the median record; anatomy 16 and 12,
  walkthrough 11 and 7, scope 12 and 6, audio 16 and 14. Measured on the SVGs, good figures hold 69 text runs and 14
  text boxes (`style-rules.md` §9, budgets per kind in `style-thresholds.json`).

## 6. Composition motifs

Mined from the records' layout descriptions; a figure shows three on median, and they combine freely.

| motif | pool | meaning | high in |
|---|---:|---|---|
| `centre-piece` | 31% | one unit in the centre the rest refer to | mosaic 45%, scope 43%, actors 36% |
| `cards` | 28% | units drawn as cards or tiles | scope 55%, mosaic 48%, multimodal 48% |
| `rows` | 25% | stacked horizontal rows or bands | science 52%, generative 40%, mosaic 38% |
| `bottom-strip` | 24% | a strip along the bottom: legend, results, examples, summary | audio 41%, scope 34% |
| `top-strip` | 24% | a strip along the top: title, inputs, film strip, legend | audio 45%, scope 38%, multimodal 35% |
| `input-left-output-right` | 22% | inputs at the left, outputs at the right | pipeline 36%, anatomy 33%, science 33% |
| `columns` | 20% | side-by-side columns | multimodal 33%, concept 32%, vision 29% |
| `chart-attached` | 17% | a chart or plot beside the drawing | mosaic 52%, rl-robotics 24%, llm-nlp 22% |
| `grid` | 15% | a regular grid of units | vision 32%, scope 21% |
| `side-panel` | 11% | a narrower unit at one side | actors 25%, audio 23% |
| `loop` | 10% | a cycle or ring | actors 43%, agents 36% |
| `zoom` | 7% | a part enlarged elsewhere | anatomy 21%, audio 14% |
| `fan` | 7% | one fans out to several, or several merge | anatomy 13% |
| `top-down` | 6% | reads from the top down | science 14%, llm-nlp 12% |
| `title-in-figure` | 6% | a title, claim or logo set into the figure | scope 19%, generative 16% |
| `bottom-up` | 5% | inputs at the bottom, outputs at the top | audio 45%, anatomy 19% |
| `mirrored` | 4% | two halves in the same grammar | actors 14%, agents 12% |
| `timeline` | 1% | an explicit time or step axis | — |

## 7. Ground and grouping

- **Ground** (pool): white 63%, tinted regions 31%, grey panels 6% (the pre-screen over all figures: 61% / 33% / 6%).
  Scope overviews are tinted in 49%, agents 48%, multimodal 45%; science-engineering is white in 90%, walkthroughs 83%,
  generative 80%.
- **How parts are set apart** (a figure uses two devices in 49%, three in 33%): tinted regions 60%, framed boxes 59%,
  dashed boxes 45%, white space 41%, panel frames 15%. Actors tint 86%; contrasts and walkthroughs lean on white space
  (58%, 62%); pipelines frame 70%. On a white ground the devices are white space 58% and frames 54%; on a tinted
  ground, frames 65% and dashed boxes 55% inside the tints.
- **Nesting depth:** flat 12%, regions holding parts 44%, regions inside regions 42%, deeper 1%; actors and scope go
  three deep in 57% and 53%, concept and walkthrough stay at two (68%, 55%).
- **Region tints:** one tint per figure in 56%, two 25%, three or more 19%; grey 37% of tints, orange 21%, green 13%,
  blue 12%, teal 6%; lightness median 0.91 (p10 0.82, p90 0.96), saturation median 0.10 (p90 0.20). The values most
  used are the Office tints: `#f2f2f2`, `#fff2cc`, `#fbe3d6` / `#fbe5d6`, `#d9f2d0` / `#e2f0d9`, `#dceaf7` / `#deebf7`
  (`palettes.md` §7).

## 8. Inventing an arrangement

Four per cent of the pool is `free` and one per cent `other`; a figure that fits no row of §1 is normal. Keep what the
corpus keeps even then:

- one reading path the eye can find from the top-left or from a marked start, with the contribution on it;
- one grammar for repeated units (the same frame, title style and sample size in every card or lane);
- the full text width unless the content is a column; height from the content (median 198 pt, p95 317);
- the budget of the kind (`style-thresholds.json` `by_kind`): more units means smaller units, never smaller type;
- a strip for what is not the main drawing (legend, results, the paper's name) rather than a scattering;
- a zoom tied by a wedge or leaders; a loop drawn as a ring with its direction marked.

Write the arrangement in your own words in the plan and `meta.ai.notes`; `arrangement: other` is a value.

## 9. Figures to look at, per arrangement

Deep-record exemplars (open with `python3 scripts/find_ai_exemplars.py files ID`):

- `panels-row`: aaai23-0023_fig1, aaai24-0061_fig1, aaai25-0013_fig1, aaai25-0069_fig1, aaai25-0102_fig1, aaai25-0124_fig1, acl23-0008_fig1
- `panels-grid`: aaai25-0057_fig1, aaai25-0073_fig1, aaai25-0119_fig1, aaai26-0006_fig1, acl23-0002_fig1, acl24-0062_fig1, acl25-0013_fig1
- `bands`: aaai25-0009_fig1, aaai25-0059_fig1, aaai25-0071_fig1, aaai25-0083_fig1, acl24-0024_fig1, acl25-0048_fig1
- `lanes`: aaai26-0001_fig1, acl23-0022_fig1, acl24-0007_fig1, cvpr24-0028_fig1, iclr25-0140_fig1
- `pipeline-row`: aaai25-0067_fig1, aaai25-0072_fig1, aaai25-0110_fig1, acl23-0082_fig1, acl25-0127_fig1, iclr23-0013_fig1
- `free`: acl24-0005_fig1, cvpr24-0031_fig1, cvpr25-0026_fig1, iclr23-0028_fig1, icml24-0039_fig1
- `panels-column`: acl23-0028_fig1, acl26-0014_fig1, cvpr26-0041_fig1, iclr26-0034_fig1, icml23-0002_fig1
- `hub`: acl26-0041_fig1, cvpr23-0038_fig1, cvpr25-0010_fig1, iclr24-0067_fig1, iclr26-0136_fig1
- `cards-grid`: aaai26-0009_fig1, acl25-0093_fig1, iclr23-0108_fig1, iclr25-0157_fig1, neurips24-0037_fig1
- `dashboard`: aaai26-0028_fig1, acl25-0103_fig1, cvpr25-0043_fig1, cvpr26-0003_fig1, neurips25-0203_fig1
- `pipeline-column`: iclr24-0119_fig1, icml24-0083_fig1, icml26-0016_fig1
- `inset`: iclr24-0087_fig1, icml26-0370_fig1, neurips25-0082_fig1
- `single`: icml26-0157_fig1, neurips23-0145_fig1, neurips24-0243_fig1
- `chat-column`: icml24-0023_fig1, neurips23-0046_fig1

## 10. In the spec

`meta.ai.arrangement` takes the values of §1; `panels[]` declares the units with `axis` from §2 (`alternatives`,
`stages`, `examples`, `narrative`, `overview`, `zoom`, `time`, `modalities`, `part`), `panel_label` for letters or
titles and `order`; `lanes[]` the aligned tracks; `meta.ai.grouping` the devices of §7 (`tinted-regions`,
`framed-boxes`, `dashed-boxes`, `whitespace`, `panel-frames`); `meta.direction` the reading direction and
`meta.step_markers` the marker style (`letters`, `plain-numbers`, `labelled-arrows`, `circled-numbers`, `none`);
`meta.column: double` for the full text width (the default of this family), `single` for one column of a two-column
venue (`spec-guide.md` §9). The validator reads these to count budgets and to repeat panel templates; it never
rejects an arrangement.
