# The drawing plan — say what the picture looks like before writing coordinates

The brief says what the figure *means*; the drawing plan says what it *looks like*. Write it after the spec
validates and before the first `<rect>`: a page of plain language that fixes the composition, so the SVG is
transcription rather than improvisation, and so the rendered PNG can be checked against a stated intent.
It lives next to the SVG as `plan.md`, goes to the user with v1 ("this is how I laid it out"), and is updated
whenever the layout changes. 120–300 words for a typical figure; longer only for two-panel or matrix figures.

## Sections

1. **Canvas** — column and size in pt (single 240 × 130–170; double 504 × 140–180), margins (≥ 4 pt),
   the grid you will snap to (e.g. 4 pt), the font key and base size (7 pt labels, 7.5–8 pt group titles,
   6 pt small print).
2. **Regions** — divide the canvas into named regions with approximate extents ("left 55 %: Host container;
   right 40 %: Backend; bottom strip 12 pt: legend"). One sentence per container / lane: stroke style, fill,
   where its title sits (top-left inside is the default), padding (≥ 6 pt around children).
3. **Placement** — for every node: region, row/column position, size (from `measure_text.py`: label width +
   8 pt, 1.4 × font size per line + 6 pt), shape idiom if not a rectangle (cylinder, stacked ×N, icon +
   label, picture + caption). State the alignment groups explicitly ("Client, Parser, Store share a baseline at
   y = 44; equal gaps of 10 pt"). For a bitmap, its box in pt at the picture's aspect ratio (or the crop), the
   pixel size that gives (≥ 150 ppi, 300 for photos), the frame, and where the caption sits.
4. **Routes** — the main path first: which sides it leaves and enters, orthogonal or straight, where the
   circled step numbers sit (upper-left of the arrow's midpoint, never on the line). Then secondary edges:
   dashed / dotted, colour role, how they avoid crossing boxes and text. Say which crossings, if any, are
   unavoidable and how they are disambiguated (a small gap or a hop).
5. **Emphasis** — exactly which element carries the accent (fill, border or thicker path) and what
   everything else does to stay quiet (grey / pastel fills, thin strokes). The figure's one point from the
   brief should be visible in this sentence.
6. **Legend, labels, annotations** — legend position and items, sublabels (§ references, "×N"), free
   annotations and their leaders.
7. **Check list for the PNG** — 4–6 concrete things to verify after rendering, derived from the above
   ("the accent box is the darkest thing on the page", "no arrow passes behind a label", "the three tier
   bands are equal height", "every label ≥ 6 pt when the page is at 100 %").

## Rules of thumb (corpus numbers)

- Boxes: 0.5–0.75 pt strokes, 1–2 pt corner radius, label padding ≥ 4 pt horizontal / 3 pt vertical.
- Gaps: equal gaps within a row (8–12 pt); containers pad their children by 6–10 pt; title band ≈ 1.6 × title size.
- Arrows: 0.7 pt lines, head length ≈ 4–5 × line width, main path 1.2–1.5 pt; leave 0.5 pt between a head and the box it enters.
- Steps: circled numbers ⌀ 8–12 pt at the arrow midpoints, in reading order, matching the caption.
- Text: one sans family, three sizes at most; nothing below 6 pt except badge digits.
- Bitmaps (print practice, not a corpus number): a local PNG / JPEG, box at its aspect ratio, ≥ 150 ppi at print
  size; a photo or screenshot gets a thin frame in the box stroke weight and its label as a caption clear of it.
- Whatever the plan cannot make fit at these numbers is a content problem — go back to the brief and merge or split, do not shrink type.

## Example (minimal figure)

> **Canvas.** Single column, 240 × 100 pt, 4 pt grid, Arimo 7 pt labels / 7.5 pt bold group title / 6 pt note.
> **Regions.** Host container x 8–168, y 14–74 (solid grey 0.8 pt, title top-left); Backend stands alone at x 186–226.
> **Placement.** One row at y 34–54: Client (40 wide), Span Parser (46, accent), Pattern Library (40, two-line label); Backend (40) outside. Gaps 10 pt inside the host; 24 pt to Backend marks the boundary.
> **Routes.** Straight left→right arrows at y 44 with filled heads; ① on e:1 at (61,37). Store→Backend dashed red with red head, label "sync" 6 pt above the line.
> **Emphasis.** Only Span Parser is orange with white bold text; everything else pastel/grey.
> **Legend.** None; a 6 pt note at the bottom explains grey/orange/dashed.
> **Check.** Orange box is the darkest fill; no text touches a line; four boxes share top and bottom edges; note stays ≥ 4 pt from the bottom.

## Mechanism figures — three more paragraphs

The seven sections above still apply (canvas, regions, placement, routes, emphasis, legend, check list). A
mechanism figure adds three paragraphs between **Regions** and **Placement**, because its composition is
decided by what repeats, what differs and how the reader moves — not by containers and tiers. Corpus shares
are from the 152 mechanism records (`references/mechanism/layouts.md`); they say what is common, not what is
required.

- **Repetition** — what the template is (the structure drawn once and repeated), how many panels or frames
  (45 % of figures have one drawing; panels median 3, rarely more than 4), their arrangement (row 25 %,
  grid 9 %, column 9 %, frames 7 %, inset 6 %) and whether positions are identical across panels
  (`identical` 21 %, `aligned` 47 %, `free` 32 %). State the panel size and gap once and the panel labels
  ((a)/(b), a name, or a caption line under each) and where they sit.
- **Difference** — exactly what changes from panel to panel or frame to frame, and the one marking style the
  figure uses for it: colour on the changed element (53 %), a callout (11 %), a badge (7 %), a dashed ghost of
  the old state, a strike — or nothing, when the difference is a label or a count the reader can see (26 %).
  Everything unchanged stays quiet: same grey, same weight, same place. If states are coloured, list the
  states and their colours here (`references/palettes.md` "Mechanism figures") and whether a legend is
  needed (70 % of figures manage without one; more than two coloured states usually needs one).
- **Reading path** — where the eye starts and how it moves: step markers (circled numbers 20 %, plain digits
  7 %, letters 7 %; on the arrow's upper-left, never on the line), the arrows themselves, panel order, a
  timeline's axis; and how the caption walks it (each marker gets a clause). For a worked example, which
  cells hold the input, intermediate and result values and how a value that recurs is linked (one colour per
  value is the corpus default; position or leaders otherwise).

Then **Placement** and **Routes** as above, per panel when the layout repeats (write the template once and say
"same in every panel"); **Emphasis** names the *difference* as the loudest thing; the **check list** gets the
mechanism items: panels the same size with elements at the same positions, the changed element visibly
different at 100 %, every branch of a decision labelled, markers in reading order and matching the caption,
values readable and results distinguishable from inputs, nothing below 6 pt in a repeated frame.

**When the figure fits none of this** — no panels, no steps, an arrangement of your own — write the three
paragraphs anyway in your own words (what repeats: "nothing"; what differs: "the highlighted subset"; reading
path: "from the query box to the three highlighted rows"). The plan is the place where a deviation from the
common shapes is stated, so the reviewer reads it as a choice.

### Example (mechanism, from `asplos25-006_fig1`)

> **Canvas.** Single column, 240 × 118 pt, 4 pt grid, 7 pt labels / 6.5 pt bar labels.
> **Regions.** Two panels stacked, each 240 × 52 pt, 8 pt apart; panel tag (a)/(b) top-left inside, 7.5 pt bold.
> **Repetition.** Template = Device 0 / Device 1 dashed boxes with the chain fwd → bwd → update; drawn identically in both panels (same x for every stage, same y within its panel).
> **Difference.** Panel (b) adds an AllGather bar before fwd and before bwd and replaces the AllReduce label with ReduceScatter; the added bars are the only saturated fill (blue); collective names in red italic in both panels so the rename is comparable.
> **Reading path.** Left to right along the chain in (a), then the same in (b); no step numbers — the caption names the phases.
> **Placement / Routes.** … (as above, once, "same in (b)").
> **Emphasis.** The blue bars in (b) are the darkest thing; everything else pastel and grey.
> **Check.** Both panels the same height with stages at the same x; blue bars visibly distinct at 100 %; the two red labels differ in text only; no label below 6.5 pt; panel tags do not collide with the device boxes.

## AI-venue figures — what the plan adds

The seven sections stay; for `meta.family: ai` they carry four more things (`references/ai/layouts.md`, `kinds.md`,
`anti-patterns.md` §6):

1. **Canvas** — the venue's text width (NeurIPS / ICLR 396, ICML 486, CVPR 495, ACL 454, AAAI 504 pt; one column,
   219-239 pt, only in the two-column venues), height from the content (good figures: median 198 pt, p95 317), the
   font the paper uses (sans in half the corpus, serif in a third).
2. **Samples and pictures** — for every `image`, `text`, `bubble` and `chart` node: the file or the exact text, the
   box in pt at the picture's aspect ratio (≥ 150 ppi at print size, 300 for photos), the frame (one frame style for
   all pictures of the figure), where the caption or label sits, and which lines of a text are quoted (two or three;
   the rest elided). Pictures cover a tenth of the canvas on median, a quarter in scope overviews and mosaics.
3. **Idioms and icons** — which parts of the library are copied for the stock forms (`assets/symbols/`, `subtype: ai`,
   the family of each `idiom`), recoloured by role; icons at label size (8-12 pt), one style across the figure, next
   to what they name; grey slots where the paper's logo or mascot goes.
4. **Emphasis and colour meaning** — the one strong colour (or frame, size, written claim) that carries the point, and
   what each colour means (per part, per actor, verdict, trainable against frozen, modality) with the key or the
   direct labels that say so; large fields pale (lightness ≈ 0.9), strong colour on small things only.

The check list for the PNG adds: every sample readable and framed alike; no text block longer than three lines; the
strong colour on the point and nowhere else; the panels lettered in reading order; the figure filling the text width.

### Example (the ICML agent figure of the brief template)

> **Canvas.** ICML, full width 486 × 170 pt, 4 pt grid; Arimo 7 pt labels / 7.5 pt bold band titles / 6 pt notes.
> **Regions.** Three bands x 8–478: Plan y 12–60 (`#fbe3d6`), Act y 66–122 (`#e2f0d9`), Verify y 128–166 (`#deebf7`);
> band titles top-left; a key at the right end of the Verify band.
> **Samples.** Task card 110 × 26 pt in Plan, two quoted lines at 6.5 pt in a white card with a 0.5 pt grey frame;
> browser screenshot 96 × 54 pt in Act (640 px wide file → 480 ppi), same frame; answer bubble 110 × 30 pt in Verify
> with a 6 pt tail to the Verifier.
> **Idioms.** `llm` box (library `llm-box-...`) for Planner and Verifier, recoloured to the band tint with a grey
> outline; `typed-trace-blocks` part for the three calls (blue message, orange command, green output rows), snowflake
> glyph from `frozen-trainable` on the Verifier.
> **Routes.** Left to right inside each band, a 0.7 pt grey arrow between bands at the band's left third; the
> observation back-arrow dashed; the retry loop a curved 0.7 pt arc from Verifier to Planner along the left margin,
> labelled 6 pt.
> **Emphasis.** The trace block is the one orange fill (`#ed7d31`); everything else pale on tints. Key: snowflake =
> frozen; nothing else needs decoding.
> **Check.** Trace is the darkest thing; both text samples ≥ 6.5 pt; the three pictures share one frame; step digits
> 1-3 in reading order; nothing outside 486 × 170.
