"""Small numpy helpers for painting pixel art in code: colour space changes, smooth value noise,
ordered dithering and colour ramps. Used by the baked island ground (ground.py), the house
(house.py) and the boat and pier (dock.py).
"""
from __future__ import annotations

import numpy as np
from PIL import Image


def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """rgb floats 0..1, shape (..., 3) -> hsv floats 0..1."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.max(rgb[..., :3], axis=-1)
    mn = np.min(rgb[..., :3], axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-9
    rc = np.where(nz, (mx - r) / np.where(nz, d, 1), 0)
    gc = np.where(nz, (mx - g) / np.where(nz, d, 1), 0)
    bc = np.where(nz, (mx - b) / np.where(nz, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(nz, (h / 6.0) % 1.0, 0.0)
    s = np.where(mx > 1e-9, d / np.where(mx > 1e-9, mx, 1), 0)
    return np.stack([h, s, mx], axis=-1)


def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0] % 1.0, np.clip(hsv[..., 1], 0, 1), np.clip(hsv[..., 2], 0, 1)
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    choices = [np.stack(c, axis=-1) for c in ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))]
    out = np.zeros(h.shape + (3,))
    for k in range(6):
        out = np.where((i == k)[..., None], choices[k], out)
    return out


def value_noise(w: int, h: int, cell: int, seed: int) -> np.ndarray:
    """Smooth noise 0..1 of size (h, w), features about `cell` pixels across (bicubic upsampling)."""
    rng = np.random.default_rng(seed)
    gw, gh = w // cell + 3, h // cell + 3
    g = (rng.random((gh, gw)) * 255).astype(np.uint8)
    big = Image.fromarray(g).resize((gw * cell, gh * cell), Image.BICUBIC)
    a = np.asarray(big).astype(float)[cell:cell + h, cell:cell + w] / 255.0
    return np.clip(a, 0, 1)


def fractal_noise(w: int, h: int, cells=(96, 40, 16), weights=(0.55, 0.3, 0.15), seed: int = 0) -> np.ndarray:
    out = np.zeros((h, w))
    for i, (c, wt) in enumerate(zip(cells, weights)):
        out += value_noise(w, h, c, seed * 31 + i) * wt
    out /= sum(weights)
    lo, hi = np.percentile(out, 2), np.percentile(out, 98)
    return np.clip((out - lo) / max(hi - lo, 1e-6), 0, 1)


BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32.0


def bayer(w: int, h: int, ox: int = 0, oy: int = 0) -> np.ndarray:
    ys, xs = np.mgrid[0:h, 0:w]
    return BAYER4[(ys + oy) % 4, (xs + ox) % 4]


def hexc(s: str, a: int = 255) -> tuple[int, int, int, int]:
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def ramp_pick(ramp: list, t: np.ndarray, dither: np.ndarray | None = None) -> np.ndarray:
    """Pick from a colour ramp (dark -> light) by t in 0..1, optionally with ordered dithering
    between neighbouring steps. Returns uint8 RGBA (..., 4)."""
    n = len(ramp)
    x = np.clip(t, 0, 1) * (n - 1)
    if dither is not None:
        idx = np.floor(x + (dither - 0.5) * 0.9 + 0.5)
    else:
        idx = np.floor(x + 0.5)
    idx = np.clip(idx, 0, n - 1).astype(int)
    arr = np.array(ramp, dtype=np.uint8)
    return arr[idx]


def composite(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    """Alpha-composite RGBA uint8 `src` onto `dst` in place at (x, y), clipped."""
    H, W = dst.shape[:2]
    h, w = src.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(float)
    d = dst[y0:y1, x0:x1].astype(float)
    a = s[..., 3:4] / 255.0
    da = d[..., 3:4] / 255.0
    oa = a + da * (1 - a)
    rgb = (s[..., :3] * a + d[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-6)
    dst[y0:y1, x0:x1, :3] = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
    dst[y0:y1, x0:x1, 3] = np.clip(oa[..., 0] * 255 + 0.5, 0, 255).astype(np.uint8)
