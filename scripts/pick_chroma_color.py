#!/usr/bin/env python3
"""Pick the easiest chroma-key background color for a portrait.

Samples the portrait's dominant colors (hair, clothing, skin) and returns
the saturated key color whose distance to every dominant color is largest,
so the background can be keyed out cleanly without touching the figure.

White is never offered: the sticker outline is always white. Black is only
recommended when the portrait has no dark hair or clothing. The chosen hex
goes into the generation prompt's [key color] field, and the same hex is
later passed to rebuild_outline.py --chroma for deterministic keying.

Requires only Pillow.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python3 -m pip install Pillow"
    ) from exc

# Saturated key colors plus black. White is intentionally excluded.
CANDIDATES = {
    "FF00FF": "magenta",
    "00FF00": "green",
    "0000FF": "blue",
    "FF0000": "red",
    "00FFFF": "cyan",
    "FFFF00": "yellow",
    "000000": "black",
}

# The sticker outline is always white, so every key color must also be far
# from white. Distances below MIN_DISTANCE mean the key would eat the figure.
WHITE = (255, 255, 255)
MIN_DISTANCE = 90


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def dominant_colors(image: Image.Image, count: int = 8, min_share: float = 0.03):
    """Quantize the portrait and return (rgb, share) pairs above min_share."""
    rgb = image.convert("RGBA")
    # Flatten transparency onto white so transparent padding does not skew
    # the palette toward black.
    flat = Image.new("RGB", rgb.size, WHITE)
    flat.paste(rgb, (0, 0), rgb)
    small = flat.resize((max(1, flat.width // 4), max(1, flat.height // 4)))
    quantized = small.quantize(colors=count)
    palette = quantized.getpalette()
    total = small.width * small.height
    result = []
    for pixels, index in sorted(quantized.getcolors(), key=lambda t: -t[0]):
        share = pixels / total
        if share < min_share:
            continue
        color = tuple(palette[index * 3 : index * 3 + 3])
        # Skip colors that are already near-white (backgrounds, highlights):
        # the white-outline rule covers them.
        if distance(color, WHITE) < 40:
            continue
        result.append((color, share))
    return result


def pick(dominant) -> list[dict]:
    ranked = []
    for hexcode, name in CANDIDATES.items():
        color = hex_to_rgb(hexcode)
        # Score: distance to the closest dominant color; the white outline
        # counts as an implicit dominant color.
        nearest = min([distance(color, d) for d, _ in dominant] + [distance(color, WHITE)])
        ranked.append({"hex": hexcode, "name": name, "clearance": round(nearest, 1)})
    ranked.sort(key=lambda r: -r["clearance"])
    return ranked


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("portrait", type=Path, help="User portrait image")
    parser.add_argument("--colors", type=int, default=8, help="Palette size for dominant-color extraction")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.portrait.is_file():
        raise SystemExit(f"portrait not found: {args.portrait}")

    image = Image.open(args.portrait)
    dominant = dominant_colors(image, count=args.colors)
    if not dominant:
        raise SystemExit("could not extract dominant colors from the portrait")

    ranked = pick(dominant)
    best = ranked[0]
    report = {
        "portrait": str(args.portrait),
        "dominant_colors": [
            {"rgb": list(color), "share": round(share, 3)} for color, share in dominant
        ],
        "key_color": best["hex"],
        "key_color_name": best["name"],
        "clearance": best["clearance"],
        "ranked": ranked,
        "rules": [
            "white is never used as a key color because the outline is white",
            "black only when hair and clothing contain no dark colors",
            "if clearance < %d, keying may bleed into the figure; pick the next color" % MIN_DISTANCE,
        ],
    }
    if best["clearance"] < MIN_DISTANCE:
        report["warning"] = (
            "best clearance is low; the character likely wears many colors. "
            "Consider regenerating the wardrobe or accept a higher --chroma-tol."
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
