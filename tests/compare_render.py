"""Compare a fresh render against the committed example PNG.

Usage:
    uv run --with pillow python tests/compare_render.py <rendered.png> <committed.png> [--max-diff 0.03]

A byte-for-byte hash never matches across platforms (fonts are rasterised and
anti-aliased differently on Linux CI than on the macOS machine that produced
the committed PNG), so this checks what actually matters instead:

  1. both images have the same pixel size — a layout change, a missing element,
     or a different scale shows up here;
  2. the fraction of pixels whose grayscale value differs by more than
     THRESHOLD is at most --max-diff. This is only a sanity check: Linux CI
     text differs from a macOS render on 1.9% of pixels, and the whole drawing
     covers just 4.3%, so a blank render fails but a partial one or a small
     edit can pass. The exact check is the SVG comparison in CI.
"""
from __future__ import annotations

import argparse
import sys

from PIL import Image, ImageChops

THRESHOLD = 32  # grayscale delta (0-255) below which a pixel counts as unchanged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rendered")
    parser.add_argument("committed")
    parser.add_argument("--max-diff", type=float, default=0.03,
                        help="max fraction of pixels allowed to differ (default 0.03)")
    args = parser.parse_args()

    rendered = Image.open(args.rendered).convert("L")
    committed = Image.open(args.committed).convert("L")
    if rendered.size != committed.size:
        print(f"FAIL size differs: rendered {rendered.size} vs committed {committed.size}")
        return 1

    histogram = ImageChops.difference(rendered, committed).histogram()
    total = rendered.size[0] * rendered.size[1]
    changed = sum(histogram[THRESHOLD:]) / total
    verdict = "ok" if changed <= args.max_diff else "FAIL"
    print(f"{verdict} size {rendered.size}, {changed:.4%} of pixels differ by > {THRESHOLD} "
          f"(limit {args.max_diff:.2%})")
    return 0 if verdict == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
