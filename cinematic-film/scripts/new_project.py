#!/usr/bin/env python3
"""Start a cinematic-film project folder from the template (or copy the worked example).

  python3 new_project.py my-film --title "The Great Molasses Flood"
  python3 new_project.py wright-demo --example        # the Wright Flyer film, ready to fetch, voice and render

Layout:
  script.json   narration, one entry per line (text, spoken, hero, typed), grouped into takes
  photos.json   every image: id, kind, crop, source, credit, licence
  map.json      optional maps (make_map.py)
  scene.py      the film: build_film(doc) places items and camera keys on the voiceover timing
  assets/photos (downloads)  assets/prep (graded, generated)  audio/  out/  fonts/ (optional overrides)
"""
import argparse
import json
import pathlib
import shutil
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--title", default=None)
    ap.add_argument("--example", action="store_true", help="copy the Wright Flyer example instead of the blank template")
    a = ap.parse_args()
    dst = pathlib.Path(a.folder)
    if dst.exists() and any(dst.iterdir()):
        sys.exit(f"{dst} exists and is not empty")
    src = SKILL / "assets" / ("wright-flyer" if a.example else "template")
    shutil.copytree(src, dst, dirs_exist_ok=True)
    for sub in ("assets/photos", "assets/prep", "audio/takes", "out"):
        (dst / sub).mkdir(parents=True, exist_ok=True)
    if a.title:
        sp = dst / "script.json"
        s = json.loads(sp.read_text()); s["title"] = a.title
        sp.write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n")
    print(f"created {dst} from {src.name}")
    print("next: write script.json, then  make_beats.py -> tts_say.py -> split_takes.py -> build_narration.py")


if __name__ == "__main__":
    main()
