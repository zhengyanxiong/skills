#!/usr/bin/env python3
"""Mine CANDIDATE reusable vector parts out of the author-source SVGs of the
"good architecture diagram" subset of the corpus (STEP 5b of the skill build).

WHAT IT PRODUCES
    A *pool* of small standalone SVG snippets -- icons/pictograms, shape idioms
    (cylinders, stacked cards, chips, queues, clouds, people, servers), step
    badges, arrowheads, legend blocks, container-title styles and connector
    styles -- plus thumbnails and printed contact sheets so that other agents
    can name / categorise / dedupe them visually.  This script deliberately
    does NOT name or classify anything semantically; every label it writes is a
    mechanical `heuristic` tag.

PIPELINE
    1. select figures   rows of the corpus index with type == diagram,
                        subtype == architecture, aesthetic == good and a
                        non-empty `src_svgs` (one figure may have several
                        panel files separated by '|').
    2. parse            lxml walk of each source SVG.  Ancestor transforms are
                        composed into a CTM per element, presentation
                        attributes (fill/stroke/stroke-width/dasharray/opacity/
                        fill-rule/font-*) are inherited down, paths are
                        flattened (beziers sampled) so every drawable gets an
                        accurate bbox in ROOT USER UNITS.
    3. print scale      the source SVG is usually 2-4x larger than the printed
                        figure.  scale = style.size.w / viewBox width (from the
                        index `style` JSON, measured at print size), so every
                        threshold below can be expressed in PRINT POINTS.
                        Multi-panel figures pick the row/column arrangement
                        whose combined aspect best matches the printed aspect.
    4. classify         text | box | connector | image | small   (see THRESHOLDS)
    5. cluster          `small` elements whose bboxes -- grown by CLUSTER_PAD_PT
                        -- intersect are unioned into candidate parts.
    6. detectors        badge / cylinder / stacked / arrowhead / legend /
                        container-title / connector-style, each emitting extra
                        candidates tagged with that `heuristic`.
    7. export           one standalone SVG per candidate under <out>/svg/,
                        attributes resolved, transforms baked, clip-paths and
                        @font-face blocks dropped.
    8. dedupe           (a) geometry: path points normalised into a unit box,
                        rounded to 2 decimals, hashed;  (b) visual: 16x16 dHash
                        of the thumbnail, grouped by Hamming distance.
                        One representative per group; `occurrences` and
                        `sources` record how many figures used it -- frequency
                        is the main signal of which parts matter.
    9. review assets    <out>/thumbs/<id>.png  (~120x120, Chromium-rendered)
                        <out>/sheets/sheet_NNN.png + .json  (6x5 = 30 tiles)
                        <out>/sheets/top_by_occurrence.png  (60 most frequent)
   10. reports          candidates.jsonl, bitmap_icons.jsonl, summary.md

THRESHOLDS (all in PRINT points unless noted; edit the TH dict below)
    box            axis-aligned rect-like, both dims >= 20
    connector      stroked, unfilled, open, polyline length >= 25, or bbox
                   aspect >= 4 with long side >= 25
    cluster pad    1.5   (bboxes grown by this before the intersection test)
    candidate keep long side 4..90, aspect 0.25..4, >= 2 elements or 1 with curves
    hint text      nearest text within 8 of the bbox (plus any text inside it)
    badge          <= 14 long side, single digit/letter/circled glyph inside
    stacked        >= 2 same-size boxes offset by 1.5..8
    arrowhead      filled, <= 12 long side, <= 6 corners, touching a connector end
    legend         swatch <= 20 with a text within 12 to its right, >= 2 aligned,
                   inside the bottom 25% or right 25% of the figure
    container      box >= 60 wide, dashed or grey stroke, title text at its top
    per figure     at most 80 candidates per source file

SELECTING WHICH FIGURES TO MINE  (--select, comma-separated, first match wins)
    arch-good-src  DEFAULT, the original pool: subtype architecture, aesthetic
                   good, author source SVG(s).
    diagram-src    every type == 'diagram' row with an author source SVG, all
                   subtypes, every aesthetic except 'discard'.
    arch-pdf       architecture rows with NO author source -- the figure SVG
                   extracted from the paper PDF, already at print size (scale 1).
    topology-pdf   the same for subtype == 'topology' (hardware/network icons
                   concentrate in topology figures).

RERUN
    # the original pool
    python3 figgenie-paper-diagram/scripts/distill/extract_parts.py \
        --index lab/extracted/corpus_index.csv \
        --semantics lab/extracted/corpus_semantics.jsonl \
        --extracted-dir lab/extracted \
        --out <scratchpad>/step5/candidates

    # the extended sweep for the icon families the first pool lacked
    python3 figgenie-paper-diagram/scripts/distill/extract_parts.py \
        --select diagram-src,arch-pdf,topology-pdf \
        --exclude-ids-from <scratchpad>/step5/candidates/candidates.jsonl \
        --skip-heuristics connector-style,container-title,legend \
        --missing-sheets --out <scratchpad>/step5/candidates_ext

    Useful flags:  --ids asplos25-002,asplos25-031:1   --limit 20
                   --jobs N   --no-render (skip Chromium; skips visual dedupe
                   and sheets)   --phash-dist N   --missing-sheet-cap N
    --exclude-ids-from takes a previous run's candidates.jsonl: those figures
    are skipped and that run's geometry hashes plus every thumbnail in its
    sibling thumbs/ are used as a dedupe reference, so already-reviewed parts
    do not come back.
    --missing-sheets additionally groups the pool by the MISSING_TYPES keyword
    table (defined below) into sheets/missing_<type>_NN.png + .json.
    The output directory is rewritten in place; svg/ thumbs/ sheets/ are cleared
    at the start of a full run.
"""

import argparse
import copy
import csv
import hashlib
import json
import math
import os
import re
import shutil
import sys
import time
from collections import Counter, defaultdict

from lxml import etree

try:
    import numpy as np
except ImportError:  # numpy is required for the visual dedupe / sheets
    np = None

csv.field_size_limit(10 ** 9)

SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_NS = 'http://www.w3.org/1999/xlink'

# ---------------------------------------------------------------------------
# thresholds (print points)
# ---------------------------------------------------------------------------
TH = {
    'box_min_pt': 20.0,
    'connector_min_len_pt': 25.0,
    'connector_aspect': 4.0,
    'cluster_pad_pt': 1.5,
    'cand_min_pt': 4.0,
    'cand_max_pt': 90.0,
    'cand_aspect_lo': 0.25,
    'cand_aspect_hi': 4.0,
    'cand_max_elements': 30,
    'link_fragment_min_pt': 12.0,
    'link_fragment_aspect': 2.5,
    'hint_text_pt': 8.0,
    'hint_wide_pt': 20.0,
    'badge_max_pt': 14.0,
    'stack_off_lo_pt': 1.5,
    'stack_off_hi_pt': 8.0,
    'stack_size_tol': 0.08,
    'arrow_max_pt': 12.0,
    'arrow_touch_pt': 4.0,
    'legend_swatch_max_pt': 20.0,
    'legend_gap_pt': 12.0,
    'container_min_w_pt': 60.0,
    'container_min_h_pt': 35.0,
    'container_min_inner': 2,
    'max_cands_per_file': 80,
    'max_arrowheads_per_file': 6,
    'max_connstyles_per_file': 8,
    'max_stacked_per_file': 8,
    # tuned after looking at the first contact sheets (see summary.md):
    # a cluster made only of rectangle-like elements is a node box / table cell /
    # bar, not an icon, unless there are >= 3 of them (grids, chips, queues).
    'cluster_need_nonrect': True,
    'rect_thresh': 0.85,
}

SKIP_TAGS = {'clipPath', 'mask', 'defs', 'symbol', 'metadata', 'title', 'desc',
             'style', 'script', 'filter', 'linearGradient', 'radialGradient',
             'pattern', 'marker'}
DRAW_TAGS = {'path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline',
             'image', 'text'}
INHERIT = ('fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap',
           'stroke-linejoin', 'fill-rule', 'opacity', 'fill-opacity',
           'stroke-opacity', 'font-size', 'font-family', 'font-weight',
           'font-style')

NUM_TOKEN = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
PATH_TOKEN = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)')
TRANSFORM_RE = re.compile(r'(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)')
CIRCLED_RE = re.compile(r'[①-⑳❶-❿Ⓐ-ⓩ➀-➓➊-➓⓪]')
# `<latexit sha1_base64="...">` blobs are embedded by latex figure tooling and
# are pure noise in hint_text
JUNK_TEXT_RE = re.compile(r'<latexit[^>]*>|sha1_base64="[^"]*"|[A-Za-z0-9+/]{40,}={0,2}')
BADGE_TEXT_RE = re.compile(r'^[\s]*([0-9]|[A-Za-z]|[①-⑳❶-❿Ⓐ-ⓩ➀-➓])[\s]*$')
MONO_RE = re.compile(r'Mono|Courier|Consolas|Menlo|Monaco|typewriter|txtt|Inconsolata|Source ?Code|Fira ?Code|CMTT|LMMono|Nimbus ?Mon|pcr', re.I)
SERIF_RE = re.compile(r'Times|Roman|Nimbus ?Rom|Libertine|Georgia|Cambria|Palatino|Garamond|CM(R|BX|TI|MI|SY|EX)|Computer ?Modern|Latin ?Modern|LMRoman|Charter|Minion|Serif|STIX|Termes|Utopia|Century|Schoolbook|ptm|txr', re.I)
FONTFACE_FAM_RE = re.compile(r'@font-face\s*{[^}]*?font-family\s*:\s*"?([^";}]+)"?', re.S)

TUNING_NOTES = """
## What was tuned (and why) after looking at the first contact sheets

Everything below was changed after rendering sheets and reading them; the
starting point was the literal spec thresholds.

1. **Visual dedupe hash.**  A 16x16 dHash was useless: most thumbnails are a
   thin drawing on white, so unrelated sparse parts had near-identical gradient
   hashes and collapsed into one group (an arrowhead, a legend row and three
   coloured bars ended up "the same part").  Replaced with a 16x16 **ink
   occupancy silhouette** computed by thresholding at 128x128 and max-pooling,
   so hairlines survive the downsample.  The Hamming tolerance is additionally
   **scaled by ink mass** (`min(8, 0.30 * min(ink_a, ink_b))`) so nearly empty
   thumbnails must match almost exactly.
2. **Silhouettes are measured on the white render.**  Invisible white-on-white
   parts are re-rendered on light grey *afterwards* (25 of them) purely for
   review; hashing the grey render made every cell "ink" and merged them all.
3. **Representative choice.**  The largest member of a group, but never one
   whose own label differs from the group's label -- otherwise an `arrowhead`
   group could be illustrated by the biggest thing that merged into it.
4. **Icon clusters.**  Added a 30-element cap (bigger clusters are whole
   sub-panels, not parts) and a rule that a cluster of only 1-2 rectangle-like
   elements is rejected: those are node boxes, bars and table cells, and they
   flooded the pool.  3+ rectangles are kept (grids, chips, queues).
5. **Arrowheads.**  A 3-6 corner filled shape also matches small solid
   rectangles, which dominated the "most frequent" sheet.  Added a polygon
   area / bbox area test (`0.15 <= ratio <= 0.80`) so bars and squares are
   rejected while triangles, chevrons and diamonds pass.  Arrowheads dedupe on
   an **orientation-free** shape key (rotated so the tip points right, rounded
   to 0.1), which collapsed 388 raw heads into ~14 distinct shapes.
6. **Cylinders.**  The first version labelled circles, check marks, CPU-chip
   icons, stadium bars and outlined glyph runs as cylinders.  Now requires: a
   curve, at most 2 subpaths, aspect 0.5-2.2, two straight vertical sides, full
   width at mid height (rejects hooks/bent arrows), no full-width straight edge
   (rejects rounded rectangles) and a cap depth between 0.04w and 0.40w
   (rejects stadium/pill shapes, whose cap depth is exactly w/2).
7. **Stacked.**  Nested/containing pairs are rejected (that is a double border,
   not a stack) and the offset must be diagonal -- `dx` and `dy` both >= 1.5pt
   -- otherwise adjacent boxes in a grid all read as stacks.  Capped at 8 per
   source file so one Tetris-like figure cannot flood the pool.
8. **Container titles.**  Originally fired on every labelled node box.  Now the
   box must be >= 60x35pt, its stroke dashed or *mid* grey (a plain black
   outline no longer counts as "grey"), it must actually contain >= 2 other
   elements, and the title must be at least 2 characters (a step badge is not a
   title).  The exported crop is a ~110x34pt window on the top edge that slides
   right to catch top-centre/top-right titles -- a full-width crop of a 160pt
   container rendered the title unreadably small.
9. **Style records skip the visual dedupe.**  Every connector sample looks like
   "a horizontal line" and every container corner like "an L", so they were all
   collapsing into a single group (and losing their representatives).  They
   dedupe on a bucketed **style key** instead: colour family, 0.5pt width
   bucket, dash class, head presence and 3pt head-length bucket for connectors;
   colour family, width, dash class, fill, corner radius, title position and
   font size for containers.
10. **hint_text** strips `<latexit sha1_base64=...>` blobs, which some LaTeX
    figure tooling embeds as invisible text.

## Known failure modes for reviewers

- **Outlined text.**  Several TikZ/PDF sources convert type to vector outlines,
  so whole words arrive as one path.  They land in the `icon` pool and look
  like lettering; the multi-subpath test keeps them out of `cylinder` but not
  out of `icon`.
- **Bitmap icons are NOT extracted.**  `<image>` elements are only recorded in
  `bitmap_icons.jsonl` (figure, size, position, nearby text).
- **Proximity clustering** merges an icon with whatever sits within 1.5pt of
  it, so some candidates are "box + arrow + glyph" mini-flows rather than a
  single pictogram.
- **`legend`** fires on any small shape with a text to its right inside the
  bottom/right quadrant, so it also catches ordinary labelled nodes there.
- **Colour is not part of the geometry key**, so one representative can stand
  for the same shape in several palettes -- `colors_all` lists every colour
  seen in the group.
- **Multi-panel figures** share one printed width, so per-panel pt sizes are
  inferred from the best-fitting row/column arrangement (see the scale table).
"""

# ---------------------------------------------------------------------------
# "missing type" keyword table (STEP 5b follow-up)
#
# Reviewers of the first pool listed the pictogram families it lacked.  Each
# entry is (type name, regex).  A candidate is tagged with a type when the
# regex matches any of: hint_text, hint_wide (all text within 20 print-pt),
# the figure caption, or the source file name.  Matching is case-insensitive
# and word-boundary anchored, so 'key' does not fire on 'keyboard'/'monkey'
# and 'tape' does not fire on 'tapestry'.  These are RECALL aids for the
# reviewers, not classifications -- a hit only means "text near this part
# mentions the concept".
# ---------------------------------------------------------------------------
MISSING_TYPES = [
    ('lock-security', r'\b(lock|locks|locked|padlock|unlock|shield|shields|key|keys|keypair|certificate|certificates|cert|certs|attestation|attest|encrypt\w*|decrypt\w*|secure|security|tee|enclave|sgx|sev|tdx|trusted)\b'),
    ('gear-settings',  r'\b(gear|gears|cog|cogs|setting|settings|config|configure|configuration|knob|knobs|tuning|tuner|policy engine)\b'),
    ('magnifier-search', r'\b(search|searching|magnif\w*|lookup|look-?up|probe|probing|inspect|inspector|query engine|find|discovery|scan|scanner|scanning)\b'),
    ('warning',        r'\b(warn|warning|alert|alerts|alarm|error|errors|fault|faults|failure|failures|fail|failed|exception|violation|anomaly|anomalies|attention|caution|danger|risk|invalid|miss|misses)\b'),
    ('check-mark',     r'\b(check|checked|checkmark|tick|valid|verified|verify|verification|correct|success|successful|ok|pass|passed|accept|accepted|approved|hit|hits|yes)\b'),
    ('server-rack',    r'\b(server|servers|rack|racks|cabinet|tower|blade|blades|host|hosts|machine|machines|node|nodes|datacenter|data ?cent(er|re)|cluster|pod|pods|chassis)\b'),
    ('nic',            r'\b(nic|nics|smartnic|smart-?nic|dpu|network (card|adapter|interface)|rnic|ib|infiniband|rdma|ethernet|port|ports|link|links|uplink|downlink)\b'),
    ('router-switch',  r'\b(router|routers|switch|switches|switching|tor|spine|leaf|gateway|gateways|proxy|load ?balancer|lb|ingress|egress|firewall|middlebox|fabric)\b'),
    ('dram-module',    r'\b(dram|dimm|dimms|hbm|hbm\d|ddr\d?|lpddr|sdram|memory module|main memory|mem ?ctrl|memory controller|nvdimm|cxl memory|rank|ranks|bank|banks)\b'),
    ('storage-flash',  r'\b(ssd|ssds|nvme|hdd|hdds|disk|disks|flash|nand|zns|zn|tape|tapes|drive|drives|storage|nvm|optane|pmem|persistent memory|block device|blob store)\b'),
    ('chip-gpu',       r'\b(gpu|gpus|cuda|sm|sms|tensor core|tensor cores|nvlink|a100|h100|v100|h800|a10|rtx|streaming multiprocessor)\b'),
    ('chip-cpu',       r'\b(cpu|cpus|core|cores|socket|sockets|numa|x86|arm|risc-?v|processor|processors|host cpu|vcpu|vcpus)\b'),
    ('chip-tpu',       r'\b(tpu|tpus|npu|npus|accelerator|accelerators|asic|asics|systolic|pe array|ipu|xpu|trainium|inferentia)\b'),
    ('chip-fpga',      r'\b(fpga|fpgas|lut|luts|bitstream|verilog|rtl|hls|xilinx|altera|alveo|smart ?fpga)\b'),
    ('packet-message', r'\b(packet|packets|message|messages|msg|msgs|envelope|mail|frame|frames|datagram|rpc|rpcs|request|requests|response|responses|payload|header|headers|flit|flits)\b'),
    ('token-squares',  r'\b(token|tokens|tokenizer|prompt|prompts|kv ?cache|embedding|embeddings|sequence|seq|context window|prefill|decode)\b'),
    ('transformer-block', r'\b(transformer|attention|self-?attention|mha|ffn|mlp|layernorm|layer ?norm|rmsnorm|softmax|qkv|q ?k ?v|encoder|decoder|block|blocks|head|heads|layer|layers)\b'),
    ('table-grid',     r'\b(table|tables|spreadsheet|matrix|matrices|grid|row|rows|column|columns|cell|cells|tuple|tuples|schema|index|indices|entry|entries)\b'),
    ('file-folder',    r'\b(file|files|folder|folders|directory|directories|document|documents|doc|docs|log|logs|logging|journal|record|records|dataset|datasets|checkpoint|checkpoints|snapshot|manifest|config file)\b'),
    ('queue-slots',    r'\b(queue|queues|queued|fifo|lifo|buffer|buffers|ring|ringbuffer|slot|slots|pending|backlog|batch queue|work ?queue|task queue|inbox)\b'),
    ('person-user',    r'\b(user|users|client|clients|person|people|admin|admins|administrator|operator|operators|developer|developers|tenant|tenants|attacker|attackers|adversary|analyst|customer|customers|human)\b'),
    ('device-endpoint', r'\b(phone|phones|mobile|smartphone|laptop|laptops|desktop|browser|browsers|tablet|edge device|iot|terminal|workstation|app|apps|frontend|front-?end|ui)\b'),
    ('cloud',          r'\b(cloud|clouds|aws|azure|gcp|s3|ec2|lambda|serverless|public cloud|private cloud|cloud provider|region|availability zone)\b'),
    ('globe-internet',  r'\b(globe|global|internet|www|web|wan|world|earth|geo|cdn|edge network|public network|dns)\b'),
    ('clock-timer',    r'\b(clock|clocks|timer|timers|timeout|timeouts|time|latency|deadline|deadlines|schedule|scheduler|scheduling|epoch|tick|ticks|interval|delay|duration|elapsed)\b'),
    ('battery-power',  r'\b(power|powers|watt|watts|energy|battery|batteries|joule|joules|voltage|dvfs|frequency scaling|tdp|consumption)\b'),
    ('thermal',        r'\b(temperature|thermal|thermometer|heat|hot|cold|warm|cool|cooling|flame|fire|burn|snowflake|frozen|freeze|throttl\w*|degree|celsius)\b'),
    ('dollar-cost',    r'\b(cost|costs|costly|price|prices|pricing|dollar|dollars|usd|budget|budgets|billing|bill|spend|spending|expense|cheap|expensive|\$)'),
]
MISSING_RE = [(name, re.compile(rx, re.I)) for name, rx in MISSING_TYPES]


# where a keyword matched, strongest evidence first: a label touching the part
# is far better evidence than a word somewhere in the figure caption
MATCH_FIELDS = ('hint_text', 'hint_wide', 'icons_hint', 'file_name', 'caption')
MATCH_RANK = {f: i for i, f in enumerate(MATCH_FIELDS)}


def match_missing_types(rec, file_name):
    """-> {type name: field that matched}, strongest field per type."""
    fields = {
        'hint_text': str(rec.get('hint_text') or ''),
        'hint_wide': str(rec.get('hint_wide') or ''),
        'icons_hint': str((rec.get('hint_semantics') or {}).get('icons') or ''),
        'file_name': os.path.basename(file_name or ''),
        'caption': str(rec.get('caption') or ''),
    }
    hits = {}
    for fname in MATCH_FIELDS:
        text = fields[fname]
        if not text.strip():
            continue
        for name, rx in MISSING_RE:
            if name not in hits and rx.search(text):
                hits[name] = fname
    return hits


def pictogram_score(c):
    """How pictogram-like a candidate looks -- used to order the missing-type
    sheets so that actual glyphs come before plain boxes and arrows, which
    ordering by occurrence alone put on top."""
    s = 0.0
    if c['heuristic'] in ('icon', 'cylinder'):
        s += 2.0
    if c.get('has_curve'):
        s += 2.0
    s += min(c.get('n_elements') or 1, 12) * 0.25
    w, h = c['w_pt'], c['h_pt']
    long_, short = max(w, h), min(w, h)
    asp = long_ / max(short, 1e-6)
    if asp <= 2.0:
        s += 1.5
    elif asp <= 3.0:
        s += 0.5
    if 8.0 <= long_ <= 45.0:
        s += 1.5
    elif long_ <= 60.0:
        s += 0.5
    if c.get('n_text'):
        s -= 0.5
    return s


HEURISTIC_ORDER = ['icon', 'badge', 'cylinder', 'stacked', 'arrowhead', 'legend',
                   'container-title', 'connector-style']
# more specific wins when identical geometry shows up under two labels
HEURISTIC_RANK = {h: i for i, h in enumerate(
    ['arrowhead', 'badge', 'cylinder', 'stacked', 'legend', 'container-title',
     'connector-style', 'icon'])}


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def mat_mul(m, n):
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def parse_transform(s):
    m = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    if not s:
        return m
    for name, args in TRANSFORM_RE.findall(s):
        v = [float(x) for x in NUM_TOKEN.findall(args)]
        try:
            if name == 'matrix' and len(v) == 6:
                t = tuple(v)
            elif name == 'translate':
                t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
            elif name == 'scale':
                t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
            elif name == 'rotate':
                r = math.radians(v[0]); cs, sn = math.cos(r), math.sin(r)
                t = (cs, sn, -sn, cs, 0, 0)
                if len(v) == 3:
                    t = mat_mul(mat_mul((1, 0, 0, 1, v[1], v[2]), t),
                                (1, 0, 0, 1, -v[1], -v[2]))
            elif name == 'skewX':
                t = (1, 0, math.tan(math.radians(v[0])), 1, 0, 0)
            elif name == 'skewY':
                t = (1, math.tan(math.radians(v[0])), 0, 1, 0, 0)
            else:
                continue
        except (IndexError, ValueError):
            continue
        m = mat_mul(m, t)
    return m


def apply_m(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def scale_of(m):
    return math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0


def mat_str(m):
    return 'matrix(%s)' % ','.join(('%.6g' % v) for v in m)


def _bez3(p0, p1, p2, p3, n=10):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                    u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]))
    return out


def _bez2(p0, p1, p2, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def _arc(p0, rx, ry, phi, large, sweep, p1, n=12):
    """Endpoint -> centre parameterisation, sampled.  Falls back to a line."""
    try:
        if rx == 0 or ry == 0:
            return [p1]
        rx, ry = abs(rx), abs(ry)
        cphi, sphi = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        dx2, dy2 = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
        x1p = cphi * dx2 + sphi * dy2
        y1p = -sphi * dx2 + cphi * dy2
        lam = x1p * x1p / (rx * rx) + y1p * y1p / (ry * ry)
        if lam > 1:
            s = math.sqrt(lam); rx *= s; ry *= s
        num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
        den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
        co = math.sqrt(max(0.0, num / den)) if den else 0.0
        if large == sweep:
            co = -co
        cxp = co * rx * y1p / ry
        cyp = -co * ry * x1p / rx
        cx = cphi * cxp - sphi * cyp + (p0[0] + p1[0]) / 2.0
        cy = sphi * cxp + cphi * cyp + (p0[1] + p1[1]) / 2.0

        def ang(ux, uy, vx, vy):
            d = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
            a = math.acos(max(-1.0, min(1.0, d)))
            return -a if ux * vy - uy * vx < 0 else a

        th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
        dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
        if not sweep and dth > 0:
            dth -= 2 * math.pi
        elif sweep and dth < 0:
            dth += 2 * math.pi
        out = []
        for i in range(1, n + 1):
            t = th1 + dth * i / n
            x = cphi * rx * math.cos(t) - sphi * ry * math.sin(t) + cx
            y = sphi * rx * math.cos(t) + cphi * ry * math.sin(t) + cy
            out.append((x, y))
        return out
    except Exception:
        return [p1]


def parse_path_flat(d, max_pts=1200):
    """-> (subpaths, has_curve); each subpath is (points, closed) already flattened."""
    subs = []
    pts, closed, curve = [], False, False
    cx = cy = sx = sy = 0.0
    px = py = None          # previous control point (for S/T)
    cmd = None
    toks = PATH_TOKEN.findall(d)
    i, n = 0, len(toks)
    total = 0

    def flush():
        nonlocal pts, closed
        if len(pts) > 1:
            subs.append((pts, closed))
        pts, closed = [], False

    while i < n and total < max_pts:
        c, _num = toks[i]
        if c:
            cmd = c
            i += 1
            if cmd in 'Zz':
                closed = True
                flush()
                cx, cy = sx, sy
                pts = [(cx, cy)]
                closed = False
            continue
        if cmd is None:
            cmd = 'L'
        need = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7}.get(cmd.upper(), 2)
        vals = []
        while i < n and not toks[i][0] and len(vals) < need:
            try:
                vals.append(float(toks[i][1]))
            except ValueError:
                vals.append(0.0)
            i += 1
        if len(vals) < need:
            break
        rel = cmd.islower()
        u = cmd.upper()
        if u == 'M':
            if len(pts) > 1:
                flush()
            x, y = vals
            if rel:
                x += cx; y += cy
            cx, cy = sx, sy = x, y
            pts = [(x, y)]
            cmd = 'l' if rel else 'L'
            px = py = None
        elif u == 'L':
            x, y = vals
            if rel:
                x += cx; y += cy
            cx, cy = x, y; pts.append((x, y)); px = py = None
        elif u == 'H':
            x = vals[0] + (cx if rel else 0); cx = x; pts.append((cx, cy)); px = py = None
        elif u == 'V':
            y = vals[0] + (cy if rel else 0); cy = y; pts.append((cx, cy)); px = py = None
        elif u == 'C':
            curve = True
            p = list(zip(vals[0::2], vals[1::2]))
            if rel:
                p = [(a + cx, b + cy) for a, b in p]
            pts.extend(_bez3((cx, cy), p[0], p[1], p[2]))
            px, py = p[1]; cx, cy = p[2]
        elif u == 'S':
            curve = True
            p = list(zip(vals[0::2], vals[1::2]))
            if rel:
                p = [(a + cx, b + cy) for a, b in p]
            c1 = (2 * cx - px, 2 * cy - py) if px is not None else (cx, cy)
            pts.extend(_bez3((cx, cy), c1, p[0], p[1]))
            px, py = p[0]; cx, cy = p[1]
        elif u == 'Q':
            curve = True
            p = list(zip(vals[0::2], vals[1::2]))
            if rel:
                p = [(a + cx, b + cy) for a, b in p]
            pts.extend(_bez2((cx, cy), p[0], p[1]))
            px, py = p[0]; cx, cy = p[1]
        elif u == 'T':
            curve = True
            x, y = vals
            if rel:
                x += cx; y += cy
            c1 = (2 * cx - px, 2 * cy - py) if px is not None else (cx, cy)
            pts.extend(_bez2((cx, cy), c1, (x, y)))
            px, py = c1; cx, cy = x, y
        elif u == 'A':
            curve = True
            x, y = vals[5], vals[6]
            if rel:
                x += cx; y += cy
            pts.extend(_arc((cx, cy), vals[0], vals[1], vals[2], vals[3], vals[4], (x, y)))
            cx, cy = x, y; px = py = None
        total = sum(len(s[0]) for s in subs) + len(pts)
    flush()
    return subs, curve


def bbox_of(points):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_inter(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def bbox_union(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def color_norm(c):
    if not c:
        return None
    c = c.strip().lower()
    if c in ('none', 'transparent'):
        return 'none'
    if c.startswith('#'):
        if len(c) == 4:
            c = '#' + ''.join(ch * 2 for ch in c[1:])
        return c[:7]
    m = re.match(r'rgb\(\s*([\d.]+%?)\s*,\s*([\d.]+%?)\s*,\s*([\d.]+%?)\s*\)', c)
    if m:
        v = []
        for t in m.groups():
            v.append(int(round(float(t[:-1]) * 2.55)) if t.endswith('%') else int(float(t)))
        return '#%02x%02x%02x' % tuple(min(255, max(0, x)) for x in v)
    names = {'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'blue': '#0000ff',
             'green': '#008000', 'gray': '#808080', 'grey': '#808080',
             'orange': '#ffa500', 'yellow': '#ffff00', 'purple': '#800080'}
    if c.startswith('url('):
        return 'url'
    return names.get(c, c)


def hue_family(hexc):
    """Coarse colour bucket -- used so that connector STYLES dedupe across
    palettes instead of producing one entry per figure-specific hex."""
    try:
        r, g, b = (int(hexc[1:3], 16) / 255, int(hexc[3:5], 16) / 255,
                   int(hexc[5:7], 16) / 255)
    except (ValueError, IndexError, TypeError):
        return 'other'
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if mx < 0.14:
        return 'black'
    if d < 0.09 or (d / mx if mx else 0) < 0.16:
        return 'white' if mx > 0.93 else 'grey'
    if mx == r:
        h = (60 * ((g - b) / d) + 360) % 360
    elif mx == g:
        h = 60 * ((b - r) / d) + 120
    else:
        h = 60 * ((r - g) / d) + 240
    for lim, name in ((15, 'red'), (45, 'orange'), (70, 'yellow'), (170, 'green'),
                      (200, 'cyan'), (260, 'blue'), (300, 'purple'), (345, 'pink')):
        if h < lim:
            return name
    return 'red'


def dash_class(dash_pt):
    if not dash_pt:
        return 'solid'
    try:
        v = [float(x) for x in NUM_TOKEN.findall(str(dash_pt))]
    except ValueError:
        return 'dashed'
    if not v:
        return 'solid'
    on = v[0]
    return 'dotted' if on <= 1.6 else ('dashed-short' if on <= 4.0 else 'dashed-long')


def bucket(v, step):
    try:
        return round(float(v) / step) * step
    except (TypeError, ValueError):
        return None


def style_key(prefix, parts):
    return prefix + hashlib.sha1(repr(parts).encode()).hexdigest()[:16]


def arrow_shape_key(el):
    """Orientation-free shape key: rotate so the tip points right, normalise,
    round to 0.1.  Collapses the same head drawn up/down/left/right."""
    pts = [(round(x, 3), round(y, 3)) for x, y in el.pts]
    uniq = sorted(set(pts))
    if len(uniq) < 3:
        return None
    cx = sum(p[0] for p in uniq) / len(uniq)
    cy = sum(p[1] for p in uniq) / len(uniq)
    tip = max(uniq, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    a = -math.atan2(tip[1] - cy, tip[0] - cx)
    ca, sa = math.cos(a), math.sin(a)
    rot = [((p[0] - cx) * ca - (p[1] - cy) * sa, (p[0] - cx) * sa + (p[1] - cy) * ca)
           for p in uniq]
    xs = [p[0] for p in rot]; ys = [p[1] for p in rot]
    w = max(max(xs) - min(xs), 1e-6); h = max(max(ys) - min(ys), 1e-6)
    norm = sorted((round((x - min(xs)) / w, 1), round((y - min(ys)) / h, 1)) for x, y in rot)
    return style_key('ah:', (len(uniq), norm, bool(el.fill and el.fill != 'none')))


def is_grey(hexc):
    try:
        r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    except (ValueError, IndexError, TypeError):
        return False
    return max(r, g, b) - min(r, g, b) < 22


# ---------------------------------------------------------------------------
# element model
# ---------------------------------------------------------------------------
class El:
    __slots__ = ('tag', 'node', 'ctm', 'bbox', 'pts', 'closed', 'curve', 'fill',
                 'stroke', 'sw', 'dash', 'opacity', 'text', 'font_size', 'style',
                 'cls', 'idx', 'plen', 'nsub')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def w(self):
        return self.bbox[2] - self.bbox[0]

    def h(self):
        return self.bbox[3] - self.bbox[1]


def tagname(el):
    t = el.tag
    return t.rsplit('}', 1)[-1] if isinstance(t, str) else ''


def style_lookup(node, name, inherited):
    v = node.get(name)
    st = node.get('style')
    if st:
        m = re.search(r'(?:^|;)\s*' + re.escape(name) + r'\s*:\s*([^;]+)', st)
        if m:
            v = m.group(1).strip()
    return v if v is not None else inherited.get(name)


def fnum(v, default=0.0):
    if v is None:
        return default
    m = NUM_TOKEN.search(str(v))
    return float(m.group(0)) if m else default


def rect_points(x, y, w, h, rx=0.0, ry=0.0):
    if rx <= 0 and ry <= 0:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], True, False
    rx = min(rx or ry, w / 2.0); ry = min(ry or rx, h / 2.0)
    pts = []
    for cx, cy, a0 in ((x + w - rx, y + ry, -90), (x + w - rx, y + h - ry, 0),
                       (x + rx, y + h - ry, 90), (x + rx, y + ry, 180)):
        for i in range(9):
            a = math.radians(a0 + i * 10)
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    pts.append(pts[0])
    return pts, True, True


def ellipse_points(cx, cy, rx, ry, n=32):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n))
            for i in range(n + 1)], True, True


def text_local_boxes(node, fs):
    """-> (list of local-space bboxes, joined string)."""
    boxes, chunks = [], []
    tspans = [c for c in node.iter() if tagname(c) == 'tspan']
    items = tspans if tspans else [node]
    for ts in items:
        txt = ''.join(ts.itertext()) if ts is node else (ts.text or '')
        if ts is not node:
            txt = ts.text or ''
        s = fnum(ts.get('font-size'), fs) or fs
        xs = [float(v) for v in NUM_TOKEN.findall(ts.get('x') or '')]
        ys = [float(v) for v in NUM_TOKEN.findall(ts.get('y') or '')]
        if not xs or not ys:
            continue
        x0, x1 = min(xs), max(xs)
        y0 = min(ys)
        # last glyph advance ~0.55em; fall back to a crude per-char estimate
        x1 = x1 + 0.55 * s if len(xs) > 1 else x1 + 0.55 * s * max(1, len(txt.strip()))
        boxes.append((x0, y0 - 0.80 * s, x1, y0 + 0.24 * s))
        if txt:
            chunks.append(txt)
    return boxes, ''.join(chunks)


def walk(root, defs_by_id):
    """Yield El for every drawable, with CTM + resolved presentation attributes."""
    out = []
    idx = [0]

    def rec(node, ctm, inh, depth, use_depth):
        for child in node:
            t = tagname(child)
            if not t or t in SKIP_TAGS:
                continue
            m = mat_mul(ctm, parse_transform(child.get('transform')))
            style = dict(inh)
            for k in INHERIT:
                v = style_lookup(child, k, inh)
                if v is not None:
                    style[k] = v
            if t == 'g' or t == 'a' or t == 'svg':
                rec(child, m, style, depth + 1, use_depth)
                continue
            if t == 'use':
                if use_depth > 3:
                    continue
                href = child.get('{%s}href' % XLINK_NS) or child.get('href') or ''
                tgt = defs_by_id.get(href.lstrip('#'))
                if tgt is None:
                    continue
                ux, uy = fnum(child.get('x')), fnum(child.get('y'))
                m2 = mat_mul(m, (1, 0, 0, 1, ux, uy))
                holder = etree.Element('g')
                holder.append(copy.deepcopy(tgt))
                rec(holder, m2, style, depth + 1, use_depth + 1)
                continue
            if t not in DRAW_TAGS:
                continue
            el = build_el(child, t, m, style, idx)
            if el is not None:
                out.append(el)

    rec(root, (1, 0, 0, 1, 0, 0), {}, 0, 0)
    return out


def build_el(node, t, m, style, idx):
    fill = color_norm(style.get('fill'))
    stroke = color_norm(style.get('stroke'))
    if fill is None and t != 'text':
        fill = '#000000'          # SVG default
    if t == 'text' and fill is None:
        fill = '#000000'
    sw_local = fnum(style.get('stroke-width'), 1.0)
    sc = scale_of(m)
    sw = sw_local * sc if stroke and stroke != 'none' else 0.0
    dash = style.get('stroke-dasharray')
    if dash and dash.strip().lower() in ('none', ''):
        dash = None
    opacity = fnum(style.get('opacity'), 1.0)

    pts, closed, curve, text, fs = None, False, False, None, None
    if t == 'path':
        d = node.get('d')
        if not d:
            return None
        subs, curve = parse_path_flat(d)
        if not subs:
            return None
        pts = [p for s in subs for p in s[0]]
        closed = any(s[1] for s in subs)
        nsub = len(subs)
    elif t == 'rect':
        x, y = fnum(node.get('x')), fnum(node.get('y'))
        w, h = fnum(node.get('width')), fnum(node.get('height'))
        if w <= 0 or h <= 0:
            return None
        pts, closed, curve = rect_points(x, y, w, h, fnum(node.get('rx')), fnum(node.get('ry')))
        nsub = 1
    elif t == 'circle':
        r = fnum(node.get('r'))
        if r <= 0:
            return None
        pts, closed, curve = ellipse_points(fnum(node.get('cx')), fnum(node.get('cy')), r, r)
        nsub = 1
    elif t == 'ellipse':
        rx, ry = fnum(node.get('rx')), fnum(node.get('ry'))
        if rx <= 0 or ry <= 0:
            return None
        pts, closed, curve = ellipse_points(fnum(node.get('cx')), fnum(node.get('cy')), rx, ry)
        nsub = 1
    elif t == 'line':
        pts = [(fnum(node.get('x1')), fnum(node.get('y1'))),
               (fnum(node.get('x2')), fnum(node.get('y2')))]
        nsub = 1
    elif t in ('polygon', 'polyline'):
        v = [float(x) for x in NUM_TOKEN.findall(node.get('points') or '')]
        pts = list(zip(v[0::2], v[1::2]))
        if len(pts) < 2:
            return None
        closed = (t == 'polygon')
        nsub = 1
    elif t == 'image':
        x, y = fnum(node.get('x')), fnum(node.get('y'))
        w, h = fnum(node.get('width')), fnum(node.get('height'))
        if w <= 0 or h <= 0:
            return None
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        nsub = 1
    elif t == 'text':
        fs = fnum(style.get('font-size'), 10.0)
        boxes, text = text_local_boxes(node, fs)
        if not boxes:
            return None
        pts = []
        for b in boxes:
            pts += [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])]
        nsub = len(boxes)
        fs = fs * scale_of(m)
    else:
        return None

    tp = [apply_m(m, x, y) for x, y in pts]
    bb = bbox_of(tp)
    if t not in ('text', 'image') and sw:
        bb = (bb[0] - sw / 2, bb[1] - sw / 2, bb[2] + sw / 2, bb[3] + sw / 2)
    plen = 0.0
    if t != 'text':
        for i in range(1, len(tp)):
            plen += math.hypot(tp[i][0] - tp[i - 1][0], tp[i][1] - tp[i - 1][1])
    idx[0] += 1
    return El(tag=t, node=node, ctm=m, bbox=bb, pts=tp, closed=closed, curve=curve,
              fill=fill, stroke=stroke, sw=sw, dash=dash, opacity=opacity,
              text=(text or '').strip() if t == 'text' else None,
              font_size=fs, style=style, cls=None, idx=idx[0], plen=plen, nsub=nsub)


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------
def rectangularity(el):
    """Fraction of points lying on the bbox border (rect / rounded-rect ~ 1.0)."""
    x0, y0, x1, y1 = el.bbox
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return 0.0
    eps = max(0.02 * max(w, h), 0.12 * min(w, h))
    on = 0
    for x, y in el.pts:
        if min(x - x0, x1 - x, y - y0, y1 - y) <= eps:
            on += 1
    return on / max(1, len(el.pts))


def classify(el, scale):
    pt = lambda v: v * scale
    if el.tag == 'text':
        return 'text'
    if el.tag == 'image':
        return 'image'
    w_pt, h_pt = pt(el.w()), pt(el.h())
    long_pt = max(w_pt, h_pt)
    short_pt = min(w_pt, h_pt)
    unfilled = (el.fill in (None, 'none'))
    stroked = bool(el.stroke and el.stroke != 'none')
    if stroked and unfilled:
        if (not el.closed and pt(el.plen) >= TH['connector_min_len_pt']):
            return 'connector'
        if short_pt > 0 and long_pt / max(short_pt, 1e-6) >= TH['connector_aspect'] \
                and long_pt >= TH['connector_min_len_pt']:
            return 'connector'
    if el.tag == 'line' and pt(el.plen) >= TH['connector_min_len_pt']:
        return 'connector'
    if w_pt >= TH['box_min_pt'] and h_pt >= TH['box_min_pt'] and rectangularity(el) >= 0.9:
        return 'box'
    return 'small'


# ---------------------------------------------------------------------------
# candidate assembly
# ---------------------------------------------------------------------------
class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]; a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def is_link_fragment(el, scale):
    """A short open stroked segment: a topology link, a leader line or one dash
    of an exploded dashed line.  Below `connector_min_len_pt` these are class
    `small`, and because they physically touch the nodes at both ends they chain
    a whole topology figure into one blob.  Excluded from clustering (they are
    still available to the arrowhead/legend detectors)."""
    if el.tag in ('text', 'image') or el.closed:
        return False
    if not (el.stroke and el.stroke != 'none') or el.fill not in (None, 'none'):
        return False
    w, h = el.w(), el.h()
    long_, short = max(w, h), min(w, h)
    if long_ <= 0:
        return False
    return (el.plen * scale >= TH['link_fragment_min_pt']
            and long_ / max(short, 1e-6) >= TH['link_fragment_aspect'])


def _cluster_once(els, idxs, pad):
    """Union the given elements whose bboxes, grown by `pad`, intersect."""
    if len(idxs) < 2:
        return [list(idxs)]
    boxes = [(els[i].bbox[0] - pad, els[i].bbox[1] - pad,
              els[i].bbox[2] + pad, els[i].bbox[3] + pad) for i in idxs]
    order = sorted(range(len(idxs)), key=lambda k: boxes[k][0])
    uf = UF(len(idxs))
    for a in range(len(order)):
        ia = order[a]
        for b in range(a + 1, len(order)):
            ib = order[b]
            if boxes[ib][0] > boxes[ia][2]:
                break
            if bbox_inter(boxes[ia], boxes[ib]):
                uf.union(ia, ib)
    groups = defaultdict(list)
    for k in range(len(idxs)):
        groups[uf.find(k)].append(idxs[k])
    return list(groups.values())


def cluster_small(els, scale, max_depth=5):
    """Proximity clusters of `small` elements, with adaptive re-splitting.

    A single pad chains a dense drawing into one blob -- badly so at print
    scale, where a whole PDF-extracted figure collapsed into two clusters of
    140pt and every icon in it was lost.  Any cluster whose long side exceeds
    the candidate window is therefore re-clustered with half the pad, down to
    ~0.1pt.  This is purely additive: clusters that already fit the window are
    never touched, and oversize clusters used to be discarded outright.
    """
    pad0 = TH['cluster_pad_pt'] / scale
    minpad = 0.1 / scale
    maxu = TH['cand_max_pt'] / scale
    idxs = [i for i, e in enumerate(els)
            if e.cls == 'small' and max(e.w(), e.h()) <= maxu
            and not is_link_fragment(e, scale)]
    if not idxs:
        return []
    out, stack = [], [(idxs, pad0, 0)]
    while stack:
        cur, pad, depth = stack.pop()
        for g in _cluster_once(els, cur, pad):
            bb = els[g[0]].bbox
            for i in g[1:]:
                bb = bbox_union(bb, els[i].bbox)
            too_big = max(bb[2] - bb[0], bb[3] - bb[1]) > maxu
            if too_big and len(g) > 1 and depth < max_depth and pad > minpad:
                stack.append((g, pad / 2.0, depth + 1))
            else:
                out.append(g)
    return out


def near_texts(els, bb, scale, tol_pt=None, limit=120):
    """Texts inside bb, plus text within `tol_pt` print-pt of it.

    The default radius feeds `hint_text` (a caption-like label); the wider
    radius feeds `hint_wide`, which is only used for keyword matching."""
    inside, near, best = [], None, 1e18
    wide = []
    tol = (tol_pt if tol_pt is not None else TH['hint_text_pt']) / scale
    for e in els:
        if e.cls != 'text' or not e.text:
            continue
        b = e.bbox
        if b[0] >= bb[0] - 1 and b[2] <= bb[2] + 1 and b[1] >= bb[1] - 1 and b[3] <= bb[3] + 1:
            inside.append(e.text)
            continue
        dx = max(bb[0] - b[2], b[0] - bb[2], 0.0)
        dy = max(bb[1] - b[3], b[1] - bb[3], 0.0)
        d = math.hypot(dx, dy)
        if d > tol:
            continue
        wide.append(e.text)
        if d < best:
            best, near = d, e.text
    if tol_pt is None:
        txt = ' '.join(inside)
        if near:
            txt = (txt + ' ' + near).strip() if txt else near
    else:
        txt = ' '.join(inside + wide)
    txt = JUNK_TEXT_RE.sub(' ', txt)
    return re.sub(r'\s+', ' ', txt).strip()[:limit]


def contains_bb(a, b, m=0.0):
    return a[0] <= b[0] + m and a[1] <= b[1] + m and a[2] >= b[2] - m and a[3] >= b[3] - m


def fill_ratio(el):
    """|polygon area| / bbox area.  1.0 for a rectangle, ~0.5 for a triangle,
    ~0.3 for a chevron -- the cheapest way to keep small filled RECTANGLES out
    of the arrowhead pool (they have four corners too)."""
    x0, y0, x1, y1 = el.bbox
    a = (x1 - x0) * (y1 - y0)
    if a <= 0 or len(el.pts) < 3:
        return 1.0
    p = el.pts
    sh = 0.0
    for i in range(len(p)):
        q = p[(i + 1) % len(p)]
        sh += p[i][0] * q[1] - q[0] * p[i][1]
    return min(1.0, abs(sh) / 2.0 / a)


def mid_span_full(pts, bb, band=0.10, frac=0.85):
    """True when the shape is as wide at half height as it is overall -- true
    for a cylinder body, false for hooks, L-arrows and other bent shapes."""
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return False
    cy = (y0 + y1) / 2.0
    # straight runs are stored as endpoints only, so intersect the mid line
    # with every segment instead of sampling points near it
    xs = [x for x, y in pts if abs(y - cy) <= band * h]
    for i in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        if (ay - cy) * (by - cy) <= 0 and ay != by:
            xs.append(ax + (bx - ax) * (cy - ay) / (by - ay))
    return len(xs) >= 2 and (max(xs) - min(xs)) >= frac * w


def apex_narrow(el, band=0.06, max_span=0.55):
    """True when the very top of the shape tapers (an elliptical cap) instead of
    running the full width (a rectangle, a rounded box, a row of glyphs)."""
    x0, y0, x1, y1 = el.bbox
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return False
    top = [x for x, y in el.pts if y <= y0 + band * h]
    if len(top) < 2:
        return False
    return (max(top) - min(top)) <= max_span * w


def looks_cylinder(sub, scale):
    """Elliptical cap(s) above/below a body with two straight vertical sides.

    Deliberately conservative -- a missed cylinder still shows up in the pool
    tagged `icon`, whereas a loose test floods the pool (the first tuning pass
    labelled circles, check marks and rounded boxes as cylinders).
    """
    bb = sub['bbox']
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    if w <= 0 or h <= 0 or not (0.50 <= w / h <= 2.2):
        return False
    els = sub['els']
    if not any(e.curve for e in els):
        return False
    if len(els) == 1:
        e = els[0]
        if not e.curve or len(e.pts) < 12 or (e.nsub or 1) > 2:
            return False                  # outlined glyph runs, icon groups
        if not mid_span_full(e.pts, bb):
            return False                  # hooks and bent arrows
        straight, flat = 0, 0
        for i in range(1, len(e.pts)):
            dx = abs(e.pts[i][0] - e.pts[i - 1][0])
            dy = abs(e.pts[i][1] - e.pts[i - 1][1])
            if dx <= 0.03 * w and dy >= 0.20 * h:
                straight += 1             # a straight vertical body side
            if dy <= 0.02 * h and dx >= 0.55 * w:
                flat += 1                 # a full-width straight edge
        if straight < 2 or flat:
            return False                  # rounded rectangles have flat edges
        # the top must be an arc: the sides start below the top by a cap depth
        # that is small compared with the width (a stadium's is exactly w/2)
        side = [y for x, y in e.pts if min(abs(x - bb[0]), abs(x - bb[2])) <= 0.03 * w]
        if not side:
            return False
        cap = min(side) - bb[1]
        return 0.04 * w <= cap <= 0.40 * w
    # group form: a wide flat curved cap sitting on top of taller geometry
    caps = [e for e in els
            if e.curve and e.w() >= 1.7 * e.h() and e.w() >= 0.65 * w
            and e.h() <= 0.45 * h and (e.bbox[1] - bb[1]) <= 0.12 * h
            and apex_narrow(e)]
    if not caps:
        return False
    cap_bot = min(e.bbox[3] for e in caps)
    if not any(e is not caps[0] and e.bbox[3] > cap_bot + 0.15 * h for e in els):
        return False
    return mid_span_full([p for e in els for p in e.pts], bb, frac=0.80)


def cand_hash(c, gels, bb):
    """Dedupe key for one candidate.

    Icons/cylinders/stacks/legends/badges use exact normalised geometry.
    Arrowheads use an orientation-free coarse shape key, and the two *style
    record* heuristics use a bucketed style key so that the same idiom drawn in
    a different palette or at a slightly different size collapses into one
    entry (otherwise every figure contributes its own hex colour).
    """
    h = c['heuristic']
    x = c['extra']
    if h == 'container-title':
        return style_key('ct:', (hue_family(x.get('stroke') or '#000000'),
                                 bucket(x.get('stroke_w_pt'), 0.25),
                                 dash_class(x.get('dasharray_pt')),
                                 hue_family(x.get('fill') or '#ffffff'),
                                 bucket(x.get('corner_r_pt'), 1.0),
                                 x.get('title_pos'),
                                 bucket(x.get('title_font_pt'), 0.5)))
    if h == 'arrowhead' and len(gels) == 1:
        k = arrow_shape_key(gels[0])
        if k:
            return k
    return geom_hash(gels, bb)


def geom_hash(els, bb):
    """Normalise all points into a unit box, round, hash (colour-independent)."""
    w = max(bb[2] - bb[0], 1e-6); h = max(bb[3] - bb[1], 1e-6)
    parts = []
    for e in sorted(els, key=lambda e: (e.bbox[0], e.bbox[1], e.tag)):
        seq = [(round((x - bb[0]) / w, 2), round((y - bb[1]) / h, 2)) for x, y in e.pts[:400]]
        parts.append(e.tag + ':' + ';'.join('%.2f,%.2f' % p for p in seq))
    return hashlib.sha1('|'.join(parts).encode()).hexdigest()[:20]


# ---------------------------------------------------------------------------
# standalone SVG export
# ---------------------------------------------------------------------------
def font_stack(fam, faces):
    fam = (fam or '').strip()
    first = fam.split(',')[0].strip().strip('"\'')
    generic = 'monospace' if MONO_RE.search(fam) else ('serif' if SERIF_RE.search(fam) else 'sans-serif')
    if not fam or first in faces:
        base = first or 'Helvetica'
        return "%s, Helvetica, Arial, %s" % (base, generic)
    if re.search(r'\b(sans-serif|serif|monospace)\s*$', fam):
        return fam
    return fam + ', ' + generic


PRESENT = ('fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap',
           'stroke-linejoin', 'stroke-miterlimit', 'fill-rule', 'opacity',
           'fill-opacity', 'stroke-opacity', 'font-size', 'font-weight', 'font-style')


def export_candidate_svg(els, bb, comment, faces, pad_frac=0.04):
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    pad = max(pad_frac * max(w, h), 0.5)
    x0, y0 = bb[0] - pad, bb[1] - pad
    vw, vh = w + 2 * pad, h + 2 * pad
    root = etree.Element('{%s}svg' % SVG_NS, nsmap={None: SVG_NS})
    root.set('viewBox', '%.3f %.3f %.3f %.3f' % (x0, y0, vw, vh))
    root.set('width', '%.3f' % vw)
    root.set('height', '%.3f' % vh)
    root.append(etree.Comment(' ' + comment.replace('--', '- -') + ' '))
    for e in els:
        c = copy.deepcopy(e.node)
        for k in list(c.attrib):
            if k in ('clip-path', 'mask', 'filter', 'style', 'clip-rule', 'id'):
                del c.attrib[k]
        for sub in c.iter():
            for k in list(sub.attrib):
                if k in ('clip-path', 'mask', 'filter', 'clip-rule'):
                    del sub.attrib[k]
        c.set('transform', mat_str(e.ctm))
        for k in PRESENT:
            v = e.style.get(k)
            if v is not None and str(v).strip() != '':
                c.set(k, str(v))
        if e.tag != 'text':
            c.set('fill', e.fill or 'none')
            if e.stroke:
                c.set('stroke', e.stroke)
        else:
            c.set('fill', e.fill or '#000000')
            c.set('font-family', font_stack(e.style.get('font-family'), faces))
        root.append(c)
    return etree.tostring(root, pretty_print=True, encoding='unicode')


def synth_connector_svg(style):
    """A 56pt sample line drawn with the recorded stroke properties + a head."""
    sw = max(style['width_pt'], 0.3)
    head = style.get('head_len_pt') or 0
    L = 56.0
    parts = ['<svg xmlns="%s" viewBox="0 0 %.1f %.1f" width="%.1f" height="%.1f">'
             % (SVG_NS, L + 8, 20.0, L + 8, 20.0)]
    dash = ' stroke-dasharray="%s"' % style['dash_pt'] if style.get('dash_pt') else ''
    parts.append('<path d="M4 10H%.1f" fill="none" stroke="%s" stroke-width="%.2f"%s stroke-linecap="%s"/>'
                 % (4 + L - head, style['color'], sw, dash, style.get('linecap') or 'butt'))
    if head:
        tip = 4 + L
        parts.append('<path d="M%.1f 10 L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
                     % (tip, tip - head, 10 - head * 0.45, tip - head, 10 + head * 0.45,
                        style.get('head_fill') or style['color']))
    parts.append('</svg>')
    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# per-file worker
# ---------------------------------------------------------------------------
def process_file(job):
    meta, rel, path, file_index, skip_heur = job
    pid, fig = meta['paper_id'], meta['fig']
    scale, scale_note = meta['scale'], meta['scale_note']
    tool, venue, caption = meta['tool'], meta['venue'], meta['caption']
    hint_sem = meta['hint_sem']
    skip_heur = set(skip_heur or ())
    res = {'paper_id': pid, 'fig': fig, 'file': rel, 'scale': scale,
           'scale_note': scale_note, 'tool': tool, 'ok': False, 'error': None,
           'select': meta.get('select'), 'subtype': meta.get('subtype'),
           'n_elems': 0, 'cls': {}, 'candidates': [], 'bitmaps': []}
    try:
        raw = open(path, 'rb').read()
        faces = set(FONTFACE_FAM_RE.findall(raw[:400000].decode('utf-8', 'replace')))
        parser = etree.XMLParser(recover=True, huge_tree=True, remove_comments=True)
        root = etree.fromstring(raw, parser=parser)
        if root is None:
            res['error'] = 'unparsable'
            return res
        vb = root.get('viewBox')
        if vb:
            v = [float(x) for x in NUM_TOKEN.findall(vb)]
            W, H = (v[2], v[3]) if len(v) >= 4 else (fnum(root.get('width'), 100), fnum(root.get('height'), 100))
            ox, oy = (v[0], v[1]) if len(v) >= 4 else (0.0, 0.0)
        else:
            W, H = fnum(root.get('width'), 100.0), fnum(root.get('height'), 100.0)
            ox = oy = 0.0
        defs_by_id = {}
        for node in root.iter():
            i = node.get('id')
            if i:
                defs_by_id[i] = node
        els = walk(root, defs_by_id)
        for e in els:
            e.cls = classify(e, scale)
        res['n_elems'] = len(els)
        res['cls'] = dict(Counter(e.cls for e in els))
        pt = lambda v: v * scale
        fig_bb = (ox, oy, ox + W, oy + H)
        comment_base = 'source: %s fig%s %s' % (pid, fig, rel)

        cands = []          # dicts: els, bbox, heuristic, extra
        # ---- generic icon clusters -------------------------------------
        for grp in cluster_small(els, scale):
            gels = [els[i] for i in grp]
            bb = gels[0].bbox
            for e in gels[1:]:
                bb = bbox_union(bb, e.bbox)
            w_pt, h_pt = pt(bb[2] - bb[0]), pt(bb[3] - bb[1])
            long_pt, short_pt = max(w_pt, h_pt), min(w_pt, h_pt)
            if not (TH['cand_min_pt'] <= long_pt <= TH['cand_max_pt']):
                continue
            asp = w_pt / h_pt if h_pt > 0 else 99
            if not (TH['cand_aspect_lo'] <= asp <= TH['cand_aspect_hi']):
                continue
            n_eff = len({(round(e.bbox[0], 1), round(e.bbox[1], 1),
                          round(e.bbox[2], 1), round(e.bbox[3], 1)) for e in gels})
            if n_eff > TH['cand_max_elements']:
                continue                       # a whole sub-panel, not a part
            # (fill and stroke are usually drawn as two identical paths, so the
            #  raw element count roughly doubles -- count distinct geometry)
            has_curve = any(e.curve for e in gels)
            if len(gels) < 2 and not has_curve:
                continue
            if TH['cluster_need_nonrect'] and len(gels) < 3:
                # 1-2 plain rectangles == a node box / bar / table cell
                if all(rectangularity(e) >= TH['rect_thresh'] for e in gels):
                    continue
            cands.append({'els': gels, 'bbox': bb, 'heuristic': 'icon', 'extra': {}})

        # ---- badge ------------------------------------------------------
        for c in cands:
            bb = c['bbox']
            long_pt = pt(max(bb[2] - bb[0], bb[3] - bb[1]))
            if long_pt > TH['badge_max_pt']:
                continue
            if not any(e.curve for e in c['els']):
                continue
            inner = [e for e in els if e.cls == 'text' and e.text
                     and bb[0] - 1 <= e.bbox[0] and e.bbox[2] <= bb[2] + 1
                     and bb[1] - 1 <= e.bbox[1] and e.bbox[3] <= bb[3] + 1]
            if len(inner) == 1 and BADGE_TEXT_RE.match(inner[0].text or ''):
                c['heuristic'] = 'badge'
                c['els'] = c['els'] + inner
                c['extra'] = {'badge_glyph': inner[0].text.strip()}
        # circled-glyph text with no shape around it
        for e in els:
            if e.cls == 'text' and e.text and CIRCLED_RE.search(e.text) and len(e.text.strip()) <= 3:
                cands.append({'els': [e], 'bbox': e.bbox, 'heuristic': 'badge',
                              'extra': {'badge_glyph': e.text.strip(), 'glyph_only': True}})

        # ---- cylinder ---------------------------------------------------
        for c in cands:
            if c['heuristic'] == 'icon' and looks_cylinder(c, scale):
                c['heuristic'] = 'cylinder'
        # single large paths that were classified `small` but are cylinder-shaped
        for e in els:
            if e.cls in ('small', 'box') and e.curve and \
                    TH['cand_min_pt'] <= pt(max(e.w(), e.h())) <= TH['cand_max_pt'] * 1.6:
                sub = {'els': [e], 'bbox': e.bbox}
                if looks_cylinder(sub, scale) and not any(e in c['els'] for c in cands):
                    cands.append({'els': [e], 'bbox': e.bbox, 'heuristic': 'cylinder', 'extra': {}})

        # ---- stacked cards ----------------------------------------------
        rects = [e for e in els if e.tag != 'text' and e.tag != 'image'
                 and rectangularity(e) >= 0.9 and pt(min(e.w(), e.h())) >= 6]
        used = set()
        n_stacked = 0
        for i, a in enumerate(rects):
            if id(a) in used:
                continue
            grp = [a]
            for b in rects[i + 1:]:
                if id(b) in used:
                    continue
                if contains_bb(a.bbox, b.bbox) or contains_bb(b.bbox, a.bbox):
                    continue               # nested / double-border, not stacked
                if abs(a.w() - b.w()) <= TH['stack_size_tol'] * max(a.w(), 1e-6) and \
                   abs(a.h() - b.h()) <= TH['stack_size_tol'] * max(a.h(), 1e-6):
                    dx = pt(abs(b.bbox[0] - a.bbox[0])); dy = pt(abs(b.bbox[1] - a.bbox[1]))
                    off = math.hypot(dx, dy)
                    if TH['stack_off_lo_pt'] <= off <= TH['stack_off_hi_pt'] * 1.5 and \
                       dx <= TH['stack_off_hi_pt'] and dy <= TH['stack_off_hi_pt'] and \
                       dx >= TH['stack_off_lo_pt'] and dy >= TH['stack_off_lo_pt']:
                        grp.append(b)
            if len(grp) >= 2:
                bb = grp[0].bbox
                for e in grp[1:]:
                    bb = bbox_union(bb, e.bbox)
                if pt(max(bb[2] - bb[0], bb[3] - bb[1])) <= TH['cand_max_pt'] and \
                        n_stacked < TH['max_stacked_per_file']:
                    n_stacked += 1
                    for e in grp:
                        used.add(id(e))
                    cands.append({'els': grp, 'bbox': bb, 'heuristic': 'stacked',
                                  'extra': {'n_cards': len(grp)}})

        # ---- arrowheads + connector styles -------------------------------
        conns = [e for e in els if e.cls == 'connector']
        ends = []
        for e in conns:
            if len(e.pts) >= 2:
                ends.append((e.pts[0], e)); ends.append((e.pts[-1], e))
        heads, seen_head = [], set()
        touch = TH['arrow_touch_pt'] / scale
        for e in els:
            if e.tag in ('text', 'image'):
                continue
            if e.fill in (None, 'none'):
                continue
            if pt(max(e.w(), e.h())) > TH['arrow_max_pt'] or pt(max(e.w(), e.h())) < 1.0:
                continue
            corners = len({(round(x, 2), round(y, 2)) for x, y in e.pts})
            if corners > 6 or corners < 3:
                continue
            if not (0.15 <= fill_ratio(e) <= 0.80):
                continue                   # a solid bar / square, not a head
            cx = (e.bbox[0] + e.bbox[2]) / 2; cy = (e.bbox[1] + e.bbox[3]) / 2
            hit = None
            for (p, ce) in ends:
                if math.hypot(p[0] - cx, p[1] - cy) <= touch + max(e.w(), e.h()):
                    hit = ce
                    break
            if hit is None:
                continue
            gh = geom_hash([e], e.bbox)
            if gh in seen_head:
                continue
            seen_head.add(gh)
            heads.append((e, hit))
            if len(heads) >= TH['max_arrowheads_per_file']:
                break
        for e, ce in heads:
            cands.append({'els': [e], 'bbox': e.bbox, 'heuristic': 'arrowhead',
                          'extra': {'head_w_pt': round(pt(e.w()), 2),
                                    'head_h_pt': round(pt(e.h()), 2),
                                    'conn_stroke_pt': round(pt(ce.sw), 2),
                                    'conn_color': ce.stroke,
                                    'conn_dash': ce.dash}})
        # distinct connector styles
        styles = {}
        head_by_conn = {}
        conns = [] if 'connector-style' in skip_heur else conns
        for e, ce in heads:
            head_by_conn.setdefault(id(ce), (e, pt(max(e.w(), e.h()))))
        for e in conns:
            hd = head_by_conn.get(id(e))
            dash_pt = None
            if e.dash:
                try:
                    dash_pt = ','.join('%.2g' % (float(v) * scale_of(e.ctm) * scale)
                                       for v in NUM_TOKEN.findall(e.dash))
                except ValueError:
                    dash_pt = e.dash
            key = (hue_family(e.stroke or '#000000'),
                   bucket(min(pt(e.sw), 4.0), 0.5), dash_class(dash_pt), bool(hd),
                   bucket(min(hd[1], 12.0), 3.0) if hd else 0, bool(e.curve))
            if key in styles:
                continue
            styles[key] = {'color': e.stroke or '#000000', 'width_pt': round(pt(e.sw), 2),
                           'dash_pt': dash_pt, 'linecap': e.style.get('stroke-linecap'),
                           'head_len_pt': round(hd[1], 1) if hd else 0,
                           'head_fill': hd[0].fill if hd else None,
                           'curved': bool(e.curve),
                           'len_pt': round(pt(e.plen), 1)}
            if len(styles) >= TH['max_connstyles_per_file']:
                break

        # ---- legend blocks ------------------------------------------------
        pairs = []
        gap = TH['legend_gap_pt'] / scale
        sw_max = TH['legend_swatch_max_pt'] / scale
        texts = [e for e in els if e.cls == 'text' and e.text]
        for e in (() if 'legend' in skip_heur else els):
            if e.tag in ('text', 'image') or e.cls == 'connector':
                continue
            if max(e.w(), e.h()) > sw_max or max(e.w(), e.h()) < 2.0 / scale:
                continue
            ecy = (e.bbox[1] + e.bbox[3]) / 2
            best = None
            for t in texts:
                tcy = (t.bbox[1] + t.bbox[3]) / 2
                if t.bbox[0] >= e.bbox[2] - 0.5 and t.bbox[0] - e.bbox[2] <= gap and \
                        abs(tcy - ecy) <= max(e.h(), 1.0):
                    if best is None or t.bbox[0] < best.bbox[0]:
                        best = t
            if best is not None:
                pairs.append((e, best))
        if len(pairs) >= 2 and 'legend' not in skip_heur:
            bot = fig_bb[3] - 0.25 * H
            rgt = fig_bb[2] - 0.25 * W
            rows = defaultdict(list)
            cols = defaultdict(list)
            for e, t in pairs:
                rows[round(((e.bbox[1] + e.bbox[3]) / 2) / max(e.h(), 1.0))].append((e, t))
                cols[round(e.bbox[0] / max(e.w(), 1.0))].append((e, t))
            blocks = [v for v in list(rows.values()) + list(cols.values()) if len(v) >= 2]
            seen_block = set()
            for blk in sorted(blocks, key=lambda b: -len(b))[:3]:
                key = tuple(sorted(id(e) for e, _ in blk))
                if key in seen_block:
                    continue
                seen_block.add(key)
                gels = []
                bb = None
                for e, t in blk:
                    gels += [e, t]
                    bb = e.bbox if bb is None else bbox_union(bb, e.bbox)
                    bb = bbox_union(bb, t.bbox)
                if bb[1] < bot and bb[0] < rgt:
                    continue                       # not in the legend zone
                cands.append({'els': gels, 'bbox': bb, 'heuristic': 'legend',
                              'extra': {'n_items': len(blk),
                                        'zone': 'bottom' if bb[1] >= bot else 'right'}})

        # ---- container titles ---------------------------------------------
        n_ct = 0
        boxable = [e for e in els if e.tag not in ('text',) and e.cls != 'text']
        for e in (() if 'container-title' in skip_heur else els):
            if e.cls != 'box' or pt(e.w()) < TH['container_min_w_pt'] \
                    or pt(e.h()) < TH['container_min_h_pt']:
                continue
            # "grey" means a mid-grey rule, not a plain black outline
            greyish = bool(e.stroke and e.stroke != 'none' and is_grey(e.stroke)
                           and 0x50 <= int(e.stroke[1:3], 16) <= 0xd8) \
                if (e.stroke or '').startswith('#') else False
            if not (e.dash or greyish):
                continue
            inner = sum(1 for o in boxable
                        if o is not e and contains_bb(e.bbox, o.bbox, -0.5)
                        and o.w() < 0.95 * e.w())
            if inner < TH['container_min_inner']:
                continue                       # a labelled node box, not a container
            title = None
            for t in texts:
                if t.bbox[0] >= e.bbox[0] - 2 and t.bbox[2] <= e.bbox[2] + 2 and \
                        e.bbox[1] - 2 <= t.bbox[1] <= e.bbox[1] + 0.30 * e.h():
                    if len((t.text or '').strip()) < 2:
                        continue           # a step badge, not a container title
                    if title is None or t.bbox[1] < title.bbox[1]:
                        title = t
            if title is None:
                continue
            tcx = (title.bbox[0] + title.bbox[2]) / 2
            rel_x = (tcx - e.bbox[0]) / max(e.w(), 1e-6)
            posn = 'top-left' if rel_x < 0.33 else ('top-centre' if rel_x < 0.67 else 'top-right')
            # corner radius: distance from the bbox corner to the nearest path point
            cr = 0.0
            for cxx, cyy in ((e.bbox[0], e.bbox[1]), (e.bbox[2], e.bbox[1])):
                d = min(math.hypot(p[0] - cxx, p[1] - cyy) for p in e.pts)
                cr = max(cr, d)
            # a ~110x34pt window on the top edge: wide enough to show the
            # corner radius and the dash pattern, narrow enough that the title
            # is still legible in a 120px thumbnail.  Slide it right when the
            # title sits at the top-centre/top-right of a wide container.
            crop_w = min(e.w(), 110.0 / scale)
            crop_h = min(e.h(), max(34.0 / scale, 2.4 * (title.bbox[3] - title.bbox[1])))
            cx0 = e.bbox[0]
            if title.bbox[2] > cx0 + crop_w:
                cx0 = min(e.bbox[2] - crop_w,
                          (title.bbox[0] + title.bbox[2]) / 2 - crop_w / 2)
                cx0 = max(cx0, e.bbox[0])
            bb = (cx0, e.bbox[1], cx0 + crop_w, e.bbox[1] + crop_h)
            dash_pt = None
            if e.dash:
                try:
                    dash_pt = ','.join('%.2g' % (float(v) * scale_of(e.ctm) * scale)
                                       for v in NUM_TOKEN.findall(e.dash))
                except ValueError:
                    dash_pt = e.dash
            cands.append({'els': [e, title], 'bbox': bb, 'heuristic': 'container-title',
                          'extra': {'stroke': e.stroke, 'stroke_w_pt': round(pt(e.sw), 2),
                                    'dasharray_pt': dash_pt, 'fill': e.fill,
                                    'corner_r_pt': round(pt(cr), 2),
                                    'title_pos': posn,
                                    'title_font_pt': round((title.font_size or 0) * scale, 2),
                                    'box_w_pt': round(pt(e.w()), 1),
                                    'box_h_pt': round(pt(e.h()), 1),
                                    'title_text': (title.text or '')[:60]}})
            n_ct += 1
            if n_ct >= 6:
                break

        # ---- bitmap icons (recorded only) ----------------------------------
        for e in els:
            if e.tag != 'image':
                continue
            res['bitmaps'].append({
                'paper_id': pid, 'fig': fig, 'file': rel, 'tool': tool,
                'w_pt': round(pt(e.w()), 1), 'h_pt': round(pt(e.h()), 1),
                'x_frac': round((e.bbox[0] - ox) / max(W, 1e-6), 3),
                'y_frac': round((e.bbox[1] - oy) / max(H, 1e-6), 3),
                'area_frac': round((e.w() * e.h()) / max(W * H, 1e-6), 4),
                'hint_text': near_texts(els, e.bbox, scale),
                'hint_semantics': hint_sem})

        # ---- materialise ----------------------------------------------------
        if skip_heur:
            cands = [c for c in cands if c['heuristic'] not in skip_heur]
        cands = cands[:TH['max_cands_per_file']]
        out = []
        for k, c in enumerate(cands):
            bb = c['bbox']
            gels = c['els']
            w_pt, h_pt = pt(bb[2] - bb[0]), pt(bb[3] - bb[1])
            cid = '%s_fig%s_%d' % (pid, fig, file_index * 100 + k)
            comment = '%s bbox=%.2f,%.2f,%.2f,%.2f scale=%.4f' % (
                comment_base, bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1], scale)
            try:
                svg = export_candidate_svg(gels, bb, comment, faces)
            except Exception as exc:      # noqa: BLE001
                continue
            colors = sorted({e.fill for e in gels if e.fill and e.fill != 'none'} |
                            {e.stroke for e in gels if e.stroke and e.stroke != 'none'})
            hint = (c['extra'].get('title_text') or '') if c['heuristic'] == 'container-title' \
                else near_texts(els, bb, scale)
            out.append({
                'candidate_id': cid, 'paper_id': pid, 'fig': fig, 'file': rel,
                'tool': tool, 'venue': venue, 'heuristic': c['heuristic'],
                'w_pt': round(w_pt, 2), 'h_pt': round(h_pt, 2),
                'size_pt': [round(w_pt, 1), round(h_pt, 1)],
                'n_elements': len(gels),
                'n_text': sum(1 for e in gels if e.tag == 'text'),
                'has_curve': any(e.curve for e in gels),
                'colors': colors[:8],
                'bbox_src': [round(v, 2) for v in bb],
                'scale': round(scale, 5), 'scale_note': scale_note,
                'pos_frac': [round((bb[0] - ox) / max(W, 1e-6), 3),
                             round((bb[1] - oy) / max(H, 1e-6), 3)],
                'hint_text': hint,
                'hint_wide': near_texts(els, bb, scale, tol_pt=TH['hint_wide_pt'],
                                        limit=260),
                'hint_semantics': hint_sem,
                'caption': (caption or '')[:300],
                'select': meta.get('select'), 'subtype': meta.get('subtype'),
                'aesthetic': meta.get('aesthetic'), 'source_kind': meta.get('source_kind'),
                'geom_hash': cand_hash(c, gels, bb),
                'extra': c['extra'],
                'svg': svg,
            })
        # synthetic connector-style candidates
        for j, (key, st) in enumerate(styles.items()):
            cid = '%s_fig%s_%d' % (pid, fig, file_index * 100 + 90 + j)
            out.append({
                'candidate_id': cid, 'paper_id': pid, 'fig': fig, 'file': rel,
                'tool': tool, 'venue': venue, 'heuristic': 'connector-style',
                'w_pt': 56.0, 'h_pt': 20.0, 'size_pt': [56.0, 20.0],
                'n_elements': 1 + (1 if st['head_len_pt'] else 0), 'n_text': 0,
                'has_curve': st['curved'],
                'colors': [c for c in [st['color'], st['head_fill']] if c],
                'bbox_src': None, 'scale': round(scale, 5), 'scale_note': scale_note,
                'pos_frac': None, 'hint_text': '', 'hint_semantics': hint_sem,
                'caption': (caption or '')[:300], 'hint_wide': '',
                'select': meta.get('select'), 'subtype': meta.get('subtype'),
                'aesthetic': meta.get('aesthetic'), 'source_kind': meta.get('source_kind'),
                'geom_hash': style_key('cs:', key),
                'extra': st,
                'svg': synth_connector_svg(st),
            })
        res['candidates'] = out
        res['ok'] = True
    except Exception as exc:              # noqa: BLE001
        res['error'] = '%s: %s' % (type(exc).__name__, exc)
    return res


# ---------------------------------------------------------------------------
# figure selection
# ---------------------------------------------------------------------------
def pick_scale(print_w, print_h, sizes):
    """sizes: [(w,h), ...] of the panel source viewBoxes -> (scale, note)."""
    if not sizes or not print_w:
        return 1.0, 'no-style'
    if len(sizes) == 1:
        w, h = sizes[0]
        sw = print_w / w if w else 1.0
        sh = print_h / h if h else sw
        aspr = (sw / sh) if sh else 1.0
        if 0.8 <= aspr <= 1.25:
            return sw, 'single'
        return math.sqrt(max(sw * sh, 1e-9)), 'single-aspect-mismatch'
    sum_w = sum(s[0] for s in sizes); max_w = max(s[0] for s in sizes)
    sum_h = sum(s[1] for s in sizes); max_h = max(s[1] for s in sizes)
    want = (print_w / print_h) if print_h else 1.0
    row_asp = sum_w / max_h if max_h else 1.0
    col_asp = max_w / sum_h if sum_h else 1.0
    if abs(math.log(max(row_asp, 1e-6) / max(want, 1e-6))) <= abs(math.log(max(col_asp, 1e-6) / max(want, 1e-6))):
        return print_w / sum_w, 'multi-row(%d)' % len(sizes)
    return print_w / max_w, 'multi-col(%d)' % len(sizes)


VB_RE = re.compile(r'viewBox\s*=\s*"([^"]+)"')
WH_RE = re.compile(r'\bwidth\s*=\s*"([^"]+)"[^>]*?\bheight\s*=\s*"([^"]+)"')


def svg_size(path):
    head = open(path, encoding='utf-8', errors='replace').read(4000)
    m = VB_RE.search(head)
    if m:
        v = [float(x) for x in NUM_TOKEN.findall(m.group(1))]
        if len(v) >= 4 and v[2] > 0 and v[3] > 0:
            return v[2], v[3]
    m = WH_RE.search(head)
    if m:
        return fnum(m.group(1), 100.0), fnum(m.group(2), 100.0)
    return 100.0, 100.0


SELECTIONS = ('arch-good-src', 'diagram-src', 'arch-pdf', 'topology-pdf')


def _row_matches(r, sel):
    """Which --select bucket a corpus-index row belongs to (or None).

    arch-good-src  the original pool: architecture + aesthetic good + author
                   source SVG(s).
    diagram-src    every type == 'diagram' row with an author source SVG, all
                   subtypes, every aesthetic except 'discard' (most rows are
                   simply un-reviewed, aesthetic == '').
    arch-pdf       architecture rows with NO author source -- fall back to the
                   figure SVG extracted from the paper PDF (already at print
                   size, so scale = 1).
    topology-pdf   the same for subtype == 'topology' (hardware/network icons
                   concentrate there).
    """
    if r.get('type') != 'diagram':
        return None
    has_src = bool((r.get('src_svgs') or '').strip())
    has_pdf = bool((r.get('pdf_svg') or '').strip())
    sub, aes = r.get('subtype'), r.get('aesthetic')
    if sel == 'arch-good-src':
        return 'src' if (sub == 'architecture' and aes == 'good' and has_src) else None
    if aes == 'discard':
        return None
    if sel == 'diagram-src':
        return 'src' if has_src else None
    if sel == 'arch-pdf':
        return 'pdf' if (sub == 'architecture' and not has_src and has_pdf) else None
    if sel == 'topology-pdf':
        return 'pdf' if (sub == 'topology' and not has_src and has_pdf) else None
    return None


def select_figures(index_path, extracted_dir, semantics_path, ids=None, limit=None,
                   selects=('arch-good-src',), exclude_keys=None):
    """-> list of figure jobs.  `selects` may name several buckets; a figure is
    taken by the FIRST bucket that claims it, so the buckets never overlap."""
    sem = {}
    if semantics_path and os.path.exists(semantics_path):
        for line in open(semantics_path, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            sem[(d.get('paper_id'), str(d.get('fig')))] = d
    want_pid, want_pair = None, None
    if ids:
        want_pid, want_pair = set(), set()
        for tok in ids.split(','):
            tok = tok.strip()
            if not tok:
                continue
            if ':' in tok:
                a, b = tok.split(':', 1)
                want_pair.add((a.strip(), b.strip()))
            else:
                want_pid.add(tok)
    exclude_keys = exclude_keys or set()
    figs, skipped = [], 0
    with open(index_path, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            sel = kind = None
            for cand in selects:
                k = _row_matches(r, cand)
                if k:
                    sel, kind = cand, k
                    break
            if sel is None:
                continue
            pid, fig = r['paper_id'], str(r['fig'])
            if '%s_fig%s' % (pid, fig) in exclude_keys:
                skipped += 1
                continue
            if want_pid is not None and pid not in want_pid and (pid, fig) not in want_pair:
                continue
            if kind == 'src':
                files = [f for f in r['src_svgs'].split('|') if f.strip()]
            else:
                files = [r['pdf_svg'].strip()]
            paths = [os.path.join(extracted_dir, pid, f.strip()) for f in files]
            keep = [(f.strip(), p) for f, p in zip(files, paths) if os.path.exists(p)]
            if not keep:
                continue
            try:
                st = json.loads(r['style']) if r.get('style') else {}
            except json.JSONDecodeError:
                st = {}
            pw = (st.get('size') or {}).get('w')
            ph = (st.get('size') or {}).get('h')
            if kind == 'pdf':
                # the PDF export IS the printed figure -> user units are pt
                scale, note = 1.0, 'pdf'
            else:
                sizes = [svg_size(p) for _f, p in keep]
                scale, note = pick_scale(pw, ph, sizes)
            s = sem.get((pid, fig)) or {}
            icons = ((s.get('style') or {}).get('icons') or '')
            comps = [c.get('name') for c in ((s.get('content') or {}).get('components') or [])
                     if c.get('name')]
            hint_sem = {'icons': icons[:220], 'components': comps[:14]}
            figs.append({'paper_id': pid, 'fig': fig, 'tool': r.get('tool') or 'unknown',
                         'venue': r.get('venue') or '', 'caption': r.get('caption') or '',
                         'files': keep, 'scale': scale, 'scale_note': note,
                         'hint_sem': hint_sem, 'select': sel, 'source_kind': kind,
                         'subtype': r.get('subtype') or '', 'aesthetic': r.get('aesthetic') or '',
                         'print_w': pw, 'print_h': ph})
            if limit and len(figs) >= limit:
                break
    if skipped:
        print('  excluded %d already-processed figures' % skipped, flush=True)
    return figs


# ---------------------------------------------------------------------------
# dedupe
# ---------------------------------------------------------------------------
INK_THRESH = 245        # a 16x16 area-averaged cell darker than this counts as ink


def ink_bits(img):
    """16x16 ink-occupancy silhouette -> (256-bit hash, ink cell count).

    A plain dHash was tried first and was useless here: most thumbnails are a
    thin drawing on white, so their gradient hashes are near-identical and
    unrelated parts (a legend row, an arrowhead, three coloured bars) collapsed
    into one group.  An area-averaged ink mask keeps the silhouette instead.
    """
    from PIL import Image
    im = img.convert('L').resize((128, 128), Image.BILINEAR)
    m = np.asarray(im, dtype=np.int16) < INK_THRESH
    m = m.reshape(16, 8, 16, 8).any(axis=(1, 3))   # max-pool: keep hairlines
    return np.packbits(m.flatten()), int(m.sum())


POPCNT = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint8)


def group_by_phash(hashes, inks, thresh, chunk=256):
    """Union candidates whose ink silhouettes are close.

    The tolerance is scaled by ink mass: a pair of nearly empty thumbnails (a
    couple of hairlines) must match almost exactly, otherwise every sparse part
    in the corpus collapses into one group -- that bug produced groups where an
    arrowhead and a 460pt block diagram were "the same part".
    """
    n = len(hashes)
    if n == 0:
        return []
    M = np.stack(hashes).astype(np.uint8)
    ink = np.asarray(inks, dtype=np.int32)
    uf = UF(n)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        d = POPCNT[np.bitwise_xor(M[s:e, None, :], M[None, :, :])].sum(axis=2)
        lim = np.minimum(thresh,
                         np.maximum(1, (0.30 * np.minimum(ink[s:e, None], ink[None, :])).astype(np.int32)))
        ok = d <= lim
        for i in range(e - s):
            for j in np.nonzero(ok[i])[0]:
                if j != s + i:
                    uf.union(s + i, int(j))
    groups = defaultdict(list)
    for i in range(n):
        groups[uf.find(i)].append(i)
    return list(groups.values())


def load_exclusions(path, skip_render=False):
    """Read a previous run's candidates.jsonl.

    Returns (figure keys to skip, geometry hashes, reference ink silhouettes).
    The sibling `thumbs/` directory holds one PNG per geometry-deduped candidate
    of that run, so hashing them gives a complete visual reference -- identical
    geometry renders identically, which also covers the geometry hashes that the
    jsonl does not carry (it stores only each representative's own hash).
    """
    keys, geom = set(), set()
    base = os.path.dirname(os.path.abspath(path))
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get('paper_id') and d.get('fig') is not None:
                keys.add('%s_fig%s' % (d['paper_id'], d['fig']))
            for cid in (d.get('group_geom') or []) + (d.get('group_visual') or []):
                keys.add(cid.rsplit('_', 1)[0])
            if d.get('geom_hash'):
                geom.add(d['geom_hash'])
            for h in (d.get('geom_hashes') or []):
                geom.add(h)
    ink = []
    tdir = os.path.join(base, 'thumbs')
    if not skip_render and np is not None and os.path.isdir(tdir):
        from PIL import Image
        for fn in sorted(os.listdir(tdir)):
            if not fn.endswith('.png'):
                continue
            try:
                bits, n = ink_bits(Image.open(os.path.join(tdir, fn)))
            except Exception:             # noqa: BLE001
                continue
            if n:
                ink.append(bits)
    return keys, geom, ink


def match_reference(hashes, inks, ref, thresh, chunk=256):
    """-> indices of `hashes` that are within `thresh` of any reference hash."""
    if not hashes or not ref:
        return set()
    M = np.stack(hashes).astype(np.uint8)
    R = np.stack(ref).astype(np.uint8)
    ink = np.asarray(inks, dtype=np.int32)
    out = set()
    for s in range(0, len(hashes), chunk):
        e = min(len(hashes), s + chunk)
        d = POPCNT[np.bitwise_xor(M[s:e, None, :], R[None, :, :])].sum(axis=2)
        lim = np.minimum(thresh, np.maximum(1, (0.30 * ink[s:e]).astype(np.int32)))
        hit = (d <= lim[:, None]).any(axis=1)
        out.update(s + int(i) for i in np.nonzero(hit)[0])
    return out


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------
GRID_COLS, GRID_ROWS, CELL = 10, 10, 130     # thumbnail render grid


def render_thumbs(items, thumbs_dir, quiet=False, bg='#ffffff'):
    """items: [(candidate_id, svg_text)] -> writes <thumbs_dir>/<id>.png (~120px).

    `bg` is the cell background; the second pass re-renders white-on-white
    candidates on light grey so that reviewers can still see them.
    """
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import io
    os.makedirs(thumbs_dir, exist_ok=True)
    per = GRID_COLS * GRID_ROWS
    done = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--force-color-profile=srgb',
                                          '--disable-lcd-text'])
        page = browser.new_page(viewport={'width': GRID_COLS * CELL,
                                          'height': GRID_ROWS * CELL},
                                device_scale_factor=1)
        for s in range(0, len(items), per):
            batch = items[s:s + per]
            cells = []
            for cid, svg in batch:
                body = re.sub(r'^\s*<\?xml[^>]*\?>\s*', '', svg)
                body = re.sub(r'<svg\b', '<svg preserveAspectRatio="xMidYMid meet" ', body, count=1)
                body = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r'\1', body, count=1)
                body = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r'\1', body, count=1)
                body = re.sub(r'<svg\b', '<svg width="108" height="108" ', body, count=1)
                cells.append('<div class="c">%s</div>' % body)
            html = ('<html><head><meta charset="utf-8"><style>'
                    'html,body{margin:0;padding:0;background:%s}'
                    '.g{display:grid;grid-template-columns:repeat(%d,%dpx);}'
                    '.c{width:%dpx;height:%dpx;display:flex;align-items:center;'
                    'justify-content:center;background:%s;overflow:hidden}'
                    'svg{display:block}'
                    '</style></head><body><div class="g">%s</div></body></html>'
                    % (bg, GRID_COLS, CELL, CELL, CELL, bg, ''.join(cells)))
            try:
                page.set_content(html, wait_until='load', timeout=30000)
                shot = page.screenshot(clip={'x': 0, 'y': 0,
                                             'width': GRID_COLS * CELL,
                                             'height': GRID_ROWS * CELL})
            except Exception as exc:      # noqa: BLE001
                if not quiet:
                    print('  render batch failed: %s' % exc, file=sys.stderr)
                continue
            sheet = Image.open(io.BytesIO(shot)).convert('RGB')
            for k, (cid, _svg) in enumerate(batch):
                r, c = divmod(k, GRID_COLS)
                tile = sheet.crop((c * CELL + 5, r * CELL + 5,
                                   c * CELL + CELL - 5, r * CELL + CELL - 5))
                tile = tile.resize((120, 120))
                tile.save(os.path.join(thumbs_dir, cid + '.png'))
                done += 1
            if not quiet:
                print('  thumbs %d/%d' % (done, len(items)), flush=True)
        browser.close()
    return done


# ---------------------------------------------------------------------------
# contact sheets
# ---------------------------------------------------------------------------
SHEET_COLS, SHEET_ROWS = 6, 5
TILE_W, TILE_H = 196, 214
MARGIN, HEADER = 16, 40


def _fonts():
    from PIL import ImageFont
    cands = ['/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf']
    bold = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf']
    def pick(paths, size):
        for p in paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()
    return {'num': pick(bold, 20), 'lbl': pick(bold, 11), 'txt': pick(cands, 10),
            'hdr': pick(bold, 18)}


def draw_sheet(rows, thumbs_dir, out_png, title, cols=SHEET_COLS, nrows=SHEET_ROWS):
    from PIL import Image, ImageDraw
    F = _fonts()
    W = cols * TILE_W + 2 * MARGIN
    H = nrows * TILE_H + 2 * MARGIN + HEADER
    img = Image.new('RGB', (W, H), '#ffffff')
    dr = ImageDraw.Draw(img)
    dr.text((MARGIN, 12), title, fill='#111111', font=F['hdr'])
    for k, rec in enumerate(rows):
        r, c = divmod(k, cols)
        x = MARGIN + c * TILE_W
        y = MARGIN + HEADER + r * TILE_H
        dr.rectangle([x, y, x + TILE_W - 6, y + TILE_H - 6], outline='#d8d8d8')
        tp = os.path.join(thumbs_dir, rec['candidate_id'] + '.png')
        if os.path.exists(tp):
            try:
                th = Image.open(tp).convert('RGB')
                img.paste(th, (x + (TILE_W - 6 - 120) // 2, y + 22))
            except Exception:             # noqa: BLE001
                pass
        else:
            dr.text((x + 60, y + 70), 'no thumb', fill='#bbbbbb', font=F['txt'])
        dr.rectangle([x + 3, y + 3, x + 33, y + 21], fill='#1a1a1a')
        dr.text((x + 9, y + 2), str(k + 1), fill='#ffffff', font=F['num'])
        occ = rec.get('occurrences', 1)
        dr.text((x + 40, y + 6), '%s  x%d' % (rec['heuristic'], occ),
                fill='#0b57a4', font=F['lbl'])
        ln = y + 146
        dr.text((x + 8, ln), '%.0f x %.0f pt' % (rec['w_pt'], rec['h_pt']),
                fill='#333333', font=F['txt'])
        dr.text((x + 92, ln), '%d el' % rec['n_elements'], fill='#777777', font=F['txt'])
        ht = (rec.get('hint_text') or '').replace('\n', ' ')
        dr.text((x + 8, ln + 14), ht[:30], fill='#444444', font=F['txt'])
        dr.text((x + 8, ln + 27), ht[30:60], fill='#444444', font=F['txt'])
        src = '%s f%s' % (rec['paper_id'], rec['fig'])
        sub = rec.get('subtype') or ''
        if sub:
            src += '  ' + sub[:12]
        if (rec.get('source_kind') or '') == 'pdf':
            src += ' [pdf]'
        dr.text((x + 8, ln + 42), src[:40], fill='#999999', font=F['txt'])
    img.save(out_png)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--index', default='lab/extracted/corpus_index.csv')
    ap.add_argument('--semantics', default='lab/extracted/corpus_semantics.jsonl')
    ap.add_argument('--extracted-dir', default='lab/extracted')
    ap.add_argument('--out', required=True)
    ap.add_argument('--ids', default=None, help='comma list of paper_id or paper_id:fig')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 1))
    ap.add_argument('--select', default='arch-good-src',
                    help='comma list of %s; a figure goes to the first bucket '
                         'that claims it (default: arch-good-src)' % (', '.join(SELECTIONS),))
    ap.add_argument('--exclude-ids-from', default=None,
                    help='a previous run\'s candidates.jsonl: its figures are skipped '
                         'and its geometry/silhouette hashes are used as an extra '
                         'dedupe reference, so already-reviewed parts do not come back')
    ap.add_argument('--skip-heuristics', default='',
                    help='comma list of heuristics not to emit, e.g. '
                         'connector-style,container-title,legend')
    ap.add_argument('--missing-sheets', action='store_true',
                    help='also build per-type sheets/missing_<type>_NN.png from the '
                         'keyword table (see MISSING_TYPES in this file)')
    ap.add_argument('--missing-sheet-cap', type=int, default=60,
                    help='max tiles per missing-type sheet set (default 60)')
    ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--phash-dist', type=int, default=8,
                    help='max Hamming distance (of 256) between ink silhouettes to merge')
    args = ap.parse_args()

    t0 = time.time()
    n_grey = 0
    out = os.path.abspath(args.out)
    svg_dir = os.path.join(out, 'svg')
    thumbs_dir = os.path.join(out, 'thumbs')
    sheets_dir = os.path.join(out, 'sheets')
    for d in (svg_dir, thumbs_dir, sheets_dir):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    selects = tuple(x.strip() for x in args.select.split(',') if x.strip())
    for x in selects:
        if x not in SELECTIONS:
            ap.error('unknown --select %r (choose from %s)' % (x, ', '.join(SELECTIONS)))
    skip_heur = tuple(x.strip() for x in args.skip_heuristics.split(',') if x.strip())

    exclude_keys, ref_geom, ref_ink = set(), set(), []
    if args.exclude_ids_from:
        exclude_keys, ref_geom, ref_ink = load_exclusions(args.exclude_ids_from,
                                                          skip_render=args.no_render)
        print('exclusions: %d figures, %d geometry hashes, %d reference thumbnails'
              % (len(exclude_keys), len(ref_geom), len(ref_ink)), flush=True)

    figs = select_figures(args.index, args.extracted_dir, args.semantics,
                          args.ids, args.limit, selects=selects,
                          exclude_keys=exclude_keys)
    jobs = []
    for f in figs:
        meta = {k: v for k, v in f.items() if k != 'files'}
        for i, (rel, path) in enumerate(f['files']):
            jobs.append((meta, rel, path, i, skip_heur))
    print('figures %d   source files %d   jobs=%d' % (len(figs), len(jobs), args.jobs), flush=True)

    results = []
    if args.jobs > 1:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(args.jobs) as pool:
            for i, r in enumerate(pool.imap_unordered(process_file, jobs, chunksize=2)):
                results.append(r)
                if (i + 1) % 40 == 0:
                    print('  parsed %d/%d  (%.0fs)' % (i + 1, len(jobs), time.time() - t0), flush=True)
    else:
        for i, j in enumerate(jobs):
            results.append(process_file(j))

    failures = [(r['paper_id'], r['fig'], r['file'], r['error']) for r in results if r.get('error')]
    n_elems = sum(r['n_elems'] for r in results)
    cls_tot = Counter()
    for r in results:
        cls_tot.update(r['cls'])
    raw = [c for r in results for c in r['candidates']]
    bitmaps = [b for r in results for b in r['bitmaps']]
    print('parsed: elements=%d  raw candidates=%d  bitmaps=%d  failures=%d  (%.0fs)'
          % (n_elems, len(raw), len(bitmaps), len(failures), time.time() - t0), flush=True)

    # ---- stage 1: geometry dedupe -------------------------------------------
    by_geom = defaultdict(list)
    for c in raw:
        by_geom[c['geom_hash']].append(c)

    def rep_of(members, heur=None):
        """Largest member, but never one whose own label differs from the
        group's label (otherwise an `arrowhead` group can end up illustrated by
        the biggest thing that happened to merge into it)."""
        pool = [m for m in members if m['heuristic'] == heur] if heur else []
        return max(pool or members,
                   key=lambda c: (c['w_pt'] * c['h_pt'], c['n_elements']))

    stage1 = []
    n_ref_geom_drop = 0
    for gh, members in by_geom.items():
        if gh in ref_geom:
            n_ref_geom_drop += 1        # identical part already in the old pool
            continue
        best_h = min((m['heuristic'] for m in members), key=lambda h: HEURISTIC_RANK.get(h, 99))
        rep = dict(rep_of(members, best_h))
        rep['heuristic'] = best_h
        rep['heuristics_seen'] = sorted({m['heuristic'] for m in members})
        rep['group_geom'] = [m['candidate_id'] for m in members]
        rep['geom_hashes'] = [gh]
        rep['colors_all'] = sorted({c for m in members for c in (m['colors'] or [])})[:16]
        stage1.append(rep)
    print('after geometry dedupe: %d%s' % (
        len(stage1),
        ('  (%d dropped as already in the reference pool)' % n_ref_geom_drop)
        if n_ref_geom_drop else ''), flush=True)

    for c in stage1:
        with open(os.path.join(svg_dir, c['candidate_id'] + '.svg'), 'w', encoding='utf-8') as fh:
            fh.write(c['svg'])

    # ---- stage 2: thumbnails + visual dedupe --------------------------------
    reps = stage1
    if not args.no_render and np is not None:
        items = [(c['candidate_id'], c['svg']) for c in stage1]
        print('rendering %d thumbnails...' % len(items), flush=True)
        render_thumbs(items, thumbs_dir)
        from PIL import Image
        # Silhouettes MUST be measured on the white render.  (The grey re-render
        # below makes every cell "ink", which once merged every invisible part
        # with every solid one.)
        # Schematic/style records skip the silhouette dedupe entirely: every
        # connector sample is "a horizontal line" and every container corner is
        # "an L", so they would all collapse into a single group.  They are
        # already deduped by their style key in the geometry stage.
        NO_VISUAL = {'connector-style', 'container-title'}
        hashes, inks, keep_idx, invis = [], [], [], []
        for i, c in enumerate(stage1):
            p = os.path.join(thumbs_dir, c['candidate_id'] + '.png')
            if not os.path.exists(p):
                continue
            try:
                bits, ink = ink_bits(Image.open(p))
            except Exception:             # noqa: BLE001
                continue
            if ink == 0:                  # white-on-white: invisible, not mergeable
                invis.append(c)
                continue
            if c['heuristic'] in NO_VISUAL:
                continue
            hashes.append(bits)
            inks.append(ink)
            keep_idx.append(i)
        # give the invisible ones a light-grey ground so reviewers can see them
        if invis:
            print('  re-rendering %d invisible candidates on grey' % len(invis), flush=True)
            render_thumbs([(c['candidate_id'], c['svg']) for c in invis], thumbs_dir,
                          bg='#e6e6e6')
            for c in invis:
                c['thumb_bg'] = 'grey'
            n_grey = len(invis)
        ref_drop_idx = set()
        if ref_ink:
            drop = match_reference(hashes, inks, ref_ink, args.phash_dist)
            if drop:
                ref_drop_idx = {keep_idx[i] for i in drop}
                print('  %d candidates match a part already in the reference pool'
                      % len(drop), flush=True)
                hashes = [h for i, h in enumerate(hashes) if i not in drop]
                inks = [k for i, k in enumerate(inks) if i not in drop]
                keep_idx = [k for i, k in enumerate(keep_idx) if i not in drop]
        print('silhouette grouping %d (dist<=%d)...' % (len(hashes), args.phash_dist), flush=True)
        groups = group_by_phash(hashes, inks, args.phash_dist)
        reps = []
        merged = set()
        for g in groups:
            members = [stage1[keep_idx[i]] for i in g]
            best_h = min((m['heuristic'] for m in members),
                         key=lambda h: HEURISTIC_RANK.get(h, 99))
            rep = dict(rep_of(members, best_h))
            rep['heuristic'] = best_h
            rep['heuristics_seen'] = sorted({h for m in members for h in m['heuristics_seen']})
            rep['group_visual'] = [m['candidate_id'] for m in members]
            rep['group_geom'] = sorted({x for m in members for x in m['group_geom']})
            rep['geom_hashes'] = sorted({x for m in members for x in m.get('geom_hashes', [])})
            rep['colors_all'] = sorted({c for m in members for c in (m.get('colors_all') or [])})[:16]
            reps.append(rep)
            merged.update(keep_idx[i] for i in g)
        ref_dropped = set(ref_drop_idx)
        for i, c in enumerate(stage1):     # style records + un-rendered ones
            if i not in merged and i not in ref_dropped:
                c.setdefault('group_visual', [c['candidate_id']])
                reps.append(c)
        print('after visual dedupe: %d' % len(reps), flush=True)
    else:
        ref_drop_idx = set()
        for c in reps:
            c['group_visual'] = [c['candidate_id']]

    for c in reps:
        srcs = sorted({cid.rsplit('_', 1)[0] for cid in c['group_geom']})
        c['sources'] = srcs[:40]
        c['occurrences'] = len(srcs)
        c['n_members'] = len(c['group_geom'])

    for c in reps:
        hits = match_missing_types(c, c.get('file'))
        c['missing_hits'] = hits
        c['missing_types'] = sorted(hits)
        c['pictogram_score'] = round(pictogram_score(c), 2)

    order_key = lambda c: (HEURISTIC_ORDER.index(c['heuristic'])
                           if c['heuristic'] in HEURISTIC_ORDER else 99,
                           -c['occurrences'], -(c['w_pt'] * c['h_pt']))
    reps.sort(key=order_key)

    # ---- outputs -------------------------------------------------------------
    with open(os.path.join(out, 'candidates.jsonl'), 'w', encoding='utf-8') as fh:
        for c in reps:
            d = {k: v for k, v in c.items() if k != 'svg'}
            d['svg_path'] = 'svg/%s.svg' % c['candidate_id']
            d['thumb_path'] = 'thumbs/%s.png' % c['candidate_id']
            fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    with open(os.path.join(out, 'bitmap_icons.jsonl'), 'w', encoding='utf-8') as fh:
        for b in bitmaps:
            fh.write(json.dumps(b, ensure_ascii=False) + '\n')

    # ---- contact sheets ------------------------------------------------------
    n_sheets = 0
    if not args.no_render:
        per = SHEET_COLS * SHEET_ROWS
        for s in range(0, len(reps), per):
            batch = reps[s:s + per]
            n = s // per + 1
            title = ('sheet %03d  |  %d-%d of %d  |  %s'
                     % (n, s + 1, s + len(batch), len(reps),
                        ', '.join(sorted({b['heuristic'] for b in batch}))))
            draw_sheet(batch, thumbs_dir, os.path.join(sheets_dir, 'sheet_%03d.png' % n), title)
            meta = {}
            for k, rec in enumerate(batch):
                meta[str(k + 1)] = {
                    'candidate_id': rec['candidate_id'],
                    'source': '%s fig%s %s' % (rec['paper_id'], rec['fig'], rec['file']),
                    'subtype': rec.get('subtype'), 'select': rec.get('select'),
                    'source_kind': rec.get('source_kind'),
                    'missing_types': rec.get('missing_types'),
                    'caption': rec.get('caption'),
                    'size_pt': rec['size_pt'], 'n_elements': rec['n_elements'],
                    'occurrences': rec['occurrences'], 'heuristic': rec['heuristic'],
                    'heuristics_seen': rec.get('heuristics_seen'),
                    'hint_text': rec['hint_text'], 'hint_semantics': rec['hint_semantics'],
                    'tool': rec['tool'], 'colors': rec.get('colors_all') or rec['colors'],
                    'sources': rec['sources'], 'extra': rec['extra'],
                    'svg_path': 'svg/%s.svg' % rec['candidate_id'],
                }
            with open(os.path.join(sheets_dir, 'sheet_%03d.json' % n), 'w', encoding='utf-8') as fh:
                json.dump({'sheet': n, 'tiles': meta}, fh, ensure_ascii=False, indent=1)
            n_sheets += 1
        ranked = sorted(reps, key=lambda c: (-c['occurrences'], -(c['w_pt'] * c['h_pt'])))
        top, n_cs = [], 0        # cap the synthetic line samples at 10 tiles
        for c in ranked:
            if c['heuristic'] == 'connector-style':
                if n_cs >= 10:
                    continue
                n_cs += 1
            top.append(c)
            if len(top) >= 60:
                break
        draw_sheet(top, thumbs_dir, os.path.join(sheets_dir, 'top_by_occurrence.png'),
                   'top 60 by occurrence (number of distinct figures using the part)',
                   cols=6, nrows=10)
        with open(os.path.join(sheets_dir, 'top_by_occurrence.json'), 'w', encoding='utf-8') as fh:
            json.dump({str(i + 1): {'candidate_id': c['candidate_id'],
                                    'occurrences': c['occurrences'],
                                    'heuristic': c['heuristic'],
                                    'hint_text': c['hint_text'],
                                    'sources': c['sources']}
                       for i, c in enumerate(top)}, fh, ensure_ascii=False, indent=1)

    # ---- per-type "missing icon family" sheets -------------------------------
    missing_stats = {}
    if args.missing_sheets and not args.no_render:
        per = SHEET_COLS * SHEET_ROWS
        for tname, _rx in MISSING_TYPES:
            hits = [c for c in reps if tname in c['missing_hits']]
            # strongest evidence first, then most pictogram-like, then frequency
            hits.sort(key=lambda c: (MATCH_RANK[c['missing_hits'][tname]],
                                     -c['pictogram_score'], -c['occurrences'],
                                     -(c['w_pt'] * c['h_pt'])))
            shown = hits[:args.missing_sheet_cap]
            by_sub = Counter((c.get('subtype') or '?') for c in hits)
            missing_stats[tname] = {'hits': len(hits), 'shown': len(shown),
                                    'sheets': 0, 'by_subtype': dict(by_sub)}
            for s2 in range(0, len(shown), per):
                batch = shown[s2:s2 + per]
                n = s2 // per + 1
                title = ('missing type: %s  |  %d-%d of %d hits (label-proximity, '
                         'then pictogram-likeness)  |  %s'
                         % (tname, s2 + 1, s2 + len(batch), len(hits),
                            ', '.join('%s=%d' % kv for kv in by_sub.most_common(4))))
                png = os.path.join(sheets_dir, 'missing_%s_%02d.png' % (tname, n))
                draw_sheet(batch, thumbs_dir, png, title)
                tiles = {}
                for k, rec in enumerate(batch):
                    tiles[str(k + 1)] = {
                        'candidate_id': rec['candidate_id'],
                        'source': '%s fig%s %s' % (rec['paper_id'], rec['fig'], rec['file']),
                        'subtype': rec.get('subtype'), 'select': rec.get('select'),
                        'source_kind': rec.get('source_kind'),
                        'size_pt': rec['size_pt'], 'n_elements': rec['n_elements'],
                        'occurrences': rec['occurrences'], 'heuristic': rec['heuristic'],
                        'hint_text': rec['hint_text'], 'hint_wide': rec.get('hint_wide'),
                        'caption': rec.get('caption'), 'tool': rec['tool'],
                        'colors': rec.get('colors_all') or rec['colors'],
                        'missing_types': rec['missing_types'],
                        'matched_on': rec['missing_hits'].get(tname),
                        'pictogram_score': rec['pictogram_score'],
                        'sources': rec['sources'],
                        'svg_path': 'svg/%s.svg' % rec['candidate_id'],
                    }
                with open(png[:-4] + '.json', 'w', encoding='utf-8') as fh:
                    json.dump({'missing_type': tname, 'sheet': n,
                               'total_hits': len(hits),
                               'by_subtype': dict(by_sub), 'tiles': tiles},
                              fh, ensure_ascii=False, indent=1)
                missing_stats[tname]['sheets'] += 1
        print('missing-type sheets: %d types, %d sheets'
              % (sum(1 for v in missing_stats.values() if v['sheets']),
                 sum(v['sheets'] for v in missing_stats.values())), flush=True)

    # ---- summary -------------------------------------------------------------
    per_h_raw = Counter(c['heuristic'] for c in raw)
    per_h_rep = Counter(c['heuristic'] for c in reps)
    hint_top = Counter(c['hint_text'].lower() for c in reps if c['hint_text']).most_common(30)
    tool_cnt = Counter(c['tool'] for c in reps)
    fig_tool = Counter(f['tool'] for f in figs)
    dt = time.time() - t0
    with open(os.path.join(out, 'summary.md'), 'w', encoding='utf-8') as fh:
        w = fh.write
        w('# Candidate part pool -- extraction summary\n\n')
        w('generated by `figgenie-paper-diagram/scripts/distill/extract_parts.py` in %.1f min\n\n' % (dt / 60))
        w('## Corpus\n\n')
        w('- selection: `--select %s`%s\n' % (
            ','.join(selects),
            ('  (skipped heuristics: %s)' % ', '.join(skip_heur)) if skip_heur else ''))
        w('- figures selected: **%d**\n' % len(figs))
        for k, n in Counter(f['select'] for f in figs).most_common():
            sub = Counter(f['subtype'] for f in figs if f['select'] == k)
            w('  - `%s`: %d figures (%s)\n'
              % (k, n, ', '.join('%s=%d' % kv for kv in sub.most_common())))
        if args.exclude_ids_from:
            w('- excluded via `--exclude-ids-from %s`: %d figures already reviewed, '
              '%d reference geometry hashes, %d reference thumbnails\n'
              % (args.exclude_ids_from, len(exclude_keys), len(ref_geom), len(ref_ink)))
            w('  - dropped as already-known parts: %d geometry groups + %d silhouette matches\n'
              % (n_ref_geom_drop, len(ref_drop_idx)))
        w('- figures by subtype: %s\n'
          % ', '.join('%s=%d' % kv for kv in Counter(f['subtype'] for f in figs).most_common()))
        w('- source SVG files parsed: **%d** (multi-panel figures contribute several)\n' % len(jobs))
        w('- drawable elements seen: **%d**\n' % n_elems)
        w('- element classes: %s\n' % ', '.join('%s=%d' % kv for kv in cls_tot.most_common()))
        w('- figures per tool: %s\n\n' % ', '.join('%s=%d' % kv for kv in fig_tool.most_common()))
        w('## Candidates\n\n')
        w('| stage | count |\n|---|---|\n')
        w('| raw (before dedupe) | %d |\n' % len(raw))
        w('| after geometry dedupe | %d |\n' % len(stage1))
        w('| after visual dedupe (representatives) | %d |\n' % len(reps))
        w('\nreduction: %.1f%% of raw candidates collapsed into representatives\n\n'
          % (100.0 * (1 - len(reps) / max(1, len(raw)))))
        w('### per heuristic\n\n| heuristic | raw | representatives |\n|---|---|---|\n')
        for h in HEURISTIC_ORDER:
            w('| %s | %d | %d |\n' % (h, per_h_raw.get(h, 0), per_h_rep.get(h, 0)))
        w('\n### representatives per tool\n\n')
        w(', '.join('%s=%d' % kv for kv in tool_cnt.most_common()) + '\n\n')
        w('## Most frequent hint_text values (top 30)\n\n')
        for t, n in hint_top:
            w('- `%s` x%d\n' % (t[:70], n))
        if missing_stats:
            w('\n## Missing icon families (keyword recall)\n\n')
            w('A hit means the text within %g print-pt of the part, its figure caption, '
              'the semantic icon hint or the file name matches that family\'s keyword '
              'regex (see `MISSING_TYPES` in the script).  It is a RECALL aid, not a '
              'classification -- reviewers still have to look.\n\n' % TH['hint_wide_pt'])
            w('| missing type | hits | on sheets | sheets | topology | architecture | other subtypes |\n')
            w('|---|---|---|---|---|---|---|\n')
            for tname, _rx in MISSING_TYPES:
                st = missing_stats.get(tname) or {}
                bs = st.get('by_subtype') or {}
                other = ', '.join('%s=%d' % kv for kv in
                                  sorted(((k, v) for k, v in bs.items()
                                          if k not in ('topology', 'architecture')),
                                         key=lambda kv: -kv[1])[:4]) or '-'
                w('| %s | %d | %d | %d | %d | %d | %s |\n'
                  % (tname, st.get('hits', 0), st.get('shown', 0), st.get('sheets', 0),
                     bs.get('topology', 0), bs.get('architecture', 0), other))
            w('\nSheets: `sheets/missing_<type>_NN.png` + `.json` (<= %d tiles per type). '
              'Tiles are ordered by how close the matching text sits to the part '
              '(label touching it > text within %g pt > semantic hint > file name > '
              'caption), then by a pictogram-likeness score (curved, compact, '
              'multi-element parts first), then by frequency -- ordering by frequency '
              'alone put plain boxes and arrows on top.  Every tile records the source '
              'figure\'s subtype and, for PDF-extracted figures, a `[pdf]` marker.\n'
              % (args.missing_sheet_cap, TH['hint_wide_pt']))
        w('\n## Bitmap icons (recorded, not extracted)\n\n')
        w('- `<image>` elements: **%d** in %d figures\n'
          % (len(bitmaps), len({(b['paper_id'], b['fig']) for b in bitmaps})))
        w('\n## Review assets\n\n')
        w('- `svg/` %d standalone candidate SVGs (all geometry-deduped candidates)\n' % len(stage1))
        w('- `thumbs/` %d 120x120 PNGs, one per candidate SVG (%d rendered on light '
          'grey because they are white-on-white)\n' % (len(stage1), n_grey))
        w('- `candidates.jsonl` one line per representative: `occurrences` counts the '
          'distinct figures using the part, `sources` lists them (capped at 40 entries, '
          '`occurrences` is always the true count), `group_geom` / `group_visual` list '
          'the merged candidate ids and `colors_all` every colour seen in the group\n')
        w('- `sheets/sheet_NNN.png` + `.json`, %d sheets of 30 tiles, ordered by heuristic then occurrences\n' % n_sheets)
        w('- `sheets/top_by_occurrence.png` -- 60 most frequent parts\n')
        if any(f['source_kind'] == 'pdf' for f in figs):
            w('\n### PDF-extracted sources\n\n')
            w('%d of the %d figures have no author source SVG, so the figure region '
              'extracted from the paper PDF is used instead.  Those are already at '
              'print size (scale = 1).  Caveats: the extracted region can carry a '
              'caption line or a sliver of body text, and `mixed` figures embed '
              'rasterised parts as `<image>` (recorded in bitmap_icons.jsonl, never '
              'vectorised).  Stray text only reaches `hint_text`/`hint_wide`, never the '
              'icon clusters, which are vector-only; the same 4-90pt size window and '
              '30-element cap that reject whole sub-panels also reject text blocks and '
              'figure fragments.  Tiles from these figures are marked `[pdf]`.\n'
              % (sum(1 for f in figs if f['source_kind'] == 'pdf'), len(figs)))
        w('\n## Print-scale confidence\n\n')
        w('`scale = style.size.w / source viewBox width`; every threshold above is in print pt.\n\n')
        for k, n in Counter(f['scale_note'] for f in figs).most_common():
            w('- `%s`: %d figures\n' % (k, n))
        w('\n`single-aspect-mismatch` = the printed aspect differs from the source '
          'viewBox by more than 25% (cropped or partially reused source); those use '
          'the geometric mean of the width and height scales, so their pt sizes are '
          'approximate.\n')
        w('\n## Thresholds in effect\n\n```json\n%s\n```\n' % json.dumps(TH, indent=2))
        w(TUNING_NOTES)
        w('\n## Failures (%d)\n\n' % len(failures))
        for pid, fig, rel, err in failures[:40]:
            w('- %s fig%s %s -- %s\n' % (pid, fig, rel, err))
    print('done in %.1f min -> %s' % (dt / 60, out), flush=True)


if __name__ == '__main__':
    main()
