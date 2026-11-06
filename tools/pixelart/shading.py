"""Form shading for code-drawn pixel art: a silhouette in, banded light-and-shadow out.

A shape is drawn as a flat mask; each pixel's distance to the edge becomes a height (a soft
dome), the height's slope becomes a surface direction, and light from the upper left picks a
colour from a dark-to-light ramp. No anti-aliasing: every pixel gets one ramp colour.
"""
from __future__ import annotations

import math
from collections import deque
from typing import Callable

from px import Px

Mask = set[tuple[int, int]]


def mask(w: int, h: int, draw: Callable[[Px], None]) -> Mask:
    """Pixels made opaque by `draw` on a blank w x h canvas."""
    scratch = Px(w, h)
    draw(scratch)
    px = scratch.im.load()
    return {(x, y) for y in range(h) for x in range(w) if px[x, y][3]}


def distance(m: Mask) -> dict[tuple[int, int], int]:
    """Steps from each pixel of the mask to the nearest pixel outside it (4-neighbour)."""
    dist: dict[tuple[int, int], int] = {}
    q: deque[tuple[int, int]] = deque()
    for (x, y) in m:
        if any((x + dx, y + dy) not in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            dist[(x, y)] = 1
            q.append((x, y))
    while q:
        x, y = q.popleft()
        d = dist[(x, y)] + 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in m and n not in dist:
                dist[n] = d
                q.append(n)
    return dist


def autoshade(p: Px, m: Mask, ramp: list, depth: float = 6.0, light: tuple[float, float] = (-0.62, -0.78),
              lift: float = 0.0, gain: float = 1.0) -> None:
    """Paint the mask with `ramp` (darkest first). A flat top lands in the middle of the ramp,
    edges facing the light go up it and edges facing away go down. `depth` is how many pixels in
    from the edge the dome flattens; `lift` moves the whole shape up (+) or down (-) by bands."""
    dist = distance(m)

    def height(x: int, y: int) -> float:
        d = dist.get((x, y), 0)
        t = min(d, depth) / depth
        return math.sqrt(t) * depth * 0.9

    lx, ly = light
    lz = 0.9
    norm = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / norm, ly / norm, lz / norm
    n_bands = len(ramp)
    for (x, y) in m:
        gx = (height(x + 1, y) - height(x - 1, y)) * 0.5
        gy = (height(x, y + 1) - height(x, y - 1)) * 0.5
        nx, ny, nz = -gx, -gy, 1.0
        nn = math.sqrt(nx * nx + ny * ny + nz * nz)
        v = (nx * lx + ny * ly + nz * lz) / nn
        v = 0.5 + (v - lz) * gain + lift / n_bands
        band = int(math.floor(v * n_bands - 0.5))
        p.dot(x, y, ramp[max(0, min(n_bands - 1, band))])


def outline_mask(p: Px, m: Mask, colour, diagonal: bool = False) -> None:
    """A 1-px line around the outside of a mask (only on pixels that are still empty)."""
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        nb += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    px = p.im.load()
    for (x, y) in m:
        for dx, dy in nb:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in m and 0 <= nx < p.w and 0 <= ny < p.h and px[nx, ny][3] == 0:
                px[nx, ny] = colour


def inner_edge(m: Mask, other: Mask) -> Mask:
    """Pixels of `m` that touch `other`: where to draw a seam between two parts."""
    return {(x, y) for (x, y) in m
            if any((x + dx, y + dy) in other for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
