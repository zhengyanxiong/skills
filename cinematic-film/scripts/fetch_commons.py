#!/usr/bin/env python3
"""Find and download archival images from Wikimedia Commons with their licence, and keep the credits.

  python3 fetch_commons.py search "wright brothers first flight 1903" --limit 12
  python3 fetch_commons.py category "Category:Wright Flyer" --limit 40
  python3 fetch_commons.py get --project my-film          # download every photos.json entry that has no file yet
  python3 fetch_commons.py credits --project my-film      # write credits.md from photos.json

photos.json entries name their source one of two ways:
  {"id": "P01", "kind": "photo", "commons": "File:Wright First Flight 1903Dec17.jpg"}
  {"id": "P07", "kind": "doc", "url": "https://.../full.jpg", "credit": "...", "license": "Public domain", "source": "..."}

For "commons" entries, `get` fills file, source, credit, license and license_ok from the file page's
metadata. It refuses a licence that is not public domain, CC0, CC BY or CC BY-SA unless you pass
--allow-nonfree (and then you own the rights question). "url" entries download as given: fill in
credit and licence yourself from the archive's record page (Library of Congress, National Archives).

Search tips: Commons search matches file names and descriptions, so search the archive's words
("first flight", "Kitty Hawk 1903"), then open the category of a good hit to see its siblings.
Large originals are fetched as 3200 px renders, which is more than a print on screen ever needs.
"""
import argparse
import html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "cinematic-film/1.0 (+https://github.com/Moh4696/open-3d-skills)"
FREE = re.compile(r"public domain|^pd\b|^pd-|cc0|cc[- ]by(?!.*\bnc\b)(?!.*\bnd\b)", re.I)


def api(**params):
    params.update(format="json", formatversion="2")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(3 * (attempt + 1)); continue
            raise


def text(v):
    return html.unescape(re.sub(r"<[^>]+>", "", v or "")).strip()


def info(page):
    ii = (page.get("imageinfo") or [{}])[0]
    md = ii.get("extmetadata", {})
    g = lambda k: text(md.get(k, {}).get("value", ""))
    return {"title": page.get("title"), "w": ii.get("width"), "h": ii.get("height"), "mime": ii.get("mime"),
            "url": ii.get("url"), "thumb": ii.get("thumburl"), "source": ii.get("descriptionurl"),
            "license": g("LicenseShortName") or g("UsageTerms"), "license_url": g("LicenseUrl"),
            "credit": g("Artist") or g("Credit"), "date": g("DateTimeOriginal") or g("DateTime"),
            "desc": g("ImageDescription")[:160]}


IIPROP = dict(prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=3200)


def show(pages):
    for p in pages:
        d = info(p)
        ok = "free " if FREE.search(d["license"] or "") else "CHECK"
        print(f"[{ok}] {d['title']}\n        {d['w']}x{d['h']}  {d['license'] or 'no licence field'}  {d['credit'][:60]}  {d['date'][:20]}\n        {d['desc'][:120]}")


def cmd_search(a):
    r = api(action="query", generator="search", gsrsearch=a.query, gsrnamespace=6, gsrlimit=a.limit, **IIPROP)
    show(sorted((r.get("query") or {}).get("pages", []), key=lambda p: p.get("index", 0)))


def cmd_category(a):
    cat = a.category if a.category.startswith("Category:") else "Category:" + a.category
    r = api(action="query", generator="categorymembers", gcmtitle=cat, gcmtype="file", gcmlimit=a.limit, **IIPROP)
    show((r.get("query") or {}).get("pages", []))


def download(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                dst.write_bytes(r.read()); return
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1)); continue
            raise


def cmd_get(a):
    proj = pathlib.Path(a.project)
    spec = json.loads((proj / "photos.json").read_text())
    dst_dir = proj / "assets" / "photos"; dst_dir.mkdir(parents=True, exist_ok=True)
    refused = 0
    for p in spec["photos"]:
        have = bool(p.get("file")) and (dst_dir / p["file"]).exists()
        if have and not a.force and (p.get("license") or not p.get("commons")):
            continue                     # downloaded and credited (or a local/url file the user credits by hand)
        if p.get("commons"):
            title = p["commons"] if p["commons"].startswith("File:") else "File:" + p["commons"]
            pages = (api(action="query", titles=title, **IIPROP).get("query") or {}).get("pages", [])
            if not pages or pages[0].get("missing"):
                print(f"{p['id']}: {title} not found on Commons"); refused += 1; continue
            d = info(pages[0])
            ok = bool(FREE.search(d["license"] or ""))
            if not ok and not a.allow_nonfree:
                print(f"{p['id']}: REFUSED, licence {d['license']!r} is not free ({d['source']})"); refused += 1; continue
            url = d["thumb"] if d["thumb"] and (d["w"] or 0) > 3200 and "svg" not in (d["mime"] or "") else d["url"]
            if "svg" in (d["mime"] or ""):
                url = d["thumb"]
            ext = pathlib.Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
            fname = p["file"] if have and not a.force else f"{p['id']}_{re.sub(r'[^A-Za-z0-9]+', '_', title[5:].rsplit('.', 1)[0])[:48]}{ext}"
            if not have or a.force:
                download(url, dst_dir / fname)   # an existing file only gets its credit and licence filled in
            p.update(file=fname, source=d["source"], credit=p.get("credit") or d["credit"], license=d["license"],
                     license_url=d["license_url"], date=d["date"], license_ok=ok)
            print(f"{p['id']}: {fname}  [{d['license']}]  {p['credit'][:50]}")
            time.sleep(0.5)
        elif p.get("url"):
            ext = pathlib.Path(urllib.parse.urlparse(p["url"]).path).suffix.lower() or ".jpg"
            fname = f"{p['id']}{ext}"
            download(p["url"], dst_dir / fname)
            p["file"] = fname
            p.setdefault("license_ok", bool(FREE.search(p.get("license", ""))))
            print(f"{p['id']}: {fname}  [{p.get('license') or 'LICENCE NOT RECORDED'}]")
        else:
            print(f"{p['id']}: no 'commons' or 'url' and no file in assets/photos/; add one")
    (proj / "photos.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
    if refused:
        sys.exit(f"{refused} image(s) not downloaded; replace them or decide on the rights yourself")


def cmd_credits(a):
    proj = pathlib.Path(a.project)
    spec = json.loads((proj / "photos.json").read_text())
    rows, unclear = [], []
    for p in spec["photos"]:
        lic = p.get("license") or "NOT RECORDED"
        if not p.get("license_ok", bool(FREE.search(lic))):
            unclear.append(p["id"])
        rows.append(f"| {p['id']} | {p.get('what', '')} | {p.get('credit', '')} | {lic} | {p.get('source', '')} |")
    md = ("# Image credits\n\n| ID | What | Credit | Licence | Source |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
    recs = [l for l in spec.get("recreations", [])]
    if recs:
        md += "\n## Recreations drawn in code\n\n" + "\n".join(f"- {r}" for r in recs) + "\n"
    if unclear:
        md += f"\n**Rights unclear:** {', '.join(unclear)}. Verify or replace before publishing anything monetised.\n"
    (proj / "credits.md").write_text(md)
    print(f"credits.md: {len(rows)} images" + (f", rights unclear for {', '.join(unclear)}" if unclear else ", all free"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=12)
    c = sub.add_parser("category"); c.add_argument("category"); c.add_argument("--limit", type=int, default=40)
    g = sub.add_parser("get"); g.add_argument("--project", required=True); g.add_argument("--force", action="store_true")
    g.add_argument("--allow-nonfree", action="store_true")
    k = sub.add_parser("credits"); k.add_argument("--project", required=True)
    a = ap.parse_args()
    {"search": cmd_search, "category": cmd_category, "get": cmd_get, "credits": cmd_credits}[a.cmd](a)


if __name__ == "__main__":
    main()
