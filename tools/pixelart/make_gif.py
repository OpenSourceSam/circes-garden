"""Assemble browser frames (from playtest.py --frames-dir) into a README GIF with Pillow.

Usage:
    python tools/pixelart/make_gif.py --frames build/frames --out docs/screenshots/playthrough.gif
                                      [--width 360] [--every 2] [--start 0] [--end 0] [--max-mb 4]

Frames are 150 ms apart; `--every 2` keeps one in two (300 ms per frame).
Near-identical consecutive frames are dropped so idle stretches do not bloat the file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="build/frames")
    ap.add_argument("--out", default="docs/screenshots/playthrough.gif")
    ap.add_argument("--width", type=int, default=360)
    ap.add_argument("--every", type=int, default=2)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=0, help="0 = last frame")
    ap.add_argument("--max-mb", type=float, default=4.0)
    args = ap.parse_args()

    frames_dir = (REPO / args.frames).resolve()
    files = sorted(frames_dir.glob("f*.png"))
    if args.end:
        files = files[: args.end]
    files = files[args.start :: max(1, args.every)]
    if not files:
        print("no frames")
        return 1

    images: list[Image.Image] = []
    durations: list[int] = []
    last = None
    for f in files:
        im = Image.open(f).convert("RGB")
        ratio = args.width / im.width
        im = im.resize((args.width, int(im.height * ratio)), Image.Resampling.NEAREST)
        if last is not None:
            diff = ImageChops.difference(im, last).getbbox()
            if diff is None:
                durations[-1] += 150 * args.every
                continue
        images.append(im)
        durations.append(150 * args.every)
        last = im

    out = (REPO / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    pal = [im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in images]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durations, loop=0, optimize=True, disposal=1)
    size_mb = out.stat().st_size / 1e6
    print(f"{len(images)} frames -> {out} ({size_mb:.2f} MB)")
    if size_mb > args.max_mb:
        print(f"over {args.max_mb} MB: raise --every or lower --width")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
