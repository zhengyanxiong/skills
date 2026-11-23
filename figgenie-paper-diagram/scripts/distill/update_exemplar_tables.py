#!/usr/bin/env python3
"""Rewrite the **Exemplars** block of every template section in references/layouts.md from the
built assets/exemplars/<template>/index.json files (v2 layout).

Each block becomes a table of the starred (must-see) exemplars — id + what_to_learn — followed by a
pointer to the template's index.json for the rest. Blocks are located as the paragraph that starts
with "**Exemplars**" inside each "### <n>. `<template>`" section and ends at the next blank line.

    python3 update_exemplar_tables.py [--layouts FILE] [--exemplars DIR] [--max-rows 12] [--dry-run]
    python3 update_exemplar_tables.py --kind mechanism [--max-rows 12]

--kind mechanism rewrites the "### Exemplars" subsection of every "## <group> — ..." section in
references/mechanism/layouts.md from assets/exemplars/mechanism/<group>/index.json: a table of the
starred figures (id | base | arrangement | what to learn) whose paths point into assets/exemplars/figures/,
then a pointer to the group's index.json for the rest.
"""
import argparse, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
DEFAULT_LAYOUTS = SKILL / "references" / "layouts.md"
DEFAULT_EXEMPLARS = SKILL / "assets" / "exemplars"
HEAD_RE = re.compile(r"^### (?:\d+|[A-Z])\. `([a-z0-9-]+)`", re.M)
MECH_LAYOUTS = SKILL / "references" / "mechanism" / "layouts.md"
MECH_GROUPS = ["comparison", "evolution", "logic", "walkthrough", "anatomy"]
MECH_HEAD_RE = re.compile(r"^## (comparison|evolution|logic|walkthrough|anatomy)\b.*$", re.M)


def mech_block(g, idx, max_rows, figs):
    """The '### Exemplars' subsection for one mechanism group: starred rows, then a pointer to the rest."""
    ex = idx["exemplars"]
    stars = [e for e in ex if e.get("star")]
    rows = stars[:max_rows] if stars else ex[:min(6, len(ex))]
    n_rest = len(ex) - len(rows)
    lines = ["### Exemplars", "",
             f"`assets/exemplars/mechanism/{g}/index.json` lists all {len(ex)} (starred first, one-line notes); each figure "
             f"lives in `assets/exemplars/figures/<id>/` — look at `print.png` (the figure as printed; `preview.png` is the "
             f"author render when there is one), then `manifest.json` and `semantics.json`. They are reference and "
             f"reinforcement: borrow the device that serves your figure; the layout itself follows what this mechanism has to "
             f"show, and may look like none of them.", "",
             "| id | base | arrangement | what to learn |", "|---|---|---|---|"]
    for e in rows:
        m = figs.get(e["id"], {})
        arr = m.get("arrangement") or ""
        if m.get("panel_count") and m["panel_count"] > 1:
            arr += f" ×{m['panel_count']}"
        note = (e.get("what_to_learn") or "").replace("|", "/").strip()
        lines.append(f"| `{e['id']}`{' ★' if e.get('star') else ''} | {m.get('base') or ''} | {arr} | {note} |")
    tail = f"{'Starred' if stars else 'First'} {len(rows)} of {len(ex)}"
    if n_rest > 0:
        tail += f"; the other {n_rest} are in `index.json` with one-line notes"
    if stars and len(stars) > max_rows:
        tail += f" ({len(stars) - max_rows} further starred ones included)"
    lines += ["", tail + "."]
    return "\n".join(lines)


def rewrite_mechanism(text, exemplars, max_rows):
    heads = list(MECH_HEAD_RE.finditer(text))
    out = []; pos = 0; done = []
    for k, m in enumerate(heads):
        g = m.group(1)
        end = heads[k + 1].start() if k + 1 < len(heads) else len(text)
        # the group section ends at the next "## " heading of any kind
        nxt = re.search(r"^## ", text[m.end():], re.M)
        end = min(end, m.end() + nxt.start()) if nxt else end
        sect = text[m.start():end]
        idx_path = Path(exemplars) / "mechanism" / g / "index.json"
        bm = re.search(r"^### Exemplars[^\n]*\n(?:.*?\n)*?(?=^### |\Z)", sect, re.M)
        if not bm or not idx_path.exists():
            continue
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
        figs = {}
        for e in idx["exemplars"]:
            mp = Path(exemplars) / "figures" / e["id"] / "manifest.json"
            if mp.is_file():
                figs[e["id"]] = json.loads(mp.read_text(encoding="utf-8"))
        new_sect = sect[:bm.start()] + mech_block(g, idx, max_rows, figs) + "\n\n" + sect[bm.end():]
        out.append(text[pos:m.start()] + new_sect); pos = end; done.append(g)
    out.append(text[pos:])
    return "".join(out), done


def block_for(t, idx, max_rows):
    ex = idx["exemplars"]
    stars = [e for e in ex if e.get("star")]
    rows = stars[:max_rows] if stars else ex[:min(6, len(ex))]
    n_rest = len(ex) - len(rows)
    lines = [f"**Exemplars** (`assets/exemplars/{t}/index.json` lists all {len(ex)}; figures live in `assets/exemplars/figures/<id>/`):", "",
             "| id | what to learn |", "| --- | --- |"]
    for e in rows:
        note = (e.get("what_to_learn") or "").replace("|", "/").strip()
        lines.append(f"| `{e['id']}` | {note} |")
    tail = f"{'Starred' if stars else 'First'} {len(rows)} of {len(ex)}"
    if n_rest > 0:
        tail += f"; the other {n_rest} are in `index.json` with one-line notes"
    if stars and len(stars) > max_rows:
        tail += f" ({len(stars) - max_rows} further starred ones included)"
    lines.append(tail + ".")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["architecture", "mechanism"], default="architecture")
    ap.add_argument("--layouts", help="default: references/layouts.md, or references/mechanism/layouts.md with --kind mechanism")
    ap.add_argument("--exemplars", default=str(DEFAULT_EXEMPLARS))
    ap.add_argument("--max-rows", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.layouts:
        a.layouts = str(MECH_LAYOUTS if a.kind == "mechanism" else DEFAULT_LAYOUTS)
    text = Path(a.layouts).read_text(encoding="utf-8")
    if a.kind == "mechanism":
        new, done = rewrite_mechanism(text, a.exemplars, a.max_rows)
        if a.dry_run:
            print("would rewrite:", done)
        else:
            Path(a.layouts).write_text(new, encoding="utf-8")
            print("rewrote exemplar blocks for:", done)
        return
    heads = list(HEAD_RE.finditer(text))
    out = []; pos = 0; done = []
    for k, m in enumerate(heads):
        t = m.group(1)
        end = heads[k + 1].start() if k + 1 < len(heads) else len(text)
        sect = text[m.start():end]
        idx_path = Path(a.exemplars) / t / "index.json"
        bm = re.search(r"^\*\*Exemplars\*\*.*?(?=\n\n)", sect, re.S | re.M)
        if not bm or not idx_path.exists():
            continue
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
        # a table block continues past the first blank line only if the table follows the intro line
        blk_end = bm.end()
        rest = sect[blk_end:]
        tm = re.match(r"\n\n(\| id \| what to learn \|\n\| --- \| --- \|\n(?:\|.*\n)+)", rest)
        if tm:
            blk_end += tm.end() - 1  # keep the trailing newline
        new_sect = sect[:bm.start()] + block_for(t, idx, a.max_rows) + sect[blk_end:]
        out.append(text[pos:m.start()] + new_sect); pos = end; done.append(t)
    out.append(text[pos:])
    new = "".join(out)
    if a.dry_run:
        print("would rewrite:", done)
    else:
        Path(a.layouts).write_text(new, encoding="utf-8")
        print("rewrote exemplar blocks for:", done)


if __name__ == "__main__":
    main()
