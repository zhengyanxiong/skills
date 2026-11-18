# Sound

Three layers: the narration, synthesised effects, and an optional score. Effects should be felt, not noticed; the voice always wins.

## Effects

```bash
python3 scripts/render.py --project my-film --cues     # sfx_cues.json
python3 scripts/build_sfx.py --project my-film          # audio/sfx.wav
```

Items cue their own sounds:

| Item | Sound |
| --- | --- |
| `Print` | pop (slide for torn clippings) |
| `Stamp` | stamp |
| `PenMark` | pencil (marker for highlights, snip for quick strikes) |
| `Chalk` | tick per mark |
| `Counter` | ticks |
| `Route` | whoosh |
| `StringLine` | slide |
| `XMarker`, `MapPin` | pop |
| `Ledger` | impact |

Fast camera moves get a whoosh. A cue the scene places by hand within 0.15 s replaces the automatic one, and `sfx=False` mutes an item.

Add the score-like moments by hand:

- `film.cue("boom", title_t, 0.55)`: the title or the biggest reveal. Use it once or twice per film.
- `film.cue("riser", L(9) - 1.3, 0.5, dur=1.2)`: a crescendo into a new section. It peaks at `t + dur`, so end it on the line start.
- `film.cue("heartbeat", t)` once a second, 3 to 6 beats, under the tensest line. Or `film.cue("clock", t, dur=4)`.
- `film.cue("impact", t, 0.4)`: a number or year landing. Also available as `BigText(hit=0.4)`.
- `film.room_tone = [[0, film.duration]]`: a quiet room bed. Leave gaps in it for deliberate silence.

## Score

Optional. A documentary bed works best when it is sparse:

- a low pulse
- a few held notes
- silences that line up with section changes

Generate one (ElevenLabs Music, or any music model whose terms allow it), use a licensed track, or skip it. Most tense true stories play better on effects alone, with the score very low. Check where the score's own breaks fall, and move it (or cut lines) so they hit section starts.

## Mix

```bash
python3 scripts/mix_soundtrack.py --project my-film                                    # voice + effects
python3 scripts/mix_soundtrack.py --project my-film --music audio/score.mp3 \
    --music-db -4 --sfx-db -3 --duck-ratio 3 --duck-threshold 0.03 --music-level 0.07 --music-eq-dip 4
```

- The score ducks under the narration (sidechain), and a slow leveller stops a building score swamping the voice. A small dip at 2.4 kHz clears the voice's presence band.
- Two-pass loudness: -15 LUFS integrated, -1.5 dBTP. That suits X, YouTube and Instagram; YouTube turns louder files down anyway.
- Check the result by listening on phone speakers and on headphones. If you can follow the score's melody, it is too loud.
- `--stems` writes the ducked music alone, to measure it. Under -30 LUFS in a -15 mix reads as "felt, not followed".
