#!/usr/bin/env python3
"""Check a cutting agent's output in an AI parts-mining package (ai_parts_pool.py), figure by figure.

  python3 scripts/distill/ai_parts_check.py --agent ai-parts/pilot/agents/agent_haiku [--figure <fig_id>]

Reads review.jsonl, progress.json, cuts/<fig>/cuts.json and the package's checklist (vocab_v2) and prints every problem:
bad JSON lines, missing fields, unknown family (not a vocabulary id and not new:<slug>), unknown kind / groups /
convention / license values, a ref with no cut SVG, duplicate names, cuts without a review line, figures done without
review lines. Exit code 1 when there are problems. Run it after every figure.
"""
import argparse, collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
KINDS = ('icon', 'shape', 'motif', 'device')
REQ = ('figure', 'ref', 'keep', 'name', 'kind', 'family', 'depicts', 'groups', 'style', 'quality', 'tags')
CONV = ('common', 'variant', 'own', '')
LIC = ('ok', 'stock', 'emoji', 'logo', '')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--agent', required=True); ap.add_argument('--figure', default=None); a = ap.parse_args()
    adir = Path(a.agent); pkg = adir.parents[1]
    voc = {e['id'] for e in json.load(open(ROOT / 'ai-corpus' / 'typedisc' / 'tagmerge' / 'v2' / 'vocab_v2.json', encoding='utf-8'))['entries'] if e['cls'] in ('idiom', 'part', 'modifier')}
    groups = set(json.load(open(pkg / 'groups.json', encoding='utf-8'))) if (pkg / 'groups.json').exists() else set()
    figs = {f['id'] for f in json.load(open(adir / 'figures.json', encoding='utf-8'))}
    problems, lines, names = [], [], collections.Counter()
    rp = adir / 'review.jsonl'
    if rp.exists():
        for i, raw in enumerate(open(rp, encoding='utf-8'), 1):
            if not raw.strip(): continue
            try: r = json.loads(raw)
            except json.JSONDecodeError as e: problems.append(f'review.jsonl:{i}: bad JSON ({e})'); continue
            if a.figure and r.get('figure') != a.figure: continue
            lines.append(r)
            for k in REQ:
                if k not in r: problems.append(f"review.jsonl:{i} ({r.get('ref')}): missing `{k}`")
            if r.get('figure') not in figs: problems.append(f"review.jsonl:{i}: figure {r.get('figure')!r} is not one of yours")
            fam = r.get('family') or ''
            if not (fam in voc or fam.startswith('new:')): problems.append(f"review.jsonl:{i} ({r.get('ref')}): family {fam!r} is neither a vocabulary id nor new:<slug>")
            if r.get('kind') not in KINDS: problems.append(f"review.jsonl:{i} ({r.get('ref')}): kind {r.get('kind')!r}")
            bad = [g for g in (r.get('groups') or []) if g not in groups]
            if bad: problems.append(f"review.jsonl:{i} ({r.get('ref')}): groups {bad} are not figure kinds")
            if (r.get('convention') or '') not in CONV: problems.append(f"review.jsonl:{i} ({r.get('ref')}): convention {r.get('convention')!r}")
            if (r.get('license') or '') not in LIC: problems.append(f"review.jsonl:{i} ({r.get('ref')}): license {r.get('license')!r}")
            if r.get('keep') is True: names[r.get('name')] += 1
            cj = adir / 'cuts' / str(r.get('figure')) / 'cuts.json'
            if r.get('source', 'cut') == 'cut':
                if not cj.exists(): problems.append(f"review.jsonl:{i}: no cuts.json for {r.get('figure')}")
                else:
                    recs = {c['name']: c for c in json.load(open(cj, encoding='utf-8'))['cuts']}
                    c = recs.get(r.get('ref'))
                    if not c: problems.append(f"review.jsonl:{i}: ref {r.get('ref')!r} is not a cut of {r.get('figure')}")
                    elif not c.get('svg') and r.get('keep') is True: problems.append(f"review.jsonl:{i}: kept ref {r.get('ref')!r} has no SVG (warnings: {c.get('warnings')})")
    for n, c in names.items():
        if c > 1: problems.append(f'name {n!r} used {c} times among kept parts')
    reviewed = collections.defaultdict(set)
    for r in lines: reviewed[r.get('figure')].add(r.get('ref'))
    for cj in sorted((adir / 'cuts').glob('*/cuts.json')):
        fid = cj.parent.name
        if a.figure and fid != a.figure: continue
        for c in json.load(open(cj, encoding='utf-8'))['cuts']:
            if c.get('svg') and c['name'] not in reviewed[fid]: problems.append(f'{fid}: cut {c["name"]!r} has no review line (keep or reject it)')
    done = []
    if (adir / 'progress.json').exists():
        done = json.load(open(adir / 'progress.json', encoding='utf-8')).get('done', [])
        for fid in done:
            if fid not in reviewed and not (adir / 'cuts' / fid / 'cuts.json').exists(): problems.append(f'{fid} is in progress.json but has no cuts and no review lines (fine only if discoveries.md says why)')
    kept = sum(1 for r in lines if r.get('keep') is True)
    print(f'{adir.name}: {len(done)}/{len(figs)} figures done, {len(lines)} review lines, {kept} kept, {len(problems)} problems')
    for p in problems[:80]: print('  PROBLEM', p)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
