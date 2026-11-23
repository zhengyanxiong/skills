// TeX → MathML for every entry of a JSON job file (used by svg2pptx.py to build PowerPoint equations).
//   node tex2mml.mjs jobs.json out.json      jobs.json as for tex2svg.mjs; out.json: {"key": "<math>…</math>"}
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import {SerializedMmlVisitor} from 'mathjax-full/js/core/MmlTree/SerializedMmlVisitor.js';
import {STATE} from 'mathjax-full/js/core/MathItem.js';
import {AllPackages} from 'mathjax-full/js/input/tex/AllPackages.js';
import fs from 'fs';
const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
// no output jax here: 'bussproofs' needs one (getBBox) and would throw; 'noundefined' would hide typos as red text
const packages = AllPackages.filter(p => p !== 'noundefined' && p !== 'bussproofs');
const html = mathjax.document('', {InputJax: new TeX({packages})});
const visitor = new SerializedMmlVisitor();
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = {};
for (const [key, job] of Object.entries(jobs)) {
  const tex = typeof job === 'string' ? job : job.tex;
  const display = typeof job === 'string' ? false : !!job.display;
  try { out[key] = visitor.visitTree(html.convert(tex, {display, end: STATE.CONVERT}), html); }
  catch (e) { out[key] = null; }
}
fs.writeFileSync(process.argv[3], JSON.stringify(out));
