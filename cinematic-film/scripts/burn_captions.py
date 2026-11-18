#!/usr/bin/env python3
"""Burn a caption style into a finished render (a second pass, no re-render) and write an SRT.

  python3 burn_captions.py --project my-film --video out/final.mp4 --audio audio/mix.m4a --style highlighter --out out/final_captions.mp4
  python3 burn_captions.py --project my-film --srt-only --out out/captions.srt

N workers each decode a time slice of the video, composite the caption layer onto the bottom
quarter of each frame and encode; the slices are joined losslessly and the audio is muxed.
Captions sit in the bottom 26% of the frame: keep big on-screen numbers out of that band.
Styles: highlighter, clean, paper, redbar (see captions.py). The SRT uses sentence-sized chunks
for players (upload it to YouTube with the clean, caption-free render).
"""
import argparse
import json
import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
                          "-of", "json", str(video)], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    nb = int(s.get("nb_frames") or 0)
    if not nb:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                                   capture_output=True, text=True).stdout)
        nb = int(round(dur * num / den))
    return s["width"], s["height"], num / den, nb


def worker(args):
    video, style, f0, f1, fps, w, h, out, crf, timing, fonts = args
    import numpy as np
    from captions import Captions
    cap = Captions(style, w, h, timing, fonts)
    y0 = int(h * 0.74)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{f0 / fps:.4f}", "-i", str(video), "-frames:v", str(f1 - f0),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), *(["-rc-lookahead", "10", "-threads", "2"] if w >= 2000 else []),
                            "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    size = w * h * 3
    t0 = time.time()
    for n in range(f0, f1):
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        layer = cap.layer(n / fps)
        if layer is not None:
            frame = frame.copy()
            a = layer[y0:, :, 3:4].astype(np.float32) * (1 / 255.0)
            frame[y0:] = np.clip(frame[y0:].astype(np.float32) * (1 - a) + layer[y0:, :, :3], 0, 255).astype(np.uint8)
        enc.stdin.write(frame.tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    return f0, f1, time.time() - t0


def srt(timing, out):
    from captions import chunks_for
    total = timing["total_duration"]

    def ts(x):
        ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    rows = chunks_for(timing, "clean")
    lines = []
    for i, c in enumerate(rows, 1):
        lines += [str(i), f"{ts(c['t0'])} --> {ts(min(c['t1'], total))}", " ".join(w for w, _ in c["words"]), ""]
    pathlib.Path(out).write_text("\n".join(lines))
    print(f"srt: {out} ({len(rows)} cues)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--video")
    ap.add_argument("--audio")
    ap.add_argument("--style", default="highlighter", choices=["highlighter", "clean", "paper", "redbar"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=max(1, min(6, (os.cpu_count() or 4) - 1)))
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--srt-only", action="store_true")
    a = ap.parse_args()
    proj = pathlib.Path(a.project).resolve()
    rel = lambda p: p if pathlib.Path(p).is_absolute() else proj / p
    timing = json.loads((proj / "audio" / "timing.json").read_text())
    out = rel(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    if a.srt_only:
        srt(timing, out); return
    if not a.video:
        sys.exit("--video is required (or --srt-only)")
    video = rel(a.video)
    w, h, fps, nb = probe(video)
    work = proj / "out" / "burn"; work.mkdir(parents=True, exist_ok=True)
    for old in work.glob("*.mp4"):
        old.unlink()
    k = a.workers
    b = [nb * i // k for i in range(k + 1)]
    fonts = str(proj / "fonts")
    jobs = [(str(video), a.style, b[i], b[i + 1], fps, w, h, work / f"b{i:02d}.mp4", a.crf, timing, fonts) for i in range(k)]
    t0 = time.time()
    with mp.get_context("spawn").Pool(k) as pool:
        for f0, f1, dt in pool.imap_unordered(worker, jobs):
            print(f"  frames {f0}-{f1}: {dt:.0f}s", flush=True)
    lst = work / "list.txt"; lst.write_text("".join(f"file '{j[7].resolve()}'\n" for j in jobs))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if a.audio:
        cmd += ["-i", str(rel(a.audio)), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(f"wrote {out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
