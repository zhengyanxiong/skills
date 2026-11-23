#!/usr/bin/env python3
"""F. Visual encoding of the AI-family figures: what colour, line style, shape, markers and emphasis are used to say.

    python3 figgenie-paper-diagram/scripts/distill/ai_encoding.py        # -> ai-corpus/lab/distill/encoding/

  encoding.md           the tables below
  variable_meanings.csv  visual variable, category, figures, share, example figures
  color_roles.csv        colour word x meaning bucket, mined from the "colour = meaning" clauses of `encoding.color_means`
  clauses.csv            every "left = right" clause of the five encoding fields (raw material for the parts library)
  weaknesses.csv         weakness category, figures, share, quoted examples
  residue.csv            the field texts no rule matched

WHAT IS AUTOMATIC AND WHAT IS NOT
  * legend / markers / model depiction / state marker are enumerated record fields and are only counted here.
  * everything else is KEYWORD MATCHING OVER MODEL-WRITTEN ENGLISH PROSE (`encoding.color_means`, `line_style_means`,
    `shape_means`, `marker_means`, `emphasis`, `weaknesses`). Rules are scoped to the field that describes the variable
    and are not exclusive: one figure usually matches several categories. A convention the record does not mention is
    invisible and a phrasing the patterns miss is lost, so read a count as "how often the records say X", a floor for
    "how often X is drawn". The rules were tuned by reading the residue; `residue.csv` holds what is left.
  * recommended defaults and the anti-pattern list are a human synthesis on top of these tables, not produced here.
"""
import os, re
from ai_common import *

OUT = os.path.join(DISTILL, 'encoding')
COLOR = [
    ('identity', 'one colour per item (class, task, token type, agent, module group, dimension), carried wherever the item appears',
     r'one colou?r per|\bper[- ](class|task|method|token|agent|modality|domain|category|type|dimension|stage|step|speaker|source|module|model|layer|branch|chunk|feature|object|concept)\b|(has|have|gets?|takes?|keeps?) (its|their) own (colou?r|pastel|tint|hue)|\bown (colou?r|pastel|tint|hue)\b|(kept|carried|repeated|reused|recurs?|runs?) (from|through|across|in|on) |same colou?rs? (as|in|on|for|shade|fill|mark|tint)|colou?r (follows|identifies|names|ties|links|pairs|matches)|colou?r[- ]matched|takes the colou?r of|\b(two|three|four|five|six|seven) (task |class |method |agent |token )?colou?rs\b'),
    ('element-type', 'colour tells kinds of element apart: inputs, operations, outputs, data, modules',
     r'\b(inputs?|outputs?|operations?|processing|modules?|data|features?|tokens?|embeddings?|losses|loss terms?|prompts?|parameters?|weights?)\b[^;=]{0,40}=|=[^;=]{0,12}\b(inputs?|outputs?|operations?|modules?|data|losses|loss)\b|by (role|function|content type|type)|fill by role|content type'),
    ('ours-vs-prior', 'the proposed parts against existing, baseline or standard ones',
     r'\b(ours|our (method|model|approach|parts?|modules?|contribution)|proposed|new (parts?|components?|modules?|operators?|block)|contributions?|novel|baselines?|prior (work|methods?)|existing|previous|naive|vanilla|standard|conventional|traditional|other methods)\b'),
    ('trainable-frozen', 'what is trained against what stays frozen',
     r'\b(frozen|trainable|trained|fine-?tuned|learnable|learned|pre-?trained|updated|tuned|randomly initiali[sz]ed|fixed weights?)\b'),
    ('phase', 'training against inference, or one stage against the next',
     r'\b(training|inference|testing|test[- ]time|pre-?training|fine-?tuning|offline|online|stage (one|two|three|1|2|3|i|ii)|phase (one|two|1|2|i|ii)|first stage|second stage|step [1-9]\b)'),
    ('verdict', 'right against wrong, success against failure, safe against harmful',
     r'\b(correct|wrong|incorrect|errors?|fail(ure|s|ed|ing)?|success(ful)?|pass(es|ed)?|harmful|unsafe|safe|positive|negative|accept(ed|s)?|reject(ed|s)?|tick|cross|valid|invalid|good|bad|hallucinat\w+|misaligned|aligned|violat\w+|met|not met|true|false)\b'),
    ('modality', 'text against image, audio, video or another modality',
     r'\bmodalit|\b(text|textual|language|linguistic|image|visual|vision|audio|speech|acoustic|video|point[- ]cloud|depth|tactile)\b[^;=]{0,25}\b(tokens?|branch|stream|path|features?|encoders?|embeddings?|inputs?|side|modality|data)\b'),
    ('scale', 'a sequential or diverging scale for a quantity (heat map, darker = more)',
     r'\b(darker|lighter|deeper|paler) (=|means|for|is|shade|the)|heat ?map|colou?r ?(scale|map|bar|ramp)|sequential|diverging|viridis|jet\b|intensity|gradient (from|of|encodes|scale)|fades? (from|to)|saturation (=|encodes|shows)'),
    ('actor', 'who is speaking or acting: user, model, agent, attacker, expert',
     r'\b(users?|humans?|assistant|agents?|speakers?|attackers?|experts?|teacher|student|server|clients?|robots?|annotators?|players?|judge|critic|actor|planner|verifier)\b'),
    ('highlight', 'one strong colour picks out the key item: evidence span, changed part, error',
     r'\bhighlight\w*|\bemphasi[sz]\w+|\bkey (words?|spans?|evidence|parts?|tokens?|frames?|phrases?)\b|\bmarks? (the|what|where)\b|\baccent\b|\bpicks? out\b|\bdraws? the eye\b|\bevidence\b|\bchanged?\b|\battention\b'),
    ('region-identity', 'a tint only names a region, panel, stage or card, with no further meaning',
     r'\b(panel|region|band|zone|card|section|block|stage|lane|group|column|row|half|tile)s? (tints?|fills?|grounds?|titles?|bands?|headers?|backgrounds?)\b|\btint(s|ed)? (the |each |of the )?(panel|region|band|zone|card|section|block|stage|lane|group|half|tile)|used only for|title (band|strip|bar)|per[- ](panel|card|section|region|stage|tile)'),
    ('per-part', 'three or more parts each get a colour of their own, named one by one (set by the clause count, not by a pattern)', r'(?!x)x'),
    ('none', 'the record says colour carries no code',
     r'\b(no|not|without) (colou?r )?(meaning|coding|code)\b|carr(y|ies) no (meaning|code)|\bdecorative\b|no (clear |consistent )?(colou?r )?(code|coding|meaning)|does not (encode|carry)|not (a |an )?(code|encoding)|colou?r is not'),
]
LINE = [
    ('dashed-frame', 'a dashed box or frame groups parts or marks a scope', r'dashed[^;]{0,40}(frame|box|boxes|outline|outlines|rectangle|rectangles|border|borders|region|regions|container|containers|ring|circle|ellipse|capsule)s?\b'),
    ('dashed-secondary-flow', 'a dashed arrow is a secondary flow: optional, feedback, gradient, training-only, skipped',
     r'(dashed|dotted|dash-dot)[^;=]{0,40}(arrows?|lines?|paths?|links?|edges?|curves?)[^;]{0,80}(optional|auxiliar|secondary|feedback|gradient|back-?prop|loss|updates?|training|inference|skip|residual|condition|not (selected|used|picked|taken)|discard|frozen|virtual|implicit|indirect|supervis|reference|retriev|correspond|alternative|future|previous|weak|soft)|(optional|feedback|gradient|back-?prop|supervision|training[- ]only|inference[- ]only)[^;=]{0,30}(dashed|dotted)'),
    ('dashed-divider', 'a dashed rule separates panels, stages or halves', r'(dashed|dotted)[^;=]{0,24}(rules?|lines?|dividers?|separators?)[^;]{0,40}(separat|split|divid|between)|(separat|split|divid)[^;=]{0,40}(dashed|dotted)'),
    ('zoom-lines', 'thin or dashed lines tie a zoomed view to its source', r'\b(wedge|zoom|leader|call-?out|magnif|enlarg)'),
    ('solid-main-flow', 'solid arrows are the main data flow', r'solid[^;=]{0,30}(=|is|are|carr|mark)[^;]{0,30}(main|data|forward|flow|primary)|(main|data|forward) (flow|path)[^;=]{0,20}solid|\b(thin|black|grey|straight|solid)[^;=]{0,18}arrows? (=|carry|are)[^;]{0,24}(data|main|flow|forward)'),
    ('colour-coded-arrows', 'arrow colour says what kind of flow it is', r'\b(red|blue|green|orange|purple|yellow|pink|teal|cyan|brown|magenta|gold|coloured|colored|colou?r of the)[^;=]{0,18}(arrows?|lines?|edges?|curves?|paths?)\b'),
    ('block-arrows', 'block or hollow arrows mark a hand-over between stages or panels', r'\b(block|hollow|fat|chevron|wide|thick grey|gradient) arrows?\b|\bchevrons?\b'),
    ('weight', 'line weight separates main from minor', r'\b(thick|thicker|bold|heavy|heavier)\b[^;=]{0,24}(=|arrows?|lines?|outline|frame|border)|\bthin(ner)?\b[^;]{0,60}\bthick'),
    ('curved', 'curved or looping arrows mark feedback, iteration or long-range links', r'\bcurved\b|\barcs?\b|\bloop(ing)?\b|\bcircular arrows?\b|\bU-turn\b'),
    ('double-headed', 'double-headed arrows mark exchange, comparison or alignment', r'double-?headed|two-?way|bidirectional|both directions'),
    ('gradient-or-loss', 'a distinct arrow style for losses, gradients or supervision', r'\b(gradient|back-?prop\w*|loss(es)?|supervis\w+|update)\b[^;=]{0,24}(arrows?|flow|path|signal|lines?)|arrows?[^;=]{0,30}\b(gradient|loss|back-?prop\w*|supervis\w+)\b'),
    ('outline-colour', 'outline colour or weight marks a state or a class of box', r'\b(red|green|blue|orange|purple|yellow|bold|thick|coloured|colored)[^;=]{0,14}(outline|outlines|border|borders|frame|frames)\b'),
    ('none', 'the record says line style carries no meaning', r'no line style|carr(y|ies) no meaning|no (meaning|code)\b|only (thin|solid|black)|line style (is|does) not|all (arrows|lines) are solid|no dashed'),
]
SHAPE = [
    ('rounded-box', 'rounded rectangle', r'rounded[^;=]{0,14}(box|boxes|rectangle|rectangles|squares?|frames?|cards?|bars?)'),
    ('cells-or-strip', 'row, strip or grid of small squares or cells', r'(row|strip|grid|column|line|stack|sequence)s? of (small |tiny |coloured |rounded )*(squares?|cells?|boxes|circles?|blocks?|dots?)|small (squares|cells|boxes)|token (squares|cells)|\bcells?\b|\bgrid\b'),
    ('circle-node', 'circle, oval or circled operator', r'\bcircle[sd]?\b|\bovals?\b|\bellipses?\b|\bdots?\b|\bnodes?\b|⊕|⊗'),
    ('stack', 'stack of offset cards, sheets, slabs or layers', r'\b(offset |tilted )?stack(s|ed)?\b|\bslabs?\b|\bsheets?\b|\blayered\b'),
    ('trapezoid', 'trapezoid or funnel', r'trapez\w+|\bfunnel\b|\btapered\b|\bwedge[- ]shaped\b'),
    ('cylinder', 'cylinder (database, storage, dataset)', r'\bcylinders?\b|\bdrum\b|\bdatabase (icon|symbol|shape)\b'),
    ('pill-chip', 'pill, capsule, chip, tag or badge', r'\bpills?\b|\bcapsules?\b|\bchips?\b|\btags?\b|\bbadges?\b|\blozenges?\b'),
    ('bubble', 'speech bubble or call-out', r'\b(speech )?bubbles?\b|\bcall-?outs?\b'),
    ('card-document', 'card, document, page or folded-corner sheet', r'\bcards?\b|\bdocuments?\b|\bfolded[- ]corner\b|\bpages?\b|\bnotepad\b|\bscroll\b|\bclipboard\b'),
    ('icon', 'an icon, logo, avatar or emoji stands for the thing', r'\bicons?\b|\blogos?\b|\bavatars?\b|\bemoji\b|\brobot (head|face|icon)?\b|\bmascot\b|\bpictogram'),
    ('cube-3d', 'cube, cuboid or other pseudo-3D solid', r'\bcubes?\b|\bcuboids?\b|\b3-?d (box|block|slab)\b|\bisometric\b|\bprisms?\b|\bparallelepiped'),
    ('diamond', 'diamond', r'\bdiamonds?\b|\brhomb\w+'),
    ('cloud', 'cloud or thought bubble', r'\bclouds?\b|\bthought\b'),
    ('polygon', 'hexagon, octagon, star, triangle', r'\bhexagons?\b|\boctagons?\b|\bpentagons?\b|\bstars?\b|\btriangles?\b|\bpolygons?\b'),
    ('bars', 'bars standing for vectors, scores or amounts', r'\bbars?\b|\bhistogram'),
    ('block-arrow', 'block arrow as a shape of its own', r'\bblock arrows?\b|\bchevrons?\b'),
    ('none', 'the record says shape carries no meaning', r'no shape|carr(y|ies) no meaning|shape (is|does) not'),
]
MARKER = [
    ('panel-letters', 'letters head the panels', r'\([a-h]\)|letters?[^;=]{0,30}(panels?|head|name)|panel letters|lettered|\b[A-D] (to|and|-) [B-H]\b[^;]{0,20}panels?'),
    ('order-numbers', 'numbers order the steps', r'circled (numbers?|digits?|[0-9])|step numbers?|\bsteps? ?[1-9]\b|head and order|order the (bands|panels|rows|cards|lanes)|numbers?[^;=]{0,24}(order|steps?|stages?|sequence)|(order|number)s? the (steps|stages|turns)|\bnumbered\b|①|\bsteps? [1-9]\b|\b(i|1)\)? (to|and|-) \(?(iv|iii|ii|[2-9])\)?[^;]{0,20}(order|stage|step)'),
    ('item-names', 'subscripts, indices or short ids name items', r'subscripts?|superscripts?|\bind(ex|ices)\b|\bids?\b|name[sd]? (the )?(items?|tokens?|layers?|agents?|samples?|variables?)|\b[a-zA-Z]_?[0-9ijkntT]\b[^;]{0,30}name'),
    ('tick-cross', 'tick and cross (or thumbs) give a verdict', r'\bticks?\b|\bcross(es)?\b|check ?marks?|✓|✗|✔|✘|\bthumbs?\b'),
    ('snowflake-flame', 'snowflake, flame or padlock mark frozen against trained', r'snowflake|flame|\bfire\b|padlock|\block(ed)?\b'),
    ('repeat-count', 'a count such as xN or xL says a block repeats', r'[x×]\s?[NLKMT]\b|[NLKMT]\s?[x×]|\brepeat'),
    ('emoji-state', 'emoji or small faces give a state or a judgement', r'\bemoji\b|\bsmil\w+|\bfaces?\b|\bfrown'),
    ('star', 'a star or asterisk marks the proposed or the best item', r'\bstars?\b|asterisk|★|⭐'),
    ('question-mark', 'a question mark stands for the unknown or the query', r'question marks?|\?'),
    ('inline-values', 'numbers written into the figure as values: scores, sizes, strides, probabilities, gains', r'\b(scores?|values?|strides?|sizes?|counts?|probabilit\w+|percent\w*|dimensions?|shapes?|gains?|accurac\w+)\b|[+-]?\d+(\.\d+)?\s?%'),
    ('titles', 'bold titles or headings name the sections', r'(titles?|headings?|headers?)[^;=]{0,30}(head|name|section|stage|panel|region)|section (titles?|names?)'),
    ('none', 'the record says there are no markers', r'\bno (numbers|markers|letters|step|numbering)|\bnone\b'),
]
EMPH = [
    ('strong-colour', 'the one saturated, dark or red element among pale ones', r'\bthe only\b|\bonly (dark|saturated|coloured|colored|red|bold|filled)|against (the |a )?(pale|grey|white|muted|plain)|\bsaturated\b|\bdark(est)?\b|\bred\b|\bbright\b|colou?r contrast|\bvivid\b'),
    ('size', 'the largest thing on the canvas', r'\b(large|larger|largest|big|bigger|biggest|wide|wider|widest|tall|taller|tallest|enlarged|oversized)\b|fills? (most|half|the)|takes? (up )?(most|half)|\bmost of the (area|canvas|width)'),
    ('centre', 'placed in the centre', r'\b(centre|center|central|middle)\b'),
    ('position-end', 'placed where reading starts or ends', r'top[- ]left|at the top|\bfirst\b|right(most| half| end| edge| side)|far right|\blast\b|bottom[- ]right|at the end|top row'),
    ('bold-type', 'bold type, a title, a banner or a written claim', r'\bbold\b|\btitles?\b|\bheadings?\b|\bbanner\b|\bheadline\b|\bclaim\b|\bcapitals?\b|\bunderlin'),
    ('tinted-ground', 'the proposed part sits on a tint while the rest stays plain', r'\btint(s|ed)?\b|\bshaded\b|coloured (region|box|band|ground|panel)|\bplain\b|stays? (white|plain|grey)|\bpastel\b'),
    ('frame', 'a thick or coloured frame around the key part', r'\bthick\b|\bheavy\b|\bframe[sd]?\b|\boutline[sd]?\b|\bborders?\b|\bboxed\b|\bringed\b|\bhalo\b'),
    ('repetition', 'the same motif repeated so that the change stands out', r'\brepeat\w*|\bsame\b[^;]{0,40}(every|each|all|both)|\brecur\w*|\bmotif\b'),
    ('pictures', 'real pictures, renders or examples carry the eye', r'\bphotos?\b|\bpictures?\b|\bimages?\b|\brenders?\b|\bgaller\w+|\bfilm ?strips?\b|\bthumbnails?\b|\bscreenshots?\b'),
    ('icon-or-mark', 'an icon, a star, an arrow or a call-out points at it', r'\bstars?\b|\bcall-?outs?\b|\bicons?\b|\bbadges?\b|\bemoji\b|\blogos?\b|\bmascot\b|\bticks?\b|\bcross(es)?\b|\bflames?\b'),
    ('numbers', 'a headline number, a gain or a chart', r'\bnumbers?\b|\bpercent\w*|\bscores?\b|\bgains?\b|\bcharts?\b|\bbars?\b|\bplots?\b|[+-]\d'),
    ('arrows', 'big or coloured arrows lead to it', r'\barrows?\b'),
    ('whitespace', 'isolation by white space', r'white ?space|\bisolat\w+|\balone\b|\bempty\b'),
]
WEAK = [
    ('small-text', 'text too small to read at print size', r'\b\d(\.\d)? ?pt\b|\btiny\b|small (text|type|labels?|font|print|lettering)|too small|illegible|hard to read|unreadable|microscopic|barely (readable|legible)|below \d'),
    ('code-unexplained', 'a colour, line or symbol code that the figure does not explain', r'(no|without|lacks?|missing) (a |any )?(legend|key)|not (explained|keyed|defined|labelled as)|unexplained|only in the caption|caption[- ]only|never (explained|defined|keyed)|undefined|not (stated|given|said|explained) in the (figure or )?caption|caption does not (say|explain|define)|(figure|key|legend) (or caption )?does not (say|explain)|not explained in the figure or (the )?caption|has to be (guessed|inferred)|must be (guessed|inferred)|left to the (reader|caption)|\bimplicit\b|not stated'),
    ('colour', 'colour trouble: red against green, tints too close, weak contrast, too many hues', r'red[- /](and |against |versus |vs\.? )?green|colou?r[- ]?(blind|vision)|too many (colou?rs|hues|tints)|(similar|close|near-identical|hard to tell apart)[^;.]{0,24}(colou?rs?|tints?|hues?|shades?|blues?|greens?|greys?)|low contrast|weak contrast|\bcontrast\b|pale[^;.]{0,20}(text|on (white|pale))|same colou?r[^;.]{0,30}(two|different)|reuses?[^;.]{0,20}colou?r|colou?r[^;.]{0,30}(overloaded|reused|two meanings|different meanings|inconsistent)|two meanings|carries two|(hue|colou?r|red|blue|green|orange|yellow|grey)[^;.]{0,40}\bbut\b[^;.]{0,40}(at right|elsewhere|in the|on the)|differ only in (pale )?shades|can be read as a code'),
    ('crowding', 'too much in too little space', r'crowd\w*|\bdense\b|clutter\w*|cramped|packed|\bbusy\b|overload\w*|\btight\b|squeez\w+|too (many|much)'),
    ('arrows', 'arrows that cross, run long, or leave direction or meaning unclear', r'cross(ing|es)?\b[^;.]{0,20}(each other|between|over|arrows?|lines?)|cross(ing|es)\b|tangl\w+|ambiguous|bent arrows?|run close|unclear (where|which|whether|direction|what)|direction[^;.]{0,20}(unclear|not|ambiguous|hard)|arrowheads?|unlabelled (arrows?|lines?)|long (arrows?|lines?|detours?)|detours?|hard to (follow|trace)|which (box|arrow|line)'),
    ('inconsistency', 'the same thing drawn in two ways, or two things in one way', r'inconsisten\w+|not consistent|mismatch\w*|two (drawing )?grammars|two type voices|in some [^;.]{0,30}(and|but) not in others|\bdrawn twice\b|mixed (fonts|styles|notation)|two (fonts|styles|typefaces|notations)|differ(s|ent|ently)[^;.]{0,30}(between|from|across)|not the same|contradict\w*|disagree\w*'),
    ('labels', 'missing labels, undefined symbols or abbreviations', r'abbreviat\w+|acronym\w*|undefined (symbols?|terms?|notation)|unlabelled|no labels?|not labelled|jargon|symbols?[^;.]{0,20}(not|never|un)|notation[^;.]{0,20}(not|never|un)|(not|never) (named|introduced)'),
    ('link-not-drawn', 'a relation the reader needs is left to position, a shared name or the text: no arrow or leader ties the parts',
     r'\bno (arrows?|lines?|leaders?|leader lines?|links?|connectors?)\b[^;.]{0,40}(tie|join|connect|link|show|carr|lead|from|to|between)|\btied\b[^;.]{0,50}\b(only|by name|by position|by the text|to nothing|by title|by colou?r)\b|\b(only|is|are) implied\b|\bimplied (by|only)\b|by (position|adjacency|name|proximity|placement) (only|alone)|\brests? on\b|\bnot (tied|linked|connected|joined)\b|\bno leader\b|has to be read (off|from)|must be read (off|from)|can be read only|only visible from|is not drawn\b[^;.]{0,30}(read|implied)'),
    ('faint', 'marks too faint, thin or pale to notice', r'\bfaint\w*|\bsubtle\b|(nearly|almost|barely) (in)?visible|easy to (miss|overlook)|hard to (see|spot|notice)|\bwashed out\b|too (pale|light|thin)\b|thin and (pale|light|easy)|disappears?'),
    ('content-missing', 'something the argument needs is not on the canvas: the model, the data, the remedy, the numbers, an axis',
     r'\b(is|are) (never|not) (drawn|shown|pictured|depicted)\b|\b(never|not) (drawn|shown)\b|\bno (model|data|samples?|examples?|numbers|values|axis|axes|scale|units?|results?)\b|carr(y|ies) no (numbers|values|name|label|title|letter|axis)|only the problem|without (values|numbers|an axis|axes|units)|have no (axis|values|names?|labels?)|has no (axis|values|name|label|title)'),
    ('placement', 'a label, legend or mark placed away from what it belongs to, or out of line', r'\bsits? (far|away|apart|lower|higher|on top of|over|below|beside|inside|outside|under)\b|\bfar from\b|\baway from\b|misalign\w*|not aligned|\brotated\b|out of line|\boff[- ]centre\b|\buneven (spacing|gaps)'),
    ('wording', 'typos and uneven wording', r'\btypos?\b|misspel\w+|\bspel(led|t)\b|\bword(s|ed|ing)? [^;.]{0,30}differently|\bgrammar\b(?! meet)'),
    ('reading-order', 'no clear place to start or order to follow', r'against (the )?reading direction|against the (usual|convention)|opposite to the usual|right to left|reading order|where to (start|begin)|order[^;.]{0,20}(unclear|not (marked|given|shown)|ambiguous|hard)|no (step|panel) (numbers|letters|markers)|unnumbered|not numbered|entry point|no (obvious|clear) (start|order|path)'),
    ('caption-dependence', 'something is said only in the caption or the text, so the figure cannot be read alone', r'(only|just|solely) (in|from|by|through) the (caption|text|paper)|caption[- ]only|(in|from) the caption (only|alone)|(needs?|relies on|depends on|requires?) the (caption|text|paper)|without the (caption|text|paper)|(named|explained|defined|given|stated|keyed|appears?) only in the (caption|text)|is in the (text|caption), not (in )?the figure|left to the caption|has to be read (off|from) the caption|caption (has to|must|is needed)'),
    ('bitmap-quality', 'pasted bitmaps: low resolution, blur, JPEG edges, mismatched style', r'\bbitmap\w*|\braster\w*|low[- ]res\w*|\bblur\w*|pixelat\w+|\bjpeg\b|compress\w+|screenshot'),
    ('overlap-clipping', 'text or shapes that overlap, touch or are cut off', r'overlap\w*|clipp\w+|cut off|truncat\w+|collid\w+|\btouch(es|ing)?\b|runs? (into|over|off)|spill\w*|bleed\w*'),
    ('balance', 'empty areas or an unbalanced canvas', r'\bempty\b|white ?space|unbalanced|imbalanc\w+|lopsided|wasted|\bblank\b|\b(large|wide|white) margins?\b'),
    ('decoration', 'effects or decoration that carry nothing', r'decorat\w+|redundan\w+|unnecessar\w+|\bshadows?\b|3-?d effect|clip-?art|gratuitous|ornament\w+|\bglow\b|\bbevel'),
    ('typography', 'font trouble: mixed families, outlined or stretched type', r'\bfonts?\b|\bserif\b|typeface|outlined (text|type)|\bstretched\b|\bkerning\b'),
]
FIELDS = [('color_means', 'Colour', COLOR), ('line_style_means', 'Line style', LINE), ('shape_means', 'Shape', SHAPE), ('marker_means', 'Markers', MARKER), ('emphasis', 'Emphasis', EMPH)]
COLOUR_WORDS = r'(light[- ]?|pale[- ]?|dark[- ]?|deep[- ]?|bright[- ]?|mid[- ]?)?(blue|green|red|orange|yellow|purple|pink|grey|gray|black|white|teal|cyan|brown|lavender|peach|cream|mauve|lilac|navy|gold|magenta|olive|beige|violet|coral|turquoise|salmon|indigo)'
BASE = {'gray': 'grey', 'lavender': 'purple', 'mauve': 'purple', 'lilac': 'purple', 'violet': 'purple', 'indigo': 'purple', 'peach': 'orange', 'cream': 'yellow', 'gold': 'yellow', 'beige': 'yellow', 'navy': 'blue',
        'cyan': 'teal', 'turquoise': 'teal', 'magenta': 'pink', 'coral': 'red', 'salmon': 'red', 'olive': 'green'}
CLAUSE = re.compile(r'(?:^|[;.:,]\s+|\band\s+)([^=;.]{2,70}?)\s=\s([^;=]{2,140}?)(?=;|$|,\s+[^=;,]{2,60}\s=\s|\.\s)')


def cats_of(text, rules): return {n for n, _, rx in rules if rx.search(text or '')}


def main():
    data = load(); n = len(data); L = ['# F. Encoding: what colour, line style, shape, markers and emphasis are used to say', '', POOL_NOTE, '',
                                       'Everything in sections 1 to 5 and 7 is keyword matching over the agents\' prose (see the header of the script): categories overlap, and a count is a floor.', '']
    comp = {k: [(nm, w, re.compile(p, re.I)) for nm, w, p in rules] for k, _, rules in FIELDS}; weak_c = [(nm, w, re.compile(p, re.I)) for nm, w, p in WEAK]
    rows_var, residue, clauses = [], [], []
    for d in data:
        enc = d['rec'].get('encoding') or {}
        d['enc'] = {k: cats_of(str(enc.get(k) or ''), comp[k]) for k, _, _ in FIELDS}
        if len([1 for m in CLAUSE.finditer(str(enc.get('color_means') or '')) if re.search(COLOUR_WORDS, m.group(1), re.I)]) >= 3: d['enc']['color_means'].add('per-part')
        d['weak'] = set(); d['weak_txt'] = [str(w) for w in lst(enc.get('weaknesses'))]
        for w in d['weak_txt']:
            hit = cats_of(w, weak_c); d['weak'] |= hit
            if not hit: residue.append([d['id'], 'weaknesses', w])
        for k, _, _ in FIELDS:
            t = str(enc.get(k) or '')
            if t and not d['enc'][k]: residue.append([d['id'], k, t])
            for m in CLAUSE.finditer(t): clauses.append([d['id'], d['kind'], d['sub'], k, m.group(1).strip(), m.group(2).strip()])
    for i, (k, title, rules) in enumerate(FIELDS, 1):
        cats = sorted((nm for nm, _, _ in rules), key=lambda c: -sum(1 for d in data if c in d['enc'][k]))
        L += [f'## {i}. {title}', '']
        L += ['| category | meaning | figures | share |', '|---|---|---:|---:|']
        for c in cats:
            g = [d for d in data if c in d['enc'][k]]; w = next(w for nm, w, _ in rules if nm == c)
            L.append(f'| `{c}` | {w} | {len(g)} | {pct(len(g), n)} |'); rows_var.append([k, c, w, len(g), round(len(g) / n, 3), ' '.join(d['id'] for d in g[:6])])
        L += ['', f'Figures no rule matched: {sum(1 for d in data if not d["enc"][k])}.', '']
        L += share_table(data, [c for c in cats if c != 'none'][:10], lambda d, k=k: d['enc'][k], title=f'{title} by kind and sub-field')
        if k == 'color_means':
            per = C(len(d['enc'][k] - {'none'}) for d in data)
            L += ['Colour codes per figure (how many of the categories above one figure uses at once): ' + ', '.join(f'{a}: {pct(b, n)}' for a, b in sorted(per.items())), '']
            cw = re.compile(COLOUR_WORDS, re.I); buckets = [nm for nm, _, _ in COLOR if nm != 'none']; tabc = collections.defaultdict(C)
            for cid, _, _, f, lhs, rhs in clauses:
                if f != 'color_means': continue
                words = {BASE.get(m.group(2).lower(), m.group(2).lower()) for m in cw.finditer(lhs)}
                for b in cats_of(rhs, comp[k]) - {'none', 'identity', 'region-identity', 'element-type'}:
                    for w_ in words: tabc[w_][b] += 1
            cols = ['ours-vs-prior', 'trainable-frozen', 'phase', 'verdict', 'modality', 'actor', 'highlight', 'scale']
            L += ['### Which colour word is given which meaning', '',
                  'From the clauses written as "colour = meaning" (' + str(sum(1 for c in clauses if c[3] == 'color_means')) + ' clauses). A cell is the number of clauses in which the colour word on the left '
                  'meets a meaning of that kind on the right; it does not say which side of the contrast the colour takes (see the split below).', '']
            L += md_table(['colour'] + cols + ['total'], [[w_] + [tabc[w_][b] for b in cols] + [sum(tabc[w_][b] for b in cols)] for w_ in sorted(tabc, key=lambda w_: -sum(tabc[w_].values()))][:14])
            split = [('trained', r'\b(trainable|trained|fine-?tuned|learnable|updated|tuned)\b', 'frozen', r'\b(frozen|fixed|pre-?trained)\b'),
                     ('right', r'\b(correct|success\w*|pass\w*|safe|valid|accept\w*|aligned|met)\b', 'wrong', r'\b(wrong|incorrect|errors?|fail\w*|harmful|unsafe|invalid|reject\w*|misaligned|hallucinat\w+|violat\w+|not met)\b'),
                     ('ours', r'\b(ours|our|proposed|new|novel)\b', 'prior', r'\b(baselines?|prior|existing|previous|naive|vanilla|standard|conventional|traditional)\b')]
            L += ['### Which colour takes which side', '']
            for a, ra, b, rb in split:
                ca, cb = C(), C()
                for cid, _, _, f, lhs, rhs in clauses:
                    if f != 'color_means': continue
                    words = {BASE.get(m.group(2).lower(), m.group(2).lower()) for m in cw.finditer(lhs)}
                    ia, ib = bool(re.search(ra, rhs, re.I)), bool(re.search(rb, rhs, re.I))
                    if ia and not ib: ca.update(words)
                    if ib and not ia: cb.update(words)
                L += [f'- **{a}**: ' + (', '.join(f'{w_} {v}' for w_, v in ca.most_common(6)) or '-') + f'; **{b}**: ' + (', '.join(f'{w_} {v}' for w_, v in cb.most_common(6)) or '-')]
            L += ['']
            write_csv(os.path.join(OUT, 'color_roles.csv'), ['colour'] + buckets, [[w_] + [tabc[w_][b] for b in buckets] for w_ in sorted(tabc, key=lambda w_: -sum(tabc[w_].values()))])
    # ---- 6. enumerated
    L += ['## 6. Legend, model depiction, state marker (enumerated fields)', '']
    for sec, k, t in (('layout', 'legend', 'Legend'), ('style', 'model_depiction', 'How the model is drawn'), ('style', 'state_marker', 'Trainable / frozen marker')):
        vals = [a for a, _ in C(str(d['rec'][sec].get(k)) for d in data).most_common(9)]
        L += share_table(data, vals, lambda d, sec=sec, k=k: {str(d['rec'][sec].get(k))}, title=t)
    cl = corpus_share('legend'); cf = corpus_share('frozen_fire')
    L += [f'Pre-screen on the corpus: a legend in {100 * cl.get("True", (0, 0))[0]:.0f}% of the designed figures, a snowflake / flame marker in {100 * cf.get("True", (0, 0))[0]:.0f}%.', '']
    # ---- 7. weaknesses
    wcats = sorted((nm for nm, _, _ in WEAK), key=lambda c: -sum(1 for d in data if c in d['weak'])); nw = sum(len(d['weak_txt']) for d in data)
    L += ['## 7. Weaknesses the records name (these are figures rated good)', '', f'{nw} weakness statements, {nw / n:.1f} per figure. They are what a careful reader finds wrong in good figures: the raw list for the anti-pattern step.', '',
          '| category | meaning | figures | share |', '|---|---|---:|---:|']
    wrows = []
    for c in wcats:
        g = [d for d in data if c in d['weak']]; w = next(w for nm, w, _ in WEAK if nm == c); rx = next(rx for nm, _, rx in weak_c if nm == c)
        ex = [t for d in g for t in d['weak_txt'] if rx.search(t)][:4]
        L.append(f'| `{c}` | {w} | {len(g)} | {pct(len(g), n)} |'); wrows.append([c, w, len(g), round(len(g) / n, 3), ' || '.join(ex)])
    L += ['', f'Statements no rule matched: {sum(1 for r in residue if r[1] == "weaknesses")} of {nw}.', '']
    L += share_table(data, wcats[:10], lambda d: d['weak'], title='Weaknesses by kind and sub-field')
    write_md(os.path.join(OUT, 'encoding.md'), L)
    write_csv(os.path.join(OUT, 'variable_meanings.csv'), ['field', 'category', 'meaning', 'figures', 'share', 'examples'], rows_var)
    write_csv(os.path.join(OUT, 'clauses.csv'), ['id', 'kind', 'subfield', 'field', 'left', 'right'], clauses)
    write_csv(os.path.join(OUT, 'weaknesses.csv'), ['category', 'meaning', 'figures', 'share', 'examples'], wrows)
    write_csv(os.path.join(OUT, 'residue.csv'), ['id', 'field', 'text'], residue)
    print(f'{n} figures -> {OUT}/encoding.md; {len(clauses)} clauses; residue {len(residue)} texts ({dict(C(r[1] for r in residue))})')


if __name__ == '__main__':
    main()
