#!/usr/bin/env python3
"""Re-cut the reviewed figures of a parts-mining package with the current cut_parts.py, keeping the element
selections the reviewers saw, and report what changed.

  python3 scripts/distill/mech_recut.py --package mech-parts/pilot-evolution [--agents agent_1,agent_2] [--figs a,b]

For each agent directory: cuts/ is copied once to cuts_v1/ (never overwritten); every figure that has lines in
review.jsonl is re-cut from requests/<fig>.json. Figures whose current cuts come from the first tool (records without
a "geometry" field) get "geometry": "legacy" on each request, so the estimated boxes the reviewer's cut was made with
select the same elements. The new records are compared with the records before the re-cut by name and element
count, and the export (text hidden) and text fidelity warnings of every cut are collected. Figures that were cut but
not reviewed are left alone. Writes <package>/recut_report.json (an earlier report is kept once as recut_report_v1.json).
"""
import argparse, json, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cut_parts as C              # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--package', required=True); ap.add_argument('--agents', default='')
    ap.add_argument('--figs', default='', help='comma-separated figure ids (default: every reviewed figure)')
    a = ap.parse_args()
    t0 = time.time()
    pkg = Path(a.package)
    wanted = {x.strip() for x in a.agents.split(',') if x.strip()}
    only = {x.strip() for x in a.figs.split(',') if x.strip()}
    report = {'figures': [], 'mismatches': [], 'lost': [], 'fidelity_warnings': [], 'text_warnings': []}
    for adir in sorted(p for p in (pkg / 'agents').glob('agent_*') if p.is_dir()):
        if wanted and adir.name not in wanted: continue
        rp = adir / 'review.jsonl'
        if not rp.exists() or not (adir / 'requests').exists(): continue
        figs = sorted({json.loads(l)['figure'] for l in open(rp, encoding='utf-8') if l.strip()})
        if (adir / 'cuts').exists() and not (adir / 'cuts_v1').exists():
            shutil.copytree(adir / 'cuts', adir / 'cuts_v1')
        for fig in figs:
            if only and fig not in only: continue
            req_path = adir / 'requests' / (fig + '.json')
            if not req_path.exists(): continue
            reqs = json.loads(req_path.read_text(encoding='utf-8'))
            if isinstance(reqs, dict): reqs = reqs.get('requests') or reqs.get('cuts') or []
            changed = False
            # only cuts made by the first tool (records without a "geometry" field) keep their estimated-box selections;
            # figures cut since then use measured geometry and must not be converted
            cur_p = adir / 'cuts' / fig / 'cuts.json'
            cur = json.load(open(cur_p, encoding='utf-8')).get('cuts', []) if cur_p.exists() else []
            if cur and all('geometry' not in c for c in cur):
                for q in reqs:
                    if 'geometry' not in q: q['geometry'] = 'legacy'; changed = True
            if changed: req_path.write_text(json.dumps(reqs, ensure_ascii=False, indent=1), encoding='utf-8')
            if not cur:
                old_p = adir / 'cuts_v1' / fig / 'cuts.json'
                cur = json.load(open(old_p, encoding='utf-8'))['cuts'] if old_p.exists() else []
            prev = {c['name']: c for c in cur}
            recs = C.cut_figure(pkg / 'figs' / fig, reqs, adir, quiet=True)
            new = {r['name']: r for r in recs}
            for name, o in prev.items():
                if not o.get('svg'): continue
                n = new.get(name)
                if not n or not n.get('svg'): report['lost'].append([adir.name, fig, name]); continue
                if n['n_elements'] != o['n_elements']: report['mismatches'].append([adir.name, fig, name, o['n_elements'], n['n_elements']])
            for n in recs:
                if (n.get('fidelity_diff') or 0) > C.FIDELITY_WARN: report['fidelity_warnings'].append([adir.name, fig, n['name'], n['fidelity_diff']])
                if (n.get('text_fidelity_diff') or 0) > C.TEXT_FIDELITY_WARN: report['text_warnings'].append([adir.name, fig, n['name'], n['text_fidelity_diff']])
            f = {'agent': adir.name, 'figure': fig, 'cuts': sum(1 for r in recs if r.get('svg')),
                 'max_fidelity_diff': max([r.get('fidelity_diff') or 0 for r in recs] or [0]),
                 'max_text_fidelity_diff': max([r.get('text_fidelity_diff') or 0 for r in recs] or [0])}
            report['figures'].append(f)
            print('%s %-24s %2d cuts  max diff %.3f  text %.3f' % (adir.name, fig, f['cuts'], f['max_fidelity_diff'], f['max_text_fidelity_diff']), flush=True)
    report['summary'] = {'figures': len(report['figures']), 'cuts': sum(f['cuts'] for f in report['figures']),
                         'mismatches': len(report['mismatches']), 'lost': len(report['lost']),
                         'fidelity_warnings': len(report['fidelity_warnings']), 'text_warnings': len(report['text_warnings']),
                         'minutes': round((time.time() - t0) / 60, 1)}
    out = pkg / 'recut_report.json'
    if out.exists() and not (pkg / 'recut_report_v1.json').exists(): shutil.copy2(out, pkg / 'recut_report_v1.json')
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(report['summary']))
    for m in report['mismatches'][:20]: print('mismatch', m)
    for m in report['lost'][:20]: print('lost', m)
    for m in report['fidelity_warnings'][:20]: print('fidelity', m)
    for m in report['text_warnings'][:40]: print('text', m)


if __name__ == '__main__':
    main()
