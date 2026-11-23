#!/usr/bin/env python3
"""Build a single-file HTML page to review exemplar candidates per template (open it locally in a browser).

    python3 review_candidates.py --candidates <dir>/candidates.json --out <dir>/review.html

The page shows one tab per template, a thumbnail grid (print-size PNG from the PDF, or the author
preview PNG when the figure only exists as a source file), and two toggles per figure:
  ✗ drop   — exclude this figure from the template's exemplars
  ★ star   — mark it as a must-see exemplar (goes into the layouts.md exemplar table)
State is kept in localStorage; the text box at the bottom always holds the current decisions as JSON
({"drop": {template: [ids]}, "star": {template: [ids]}}) so it can be copied back to the assistant.
Image paths are absolute file:// paths into lab/extracted/, so the page only works on this machine.
"""
import argparse, html, json
from pathlib import Path

CSS = """
body{font:13px/1.35 -apple-system,Helvetica,Arial,sans-serif;margin:0;background:#fafafa;color:#222}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:8px 12px;z-index:5}
.tabs button{margin:2px;padding:4px 8px;border:1px solid #bbb;background:#f4f4f4;border-radius:4px;cursor:pointer}
.tabs button.on{background:#1f5fbf;color:#fff;border-color:#1f5fbf}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:10px;padding:10px}
.tile{background:#fff;border:1px solid #ddd;border-radius:6px;padding:6px;position:relative}
.tile.drop{opacity:.35;background:#fee}
.tile.star{border-color:#e6a700;box-shadow:0 0 0 2px #ffe08a inset}
.tile img{width:100%;max-height:280px;object-fit:contain;background:#fff;border:1px solid #eee}
.meta{font-size:12px;color:#444;margin-top:4px}
.meta b{color:#000}
.ctl{position:absolute;top:8px;right:8px;display:flex;gap:4px}
.ctl button{border:1px solid #999;background:#fff;border-radius:4px;padding:2px 7px;cursor:pointer;font-size:14px}
.ctl button.on{background:#c00;color:#fff;border-color:#c00}
.ctl button.staron{background:#e6a700;color:#fff;border-color:#e6a700}
textarea{width:98%;height:120px;font:12px monospace;margin:10px}
.summ{font-size:12px;color:#555}
"""

JS = """
const KEY='exemplar-review-v1';
let state=JSON.parse(localStorage.getItem(KEY)||'{"drop":{},"star":{}}');
function save(){localStorage.setItem(KEY,JSON.stringify(state));document.getElementById('out').value=JSON.stringify(state,null,1);}
function has(k,t,id){return (state[k][t]||[]).includes(id);}
function toggle(k,t,id){const a=state[k][t]||[];const i=a.indexOf(id);if(i>=0)a.splice(i,1);else a.push(id);state[k][t]=a;save();render();}
let cur=Object.keys(DATA)[0];
function render(){
  const tabs=document.getElementById('tabs');tabs.innerHTML='';
  for(const t of Object.keys(DATA)){const b=document.createElement('button');const d=(state.drop[t]||[]).length;const s=(state.star[t]||[]).length;
    b.textContent=`${t} ${DATA[t].length-d}/${DATA[t].length}`+(s?` ★${s}`:'');b.className=t===cur?'on':'';b.onclick=()=>{cur=t;render();};tabs.appendChild(b);}
  const g=document.getElementById('grid');g.innerHTML='';
  document.getElementById('summ').textContent=SUMM[cur]||'';
  for(const c of DATA[cur]){const d=has('drop',cur,c.id),s=has('star',cur,c.id);
    const el=document.createElement('div');el.className='tile'+(d?' drop':'')+(s?' star':'');
    const img=c.pdf_png||c.src_png;
    el.innerHTML=`<img loading="lazy" src="file://${img}" title="${c.id}">`+
      `<div class="meta"><b>#${c.rank} ${c.id}</b> · ${c.venue} · corpus:${c.corpus_template} · conf:${c.confidence} · weak:${c.weaknesses} · ${c.text_density} · ${c.column}/${c.direction} · svg:${c.svg}<br>${esc(c.why)}<br><i>${esc(c.one_liner)}</i></div>`+
      `<div class="ctl"><button class="${s?'staron':''}" title="must-see">★</button><button class="${d?'on':''}" title="drop">✗</button></div>`;
    const [bs,bd]=el.querySelectorAll('.ctl button');bs.onclick=()=>toggle('star',cur,c.id);bd.onclick=()=>toggle('drop',cur,c.id);
    g.appendChild(el);}
  document.getElementById('out').value=JSON.stringify(state,null,1);
}
function esc(s){return (s||'').replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));}
function copyOut(){navigator.clipboard&&navigator.clipboard.writeText(document.getElementById('out').value);}
function resetAll(){if(confirm('Clear all decisions?')){state={drop:{},star:{}};save();render();}}
render();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(a.candidates))
    data = {}
    for c in d["candidates"]:
        data.setdefault(c["template"], []).append(c)
    summ = {t: f"pool {s['pool']} · quota {s['quota']} · chosen {s['chosen']} · venues {s['venues']}"
            + (f" · excluded (text as paths / no SVG): {', '.join(i for i, _ in s['excluded'])}" if s.get("excluded") else "")
            for t, s in d["summary"].items()}
    page = ("<!doctype html><meta charset='utf-8'><title>Exemplar candidates</title><style>" + CSS + "</style>"
            "<header><div class='tabs' id='tabs'></div><div class='summ' id='summ'></div></header>"
            "<div class='grid' id='grid'></div>"
            "<div style='padding:0 10px'><button onclick='copyOut()'>copy decisions JSON</button> <button onclick='resetAll()'>reset</button></div>"
            "<textarea id='out' readonly></textarea>"
            "<script>const DATA=" + json.dumps(data, ensure_ascii=False) + ";const SUMM=" + json.dumps(summ, ensure_ascii=False) + ";" + JS + "</script>")
    Path(a.out).write_text(page, encoding="utf-8")
    print(f"wrote {a.out}: {sum(len(v) for v in data.values())} tiles in {len(data)} tabs")


if __name__ == "__main__":
    main()
