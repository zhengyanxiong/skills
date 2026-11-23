// TeX → standalone SVG (paths only, no font cache) for every entry of a JSON job file.
//   node tex2svg.mjs jobs.json out.json
// jobs.json: {"key": "\\pi_\\theta^{(0)}"} or {"key": {"tex": "...", "display": false}}
// out.json:  {"key": {"tex": "...", "display": false, "svg": "<svg viewBox=\"x0 y0 w h\" ...>…</svg>"}}
// The viewBox is in 1/1000 em: at font size s pt multiply every number by s/1000.
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {SVG} from 'mathjax-full/js/output/svg.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import {AllPackages} from 'mathjax-full/js/input/tex/AllPackages.js';
import fs from 'fs';
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
// 'noundefined' would typeset an unknown macro as red text instead of failing; we want typos reported.
const packages = AllPackages.filter(p => p !== 'noundefined');
const html = mathjax.document('', {InputJax: new TeX({packages}), OutputJax: new SVG({fontCache: 'none'})});
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = {};
for (const [key, job] of Object.entries(jobs)) {
  const tex = typeof job === 'string' ? job : job.tex;
  const display = typeof job === 'string' ? false : !!job.display;
  try {
    const node = html.convert(tex, {display, em: 10, ex: 4.42, containerWidth: 100000});
    out[key] = {tex, display, svg: adaptor.innerHTML(node)};
  } catch (e) {
    out[key] = {tex, display, error: String(e.message || e)};
  }
}
fs.writeFileSync(process.argv[3], JSON.stringify(out));
