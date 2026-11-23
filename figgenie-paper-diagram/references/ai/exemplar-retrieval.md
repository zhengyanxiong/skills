# Exemplars for an AI-venue figure: find them, let the user choose, read them

AI-venue figures vary far more than systems figures: the kind of figure, the field and above all the content (samples,
outputs, screenshots, icons, worked instances) decide how they are drawn. So before planning the layout, find figures
that are close to this one in kind, layout, field, tags and meaning, show a handful to the user, and read the ones they
pick. The exemplars sharpen your own plan; they are references, not templates.

## The library

`assets/exemplars/ai/` holds one card per Figure 1 of the AI corpus (ICLR, ICML, NeurIPS, CVPR, ACL, AAAI, 2023-2026),
3,210 figures in three tiers. The search ranks the tiers in this order, and so should your choice:

| tier | figures | what you can read |
|---|---:|---|
| 1 | 336 with a deep semantic record | `print.webp` (the printed figure, 150 dpi), `source.svg` (how it is built), `semantics.json` (what it shows, what to learn, idioms, encoding, weaknesses) |
| 2 | 638 more that a human rated good | `print.webp` and `source.svg` for the 422 whose vector figure could be extracted; else the picture only |
| 3 | 2,236 other designed figures (unrated, or rated ok) | a card from a first pass over the picture, the paper's title and abstract, a thumbnail; the SVG and a larger picture when the local corpus or the gallery picture is available |

Cards carry the paper title, abstract, kinds (they overlap; the first is the primary), variant, sub-field, tags,
layout (arrangement, panels, direction), what the figure holds (pictures, icons, bubbles, charts, formulas, examples),
the objects drawn, keywords, and for tier 1 the record's summary and lesson. Tier-3 labels come from a quicker pass and
are less reliable; a card rated ok says so.

Tags come from one vocabulary of about 120 entries in two groups: things that are drawn (well-known concepts with a
usual drawing such as `llm`, `transformer-block`, `diffusion-chain`, `database-cylinder`, and building blocks such as
`token-strip`, `stacked-cards`, `sunburst-taxonomy`) and devices applied to a figure or its elements (`zoom-callout`,
`block-arrows`, `verdict-marks`, `state-snapshots`, `tab-titled-panels`). `vocab` prints every entry with its
definition and how many cards carry it. Tier-1 cards are tagged from their record; the other tiers only carry what the
quick pass happened to name, so a missing tag there means little.

## The step

Do it once the brief is clear and before the layout is decided; run it again when the user asks for other options.

1. **Write the query from the brief**, not from a template (`python3 scripts/find_ai_exemplars.py vocab` lists every value):
   - `--kind`: the kinds this figure will be, primary first (two when unsure).
   - `--subfield`: the paper's field first, a second one when it straddles two.
   - `--layout`, `--panels`: only when the content already implies them (three stages, a before/after pair);
     otherwise leave them out and let the exemplars suggest layouts.
   - `--want` / `--avoid`: what the content needs: `pictures` (data samples, outputs), `icons` (actors, tools),
     `bubbles` (dialogue), `charts` (a result), `formulas`, `examples` (a worked instance).
   - `--tags`: ids of the tag vocabulary, only for things you plan to draw or devices you plan to use (`vocab`
     lists them). A tag adds to the score, it does not filter.
   - `--objects`: the things that will be drawn, in the paper's words, comma separated.
   - `--text`: the paper title, two or three sentences of the abstract, and one sentence on what the figure must make
     the reader see. This is the semantic part of the match.
2. **Search and choose by meaning.** `python3 scripts/find_ai_exemplars.py search ...` prints the best of each tier and
   a few figures of the same kind from other fields. Read the cards and choose 9 to 12 for the user:
   - mostly tier 1, two to four from tier 2, one or two from tier 3 where they fit the content better;
   - at least one from another sub-field that shares the kind or the content (the general view next to the field view);
   - different solutions (layouts, ways of showing the samples, densities), not twelve variants of one;
   - leave out a figure that matches only on topic.
3. **Show them to the user.** `python3 scripts/find_ai_exemplars.py sheet ID ... --out <work dir>/exemplar_candidates.png`
   draws a numbered sheet (★ deep record, ✓ rated good). Show the sheet with its table, adding one short line per
   figure on why it may help, and ask the user to pick two to four by number. They may also answer "you choose",
   "more like 5" (`search --like ID`), or reject them all with a hint (a new query with that hint). Take the user's pick
   as a strong preference about look and feel and say so in the plan. If the user leaves it to you, take three (two
   from tier 1, one from another field) and name them.
4. **Read the picks.** `python3 scripts/find_ai_exemplars.py files ID ...` lists, per figure, the picture to LOOK at
   and the SVG to read. Look at the picture for overall density, balance and how samples and icons sit; read the SVG
   for type sizes, colours, stroke widths, corner radii, grouping, and how bitmaps are placed and framed; for tier 1
   read the semantic record's lessons, idioms and weaknesses.
5. **Write down what you take.** In the drawing plan, per exemplar: the one or two devices you borrow, what you will
   not copy, and which of its weaknesses you will avoid.

The paper's own material (its samples, screenshots, real numbers, logos the user supplies) comes before anything an
exemplar suggests. The figure you draw should not look like any one exemplar; a figure unlike all of them is a normal
outcome.

## Notes

- What the paper's sub-field tends to draw differently from the family (kinds, samples, icons, idioms, colour, the part
  families it supplied, the fields it is paired with), with a few exemplars per field, is in `domains.md`; read it next to
  the general references, as the second view, not a filter.
- The search takes under a second and needs no network; the sheet needs Pillow. `--fetch` (sheet, files) downloads the
  gallery picture of a tier-3 figure that is not available here.
- Scores only rank; the tier bonus puts tier 1 first when the matches are close. Judge the cards, not the numbers.
- The figures belong to their authors and publishers (`assets/exemplars/ai/SOURCES.md`); they are for study, never
  material to copy into a figure.
