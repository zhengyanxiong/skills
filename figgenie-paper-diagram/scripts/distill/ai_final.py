#!/usr/bin/env python3
"""Assemble the final AI-family parts set from the mining packages (pilot + waves), for build_symbols.py --append-ai.

  python3 figgenie-paper-diagram/scripts/distill/ai_final.py [--packages ai-parts/pilot ai-parts/wave1 ai-parts/wave2 ai-parts/wave3]
      [--out ai-parts/final]

Reads <package>/result/kept.jsonl (mech_merge.py output: the agents' kept parts after the licence split, the review
drops and the geometry dedupe) of every package and writes under --out:
  svg/<name>.svg    one copy per part, as cut (units: pt at print size, `scale` 1), name unique over all packages
  parts.jsonl       one record per part: the kept fields plus `name` (unique), `name_orig`, `family` (a vocabulary id
                    or `new:<slug>`), `family_status` (vocabulary / new), `theme`, `figure_kinds` (the figure groups
                    the part serves), `domain` (the sub-field of its figure), `source` (paper, venue, tool, package,
                    agent), `svg` (the copy)
  families.json     every family with its theme, class, definition (the vocabulary's, or the agents' for a new one),
                    established flag and count
  stats.md          counts by package, kind, theme, domain, family; the largest files; parts with placeholders
Nothing here writes into the skill; build_symbols.py --append-ai imports parts.jsonl.
"""
import argparse, collections, json, os, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VOCAB = REPO / 'ai-corpus' / 'typedisc' / 'tagmerge' / 'v2' / 'vocab_v2.json'
FIG1 = REPO / 'ai-corpus' / 'lab' / 'fig1_table.jsonl'
PACKAGES = ['ai-parts/pilot', 'ai-parts/wave1', 'ai-parts/wave2', 'ai-parts/wave3']
VENUE = {'aaai': 'AAAI', 'acl': 'ACL', 'cvpr': 'CVPR', 'iclr': 'ICLR', 'icml': 'ICML', 'neurips': 'NeurIPS'}


def jl(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')
    return s or 'part'


def venue_of(pid):
    m = re.match(r'([a-z]+)(\d\d)-', pid or '')
    return f"{VENUE.get(m.group(1), m.group(1).upper())}{m.group(2)}" if m else ''


def new_family_defs(packages):
    """`new:<slug>` definitions from the agents' discoveries (result/discoveries.md of each package)."""
    defs = {}
    pat = re.compile(r'`?(new:[a-z0-9][a-z0-9-]*)`?\**\s*[:—–-]+\s*(.+)')
    for pk in packages:
        p = Path(pk) / 'result' / 'discoveries.md'
        if not p.exists(): continue
        for line in p.read_text(encoding='utf-8').splitlines():
            m = pat.search(line)
            if m and m.group(1) not in defs:
                d = m.group(2).strip().rstrip('.')
                if len(d) > 20: defs[m.group(1)] = d[:240]
    return defs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--packages', nargs='+', default=PACKAGES); ap.add_argument('--out', default='ai-parts/final')
    a = ap.parse_args()
    out = Path(a.out); (out / 'svg').mkdir(parents=True, exist_ok=True)
    voc = {e['id']: e for e in json.load(open(VOCAB, encoding='utf-8'))['entries']}
    tab = {t['paper_id']: t for t in jl(FIG1)} if FIG1.exists() else {}
    newdefs = new_family_defs(a.packages)
    rows = []
    for pk in a.packages:
        p = Path(pk) / 'result' / 'kept.jsonl'
        if not p.exists(): print('warn: no kept.jsonl in', pk, file=sys.stderr); continue
        for r in jl(p): r['_pkg'] = Path(pk).name; rows.append(r)
    used = collections.Counter(); parts = []
    for r in sorted(rows, key=lambda r: (PACKAGES.index(f"ai-parts/{r['_pkg']}") if f"ai-parts/{r['_pkg']}" in PACKAGES else 99, r['figure'], r['name'])):
        base = slug(r['name']); used[base] += 1
        name = base if used[base] == 1 else f'{base}-{used[base]}'
        src = Path(r['svg']); dst = out / 'svg' / f'{name}.svg'
        if not src.exists(): print('warn: missing svg', src, file=sys.stderr); continue
        shutil.copyfile(src, dst)
        pid = r['figure'].split('_fig')[0]; t = tab.get(pid, {})
        fam = r.get('family') or 'other'
        parts.append(dict(name=name, name_orig=r['name'], kind=r.get('kind') or 'motif', category=r.get('category') or '', family=fam,
                          family_status='vocabulary' if fam in voc else ('new' if fam.startswith('new:') else 'other'), family_raw=fam,
                          theme=r.get('theme') or ('new-families' if fam.startswith('new:') else 'other'), figure_kinds=r.get('groups') or [],
                          domain=r.get('domain') or t.get('domain') or '', convention=r.get('convention') or '', variant=r.get('variant') or '',
                          depicts=r.get('depicts') or '', varies=r.get('varies') or '', tags=r.get('tags') or [], style=r.get('style') or '',
                          quality=r.get('quality') or '', size_pt=r.get('size_pt'), colors=r.get('colors') or [], n_elements=r.get('n_elements'),
                          occurrences=r.get('occurrences', 1), placeholders=len(r.get('bitmaps') or []), license=r.get('license') or '',
                          notes=r.get('notes') or '', figure=r['figure'], scale=r.get('scale') or 1.0,
                          source=dict(paper_id=pid, fig=r['figure'].split('_fig')[-1], figure=r['figure'], file=r.get('source_file') or '',
                                      tool=t.get('tool') or '', venue=venue_of(pid), package=r['_pkg'], agent=r.get('agent') or '', origin='cut'),
                          svg=str(dst), bytes=dst.stat().st_size))
    with open(out / 'parts.jsonl', 'w', encoding='utf-8') as fh:
        for p_ in parts: fh.write(json.dumps(p_, ensure_ascii=False) + '\n')
    fam_count = collections.Counter(p_['family'] for p_ in parts)
    fam_theme = {p_['family']: p_['theme'] for p_ in parts}
    first = {}
    for p_ in parts: first.setdefault(p_['family'], p_)
    families = []
    for f, n in sorted(fam_count.items(), key=lambda kv: (-kv[1], kv[0])):
        e = voc.get(f); fp = first[f]
        # a new family's definition: the agents' discoveries, else the variant / depicts of its first part
        definition = (e or {}).get('definition') or newdefs.get(f) or (fp['variant'] or fp['depicts'])
        families.append(dict(name=f, theme=fam_theme[f], cls=(e or {}).get('cls', 'new' if f.startswith('new:') else 'other'),
                             definition=definition, established=f in voc, count=n))
    json.dump(dict(note='AI-family part families: the vocabulary v2 ids (established) plus the new: families the cutting agents opened', families=families),
              open(out / 'families.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # ---- stats
    L = [f'# AI parts, final set: {len(parts)} parts from {len({p_["figure"] for p_ in parts})} figures, {len(families)} families', '']
    for title, key in (('package', lambda p_: p_['source']['package']), ('kind', lambda p_: p_['kind']), ('theme', lambda p_: p_['theme']), ('domain', lambda p_: p_['domain'] or '-'), ('venue', lambda p_: p_['source']['venue'])):
        c = collections.Counter(key(p_) for p_ in parts)
        L += [f'## by {title}', '', '| {} | parts |'.format(title), '|---|---:|'] + [f'| {k} | {n} |' for k, n in c.most_common()] + ['']
    L += ['## families', '', '| family | status | theme | parts |', '|---|---|---|---:|'] + [f"| {f['name']} | {'vocabulary' if f['established'] else f['cls']} | {f['theme']} | {f['count']} |" for f in families] + ['']
    big = sorted(parts, key=lambda p_: -p_['bytes'])[:12]
    L += ['## largest files', '', '| part | bytes | placeholders | size pt |', '|---|---:|---:|---|'] + [f"| {p_['name']} | {p_['bytes']} | {p_['placeholders']} | {p_['size_pt']} |" for p_ in big] + ['']
    L += [f"parts with placeholders (bitmaps replaced by grey slots): {sum(1 for p_ in parts if p_['placeholders'])}; new families without a definition: {sum(1 for f in families if not f['definition'])} of {sum(1 for f in families if not f['established'])}", '']
    (out / 'stats.md').write_text('\n'.join(L), encoding='utf-8')
    print(f"{len(parts)} parts, {len(families)} families ({sum(1 for f in families if f['established'])} vocabulary, {sum(1 for f in families if not f['established'])} new) -> {out}; "
          f"largest {big[0]['name']} {big[0]['bytes']/1e6:.1f} MB; total {sum(p_['bytes'] for p_ in parts)/1e6:.1f} MB")


if __name__ == '__main__':
    main()
