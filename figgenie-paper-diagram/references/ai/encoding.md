# Encoding in AI-venue figures: what colour, line style, shape, markers and emphasis are used to say

Read from the 336 deep semantic records of the family (good figures chosen for coverage): the records' prose on what
each visual variable means was sorted by keyword rules, so every share is a floor ("how often the records say X"),
categories overlap, and a figure usually uses two or three colour codes at once. The pre-screen over all 3,274 figures
is quoted where it labelled the same thing. Each table names the kinds and fields where a device is most used: read
the family column and the kind or field column together. The default table at the end (Part G) is what to start from;
the figure's own content decides where to leave it.

## Part A — Colour

What colour means (share of records; one record can carry several):

| code | meaning | pool | high in |
|---|---|---:|---|
| `per-part` | three or more parts each get a colour of their own, named one by one | 75% | anatomy and contrast 85%, llm-nlp 86% |
| `identity` | one colour per item (class, task, token type, agent, module group), carried wherever it appears | 29% | scope 47%, multimodal 37% |
| `element-type` | colour tells kinds of element apart: inputs, operations, outputs, data, modules | 28% | anatomy 48%, audio 50% |
| `actor` | who speaks or acts: user, model, agent, attacker, expert | 21% | actors 61%, agents 64%, rl-robotics 41% |
| `verdict` | right against wrong, success against failure, safe against harmful | 19% | llm-nlp 29%, walkthrough 28%, contrast 27% |
| `highlight` | one strong colour picks out the key item: an evidence span, the changed part, an error | 15% | vision 29%, generative 24%, anatomy 21% |
| `ours-vs-prior` | the proposed parts against existing or baseline ones | 12% | mosaic 33%, generative 24%, contrast 21% |
| `region-identity` | a tint only names a region, panel, stage or card | 11% | mosaic 24%, scope 17% |
| `trainable-frozen` | what is trained against what stays frozen | 9% | mosaic 19%, audio 18%, rl-robotics 17% |
| `modality` | text against image, audio, video | 8% | audio 36%, anatomy 23%, multimodal 20% |
| `phase` | training against inference, one stage against the next | 6% | — |
| `scale` | a sequential or diverging scale (a heat map, darker = more) | 5% | — |

Codes per figure: none 5%, one 20%, two 31%, three 27%, four or more 17%. Three or more hue families in 72% of the
records' fill palettes (`palettes.md` §2); colour is the main carrier of meaning in this family, and "a code the figure
does not explain" is named in 41% of the records (`anti-patterns.md` §3).

**Which colour is given which meaning** (1,400 "colour = meaning" clauses): red means a verdict in 41 of its 77
clauses (wrong, failure, unsafe), then a highlight (9), ours (7), an actor (7); green a verdict in 28 of 60 (right,
success), then an actor (11); blue an actor (18), trainable or frozen (14), ours (11), a modality (11); grey the prior
or baseline (13), frozen (8); yellow and orange an actor (9, 10). Which side a colour takes: **right** is green (20 of
28 clauses) and **wrong** red (27 of 34); **ours** is red 9, pink 4, purple 4, blue 4, orange 4 and **prior** grey 15,
blue 9; **trained** and **frozen** split evenly between blue and grey (4 each side) — so a frozen / trainable code
always needs its key or its glyphs (Part D).

Outlines and arrows are coloured (not only grey or black) in 70% of the records; text is coloured in 41% — headings,
highlighted words, labels in the colour of their part — red 24% of the coloured text, blue 22%, green 17%, orange 16%
(`palettes.md` §6).

## Part B — Line style

| code | meaning | pool | high in |
|---|---|---:|---|
| `dashed-frame` | a dashed box or frame groups parts or marks a scope | 42% | concept 52%, contrast 50%, pipeline 49%, llm-nlp 51% |
| `colour-coded-arrows` | arrow colour says what kind of flow it is | 33% | vision 50%, generative 44%, pipeline 41% |
| `solid-main-flow` | solid arrows are the main data flow | 28% | pipeline 51%, anatomy 50%, audio 50% |
| `weight` | line weight separates main from minor | 21% | agents 39%, actors 29%, concept 28% |
| `curved` | curved or looping arrows mark feedback, iteration or long-range links | 17% | science 33%, generative 32%, actors 25% |
| `dashed-divider` | a dashed rule separates panels, stages or halves | 17% | generative 36%, contrast 27%, mosaic 26% |
| `zoom-lines` | thin or dashed lines tie a zoomed view to its source | 12% | pipeline and concept 20% |
| `block-arrows` | block or hollow arrows mark a hand-over between stages or panels | 12% | science 24%, pipeline 20%, mosaic 19% |
| `outline-colour` | outline colour or weight marks a state or a class of box | 10% | audio 18%, walkthrough 14% |
| `dashed-secondary-flow` | a dashed arrow is a secondary flow: optional, feedback, gradient, training-only | 9% | audio 23%, anatomy 19%, rl-robotics 14% |
| `double-headed` | double-headed arrows mark exchange, comparison or alignment | 6% | — |
| `gradient-or-loss` | a distinct arrow style for losses, gradients or supervision | 3% | — |

Measured on the SVGs (`style-rules.md` §3): a dashed stroke somewhere in 60% of good figures (40% of the weaker ones);
median stroke 0.47 pt; three widths. Dashed is spent on boxes and dividers far more than on arrows here; when a dashed
arrow is used it carries one meaning per figure (a gradient, an optional path), as in the systems family.

## Part C — Shape

| code | meaning | pool | high in |
|---|---|---:|---|
| `rounded-box` | rounded rectangle for modules and stages | 57% | pipeline 70%, anatomy 69%, audio 68% |
| `circle-node` | circle, oval or circled operator (⊕, ⊗, concat) | 36% | anatomy 63%, vision 56%, audio 55% |
| `card-document` | card, document, page or folded-corner sheet | 22% | agents 45%, scope 36%, actors 36%, pipeline 33% |
| `cells-or-strip` | a row, strip or grid of small squares (tokens, embeddings, patches) | 20% | anatomy 50%, audio 41%, science 38% |
| `pill-chip` | pill, capsule, chip, tag or badge | 16% | scope 30%, vision 24%, agents 24% |
| `stack` | offset cards, sheets, slabs or layers | 16% | anatomy 29%, audio 27%, mosaic 24% |
| `icon` | an icon, logo, avatar or emoji stands for the thing | 15% | walkthrough 34%, actors 32%, agents 27% |
| `bars` | bars standing for vectors, scores or amounts | 15% | mosaic 21%, rl-robotics 21%, science 24% |
| `trapezoid` | trapezoid or funnel (an encoder, a decoder, a projection) | 11% | anatomy 33%, science 24%, rl-robotics 21% |
| `bubble` | speech bubble or call-out | 10% | agents 30%, actors 21%, scope and mosaic 17% |
| `block-arrow` | a block arrow as a shape of its own | 9% | — |
| `cylinder` | database, storage, dataset | 7% | — |
| `polygon`, `cube-3d`, `cloud`, `diamond` | hexagons and stars; pseudo-3D solids (tensors, feature maps); thought clouds; decisions | 6% / 5% / 4% / 2% | — |

Corners, measured: mixed square and rounded 42% of good figures, rounded 41%, square 17% (`style-rules.md` §4). The
family's shape idioms — the trapezoid encoder, the token strip, the stacked feature maps, the cylinder store, the
robot or brain icon for a model — are recorded as parts (`assets/symbols/`, `subtype: ai`) and named in the vocabulary
tags; use them where readers of the field know them, draw a plain box where they do not.

## Part D — Markers

| code | meaning | pool | high in |
|---|---|---:|---|
| `item-names` | subscripts, indices or short ids name items (h1 ... hn, L0 ... L9, t-1 / t / t+1) | 29% | anatomy 50%, ml-core 43%, pipeline 41% |
| `panel-letters` | letters head the panels | 24% | science 52%, contrast 42%, vision 41%, generative 40% |
| `inline-values` | numbers written in as values: scores, sizes, strides, probabilities, gains | 21% | science 43%, mosaic 36%, vision 32%, anatomy 31% |
| `tick-cross` | tick and cross (or thumbs) give a verdict | 15% | llm-nlp 25%, concept 24%, pipeline 21% |
| `order-numbers` | numbers order the steps | 14% | walkthrough 28%, science and ml-core 23-24%, actors 21% |
| `repeat-count` | xN or xL says a block repeats | 10% | audio 32%, science 19%, actors 18%, anatomy 17% |
| `snowflake-flame` | snowflake, flame or padlock mark frozen against trained | 6% | audio 27%, anatomy 12%, generative and multimodal 12% |
| `emoji-state` | emoji or small faces give a state or a judgement | 4% | agents 12%, scope 9% |
| `star`, `question-mark` | the proposed or best item; the unknown or the query | 2% / 2% | generative 12% (star) |

Identity markers are not order markers: h1 ... hn names heads, (a) (b) names panels, ① ② orders steps. The pre-screen
over all figures counts step markers: none 60%, letters 22%, plain numbers 10%, labelled arrows 5%, circled numbers 4%
(`layouts.md` §4). Markers of state (snowflake / fire, a padlock) go on the element they qualify and into the legend
when the figure has one.

## Part E — Emphasis: how the figure argues for the contribution

| device | pool | high in |
|---|---:|---|
| `strong-colour` — the one saturated, dark or red element among pale ones | 47% | audio 68%, mosaic 57%, contrast 56%, vision 56% |
| `bold-type` — bold type, a title, a banner or a written claim | 42% | mosaic 62%, agents 61%, pipeline 49% |
| `size` — the largest thing on the canvas | 36% | agents 61%, actors 57%, mosaic 55%, rl-robotics 48% |
| `frame` — a thick or coloured frame around the key part | 26% | actors 46%, agents 36%, rl-robotics 34% |
| `arrows` — big or coloured arrows lead to it | 24% | rl-robotics 41%, ml-core 40%, concept 40%, walkthrough 38% |
| `icon-or-mark` — an icon, a star, a call-out points at it | 20% | generative 36%, actors 36%, contrast 29% |
| `numbers` — a headline number, a gain or a chart | 18% | mosaic 38%, llm-nlp 28%, contrast 27% |
| `centre` — placed in the centre | 13% | scope 26%, agents 24%, mosaic 21%, vision 21% |
| `position-end` — placed where reading starts or ends | 12% | rl-robotics 21%, contrast 19% |
| `pictures` — real pictures, renders or examples carry the eye | 9% | vision 21%, mosaic and science 19% |
| `repetition` — the same motif repeated so the change stands out | 9% | — |
| `tinted-ground` — the proposed part sits on a tint while the rest stays plain | 7% | — |
| `whitespace` — isolation by white space | 2% | — |

One strong colour among pale fills is the family's accent, as in the systems family; what differs is how often the
claim is *written* into the figure (a bold title, a banner, a headline number: 42% and 18%) and how often the key part
is simply the largest (36%). Mosaics and agent figures do both.

## Part F — Legend, how the model is drawn, state markers

- **Legend:** none 59%, inside 23%, caption only 7%, per panel 6%, below 4%, right 1% (pre-screen over all figures:
  30% have one). Anatomy and contrast 56% with a legend; pipelines 28%, actors 25%. A legend inside the figure sits in
  a corner or a strip; per-panel legends belong to mosaics (17%) and science figures (19%).
- **The model** is drawn as a box in 29% of the records, not drawn at all in 23%, a robot 11%, an icon (brain, gear,
  chip) 7%, a trapezoid 6%, a network glyph 6%, a layer stack 6%, a logo 4%. By kind: anatomy box 52%, trapezoid 17%,
  layer stack 13%; actors robot 32%, icon 14%, logo 11%; walkthroughs icon 24%, robot 14%; scope none 57%. By field:
  audio box 82%; agents robot 33%, logo 12%; llm-nlp box 22%, robot 13%, icon 13%; science trapezoid 19%, layer stack
  14%; ml-core network glyph 14%. A logo is the paper's own material; the library's robot, brain, gear and chip icons
  and the box, trapezoid and layer-stack motifs are in `assets/symbols/` (families `llm`, `model-pictogram`,
  `trapezoid-module`, `transformer-block`).
- **Training state:** no marker in 78% of the records; a colour key 7%, snowflake and fire 6%, a padlock 1%, another
  device 9%. Anatomy 15% snowflake-fire, audio 27%; contrasts use a colour key 13%. The pre-screen counts a snowflake
  or flame in 9% of all figures (anatomy 17%, audio 27%, multimodal 16%, vision 15%); good figures 8% against 2%.

## Part G — Default encoding table

Start from these unless the figure or the user says otherwise; "deviate when" lists the recorded exceptions, and the
figure's own content may add others. Shares are of the 336 records unless marked (corpus).

| variable | default meaning | share | deviate when |
|---|---|---:|---|
| fill colour, modules | one pale colour per *kind* of element (inputs, modules, outputs, data) or per *part* named in the key | element-type 28%; per-part 75% | the figure is about actors (colour by actor, 21%) or about one item's identity across the figure (29%) |
| one strong colour among pale fills | the contribution, the changed part, the evidence span | emphasis strong-colour 47%; highlight 15% | the figure argues by a written claim or a headline number (bold-type 42%, numbers 18%) |
| red | wrong, failed, unsafe — or the one highlight; never both in one figure | verdict 41 of 77 red clauses | red is the paper's identity colour (say so in the key) |
| green | right, correct, safe, as red's counterpart | 28 of 60 green clauses | green is already a category colour |
| grey | the prior or baseline, the frozen part, the inactive region | prior 13, frozen 8 clauses | grey is already the ground |
| blue and grey for trainable / frozen | **say which** in a key or by snowflake / fire glyphs: the corpus splits evenly | trained blue 4 / grey 1; frozen grey 4 / blue 4 | — |
| region tints | name a stage, panel or role; pale (lightness ≈ 0.9), one hue per region | tinted regions 60%; region-identity 11% | the figure is one drawing on white (63% of the pool) |
| dashed box | a group, a scope, an optional or virtual part | 42% | dashed is already spent on a divider or an arrow meaning |
| dashed rule | a divider between panels, stages or halves | 17% | — |
| solid arrow | the main data flow | 28% say so; the default everywhere | — |
| coloured arrow | the kind of flow (per modality, per phase, per loss) | 33% | more than three arrow colours (then a key, or labels on the arrows) |
| dashed arrow | one secondary flow per figure: a gradient, feedback, an optional path | 9% | — |
| curved arrow | feedback, iteration, a long-range link | 17% | — |
| block arrow | a hand-over between stages or panels | 12% (a third of the records tag it) | — |
| line weight | main against minor | 21% | — |
| rounded box | a module or stage; square for cards, panels and cells | 57% / corners mixed 42% (corpus) | the field draws plain squares (audio, ml-core) |
| circle | an operator (⊕, ⊗, concat), a node, a variable | 36% | — |
| trapezoid | an encoder, decoder or projection | 11% (anatomy 33%) | the reader's field does not use it (then a labelled box) |
| strip of cells | tokens, embeddings, patches, a sequence | 20% (anatomy 50%) | — |
| card, document | a sample, a prompt, a record, a page | 22% | — |
| bubble | a message of an actor; dialogue | 10% (agents 30%) | — |
| icon | an actor or a tool, at label size, one style per figure | 15% (walkthrough 34%) | the icon would carry the content (`anti-patterns.md` §2) |
| (a) (b) letters on panels | the order to read the panels | 24% of records; 22% of all figures | panels are titled and the titles order themselves (39%) |
| plain digits or labelled arrows | the order of steps along a chain | 7% + 11%; corpus 10% + 5% | nothing is in sequence (68% of the pool has no step marker) |
| circled numbers | the same, the systems habit | 7%; corpus 4% | — |
| xN, t-1 / t / t+1 | a block repeats; one block over time | 10% | — |
| tick / cross, faces, star | a verdict, a judgement, the best item | 15%, 4%, 2% | — |
| snowflake / fire, padlock | frozen against trained | 6% + 1% (anatomy 12%, audio 27%) | the figure has no training story |
| inline values | real scores, sizes, probabilities, gains | 21% (science 43%, mosaic 36%) | the numbers are not the content |
| legend | inside, when a colour or marker code has more than two values and no direct label | 23% inside; none 59% | a direct label on the first instance does the work |

What the records fault most in their own figures: a code without a key (41%), a relation left to position or a shared
name instead of an arrow or leader (31%), arrows that cross or whose meaning is unclear (16%), missing labels or
unexplained symbols (14%), a meaning given only in the caption (14%) — `anti-patterns.md` §3 lists each with what to do
instead.
