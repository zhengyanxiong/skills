#!/usr/bin/env python3
"""Render a cinematic-film project (its scene.py) to stills, contact strips, a cue list or an MP4.

  python3 render.py --project my-film --probe 1.0,6.2,11.5 --size 1280x720     # stills -> out/probe/
  python3 render.py --project my-film --strip 17.9:21.6:12 --size 1280x720     # 12-frame contact sheet of a move
  python3 render.py --project my-film --cues                                   # sfx_cues.json for build_sfx.py
  python3 render.py --project my-film --t0 0 --t1 30 --size 1280x720 --out out/draft.mp4 --audio audio/narration.m4a
  python3 render.py --project my-film --size 1920x1080 --out out/final.mp4 --audio audio/mix.m4a

Each worker builds the film, renders a contiguous range of frames and pipes raw RGB into its own
ffmpeg; the chunks are joined losslessly, then the soundtrack is muxed. --workers defaults to what
fits in memory (a 4K worker plus its encoder needs about 2 GB; past that the machine swaps and
everything slows to a crawl).
"""
import argparse
import importlib.util
import json
import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_scene(project):
    path = pathlib.Path(project) / "scene.py"
    if not path.exists():
        sys.exit(f"{path} not found (new_project.py makes one)")
    spec = importlib.util.spec_from_file_location("scene", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


def make(project, size):
    from engine import Doc, Renderer
    w, h = map(int, size.lower().split("x"))
    doc = Doc(project)
    film = load_scene(project).build_film(doc)
    return film, Renderer(film, w, h, doc), doc


def total_ram_gb():
    try:
        if sys.platform == "darwin":
            return int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout) / 2 ** 30
        with open("/proc/meminfo") as f:
            return int(f.readline().split()[1]) / 2 ** 20
    except Exception:
        return 8.0


def auto_workers(w, h):
    px = w * h
    per = 0.55 + 1.5 * px / (3840 * 2160)          # GB per worker + encoder, measured: ~0.9 at 1080p, ~2 at 4K
    by_ram = int(total_ram_gb() * 0.6 / per)
    by_cpu = max(1, (os.cpu_count() or 4) - 1)
    return max(1, min(by_ram, by_cpu, 8))


def encoder_args(w, crf):
    # x264 lookahead buffers ran ~2 GB per encoder at 4K; capping them keeps parallel workers in RAM
    lean = ["-rc-lookahead", "10", "-threads", "2"] if w >= 2000 else []
    return ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), *lean, "-pix_fmt", "yuv420p"]


def worker(args):
    project, size, f0, f1, out, crf = args
    film, r, _ = make(project, size)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{r.W}x{r.H}",
                           "-r", str(film.fps), "-i", "-", *encoder_args(r.W, crf), str(out)], stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(f0, f1):
        ff.stdin.write(r.frame(n).tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for chunk {out}")
    return f0, f1, time.time() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--probe", default="", help="comma-separated times: one PNG still each")
    ap.add_argument("--strip", default="", help="t0:t1:n  contact sheet of n frames between t0 and t1")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--out", default="")
    ap.add_argument("--audio", default="")
    ap.add_argument("--workers", type=int, default=0, help="0 = as many as fit in memory")
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--cues", action="store_true")
    a = ap.parse_args()
    proj = pathlib.Path(a.project).resolve()

    if a.cues:
        from engine import Doc
        film = load_scene(proj).build_film(Doc(proj))
        cues = film.all_cues()
        (proj / "sfx_cues.json").write_text(json.dumps({"duration": film.duration, "cues": cues, "room_tone": film.room_tone}, indent=1))
        kinds = {}
        for c in cues:
            kinds[c["type"]] = kinds.get(c["type"], 0) + 1
        print(f"sfx_cues.json: {len(cues)} cues  " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
        return

    if a.probe or a.strip:
        from PIL import Image
        film, r, _ = make(proj, a.size)
        pdir = proj / "out" / "probe"; pdir.mkdir(parents=True, exist_ok=True)
        if a.probe:
            for ts in [float(x) for x in a.probe.split(",") if x.strip()]:
                t0 = time.time(); img = r.frame(round(ts * film.fps))
                p = pdir / f"t{ts:07.2f}.png"; Image.fromarray(img).save(p)
                print(f"{p}  ({time.time() - t0:.2f}s)")
        if a.strip:
            s0, s1, n = a.strip.split(":"); s0, s1, n = float(s0), float(s1), int(n)
            frames = [Image.fromarray(r.frame(round((s0 + (s1 - s0) * i / max(1, n - 1)) * film.fps))) for i in range(n)]
            cols = 4; rows = (n + cols - 1) // cols
            tw, th = frames[0].width // 2, frames[0].height // 2
            sheet = Image.new("RGB", (cols * tw, rows * th), "white")
            for i, f in enumerate(frames):
                sheet.paste(f.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
            p = pdir / f"strip_{s0:06.2f}_{s1:06.2f}.jpg"; sheet.save(p, quality=85); print(p)
        return

    if not a.out:
        sys.exit("--out is required for a video render (or use --probe, --strip, --cues)")
    from engine import Doc
    film = load_scene(proj).build_film(Doc(proj))
    fps = film.fps
    t1 = a.t1 if a.t1 is not None else film.duration
    f0, f1 = round(a.t0 * fps), round(t1 * fps)
    n = f1 - f0
    w, h = map(int, a.size.lower().split("x"))
    k = max(1, min(a.workers or auto_workers(w, h), n // 30 or 1))
    work = proj / "out" / "chunks"; work.mkdir(parents=True, exist_ok=True)
    for old in work.glob("*.mp4"):
        old.unlink()
    bounds = [f0 + n * i // k for i in range(k + 1)]
    jobs = [(str(proj), a.size, bounds[i], bounds[i + 1], work / f"c{i:03d}.mp4", a.crf) for i in range(k)]
    print(f"rendering {n} frames ({n / fps:.1f}s) at {a.size} on {k} workers")
    t0 = time.time()
    with mp.get_context("spawn").Pool(k) as pool:
        for b0, b1, dt in pool.imap_unordered(worker, jobs):
            print(f"  frames {b0}-{b1}: {dt:.0f}s ({(b1 - b0) / dt:.1f} fps/worker)", flush=True)
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{j[4].resolve()}'\n" for j in jobs))
    out = pathlib.Path(a.out)
    out = (out if out.is_absolute() else proj / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if a.audio:
        audio = pathlib.Path(a.audio)
        audio = audio if audio.is_absolute() else proj / audio
        cmd += ["-ss", f"{a.t0:.3f}", "-t", f"{t1 - a.t0:.3f}", "-i", str(audio.resolve()),
                "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(f"wrote {out}  ({n} frames in {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
