#!/usr/bin/env python3
"""Record every take in script.json with a local voice: a free scratch track to time the film against.

The film is timed to the voiceover, so the picture cannot be built before there is a voice. A
scratch track from the system voice costs nothing, gives real timings, and is replaced later by
the final voice (any TTS or a human): the scene re-times itself because it asks for line starts
and spoken words, never fixed seconds.

  python3 tts_say.py --project my-film                       # macOS `say`, or espeak-ng on Linux
  python3 tts_say.py --project my-film --voice Daniel --rate 165
  python3 tts_say.py --project my-film --cmd 'piper -m en_US-lessac-medium.onnx -f {out} < {txt}'

--cmd runs any command-line TTS once per take: {txt} is a text file with the take's lines (one per
paragraph), {out} the WAV it must write. Each take is read in one go so the delivery stays even;
split_takes.py then cuts it into lines. Writes audio/takes/<take>.wav.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile


def run(cmd, shell=False):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
    if r.returncode != 0:
        sys.exit(f"FAILED: {cmd if shell else ' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r.stdout


def to_wav(src, dst):
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ar", "48000", "-ac", "1", str(dst)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--voice", default=None, help="say / espeak-ng voice name")
    ap.add_argument("--rate", type=int, default=165, help="words per minute (documentary pace is 150-170)")
    ap.add_argument("--pause", type=int, default=650, help="pause between lines, ms (split_takes.py cuts there)")
    ap.add_argument("--cmd", default=None, help="any TTS command with {txt} and {out} placeholders")
    ap.add_argument("--only", default="", help="comma-separated take names to (re)record")
    a = ap.parse_args()

    proj = pathlib.Path(a.project)
    script = json.loads((proj / "script.json").read_text())
    tdir = proj / "audio" / "takes"; tdir.mkdir(parents=True, exist_ok=True)
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    engine = "cmd" if a.cmd else "say" if shutil.which("say") else "espeak-ng" if shutil.which("espeak-ng") else None
    if engine is None:
        sys.exit("no local voice: install espeak-ng (apt install espeak-ng), or pass --cmd for your TTS, "
                 "or record takes elsewhere and save them as audio/takes/<take>.wav")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for take in script["takes"]:
            name = take["take"]
            if only and name not in only:
                continue
            lines = [l["spoken"].strip() for l in take["lines"]]
            out = tdir / f"{name}.wav"
            if engine == "say":
                text = f" [[slnc {a.pause}]] ".join(lines)
                raw = tmp / f"{name}.aiff"
                cmd = ["say", "-r", str(a.rate), "-o", str(raw)] + (["-v", a.voice] if a.voice else []) + [text]
                run(cmd); to_wav(raw, out)
            elif engine == "espeak-ng":
                ssml = "<speak>" + f"<break time='{a.pause}ms'/>".join(lines) + "</speak>"
                raw = tmp / f"{name}.wav"
                cmd = ["espeak-ng", "-m", "-s", str(a.rate), "-w", str(raw)] + (["-v", a.voice] if a.voice else []) + [ssml]
                run(cmd); to_wav(raw, out)
            else:
                txt = tmp / f"{name}.txt"; txt.write_text("\n\n".join(lines) + "\n")
                raw = tmp / f"{name}_raw.wav"
                run(a.cmd.format(txt=str(txt), out=str(raw)), shell=True)
                to_wav(raw, out)
            dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)]))
            print(f"{name:<20} {len(lines)} lines  {dur:5.1f}s  -> {out}")


if __name__ == "__main__":
    main()
