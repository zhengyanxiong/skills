# Formulas in a figure — vector TeX inside the SVG

Some architecture figures carry the paper's own symbols: a loss inside the module that
minimises it, the weighting rule a scorer applies, the name of the selected parameters (θ<sup>⋆</sup>) on the
arrow that carries them. Most figures carry none, and the rules of `style-rules.md` still apply: a formula is a
label, not decoration — it goes where the paper's term would go, at label size, in the label's colour. When the
figure needs one, this is how it is drawn: the TeX is typeset by MathJax (TeX fonts, node) into vector paths
that live inside the figure, print like the rest of it, and stay editable through the TeX source kept in the
markup. `embed_fonts.py`, `export_pdf.py` and the PowerPoint export all work on the result without any change.

## 1. The placeholder (what you write by hand)

A formula is one `<g>` inside the spec element it belongs to (a node, a container title, an annotation, a legend
row), exactly where a `<text>` would be. A formula that labels an edge goes in its own `a:<id>` annotation group
with `data-anchor` set to the edge id, not inside the `e:` group: glyph paths inside an edge group make the
linter measure the edge from the formula (`edge.dangling`, `edge.endpoint`).

```svg
<g data-symbol="tex" data-tex="\hat{J}(\theta)" data-x="54" data-y="24"
   data-size="6.5" data-anchor="middle" data-fill="#0d0d0d"/>
```

| attribute | meaning | default |
|---|---|---|
| `data-tex` | the TeX (MathJax syntax; `base` + AMS + the usual packages; `\text{}`, `\mathrm{}`, `\hat{}`, `\frac{}{}`, `\sum`, `\arg\max`, `\big(`, `\,` all work) | required |
| `data-x` | anchor x in pt | required |
| `data-anchor` | `start` \| `middle` \| `end` — what `data-x` is, like `text-anchor` | `start` |
| `data-y` | baseline y in pt (the same baseline a `<text>` on that line would use) | required |
| `data-valign="middle"` | make `data-y` the vertical ink centre instead (for a formula centred in a card or badge) | off |
| `data-size` | font size in pt = the em of the formula; keep it equal to the label size around it | root `font-size` |
| `data-fill` | colour | nearest ancestor `fill`, else `#0d0d0d` |
| `data-display="1"` | display style: `\sum` limits above/below, taller fractions, `\arg\max_{x}` with the subscript underneath | off |

`tex_fill.py` renders the placeholder in place and records the measured box on it (`data-w`, `data-asc`,
`data-desc`, `data-baseline`); the paths are regenerated from `data-tex` every time it runs, so the TeX in the
file is the only source of truth. Never edit the generated paths. Legacy spellings `data-ax` / `data-baseline`
from older figures are accepted and rewritten.

This is the one sanctioned exception to "text stays `<text>`": the paths are wrapped in `<g data-symbol="tex">`,
the linter treats them like the parts of a library symbol (they are not mistaken for the node's box), and the
source is kept.

## 2. Where it enters the workflow

The formula tools are used *while* drawing, in the same places text is measured, written and checked:

| step | what to do |
|---|---|
| 4 drawing plan | measure like any label: `python3 scripts/tex_measure.py --size 6.5 --box '\hat{J}(\theta)' 'B_t'` prints width, ascent, descent and the box that holds it. Fractions and `\sum` are about two text lines tall — plan the box height from the printed ascent + descent, not from the label height. |
| 5 draw | write the placeholder where the `<text>` would be. For a label with inline formulas ("Sampler $p_\theta(x)$") let the tool lay out the runs: `python3 scripts/tex_measure.py --mixed 'Sampler $p_\theta(x)$' --size 6.5 --bold --x 54 --y 24 --anchor middle --emit` prints the `<text>` and `<g data-symbol="tex">` elements with their x positions; paste them into the group. Text runs are measured with the figure's fonts (`--font` / `--cjk` keys), formulas with MathJax, 1.5 pt between runs (`--gap`). |
| 6 self-check | `python3 scripts/tex_fill.py fig.svg --check` **before** `check.py`: it renders every placeholder and reports formulas that leave their box (`tex.overflow`, error), sit closer than 1.5 pt to its edge (`tex.padding`, warning) or collide with a label or another formula in the same group (`tex.overlap`, error). Then run `check.py` as usual and look at the PNG. Edit the TeX or the position, re-run `tex_fill.py`, re-check. |
| 7 deliver | nothing changes: the formula is paths, `embed_fonts.py` and `export_pdf.py` need no extra face. |
| PowerPoint copy | `svg2pptx.py` turns each formula into a native PowerPoint equation (`references/pptx-export.md`). |

`tex_fill.py fig.svg --strip` puts the file back to bare placeholders (small diffs for review); fill again before rendering.

## 3. Conventions

- **Size.** A formula inside a box is set at the box's label size (6.5 pt) or its sublabel size (6 pt), never
  smaller than 6 pt; the em of the formula is `data-size`, so a fraction at 6 pt already spans ≈ 21 pt of height.
  Do not shrink a formula to make it fit — split it into lines (one placeholder per line, left-aligned at the
  same x) or shorten it (`\hat{J}` in the figure, the full expectation in the text).
- **Display style** only for a formula that stands alone in a box (the sampling rule, the selection rule);
  inline formulas in a sentence stay inline (`\sum_{i}` becomes a side subscript, which is what a text line wants).
- **Colour** follows the text it replaces: ink on light fills, white on the accent, muted grey in notes.
- **Symbols are the paper's own.** Use the exact symbol the text uses (`\theta^\star` if the paper writes
  a star), so the figure, the caption and the body agree; abbreviations (`\mathcal{L}_{fit}`) are fine when the caption
  expands them.
- **Which labels get a formula.** The name of the thing that flows along an edge (`B_t`, `\theta^\star`), the one
  rule a module applies (one line, not the derivation), the objective in a note. Not every node needs one; a
  figure with more formulas than nouns is a slide, not a figure.
- **Spacing in mixed lines.** Trailing/leading ASCII spaces inside `<text>` are dropped by SVG; rely on the
  1.5 pt gap the tool leaves between runs, and on `\,` / `\;` inside the formula.

## 4. Requirements and failure modes

- `node` ≥ 18 and `scripts/mathjax/node_modules` (`npm install` there; the tools run it once for you, network needed).
- Malformed TeX is reported with MathJax's message (`Missing argument for \frac`, `Undefined control sequence`):
  fix the TeX, the placeholder stays. `\newcommand` does not persist between formulas — write them out.
- The linter does not measure formulas as text: `tex_fill.py --check` is the overflow / overlap check for them.
