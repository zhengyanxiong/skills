# Voice

The film is timed to the voice, so the voice comes before the picture. Use a free scratch voice to build against, then swap in the final one. The scene asks for line starts and spoken words, never fixed seconds, so it re-times itself.

## Scratch voice

```bash
python3 scripts/tts_say.py --project my-film                         # macOS say, or espeak-ng on Linux
python3 scripts/tts_say.py --project my-film --voice Daniel --rate 165
```

It reads each take in one go, with a clear pause between lines, and writes `audio/takes/<take>.wav`.

## Final voice: any provider

Record **one take per section**, not one call per line. One call keeps the delivery even. Per-line calls change pace and pitch from line to line, which sounds stitched together.

- **A command-line TTS** (Piper, a provider's CLI, your own script): `tts_say.py --cmd 'tool --in {txt} --out {out}'`. `{txt}` is a file with the take's lines, one paragraph each.
- **An API or app** (ElevenLabs, OpenAI, Higgsfield, PlayHT): send each take's `spoken` lines joined with a paragraph break (or the provider's pause tag), and save the result as `audio/takes/<take>.wav`. Any format ffmpeg reads is fine.
- **A person**: one file per take, a beat of silence between lines.

Then:

```bash
python3 scripts/split_takes.py --project my-film
python3 scripts/build_narration.py --project my-film                 # natural read
python3 scripts/build_narration.py --project my-film --target 88     # fit to 88 s (0.90 to 1.15x only)
```

## Checking the split

`split_takes.py` measures every line's speaking rate in letters per second of actual speech, and flags lines more than 35% off the median. A flag nearly always means one of three things:

- **Two lines run together.** The voice did not pause, so the cut landed a sentence late. Force the boundary in `audio/overrides.json`: `{"cut_before": {"53": 26.80}}`, the line id and the seconds into its take where that line starts. Find the spot by listening, or with `ffmpeg -i take.wav -af silencedetect=noise=-40dB:d=0.1 -f null -`.
- **A dramatic pause inside a line** ("He was... thirty-two") got taken for a boundary. Force the real one the same way.
- **A dropped or doubled word.** Re-record that take.

Listen to every flagged line. A cut in the wrong place shifts every visual hit after it.

## Re-recording

Re-record a whole take, never a single line: one line patched in from another call stands out. After any change, run `split_takes.py` and `build_narration.py` again, then `render.py --probe` on the affected lines. If a line got noticeably longer, check its camera keys still have time.

## Delivery notes

- Ask for a measured documentary read. A pace of 150 to 170 words a minute suits these films.
- Numbers and names go in `spoken` exactly as they should be said.
- A tempo fit beyond 0.90 to 1.15x sounds wrong. `build_narration.py` refuses it: cut or add lines instead.
- The narration lands at -16 LUFS. `mix_soundtrack.py` sets the final loudness.
