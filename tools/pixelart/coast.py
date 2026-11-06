"""The sea round Aiaia, its banks, the beach and the pier, painted into the baked island ground.

The LPC sea tiles repeated every 64 px with bright cyan dashes, and the island's edge was a thin
wavy line. Here the water is a soft teal that turns turquoise in the shallows, with a broken
foam line along the shore and sparse pale glints; the grass ends in a low earth bank whose face
shows on the sides that face the viewer; the south shore is a curved beach of dry and wet sand
with pebbles and shells; and the pier is a plank jetty on posts that stand in the water, with
its shadow on the sea.

The painted coast only ever adds land over the edge of sea cells (never paints water over
walkable land), so Circe cannot appear to walk on water.
"""
from __future__ import annotations

import numpy as np

import paint
from paint import hexc

T = 32

WATER = [hexc("#28627a"), hexc("#2f6f84"), hexc("#367b8c"), hexc("#408a95"), hexc("#4f9d9d"),
         hexc("#66b1a6"), hexc("#82c2b1")]
FOAM = hexc("#e4efe3")
FOAM_SHADE = hexc("#b4d3c8")
GLINT = hexc("#8fc9c4")
BANK = [hexc("#3a2818"), hexc("#533922"), hexc("#6d4b2d"), hexc("#86603a"), hexc("#9c7547")]
SAND = [hexc("#a8946b"), hexc("#c4ae80"), hexc("#d8c493"), hexc("#e4d3a6"), hexc("#efe3bf")]
WET = [hexc("#9c8862"), hexc("#ae9a72")]
WOOD = [hexc("#3d2a1b"), hexc("#5a3f28"), hexc("#744f31"), hexc("#8d653f"), hexc("#a47b4e"), hexc("#bb9462")]


def grow(mask: np.ndarray, steps: int) -> np.ndarray:
    """Distance (in pixels, octagonal) from every pixel outside `mask` to the mask, up to steps;
    inside the mask 0, beyond `steps` steps + 1."""
    dist = np.where(mask, 0, steps + 1).astype(np.int16)
    cur = mask.copy()
    for k in range(1, steps + 1):
        nxt = cur.copy()
        nxt[1:, :] |= cur[:-1, :]
        nxt[:-1, :] |= cur[1:, :]
        nxt[:, 1:] |= cur[:, :-1]
        nxt[:, :-1] |= cur[:, 1:]
        if k % 2 == 0:                                       # diagonal every other step
            nxt[1:, 1:] |= cur[:-1, :-1]
            nxt[1:, :-1] |= cur[:-1, 1:]
            nxt[:-1, 1:] |= cur[1:, :-1]
            nxt[:-1, :-1] |= cur[1:, 1:]
        dist[nxt & ~cur] = k
        cur = nxt
    return dist


def land_mask(rows: list[str]) -> np.ndarray:
    """Pixels of land cells. The pier's first cell, on the beach, counts as land (sand under it);
    the pier cells out over the sea count as water."""
    H, W = len(rows), len(rows[0])
    m = np.zeros((H * T, W * T), dtype=bool)
    for r, line in enumerate(rows):
        for c, k in enumerate(line):
            land = k not in ("~", "P") or (k == "P" and r > 0 and rows[r - 1][c] not in ("~", "P"))
            if land:
                m[r * T:(r + 1) * T, c * T:(c + 1) * T] = True
    return m


def paint_coast(g, rows: list[str]) -> dict:
    """Paint water, banks and beach into g.img. Returns masks other passes need."""
    img, h, w = g.img, g.h, g.w
    rng = np.random.default_rng(23)
    cells_land = land_mask(rows)
    # Land reaches a few pixels out over the sea cells, by a wavy amount, so the coast is not a
    # ruler line along the tile grid.
    reach = 3 + paint.fractal_noise(w, h, (60, 20, 7), (0.5, 0.35, 0.15), seed=31) * 8
    d_out = grow(cells_land, 12)
    land = cells_land | (d_out <= reach)
    water = ~land
    d_w = grow(land, 30)                                     # water: distance from the shore (recomputed below)
    d_l = grow(water, 40)                                    # land: distance from the shore

    # Which shore faces south (land above the water): there the bank's face shows, or the beach.
    beach_rows = [r for r, line in enumerate(rows) if "S" in line]
    beach_y = (min(beach_rows) * T) if beach_rows else h
    south = np.zeros_like(land)
    for k in range(1, 7):
        south[k:, :] |= land[:-k, :] & water[k:, :]

    # ---- water --------------------------------------------------------------------------
    jitter = (paint.value_noise(w, h, 9, 41) - 0.5) * 4
    deep = paint.fractal_noise(w, h, (120, 40), (0.7, 0.3), seed=43)
    dd = d_w + jitter
    band = np.where(dd < 5, 6, np.where(dd < 9, 5, np.where(dd < 14, 4, np.where(dd < 22, 3, 2))))
    # (No separate deep-water band: both a hard-edged and a dithered one read as shapes, not depth.)
    wcol = np.array(WATER, dtype=np.uint8)[band]
    img[water] = wcol[water]
    # Glints: short pale dashes, a few pixels long, scattered (not on a grid).
    ys, xs = np.nonzero(water & (d_w > 8))
    pick = rng.random(len(ys)) < 0.0035
    for y, x in zip(ys[pick], xs[pick]):
        n = int(rng.integers(2, 5))
        b = int(band[y, x])
        c = np.array(WATER[min(6, b + 2)], dtype=np.uint8)
        for i in range(n):
            if 0 <= x + i < w and water[y, x + i]:
                img[y, x + i] = c
        if rng.random() < 0.4 and y + 1 < h:
            for i in range(1, n + 1):
                if 0 <= x + i < w and water[y + 1, x + i]:
                    img[y + 1, x + i] = np.array(WATER[min(6, b + 1)], dtype=np.uint8)

    # Rows of small wave crests across the open water: a short lit arc with a shadow under it,
    # loosely in rows, so the sea reads as moving water and not as a flat slab.
    for row_y in range(8, h, 15):
        x = int(rng.integers(0, 30))
        while x < w:
            y = row_y + int(rng.integers(-3, 4))
            n = int(rng.integers(6, 12))
            if 0 <= y < h - 1 and all(0 <= x + i < w and water[y, x + i] and d_w[y, x + i] > 10 for i in range(n)):
                b = int(band[y, x])
                lit = np.array(WATER[min(6, b + 2)], dtype=np.uint8)
                dark = np.array(WATER[max(0, b - 1)], dtype=np.uint8)
                for i in range(n):
                    arc = 1 if i in (0, n - 1) else 0
                    img[y + arc, x + i] = lit
                    if not arc:
                        img[y + 1, x + i] = dark
            x += int(rng.integers(26, 60))

    # ---- the grass bank: its face where the shore faces the viewer, a dark rim elsewhere ----
    stones = rng.random((h, w))
    above = np.arange(h)[:, None] < beach_y - 6
    run = water.copy()                                       # water all the way up k rows
    for k in range(5):
        shifted = np.zeros_like(land)
        shifted[k + 1:, :] = land[:-(k + 1), :]
        face = run & shifted & above
        c = np.array(BANK[[4, 3, 3, 2, 1][k]], dtype=np.uint8)
        img[face] = c
        if k in (1, 2, 3):
            st = face & (stones < 0.12)
            img[st] = np.array(hexc("#8f8577"), dtype=np.uint8)
            st2 = face & (stones < 0.05)
            img[st2] = np.array(hexc("#6d665b"), dtype=np.uint8)
        wshift = np.zeros_like(water)
        wshift[k + 1:, :] = water[:-(k + 1), :]
        run = run & wshift
    face_any = np.zeros_like(water)
    run = water.copy()
    for k in range(5):
        shifted = np.zeros_like(land)
        shifted[k + 1:, :] = land[:-(k + 1), :]
        face_any |= run & shifted & above
        wshift = np.zeros_like(water)
        wshift[k + 1:, :] = water[:-(k + 1), :]
        run = run & wshift
    water = water & ~face_any                                # the bank's face is not water
    # Rim of darker grass along the top of every grass shore.
    rim = land & (d_l <= 1)
    img[rim, :3] = (img[rim, :3].astype(float) * 0.72).astype(np.uint8)

    # ---- beach -------------------------------------------------------------------------
    sand = np.zeros_like(land)
    if beach_rows:
        top = paint.value_noise(w, 4, 26, 51)[0]
        xs_ = np.arange(w)
        land_cols = np.nonzero(cells_land[beach_y + 8])[0]
        bx0, bx1 = land_cols.min(), land_cols.max()
        # The beach's top edge: wavy, curving down to meet the water at both ends.
        edge = beach_y - 6 + (top - 0.5) * 10
        end_l = np.clip((bx0 + 70 - xs_) / 70.0, 0, 1)
        end_r = np.clip((xs_ - (bx1 - 70)) / 70.0, 0, 1)
        edge = edge + (end_l ** 1.6 + end_r ** 1.6) * 44
        yy = np.arange(h)[:, None]
        sand = land & (yy >= edge[None, :]) & (yy > beach_y - 40)
        # Dry sand: one warm tone with fine grain and soft wind ripples, not blotches.
        grain = rng.random((h, w))
        yy_, xx_ = np.mgrid[0:h, 0:w]
        ripple = (yy_ + np.round(np.sin(xx_ / 11.0) * 2 + np.sin(xx_ / 4.3) * 0.6)) % 9
        sc = np.full((h, w), 2)
        sc = np.where(ripple == 0, 3, sc)
        sc = np.where(ripple == 1, 1, np.where(grain < 0.05, 1, sc))
        sc = np.where(grain > 0.96, 3, sc)
        sc = np.where(d_l <= 4, 0, sc)                          # wet sand at the water's edge
        scol = np.array(SAND, dtype=np.uint8)[sc]
        img[sand] = scol[sand]
        wet = sand & (d_l <= 4)
        img[wet] = np.where((d_l[wet] <= 2)[:, None], np.array(WET[0], dtype=np.uint8), np.array(WET[1], dtype=np.uint8))
        # The sand's top edge: a lighter lip, then grass tufts overlapping it.
        lip = sand & ~np.roll(sand, 1, axis=0)
        img[lip] = np.array(SAND[4], dtype=np.uint8)
        # A line of washed-up seaweed and bits of driftwood just above the wet sand.
        ys, xs = np.nonzero(sand & (d_l >= 5) & (d_l <= 7))
        pick = rng.random(len(ys)) < 0.05
        for y, x in zip(ys[pick], xs[pick]):
            if rng.random() < 0.75:
                g._px(x, y, hexc("#4f5a2c")); g._px(x + 1, y, hexc("#3c4521"))
            else:
                g._px(x, y, hexc("#8a7253")); g._px(x + 1, y, hexc("#8a7253")); g._px(x + 2, y, hexc("#6c573e"))
        # Pebbles and shells on the dry sand.
        ys, xs = np.nonzero(sand & (d_l > 6))
        pick = rng.random(len(ys)) < 0.004
        for y, x in zip(ys[pick], xs[pick]):
            kind = rng.random()
            if kind < 0.5:
                g._px(x, y, hexc("#8d8578")); g._px(x + 1, y, hexc("#a9a093")); g._px(x, y + 1, hexc("#6c655b"))
            elif kind < 0.8:
                g._px(x, y, hexc("#f2e6d8")); g._px(x + 1, y, hexc("#e0c9b6")); g._px(x, y - 1, hexc("#f7efe4"))
            else:
                g._px(x, y, hexc("#e8b4a0")); g._px(x + 1, y, hexc("#c98f7c"))
    # ---- foam along every shore, broken; on the beach a wider wash and a second wave ---------
    d_w = grow(~water, 30)
    fn = paint.value_noise(w, h, 6, 61)
    near_beach = np.zeros_like(water)
    if beach_rows:
        near_beach = grow(sand, 14) <= 12
    foam1 = water & (d_w <= 1) & (fn > 0.3)
    foam2 = water & (d_w == 2) & (fn > 0.55)
    img[foam2] = np.array(FOAM_SHADE, dtype=np.uint8)
    img[foam1] = np.array(FOAM, dtype=np.uint8)
    if beach_rows:
        wash = water & near_beach & (d_w <= 3) & (fn > 0.25)
        img[wash] = np.array(FOAM, dtype=np.uint8)
        wave = water & near_beach & (np.abs(d_w - 8 - (fn - 0.5) * 3) < 0.8) & (fn > 0.45)
        img[wave] = np.array(FOAM_SHADE, dtype=np.uint8)
    g.grass_ok &= ~(water | sand)
    g.grass_ok &= ~(grow(water, 6) <= 5)
    return {"land": land, "water": water, "sand": sand, "d_w": d_w, "d_l": d_l}


SEA_ROCK = [hexc("#3d3a36"), hexc("#57524b"), hexc("#756d62"), hexc("#958b7c"), hexc("#b2a896")]


def sea_rock(g, cx: int, cy: int, rx: int, ry: int, seed: int, water: np.ndarray) -> None:
    """A rock standing out of the sea: lit on top and to the left, dark at the waterline, its
    submerged base showing as a darker shape, and a ring of broken foam round it."""
    rng = np.random.default_rng(seed)
    img = g.img
    jit = paint.value_noise(2 * rx + 9, 2 * ry + 9, 3, seed)
    for y in range(cy - ry - 4, cy + ry + 5):
        for x in range(cx - rx - 4, cx + rx + 5):
            if not (0 <= x < g.w and 0 <= y < g.h) or not water[y, x]:
                continue
            j = jit[y - cy + ry + 4, x - cx + rx + 4]
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 - (j - 0.5) * 0.5
            if d <= 1.0:
                up = (cy - y) / ry
                k = 4 if (up > 0.35 and x < cx + rx * 0.2) else (3 if up > -0.1 else (2 if up > -0.55 else 1))
                if x > cx + rx * 0.55:
                    k = max(1, k - 1)
                img[y, x, :3] = np.array(SEA_ROCK[k][:3], dtype=np.uint8)
            elif d <= 1.6 and y > cy:
                img[y, x, :3] = (img[y, x, :3].astype(float) * 0.7).astype(np.uint8)   # base under water
            elif d <= 2.1 and rng.random() < 0.55:
                img[y, x, :3] = np.array(FOAM[:3] if d < 1.85 else FOAM_SHADE[:3], dtype=np.uint8)


def paint_pier(g, x0: int, x1: int, y0: int, y1: int, water: np.ndarray) -> None:
    """A plank jetty from (x0, y0) to (x1, y1): planks across it with gaps, edge beams, posts in
    the water along both sides and under its end, and its shadow on the sea."""
    img = g.img
    rng = np.random.default_rng(71)
    # Shadow on the water to the right of the pier and under its end (light from the upper left).
    for y in range(y0, y1 + 10):
        for x in range(x0 + 2, x1 + 9):
            if 0 <= y < g.h and 0 <= x < g.w and water[y, x] and (x > x1 or y > y1):
                img[y, x, :3] = (img[y, x, :3].astype(float) * 0.68).astype(np.uint8)
    # Posts standing in the water along the sides and under the end.
    posts = [(x0 - 3, y) for y in range(y0 + 22, y1, 30)] + [(x1 - 1, y) for y in range(y0 + 22, y1, 30)]
    posts += [(x0 + 2, y1 + 4), ((x0 + x1) // 2 - 2, y1 + 4), (x1 - 6, y1 + 4)]
    for (px, py) in posts:
        for y in range(py - 4, py + 7):
            for x in range(px, px + 5):
                c = WOOD[3] if x == px + 1 else (WOOD[2] if x < px + 4 else WOOD[1])
                if x == px or y == py + 6:
                    c = WOOD[0]
                g._px(x, y, c)
        for x in range(px, px + 5):                       # cut top of the post, lit
            g._px(x, py - 5, WOOD[5] if x < px + 3 else WOOD[4])
        for x in range(px - 2, px + 7):                   # ripple round its foot
            if 0 <= py + 7 < g.h and water[py + 7, min(g.w - 1, max(0, x))]:
                g._px(x, py + 7, FOAM if abs(x - px - 2) < 3 else FOAM_SHADE)
    # The deck: planks across the pier, each a slightly different board, with dark gaps.
    y = y0
    while y < y1 - 1:
        ph = 6
        tone = int(rng.integers(2, 5))
        joint = int(rng.integers(x0 + 18, x1 - 18)) if rng.random() < 0.6 else None
        for yy in range(y, min(y + ph, y1)):
            for x in range(x0, x1 + 1):
                if yy == y + ph - 1:
                    c = WOOD[0]                            # the gap to the next plank
                elif yy == y:
                    c = WOOD[min(5, tone + 1)]             # lit leading edge
                else:
                    c = WOOD[tone]
                    if (x * 13 + yy * 7) % 17 == 0:
                        c = WOOD[max(1, tone - 1)]         # grain
                if joint is not None and x == joint and yy < y + ph - 1:
                    c = WOOD[0]
                g._px(x, yy, c)
        for nx in (x0 + 3, (x0 + x1) // 2, x1 - 3):        # nails over the beams below
            g._px(nx, y + 2, hexc("#2a221c"))
        if rng.random() < 0.25:                             # a knot
            kx = int(rng.integers(x0 + 6, x1 - 6))
            g._px(kx, y + 2, WOOD[1]); g._px(kx + 1, y + 3, WOOD[1])
        y += ph
    # Edge beams along both sides, and the deck's thickness at its end.
    for yy in range(y0, y1 + 1):
        g._px(x0 - 1, yy, WOOD[0]); g._px(x0, yy, WOOD[4]); g._px(x0 + 1, yy, WOOD[3])
        g._px(x1 - 1, yy, WOOD[2]); g._px(x1, yy, WOOD[1]); g._px(x1 + 1, yy, WOOD[0])
    for x in range(x0 - 1, x1 + 2):
        g._px(x, y1, WOOD[2]); g._px(x, y1 + 1, WOOD[1]); g._px(x, y1 + 2, WOOD[1]); g._px(x, y1 + 3, WOOD[0])
    # On the deck: a coil of rope and a mooring post at the end.
    cx, cy = x1 - 14, y1 - 12
    for a in range(0, 360, 20):
        for rr in (2.5, 4.5):
            x = int(round(cx + np.cos(np.radians(a)) * rr)); yy = int(round(cy + np.sin(np.radians(a)) * rr * 0.7))
            g._px(x, yy, hexc("#c9b27a") if a < 180 else hexc("#9b8456"))
    g._px(cx, cy, hexc("#6e5a36"))
    bx, by = x0 + 8, y1 - 10
    for yy in range(by - 6, by + 2):
        for x in range(bx, bx + 5):
            g._px(x, yy, WOOD[4] if x == bx + 1 else (WOOD[3] if x < bx + 4 else WOOD[1]))
    for x in range(bx, bx + 5):
        g._px(x, by - 7, WOOD[5]); g._px(x, by + 2, WOOD[0])
    g._px(bx - 1, by - 3, hexc("#c9b27a")); g._px(bx + 5, by - 2, hexc("#9b8456"))
