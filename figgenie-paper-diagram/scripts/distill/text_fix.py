#!/usr/bin/env python3
"""List or rewrite the text leaves of a part SVG (human pass of the mechanism parts library: the user decided
that labels garbled by the dropped embedded fonts are corrected, not dropped).

  python3 scripts/distill/text_fix.py --list part.svg
      prints one line per text leaf: index, tag, font attributes, current content
  python3 scripts/distill/text_fix.py --apply fixes.jsonl [--out-dir DIR]
      applies the fixes; each line is {"svg": path, "fixes": [{"i": leaf index, "old": current content (checked
      when given), "new": replacement}]}. Writes the SVG in place, or under DIR (same basename) when given.

A text leaf is a <text> element without <tspan> children, or a <tspan> without nested <tspan>; leaves are
numbered in document order, so an index found with --list stays valid until the file is rewritten.
"""
import argparse, json, os, sys
from lxml import etree

SVG_NS = 'http://www.w3.org/2000/svg'
TEXT, TSPAN = '{%s}text' % SVG_NS, '{%s}tspan' % SVG_NS


def leaves(doc):
    out = []
    for el in doc.iter(TEXT, TSPAN):
        if any(isinstance(c.tag, str) and c.tag == TSPAN for c in el): continue
        out.append(el)
    return out


def content(el):
    return ''.join(el.itertext())


def set_content(el, s):
    for c in list(el):                     # a leaf has no tspan children; drop anything else (titles) to be safe
        el.remove(c)
    el.text = s


def parse(path):
    return etree.parse(path, parser=etree.XMLParser(huge_tree=True, remove_blank_text=False))


def cmd_list(path):
    doc = parse(path)
    for i, el in enumerate(leaves(doc.getroot())):
        attrs = ' '.join('%s=%s' % (k.split('}')[-1], v) for k, v in el.attrib.items()
                         if k.split('}')[-1] in ('font-family', 'font-size', 'font-style', 'font-weight', 'baseline-shift', 'dy'))
        print('%3d  %-5s %-40s %r' % (i, el.tag.split('}')[-1], attrs[:40], content(el)))


def cmd_apply(fixes_path, out_dir=None):
    n_files = n_fix = 0
    for line in open(fixes_path, encoding='utf-8'):
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        path = rec['svg']
        doc = parse(path); lv = leaves(doc.getroot())
        for f in rec.get('fixes', []):
            i = int(f['i'])
            if i >= len(lv): sys.exit('%s: leaf %d out of range (%d leaves)' % (path, i, len(lv)))
            cur = content(lv[i])
            if 'old' in f and f['old'] is not None and f['old'] != cur:
                sys.exit('%s: leaf %d reads %r, fixes file expected %r' % (path, i, cur, f['old']))
            set_content(lv[i], f['new']); n_fix += 1
        out = path if not out_dir else os.path.join(out_dir, os.path.basename(path))
        if out_dir: os.makedirs(out_dir, exist_ok=True)
        doc.write(out, encoding='utf-8', xml_declaration=True)
        n_files += 1
    print('applied %d fixes in %d files' % (n_fix, n_files))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--list', metavar='SVG'); g.add_argument('--apply', metavar='FIXES_JSONL')
    ap.add_argument('--out-dir', default=None)
    a = ap.parse_args()
    if a.list: cmd_list(a.list)
    else: cmd_apply(a.apply, a.out_dir)


if __name__ == '__main__':
    main()
