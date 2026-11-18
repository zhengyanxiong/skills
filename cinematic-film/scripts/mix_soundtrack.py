#!/usr/bin/env python3
"""Mix narration, sound effects and an optional music bed into the film's soundtrack.

  python3 mix_soundtrack.py --project my-film                                   # voice + sfx
  python3 mix_soundtrack.py --project my-film --music audio/score.mp3           # + score, ducked under the voice
  python3 mix_soundtrack.py --project my-film --music audio/score.mp3 --music-db -4 --music-level 0.07 --music-eq-dip 4

The music is side-chain compressed by the narration (it dips while the narrator speaks and swells in
the gaps); the effects ride on top; the whole mix is normalised in two passes (measure, then apply)
to the target loudness with a -1.5 dBTP ceiling, so nothing pumps.

Levels that worked for a tense documentary where the music should be felt, not followed:
  --music-db -4 --sfx-db -3 --duck-ratio 3 --duck-threshold 0.03 --music-level 0.07 --music-eq-dip 4
(music lands near -30 LUFS under a -15 LUFS mix). Writes audio/mix.m4a; --stems also writes the
ducked music alone so you can check its level.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(map(str, cmd))}\n{r.stderr[-2500:]}")
    return r


def resolve(proj, p):
    p = pathlib.Path(p)
    return p if p.is_absolute() else proj / p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--voice", default="audio/narration.m4a")
    ap.add_argument("--sfx", default="audio/sfx.wav")
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", default="audio/mix.m4a")
    ap.add_argument("--music-db", type=float, default=-6.0, help="music gain before ducking")
    ap.add_argument("--sfx-db", type=float, default=-7.0, help="effects bus gain")
    ap.add_argument("--lufs", type=float, default=-15.0)
    ap.add_argument("--fade-in", type=float, default=1.2)
    ap.add_argument("--fade-out", type=float, default=3.5)
    ap.add_argument("--duck-threshold", type=float, default=0.025)
    ap.add_argument("--duck-ratio", type=float, default=4.0)
    ap.add_argument("--music-level", type=float, default=None, help="slow leveller threshold for a score that builds (0.1 = -20 dBFS)")
    ap.add_argument("--music-eq-dip", type=float, default=0.0, help="dB cut in the music around 2.4 kHz, where the voice lives")
    ap.add_argument("--stems", action="store_true")
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    dur = json.loads((proj / "audio" / "timing.json").read_text())["total_duration"]
    voice, sfx = resolve(proj, a.voice), resolve(proj, a.sfx)
    inputs = ["-i", str(voice)]
    graph = "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][vk];"
    mix = ["[v]"]
    if sfx.exists():
        inputs += ["-i", str(sfx)]
        graph += f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={a.sfx_db}dB[s];"
        mix.append("[s]")
    else:
        print(f"no {sfx}: mixing without effects")
    if a.music:
        mi = len(inputs) // 2
        inputs += ["-i", str(resolve(proj, a.music))]
        lev = f"acompressor=threshold={a.music_level}:ratio=3:attack=1500:release=3500:makeup=1," if a.music_level else ""
        lev += f"equalizer=f=2400:t=q:w=1.1:g={-abs(a.music_eq_dip)}," if a.music_eq_dip else ""
        graph += (f"[{mi}:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,{lev}"
                  f"afade=t=in:d={a.fade_in},afade=t=out:st={dur - a.fade_out:.3f}:d={a.fade_out},volume={a.music_db}dB[m];"
                  f"[m][vk]sidechaincompress=threshold={a.duck_threshold}:ratio={a.duck_ratio}:attack=35:release=550:makeup=1:knee=4[md];")
        mix.append("[md]")
    else:
        graph += "[vk]anullsink;"
    premix = graph + "".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.9:level=disabled"

    r = run(["ffmpeg", "-v", "info", "-y", *inputs, "-filter_complex", premix + f",loudnorm=I={a.lufs}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S).group(0))
    ln = (f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    out = resolve(proj, a.out)
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", premix + "," + ln + ",aresample=48000", "-c:a", "aac", "-b:a", "256k", str(out)])
    print(f"mix: {out}  (measured {m['input_i']} LUFS -> {a.lufs})")
    if a.stems and a.music:
        stem = out.with_name(out.stem + "_music.wav")
        sinks = "[v]anullsink;" + ("[s]anullsink;" if "[s]" in mix else "")
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph + sinks.rstrip(";"), "-map", "[md]", str(stem)])
        print(f"ducked music stem: {stem}")


if __name__ == "__main__":
    main()
