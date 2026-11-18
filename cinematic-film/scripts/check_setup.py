#!/usr/bin/env python3
"""Check that this machine can build a cinematic-film project, and say exactly what to install if not.

  python3 check_setup.py

Checks Python, numpy, Pillow, skia-python, ffmpeg and ffprobe (with libx264), the fonts each text
role will use, a local voice for scratch tracks, and how many render workers fit in memory.
Exit code 1 when something required is missing.
"""
import importlib
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ok = True


def line(status, what, detail=""):
    print(f"  [{status}] {what}" + (f"  {detail}" if detail else ""))


def need(cond, what, fix):
    global ok
    line("ok" if cond else "MISSING", what, "" if cond else fix)
    ok &= bool(cond)


print("cinematic-film setup check")
need(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}", "needs Python 3.9 or newer")
mods = {}
for mod, pip in (("numpy", "numpy"), ("PIL", "pillow"), ("skia", "skia-python")):
    try:
        mods[mod] = importlib.import_module(mod)
        line("ok", f"{pip} {getattr(mods[mod], '__version__', '')}")
    except Exception as e:
        need(False, pip, f"pip install {pip}   ({type(e).__name__})")
try:
    import scipy  # noqa: F401
    line("ok", "scipy (optional: faster sound-effects render)")
except Exception:
    line("--", "scipy not installed (optional; build_sfx.py falls back to a slower filter)")

for tool in ("ffmpeg", "ffprobe"):
    need(shutil.which(tool), tool, "install ffmpeg: brew install ffmpeg / apt install ffmpeg / winget install ffmpeg")
if shutil.which("ffmpeg"):
    enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    need("libx264" in enc, "ffmpeg has libx264", "your ffmpeg build lacks libx264; install a full build")
    filt = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    need("loudnorm" in filt and "sidechaincompress" in filt, "ffmpeg has loudnorm and sidechaincompress", "install a full ffmpeg build")

if "skia" in mods:
    sys.path.insert(0, str(HERE))
    from engine import FONT_ROLES, resolve_typeface
    print("  fonts (drop <project>/fonts/<role>.ttf to override any of them):")
    for role in FONT_ROLES:
        tf, desc = resolve_typeface(role)
        print(f"     {role:<7} {desc}")
    if any(resolve_typeface(r)[1].startswith("system default") for r in FONT_ROLES):
        print("     -> run get_fonts.py --project <folder> to fetch open-licensed replacements")

voice = "say" if shutil.which("say") else "espeak-ng" if shutil.which("espeak-ng") else None
line("ok" if voice else "--", f"scratch voice: {voice}" if voice else "no local voice for scratch tracks",
     "" if voice else "optional: apt install espeak-ng, or use any TTS and save takes as WAV")

sys.path.insert(0, str(HERE))
try:
    from render import auto_workers, total_ram_gb
    print(f"  memory {total_ram_gb():.0f} GB: {auto_workers(1920, 1080)} workers at 1080p, "
          f"{auto_workers(2560, 1440)} at 1440p, {auto_workers(3840, 2160)} at 4K")
except Exception:
    pass
print("ready" if ok else "fix the MISSING items above, then run this again")
sys.exit(0 if ok else 1)
