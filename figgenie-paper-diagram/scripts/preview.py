#!/usr/bin/env python3
"""Build a self-contained HTML debug page for a figure: the SVG at 1×/2×/4×, an optional lint overlay,
a pt ruler/grid, element inspector (hover shows id, kind, box in pt) and the lint findings list.

  python3 scripts/preview.py fig.svg [--lint fig.lint.json] [--spec fig.json] [-o fig.preview.html]

Open the HTML in any browser (no server needed; fonts from assets/fonts and the figure's local bitmaps are
embedded, so the page works wherever it is written). Use it when the PNG self-check is not enough — e.g. to hover
an element and read its exact coordinates.
"""
import argparse, html, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _svgkit as K

TEMPLATE = r"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>
body{{margin:0;font:13px/1.4 -apple-system,Helvetica,Arial,sans-serif;background:#f4f4f6;color:#222}}
header{{padding:8px 14px;background:#fff;border-bottom:1px solid #ddd;display:flex;gap:14px;align-items:center;flex-wrap:wrap}}
header b{{font-size:14px}} header label{{user-select:none}}
main{{display:grid;grid-template-columns:1fr 340px;gap:12px;padding:12px}}
.stage{{background:#fff;border:1px solid #ddd;padding:16px;overflow:auto;position:relative}}
.stage svg.fig{{display:block;box-shadow:0 0 0 1px #bbb}}
aside{{background:#fff;border:1px solid #ddd;padding:10px;font-size:12px;max-height:90vh;overflow:auto}}
aside h3{{margin:4px 0 6px;font-size:13px}}
.f{{padding:4px 6px;border-left:3px solid #999;margin:3px 0;background:#fafafa;cursor:pointer}}
.f.error{{border-color:#e00000}} .f.warn{{border-color:#ff8c00}} .f.info{{border-color:#2f7bd6}}
.f.on{{background:#fff3cd}}
#tip{{position:fixed;pointer-events:none;background:#222;color:#fff;padding:4px 7px;border-radius:3px;font-size:11px;display:none;z-index:9;white-space:pre}}
.hl{{outline:1.2px solid #d00;outline-offset:0}}
{fontcss}
</style></head><body>
<header><b>{title}</b> <span>{W:.1f} × {H:.1f} pt</span>
<label><input type="range" id="zoom" min="1" max="6" step="0.5" value="2"> zoom <span id="zv">2×</span></label>
<label><input type="checkbox" id="grid" checked> 10 pt grid</label>
<label><input type="checkbox" id="ov" checked> lint overlay</label>
<label><input type="checkbox" id="ids"> show ids</label>
<span id="stat"></span></header>
<main>
<div class="stage" id="stage">{svg}</div>
<aside><h3>Findings ({nerr} errors, {nwarn} warnings)</h3>{findings}<h3>Spec</h3><pre style="white-space:pre-wrap;font-size:11px">{spec}</pre></aside>
</main><div id="tip"></div>
<script>
const W={W},H={H};const svg=document.querySelector('svg.fig');const stage=document.getElementById('stage');
svg.removeAttribute('width');svg.removeAttribute('height');
function setZoom(z){{svg.style.width=(W*z)+'px';svg.style.height=(H*z)+'px';document.getElementById('zv').textContent=z+'×';}}
const zoom=document.getElementById('zoom');zoom.oninput=()=>setZoom(parseFloat(zoom.value));setZoom(2);
const NS='http://www.w3.org/2000/svg';
const grid=document.createElementNS(NS,'g');grid.id='pv-grid';grid.setAttribute('pointer-events','none');
for(let x=0;x<=W;x+=10){{const l=document.createElementNS(NS,'line');l.setAttribute('x1',x);l.setAttribute('x2',x);l.setAttribute('y1',0);l.setAttribute('y2',H);l.setAttribute('stroke',x%50?'#e8e8ff':'#c8c8ff');l.setAttribute('stroke-width',x%50?0.15:0.3);grid.appendChild(l);}}
for(let y=0;y<=H;y+=10){{const l=document.createElementNS(NS,'line');l.setAttribute('y1',y);l.setAttribute('y2',y);l.setAttribute('x1',0);l.setAttribute('x2',W);l.setAttribute('stroke',y%50?'#e8e8ff':'#c8c8ff');l.setAttribute('stroke-width',y%50?0.15:0.3);grid.appendChild(l);}}
svg.insertBefore(grid,svg.firstChild);
document.getElementById('grid').onchange=e=>grid.style.display=e.target.checked?'':'none';
const ov=svg.querySelector('#lint-overlay');document.getElementById('ov').onchange=e=>{{if(ov)ov.style.display=e.target.checked?'':'none';}};
const idl=document.createElementNS(NS,'g');idl.id='pv-ids';idl.style.display='none';idl.setAttribute('pointer-events','none');
for(const g of svg.querySelectorAll('g[id]')){{if(g.id.startsWith('pv-')||g.id==='lint-overlay')continue;const r=g.getBBox();const t=document.createElementNS(NS,'text');t.setAttribute('x',r.x+0.5);t.setAttribute('y',r.y-0.8);t.setAttribute('font-size','3');t.setAttribute('fill','#0a58ca');t.setAttribute('font-family','Arimo,Arial,sans-serif');t.textContent=g.id;idl.appendChild(t);}}
svg.appendChild(idl);document.getElementById('ids').onchange=e=>idl.style.display=e.target.checked?'':'none';
const tip=document.getElementById('tip');
svg.addEventListener('mousemove',e=>{{const el=e.target.closest('g[id],text,rect,path,circle,ellipse,line,polygon,polyline');if(!el||el.closest('#pv-grid,#lint-overlay,#pv-ids')){{tip.style.display='none';return;}}
 const r=el.getBoundingClientRect(),s=svg.getBoundingClientRect(),z=s.width/W;const g=el.closest('g[id]');
 tip.textContent=(g?g.id+(g.dataset.kind?' ('+g.dataset.kind+')':'')+'\n':'')+el.tagName+(el.id&&el.id!==(g&&g.id)?' #'+el.id:'')+(el.tagName==='text'?' "'+el.textContent.trim()+'"':'')+'\nx '+((r.left-s.left)/z).toFixed(1)+'  y '+((r.top-s.top)/z).toFixed(1)+'  w '+(r.width/z).toFixed(1)+'  h '+(r.height/z).toFixed(1)+' pt';
 tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px';tip.style.display='block';}});
svg.addEventListener('mouseleave',()=>tip.style.display='none');
document.querySelectorAll('.f').forEach(d=>d.onclick=()=>{{document.querySelectorAll('.hl').forEach(x=>x.classList.remove('hl'));document.querySelectorAll('.f.on').forEach(x=>x.classList.remove('on'));d.classList.add('on');
 for(const id of (d.dataset.ids||'').split('|')){{if(!id)continue;const el=svg.getElementById(id);if(el)el.classList.add('hl');}}}});
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg'); ap.add_argument('--lint'); ap.add_argument('--spec'); ap.add_argument('-o', '--out')
    a = ap.parse_args()
    p = Path(a.svg); svg = p.read_text(encoding='utf-8')
    vb = K.parse_viewbox(svg) or [0, 0, 300, 200]
    lint = json.loads(Path(a.lint).read_text(encoding='utf-8')) if a.lint and Path(a.lint).exists() else None
    findings = (lint or {}).get('findings', [])
    if findings and '<g id="lint-overlay"' not in svg:
        from lint import annotate  # noqa
        tmp = p.with_suffix('.lint.svg'); annotate(svg, findings, tmp); svg = tmp.read_text(encoding='utf-8')
    svg = K.svg_for_chromium(svg, base_dir=p.resolve().parent)          # local bitmaps inlined, URLs not fetched
    svg = svg.replace('<svg ', '<svg class="fig" ', 1)
    keys = {K.resolve_font(f) for f in K.families_in_svg(svg)}
    fontcss = K.font_face_css([k for k in keys if k])
    fh = ''.join(f'<div class="f {f["severity"]}" data-ids="{html.escape("|".join(f.get("elements") or []))}"><b>{f["code"]}</b> {html.escape(f["message"])}</div>' for f in findings) or '<div>no findings</div>'
    spec = Path(a.spec).read_text(encoding='utf-8')[:4000] if a.spec and Path(a.spec).exists() else '(no spec given)'
    out = Path(a.out) if a.out else p.with_suffix('.preview.html')
    out.write_text(TEMPLATE.format(title=p.name, W=vb[2], H=vb[3], svg=svg, fontcss=fontcss, findings=fh, spec=html.escape(spec),
                                   nerr=sum(1 for f in findings if f['severity'] == 'error'), nwarn=sum(1 for f in findings if f['severity'] == 'warn')), encoding='utf-8')
    print('wrote', out)


if __name__ == '__main__':
    main()
