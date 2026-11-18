# Performance and delivery

## Render speed

Skia draws on the CPU. These rules took a 38 second draft from 22 minutes to 3:

- **Never fill with a repeating image shader under rotation.** It was about 70x slower than tiling the same image with `drawImageRect`. `tile_image()` does the tiling; use it for any texture.
- **Give every item `bounds()`.** Off-screen items are skipped. An item without bounds draws every frame, wherever the camera is.
- **Cache big static vector art** (`Cached`). Maps and street sheets draw once into an image and switch to live vectors only when the camera is close.
- **Profile one frame, not the run.** Time `Renderer.frame(n)` for a slow frame and comment items out until it is fast. A single slow item usually costs most of the time.
- Motion blur draws up to 8 sub-frames during fast moves. Whips cost more than holds; that is expected.

## Memory

Each render worker builds its own copy of the film and runs its own encoder.

| Size | Per worker (with encoder) | Workers on 16 GB |
| --- | --- | --- |
| 1280x720 | about 0.6 GB | 7 |
| 1920x1080 | about 0.9 GB | 6 to 7 |
| 2560x1440 | about 1.3 GB | 4 to 5 |
| 3840x2160 | about 2 GB | 3 to 4 |

`render.py` picks the worker count from total memory unless you pass `--workers`. Going past it puts the machine into swap, and then everything crawls. A 4K run with 15 GB of swap had to be killed. The other settings that keep a worker small:

- photos are capped at 2200 px times the render scale
- cache images are capped at 8192 px
- x264 runs with `-rc-lookahead 10 -threads 2` at 2000 px wide and up (its lookahead alone took about 2 GB at 4K)
- grain is half resolution and changes every second frame (full-resolution grain every frame made a 38 s clip 625 MB)

## Choosing a resolution

- **Drafts**: 1280x720.
- **X**: 1920x1080. X serves 1080p at most.
- **YouTube**: 2560x1440 is the sweet spot. It gets YouTube's better encode, at about a third of the cost of 4K.
- **4K**: only if asked. About 3 hours for 5 minutes on a 16 GB laptop.

## Captions

```bash
python3 scripts/burn_captions.py --project my-film --video out/final.mp4 --audio audio/mix.m4a --style highlighter --out out/final_captions.mp4
python3 scripts/burn_captions.py --project my-film --srt-only --out out/captions.srt
```

- **Styles**: `highlighter` (condensed caps, the current word swiped yellow), `clean` (classic subtitle), `paper` (typewriter on a torn strip), `redbar` (caps on a red bar). Render a still of each over the busiest shot and let the user pick.
- Captions occupy the bottom 26% of the frame. Keep big numbers and labels above it in the scene.
- **Deliver**: a captioned file for X and Instagram (they autoplay muted), and a clean file plus the SRT for YouTube.
- Also make a small phone preview (`ffmpeg -i final.mp4 -vf scale=960:-2 -crf 28 preview.mp4`), to send for review before the big upload.
