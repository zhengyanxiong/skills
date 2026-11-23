"""Family index sheets for the human review of the consolidated mechanism part families.

    python3 mech_family_index.py --final mech-parts/final [--out mech-parts/final/family_index] [--samples 6] [--rows 12]

Reads <final>/parts.jsonl and <final>/families.json (written by mech_final.py) and the tiles under <final>/tiles/,
and draws, per theme, pages of one row per family: the family name, established/new, part and slug counts and the
definition on the left, then up to --samples sample tiles chosen to cover as many raw (agent-coined) families as
possible.  Output: <out>/<theme>_N.png plus <out>/index.md (the same table in text, one line per family, with the
page each family is on).  Nothing outside --out is touched.
"""
import argparse, collections, json, textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

THEME_ORDER = ['steps-traces', 'frames-change', 'logic-time', 'structures', 'annotations', 'icons',
               'graphs', 'containers', 'data-flow', 'math-code', 'other']
QUALITY_RANK = {'good': 0, 'ok': 1, 'fair': 1, 'poor': 2}


def fonts():
    reg = ['/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf']
    bold = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf']

    def pick(paths, size):
        for p in paths:
            if Path(p).exists():
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()
    return {'hdr': pick(bold, 20), 'name': pick(bold, 14), 'meta': pick(reg, 11), 'def': pick(reg, 11), 'tile': pick(reg, 9)}


def pick_samples(rows, n):
    """Spread the samples over the raw families (one per raw slug first), best quality first, then fill up."""
    by_raw = collections.defaultdict(list)
    for r in rows:
        by_raw[r.get('family_raw') or r['family']].append(r)
    for rs in by_raw.values():
        rs.sort(key=lambda r: (QUALITY_RANK.get(r.get('quality'), 1), r['name']))
    order = sorted(by_raw, key=lambda k: (k != rows[0]['family'], -len(by_raw[k]), k))   # namesake slug first, then the big ones
    out, i = [], 0
    while len(out) < n and any(by_raw.values()):
        for k in order:
            if by_raw[k]:
                out.append(by_raw[k].pop(0))
                if len(out) >= n: break
        i += 1
        if i > 50: break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--final', default='mech-parts/final'); ap.add_argument('--out', default=None)
    ap.add_argument('--samples', type=int, default=6); ap.add_argument('--rows', type=int, default=12)
    ap.add_argument('--tile', type=int, default=150)
    a = ap.parse_args()
    final = Path(a.final); out = Path(a.out) if a.out else final / 'family_index'
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('*'):
        if old.is_file(): old.unlink()
    parts = [json.loads(l) for l in open(final / 'parts.jsonl', encoding='utf-8') if l.strip()]
    fam_json = json.load(open(final / 'families.json', encoding='utf-8'))
    fams = {f['name']: f for f in fam_json['families']}
    by_fam = collections.defaultdict(list)
    for r in parts: by_fam[r['family']].append(r)
    F = fonts(); T = a.tile; tiles = final / 'tiles'
    text_w, gap = 420, 8
    row_h = T + 2 * gap + 12
    W = 20 + text_w + a.samples * (T + gap) + 20
    md = ['# Family index — %d families, %d parts' % (len(fams), len(parts)), '',
          '| page | family | theme | est. | parts | raw slugs | definition |', '|---|---|---|---|---|---|---|']
    n_pages = 0
    for theme in THEME_ORDER + sorted(set(f['theme'] for f in fams.values()) - set(THEME_ORDER)):
        names = sorted((n for n, f in fams.items() if f['theme'] == theme), key=lambda n: (-len(by_fam.get(n, [])), n))
        if not names: continue
        for p in range(0, len(names), a.rows):
            page = names[p:p + a.rows]; pg = p // a.rows + 1
            H = 50 + len(page) * row_h + 10
            img = Image.new('RGB', (W, H), '#ffffff'); dr = ImageDraw.Draw(img)
            dr.text((20, 14), '%s  —  families %d-%d of %d' % (theme, p + 1, p + len(page), len(names)), fill='#111111', font=F['hdr'])
            for k, name in enumerate(page):
                f = fams[name]; rows = by_fam.get(name, [])
                y = 50 + k * row_h
                dr.line([(10, y), (W - 10, y)], fill='#dddddd')
                dr.text((20, y + gap), name[:44], fill='#0b57a4', font=F['name'])
                raw = sorted(set(r.get('family_raw') or name for r in rows))
                meta = '%s · %d parts · %d raw slug%s' % ('established' if f.get('established') else 'new family', len(rows), len(raw), '' if len(raw) == 1 else 's')
                dr.text((20, y + gap + 20), meta, fill='#333333', font=F['meta'])
                yy = y + gap + 38
                for ln in textwrap.wrap(f.get('definition') or '', 68)[:5]:
                    dr.text((20, yy), ln, fill='#555555', font=F['def']); yy += 14
                others = [s for s in raw if s != name and s != 'new:' + name]
                if others:
                    yy += 2
                    for ln in textwrap.wrap('from: ' + ', '.join(s.replace('new:', '') for s in others), 72)[:3]:
                        if yy + 12 > y + row_h - 2: break
                        dr.text((20, yy), ln, fill='#8a8a8a', font=F['tile']); yy += 12
                for j, r in enumerate(pick_samples(rows, a.samples)):
                    x = 20 + text_w + j * (T + gap)
                    tp = tiles / (r['name'] + '.png')
                    dr.rectangle([x, y + gap, x + T, y + gap + T], outline='#e0e0e0')
                    if tp.exists():
                        try: img.paste(Image.open(tp).convert('RGB').resize((T, T), Image.LANCZOS), (x, y + gap))
                        except Exception: pass          # noqa: BLE001
                    dr.text((x + 2, y + gap + T + 1), r['name'][:26], fill='#666666', font=F['tile'])
                md.append('| %s_%d | %s | %s | %s | %d | %d | %s |' % (theme, pg, name, theme, 'yes' if f.get('established') else '', len(rows), len(raw),
                                                                    (f.get('definition') or '').replace('|', '/')[:120]))
            img.save(out / ('%s_%d.png' % (theme, pg))); n_pages += 1
    (out / 'index.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('%d pages under %s' % (n_pages, out))


if __name__ == '__main__':
    main()
