"""A Mediterranean cypress, drawn in code: a tall, narrow, flame-shaped evergreen.

64 x 160 px (2 x 5 tiles). Dense dark foliage in small scale-like clumps, lit on the left and
turning into deep shade on the right, a soft point at the top, and a short trunk at the foot.
Replaces the pack's pine, which read as a northern forest tree on a Greek island.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from paint import hexc, value_noise

W, H = 64, 160
FOLIAGE = [hexc("#1b2a1a"), hexc("#243822"), hexc("#2f4829"), hexc("#3c5a31"), hexc("#4c6d3a"), hexc("#638545"),
           hexc("#7c9a52")]
TRUNK = [hexc("#2e2118"), hexc("#4a3424"), hexc("#674a33")]
OUTLINE = hexc("#121a10")


def half_width(y: float, top: float, bottom: float, widest: float) -> float:
    """The crown's outline: a point at the top, widest a third of the way up, rounded at the foot."""
    t = (y - top) / (bottom - top)          # 0 at the tip, 1 at the foot of the crown
    if t < 0:
        return -1
    if t < 0.68:
        return widest * (t / 0.68) ** 0.75
    u = (t - 0.68) / 0.32
    return widest * np.sqrt(max(0.0, 1 - u * u * 0.85))


def cypress(seed: int = 3, height: int = 140, widest: float = 13.5) -> Image.Image:
    a = np.zeros((H, W, 4), dtype=np.uint8)
    rng = np.random.default_rng(seed)
    cx = W / 2 - 0.5
    bottom = H - 8
    top = bottom - height
    tex = value_noise(W, H, 3, seed + 10)
    clump = value_noise(W, H, 6, seed + 20)
    edge_jit = value_noise(4, H, 5, seed + 30)[:, 0]
    mask = np.zeros((H, W), dtype=bool)
    for y in range(int(top), bottom + 1):
        hw = half_width(y, top, bottom, widest)
        if hw < 0:
            continue
        hw += (edge_jit[y] - 0.5) * 3.0 * min(1.0, (y - top) / 20)
        for x in range(W):
            if abs(x - cx) <= hw:
                mask[y, x] = True
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        hw = max(1.0, half_width(y, top, bottom, widest))
        u = (x - cx) / hw                    # -1 left edge .. 1 right edge
        light = 0.42 - u * 0.42 - (y - top) / (bottom - top) * 0.18
        light += (clump[y, x] - 0.5) * 0.45 + (tex[y, x] - 0.5) * 0.2
        k = int(np.clip(np.round(light * 6), 0, 6))
        a[y, x] = FOLIAGE[k]
    # Flame-like sprays: short upright strokes, lit at the tip, scattered over the crown and
    # thicker on the sunny left side; a few dark clefts between them.
    for _ in range(int(height * widest * 0.22)):
        y = int(rng.integers(int(top) + 4, bottom - 2))
        hw = half_width(y, top, bottom, widest)
        if hw < 2:
            continue
        x = int(round(cx + rng.uniform(-hw, hw) * 0.92))
        if not (0 <= x < W) or not mask[y, x]:
            continue
        u = (x - cx) / hw
        if rng.random() < 0.25 + max(0.0, -u) * 0.5:
            tall = int(rng.integers(2, 5))
            lit = FOLIAGE[6] if u < -0.45 else (FOLIAGE[5] if u < 0.05 else FOLIAGE[4])
            for i in range(tall):
                if mask[y - i, x]:
                    a[y - i, x] = lit if i == tall - 1 else FOLIAGE[min(6, 3 + (1 if u < 0 else 0))]
        else:
            for i in range(int(rng.integers(2, 4))):
                if mask[y + i, x]:
                    a[y + i, x] = FOLIAGE[1] if u > -0.2 else FOLIAGE[2]
    # Outline, darker on the shaded side.
    out = np.zeros_like(mask)
    out[:, 1:] |= mask[:, :-1] & ~mask[:, 1:]
    out[:, :-1] |= mask[:, 1:] & ~mask[:, :-1]
    out[1:, :] |= mask[:-1, :] & ~mask[1:, :]
    out[:-1, :] |= mask[1:, :] & ~mask[:-1, :]
    a[out] = OUTLINE
    # The trunk at the foot.
    for y in range(bottom - 3, H - 2):
        for x in range(int(cx) - 2, int(cx) + 3):
            k = 2 if x < cx - 0.5 else (1 if x < cx + 1.5 else 0)
            a[y, x] = TRUNK[k]
        a[y, int(cx) - 3] = OUTLINE
        a[y, int(cx) + 3] = OUTLINE
    for x in range(int(cx) - 4, int(cx) + 5):
        a[H - 2, x] = TRUNK[0]
    return Image.fromarray(a, "RGBA")


if __name__ == "__main__":
    from pathlib import Path
    im = cypress()
    im2 = cypress(seed=8, height=118, widest=12.0)
    bg = Image.new("RGBA", (W * 2, H), (110, 122, 56, 255))
    bg.alpha_composite(im, (0, 0)); bg.alpha_composite(im2, (W, 0))
    bg.resize((W * 8, H * 4), Image.NEAREST).save(Path(__file__).parent / "preview" / "cypress_x4.png")
    print("ok")
