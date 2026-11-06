"""Hermes' terrace and Circe's garden beds, painted into the baked island ground (ground.py).

The terrace was a flat beige slab cut from a tile sheet; here it is a raised platform of marble
paving with a lit rim, a front face of squared blocks, two steps down to the path, a small
mosaic in the middle, wear, a few cracks and moss in the joints. The garden beds were ragged
blobs of soil; here each is a rectangle of tilled earth in neat furrows inside a low border of
fieldstones.
"""
from __future__ import annotations

import numpy as np

import paint
from paint import hexc

MARBLE = [hexc("#9d927f"), hexc("#b9af9b"), hexc("#cbc1ad"), hexc("#d8cfbc"), hexc("#e4dccb"), hexc("#efe9db")]
BLOCK = [hexc("#5f574b"), hexc("#7b7264"), hexc("#958b7b"), hexc("#aaa08e")]
MOSS = [hexc("#55632c"), hexc("#6b7a37")]
SOIL = [hexc("#35251a"), hexc("#4b3423"), hexc("#61452e"), hexc("#7a583a"), hexc("#946d48"), hexc("#a98157")]
FIELDSTONE = [hexc("#4a4136"), hexc("#6a5d4d"), hexc("#877864"), hexc("#a29279"), hexc("#b9a98f")]
TERRACOTTA = [hexc("#7c3522"), hexc("#a5492d"), hexc("#c4643c")]
INK = hexc("#2c2622")


def paint_terrace(g, x0: int, y0: int, x1: int, y1: int, step_x0: int, step_x1: int) -> None:
    """The platform's top covers (x0, y0)-(x1, y1 - FACE); its front face is the last FACE rows,
    with steps between step_x0 and step_x1 reaching down past y1."""
    rng = np.random.default_rng(83)
    FACE = 9
    top_y1 = y1 - FACE
    img = g.img
    # ---- top: marble slabs, three across, in rows, joints slightly irregular -----------------
    tex = paint.value_noise(x1 - x0 + 1, y1 - y0 + 1, 7, 85)
    ys_j = list(range(y0 + 4, top_y1 - 2, 25))
    for y in range(y0, top_y1 + 1):
        for x in range(x0, x1 + 1):
            t = tex[y - y0, x - x0]
            k = 3 if t < 0.35 else (4 if t < 0.8 else 5)
            g._px(x, y, MARBLE[k])
    for i, jy in enumerate(ys_j + [top_y1]):
        if i == 0:
            continue
        prev = ys_j[i - 1]
        # vertical joints, staggered row to row
        off = 0 if i % 2 else 16
        for jx in range(x0 + 4 + off, x1 - 3, 32):
            for y in range(prev + 1, jy):
                g._px(jx, y, MARBLE[1]); g._px(jx + 1, y, MARBLE[5])
        if jy < top_y1:
            for x in range(x0 + 2, x1 - 1):
                g._px(x, jy, MARBLE[1]); g._px(x, jy + 1, MARBLE[5])
    # Veins and cracks.
    for _ in range(9):
        vx, vy = int(rng.integers(x0 + 6, x1 - 6)), int(rng.integers(y0 + 6, top_y1 - 6))
        for i in range(int(rng.integers(4, 9))):
            g._blend(vx + i, vy + int(round(np.sin(i * 0.9) * 1.2)), MARBLE[1], 0.45)
    for _ in range(3):
        cx, cy = int(rng.integers(x0 + 8, x1 - 8)), int(rng.integers(y0 + 30, top_y1 - 8))
        for i in range(int(rng.integers(4, 8))):
            g._px(cx + i // 2 * (1 if i % 3 else -1), cy + i, MARBLE[0])
    # Moss in a few joints near the edges, where nobody walks.
    for (mx, my) in ((x0 + 3, y0 + 30), (x1 - 4, y0 + 55), (x0 + 3, top_y1 - 20), (x1 - 4, top_y1 - 6)):
        for i in range(5):
            g._px(mx + (i % 2), my + i - 2, MOSS[i % 2])
    # ---- the mosaic in the middle: a ring of terracotta key pattern round a star ---------
    cx, cy, r = (x0 + x1) // 2, (y0 + top_y1) // 2 + 10, 15
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = np.hypot((x - cx) * 1.0, (y - cy) * 1.25)
            if d > r + 0.5:
                continue
            if d > r - 1.2:
                col = INK
            elif d > r - 4.5:
                a = np.degrees(np.arctan2(y - cy, x - cx)) % 30
                col = TERRACOTTA[1] if a < 15 else (MARBLE[5] if (a < 22) else TERRACOTTA[0])
            elif d > r - 5.7:
                col = INK
            else:
                ang = np.arctan2((y - cy) * 1.25, x - cx)
                star = 0.55 + 0.45 * np.cos(ang * 8)
                col = hexc("#d9a64a") if d < (r - 6) * star else hexc("#efe6d2")
                if d < 1.6:
                    col = TERRACOTTA[2]
            g._px(x, y, col)
    # ---- rim: a lit lip round the top, a dark line outside -------------------------------
    for x in range(x0, x1 + 1):
        g._px(x, y0, MARBLE[5]); g._px(x, y0 - 1, BLOCK[0])
    for y in range(y0, top_y1 + 1):
        g._px(x0, y, MARBLE[5]); g._px(x0 - 1, y, BLOCK[0])
        g._px(x1, y, MARBLE[2]); g._px(x1 + 1, y, BLOCK[1]); g._px(x1 + 2, y, BLOCK[0])   # right side face
    for x in range(x0, x1 + 1):
        g._px(x, top_y1, MARBLE[5])
    # ---- front face of squared blocks -------------------------------------------------------
    for y in range(top_y1 + 1, y1 + 1):
        for x in range(x0 - 1, x1 + 3):
            row = (y - top_y1 - 1) // 4
            off = 0 if row % 2 == 0 else 9
            joint = (x - x0 + off) % 18 == 0 or (y - top_y1 - 1) % 4 == 3
            k = 1 if joint else (3 if (y - top_y1) <= 1 else 2)
            if x >= x1 + 1:
                k = max(0, k - 1)
            g._px(x, y, BLOCK[k])
    for x in range(x0 - 1, x1 + 3):
        g._px(x, y1 + 1, BLOCK[0])
    # ---- two steps down to the path ------------------------------------------------------------
    for s in range(2):
        sy0 = y1 - 2 + s * 5
        sx0, sx1 = step_x0 - 4 * s, step_x1 + 4 * s
        for y in range(sy0, sy0 + 5):
            for x in range(sx0, sx1 + 1):
                if y == sy0:
                    col = MARBLE[5]
                elif y < sy0 + 2:
                    col = MARBLE[3]
                elif y < sy0 + 4:
                    col = BLOCK[2]
                else:
                    col = BLOCK[0]
                if x in (sx0, sx1) and y > sy0:
                    col = BLOCK[1]
                g._px(x, y, col)
    # Grass tufts at the foot of the face.
    for x in range(x0 + 2, x1, 7):
        if not (step_x0 - 10 < x < step_x1 + 10) and rng.random() < 0.7:
            g.tuft(x, y1 + 3, int(rng.integers(3, 5)))
    g.claim(x0 - 6, y0 - 6, x1 + 7, y1 + 12)


MUD = [hexc("#3a2a1c"), hexc("#4f3a26"), hexc("#634a31"), hexc("#7a5e40"), hexc("#9a7f5c")]


def paint_pen(g, mud, straw_box, seed: int) -> None:
    """Inside the pig pen: a wallow of wet mud (dark, with a lit far rim and a puddle), trampled
    grass round it, and loose straw."""
    rng = np.random.default_rng(seed)
    cx, cy, rx, ry = mud
    jit = paint.value_noise(2 * rx + 9, 2 * ry + 9, 5, seed)
    for y in range(cy - ry - 4, cy + ry + 5):
        for x in range(cx - rx - 4, cx + rx + 5):
            j = jit[y - cy + ry + 4, x - cx + rx + 4]
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 - (j - 0.5) * 0.6
            if d <= 1.0:
                k = 2 if d > 0.55 else 1
                if d < 0.25 and (x + y) % 3 == 0:
                    k = 0
                if (y < cy - ry * 0.3) and d > 0.6:
                    k = 3                                   # the lit far rim
                g._px(x, y, MUD[k])
            elif d <= 1.7:
                g._blend(x, y, MUD[3], 0.45)                # trampled, muddy grass
    for i in range(6):                                      # a puddle with sky in it
        g._px(cx - 3 + i, cy + 1, hexc("#6d8a8a") if i in (1, 2) else hexc("#4f6666"))
    g._px(cx - 1, cy, hexc("#9fb8b4"))
    x0, y0, x1, y1 = straw_box
    for _ in range(55):
        x, y = int(rng.integers(x0, x1)), int(rng.integers(y0, y1))
        c = hexc("#d9b85a") if rng.random() < 0.6 else hexc("#b8933e")
        g._px(x, y, c); g._px(x + 1, y + (1 if rng.random() < 0.5 else -1), c)
    g.claim(x0 - 4, y0 - 4, x1 + 4, y1 + 4)


def paint_bed(g, x0: int, y0: int, x1: int, y1: int, seed: int) -> None:
    """A garden bed: lumpy tilled earth in wavy furrows inside a low border of fieldstones."""
    rng = np.random.default_rng(seed)
    B = 5                                     # border width
    w, h = x1 - x0 + 1, y1 - y0 + 1
    lump = paint.value_noise(w, h, 4, seed + 1)
    patch = paint.value_noise(w, h, 14, seed + 2)
    # Earth: furrows run across the bed, gently wavy; each a lit ridge and a dark trough, with
    # lumps of soil breaking them up and damper, darker patches.
    # Mounded rows: each a rounded ridge of loose earth, lit along its top, with a dark trough
    # between ridges; the moly is planted along the middle ridge (garden.py BASE_Y).
    mid = (y0 + y1) // 2 + 4
    for y in range(y0 + B, y1 - B + 1):
        for x in range(x0 + B, x1 - B + 1):
            wave = np.sin(x / 9.0 + seed) * 0.9 + np.sin(x / 3.7) * 0.5
            v = ((y - mid + wave) / 14.0) % 1.0          # 0 at a ridge's crest
            k = 4.2 if v < 0.12 or v > 0.94 else (3.3 if v < 0.35 else (2.2 if v < 0.62 else (1.2 if v < 0.8 else 2.6)))
            k += (lump[y - y0, x - x0] - 0.5) * 1.5 + (patch[y - y0, x - x0] - 0.5) * 0.7
            g._px(x, y, SOIL[int(np.clip(round(k), 0, 5))])
    # Clods and a few pebbles.
    for _ in range(w * h // 55):
        cx, cy = int(rng.integers(x0 + B + 1, x1 - B - 1)), int(rng.integers(y0 + B + 1, y1 - B - 1))
        if rng.random() < 0.8:
            g._px(cx, cy, SOIL[5]); g._px(cx + 1, cy, SOIL[4]); g._px(cx, cy + 1, SOIL[2]); g._px(cx + 1, cy + 1, SOIL[1])
        else:
            g._px(cx, cy, FIELDSTONE[3]); g._px(cx + 1, cy, FIELDSTONE[2]); g._px(cx, cy + 1, FIELDSTONE[0])
    # Shadow of the border on the earth along the top and left inside edges; a sunlit lip of
    # earth along the bottom, where the soil slopes up to the front stones.
    for x in range(x0 + B, x1 - B + 1):
        g._darken(x, y0 + B, 0.62); g._darken(x, y0 + B + 1, 0.8)
        g._px(x, y1 - B, SOIL[5] if (x // 3) % 3 else SOIL[4])
    for y in range(y0 + B, y1 - B + 1):
        g._darken(x0 + B, y, 0.72)
    # The border: a ring of rounded fieldstones of different sizes and tones, each lit on top,
    # sunk in the grass, with a bit of moss here and there.
    def stone(sx, sy, sw, sh):
        k0 = int(rng.integers(-1, 2))
        for yy in range(sh):
            for xx in range(sw):
                if (xx in (0, sw - 1)) and (yy in (0, sh - 1)):
                    continue
                if yy == sh - 1 or xx == sw - 1:
                    k = 1
                elif yy == 0:
                    k = 4
                elif xx == 0:
                    k = 3
                else:
                    k = 2 if (xx * 3 + yy) % 5 else 3
                g._px(sx + xx, sy + yy, FIELDSTONE[int(np.clip(k + k0, 0, 4))])
        for xx in range(1, sw):
            g._darken(sx + xx, sy + sh, 0.6)
        if rng.random() < 0.2:
            g._px(sx + 1, sy + sh - 2, MOSS[1]); g._px(sx + 2, sy + sh - 2, MOSS[0])
    x = x0
    while x < x1 - 3:                                  # top and bottom rows
        sw = min(int(rng.integers(5, 12)), x1 - x + 1)
        stone(x, y0 + int(rng.integers(0, 2)), sw, B)
        stone(x, y1 - B + 1 - int(rng.integers(0, 2)), sw, B)
        x += sw
    y = y0 + B
    while y < y1 - B - 2:                              # sides
        sh = min(int(rng.integers(5, 9)), y1 - B - y + 1)
        stone(x0 + int(rng.integers(0, 2)), y, B, sh); stone(x1 - B + 1 - int(rng.integers(0, 2)), y, B, sh)
        y += sh
    g.claim(x0 - 3, y0 - 3, x1 + 4, y1 + 6)
