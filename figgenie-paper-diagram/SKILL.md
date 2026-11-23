---
name: figgenie-paper-diagram
description: >
  Draw publication-quality paper figures as SVG the way top venues draw them. Systems papers (OSDI, NSDI, SOSP,
  ASPLOS): architecture / overview figures distilled from 727 human-rated figures, and **mechanism figures** — how
  one part of a system works: a walkthrough with numbered steps, before/after or step-by-step frames, a state machine
  or decision flow, alternatives side by side, the anatomy of one component or data structure, a worked example with
  real values ("架构图", "系统总览图", "画一张 overview 图", "论文插图", "机制图", "原理图", "示意图", "画一张 X 是怎么工作的图",
  "状态机 / 流程图", "before/after 对比图", "算例图") — distilled from 986 rated mechanism figures. AI papers (ICLR, ICML,
  NeurIPS, CVPR, ACL, AAAI): the Figure 1 / teaser / overview figure — a stage pipeline, a model's anatomy, a
  side-by-side contrast, a worked walkthrough on real samples, a concept schematic, a benchmark or dataset overview,
  an agent interaction, a contribution mosaic ("AI 顶会图", "Figure 1", "teaser 图", "方法总览图", "模型结构图", "框架图",
  "benchmark 总览"), distilled from 3,274 labelled Figure 1s, 1,158 user ratings, 336 semantic records, 3,210 exemplars
  and a 998-part library. Workflow: intake → a natural-language brief the user confirms → figure spec → exemplars the
  user picks (AI family) → drawing plan → hand-drawn SVG that follows corpus layouts, palettes, visual encodings and a
  parts library → render / lint / look-and-fix loop → SVG + caption draft, then iterate on feedback. Use whenever the
  user wants such a figure for a paper or talk, asks how one should be laid out, coloured or annotated, wants an
  existing figure critiqued against the venue's conventions ("把这张图重画/改风格"), or asks for a named paper style
  ("Charon 风格"). Vector TeX formulas when the figure needs the paper's symbols; an editable PowerPoint deck on
  request ("转成可编辑的 PPT"). Not for data plots or charts.
metadata:
  origin: Sleepy-Avacado/FigGenie-paper-diagram-skill
---

# figgenie-paper-diagram (FigGenie-Skill) — architecture, mechanism and AI-venue figures the way top papers draw them

You draw the SVG yourself. The scripts do not lay out for you; they measure text, render, lint and show you the
result so you can fix it. Everything is in **pt at print size**: a single-column figure is ≈ 240 pt wide, a
double-column one ≈ 504 pt (an AI-venue figure spans its venue's text width, 396–504 pt), labels 6.5–7 pt, strokes
≈ 0.5–0.6 pt. Read the corpus numbers, then draw like the exemplars, not like a slide.

**Reference, not recipe.** The corpus numbers, the templates, the exemplars and the parts library exist to strengthen
a layout you derive from the figure's own content — what it must make the reader see — never to replace that
derivation. When the material asks for something the references do not cover, draw it, and say so in the plan.

**Two families, two kinds.** `meta.family` says which corpus the figure follows: **systems** (the default: OSDI, NSDI,
SOSP, ASPLOS) or **ai** (ICLR, ICML, NeurIPS, CVPR, ACL, AAAI; `references/ai/`). `meta.kind` says what it shows:
**architecture** (the whole system; 20 layout templates in the systems family) or **mechanism** (how one part works).
Decide both in the brief. The steps below are written for a systems architecture figure; what a mechanism figure and
what an AI-venue figure do differently each get one section after the workflow — menus with frequencies, not rulebooks.

## Workflow (gates in bold)

Work in a folder per figure: `brief.md`, `spec.json`, `plan.md`, `fig.svg`, and the outputs of `check.py`.

1. **Intake → brief.** Read what the user gave (paper sections, notes, an old figure, chat). Write the brief
   (`references/brief-template.md`): what the figure is, every component with new / existing / external tags and its
   container, the numbered main path and secondary flows, the one point the figure argues, layout and style intent
   with the closest exemplar ids (step 3), 3–5 assumptions to confirm with their source, a caption draft. Infer first;
   ask only what changes the structure and cannot be read from the material (usually "which parts are new" and "which
   path is the main one"), at most three points in one message, each phrased as your guess plus the alternative
   (`references/spec-guide.md` §1). **Gate: the user confirms the brief.**
2. **Spec.** Derive `spec.json` from the confirmed brief (`references/spec-guide.md` §2–3, schema
   `references/spec-schema.json`). The specs in `assets/specs/examples/` show how a filled-in spec is written and
   nothing else: take layout, colour and density from the exemplar library in step 3, never from them. Run
   `python3 scripts/spec_validate.py spec.json` and fix errors; read the warnings as advice. The spec is a contract for
   the linter, not a cage: `notes` and `x-*` fields are allowed everywhere, kinds have `other`, templates have `custom`.
3. **Template, exemplars, palette, encoding.** Pick the template with the decision table in `references/layouts.md`
   ("Choosing a template", then the one template section you need; 20 ids: 7 core + 13 added). Then look at exemplars
   along two lines, because the template says how the corpus arranges a figure and the content says how this field
   draws its objects: **by template**, two or three from `assets/exemplars/<template>/index.json` (starred = must-see,
   each with a one-line lesson); **by domain, content and meaning**, `python3 scripts/find_exemplars.py --domain "<field,
   kind of system>" --content "<what is drawn>" --semantics "<the point the figure argues>"` ranks all 485 exemplars of
   both kinds — open the top three to five whose systems resemble yours, whatever their template; this is where a
   field's habits come from. Usually five to eight figures in all; when the matches are only generic words, say so in
   the plan and lean on the template exemplars. LOOK at each `assets/exemplars/figures/<id>/print.png` (or
   `preview.png`) and skim `semantics.json`; imitate their arrangement, density and restraint, and borrow the devices
   that make your content visible. Choose a palette from `references/palettes.json` (one accent, grey for existing
   parts, white canvas). The 20 templates are the arrangements the corpus uses most, not moulds: `custom` with a
   `notes` line is the right answer when the structure is something else. Take the default encodings from
   `references/encoding.md` Part D (solid = data, dashed = one meaning per figure, thick = main path, circled numbers =
   the walkthrough, `×N` for repetition, red only for errors / bottlenecks).
   **Named style** — only when the user asks for one paper's look (today: `charon`, `references/styles/README.md`):
   set `meta.style`, `meta.palette` and `meta.font` as its card says, read the card (`references/styles/<id>.md`)
   before the plan, and add two or three of its figures to the exemplars (`find_exemplars.py --style <id> …`). The
   style replaces weight, outlines, fill roles and framing; the template, the content search and every print floor
   (type ≥ 6 pt included) stay as above.
4. **Drawing plan.** Write `plan.md` (`references/drawing-plan.md`): canvas and grid, regions, per-node placement and
   size, routes, emphasis, legend, and a 4–6 item check list for the PNG. Size boxes from measured labels:
   `python3 scripts/measure_text.py --font <key> --size 7 "Label" …` (CJK runs with the companion `--cjk` key; `--box`
   prints the box size; width + 8 pt, 1.4 × size per line + 6 pt). Place labels with `python3 scripts/place_text.py
   --font <key> --size 6.5 center --box x,y,w,h [--rotate -90] "Label"` (baseline from the font, the linter's own
   centring model; `line` for text with an inline ① disc). If the plan does not fit at these numbers, the content is
   too much — go back to the brief and merge or split; never shrink type below 6 pt. Formulas, only when the figure
   carries the paper's symbols: `python3 scripts/tex_measure.py --size 6.5 --box '<tex>'` (`--mixed '… $tex$ …' --emit`
   lays out a label with inline formulas); see `references/formulas.md`.
5. **Draw the SVG** under the contract (`references/spec-guide.md` §4): `viewBox="0 0 W H"` in pt, the font stack from
   `assets/fonts/fonts.json` on the root, one `<g id="n:<id>" data-kind="node">` per node (shape + `<text>`), `e:` for
   edges (with `data-from`/`data-to`, `marker-end`), `c:` containers, `l:` lanes, `s:` step badges, `a:` annotations,
   `legend`. Text stays `<text>`; a formula is the one exception — a `<g data-symbol="tex" data-tex="…" data-x data-y
   data-size data-anchor/>` placeholder that `tex_fill.py` renders to paths; no gradients, filters or external refs.
   Mark a group drawn to scale from numbers `data-scale="data"` and a label set beside its box on purpose
   `data-label="outside"` (spec-guide §4). A bitmap — a sample input or output, a photo, a screenshot, a rendered
   result, an icon — is an `<image>` in its node's group: a PNG / JPEG in the figure folder linked by a relative path,
   never a URL (spec-guide §4 "Bitmaps"). Reuse parts from `assets/symbols/` (`index.json`, `catalog-*.png`) by copying
   the inner `<g>` and recolouring by role — the library is a reference, not a limit. Default strokes, arrowheads,
   containers, badges and legends: `references/parts-styles.md` §8.
6. **Self-check loop.** If the figure has formula placeholders, first `python3 scripts/tex_fill.py fig.svg --check`.
   Then `python3 scripts/check.py fig.svg --spec spec.json` → validates, lints, renders `fig.png` and `fig.lint.png`,
   writes `fig.preview.html`. Then LOOK at `fig.png` with your image-viewing tool (Read in Claude Code, view_image in
   Codex) and go through `plan.md`'s check list and `references/anti-patterns.md` §3: overlaps, crossings, bleed,
   alignment, the accent being the loudest thing, labels readable at 100 %, arrows that mean what the brief says,
   arrowheads and tails clear of dividers, ×N stacks stepped evenly, container titles centred in their headroom,
   rotated gutter labels centred (the linter checks these too). Fix the SVG (or the spec / plan if the layout was
   wrong) and re-run until the lint has 0 errors and every remaining warning is deliberate. `scripts/render.py --scale 6
   --crop x0,y0,x1,y1` zooms into a region, `scripts/svg_edit.py shift … --with-edges` moves a group with its edges,
   `fig.preview.html` gives exact coordinates.
7. **Deliver.** `python3 scripts/embed_fonts.py fig.svg -o fig.final.svg` (fonts embedded and subsetted, CJK companion
   included, every bitmap inlined as a data URI, so the file stands alone — it refuses while an image is a URL, missing,
   or not PNG / JPEG) and `python3 scripts/export_pdf.py fig.final.svg` for LaTeX / Pages. Hand over: the final SVG, the
   PDF, the PNG preview, the caption draft, the assumption list from the brief, and one line on how to edit (element ids
   match the spec). **Gate: the user reviews.**
8. **Iterate.** Content feedback → brief → spec → redraw; layout / style feedback → spec (`spec-guide.md` §5) → redraw;
   always re-run `check.py` and look again. Keep brief, spec, plan and SVG in sync.

## Mechanism figures (kind 2): what changes, step by step

The 152 good mechanism figures of the corpus fall into five groups, but almost no two share a layout, so this section
is deliberately loose: **the groups, arrangements, default encodings and numbers are what good figures did, with how
often — a starting point, not a template to fill.** When the story needs something else, do it, and write the reason
in the plan and in the spec's `notes`. Only print physics is fixed. A good mechanism figure that looks like none of
the 146 exemplars is the expected outcome.

- **Deciding the kind (step 1).** Whole-system overview → architecture. What happens inside one component, one data
  structure, one exchange, one decision, or how alternatives differ → mechanism. Both → the one the caption leads with;
  the other becomes an inset or a second figure (`references/spec-guide.md` §7). One overview figure that holds unlike
  drawings (a structure, numbers to scale, a timeline, a loop) → a composite: its panels are parts (`axis: part`), each
  budgeted on its own (spec-guide §8).
- **Brief (step 1).** Same seven sections, three read differently (`references/brief-template.md`, "Mechanism
  figures"): §2 the structure(s) drawn, what repeats and what differs; §3 the story the reader follows (steps,
  transitions with guards, before → after deltas, the values of a worked example); §4 what the reader must *see* in
  five seconds. Answer "which group?" last; "none exactly" is acceptable if the reading path is clear.
- **Spec (step 2).** `meta.kind: mechanism`, `meta.template: mechanism`, `meta.mechanism` with the group (secondary
  `groups` allowed), `base`, `arrangement` (`other` is a value), plus the blocks the story needs: `panels[]` +
  `deltas[]` for alternatives and frames, `steps[]` for a walkthrough, `state` / `decision` nodes with guarded
  `transition` edges for logic, `values[]` for a worked example (spec-guide §7). The validator only *warns* here.
- **Group, base, arrangement, exemplars, encoding (step 3).** `references/mechanism/layouts.md` "Choosing the group,
  the base, the arrangement" (five questions, then one group section: drawing plan, numbers, variants with figure ids,
  pitfalls, "Inventing an arrangement"). Open two or three starred exemplars of the group
  (`assets/exemplars/mechanism/<group>/index.json`) and three to five found by domain, content and meaning
  (`scripts/find_exemplars.py ... --kind mechanism --group <group>`); LOOK at each `print.png`. Encoding defaults:
  `references/mechanism/encoding.md` Part E. Palette: the same 21 (`palettes.md` "Mechanism figures"); most mechanism
  figures draw on a bare canvas, and colour says *state* rather than *component kind*.
- **Plan, draw, check (steps 4–6).** Three extra plan paragraphs (`references/drawing-plan.md` "Mechanism figures":
  what repeats, what differs and how it is marked, the reading path); budgets `references/mechanism/style-rules.md`
  §12 (label-distinct). Contract additions (spec-guide §7): `p:<id>` groups per panel, `@<panel>` id suffix for
  repeated template elements, `data-delta` on the changed element, `v:<id>` for values. Parts: the 2,261 mechanism
  parts by theme (`catalog-mech-<theme>.png`; `references/parts-styles.md` §9). Then `check.py` and the self-check of
  `references/mechanism/anti-patterns.md` §6. Mechanism lint rules are advisory.

## AI-venue figures (family 2): what changes, step by step

The Figure 1 of an ICLR, ICML, NeurIPS, CVPR, ACL or AAAI paper spans the venue's full text width, carries the
paper's material (samples, prompts and answers, pictures, icons, real numbers — half the corpus shows samples), often
belongs to two or three kinds at once, and takes its habits from its field. `references/ai/` says what that corpus
does with how often; nothing in it is a rule except print physics, and **a figure that looks like none of the 3,210
exemplars is a normal outcome.** The paper's own content and material come before anything an exemplar suggests.

- **Deciding the family and the kinds (step 1).** An AI-venue paper → `meta.family: ai` with its `venue`. Then the
  kinds the figure is, primary first (`references/ai/kinds.md`: stage pipeline, model anatomy, side-by-side contrast,
  worked walkthrough, concept schematic, scope overview, actor interaction, contribution mosaic; 58% carry two), and the
  paper's sub-field (`references/ai/domains.md`, read next to the general pages as the second view, not a filter).
- **Brief (step 1).** `references/brief-template.md` "AI-venue figures": §1 adds the venue, the kinds and the field;
  §2 lists every sample, picture, icon, worked value, chart and logo the figure will show and which of them the user
  must supply (`meta.ai.materials`) — ask for the paper's own material, never invent it; §5 names the arrangement, the
  exemplar candidates and what colour will mean.
- **Spec (step 2).** `meta.family: ai`, `meta.venue`, `meta.column: double` (the text width; `single` only for one
  column of a two-column venue), `meta.template: ai`, `meta.ai` (kinds, variant, subfield, arrangement, grouping,
  samples, idioms, materials); content as `text`, `bubble`, `chart` and `image` nodes (with `image.role`), `idiom` and
  `train_state` on nodes, panel axes `stages` / `examples` / `narrative` / `overview` / `zoom`, edge kinds `gradient` /
  `attention` / `interaction` — `references/spec-guide.md` §9. The validator reads these for the venue's width band and
  the kind's budget; every AI-specific finding is advice.
- **Exemplars the user picks (step 3, required).** `python3 scripts/find_ai_exemplars.py search --kind … --subfield …
  --tags … --objects … --text …` with the words of the brief ranks the 3,210 cards (336 with a deep record, 638 rated
  good, the rest); choose 9–12 by meaning (mostly tier 1, at least one from another field, different solutions), `sheet`
  them into a numbered picture, show it, and **ask the user to pick two to four** ("you choose" and "more like 5" are
  answers too); then `files`, LOOK at each `print.webp`, read its `source.svg` and the tier-1 lessons
  (`references/ai/exemplar-retrieval.md`). The picks are a strong preference about look and feel: say so in the plan.
  **Gate: the user picks.** For a whole-model figure, `references/ai/model-architectures.md` names 16 model types' drawings.
- **Arrangement, palette, encoding (step 3).** No template: `references/ai/layouts.md` §1 (panels in a row or grid,
  bands, lanes, a pipeline row, a card grid, a hub …), §2 panels and their axes, §8 when nothing fits. Palette: the
  five AI families or any other (`references/ai/palettes.md` §9; office-pastel is the family's default look; three to
  five hue families and pale region tints are normal here, loud fills are not). What colour, line, shape and markers
  say: `references/ai/encoding.md` Part G. The field's section of `domains.md` and the family page are read together.
- **Plan (step 4).** `references/drawing-plan.md` "AI-venue figures": the venue width, a box for every sample and
  picture (≥ 150 ppi, one frame style), which lines of a text are quoted, the parts copied for the idioms, icons at
  label size in one style, the one strong colour and what each colour means. Budgets per kind
  (`references/ai/style-thresholds.json` `by_kind`; `kinds.md` "Numbers by kind").
- **Draw (step 5).** The shared contract. Parts: the 998 AI parts by theme (`assets/symbols/catalog-ai-<theme>.png`;
  `index.json` `subtype: ai`, `by_family_ai`, `domain`) — LLM boxes, Transformer blocks, token strips, diffusion chains,
  agent loops, bubbles, benchmark cards, film strips, verdict marks, zoom call-outs; `references/parts-styles.md` §10.
  A bitmap the part replaced with a grey slot is the paper's to supply.
- **Check (step 6).** `check.py` as usual; the linter adds `ai.bare`, `ai.loud-ink` and `ai.hues-no-key` and raises the
  fill ceilings for this family; then the ten questions of `references/ai/anti-patterns.md` §6 (is the point the
  loudest thing, is every code keyed, is every relation drawn, is a sample there where the kind has one, is any text
  block longer than three lines, are the large fields pale). All advisory.

## Optional add-on after delivery: an editable PowerPoint copy

Only when the user asks for a deck, or an editable / Word-native version of the figure. `python3 scripts/svg2pptx.py
fig.final.svg --spec spec.json` writes `fig.final.pptx` (one native shape per primitive, one named group per spec element,
native equations, bitmaps as pictures); `python3 scripts/pptx_check.py fig.final.pptx --svg fig.final.svg` confirms nothing
was dropped or covered. Font mapping and limits: `references/pptx-export.md`; it never overwrites a deck without `--force`.

## Reading map (load only what the step needs)

| when | read | lines |
|---|---|---|
| writing the brief / asking | `references/brief-template.md`; `references/spec-guide.md` §1–2 | 70 / 100 |
| writing the spec | `references/spec-guide.md` §3–6; `references/spec-schema.json` on demand; `assets/specs/examples/*.json` for spec syntax only | 120 |
| choosing the template (systems) | `references/layouts.md` "Choosing a template" + "Cross-template conventions", then one template section | ~120 |
| colours | `references/palettes.md` (roles, 11 hue + 10 ground families, what not to do) and the entry in `palettes.json` | 161 |
| a composite figure, what to cut when it does not fit; placing a label exactly, data to scale, a label beside its box | `references/spec-guide.md` §8; `scripts/place_text.py` + spec-guide §4 "Placing labels, drawing to scale" | 45 / 15 |
| a named style the user asked for (`meta.style`) | `references/styles/README.md`, the card `references/styles/<id>.md`; `assets/exemplars/styles/<id>/` | 40 + 150 |
| deciding the kind; a mechanism brief / spec | `references/spec-guide.md` §7; `references/brief-template.md` "Mechanism figures" | 50 + 40 |
| mechanism: group, base, arrangement; encoding; numbers; before done | `references/mechanism/layouts.md` ("How to read this", "Choosing …", one group section); `mechanism/encoding.md` Part E first; `mechanism/style-rules.md` §12 + `drawing-plan.md` "Mechanism figures"; `mechanism/anti-patterns.md` §6, §3 | 230 / 60–200 / 80 / 40–300 |
| AI family: deciding kinds and field | `references/ai/kinds.md` ("Choosing", "At a glance", the kind's section); `references/ai/domains.md` (the field's section) | 60 + 40 / 30 |
| AI family: brief and spec | `references/brief-template.md` "AI-venue figures"; `references/spec-guide.md` §9 | 60 / 80 |
| AI family: exemplars the user picks | `references/ai/exemplar-retrieval.md`; `scripts/find_ai_exemplars.py` (`vocab`, `search`, `sheet`, `files`, `card`); whole-model figures `references/ai/model-architectures.md` | 80 / 60 |
| AI family: arrangement, colour, encoding | `references/ai/layouts.md` §1–3, §8; `references/ai/palettes.md` §9, §10; `references/ai/encoding.md` Part G, then the part the figure needs | 120 / 60 / 60 |
| AI family: numbers while drawing; before done | `references/ai/style-rules.md` "Quick checklist" + §10 sizes by venue; `references/drawing-plan.md` "AI-venue figures"; `references/ai/anti-patterns.md` §6, §2 | 60 / 40 / 60 |
| systems: what dashed / bold / ①② mean; numbers while drawing; before done | `references/encoding.md` Part D (default table), Part B for emphasis; `references/style-rules.md` "Quick checklist" + "Figure size table", `references/parts-styles.md` §8; `references/anti-patterns.md` §3, §1–2 | 50–100 / 100 / 40–400 |
| formulas in the figure; a bitmap in the figure | `references/formulas.md` + `scripts/tex_measure.py`, `tex_fill.py`; `references/spec-guide.md` §4 "Bitmaps", `encoding.md` A13, AI family `references/ai/style-rules.md` §6 | 90 / 30 |
| an editable PowerPoint copy (optional) | `references/pptx-export.md`; `scripts/svg2pptx.py`, `scripts/pptx_check.py` | 80 |
| parts | `assets/symbols/README.md`, `index.json` (name / tags / depicts; `family`, `theme`, `figure_kinds`, `domain`; filter `subtype` architecture / mechanism / ai); catalogs `catalog-icon|motif|shape.png`, `catalog-mech-<theme>.png`, `catalog-ai-<theme>.png`; `references/parts-styles.md` §8–10 | — |
| exemplars | systems: `assets/exemplars/<template>/index.json`, `assets/exemplars/mechanism/<group>/index.json`, `scripts/find_exemplars.py`, per figure `assets/exemplars/figures/<id>/` (`print.png`, `source.svg`, `semantics.json`); AI: `assets/exemplars/ai/` (`cards.jsonl`, `figures/<id>/print.webp` + `source.svg` + `semantics.json`, `README.md`). Reference and reinforcement only | — |

## Rules that are not negotiable

- Units and canvas: pt, `viewBox="0 0 W H"`, W in the column band (systems: single 210–309, target 240; double
  430–603, target 504; AI family: the venue's text width — NeurIPS / ICLR 396, ICML 486, CVPR 495, ACL 454, AAAI 504 —
  or one column of a two-column venue, 219–239); height ≈ 130–180 pt (AI family 130–320); nothing outside the canvas.
- Type: one sans family (key from `fonts.json`, default `helvetica` = TeX Gyre Heros; `arial`, `calibri`, `times`,
  `computer-modern` when matching a paper), ≤ 3 sizes, labels 6.5–7 pt, nothing below 6 pt except badge digits. Labels
  are the paper's own terms. CJK labels: Latin family first, the CJK companion second (`meta.font_cjk`, default
  `source-han-sans`); never a glyph that no embedded face has (`font.glyph` in the lint catches it).
- Colour: white canvas; ≤ 2 saturated fills, exactly one accent role; grey / pale fills for existing parts; red only
  for errors, bottlenecks or the highlighted path; text contrast readable (white text on dark accents).
- Lines: every directed edge has a head; dashed carries one meaning per figure; the main path is the heaviest line;
  orthogonal routes for structure, curves only for feedback; no line through a label.
- Structure: ≤ 3 nesting levels; containers never filled darker than their children; equal gaps in a row; edges of
  boxes snapped (the linter flags 0.3–2 pt misalignment); a legend when more than four fills, line styles or icons carry
  meaning; `×N` or an ellipsis instead of drawing N copies.
- Content: nothing the brief does not contain; every spec element appears in the SVG with its id; new components
  visibly distinct from existing ones; the walkthrough numbers match the caption.
- Bitmaps (a sample, a photo, a screenshot, a rendered result, an icon): PNG or JPEG from a local file, never a URL;
  inlined into the SVG at delivery like the fonts; ≥ 150 ppi at print size (300 for photos), at its own aspect ratio.
- Never: gradients, 3D, drop shadows, rainbow categorical fills, a different shape per box, text converted to paths
  (formulas rendered by `tex_fill.py` inside `<g data-symbol="tex">` are the exception), decisions taken silently (they
  go to the brief's assumptions / `meta.open_questions`).
- Mechanism figures: the print rules hold as written; colour and structure bend where the story needs it — state
  colours may add a third and fourth hue (with a legend), the same structure is drawn once per panel, the accent is the
  *difference*, nesting follows the drawn base. Say in the plan which rule you bent and why.
- AI-venue figures: the print rules hold as written (type ≥ 6 pt above all: good AI figures run smaller and the records
  call it their first fault). Colour and structure follow that corpus instead: three to five hue families, pale region
  tints, up to four saturated fills with a key, letters on panels, samples and icons as content; the loud fill, the
  bare skeleton, the wall of text and clip-art as the content are its faults (`references/ai/anti-patterns.md`).

## Numbers to keep in your head

Systems architecture (727 good figures): median 11 components and 6 flows; 6 distinct fills, 1 saturated; label
6.5 pt; stroke 0.56 pt with 2 widths; 73 % have no legend (matrix 42 %, host-device 38 %, control-data 36 % do); 35 %
number their steps; pipeline is left-right 66 % of the time, layered top-down 79 %; double-column figures are twice as
wide but not taller (aspect ≈ 3.1).

Mechanism (152 semantic records): median 10 elements and 6 relations; 45 % one drawing, 25 % a row of panels (median
3); 82 % single column; 70 % no legend; 61 % no step markers (circled 20 %, plain digits 7 %, letters 7 %); a difference
marked by colour 53 %, callout 11 %, badge 7 %, not at all 26 %; 33 % worked examples; 55 % no container fill; 85 % of
logic transitions carry a guard.

AI-venue Figure 1s (3,274 labelled, 844 good measured, 336 records): 89 % span the text width; median 460 × 198 pt;
label 6 pt, stroke 0.47 pt; 9 fills and 4 hue families; 69 text runs and 14 labelled boxes (scope overviews 24, concept
schematics 4); 53 % hold pictures, 54 % icons, 25 % bubbles, 50 % formulas; panels in 84 % (three in 32 %), lettered in
22 %, circled step numbers in 4 %; a legend in 30 %; tinted regions as ground in 33 %; good figures are the fuller ones
— the weak ones are empty, loud, or a wall of text.

## Files

- `references/` — the distilled knowledge (every file says how it was derived); `references/mechanism/` the mechanism
  kind; `references/ai/` the AI family (`kinds`, `domains`, `layouts`, `encoding`, `palettes`, `style-rules`,
  `style-thresholds.json`, `anti-patterns`, `exemplar-retrieval`, `model-architectures`); `references/styles/` named styles.
- `assets/exemplars/` — systems: 485 published figures (339 architecture across the 20 templates, 146 mechanism across
  the 5 groups), each under `figures/<id>/` with a one-line lesson in its `index.json`; `styles/` the named styles'
  figures; `ai/` the AI family: 3,210 cards (`cards.jsonl`), 792 full packs (`figures/<id>/print.webp`, `source.svg`,
  `semantics.json` for the 336 deep records), thumbnails, `vocab.json`, `SOURCES.md`. Style reference only; provenance in
  every manifest.
- `assets/symbols/` — 3,851 parts, standalone SVGs in pt with `data-symbol`: 592 for systems architecture figures, 2,261
  for mechanism figures (`subtype: mechanism`, 155 families, 11 themes) and 998 for AI-venue figures (`subtype: ai`, 183
  families, 9 themes, each with the sub-field it came from); catalog PNGs per kind and theme.
- `assets/palettes/` — swatch cards for the 21 systems palettes, 1 named-style palette and 5 AI families;
  `assets/fonts/` — open fonts + `fonts.json`.
- `assets/specs/examples/` — specs reverse-engineered from corpus exemplars, kept only as examples of how a spec is
  written (`_source` points at the figure): systems `asplos25-100_fig5`, `asplos25-167_fig1`, `asplos26-132_fig6`,
  mechanism `asplos25-006_fig1`; AI `acl23-0028_fig1` (a stage pipeline with real sentences) and `acl25-0048_fig1` (an
  agent loop with a trace and icons).
- `scripts/` — `find_exemplars.py`, `find_ai_exemplars.py`, `spec_validate.py`, `measure_text.py`, `place_text.py`,
  `render.py`, `lint.py`, `embed_fonts.py`, `export_pdf.py`, `svg_edit.py`, `preview.py`, `check.py` (`scripts/README.md`);
  formulas `tex_measure.py`, `tex_fill.py`; PowerPoint `svg2pptx.py`, `pptx_check.py`; `scripts/distill/` re-derives the
  references from the corpora.

Requirements: python3 with lxml, Pillow, playwright (`playwright install chromium`); `fontTools` optional. Optional: `node`
≥ 18 for formulas (`scripts/mathjax`, `npm install` on first use); `python-pptx` + Office's `mathml2omml.xsl` for PowerPoint.
