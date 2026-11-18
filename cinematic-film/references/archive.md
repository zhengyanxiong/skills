# Images: archives, your own, AI stills, and the rights

## Three sources

- **Archives** (history, real people, real events): the rest of this file.
- **Your own** (product shots, team photos, screenshots, renders): drop the files in `assets/photos/` and give them a `"file"` entry in `photos.json`. Grade them `natural` so they keep their colour under one shared balance. Anyone recognisable needs to have agreed to appear.
- **AI stills** (illustration, mood, things no camera saw): generate every still with one model and one style reference, so they read as a set. The `motion-assets` skill plans the prompts and the cost before spending anything. Never use AI images of real people, or as evidence of real events. Credit them in `credits.md` as AI-generated.

## What is free to use (archives)

- **Published in the US in 1930 or earlier**: public domain in the US (as of 2026; one more year enters each January).
- **Works of the US federal government** (Library of Congress staff photos, National Archives records made by federal agencies, NASA, military, FBI): public domain in the US.
- **CC0, CC BY, CC BY-SA**: free with credit. BY-SA asks that adaptations carry the same licence; credit it and say so in `credits.md`.
- **"No known copyright restrictions"** (Flickr Commons, LOC collections): usually fine. Record the institution's statement. `fetch_commons.py` marks these CHECK, and `get` refuses them unless you pass `--allow-nonfree` after checking.
- **Not free**: press agency photos after 1930 (AP, Getty, Corbis), film stills, most photos of living people, anything marked NC or ND, anything whose uploader is not the author with no source given.

A Commons page can be wrong. For anything that matters, check that the stated source (an LOC record, a museum page) really says so. Photos taken by the subjects themselves count as theirs: the Wright portraits are credited to the brothers.

## Where to look

| Archive | Good for | How |
| --- | --- | --- |
| Wikimedia Commons | Almost everything famous, with licence fields | `fetch_commons.py search` and `category`. Open the category of a good hit to see its siblings |
| Library of Congress (loc.gov) | US photos, newspapers (Chronicling America), maps | Add `?fo=json` to an item URL for its metadata and full-size image links |
| National Archives (catalog.archives.gov) | Federal records: court files, mugshots, letters, forms | Item JSON: `https://catalog.archives.gov/proxy/records/search?naId=<id>`. The page itself is a JavaScript app |
| State archives and memory projects | Regional history | Many sites load images by JavaScript: open the page in a headless browser and save the image responses |
| Internet Archive book images | Diagrams and engravings from old books | Usually "no known restrictions"; record the book |
| Smithsonian Open Access | Objects and portraits marked CC0 | Filter for CC0 |

Search with the archive's own words. Captions use period terms ("aeroplane", "liquor raid"), so try those as well as modern ones.

## photos.json

```json
{"grade": "bw",
 "photos": [
  {"id": "P01", "what": "First flight, Dec 17 1903", "kind": "photo", "commons": "File:First flight2.jpg"},
  {"id": "P07", "what": "Telegram", "kind": "doc", "url": "https://...", "credit": "...", "license": "Public domain", "source": "https://..."}
 ],
 "recreations": ["Wilbur Wright's 1899 letter: real sentence, page typeset in code."]}
```

- `kind` sets the grade: `photo` (one duotone across the film), `paper` (newsprint, used with `Print(paper=True)` torn edges), `doc` (records keep a hint of their paper colour), `color` (covers that must stay in colour).
- `crop` is `[left, top, right, bottom]` as fractions. Crop to the part that matters: a face on the top third, a headline block, without an uploader's border.
- `credit` overrides the Commons "Artist" field. That field is sometimes only the uploader.

## Rules that keep a film honest

- Never use a stand-in face. If no photo of a person exists, show a document with their name, a blank witness card, or a silhouette labelled as such.
- Never imply a photo shows something it does not. A photo of the machine being readied is not the crash; caption it with what it is.
- A recreated document says "recreation" in `credits.md` and quotes only real words. The narration may read them; the page must not add any.
- `fetch_commons.py credits` writes `credits.md`, ready to paste under a YouTube video or in a reply on X. It lists anything with unclear rights at the bottom. Clear those before anything monetised.

## Measuring positions on a photo

Highlights, circles and holes are placed by fractions of the image (`doc.on(print, fx, fy)`). To find them, draw a 10% grid over the graded image, view it, and read off the fractions:

```python
from PIL import Image, ImageDraw
im = Image.open("assets/prep/photos/P07.jpg"); d = ImageDraw.Draw(im)
for i in range(1, 10):
    x, y = im.width * i // 10, im.height * i // 10
    d.line([(x, 0), (x, im.height)], fill=(255, 0, 0)); d.line([(0, y), (im.width, y)], fill=(0, 0, 255))
im.save("grid.jpg")
```
