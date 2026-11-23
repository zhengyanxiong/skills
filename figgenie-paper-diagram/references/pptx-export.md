# Editable PowerPoint copy of a finished figure (optional, after delivery)

Some authors want to keep editing the figure by hand — move a box, change a word, recolour — in PowerPoint
or Keynote rather than in SVG, or paste it into a Word thesis as a native object. `svg2pptx.py` turns the
delivered SVG into a `.pptx` in which **every primitive is a native, editable shape** at the same coordinates,
grouped per spec element and named so the selection pane reads like the spec. This is a post-drawing step the
user opts into; nothing in the drawing workflow depends on it.

```
python3 scripts/svg2pptx.py fig.svg --spec spec.json            # → fig.pptx
python3 scripts/pptx_check.py fig.pptx --svg fig.svg              # paint order, inventory, slide size
```

Options: `-o out.pptx`; `--scale 2` (twice the print size, easier to edit; insert into the document at 50 %);
`--latin Arial --cjk "Source Han Sans CN"` to force typefaces; `--math text` to write formulas as plain text;
`--xsl PATH` to point at Office's `mathml2omml.xsl`; `--no-group`; `--force` to overwrite an existing deck
(refused by default, because the deck may already carry hand edits).

## What becomes what

| SVG | PowerPoint |
|---|---|
| root `viewBox="0 0 W H"` | slide of exactly W × H pt (× `--scale`); 1 SVG pt = 1 PowerPoint pt |
| `<rect>` (with `rx`) | rectangle / rounded rectangle, fill, outline width, dashes reproduced exactly (`custDash`) |
| `<circle>` `<ellipse>` | oval |
| `<line>`, 2-point straight `<path>` | straight connector; `marker-start` / `marker-end` → head / tail arrowheads (filled marker → triangle, hollow → open arrow; size follows the stroke width) |
| `<polyline>` `<polygon>`, other `<path>` (H V L C S Q T A Z, relative too) | freeform custom geometry; arcs become béziers; closed paths keep their fill; "edit points" works in PowerPoint |
| `<text>` | text box, no wrap, zero margins, anchored so the baseline lands where the SVG's does; `text-anchor` → alignment; bold / italic / colour kept; `transform="rotate(…)"` → rotated box (gutter labels) |
| `<g data-symbol="tex">` | native PowerPoint equation (OMML): TeX → MathML (MathJax) → OMML (Word's stylesheet), Cambria Math, colour and size kept; double-click opens the equation editor |
| `<image>` (PNG / JPEG: a data URI, or a local file next to the SVG) | native picture with the same bytes: `preserveAspectRatio` kept (meet → fitted in the box, slice → PowerPoint's own crop, so it can be re-cropped, none → stretched), rotation and opacity kept; named `n:… 图片`, alt text = the spec label |
| `<g id="n:…">` etc. | one group per spec element, named `n:scorer Scorer` (id + spec label when `--spec` is given); `legend` rows fold into one group |
| symbols (`data-symbol="…"`), nested `<g>` with transforms | flattened into the parent group with the transform applied |
| `<defs>`, `<marker>`, `<title>`, `<desc>` | not drawn (markers become arrowheads) |
| `opacity`, `fill-opacity`, `stroke-opacity`, `stroke-linecap`, `stroke-linejoin`, `stroke-dasharray` | alpha, cap, join, custom dash |
| `<use>`, gradients, filters | not supported (the contract forbids them); reported |
| an `<image>` linked to a URL, missing, or not PNG / JPEG | skipped and reported (lint.py flags it, embed_fonts.py refuses to deliver it) |

Paint order is the SVG document order — containers under connectors under boxes under badges — enforced
after grouping (python-pptx appends every new group on top; the script puts them back). `pptx_check.py`
verifies that the deck's top-level order equals the SVG's, that every `<image>` became a picture, and that no
connector is hidden under a shape or picture the SVG draws beneath it; a covering that the SVG itself paints
(a tier drawn over an arrow tip) is reported as a note, so fix that in the SVG, not in the deck.

## Fonts

The root font stack is mapped to installed PowerPoint typefaces (`scripts/svg2pptx.py`, `PPT_FONTS`):
`helvetica` → Helvetica Neue / Helvetica, `arial` → Arial, `calibri` → Calibri, `times` → Times New Roman,
`source-sans` → Source Sans Pro if installed else Arial, CJK companion → Source Han Sans CN / PingFang SC / …
Text boxes are sized from the skill's own font files (`measure_text.py`) plus padding and never wrap, so a
substituted face only shifts glyphs by a fraction of a point. Formulas are Cambria Math (Office's math font).

## Formulas

Equations need `node` (MathJax, `scripts/mathjax`) and Office's `mathml2omml.xsl`, found automatically at
`/Applications/Microsoft Word.app/Contents/Resources/mathml2omml.xsl` (macOS) or
`C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL` (Windows); `--xsl` or `MML2OMML_XSL` override.
Without it, or with `--math text`, each formula is written as readable Unicode text (π_θ^(0)) in Cambria Math
and `pptx_check.py` says so. Finder's QuickLook cannot show OMML and displays that same fallback text;
PowerPoint shows the real equation. After PowerPoint re-saves the deck the equations are hoisted into
shape-level `mc:AlternateContent` (python-pptx no longer lists them; `pptx_check.py` reads the XML and still does).

## What to tell the user

One line on how to edit: open the selection pane (Home → Arrange → Selection Pane) — every object is named
after its spec id; double-click a group to edit one part; right-click a folded arrow → Edit Points; double-click
a formula → equation editor. Re-running the script never overwrites a deck without `--force`, so hand edits
are safe; to change the figure structurally, edit the SVG and export again.

## Requirements

`pip install python-pptx` (≥ 1.0), `node` ≥ 18 for equations, Microsoft Office for the OMML stylesheet.
