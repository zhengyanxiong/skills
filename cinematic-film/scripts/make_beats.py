#!/usr/bin/env python3
"""Write beats.md, the beat table you approve before building: one row per narration line with its
start, length, the one hero on screen and any typed text. Also lints the script.

  python3 make_beats.py --project my-film

Uses audio/timing.json when there is one; before any voice exists it estimates times from the
letters (about 14.5 letters per second plus pauses), so the table can be reviewed first.

Lint (warnings, not errors):
  * chronology: after the cold open (the first take), a year lower than one already reached
  * a line over 22 words (one idea per line; long lines get cut in half by the camera anyway)
  * a line with no hero
  * a phrase typed on screen that is also spoken word for word in the same line
  * digits left in the spoken text (voices misread "1903"; write "nineteen oh three")
"""
import argparse
import json
import pathlib
import re

LPS = 14.5


def mmss(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    script = json.loads((proj / "script.json").read_text())
    tp = proj / "audio" / "timing.json"
    timing = {s["id"]: s for s in json.loads(tp.read_text())["segments"]} if tp.exists() else {}
    lines = [(t["take"], l) for t in script["takes"] for l in t["lines"]]

    warn, rows, cursor, max_year = [], [], 0.9, None
    first_take = script["takes"][0]["take"]
    for take, l in lines:
        i = l["id"]
        if i in timing:
            start, dur = timing[i]["start"], timing[i]["duration"]
        else:
            dur = len(re.sub(r"[^A-Za-z]", "", l["spoken"])) / LPS
            start = cursor
            cursor += dur + l.get("gap_after", 0.45)
        typed = l.get("typed", "") or "--"
        hero = l.get("hero", "")
        rows.append(f"| {i} | {mmss(start)} | {dur:.1f}s | {l['text']} | {hero or '(previous hero holds)'} | {typed} |")
        words = len(l["text"].split())
        if words > 22:
            warn.append(f"line {i}: {words} words; split it (one idea per line)")
        if not hero:
            warn.append(f"line {i}: no hero (say what the camera is on, even if the previous one holds)")
        if re.search(r"\d", l["spoken"]):
            warn.append(f"line {i}: digits in the spoken text {l['spoken']!r}; write numbers as words")
        for ph in [p.strip() for p in re.split(r"[+·,;]", typed) if len(p.strip().split()) >= 3]:   # name bars are fine
            if ph.lower() in l["text"].lower():
                warn.append(f"line {i}: {ph!r} is typed AND spoken word for word; show it one way")
        years = [int(y) for y in re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", l["text"])]
        if take != first_take:
            for y in years:
                if max_year is not None and y < max_year:
                    warn.append(f"line {i}: {y} steps back in time after {max_year}; after the cold open, story time only moves forward")
                max_year = y if max_year is None else max(max_year, y)
    total = json.loads(tp.read_text())["total_duration"] if tp.exists() else cursor + 3.0
    src = "timed to audio/timing.json" if timing else "ESTIMATED from letter counts (no voice yet)"
    head = (f"# {script.get('title', proj.name)}: beat table\n\n"
            f"{len(lines)} lines, {mmss(total)} total, {src}.\n\n"
            "Hero = the one thing the camera is on (everything else dims). Typed = text drawn in code; "
            "a phrase is either typed or shown on a real document, never both.\n\n"
            "| # | Start | Len | Narration | Hero on screen | Typed |\n|---|---|---|---|---|---|\n")
    body = "\n".join(rows) + "\n"
    if warn:
        body += "\n## Lint\n\n" + "\n".join(f"- {w}" for w in warn) + "\n"
    (proj / "beats.md").write_text(head + body)
    print(f"beats.md: {len(lines)} beats, {mmss(total)} ({'timed' if timing else 'estimated'}), {len(warn)} warning(s)")
    for w in warn:
        print("  " + w)


if __name__ == "__main__":
    main()
