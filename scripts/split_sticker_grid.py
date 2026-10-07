#!/usr/bin/env python3
"""Split a regular sticker grid into numbered transparent PNG files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python3 -m pip install Pillow"
    ) from exc


def alpha_bbox(image: Image.Image):
    return image.getchannel("A").getbbox()


def trim_to_square(image: Image.Image, margin: int) -> Image.Image:
    bbox = alpha_bbox(image)
    if bbox is None:
        return image
    left, top, right, bottom = bbox
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(image.width, right + margin)
    bottom = min(image.height, bottom + margin)
    cropped = image.crop((left, top, right, bottom))
    side = max(cropped.width, cropped.height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(
        cropped, ((side - cropped.width) // 2, (side - cropped.height) // 2)
    )
    return canvas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Master grid image")
    parser.add_argument("output_dir", type=Path, help="Directory for split PNGs")
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument("--prefix", default="sticker")
    parser.add_argument("--trim", action="store_true", help="Trim transparent padding and recenter on a square canvas")
    parser.add_argument("--margin", type=int, default=24, help="Transparent margin retained when --trim is used")
    parser.add_argument("--require-alpha", action="store_true", help="Fail when the source has no transparent pixels")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rows < 1 or args.cols < 1:
        raise SystemExit("rows and cols must be positive")
    if args.margin < 0:
        raise SystemExit("margin cannot be negative")
    if not args.input.is_file():
        raise SystemExit(f"input image not found: {args.input}")

    master = Image.open(args.input).convert("RGBA")
    alpha = master.getchannel("A")
    alpha_min, alpha_max = alpha.getextrema()
    if args.require_alpha and alpha_min == 255:
        raise SystemExit(
            "source image is fully opaque; regenerate or remove the background before splitting"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    files = []
    total = args.rows * args.cols
    digits = max(2, len(str(total)))

    for row in range(args.rows):
        top = round(row * master.height / args.rows)
        bottom = round((row + 1) * master.height / args.rows)
        for col in range(args.cols):
            left = round(col * master.width / args.cols)
            right = round((col + 1) * master.width / args.cols)
            cell = master.crop((left, top, right, bottom))
            if args.trim:
                cell = trim_to_square(cell, args.margin)
            index = row * args.cols + col + 1
            filename = f"{args.prefix}-{index:0{digits}d}.png"
            output_path = args.output_dir / filename
            cell.save(output_path, "PNG")
            files.append(
                {
                    "index": index,
                    "row": row + 1,
                    "column": col + 1,
                    "file": filename,
                    "width": cell.width,
                    "height": cell.height,
                }
            )

    manifest = {
        "source": str(args.input),
        "rows": args.rows,
        "columns": args.cols,
        "source_size": [master.width, master.height],
        "source_alpha_range": [alpha_min, alpha_max],
        "files": files,
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(files)} stickers and {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
