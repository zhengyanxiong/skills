#!/usr/bin/env python3
"""Assemble the per-line clips into one narration track and the timing file the film is built on.

  python3 build_narration.py --project my-film                 # natural read (tempo 1.0)
  python3 build_narration.py --project my-film --target 75     # fit the whole film to 75 s

Trims the silence off both ends of every clip, so pacing is set here (each line's gap_after from
split_takes.py) and not by whatever padding the voice engine added. --target solves for the one
tempo change (pitch kept) that lands the film on that length, and refuses anything outside
0.90-1.15x: beyond that the read sounds wrong, and the fix is a shorter or longer script.

Reads   audio/segments.json, audio/lines/segNN.wav
Writes  audio/narration.m4a (-16 LUFS), audio/timing.json
"""
import argparse
import json
import pathlib
import subprocess
import sys

TEMPO_LIMITS = (0.90, 1.15)
TRIM = ("silenceremove=start_periods=1:start_silence=0:start_threshold=-50dB,areverse,"
        "silenceremove=start_periods=1:start_silence=0:start_threshold=-50dB,areverse")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--target", type=float, default=0.0, help="finished length in seconds; 0 keeps the natural read")
    ap.add_argument("--lead", type=float, default=0.9, help="silence before the first word (s)")
    ap.add_argument("--tail", type=float, default=3.0, help="hold after the last word, for the final pull-back (s)")
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    adir = proj / "audio"
    segments = json.loads((adir / "segments.json").read_text())["segments"]
    work = adir / "trimmed"; work.mkdir(exist_ok=True)

    for seg in segments:
        src = adir / "lines" / f"seg{seg['id']:02d}.wav"
        if not src.exists():
            sys.exit(f"missing line clip: {src} (run split_takes.py)")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", TRIM, "-ar", "48000", "-ac", "1", str(work / f"raw{seg['id']:02d}.wav")])

    raw_speech = sum(duration(work / f"raw{s['id']:02d}.wav") for s in segments)
    fixed = a.lead + a.tail + sum(s["gap_after"] for s in segments[:-1])
    tempo = 1.0 if a.target <= 0 else raw_speech / (a.target - fixed)
    if not TEMPO_LIMITS[0] <= tempo <= TEMPO_LIMITS[1]:
        sys.exit(f"tempo {tempo:.3f} is outside {TEMPO_LIMITS} for a {a.target}s film ({raw_speech:.1f}s of speech + "
                 f"{fixed:.1f}s of pauses). Rewrite the script shorter or longer instead of distorting the read.")
    print(f"speech {raw_speech:.2f}s + pauses {fixed:.2f}s, tempo {tempo:.4f}")

    timeline, parts, cursor = [], [], a.lead
    pdir = work / "parts"; pdir.mkdir(exist_ok=True)

    def silence(sec, tag):
        p = pdir / f"sil_{tag}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{sec:.3f}", str(p)])
        return p
    parts.append(silence(a.lead, "lead"))
    for i, seg in enumerate(segments):
        dst = work / f"seg{seg['id']:02d}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(work / f"raw{seg['id']:02d}.wav"), "-af", f"atempo={tempo:.6f}",
             "-ar", "48000", "-ac", "1", str(dst)])
        d = duration(dst)
        timeline.append({"id": seg["id"], "scene": seg["scene"], "caption": seg["caption"], "vo": seg["vo"],
                         "start": round(cursor, 3), "end": round(cursor + d, 3), "duration": round(d, 3)})
        parts.append(dst)
        cursor += d
        if i < len(segments) - 1:
            parts.append(silence(seg["gap_after"], f"g{seg['id']}")); cursor += seg["gap_after"]
    parts.append(silence(a.tail, "tail"))
    total = round(cursor + a.tail, 3)

    lst = pdir / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    track = adir / "narration.m4a"
    # loudnorm resamples to 96 kHz internally; force 48 kHz back out (some players choke on 96 kHz AAC)
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(track)])
    (adir / "timing.json").write_text(json.dumps({"total_duration": total, "lead_in": a.lead, "tail_out": a.tail,
                                                  "tempo": round(tempo, 4), "segments": timeline}, indent=2))
    print(f"narration {track} ({duration(track):.2f}s), timeline {total:.2f}s, {len(timeline)} lines -> audio/timing.json")


if __name__ == "__main__":
    main()
