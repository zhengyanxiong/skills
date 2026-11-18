#!/usr/bin/env python3
"""Split whole-section voice takes into one clip per narration line.

Reading a whole section in one TTS call keeps the delivery consistent, but the film needs the
timing of every line. This finds the pauses in each take (ffmpeg silencedetect) and picks the ones
that best match where each line boundary should fall, by each line's share of the letters, with a
small dynamic program so the cuts stay in order and one bad guess cannot shift every later line.

  python3 split_takes.py --project my-film

Reads   script.json and audio/takes/<take>.wav
Writes  audio/lines/segNN.wav, audio/lines/split_report.json, audio/segments.json

Sanity check: speaking rate is measured in letters per second of actual speech. A line more than
35% off the median is flagged; that is nearly always a misplaced cut or a word the voice dropped.
Listen to every flagged line.

When a voice runs two lines together with no pause (or pauses dramatically inside a line), force
the boundary in audio/overrides.json:  {"cut_before": {"14": 26.80}}  (line id: seconds into its take).
A line can set "gap_after" (seconds of silence after it in the finished track) in script.json.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

NOISE_DB = -40        # silence threshold
MIN_SIL = 0.16        # shortest pause considered a candidate cut (s)
LPS_TOL = 0.35        # flag a line whose letters/sec is more than 35% off the median


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout.strip())


def silences(path):
    err = run(["ffmpeg", "-v", "info", "-i", str(path), "-af", f"silencedetect=noise={NOISE_DB}dB:d={MIN_SIL}", "-f", "null", "-"]).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duration(path)
    if len(ends) < len(starts):
        ends.append(total)
    return list(zip(starts, ends)), total


def weight(text):
    """Rough speaking-time weight: letters, plus allowances for commas and sentence breaks inside the line."""
    return len(re.sub(r"[^A-Za-z]", "", text)) + 6 * text.count(",") + 14 * len(re.findall(r"[.!?](?=\s+\S)", text.strip()))


def choose_cuts(cands, w, start, end, p0=0.55):
    """Pick len(w)-1 pauses so each line's length matches its expected length (segment-based DP).
    Longer pauses get a small bonus: sentence ends pause longer than commas."""
    k, n = len(w), len(cands)
    if k == 1:
        return []
    if n < k - 1:
        return None
    rate = max(1e-6, (end - start - k * p0)) / sum(w)
    exp = [wi * rate + p0 for wi in w]
    mids = [(s + e) / 2 for s, e in cands]

    def seg(i, a, b):
        return (((b - a) - exp[i]) / (0.22 * exp[i] + 0.3)) ** 2

    def bonus(j):
        return 1.2 * min(cands[j][1] - cands[j][0], 0.8)
    INF = float("inf")
    cost = [[INF] * n for _ in range(k - 1)]
    back = [[-1] * n for _ in range(k - 1)]
    for j in range(n):
        cost[0][j] = seg(0, start, mids[j]) - bonus(j)
    for i in range(1, k - 1):
        for j in range(n):
            best, arg = INF, -1
            for jp in range(j):
                if cost[i - 1][jp] < INF:
                    v = cost[i - 1][jp] + seg(i, mids[jp], mids[j])
                    if v < best:
                        best, arg = v, jp
            if arg >= 0:
                cost[i][j] = best - bonus(j); back[i][j] = arg
    final = [cost[k - 2][j] + seg(k - 1, mids[j], end) if cost[k - 2][j] < INF else INF for j in range(n)]
    j = min(range(n), key=lambda x: final[x])
    if final[j] == INF:
        return None
    picks = [j]
    for i in range(k - 2, 0, -1):
        j = back[i][j]; picks.append(j)
    return [cands[x] for x in reversed(picks)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--gap", type=float, default=0.45, help="default silence after a line in the finished track (s)")
    ap.add_argument("--take-gap", type=float, default=1.0, help="silence after the last line of a take (s)")
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    script = json.loads((proj / "script.json").read_text())
    tdir, odir = proj / "audio" / "takes", proj / "audio" / "lines"
    odir.mkdir(parents=True, exist_ok=True)
    ov = proj / "audio" / "overrides.json"
    cut_before = json.loads(ov.read_text()).get("cut_before", {}) if ov.exists() else {}

    report, segments = [], []
    for take in script["takes"]:
        wav = tdir / f"{take['take']}.wav"
        if not wav.exists():
            sys.exit(f"missing take: {wav}")
        sil, total = silences(wav)
        speech_start = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
        speech_end = sil[-1][0] if sil and sil[-1][1] >= total - 0.05 else total
        inner = [(s, e) for s, e in sil if s > speech_start + 0.05 and e < speech_end - 0.05]
        lines = take["lines"]
        w = [weight(l["spoken"]) for l in lines]
        forced = {i: float(cut_before[str(l["id"])]) for i, l in enumerate(lines) if i > 0 and str(l["id"]) in cut_before}
        edges = [0] + sorted(forced) + [len(lines)]
        bounds = [speech_start - 0.05]
        for a_i, b_i in zip(edges, edges[1:]):
            g0 = speech_start if a_i == 0 else forced[a_i]
            g1 = speech_end if b_i == len(lines) else forced[b_i]
            cands = [(s, e) for s, e in inner if s > g0 + 0.05 and e < g1 - 0.05]
            cuts = choose_cuts(cands, w[a_i:b_i], g0, g1)
            if cuts is None:
                sys.exit(f"{take['take']}: only {len(cands)} pauses for {b_i - a_i} lines; re-record with clearer pauses "
                         "or add a cut_before override in audio/overrides.json")
            bounds += [(s + e) / 2 for s, e in cuts]
            if b_i < len(lines):
                bounds.append(forced[b_i])
        bounds.append(speech_end + 0.05)
        for i, line in enumerate(lines):
            t0, t1 = max(0.0, bounds[i]), min(total, bounds[i + 1])
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", str(wav),
                 "-ar", "48000", "-ac", "1", str(odir / f"seg{line['id']:02d}.wav")])
            pause = sum(min(e, t1) - max(s, t0) for s, e in sil if e > t0 and s < t1)
            speech = max(0.01, (t1 - t0) - pause)
            letters = len(re.sub(r"[^A-Za-z]", "", line["spoken"]))
            report.append({"id": line["id"], "take": take["take"], "start": round(t0, 3), "end": round(t1, 3),
                           "speech_s": round(speech, 2), "letters": letters, "lps": round(letters / speech, 2), "text": line["text"]})
            last = i == len(lines) - 1
            segments.append({"id": line["id"], "scene": take["take"], "caption": line["text"], "vo": line["spoken"],
                             "gap_after": line.get("gap_after", a.take_gap if last else a.gap)})
        print(f"{take['take']:<20} {len(lines)} lines, {len(inner)} pauses, {speech_end - speech_start:5.1f}s of speech")

    med = sorted(r["lps"] for r in report)[len(report) // 2]
    flagged = 0
    for r in report:
        r["flag"] = abs(r["lps"] / med - 1) > LPS_TOL
        flagged += r["flag"]
    (odir / "split_report.json").write_text(json.dumps(report, indent=1))
    (proj / "audio" / "segments.json").write_text(json.dumps({"segments": segments}, indent=1))
    for r in report:
        print(f"  {r['id']:>3} {r['lps']:5.2f} l/s {r['speech_s']:5.2f}s  {r['text'][:64]}{'  <-- CHECK' if r['flag'] else ''}")
    print(f"{len(report)} lines, median {med:.2f} letters/s, {flagged} flagged")


if __name__ == "__main__":
    main()
