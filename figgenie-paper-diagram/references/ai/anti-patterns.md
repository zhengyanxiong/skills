# Anti-patterns of AI-venue figures

What the figures rated lower do, and what goes wrong even in figures rated good. Three sources of different strength:
rates **measured** across the user's ratings (758 good, 158 ok, 28 bad among the figures whose extracted Figure 1
matches the published one), a **blind labelling** of fault types on 245 figures by agents that did not see the
ratings, and the weaknesses **named in the 336 semantic records** of good figures. Nothing here is a rule except where
it restates a print limit; it is evidence for a choice. Most of the systems anti-patterns (`../anti-patterns.md`) hold
here too (§7); this page is what is different.

## §1 What separates the ratings (measured)

| property | stands for | good | ok | bad |
|---|---|---:|---:|---:|
| at most 20 text items | bare | 9% | 23% | 32% |
| at most 30 text items and at most 90 shapes | bare | 4% | 15% | 14% |
| pre-screen: sparse | bare | 5% | 16% | 18% |
| no picture and no icon | bare | 19% | 17% | 32% |
| mid or strong fills on at least 15% of the canvas | loud ink | 10% | 17% | 25% |
| mid or strong fills on at least 25% of the canvas | loud ink | 4% | 8% | 14% |
| strong fills (lightness under 0.55) on at least 10% of the canvas | loud ink | 6% | 8% | 18% |
| pre-screen: drawn as a chat transcript | wall of text | 2% | 8% | 11% |
| pictures on at least 40% of the canvas | (not a fault) | 17% | 17% | 11% |
| smallest type under 5 pt | (tolerated by raters; not by print) | 53% | 33% | 39% |
| at least 120 text items | (not a fault) | 24% | 12% | 14% |

With about thirty figures rated bad, a rate in that column moves by 3-4 points per figure. Read with
`style-rules.md`: good figures carry more text (median 69 items against 42), more shapes (204 against 114), more
colours (9 against 6), fill the text width more often (89% against 78%) and have a legend more often (30% against
20%). **The lower-rated figures are not the crowded ones; they are the empty ones and the loud ones.** Small type is
*more* frequent among the good figures — the tension of §4.

## §2 The faults of lower-rated figures, tested blind

Seven fault types were named by reading the lower-rated figures with the ratings known, then labelled blind on 105
good, 105 ok and 35 bad figures in the same mix of kinds (Wilson 95% intervals in brackets; the labellers marked a fault
only when plain, so the rates are floors). At least one of the seven: good 27% (19-36), ok 39% (30-49), bad 66%
(49-79). Five are confirmed; two run the other way and are kept as cautions.

### 1. Loud ink — good 0% (0-4), ok 10% (5-17), bad 31% (19-48) — **avoid**

Large areas in saturated or dark colour, gradient-filled blocks, heavy black frames, white text on colour, red
banners: the fills shout over the content and the figure reads as a slide. The clearest divider in the data: none of
the good sample shows it. **Instead:** keep large fields pale (lightness ≈ 0.9, `palettes.md` §7) and spend strong colour
on small things that must be found (an accent, a verdict, the proposed part); outlines thin and dark, or none on a
tinted field. Across the corpus chromatic fills cover a median 12% of the canvas and strong ones almost nothing.
Lower-rated figures the blind labels put here: cvpr25-0028, iclr25-0176, iclr26-0159, icml24-0097, icml25-0136.

### 2. Clip-art as the content — good 6% (3-12), ok 7% (3-13), bad 23% (12-39) — **avoid**

Oversized stock pictograms, emoji, silhouettes or cartoon characters standing where the content should be: a globe
for "the world", a devil for "the attacker", a robot for "the model", with little else drawn. **Instead:** an icon may
name an actor at label size (the corpus draws icons in 54% of figures, at label size next to the thing they name, in
one style across the figure); it cannot carry the argument. Show what the actor does with real material: the prompt,
the sample, the output. Lower-rated figures: acl24-0027, iclr24-0014, icml23-0010, icml26-0306, neurips23-0051.

### 3. The bare skeleton — good 5% (2-11), ok 10% (6-18), bad 11% (5-26) — **avoid**

A handful of large boxes with one or two words each, joined by arrows; big type, wide gaps, nothing concrete; often a
single panel in one or two hues. It says what a reader of the abstract already knows. The measured rates of §1 are the
stronger evidence (≤ 20 text items: 9% of good, 32% of bad). **Instead:** put the content in — a real input and the
output it becomes, the thing each stage produces, the one example that shows the claim. If the idea really is three
boxes, draw it in one column, or make it one panel of a larger figure. Lower-rated figures: iclr23-0035, iclr24-0014,
icml24-0121, icml26-0096, neurips23-0120.

### 4. Small content in a big frame — good 1% (0-5), ok 3% (1-8), bad 6% (2-19) — **watch**

The drawing is fine in itself but tiny: thin lines and small icons lost in large tinted panels or in white space, so
the frame is what one sees. Rare everywhere; the direction is as expected. **Instead:** size the canvas to the content:
shrink the panels to fit, or enlarge the parts until labels reach the size floor without leaving empty fields.
Lower-rated figures: aaai23-0014, iclr25-0158, icml23-0050, neurips24-0361.

### 5. The wall of text — good 5% (2-11), ok 11% (7-19), bad 9% (3-22) — **avoid**

A transcript, a prompt, a bullet list or a table pasted in full: paragraphs of small coloured type, sometimes in three
or four highlight colours, with nothing drawn (chat transcripts: 2% of good figures, 11% of bad; tables drawn as the
figure: 0.5% against 2%). **Instead:** quote the two or three lines that matter and mark the words that carry the
point; elide the rest with an ellipsis; a list of items is a table in the text, not a figure. The text node of the spec
(`kind: text`) is for a quoted line or two, not a page. Lower-rated figures: aaai26-0010, acl25-0119, cvpr26-0017,
iclr25-0040, icml24-0027.

### Cautions the blind check did not confirm

- **Plots and screenshots as the figure** (good 4%, ok 4%, bad 6%): result charts, heat maps on dark grounds, 3D
  surfaces or raw screenshots take most of the canvas with little drawing. The rate does not separate the ratings, so
  it is a caution: a result may sit beside the drawing as one tile or an inset with a headline number (17% of good
  figures attach a chart); a screenshot is a sample — crop it to the part that matters, frame it lightly, keep it from
  setting the tone.
- **The overloaded dashboard** (good 10%, ok 3%, bad 3%): a dozen tiles, charts, photos and text blocks at one visual
  weight. The rate runs the other way — raters reward rich, many-part figures — so density itself is not the fault.
  What to keep from the first reading: give the figure's purpose the largest area, group the rest into two or three
  regions with one reading path, and make the tiles few and unequal on purpose (a contribution mosaic).

The labellers' own overall verdict followed the human rating only loosely (called weak: good 14%, ok 24%, bad 49%;
called strong: good 20%, ok 14%, bad 9%). A model judging a drawn figure is not a substitute for looking at it with
the check list of §6.

## §3 Faults named in figures rated good

1,005 weakness statements in the 336 records (3 per figure), sorted by keyword rules (a floor; a fifth match none).
These are faults a figure carries and is still rated good: polish, not what sinks a figure. Three of them are in more
than a quarter of the pool.

| fault | share | most in | instead |
|---|---:|---|---|
| text too small to read at print size | 72% | scope 89%, mosaic 79%, multimodal 82% | hold the size floor (it is a physical limit) and win the space back elsewhere: full width, shorter labels, fewer words per box, fewer tiles |
| a colour, line or symbol code the figure does not explain | 41% | mosaic 52%, pipeline 46%, vision 56%, ml-core 54% | say what a colour, a line style or a mark means inside the figure: a small key, or a direct label on the first instance (two thirds of the pool have no legend, so the label is the usual way) |
| a relation left to position, a shared name or the text: no arrow or leader | 31% | pipeline 43%, walkthrough 38%, audio 45% | if the reader must know B comes from A, draw it: an arrow, a leader, a wedge to the zoomed part, a shared colour with a label |
| arrows that cross, run long, or leave direction or meaning unclear | 16% | actors 32%, anatomy 27%, audio 27% | route so arrows do not cross; label the ones that are not plain data flow; one direction for one meaning |
| something the argument needs is not on the canvas (the model, the data, the remedy, a number, an axis) | 16% | walkthrough 28%, concept 20%, vision 21% | list what must be *seen* before drawing and check each is on the canvas |
| too much in too little space | 14% | contrast 25%, agents 21% | cut before shrinking: fewer examples, fewer tiles, shorter text; then space evenly |
| missing labels, undefined symbols or abbreviations | 14% | pipeline 23%, actors 21%, agents 24% | name every part once in words; expand an abbreviation at first use or in the key |
| a meaning given only in the caption or the text | 14% | pipeline 21%, concept 20%, ml-core 23% | write panel titles and part names into the figure; the caption explains, it is not where parts are named |
| a label, legend or mark placed away from what it belongs to | 9% | anatomy 19%, agents 15% | a label on or beside its object, a legend clear of the data, repeated things on one line |
| marks too faint, thin or pale to notice | 8% | anatomy and concept 12%, multimodal 13% | a mark that matters gets the line weight and contrast of the rest; pale leaders and thin dashes vanish in print |
| colour trouble: red against green only, tints too close, weak contrast, too many hues | 7% | contrast 15%, mosaic 12% | one hue, one meaning; tints that must be told apart kept well apart; red against green never the only signal |
| pasted bitmaps of low resolution, blurred or in another style | 6% | mosaic 12% | ≥ 150 ppi at print size (300 for photos), clean crops, the same frame on all |
| typos and uneven wording | 5% | — | proof-read; one wording per category |
| text or shapes that overlap, touch or are cut off | 4% | contrast 8%, actors 7% | no label on a line, no shape cut by the canvas edge |

Recorded examples: the four edge colours of the graph are not explained (`aaai25-0013_fig1`); no arrow ties each
instruction to its render, the match relies on left-to-right order (`aaai25-0059_fig1`); the meaning of green, yellow
and red predictions is given only in the caption (`acl23-0028_fig1`); the proposed method is not drawn, so the figure
motivates but does not explain (`aaai26-0036_fig1`).

## §4 Dense yet legible

Figures rated good are denser, and they pay for it in type size: the smallest type is under 5 pt in 53% of them (ok
33%) and "text too small" is the most named weakness of the pool. A reader at a screen zooms in; a reader of the
printed page cannot. The skill keeps its floor (6 pt for labels, 5 pt for badge digits) and reaches the density of
good figures by other means: the full text width (`meta.column: double`), short labels, a real example in place of a
sentence, a picture or an icon in place of a word, fewer and larger tiles, one key instead of repeated captions. An
empty figure with large type is not the safe choice: it is the first fault of §1.

## §5 What the checker flags

For a spec with `meta.family: ai`, `lint.py` adds advisory findings (warn or info, never an error; parameters in
`style-thresholds.json` `lint.ai_pass`):

| code | fires when | level | rate in good / bad figures |
|---|---|---|---|
| `ai.bare` | a full-width figure draws at most 20 text runs | warn | 9% / 32% |
| `ai.loud-ink` | mid or strong fills cover at least 15% of the canvas | warn | 10% / 25% |
| `ai.hues-no-key` | four or more hue families carry a meaning (per the spec) and the figure has neither a legend nor direct labels on them | info | — |
| `ai.no-sample` | a scope overview, mosaic, walkthrough or contrast has no `image`, `text`, `bubble` or `values` content | info | most good figures of these kinds carry one |

The shared checks stay as they are: type under the floor (error below 5 pt, warning below 6 pt), the venue's width
band, bleed, contrast, arrowheads, alignment, bitmaps (`SKILL.md` "Rules that are not negotiable"). The fill-colour
ceiling (`colour.fills`) is raised to 16 and the saturated-fill ceiling (`colour.saturated`) to 4 for this family,
because its good figures carry 9 fills and 4 hue families on median; both remain warnings.

## §6 Self-check before declaring done

Ask these of the PNG at 100%:

1. Can a reader find the contribution in five seconds, and is it the loudest thing (one strong colour, a frame, size
   or a written claim — not all of them)?
2. Is anything under 6 pt (badge digits 5 pt)? If the figure needed smaller type to fit, something must go, not shrink.
3. Does every colour, line style and marker that carries a meaning have a key or a direct label on its first instance?
4. Is every relation the reader needs drawn — an arrow, a leader, a wedge to the zoom — rather than implied by position
   or a shared name?
5. Where the kind usually shows a sample, a picture or a worked example (scope, mosaic, walkthrough, contrast), is one
   there, at a readable size, framed like the others, from the paper's own material?
6. Are icons at label size, in one style, next to what they name, and never the content itself?
7. Are the panels lettered or titled, read in the order the caption uses, with the prior case first and ours last?
8. Is any text block longer than two or three lines? Quote and elide.
9. Do the large fields stay pale and the strong colour small? Would the figure still read in greyscale?
10. Does it fill the venue's text width (or sit in one column of a two-column venue), at 130-320 pt tall?

## §7 What carries over from the systems anti-patterns

From `../anti-patterns.md`, unchanged: a legend that covers only part of the encoding; arrowheads missing or a tangle
without direction; the shape zoo (flowchart shapes with no stated meaning); everything drawn N times instead of once
with xN; floating call-outs without leaders; type oversized for its box or colliding with lines; misalignment; an
inverted hierarchy (containers louder than their contents); meaning recoverable only from the caption. What does *not*
carry over: the systems rule of one accent among greys (this family runs three to five hue families and tinted regions
in a third of its figures) and the rarity of pictures (half of these figures hold samples, which is content, not
decoration).

Sources: `ai-corpus/lab/distill/antipatterns/` (`antipatterns.md`, `blind/results.md`, `lower_rated_labels.csv`) and
the weakness tables of `ai-corpus/lab/distill/encoding/encoding.md` §7.
