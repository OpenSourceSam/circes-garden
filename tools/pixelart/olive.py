"""An olive tree, drawn in code: a short gnarled trunk that splits into twisting limbs, under a
broad, uneven canopy of loose silvery-green clumps with gaps between them.

Three sizes replace the pack's mismatched trees (each was drawn with a different number of
shades and leaf size, so side by side they looked like the work of different artists): one
olive design, in the island's palette, lit from the upper left like everything else.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from paint import hexc, value_noise

LEAF = [hexc("#232c1e"), hexc("#323e2a"), hexc("#445238"), hexc("#576748"), hexc("#6c7d5a"), hexc("#84946f"),
        hexc("#9eac88"), hexc("#b6c1a0")]
BARK = [hexc("#231d19"), hexc("#3a312a"), hexc("#53483d"), hexc("#6d6152"), hexc("#877a69"), hexc("#a29582")]
OUTLINE = hexc("#1a2016")
BARK_OUTLINE = hexc("#1c1612")


def olive(w_tiles: int = 4, h_tiles: int = 4, seed: int = 1) -> Image.Image:
    W, H = w_tiles * 32, h_tiles * 32
    rng = np.random.default_rng(seed)
    a = np.zeros((H, W, 4), dtype=np.uint8)
    cx = W / 2 + rng.uniform(-4, 4)
    base_y = H - 5
    crown_bottom = H * 0.62
    # ---- trunk and limbs: thick polylines that taper, twisting as they rise ----------------
    limbs = []
    trunk_top = (cx + rng.uniform(-6, 6), base_y - H * 0.26)
    limbs.append([(cx, base_y), ((cx + trunk_top[0]) / 2 + rng.uniform(-5, 5), base_y - H * 0.13), trunk_top])
    for k in range(3):
        side = (-1, 0.15, 1)[k] * (W * 0.3)
        end = (trunk_top[0] + side + rng.uniform(-6, 6), crown_bottom - H * rng.uniform(0.16, 0.3))
        mid = ((trunk_top[0] + end[0]) / 2 + rng.uniform(-6, 6), (trunk_top[1] + end[1]) / 2)
        limbs.append([trunk_top, mid, end])
    bark_mask = np.zeros((H, W), dtype=bool)
    bark_k = np.zeros((H, W))
    for li, pts in enumerate(limbs):
        r0, r1 = (W * 0.085, W * 0.06) if li == 0 else (W * 0.05, W * 0.022)
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            n = int(max(abs(xb - xa), abs(yb - ya))) + 2
            for i in range(n + 1):
                t = i / n
                seg_t = (pts.index((xa, ya)) + t) / (len(pts) - 1)
                r = r0 + (r1 - r0) * seg_t
                px, py = xa + (xb - xa) * t, ya + (yb - ya) * t
                for yy in range(int(py - r - 1), int(py + r + 2)):
                    for xx in range(int(px - r - 1), int(px + r + 2)):
                        if 0 <= xx < W and 0 <= yy < H and (xx - px) ** 2 + ((yy - py) * 0.8) ** 2 <= r * r:
                            u = (xx - px) / max(r, 1)
                            bark_mask[yy, xx] = True
                            bark_k[yy, xx] = 3.6 - u * 1.7
    # Flared roots at the foot.
    for dx in (-1, 1):
        for i in range(int(W * 0.11)):
            x = int(cx + dx * (W * 0.05 + i))
            y = int(base_y - max(0, 4 - i // 3))
            for yy in range(y, base_y + 1):
                if 0 <= x < W:
                    bark_mask[yy, x] = True
                    bark_k[yy, x] = 2.6 if dx > 0 else 3.6
    furrow = value_noise(W, H, 3, seed + 3)
    ys, xs = np.nonzero(bark_mask)
    for y, x in zip(ys, xs):
        k = bark_k[y, x] + (furrow[y, x] - 0.5) * 1.6
        if (x * 3 + int(y * 0.4)) % 5 == 0:
            k -= 1.2                                       # deep vertical furrows in the bark
        a[y, x] = BARK[int(np.clip(round(k), 0, 5))]
    # A hollow in the old trunk.
    hx, hy = int(cx + rng.uniform(-3, 3)), int(base_y - H * 0.12)
    for yy in range(hy - 4, hy + 4):
        for xx in range(hx - 2, hx + 3):
            if ((xx - hx) / 2.4) ** 2 + ((yy - hy) / 4.2) ** 2 <= 1 and bark_mask[yy, xx]:
                a[yy, xx] = BARK[0]
    a[hy - 4, hx] = BARK[4]

    # ---- canopy: loose clumps with gaps -------------------------------------------------------
    n = 4 + w_tiles
    clumps = []
    top = H * 0.08
    for i in range(n):
        t = i / max(1, n - 1)
        rx = min(W * rng.uniform(0.13, 0.18), 30)
        ry = H * rng.uniform(0.1, 0.13)
        x = W * (0.18 + 0.64 * t) + rng.uniform(-5, 5)
        x = float(np.clip(x, rx + 5, W - rx - 5))          # never cut by the picture's sides
        y = top + H * (0.24 + 0.16 * abs(t - 0.5) * 2) + rng.uniform(-5, 7)
        clumps.append((x, y, rx, ry, 0.0))
    for _ in range(2):                                     # a couple of lower, smaller clumps
        rx = W * 0.12
        clumps.append((float(np.clip(W * rng.uniform(0.3, 0.7), rx + 5, W - rx - 5)), crown_bottom - H * 0.09,
                       rx, H * 0.08, 0.4))
    clumps.append((cx + rng.uniform(-8, 8), top + H * 0.1, min(W * 0.16, 26), H * 0.09, 0.3))
    edge_n = value_noise(W, H, 4, seed + 5)
    tex = value_noise(W, H, 3, seed + 6)
    leaf_mask = np.zeros((H, W), dtype=bool)
    leaf_k = np.full((H, W), -1.0)
    clumps.sort(key=lambda c: c[1])                        # back (higher) clumps first
    for (x0, y0, rx, ry, lift) in clumps:
        for y in range(int(y0 - ry - 3), int(y0 + ry + 3)):
            for x in range(int(x0 - rx - 3), int(x0 + rx + 3)):
                if not (0 <= x < W and 0 <= y < H - 2):
                    continue
                d = ((x - x0) / rx) ** 2 + ((y - y0) / ry) ** 2 - (edge_n[y, x] - 0.5) * 0.7
                if d > 1:
                    continue
                u, v = (x - x0) / rx, (y - y0) / ry
                k = 3.7 - u * 1.3 - v * 2.9 + lift          # lit on the upper left, dark underneath
                if d > 0.78:
                    k -= 1.3 if v > -0.25 else -0.5         # rim: dark below, silver above
                k += (tex[y, x] - 0.5) * 1.6
                leaf_mask[y, x] = True
                leaf_k[y, x] = k
    # Leaf dabs: small strokes of silver and shadow over the clumps.
    ys, xs = np.nonzero(leaf_mask)
    pick = rng.random(len(ys)) < 0.06
    for y, x in zip(ys[pick], xs[pick]):
        bump = 1.6 if leaf_k[y, x] > 3.5 else -1.4
        for dx in (0, 1):
            if x + dx < W and leaf_mask[y, x + dx]:
                leaf_k[y, x + dx] += bump
    ys, xs = np.nonzero(leaf_mask)
    for y, x in zip(ys, xs):
        a[y, x] = LEAF[int(np.clip(round(leaf_k[y, x]), 0, 7))]
    # Where a clump lies over the one behind it, the one behind is in its shadow.
    over = np.zeros_like(leaf_mask)
    for (x0, y0, rx, ry, lift) in clumps:
        for x in range(int(x0 - rx), int(x0 + rx) + 1):
            if not (0 <= x < W):
                continue
            yt = y0 - ry * np.sqrt(max(0.0, 1 - ((x - x0) / rx) ** 2))
            for dy in (1, 2):
                y = int(yt) - dy
                if 0 <= y < H and leaf_mask[y, x]:
                    over[y, x] = True
    ys, xs = np.nonzero(over)
    for y, x in zip(ys, xs):
        a[y, x] = LEAF[int(np.clip(round(leaf_k[y, x]) - 2, 0, 7))]
    # Twigs showing in the gaps under the canopy.
    for _ in range(w_tiles * 3):
        x = int(rng.uniform(W * 0.2, W * 0.8))
        y = int(rng.uniform(H * 0.35, crown_bottom))
        for i in range(4):
            xx, yy = x + i * (1 if x > cx else -1), y - i
            if 0 <= xx < W and 0 <= yy < H and not leaf_mask[yy, xx] and not bark_mask[yy, xx] and a[yy, xx, 3] == 0:
                a[yy, xx] = BARK[2]
    # Outline round leaves and bark.
    solid = a[..., 3] > 0
    out = np.zeros_like(solid)
    out[:, 1:] |= solid[:, :-1] & ~solid[:, 1:]
    out[:, :-1] |= solid[:, 1:] & ~solid[:, :-1]
    out[1:, :] |= solid[:-1, :] & ~solid[1:, :]
    out[:-1, :] |= solid[1:, :] & ~solid[:-1, :]
    near_bark = np.zeros_like(solid)
    near_bark[1:-1, 1:-1] = bark_mask[:-2, 1:-1] | bark_mask[2:, 1:-1] | bark_mask[1:-1, :-2] | bark_mask[1:-1, 2:]
    a[out & near_bark & ~leaf_mask] = BARK_OUTLINE
    a[out & ~near_bark] = OUTLINE
    a[out & near_bark & leaf_mask] = OUTLINE
    # Keep the last rows clear (the placement check reads a filled bottom row as a cut picture).
    a[H - 2:, :] = 0
    return Image.fromarray(a, "RGBA")


if __name__ == "__main__":
    from pathlib import Path
    ims = [olive(4, 4, 1), olive(3, 4, 2), olive(5, 4, 3)]
    W = sum(i.width for i in ims) + 20
    out = Image.new("RGBA", (W, 128), (110, 122, 56, 255))
    x = 0
    for i in ims:
        out.alpha_composite(i, (x, 0)); x += i.width + 10
    out.resize((W * 3, 128 * 3), Image.NEAREST).save(Path(__file__).parent / "preview" / "olive_x3.png")
    print("ok")
