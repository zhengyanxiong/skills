#!/usr/bin/env python3
"""Shared helpers for the optional formula add-on (tex_measure.py, tex_fill.py, svg2pptx.py).

A formula in a figure is a placeholder group that the author writes by hand:

    <g data-symbol="tex" data-tex="\\hat{J}(\\theta)" data-x="54" data-y="24"
       data-size="6.5" data-anchor="middle" data-fill="#0d0d0d"/>

    data-tex     the TeX (MathJax syntax, AMS packages available); keep it — it is the editable source
    data-x       anchor x in pt; data-anchor = start | middle | end (default start), like text-anchor
    data-y       baseline y in pt (with data-valign="middle": the vertical ink centre instead)
    data-size    font size in pt (default: the root font-size); the em of the formula
    data-fill    colour (default: nearest ancestor fill, else #0d0d0d); data-display="1" for display style
    (legacy spellings data-ax / data-baseline are accepted and rewritten)

tex_fill.py renders every placeholder with MathJax (node, scripts/mathjax) into paths inside the group
and records the measured box as data-w / data-asc / data-desc / data-baseline. Re-running re-renders
from data-tex, so editing the TeX in the SVG and running tex_fill.py again is the whole edit loop.
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from lxml import etree

HERE = Path(__file__).resolve().parent
MATHJAX_DIR = HERE / 'mathjax'
SVG_NS = 'http://www.w3.org/2000/svg'
NSMAP = {'svg': SVG_NS}
INK_DEFAULT = '#0d0d0d'


# ---------------------------------------------------------------- node / MathJax
def node_path():
    return shutil.which('node')


def ensure_mathjax():
    """Return True when scripts/mathjax/node_modules/mathjax-full is usable; try `npm install` once if not."""
    if (MATHJAX_DIR / 'node_modules' / 'mathjax-full').exists():
        return True
    npm = shutil.which('npm')
    if not npm:
        return False
    print(f'[texkit] installing mathjax-full into {MATHJAX_DIR} (one-time, needs network) …', file=sys.stderr)
    r = subprocess.run([npm, 'install', '--no-audit', '--no-fund', '--silent'], cwd=str(MATHJAX_DIR),
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-800:], file=sys.stderr)
    return (MATHJAX_DIR / 'node_modules' / 'mathjax-full').exists()


def _run_mjs(script, jobs):
    node = node_path()
    if not node:
        raise RuntimeError('node is not installed (needed for MathJax); install Node.js ≥ 18 or brew install node')
    if not ensure_mathjax():
        raise RuntimeError(f'mathjax-full is missing: run `npm install` in {MATHJAX_DIR}')
    with tempfile.TemporaryDirectory() as td:
        jin, jout = Path(td) / 'jobs.json', Path(td) / 'out.json'
        jin.write_text(json.dumps(jobs, ensure_ascii=False))
        r = subprocess.run([node, str(MATHJAX_DIR / script), str(jin), str(jout)], capture_output=True, text=True)
        if r.returncode != 0 or not jout.exists():
            raise RuntimeError(f'{script} failed:\n{r.stderr[-1500:]}')
        return json.loads(jout.read_text())


def render_svg(jobs):
    """jobs: {key: tex | {'tex':…, 'display':bool}} → {key: {'tex','display','svg'} | {'error':…}}
    MathJax typesets bad TeX as an error box instead of throwing; such results are reported as errors here."""
    out = _run_mjs('tex2svg.mjs', jobs) if jobs else {}
    for k, r in out.items():
        svg = r.get('svg') or ''
        if 'merror' in svg or 'data-mjx-error' in svg:
            m = re.search(r'data-mjx-error="([^"]*)"', svg) or re.search(r'<title>([^<]*)</title>', svg)
            r['error'] = 'TeX error: ' + (m.group(1) if m else 'MathJax could not typeset this input')
    return out


def render_mathml(jobs):
    """jobs as above → {key: '<math …>…</math>' | None}"""
    return _run_mjs('tex2mml.mjs', jobs) if jobs else {}


# ---------------------------------------------------------------- metrics and markup
def metrics(svg_text, size):
    """(xoff, width, ascent, descent) in pt of a MathJax SVG at font size `size`."""
    x0, y0, w, h = map(float, re.search(r'viewBox="([^"]+)"', svg_text).group(1).split())
    s = size / 1000.0
    return x0 * s, w * s, -y0 * s, (y0 + h) * s


_STRIP_ATTRS = re.compile(r'^data-(?:mml-node|c|mjx-texclass|semantic-[\w-]+|latex(?:item)?)$')


def inner_elements(svg_text, fill):
    """Children of the MathJax `scale(1,-1)` group as lxml elements (MathJax data-* stripped, colour applied)."""
    root = etree.fromstring(svg_text.encode('utf-8'))
    flip = None
    for g in root.iter('{%s}g' % SVG_NS):
        if (g.get('transform') or '').replace(' ', '') == 'scale(1,-1)':
            flip = g; break
    if flip is None:
        raise ValueError('unexpected MathJax markup (no scale(1,-1) group)')
    out = []
    for ch in list(flip):
        for el in ch.iter():
            for a in list(el.attrib):
                if _STRIP_ATTRS.match(a):
                    del el.attrib[a]
            for a in ('fill', 'stroke'):
                if el.get(a) == 'currentColor':
                    el.set(a, fill)
        out.append(ch)
    return out


# ---------------------------------------------------------------- placeholders in a figure
def placeholders(root):
    return [g for g in root.iter('{%s}g' % SVG_NS) if g.get('data-symbol') == 'tex']


def inherited(el, attr, default=None):
    p = el.getparent()
    while p is not None:
        v = p.get(attr)
        if v not in (None, '', 'inherit'):
            return v
        p = p.getparent()
    return default


def params(g, root=None):
    """Normalised placeholder parameters; rewrites legacy attribute names in place."""
    if g.get('data-x') is None and g.get('data-ax') is not None:
        g.set('data-x', g.get('data-ax')); del g.attrib['data-ax']
    if g.get('data-y') is None and g.get('data-baseline') is not None:
        # legacy files recorded the resolved baseline only; adopting it as data-y reproduces the same position
        g.set('data-y', g.get('data-baseline'))
        if g.get('data-valign') == 'middle':
            del g.attrib['data-valign']
    tex = g.get('data-tex')
    if tex is None:
        raise ValueError(f'placeholder without data-tex: {etree.tostring(g)[:80]!r}')
    size = g.get('data-size') or inherited(g, 'font-size') or (root.get('font-size') if root is not None else None) or '6.5'
    fill = g.get('data-fill') or inherited(g, 'fill', INK_DEFAULT)
    if fill in ('none', 'currentColor'):
        fill = INK_DEFAULT
    return dict(tex=tex, x=float(g.get('data-x') or 0), y=float(g.get('data-y') or 0), size=float(size),
                anchor=g.get('data-anchor') or 'start', fill=fill, valign=g.get('data-valign') or 'baseline',
                display=(g.get('data-display') or '0') not in ('0', '', 'false'))


def fill_group(g, svg_text, p):
    """Render one placeholder in place; returns the ink box (x0, y0, x1, y1) in figure pt."""
    xoff, W, asc, desc = metrics(svg_text, p['size'])
    s = p['size'] / 1000.0
    X = {'start': p['x'], 'middle': p['x'] - W / 2, 'end': p['x'] - W}.get(p['anchor'], p['x']) - xoff
    Y = p['y'] + (asc - desc) / 2 if p['valign'] == 'middle' else p['y']
    for ch in list(g):
        g.remove(ch)
    g.set('transform', f'translate({X:.3f},{Y:.3f}) scale({s:.6f})')
    wrap = etree.SubElement(g, '{%s}g' % SVG_NS)
    wrap.set('fill', p['fill']); wrap.set('stroke', p['fill']); wrap.set('stroke-width', '0'); wrap.set('transform', 'scale(1,-1)')
    for el in inner_elements(svg_text, p['fill']):
        wrap.append(el)
    g.set('data-fill', p['fill']); g.set('data-size', f"{p['size']:g}"); g.set('data-anchor', p['anchor'])
    g.set('data-x', f"{p['x']:g}"); g.set('data-y', f"{p['y']:g}")
    g.set('data-w', f'{W:.2f}'); g.set('data-asc', f'{asc:.2f}'); g.set('data-desc', f'{desc:.2f}'); g.set('data-baseline', f'{Y:.2f}')
    x0 = X + xoff
    return (x0, Y - asc, x0 + W, Y + desc)


def strip_group(g):
    for ch in list(g):
        g.remove(ch)
    for a in ('transform', 'data-w', 'data-asc', 'data-desc', 'data-baseline'):
        if a in g.attrib:
            del g.attrib[a]


def ink_box(g):
    """Ink box of an already-filled placeholder from its recorded metrics, or None."""
    try:
        W, asc, desc, base = (float(g.get(k)) for k in ('data-w', 'data-asc', 'data-desc', 'data-baseline'))
        x, anchor = float(g.get('data-x')), g.get('data-anchor') or 'start'
    except (TypeError, ValueError):
        return None
    x0 = {'start': x, 'middle': x - W / 2, 'end': x - W}.get(anchor, x)
    return (x0, base - asc, x0 + W, base + desc)


def parse(path):
    parser = etree.XMLParser(remove_blank_text=False, huge_tree=True)
    return etree.parse(str(path), parser)


def write(tree, path):
    tree.write(str(path), encoding='utf-8', xml_declaration=False)
    # lxml drops the trailing newline
    with open(path, 'ab') as f:
        f.write(b'\n')


# ---------------------------------------------------------------- readable fallback text
_GREEK = {'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε', 'varepsilon': 'ε', 'zeta': 'ζ', 'eta': 'η',
          'theta': 'θ', 'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'pi': 'π', 'rho': 'ρ',
          'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ', 'phi': 'φ', 'varphi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω',
          'Gamma': 'Γ', 'Delta': 'Δ', 'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ', 'Pi': 'Π', 'Sigma': 'Σ', 'Phi': 'Φ', 'Psi': 'Ψ', 'Omega': 'Ω'}
_SYM = {'sum': 'Σ', 'prod': 'Π', 'int': '∫', 'rightarrow': '→', 'to': '→', 'leftarrow': '←', 'longrightarrow': '→', 'Rightarrow': '⇒',
        'mapsto': '↦', 'in': '∈', 'notin': '∉', 'subseteq': '⊆', 'cup': '∪', 'cap': '∩', 'ldots': '…', 'cdots': '⋯', 'cdot': '·',
        'star': '⋆', 'times': '×', 'pm': '±', 'leq': '≤', 'le': '≤', 'geq': '≥', 'ge': '≥', 'neq': '≠', 'ne': '≠', 'approx': '≈',
        'sim': '∼', 'infty': '∞', 'partial': '∂', 'nabla': '∇', 'forall': '∀', 'exists': '∃', 'mid': '|', 'quad': '  ', 'qquad': '    ',
        'langle': '⟨', 'rangle': '⟩', 'lbrace': '{', 'rbrace': '}', 'lbrack': '[', 'rbrack': ']', 'ast': '∗', 'circ': '∘', 'emptyset': '∅'}


def tex_plain(t):
    """One-line readable rendering of a TeX snippet (fallback text for viewers without equation support)."""
    t = t.replace(r'\{', '\x01').replace(r'\}', '\x02')
    t = re.sub(r'\\(?:d|t)?frac\s*\{(.+?)\}\s*\{(.+?)\}', r'(\1)/(\2)', t)
    t = re.sub(r'\\(?:mathrm|mathbf|mathbb|mathcal|mathsf|mathit|textstyle|displaystyle|text|operatorname)\s*\{(.*?)\}', r'\1', t)
    t = re.sub(r'\\(?:hat|widehat|bar|overline|tilde|vec)\s*\{(.+?)\}', r'\1', t)
    t = re.sub(r'\\(?:big|Big|bigg|Bigg|left|right)\b', '', t)
    t = re.sub(r'\\(arg|max|min|exp|log|ln|sin|cos|tan|sup|inf|lim|det)\b', r'\1', t)

    def sym(m):
        k = m.group(1)
        return _GREEK.get(k) or _SYM.get(k) or k
    t = re.sub(r'\\([A-Za-z]+)', sym, t)
    t = t.replace('\\,', '').replace('\\;', ' ').replace('\\!', '').replace('\\ ', ' ')
    t = re.sub(r'\{(.*?)\}', r'\1', t)
    t = t.replace('\x01', '{').replace('\x02', '}')
    return re.sub(r'\s+', ' ', t).strip()
