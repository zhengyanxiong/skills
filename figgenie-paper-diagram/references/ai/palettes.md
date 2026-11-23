# Palettes of AI-venue figures

What colour the Figure 1s of ICLR, ICML, NeurIPS, CVPR, ACL and AAAI carry, measured three ways: the flat fills of
2,470 figures by area (the SVGs), the palette entries of the 336 deep semantic records (what each colour is used for),
and the hue counts of the pre-screen over all 3,274 figures. The systems families of `../palettes.md` remain the
house palettes; five families of this corpus are added to `../palettes.json` with `"family": "ai"` (§9) and have swatch
cards in `../../assets/palettes/`. The figure decides; these are the habits to start from and the numbers to argue
against.

## 1. How much colour, by area

Chromatic flat fills cover a median 12% of the canvas (p25 5%, p75 28%): pale fills 6%, mid 1%, strong almost none;
light grey 2%; pictures 11% (16% in the exemplar pool). The tone of a figure's colour fields, by area:

| | pale | mixed | strong | no colour field |
|---|---:|---:|---:|---:|
| corpus (2,470) | 52% | 8% | 26% | 14% |
| rated good (758) | 53% | 8% | 25% | 14% |
| rated ok or bad (186) | 44% | 6% | 28% | 22% |

Pale fields are the family's norm; the weaker figures are more often without any colour field (22%) — the bare
skeleton of `anti-patterns.md` — not louder. By kind (exemplar pool): pipelines 61% pale, anatomy 63%, contrasts 31%
pale and 37% strong (verdicts and accents), walkthroughs 38% strong, concept schematics 24% without a colour field.
By field: agents 73% pale, audio 77%, llm-nlp 54%; generative 24% and ml-core 29% without a colour field; vision 38%
strong.

Hue families covering at least 1% of the canvas: none 13%, one 15%, two 23%, three 25%, four 15%, five or more 8%.
The largest hue is blue in 33% of the figures with a colour field, orange 25%, green 16%, teal 9%, red 7%, yellow 6%,
purple 3%, pink 2%.

## 2. How many colours

- Palette entries per record: p10 6, median 9, p90 14; measured distinct fill colours in the SVG: good median 9 (p25
  6, p75 14, p95 27), weaker figures 6 — more colours is a (small) good-figure signal (`style-rules.md` §1).
- Hue families among a record's chromatic fills: neutral only 4%, one hue 6%, two 17%, three 26%, four or five 38%,
  six or more 8%. Walkthroughs and actor figures sit at three to five (79%, 79%); vision figures are two-hue in 32%;
  llm-nlp figures reach six or more in 12%.
- The pre-screen's count by eye over all figures (tints and icon colours included): 1-2 hues 8%, 3-5 62%, 6 or more
  30%; good figures 8 / 59 / 33%, weaker ones 16 / 57 / 27%.

## 3. Which hues, and which together

Share of records using the hue family for a fill at all: blue 72%, orange 64%, green 56%, red 47%, teal 34%, yellow
29%, purple 18%, pink 16%. By field: llm-nlp blue 87%; audio orange 86%, blue 82%, green 68%; agents orange 76%;
science teal 52%; vision yellow 41%; ml-core orange only 46%.

Pairs that occur together: blue + orange 51%, blue + green 43%, green + orange 41%, blue + red 36%, orange + red 31%,
green + red 29%, orange + teal 23%, blue + teal 22%. The two-hue figures (58) are blue + orange 10, green + orange 7,
blue + red 6, blue + yellow 5; the three-hue figures (88) blue + green + orange 20, blue + orange + red 12, green +
orange + red 6. Blue and orange is the family's pair, as it is the systems family's.

## 4. How strong

By count of palette entries (not area): pale 31%, mixed 27%, strong 38%, no chromatic fill 4%; a chromatic entry is
pale in 41%, mid 30%, strong 26%, grey 3%. Pipelines (41% pale) and audio (68%) are the pale kinds; walkthroughs (55%
strong), science (52%) and ml-core (49%) spend strong colour, mostly on small things (verdicts, highlights, the
accent). Read with §1: strong entries are many but cover little area.

## 5. The values the corpus uses

Median lightness and saturation (HLS) per hue and tone, with the exact values used most (the Office theme tints are
the family's vocabulary: `#fff2cc` is the most used fill of the whole corpus):

| hue | pale (L ≈ 0.90) | mid (L ≈ 0.70) | strong (L ≈ 0.45) |
|---|---|---|---|
| blue | `#deebf7` `#dae3f3` `#dceaf7` `#dae8fc` `#bdd7ee` | `#5b9bd5` `#9dc3e6` `#a6caec` `#8faadc` | `#4472c4` `#2e75b6` `#1f77b4` |
| orange | `#fff2cc` `#fbe5d6` `#fbe3d6` `#f8cbad` `#ffe599` | `#f4b183` `#ed7d31` `#e97132` | `#ffa500` `#c55a11` `#ff7f0e` |
| green | `#e2f0d9` `#d9f2d0` `#d9ead3` | `#c5e0b4` `#a9d18e` `#b6d7a8` | `#70ad47` `#76b900` `#548235` |
| red | `#f8cecc` `#f4cccc` `#fadbdf` | `#ea9999` `#e6b8af` `#ff6666` | `#ff0000` `#c00000` `#cc0000` `#d62728` |
| yellow | `#ffe699` `#fff2ca` | `#ffd966` `#fee695` | `#ffc000` `#ffff00` `#bf9000` |
| purple | `#d9d2e9` `#e5ccff` | `#b4a7d6` `#ccb5d3` | `#7030a0` `#674ea7` |
| teal | `#c1e5f5` `#caeefb` `#b7dde8` | `#b0e3e6` `#61cbf4` `#46b1e1` | `#00b0f0` `#156082` `#1ba1e2` |
| pink | `#f2cfee` `#f6b5c7` | `#e59edd` `#e377c2` | `#d83661` `#e50088` |

Most used values over all roles: `#fff2cc` 57, `#ff0000` 49, `#c00000` 42, `#f2f2f2` 40, `#d9d9d9` 37, `#ffc000` 33,
`#7f7f7f` 29, `#deebf7` 27, `#595959` 27, `#fbe5d6` 27, `#e2f0d9` 27, `#dae3f3` 25, `#4472c4` 23, `#ed7d31` 19,
`#70ad47` 18, `#a9d18e` 18. Opacity below 1 (translucent washes and overlays) in 363 entries of 134 figures.

## 6. Lines and text

- Outlines and arrows are coloured (not only grey or black) in 70% of the records, neutral only in 15%; scope
  overviews are the exception (neutral 28%, coloured 43%). Most used line colours: `#000000`, `#7f7f7f`, `#595959`,
  `#172c51`, `#c00000`, `#042433`, `#ffc000`, `#4472c4`, `#0070c0`, `#ff0000`; a coloured line is blue 27%, green 16%,
  red 16%, orange 14%, teal 11%.
- The dark neutral of lines and text is black (`#000000`, 29 records) or dark grey (`#595959` 21, `#404040`,
  `#262626`); pure black for everything in 9% of the figures.
- Text is coloured in 41% of the records (mosaic 55%, multimodal 55%): a coloured text is red 24% (`#ff0000` 22,
  `#c00000` 13: a verdict, a highlighted word), blue 22%, green 17%, orange 16%. White text sits on dark fills in a few
  figures; keep it for strong fills that clear 4.5:1.

## 7. Grounds and region tints

Ground: white 63% of the records (61% of all figures), tinted regions 31% (33%), grey panels 6%. Scope overviews and
agent figures are tinted in half; science-engineering is white in 90%. Region tints: one per figure in 56%, two 25%,
three or more 19%; grey 37% of tints, orange 21%, green 13%, blue 12%, teal 6%, red 4%; lightness p10 0.82, median
0.91, p90 0.96; saturation median 0.10, p90 0.20. Most used: `#f2f2f2` and `#fff2cc` (9 each), `#fbe3d6`, `#d9f2d0`,
`#dceaf7`, `#fbe5d6`, `#f5f5f5`, `#e2f0d9`, `#e7e6e6`, `#d9d9d9`, `#deebf7`. On a white ground a tint is grey in 48%
and orange in 22%; on a tinted ground grey 58%, orange 41%, green and blue 27% (several tints per figure). How parts
are set apart, nesting depth and the combinations are in `layouts.md` §7.

## 8. Tool themes

A record carries three or more exact Office theme colours or tints in 39% of the pool (agents, rl-robotics and audio
45%; ml-core 29%), draw.io pairs in 7% (audio 14%, llm-nlp 13%). The measured pass over the SVGs, which looks for the
six accents of a theme, finds Office in 9% of good figures and 4% of the weaker ones, tab10 (matplotlib) in 1%. The
slide tools drew most of this corpus (`style-rules.md` §11), and their tints are what readers of these venues see.

## 9. The AI palette families

Five families added to `../palettes.json` (`"family": "ai"`; cards in `../../assets/palettes/`). They are starting
points built from §5 and §7; the systems families serve too (`ink-outline` and `blue-outline` for concept schematics
and anatomy on a bare ground, `pastel-regions` for tinted stages, `multi-hue-categorical` for a gallery of categories),
and `custom` with the roles named is always allowed.

| id (`meta.palette`) | name | module / accent | start here for |
|---|---|---|---|
| `office-pastel` | Office tints, one mid accent | `#deebf7` / `#ed7d31` | pipelines and anatomy; the family's default look (39% of the records) |
| `tinted-regions` | pale region fields, white or pale boxes | `#ffffff` on `#fbe3d6`, `#d9f2d0`, `#deebf7` / `#4472c4` | stages, roles or panels that each need a field: scope overviews, agents, mosaics |
| `role-colours` | one mid colour per actor, part or token type | `#9dc3e6`, `#f4b183`, `#a9d18e`, `#ffd966`, `#b4a7d6` / `#c00000` | actor interaction, token strips, lanes per modality; needs a key or direct labels |
| `verdict-contrast` | grey prior, blue ours, red / green verdicts | `#d9d9d9` prior, `#deebf7` ours / `#4472c4`; `#c00000` wrong, `#70ad47` right | side-by-side contrasts, problem-then-fix |
| `frozen-trainable` | blue trained, grey frozen, peach for the new block | `#deebf7`, `#e7e6e6`, `#fbe5d6` / `#ed7d31` | model anatomy with training state; the key or the glyphs say which is which |

Roles follow `../palettes.json` `role_vocabulary` (canvas, container, lane, module, module-alt, accent, stroke, text,
text-muted, arrow, arrow-accent, legend). Colour *meanings* — verdicts, actors, state, modality — are in `encoding.md`
Part A and Part G.

## 10. What not to do

- Large fields in saturated or dark colour, gradient blocks, heavy frames, red banners: loud ink, the clearest mark of
  a weak figure (none of the good sample, a third of the bad; `anti-patterns.md` §2). Strong colour on the canvas is
  almost zero by area in the corpus (§1).
- A single hue or none at all when the figure has parts to tell apart (1-2 hues: 8% of good, 16% of weaker figures).
- Red against green as the only signal of a verdict; add the tick and cross, or words.
- Four or more hue families carrying meaning with neither a key nor direct labels (`anti-patterns.md` §5 flags it).
- Tints too close to tell apart, or a tint darker than the boxes on it (an inverted hierarchy).
- Copying a colour read off a bitmap as if it were the figure's: 157 entries of 74 records are approximate values from
  pasted pictures.

## 11. Figures to look at

Deep-record exemplars by palette habit (`python3 scripts/find_ai_exemplars.py files ID`): neutral `aaai25-0057_fig1`,
`iclr26-0017_fig1`, `icml23-0002_fig1`; one hue `aaai24-0047_fig1`, `acl24-0062_fig1`, `iclr25-0069_fig1`; two hues
`aaai25-0059_fig1`, `acl23-0022_fig1`, `acl25-0080_fig1`; three hues `aaai25-0013_fig1`, `aaai25-0102_fig1`,
`acl24-0005_fig1`; four or five `aaai23-0023_fig1`, `aaai24-0061_fig1`, `aaai25-0119_fig1`; six or more
`aaai26-0028_fig1`, `acl24-0024_fig1`, `cvpr24-0028_fig1`; pale fills `aaai25-0124_fig1`, `acl23-0008_fig1`,
`acl23-0028_fig1`; strong fills `aaai24-0047_fig1`, `aaai25-0013_fig1`, `aaai25-0083_fig1`; tinted ground
`aaai26-0001_fig1`, `acl25-0148_fig1`, `cvpr25-0084_fig1`; grey panels `iclr25-0219_fig1`, `icml24-0039_fig1`.

Sources: `ai-corpus/lab/distill/palettes/` (`palettes.md`, `area_cache.json`, `entries.csv`, `swatches.csv`) and
`ai-corpus/lab/distill/grounds/`, built by `scripts/distill/ai_palettes.py` and `ai_grounds.py`.
