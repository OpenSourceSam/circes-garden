"""Tiny pixel-art helpers on top of Pillow. No anti-aliasing anywhere.

Coordinates are inclusive pixel coordinates. Every drawing call writes solid
RGBA pixels (alpha 255) or clears to alpha 0.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw

RGBA = tuple[int, int, int, int]


def rgb(hexstr: str) -> RGBA:
    h = hexstr.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


# Shared by the code-drawn props, icons and tiles.
OUTLINE = rgb("#241a26")
WHITE = rgb("#ffffff")


def darken(c: RGBA, f: float = 0.72) -> RGBA:
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f), 255)


def lighten(c: RGBA, f: float = 1.22) -> RGBA:
    return (min(255, int(c[0] * f)), min(255, int(c[1] * f)), min(255, int(c[2] * f)), 255)


class Px:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    # --- primitives -----------------------------------------------------
    def dot(self, x: int, y: int, c: RGBA) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), c)

    def rect(self, x0: int, y0: int, x1: int, y1: int, c: RGBA) -> None:
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        self.d.rectangle([x0, y0, x1, y1], fill=c)

    def hline(self, x0: int, x1: int, y: int, c: RGBA) -> None:
        self.rect(x0, y, x1, y, c)

    def vline(self, x: int, y0: int, y1: int, c: RGBA) -> None:
        self.rect(x, y0, x, y1, c)

    def ellipse(self, x0: int, y0: int, x1: int, y1: int, c: RGBA) -> None:
        self.d.ellipse([x0, y0, x1, y1], fill=c)

    def poly(self, pts: Iterable[tuple[int, int]], c: RGBA) -> None:
        self.d.polygon(list(pts), fill=c)

    def trapezoid(self, cx: int, y_top: int, w_top: int, y_bot: int, w_bot: int, c: RGBA) -> None:
        """Vertical trapezoid centred on cx, drawn row by row so edges stay crisp."""
        rows = y_bot - y_top
        for i in range(rows + 1):
            t = i / rows if rows else 0
            w = w_top + (w_bot - w_top) * t
            half = int(round(w / 2.0))
            self.hline(cx - half, cx + half - (1 if w % 2 == 0 and w > 0 else 0), y_top + i, c)

    def clear_rect(self, x0: int, y0: int, x1: int, y1: int) -> None:
        self.rect(x0, y0, x1, y1, (0, 0, 0, 0))

    # --- passes -----------------------------------------------------------
    def outline(self, c: RGBA, diagonal: bool = False) -> None:
        """Draw a 1-px outline around everything that is opaque."""
        src = self.im.load()
        add = []
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonal:
            nb += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3] != 0:
                    continue
                for dx, dy in nb:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[nx, ny][3] != 0:
                        add.append((x, y))
                        break
        for x, y in add:
            src[x, y] = c

    def recolor(self, old: RGBA, new: RGBA) -> None:
        px = self.im.load()
        for y in range(self.h):
            for x in range(self.w):
                if px[x, y] == old:
                    px[x, y] = new

    def shade_right(self, cols: int, factor: float, skip: set[RGBA] | None = None) -> None:
        """Darken the right-most `cols` opaque columns of each row (simple side light)."""
        px = self.im.load()
        skip = skip or set()
        for y in range(self.h):
            xs = [x for x in range(self.w) if px[x, y][3] != 0]
            if not xs:
                continue
            for x in xs[-cols:]:
                c = px[x, y]
                if c not in skip:
                    px[x, y] = darken(c, factor)

    def mirrored(self) -> "Px":
        other = Px(self.w, self.h)
        other.im = self.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        other.d = ImageDraw.Draw(other.im)
        return other

    def paste(self, other: "Px", x: int, y: int) -> None:
        self.im.alpha_composite(other.im, (x, y))

    def shifted(self, dx: int, dy: int) -> "Px":
        other = Px(self.w, self.h)
        other.im.alpha_composite(self.im, (dx, dy)) if dx >= 0 and dy >= 0 else other.im.paste(
            self.im.crop((max(0, -dx), max(0, -dy), self.w, self.h)), (max(0, dx), max(0, dy)))
        other.d = ImageDraw.Draw(other.im)
        return other

    def bbox(self):
        return self.im.getbbox()


def sheet(frames: list[list[Px]], cell_w: int, cell_h: int) -> Image.Image:
    """frames[row][col] -> one RGBA sheet."""
    rows = len(frames)
    cols = max(len(r) for r in frames)
    out = Image.new("RGBA", (cols * cell_w, rows * cell_h), (0, 0, 0, 0))
    for r, row in enumerate(frames):
        for c, fr in enumerate(row):
            out.alpha_composite(fr.im, (c * cell_w, r * cell_h))
    return out


def preview(img: Image.Image, scale: int = 4, grid: int | None = None, bg=(90, 120, 70, 255)) -> Image.Image:
    big = Image.new("RGBA", (img.width * scale, img.height * scale), bg)
    big.alpha_composite(img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST))
    if grid:
        d = ImageDraw.Draw(big)
        for x in range(0, big.width, grid * scale):
            d.line([(x, 0), (x, big.height)], fill=(255, 255, 255, 90))
        for y in range(0, big.height, grid * scale):
            d.line([(0, y), (big.width, y)], fill=(255, 255, 255, 90))
    return big


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)
