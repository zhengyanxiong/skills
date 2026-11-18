#!/usr/bin/env python3
"""Build the projected map data for GeoMap from public-domain boundaries (TopoJSON or GeoJSON).

  python3 make_map.py --project my-film

Reads map.json in the project:
  {"maps": [{
     "name": "us",
     "source": "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json",   # TopoJSON or GeoJSON, URL or path
     "object": "states",                                                     # TopoJSON object (ignored for GeoJSON)
     "projection": {"type": "albers", "lon0": -96, "lat0": 37.5, "p1": 29.5, "p2": 45.5},
     "drop": ["Alaska", "Hawaii", "Puerto Rico"],          # or "keep": [...]
     "neighbors": {"source": "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json", "object": "countries",
                   "keep": ["Canada", "Mexico", "Cuba"], "dark": ["Canada", "Mexico"], "clip": [-140, 12, -55, 62]},
     "frame": [-125, 24, -66, 50],                         # optional sheet bounds: lon_min, lat_min, lon_max, lat_max
     "places": {"Dayton": [39.76, -84.19], "Kitty Hawk": [36.06, -75.70]}       # [lat, lon]
  }]}

Projections: albers (equal-area conic; good for one country), equirect (lon0, lat0; fine for a region),
mercator (lon0). Units are earth radii, so GeoMap(K=24000) gives a country about 20,000 world px wide.
Boundaries are kept at full detail: thinning them opened slivers between neighbouring regions.

Good free sources (Natural Earth data is public domain; the atlas packages are ISC-licensed):
  us-atlas@3/states-10m.json (objects: states, nation)   world-atlas@2/countries-50m.json (object: countries)
  both on https://cdn.jsdelivr.net/npm/   Natural Earth GeoJSON: github.com/nvkelso/natural-earth-vector

Downloads are cached in assets/data/. Writes assets/prep/map_<name>.json.
"""
import argparse
import json
import math
import pathlib
import sys
import urllib.request

UA = "cinematic-film/1.0 (+https://github.com/Moh4696/open-3d-skills)"


def load(src, cache):
    if str(src).startswith(("http://", "https://")):
        p = cache / pathlib.Path(src.split("?")[0]).name
        if not p.exists():
            cache.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(src, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                p.write_bytes(r.read())
            print(f"downloaded {src} -> {p}")
        return json.loads(p.read_text())
    return json.loads(pathlib.Path(src).read_text())


def name_of(props):
    props = props or {}
    for k in ("name", "NAME", "ADMIN", "name_en", "NAME_EN"):
        if props.get(k):
            return props[k]
    return None


def features(data, obj=None):
    """[(name, [ring lon/lat lists])] from TopoJSON or GeoJSON."""
    out = []
    if data.get("type") == "Topology":
        tr = data.get("transform")
        arcs = []
        for arc in data["arcs"]:
            x = y = 0; pts = []
            for p in arc:
                if tr:
                    x += p[0]; y += p[1]
                    pts.append((x * tr["scale"][0] + tr["translate"][0], y * tr["scale"][1] + tr["translate"][1]))
                else:
                    pts.append((p[0], p[1]))
            arcs.append(pts)

        def ring(idx):
            pts = []
            for i in idx:
                a = arcs[i] if i >= 0 else arcs[~i][::-1]
                pts.extend(a if not pts else a[1:])
            return pts
        if obj not in data["objects"]:
            sys.exit(f"object {obj!r} not in TopoJSON; have {list(data['objects'])}")
        for g in data["objects"][obj]["geometries"]:
            polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]] if g["type"] == "Polygon" else []
            out.append((name_of(g.get("properties")) or str(g.get("id")), [ring(r) for poly in polys for r in poly]))
    else:
        feats = data["features"] if data.get("type") == "FeatureCollection" else [data]
        for f in feats:
            geo = f.get("geometry") or {}
            polys = geo.get("coordinates", []) if geo.get("type") == "MultiPolygon" else [geo.get("coordinates", [])] if geo.get("type") == "Polygon" else []
            out.append((name_of(f.get("properties")) or str(f.get("id")), [r for poly in polys for r in poly]))
    return out


def projector(spec):
    t = spec.get("type", "albers")
    r = math.radians
    if t == "albers":
        lon0, lat0, p1, p2 = spec.get("lon0", -96.0), spec.get("lat0", 37.5), spec.get("p1", 29.5), spec.get("p2", 45.5)
        n = (math.sin(r(p1)) + math.sin(r(p2))) / 2
        c = math.cos(r(p1)) ** 2 + 2 * n * math.sin(r(p1))
        rho0 = math.sqrt(c - 2 * n * math.sin(r(lat0))) / n

        def f(lon, lat):
            rho = math.sqrt(max(0.0, c - 2 * n * math.sin(r(lat)))) / n
            th = n * r(lon - lon0)
            return rho * math.sin(th), -(rho0 - rho * math.cos(th))      # y down
        return f
    if t == "equirect":
        lon0, lat0 = spec.get("lon0", 0.0), spec.get("lat0", 0.0)
        k = math.cos(r(lat0))
        return lambda lon, lat: (r(lon - lon0) * k, -r(lat - lat0))
    if t == "mercator":
        lon0 = spec.get("lon0", 0.0)
        return lambda lon, lat: (r(lon - lon0), -math.log(math.tan(math.pi / 4 + r(max(-85, min(85, lat))) / 2)))
    sys.exit(f"unknown projection {t!r} (albers, equirect, mercator)")


def clip_ring(ring, box):
    """Sutherland-Hodgman clip of a lon/lat ring to [lon0, lat0, lon1, lat1]."""
    x0, y0, x1, y1 = box
    def clip(pts, inside, cross):
        out = []
        for i, cur in enumerate(pts):
            prev = pts[i - 1]
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
        return out
    def lerp_x(a, b, x):
        u = (x - a[0]) / (b[0] - a[0]); return (x, a[1] + (b[1] - a[1]) * u)
    def lerp_y(a, b, y):
        u = (y - a[1]) / (b[1] - a[1]); return (a[0] + (b[0] - a[0]) * u, y)
    pts = [tuple(p[:2]) for p in ring]
    for inside, cross in ((lambda p: p[0] >= x0, lambda a, b: lerp_x(a, b, x0)), (lambda p: p[0] <= x1, lambda a, b: lerp_x(a, b, x1)),
                          (lambda p: p[1] >= y0, lambda a, b: lerp_y(a, b, y0)), (lambda p: p[1] <= y1, lambda a, b: lerp_y(a, b, y1))):
        if not pts:
            break
        pts = clip(pts, inside, cross)
    return pts


def project_rings(rings, proj, box=None):
    out = []
    for rg in rings:
        pts = clip_ring(rg, box) if box else [tuple(p[:2]) for p in rg]
        if len(pts) > 2:
            out.append([[round(x, 5), round(y, 5)] for x, y in (proj(lon, lat) for lon, lat in pts)])
    return out


def build(m, cache):
    proj = projector(m.get("projection", {}))
    feats = features(load(m["source"], cache), m.get("object"))
    names = [n for n, _ in feats]
    keep, drop = set(m.get("keep") or []), set(m.get("drop") or [])
    for n in keep | drop:
        if n not in names:
            print(f"  warning: {n!r} not found in {m['source']} (names look like {names[:6]})")
    regions = {}
    for n, rings in feats:
        if (keep and n not in keep) or n in drop:
            continue
        pr = project_rings(rings, proj, m.get("clip"))
        if pr:
            regions.setdefault(n, []).extend(pr)
    out = {"regions": regions, "neighbors": {}, "dark": [], "places": {}, "projection": m.get("projection", {})}
    nb = m.get("neighbors")
    if nb:
        nfeats = features(load(nb["source"], cache), nb.get("object"))
        want = set(nb.get("keep") or [])
        found = set()
        for n, rings in nfeats:
            if want and n not in want:
                continue
            pr = project_rings(rings, proj, nb.get("clip"))
            if pr:
                out["neighbors"].setdefault(n, []).extend(pr); found.add(n)
        for n in want - found:
            print(f"  warning: neighbour {n!r} not found")
        out["dark"] = nb.get("dark", [])
    for name, (lat, lon) in (m.get("places") or {}).items():
        x, y = proj(lon, lat); out["places"][name] = [round(x, 6), round(y, 6)]
    if m.get("frame"):
        a, b, c, d = m["frame"]
        corners = [proj(a, b), proj(a, d), proj(c, b), proj(c, d), proj((a + c) / 2, b), proj((a + c) / 2, d)]
        out["frame"] = [min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners), max(p[1] for p in corners)]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    a = ap.parse_args()
    proj = pathlib.Path(a.project)
    spec = json.loads((proj / "map.json").read_text())
    prep = proj / "assets" / "prep"; prep.mkdir(parents=True, exist_ok=True)
    for m in spec["maps"]:
        out = build(m, proj / "assets" / "data")
        (prep / f"map_{m['name']}.json").write_text(json.dumps(out))
        print(f"map_{m['name']}.json: {len(out['regions'])} regions, {len(out['neighbors'])} neighbours, {len(out['places'])} places")


if __name__ == "__main__":
    main()
