# Story: research, script, beat table

## Research

- Start from sources that would survive a fact-check: museum and archive pages (Smithsonian, Library of Congress, National Archives, national park sites), court records, contemporary newspapers, and good biographies. Use Wikipedia for leads only.
- Write `fact_notes` in `script.json` as you go: one line per claim, with the number, the date and where it came from. When sources disagree, say "about", "reported" or "commonly cited", or drop the claim.
- Quotes must be the person's real words. When you quote a document on screen, quote only what it says, and mark the page as a recreation in `photos.json` `recreations`.
- Check calendar facts: weekdays, intervals ("nine days later"), ages. The Wright example checks that Oct 9, 1903 was a Friday, because a typeset newspaper header shows it.

## Shapes

Every shape opens on a hook, moves forward, turns, and closes by paying off the hook while the camera pulls back to the whole board.

**Documentary, history, true crime**
- **Cold open** (2 to 5 lines): the most vivid moment, out of order. Then a title.
- **Bridge** (1 line): the only step back in time. "Four years earlier, ..." or "It started in Brooklyn, in 1899."
- **Sections** (3 to 6 lines each, one take each): strictly forward in time. Each section ends on a line that hands off to the next.
- **Turn**: the rival, the mistake, the price. Short punchy lines ("Same river. Same result.").
- **Close** (2 lines): pay off the cold open, then one line that lands the meaning.

**Product launch**
- **Problem** (2 lines): the pain, in the customer's words, with one number.
- **Reveal** (1 line): the product name, big. Then a title moment.
- **Three proofs** (2 or 3 lines each): what it does, shown, not claimed. Use one card or one product shot per proof, and a counter for each measurable claim.
- **Close**: the price or availability, and the line people will repeat.

**Brand or founder story**
- **Then**: where it started (a garage, a kitchen, a rejection letter).
- **The bet**: the risky decision.
- **The hard part**: what nearly ended it.
- **Now**: one number for scale.
- **Why**: the line that says what it was all for.

**Explainer (science, tech, how it works)**
- **The question** (1 line), asked the way a curious person would.
- **Steps** (one card or diagram each), in the order things happen. Arrows draw on between the steps.
- **The surprise**: the counter-intuitive fact.
- **Close**: the answer to the question in one sentence.

**Biography**: the same as a documentary. Open on the defining moment, bridge to childhood, then life in order.

Facts in a product or brand film are claims. Each still needs a source in `fact_notes` (a spec sheet, a press release, a dated report).

## Lines

- One idea per line, 4 to 18 words. A line is one hero on screen, so a 30-word line either holds one shot too long or crams in three heroes.
- Write for the ear: short words, concrete nouns, numbers people can picture ("less than a thousand dollars", not "under $1K").
- Put the key word last, so the visual hit lands near the end of the line where the pause follows.
- `spoken` is the same line in the form the voice reads. Write numbers as words ("nineteen oh three", "fifty thousand dollars", "fifty-nine seconds"). Spell names out phonetically if the voice stumbles on them. Leave abbreviations out. `make_beats.py` flags digits left in.
- `hero` says what the camera is on. `typed` lists any text drawn in code: labels, big numbers, stamps, document headers. Text on a document or photo is not typed.
- `gap_after` (seconds) adds room after a line: after the cold open, before a title, after a reveal. The default is 0.45, or 1.0 at the end of a take.

## script.json

```json
{"title": "Twelve Seconds",
 "takes": [{"take": "T01_cold_open", "lines": [
   {"id": 1, "text": "December 17th, 1903. A windy beach in North Carolina.",
    "spoken": "December seventeenth, nineteen oh three. A windy beach in North Carolina.",
    "hero": "the date, set big; then the map pin", "typed": "DECEMBER 17, 1903 · KILL DEVIL HILLS, N.C."}]}],
 "fact_notes": ["..."]}
```

Line ids are global and never reused. Takes are the units you record in one go, usually one per section.

## Length

| Length | Words | Lines | Takes |
| --- | --- | --- | --- |
| 60 s | about 150 | 12 to 15 | 3 to 4 |
| 90 s | about 230 | 18 to 20 | 4 to 5 |
| 5 min | about 750 | 70 | 10 |

A first film should be 60 to 90 seconds. The 5-minute version is the same method with more sections. Build and review it section by section, and look at a draft of each section before starting the next.

## Beat table

`make_beats.py` turns `script.json` (plus `audio/timing.json` when there is one) into `beats.md`. Show it to the user before any building. The lint catches:

- a year that steps back in time after the first take
- lines over 22 words
- lines with no hero
- a phrase that is typed and also spoken word for word
- digits in the spoken text
