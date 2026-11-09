#!/usr/bin/env python3
"""WCAG contrast checker + CSS token emitter for the iridescent-glass-ui palette.

Why this exists: glassmorphism puts text on *composited* backgrounds. Eyeballing a
hex pair is not enough — a card at alpha 0.30 over a tinted page is a different color
than the page itself, and white text on an amber gradient fails AA far more often than
designers expect. This script composites exactly like the browser does, then checks
every declared text/background pair at its required ratio.

Usage:
    python3 scripts/contrast_check.py assets/tokens.json
    python3 scripts/contrast_check.py assets/tokens.json --emit-css > assets/_tokens.generated.css
    python3 scripts/contrast_check.py assets/tokens.json --json

Exit codes:
    0  every pair passes its minimum ratio
    1  at least one pair fails (CI-friendly)
    2  bad input file / schema error

Stdlib only. Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional, Sequence, Tuple

RGB = Tuple[int, int, int]

VIRTUAL_BGS = {"base", "glass_over_base", "glass_over_base_fallback"}


# --------------------------------------------------------------------------- color

def hex_to_rgb(value: str) -> RGB:
    """Parse '#RRGGBB' or '#RGB' into an (r, g, b) tuple."""
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"not a hex color: {value!r}")
    return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))


def rgb_to_hex(rgb: RGB) -> str:
    return "#{:02X}{:02X}{:02X}".format(*[max(0, min(255, round(c))) for c in rgb])


def composite(overlay: RGB, alpha: float, backdrop: RGB) -> RGB:
    """Alpha-composite `overlay` at `alpha` onto an opaque `backdrop`.

    This mirrors what the GPU does for rgba() backgrounds over a page color.
    """
    return tuple(
        overlay[i] * alpha + backdrop[i] * (1.0 - alpha) for i in range(3)  # type: ignore[return-value]
    )


def _channel_luminance(channel: int) -> float:
    srgb = channel / 255.0
    return srgb / 12.92 if srgb <= 0.04045 else ((srgb + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: RGB) -> float:
    r, g, b = (_channel_luminance(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: RGB, bg: RGB) -> float:
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ----------------------------------------------------------------------- resolving

def resolve_bg(
    name: str,
    theme: Dict[str, str],
    glass: Dict[str, float],
    mode: str,
) -> RGB:
    """Turn a declared background name into the opaque RGB the user actually sees."""
    if name not in VIRTUAL_BGS:
        if name not in theme:
            raise KeyError(f"unknown background token: {name}")
        return hex_to_rgb(theme[name])

    base = hex_to_rgb(theme["base"])
    white: RGB = (255, 255, 255)

    if name == "base":
        return base

    if mode == "dark":
        if name == "glass_over_base":
            return composite(white, float(glass["alpha_dark_supported"]), base)
        return composite(white, float(glass["alpha_dark_fallback"]), base)

    if name == "glass_over_base":
        return composite(white, float(glass["alpha_supported"]), base)
    return composite(white, float(glass["alpha_fallback"]), base)


def resolve_fg(name: str, theme: Dict[str, str]) -> RGB:
    if name not in theme:
        raise KeyError(f"unknown foreground token: {name}")
    return hex_to_rgb(theme[name])


# -------------------------------------------------------------------------- checks

def run_checks(doc: dict) -> List[dict]:
    glass = doc["glass"]
    themes = doc["themes"]
    results: List[dict] = []

    for pair in doc["pairs"]:
        mode = pair.get("mode", "light")
        required = float(pair.get("min", 4.5))
        targets = list(themes) if pair.get("theme", "*") == "*" else [pair["theme"]]

        for theme_name in targets:
            theme = themes[theme_name][mode]
            fg = resolve_fg(pair["fg"], theme)
            bg = resolve_bg(pair["bg"], theme, glass, mode)
            ratio = contrast_ratio(fg, bg)
            results.append(
                {
                    "theme": theme_name,
                    "mode": mode,
                    "role": pair["role"],
                    "fg_token": pair["fg"],
                    "bg_token": pair["bg"],
                    "fg": rgb_to_hex(fg),
                    "bg": rgb_to_hex(bg),
                    "ratio": round(ratio, 2),
                    "min": required,
                    "pass": ratio >= required,
                }
            )
    return results


def print_report(results: Sequence[dict]) -> int:
    failures = [r for r in results if not r["pass"]]

    header = f"{'theme':<9} {'mode':<6} {'pair':<44} {'fg':<8} {'bg':<8} {'ratio':>6} {'min':>5}  ok"
    print(header)
    print("-" * len(header))
    for r in results:
        label = f"{r['fg_token']} / {r['bg_token']}"
        mark = "PASS" if r["pass"] else "FAIL"
        print(
            f"{r['theme']:<9} {r['mode']:<6} {label:<44} {r['fg']:<8} {r['bg']:<8} "
            f"{r['ratio']:>6.2f} {r['min']:>5.1f}  {mark}"
        )

    print()
    print(f"{len(results)} pairs checked, {len(failures)} failing")
    if failures:
        print("\nFix these before shipping — they are AA violations, not style opinions:")
        for r in failures:
            print(
                f"  - [{r['mode']}/{r['theme']}] {r['role']}: {r['fg']} on {r['bg']} "
                f"= {r['ratio']:.2f}:1 (needs {r['min']:.1f}:1)"
            )
    return 1 if failures else 0


# ----------------------------------------------------------------------- css output

def _vars(theme: Dict[str, str], glass: Dict[str, float], mode: str) -> List[str]:
    alpha_key = "alpha_dark_supported" if mode == "dark" else "alpha_supported"
    fallback_key = "alpha_dark_fallback" if mode == "dark" else "alpha_fallback"
    lines: List[str] = []

    for token in (
        "primary",
        "primary_deep",
        "btn_from",
        "btn_to",
        "base",
        "text_main",
        "text_sub",
        "gold",
        "gold_light",
    ):
        lines.append(f"  --theme-{token.replace('_', '-')}: {theme[token]};")

    primary = hex_to_rgb(theme["primary"])
    gold = hex_to_rgb(theme["gold"])
    lines.append(f"  --theme-primary-rgb: {primary[0]}, {primary[1]}, {primary[2]};")
    lines.append(f"  --theme-gold-rgb: {gold[0]}, {gold[1]}, {gold[2]};")
    lines.append(f"  --glass-alpha: {float(glass[alpha_key])};")
    lines.append(f"  --glass-alpha-fallback: {float(glass[fallback_key])};")
    lines.append(f"  --theme-on-primary: {theme['on_primary']};")
    return lines


def emit_css(doc: dict) -> str:
    glass = doc["glass"]
    themes = doc["themes"]
    out: List[str] = [
        "/* GENERATED FILE — do not edit by hand.",
        " * Source: assets/tokens.json",
        " * Regenerate: python3 scripts/contrast_check.py assets/tokens.json --emit-css",
        " */",
        "",
    ]

    default = next(iter(themes))
    out.append(f'/* default theme: {themes[default]["label"]} */')
    out.append(":root {")
    out.extend(_vars(themes[default]["light"], glass, "light"))
    out.append("}")
    out.append("")

    for name, theme in themes.items():
        out.append(f'/* {theme["label"]} */')
        out.append(f'[data-theme="{name}"] {{')
        out.extend(_vars(theme["light"], glass, "light"))
        out.append("}")
        out.append("")

    out.append(f'/* dark mode base — pairs with .dark on <html> */')
    out.append(".dark {")
    out.extend(_vars(themes[default]["dark"], glass, "dark"))
    out.append("  color-scheme: dark;")
    out.append("}")
    out.append("")

    for name, theme in themes.items():
        out.append(f'/* {theme["label"]} — dark */')
        out.append(f'[data-theme="{name}"].dark {{')
        out.extend(_vars(theme["dark"], glass, "dark"))
        out.append("  color-scheme: dark;")
        out.append("}")
        out.append("")

    return "\n".join(out)


# ----------------------------------------------------------------------------- main

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="WCAG AA checker for the iridescent glass palette.")
    parser.add_argument("tokens", help="path to tokens.json")
    parser.add_argument("--emit-css", action="store_true", help="print generated CSS custom-property blocks")
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument("--light-only", action="store_true", help="skip dark-mode pairs")
    args = parser.parse_args(argv)

    try:
        with open(args.tokens, "r", encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {args.tokens}: {exc}", file=sys.stderr)
        return 2

    for key in ("glass", "themes", "pairs"):
        if key not in doc:
            print(f"error: tokens file missing '{key}'", file=sys.stderr)
            return 2

    if args.emit_css:
        print(emit_css(doc))
        return 0

    pairs = doc["pairs"]
    if args.light_only:
        doc = {**doc, "pairs": [p for p in pairs if p.get("mode", "light") == "light"]}

    try:
        results = run_checks(doc)
    except (KeyError, ValueError) as exc:
        print(f"error: invalid token reference: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 1 if any(not r["pass"] for r in results) else 0

    return print_report(results)


if __name__ == "__main__":
    sys.exit(main())
