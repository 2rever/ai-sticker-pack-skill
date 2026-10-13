#!/usr/bin/env python3
"""Repair sticker transparency and white outlines deterministically.

Two jobs, both deterministic (no image model involved):

1. Optional chroma-key removal of a solid background. Use magenta
   (#FF00FF) when asking a model to render on a solid color: it is far
   from skin, hair, clothing, and the white sticker outline, so keying
   stays clean. Never key on black or white backgrounds -- dark hair and
   the white outline would be removed together with the background.
   "--chroma auto" samples the four image corners instead.

2. Rebuild the white sticker outline from the alpha silhouette. The
   outline is painted as a solid white underlay that is the dilated
   silhouette, so it is always closed, uniform, and fully opaque -- no
   matter what the image model or a matting tool did to the original
   outline. Broken model-drawn outlines (near-white pixels in the outer
   band) are stripped before rebuilding.

Requires only Pillow.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python3 -m pip install Pillow"
    ) from exc

ALPHA_THRESHOLD = 24  # alpha above this counts as figure


def parse_color(value: str, size: tuple[int, int]) -> tuple[int, int, int]:
    if value == "auto":
        return value  # resolved later by caller
    value = value.lstrip("#")
    if len(value) != 6:
        raise SystemExit(f"invalid color: {value!r}; use RRGGBH hex such as FF00FF")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def corner_color(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    w, h = rgb.size
    corners = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
    samples = [rgb.getpixel(p) for p in corners]
    return tuple(sorted(c[i] for c in samples)[len(samples) // 2] for i in range(3))


def chroma_key(image: Image.Image, color: tuple[int, int, int], tol: int) -> Image.Image:
    """Set alpha=0 where the pixel is within tol of the key color (soft ramp)."""
    rgb = image.convert("RGB")
    key = Image.new("RGB", rgb.size, color)
    diff = ImageChops.difference(rgb, key)
    r, g, b = diff.split()
    maxdiff = ImageChops.lighter(ImageChops.lighter(r, g), b)
    soft = max(1, tol // 2)
    # maxdiff <= soft -> alpha 0; >= tol -> 255; linear ramp between
    lut = [
        0 if i <= soft else (255 if i >= tol else round(255 * (i - soft) / (tol - soft)))
        for i in range(256)
    ]
    alpha = maxdiff.point(lut)
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def silhouette(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    return alpha.point(lambda v: 255 if v > ALPHA_THRESHOLD else 0)


def fill_holes(mask: Image.Image) -> Image.Image:
    """Fill silhouette holes (e.g. gaps between arm and torso)."""
    inv = ImageChops.invert(mask)
    w, h = inv.size
    for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if inv.getpixel(corner) == 255:
            ImageDraw.floodfill(inv, corner, 128, thresh=8)
    outside = inv.point(lambda v: 255 if v == 128 else 0)
    return ImageChops.invert(ImageChops.darker(ImageChops.invert(mask), outside))


def erode(mask: Image.Image, px: int) -> Image.Image:
    return mask.filter(ImageFilter.MinFilter(2 * px + 1))


def dilate(mask: Image.Image, px: int) -> Image.Image:
    return mask.filter(ImageFilter.MaxFilter(2 * px + 1))


def keep_largest_component(mask: Image.Image) -> tuple[Image.Image, int]:
    """Keep only the largest opaque component; for single stickers, never grids."""
    from collections import deque

    w, h = mask.size
    data = mask.tobytes()
    labels = bytearray(w * h)
    best_label, best_size, label = 0, 0, 0
    for start in range(w * h):
        if data[start] != 255 or labels[start]:
            continue
        label += 1
        size = 0
        queue = deque([start])
        labels[start] = label
        while queue:
            i = queue.popleft()
            size += 1
            x = i % w
            for j in (
                i - 1 if x > 0 else -1,
                i + 1 if x < w - 1 else -1,
                i - w,
                i + w,
            ):
                if 0 <= j < w * h and data[j] == 255 and not labels[j]:
                    labels[j] = label
                    queue.append(j)
        if size > best_size:
            best_size, best_label = size, label
    kept = Image.frombytes(
        "L", (w, h), bytes(255 if v == best_label else 0 for v in labels)
    )
    return kept, label - 1


def clip_to_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    alpha = ImageChops.darker(image.getchannel("A"), mask)
    out = image.copy()
    out.putalpha(alpha)
    return out


def strip_broken_outline(image: Image.Image, band_px: int, white_thresh: int) -> Image.Image:
    """Remove near-white pixels in the outer band (the model's broken outline)."""
    mask = fill_holes(silhouette(image))
    band = ImageChops.subtract(mask, erode(mask, band_px))
    rgb = image.convert("RGB")
    r, g, b = rgb.split()
    min_channel = ImageChops.darker(ImageChops.darker(r, g), b)
    near_white = min_channel.point(lambda v: 255 if v >= white_thresh else 0)
    zone = ImageChops.darker(band, near_white)
    alpha = ImageChops.subtract(image.getchannel("A"), zone)
    out = image.copy()
    out.putalpha(alpha)
    return out


def rebuild_outline(image: Image.Image, width_px: int) -> Image.Image:
    mask = fill_holes(silhouette(image))
    grown = dilate(mask, width_px)
    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    underlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    underlay.paste(white, (0, 0), grown)
    result = underlay.copy()
    result.alpha_composite(image)
    return result


def stats(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    transparent = sum(hist[: ALPHA_THRESHOLD + 1])
    total = image.width * image.height
    return {
        "size": [image.width, image.height],
        "figure_coverage": round(1 - transparent / total, 4),
        "alpha_range": list(alpha.getextrema()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Sticker or master grid image")
    parser.add_argument("output", type=Path, help="Repaired RGBA PNG output")
    parser.add_argument(
        "--chroma",
        default=None,
        help="Solid background to key out first: RRGGBB hex (e.g. FF00FF) or 'auto' to sample the corners",
    )
    parser.add_argument("--chroma-tol", type=int, default=48, help="Chroma key tolerance (default 48)")
    parser.add_argument(
        "--outline-width",
        type=int,
        default=None,
        help="Outline width in pixels (default: 1.2%% of the short side)",
    )
    parser.add_argument("--white-threshold", type=int, default=232, help="Channel value above which band pixels count as broken outline (default 232)")
    parser.add_argument("--no-strip", action="store_true", help="Keep the existing outline instead of stripping and rebuilding it")
    parser.add_argument("--erode", type=int, default=0, help="Shrink the silhouette by N pixels before rebuilding, cutting away fuzzy fiber fringe (use 2-4 for felt, clay, watercolor, crayon styles)")
    parser.add_argument("--keep-largest", action="store_true", help="Keep only the largest connected figure; removes detached residue. For single stickers only, never grids")
    parser.add_argument("--feather", type=float, default=0.0, help="Gaussian blur radius applied to the final alpha")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"input image not found: {args.input}")

    image = Image.open(args.input).convert("RGBA")
    before = stats(image)

    keyed = False
    if args.chroma is not None:
        color = corner_color(image) if args.chroma == "auto" else parse_color(args.chroma, image.size)
        image = chroma_key(image, color, args.chroma_tol)
        keyed = True

    removed_components = 0
    if args.keep_largest or args.erode > 0:
        mask = fill_holes(silhouette(image))
        if args.erode > 0:
            mask = erode(mask, args.erode)
        if args.keep_largest:
            mask, removed_components = keep_largest_component(mask)
        image = clip_to_mask(image, mask)

    width = args.outline_width or max(2, round(min(image.size) * 0.012))
    if not args.no_strip:
        image = strip_broken_outline(image, band_px=width + max(2, width // 2), white_thresh=args.white_threshold)
    image = rebuild_outline(image, width)

    if args.feather > 0:
        alpha = image.getchannel("A").filter(ImageFilter.GaussianBlur(args.feather))
        image.putalpha(alpha)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, "PNG")

    report = {
        "input": str(args.input),
        "output": str(args.output),
        "chroma_keyed": keyed,
        "outline_width_px": width,
        "eroded_px": args.erode,
        "removed_components": removed_components,
        "stripped_broken_outline": not args.no_strip,
        "before": before,
        "after": stats(image),
        "outline": "rebuilt from silhouette; closed and uniform by construction",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
