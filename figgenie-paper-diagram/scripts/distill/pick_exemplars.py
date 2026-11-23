#!/usr/bin/env python3
"""Build figgenie-paper-diagram/assets/exemplars/ from exemplar_selection.json.

Re-runnable: for every entry in the selection list it copies the author source
SVG, its PNG preview and the PDF-extracted print-size PNG out of the read-only
corpus, writes a semantics.json (the full semantic record) and a manifest.json,
then writes the top-level index.json.

    python3 figgenie-paper-diagram/scripts/distill/pick_exemplars.py [--dry-run]
    python3 .../pick_exemplars.py --selection other.json --out /tmp/exemplars

Nothing under lab/, workspace/ or paper-figure-corpus/ is ever written.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))       # figgenie-paper-diagram/
REPO = os.path.abspath(os.path.join(SKILL, os.pardir))                  # repo root
EXTRACTED = os.path.join(REPO, "lab", "extracted")
INDEX_CSV = os.path.join(EXTRACTED, "corpus_index.csv")
SEMANTICS = os.path.join(EXTRACTED, "corpus_semantics.jsonl")
DEFAULT_SELECTION = os.path.join(HERE, "exemplar_selection.json")
DEFAULT_OUT = os.path.join(SKILL, "assets", "exemplars")


def load_index() -> dict[tuple[str, str], dict]:
    csv.field_size_limit(10**9)
    rows: dict[tuple[str, str], dict] = {}
    with open(INDEX_CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows[(row["paper_id"], str(row["fig"]))] = row
    return rows


def load_semantics(index: dict) -> dict[tuple[str, str], dict]:
    """Semantic records restricted to architecture diagrams (727 of 739 after the 2026-09-07 backfill)."""
    recs: dict[tuple[str, str], dict] = {}
    with open(SEMANTICS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            key = (rec["paper_id"], str(rec["fig"]))
            row = index.get(key)
            if row is None:
                continue
            if row["type"] != "diagram" or row["subtype"] != "architecture":
                continue
            recs[key] = rec
    return recs


def split_id(exemplar_id: str) -> tuple[str, str]:
    paper_id, fig = exemplar_id.rsplit("_fig", 1)
    return paper_id, fig


def source_paths(row: dict) -> dict[str, str | None]:
    """Absolute paths of the four corpus files an exemplar may have."""
    pid = row["paper_id"]
    src = (row.get("src_svgs") or "").split("|")[0].strip()
    pdf = (row.get("pdf_svg") or "").strip()

    def exists(rel: str | None) -> str | None:
        if not rel:
            return None
        p = os.path.join(EXTRACTED, pid, rel)
        return p if os.path.exists(p) else None

    return {
        "src_svg": exists(src),
        "src_png": exists(os.path.splitext(src)[0] + ".png" if src else None),
        "pdf_svg": exists(pdf),
        "pdf_png": exists(os.path.splitext(pdf)[0] + ".png" if pdf else None),
    }


def relative_to_extracted(path: str | None) -> str | None:
    return os.path.relpath(path, REPO) if path else None


def build(selection_path: str, out_dir: str, dry_run: bool) -> int:
    with open(selection_path, encoding="utf-8") as fh:
        selection = json.load(fh)
    entries = selection["exemplars"]

    index = load_index()
    semantics = load_semantics(index)

    written: list[dict] = []
    problems: list[str] = []

    for entry in entries:
        eid = entry["id"]
        template = entry["template"]
        key = split_id(eid)
        row = index.get(key)
        rec = semantics.get(key)
        if row is None or rec is None:
            problems.append(f"{eid}: not an architecture-diagram record")
            continue

        paths = source_paths(row)
        if not paths["src_svg"] or not paths["src_png"]:
            problems.append(f"{eid}: missing author source SVG/PNG")
            continue

        layout = rec.get("layout", {})
        content = rec.get("content", {})
        dest = os.path.join(out_dir, template, eid)
        manifest = {
            "id": eid,
            "paper_id": row["paper_id"],
            "fig": row["fig"],
            "venue": row["venue"],
            "year": int(row["year"]) if str(row.get("year", "")).isdigit() else row.get("year"),
            "caption": row.get("caption"),
            "template": template,
            "corpus_template": layout.get("template"),
            "direction": layout.get("direction"),
            "column": layout.get("column"),
            "tool": row.get("tool"),
            "aspect": layout.get("aspect"),
            "n_components": len(content.get("components") or []),
            "n_flows": len(content.get("flows") or []),
            "nesting_depth": layout.get("nesting_depth"),
            "lanes": layout.get("lanes"),
            "legend": layout.get("legend"),
            "step_markers": layout.get("step_markers"),
            "panels": layout.get("panels"),
            "confidence": rec.get("confidence"),
            "original_paths": {
                "src_svg": relative_to_extracted(paths["src_svg"]),
                "src_png": relative_to_extracted(paths["src_png"]),
                "pdf_svg": relative_to_extracted(paths["pdf_svg"]),
                "pdf_png": relative_to_extracted(paths["pdf_png"]),
            },
            "files": {
                "source.svg": "author source SVG (from the paper's arXiv/source bundle)",
                "preview.png": "PNG render of source.svg",
                "print.png": "PNG of the figure as extracted from the published PDF, at print size"
                if paths["pdf_png"] else None,
                "semantics.json": "full semantic record for this figure",
                "manifest.json": "this file",
            },
            "why_chosen": entry["why_chosen"],
            "what_to_learn": entry["what_to_learn"],
        }
        manifest["files"] = {k: v for k, v in manifest["files"].items() if v}

        if not dry_run:
            os.makedirs(dest, exist_ok=True)
            shutil.copyfile(paths["src_svg"], os.path.join(dest, "source.svg"))
            shutil.copyfile(paths["src_png"], os.path.join(dest, "preview.png"))
            if paths["pdf_png"]:
                shutil.copyfile(paths["pdf_png"], os.path.join(dest, "print.png"))
            with open(os.path.join(dest, "semantics.json"), "w", encoding="utf-8") as fh:
                json.dump(rec, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, ensure_ascii=False, indent=2)
                fh.write("\n")

        written.append(
            {
                "id": eid,
                "template": template,
                "venue": row["venue"],
                "year": manifest["year"],
                "tool": row.get("tool"),
                "column": layout.get("column"),
                "aspect": layout.get("aspect"),
                "n_components": manifest["n_components"],
                "has_print_png": bool(paths["pdf_png"]),
                "dir": os.path.relpath(dest, out_dir),
                "files": sorted(manifest["files"]),
                "what_to_learn": entry["what_to_learn"],
            }
        )

    by_template: dict[str, int] = {}
    for w in written:
        by_template[w["template"]] = by_template.get(w["template"], 0) + 1

    index_doc = {
        "generated_by": "figgenie-paper-diagram/scripts/distill/pick_exemplars.py",
        "selection": os.path.relpath(selection_path, SKILL),
        "corpus": selection.get("source"),
        "n_exemplars": len(written),
        "by_template": dict(sorted(by_template.items(), key=lambda kv: (-kv[1], kv[0]))),
        "layout": "<template-id>/<exemplar-id>/{source.svg, preview.png, print.png, semantics.json, manifest.json}",
        "provenance": "Figures are reproduced from published OSDI/NSDI/SOSP/ASPLOS papers for style reference only.",
        "exemplars": written,
    }
    if not dry_run:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as fh:
            json.dump(index_doc, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    total = 0
    if not dry_run:
        for root, _dirs, files in os.walk(out_dir):
            for f in files:
                total += os.path.getsize(os.path.join(root, f))

    print(f"{'would write' if dry_run else 'wrote'} {len(written)} exemplars to {out_dir}")
    for t, n in index_doc["by_template"].items():
        print(f"  {t:22} {n}")
    if not dry_run:
        print(f"total size: {total / 1e6:.1f} MB")
    if problems:
        print("\nPROBLEMS:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selection", default=DEFAULT_SELECTION)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return build(args.selection, args.out, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
