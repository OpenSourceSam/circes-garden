"""Circe's house, drawn in code: a whitewashed island cottage in three-quarter view.

160 x 192 px (5 x 6 tiles), placed by worldmap.py as the prop "house". From the top: a ridge of
capping tiles and a stone chimney, a terracotta roof of barrel tiles with lime-mortar verges and
open tile ends along the eave, the eave's shadow on a lime-washed wall, an arched blue door with a
stone step, two shuttered windows with flower boxes, bundles of herbs drying under the eave, a
bougainvillea climbing the right-hand corner, pots by the door and a stone plinth. Light comes
from the upper left, as on the rest of the island.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

import paint
from paint import hexc

W, H = 160, 192
DOOR_X = 80            # centre of the door in the picture (the sleep spot stands in front of it)

ROOF = [hexc("#45201a"), hexc("#622e20"), hexc("#7f3b27"), hexc("#9b4a2f"), hexc("#b35c39"), hexc("#c87449"), hexc("#da9362")]
MORTAR = [hexc("#9e9583"), hexc("#c9c0ac"), hexc("#e6dfcf")]
PLASTER = [hexc("#a99d86"), hexc("#c6bba4"), hexc("#ddd3be"), hexc("#ebe4d3"), hexc("#f5f0e4")]
STONE = [hexc("#5d564c"), hexc("#7d7466"), hexc("#9c9282"), hexc("#b6ad9b"), hexc("#cdc5b3")]
BLUE = [hexc("#1f3346"), hexc("#2c4862"), hexc("#3a5f80"), hexc("#4b779b"), hexc("#6a95b6")]
GLASS = [hexc("#18202b"), hexc("#26323f"), hexc("#3c4d60"), hexc("#6f8599")]
POT = [hexc("#5e2a1a"), hexc("#7f3b23"), hexc("#a2512f"), hexc("#c06c42"), hexc("#d98d5e")]
LEAF = [hexc("#26341a"), hexc("#3b4d22"), hexc("#53682d"), hexc("#6e843a"), hexc("#8ea04c")]
MAGENTA = [hexc("#7d1d4b"), hexc("#a82a63"), hexc("#cf3f7f"), hexc("#e76aa0"), hexc("#f59cc3")]
RED = [hexc("#8c2420"), hexc("#bf3a2f"), hexc("#e2584a"), hexc("#f48a73")]
WOOD = [hexc("#3a2617"), hexc("#553821"), hexc("#73502f"), hexc("#94693f")]
OUTLINE = hexc("#2b1d17")


class Canvas:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)

    def px(self, x: int, y: int, c) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def get(self, x: int, y: int):
        return self.a[y, x]

    def mul(self, x: int, y: int, f: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3]:
            self.a[y, x, :3] = np.clip(self.a[y, x, :3] * f, 0, 255).astype(np.uint8)

    def rect(self, x0: int, y0: int, x1: int, y1: int, c) -> None:
        """Inclusive rectangle."""
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = c

    def mask_poly(self, pts) -> np.ndarray:
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon(pts, fill=255)
        return np.asarray(im) > 0

    def outline_mask(self, m: np.ndarray, c, sides=("l", "r", "t", "b")) -> None:
        """Draw `c` on pixels just outside mask m."""
        out = np.zeros_like(m)
        if "l" in sides:
            out[:, :-1] |= m[:, 1:] & ~m[:, :-1]
        if "r" in sides:
            out[:, 1:] |= m[:, :-1] & ~m[:, 1:]
        if "t" in sides:
            out[:-1, :] |= m[1:, :] & ~m[:-1, :]
        if "b" in sides:
            out[1:, :] |= m[:-1, :] & ~m[1:, :]
        self.a[out] = c


def _ramp(ramp, i):
    return ramp[int(np.clip(i, 0, len(ramp) - 1))]


# ---- roof ---------------------------------------------------------------------------------
ROOF_TOP, ROOF_EAVE = 14, 100        # top of the tiled slope, bottom of the eave tiles
WALL_L, WALL_R = 10, 149             # the wall's outer columns
COLS = 15                            # barrel tiles across the roof


def roof_edges(y: float) -> tuple[float, float]:
    """Left and right edge of the roof slope at row y: narrower at the ridge (perspective)."""
    t = (y - ROOF_TOP) / (ROOF_EAVE - ROOF_TOP)
    return 13 - 10 * t, 146 + 10 * t


def draw_roof(cv: Canvas) -> None:
    """Barrel tiles: rounded caps (lit on the left, turning into shade on the right) laid over
    darker channel tiles, in courses that each overlap the one below with a small lip and shadow."""
    rng = np.random.default_rng(41)
    tile_shift = rng.normal(0, 0.18, size=(20, COLS + 2))
    for y in range(ROOF_TOP, ROOF_EAVE + 1):
        xl, xr = roof_edges(y)
        course = (y - ROOF_TOP) / 9.0
        v = course - np.floor(course)                             # 0 at a course's top
        ci = int(np.floor(course))
        slope_t = (y - ROOF_TOP) / (ROOF_EAVE - ROOF_TOP)
        for x in range(int(np.floor(xl)), int(np.ceil(xr)) + 1):
            u = (x - xl) / (xr - xl) * COLS
            col = int(np.floor(u))
            f = u - col
            cap = f >= 0.36
            if not cap:                                           # the channel between caps
                k = 1.7 + (0.5 if f > 0.22 else 0.0)
                if v > 0.88:
                    k -= 0.6
            else:
                g = (f - 0.36) / 0.64                             # across the cap, 0 = left
                k = 4.6 if g < 0.3 else (3.7 if g < 0.62 else (2.8 if g < 0.88 else 2.1))
                if v > 0.86:
                    k -= 1.7                                      # shadow cast by the cap above
                elif v > 0.74:
                    k += 0.9                                      # the lower lip of the cap
                k += tile_shift[min(ci, 19), min(col, COLS + 1)]
            k += 0.45 * (1 - slope_t)                             # brighter up the slope
            k += (0.5 - u / COLS) * 0.6                           # light from the upper left
            cv.px(x, y, _ramp(ROOF, round(k)))
    # Lime-mortar verges down both ends of the roof, a dark line outside them.
    for y in range(ROOF_TOP - 2, ROOF_EAVE + 2):
        xl, xr = roof_edges(min(max(y, ROOF_TOP), ROOF_EAVE))
        l, r = int(round(xl)), int(round(xr))
        cv.px(l - 1, y, OUTLINE); cv.px(l, y, MORTAR[2]); cv.px(l + 1, y, MORTAR[1])
        cv.px(r + 1, y, OUTLINE); cv.px(r, y, MORTAR[1]); cv.px(r - 1, y, MORTAR[0])
    # Eave: open ends of the barrel tiles, each a dark mouth under a lit rim.
    y0 = ROOF_EAVE - 3
    xl, xr = roof_edges(ROOF_EAVE)
    for col in range(COLS):
        x0 = xl + (xr - xl) * col / COLS
        x1 = xl + (xr - xl) * (col + 1) / COLS
        cx = (x0 + x1) / 2 + 0.5
        for x in range(int(x0) + 1, int(x1) + 1):
            dx = abs(x - cx)
            cv.px(x, y0 + 4, _ramp(ROOF, 2 if dx < 3 else 1))
            cv.px(x, y0 + 5, ROOF[0] if dx < 4 else OUTLINE)
            if dx < 2.2:
                cv.px(x, y0 + 2, ROOF[0]); cv.px(x, y0 + 3, OUTLINE)    # the hollow of the tile
            elif dx < 3.4:
                cv.px(x, y0 + 2, ROOF[5] if x < cx else ROOF[3])
        cv.px(int(x0), y0 + 5, OUTLINE)
    # Ridge: rounded capping tiles set in mortar along the top.
    for x in range(14, 146):
        seg = (x - 14) / 10.5
        f = seg - np.floor(seg)
        for y in range(5, ROOF_TOP + 1):
            t = (y - 5) / (ROOF_TOP - 5)
            if f < 0.08:
                c = MORTAR[1] if y < ROOF_TOP - 1 else MORTAR[0]
            elif t < 0.2:
                c = ROOF[5] if f < 0.6 else ROOF[4]
            elif t < 0.55:
                c = ROOF[4] if f < 0.5 else ROOF[3]
            elif t < 0.85:
                c = ROOF[3] if f < 0.4 else ROOF[2]
            else:
                c = ROOF[1]
            cv.px(x, y, c)
        cv.px(x, 4, OUTLINE)
        cv.px(x, ROOF_TOP + 1, ROOF[0])
    for y in range(5, ROOF_TOP + 1):
        cv.px(13, y, OUTLINE); cv.px(146, y, OUTLINE)


def draw_chimney(cv: Canvas) -> None:
    x0, x1, y0, y1 = 110, 124, 0, 30
    for y in range(y0 + 4, y1 + 1):
        for x in range(x0, x1 + 1):
            if x == x0:
                c = PLASTER[4]
            elif x >= x1 - 3:
                c = PLASTER[1] if x < x1 else PLASTER[0]
            else:
                c = PLASTER[3] if (x * 7 + y * 3) % 11 else PLASTER[2]
            cv.px(x, y, c)
    for x in range(x0 - 1, x1 + 2):                                  # the cap, a stone slab
        cv.px(x, y0 + 2, STONE[3] if x < x1 - 2 else STONE[2])
        cv.px(x, y0 + 3, STONE[2] if x < x1 - 2 else STONE[1])
        cv.px(x, y0 + 4, STONE[0])
        cv.px(x, y0 + 1, OUTLINE)
    for x in range(x0 + 3, x1 - 2):                                  # the flue, black with soot
        cv.px(x, y0 + 2, hexc("#1b1512"))
    cv.px(x0 - 2, y0 + 2, OUTLINE); cv.px(x0 - 2, y0 + 3, OUTLINE)
    cv.px(x1 + 2, y0 + 2, OUTLINE); cv.px(x1 + 2, y0 + 3, OUTLINE)
    for y in range(y0 + 5, y1 + 1):
        cv.px(x0 - 1, y, OUTLINE); cv.px(x1 + 1, y, OUTLINE)
    for x in range(x0 - 1, x1 + 3):                                  # its shadow on the tiles
        for y in range(y1 + 1, y1 + 4):
            cv.mul(x + (y - y1), y, 0.7)


# ---- wall ---------------------------------------------------------------------------------
WALL_TOP, WALL_BOT = ROOF_EAVE + 3, 180


def draw_wall(cv: Canvas) -> None:
    tex = paint.value_noise(W, H, 6, 3)
    big = paint.value_noise(W, H, 26, 9)
    for y in range(WALL_TOP, WALL_BOT + 1):
        for x in range(WALL_L, WALL_R + 1):
            k = 3.0 + (tex[y, x] - 0.5) * 1.3 + (big[y, x] - 0.5) * 0.8
            if x <= WALL_L + 1:
                k += 1.0                                         # the lit corner
            if x >= WALL_R - 2:
                k -= 1.4                                         # the corner turning away
            cv.px(x, y, _ramp(PLASTER, round(k)))
    # Where the lime wash has worn: rough stones show through in two patches.
    for (cx, cy, rx, ry) in ((20, 166, 7, 5), (139, 118, 6, 4), (101, 128, 4, 3)):
        stones = np.random.default_rng(cx * 7 + cy)
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1 and stones.random() < (1.2 - d):
                    edge = d > 0.6
                    cv.px(x, y, STONE[2] if not edge else PLASTER[1])
        for _ in range(rx * ry // 3):                            # mortar joints between the stones
            x = cx + int(stones.integers(-rx + 1, rx))
            y = cy + int(stones.integers(-ry + 1, ry))
            cv.px(x, y, STONE[1]); cv.px(x + 1, y, STONE[3])
    # Hairline cracks in the wash.
    for (x, y, n) in ((44, 112, 7), (126, 160, 6)):
        for i in range(n):
            cv.mul(x + (i // 2) * (1 if i % 3 else -1), y + i, 0.82)
    # The eave's shadow on the wall: deep under the tile ends, scalloped like them.
    xl, xr = roof_edges(ROOF_EAVE)
    for x in range(WALL_L, WALL_R + 1):
        u = (x - xl) / (xr - xl) * COLS
        f = u - np.floor(u)
        depth = 7 if 0.2 < f < 0.8 else 5
        for y in range(WALL_TOP, WALL_TOP + depth):
            cv.mul(x, y, 0.58 if y < WALL_TOP + depth - 2 else 0.76)
    for y in range(WALL_TOP, WALL_BOT + 1):
        cv.px(WALL_L - 1, y, OUTLINE); cv.px(WALL_R + 1, y, OUTLINE)


def draw_plinth(cv: Canvas) -> None:
    rng = np.random.default_rng(17)
    y0, y1 = WALL_BOT + 1, WALL_BOT + 8
    x = WALL_L - 2
    while x < WALL_R + 2:
        w = int(rng.integers(7, 14))
        k = int(rng.integers(2, 4))
        for yy in range(y0, y1 + 1):
            for xx in range(x, min(x + w, WALL_R + 3)):
                if xx == x or yy == y1:
                    c = STONE[0]
                elif yy == y0:
                    c = STONE[min(4, k + 1)]
                elif xx == x + w - 1:
                    c = STONE[k - 1]
                else:
                    c = STONE[k]
                cv.px(xx, yy, c)
        x += w
    for xx in range(WALL_L - 3, WALL_R + 4):
        cv.px(xx, y0 - 1, STONE[1])
        cv.px(xx, y1 + 1, OUTLINE)
    for yy in range(y0 - 1, y1 + 2):
        cv.px(WALL_L - 3, yy, OUTLINE); cv.px(WALL_R + 3, yy, OUTLINE)
    # Soft shadow on the ground in front of the house.
    for yy in range(y1 + 2, H):
        a = int(90 * (1 - (yy - y1 - 2) / max(1, H - y1 - 2)))
        for xx in range(WALL_L - 4, WALL_R + 5):
            if cv.a[yy, xx, 3] == 0:
                cv.a[yy, xx] = (20, 24, 10, a)


# ---- door and windows ---------------------------------------------------------------------
def draw_door(cv: Canvas) -> None:
    x0, x1 = DOOR_X - 12, DOOR_X + 11
    y_spring, y_bot = 152, WALL_BOT
    cx, r = (x0 + x1) / 2, 12.0
    m = np.zeros((H, W), dtype=bool)
    for y in range(y_spring - 13, y_bot + 1):
        for x in range(x0, x1 + 1):
            if y >= y_spring or (x - cx) ** 2 + (y - y_spring) ** 2 <= r * r:
                m[y, x] = True
    # The stone surround of the arch, 3 px wide, lit on the left.
    frame = np.zeros_like(m)
    for y in range(y_spring - 17, y_bot + 1):
        for x in range(x0 - 4, x1 + 5):
            if m[y, x] if (0 <= y < H and 0 <= x < W) else False:
                continue
            if y >= y_spring and x0 - 4 <= x <= x1 + 4:
                frame[y, x] = True
            elif (x - cx) ** 2 + (y - y_spring) ** 2 <= (r + 4) ** 2:
                frame[y, x] = True
    ys, xs = np.nonzero(frame)
    for y, x in zip(ys, xs):
        c = STONE[4] if x < cx - 6 else (STONE[3] if x < cx + 6 else STONE[2])
        if y < y_spring - 8 and abs(x - cx) < 2:
            c = STONE[4]                                          # keystone
        cv.px(x, y, c)
    cv.outline_mask(frame | m, OUTLINE, ("l", "r", "t"))
    # Planks: vertical boards, each lit on its left edge, darker towards the top under the arch.
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        board = (x - x0) // 4
        f = (x - x0) % 4
        k = 3 if f == 1 else (2 if f in (2,) else (1 if f == 3 else 2))
        if f == 0:
            k = 0
        if y < y_spring - 4:
            k -= 1
        if board == 0 and f == 1:
            k += 1
        cv.px(x, y, _ramp(BLUE, k))
    for x in range(x0, x1 + 1):                                  # two iron straps
        for y in (y_spring + 3, y_bot - 7):
            cv.px(x, y, hexc("#2a2a2e")); cv.px(x, y + 1, BLUE[0])
    for (x, y) in ((x0 + 2, y_spring + 3), (x1 - 2, y_spring + 3), (x0 + 2, y_bot - 7), (x1 - 2, y_bot - 7)):
        cv.px(x, y, hexc("#8a8a90"))
    # A brass ring handle.
    hx, hy = x1 - 5, y_spring + 13
    for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1)):
        cv.px(hx + dx, hy + dy, hexc("#c99a3c") if dy < 1 else hexc("#8a6424"))
    cv.px(hx, hy - 2, hexc("#e6c262"))
    # The step: a worn threshold stone wider than the door.
    for y in range(y_bot + 1, y_bot + 6):
        for x in range(x0 - 6, x1 + 7):
            c = STONE[4] if y == y_bot + 1 else (STONE[3] if y < y_bot + 4 else STONE[1])
            if x in (x0 - 6, x1 + 6):
                c = OUTLINE
            cv.px(x, y, c)
    for x in range(x0 - 6, x1 + 7):
        cv.px(x, y_bot + 6, OUTLINE)


def draw_window(cv: Canvas, x0: int, y0: int, seed: int) -> None:
    w, h = 22, 25
    x1, y1 = x0 + w - 1, y0 + h - 1
    # Shutters, folded open against the wall either side.
    for sx in (x0 - 10, x1 + 2):
        for y in range(y0 - 1, y1 + 2):
            for x in range(sx, sx + 9):
                edge = x in (sx, sx + 8) or y in (y0 - 1, y1 + 1)
                slat = (y - y0) % 3
                c = BLUE[0] if edge else (BLUE[3] if slat == 0 else (BLUE[2] if slat == 1 else BLUE[1]))
                if not edge and x == sx + 1:
                    c = BLUE[4] if slat == 0 else BLUE[3]
                cv.px(x, y, c)
        for y in (y0 + 3, y1 - 3):                                # hinges
            hx = sx + 8 if sx < x0 else sx
            cv.px(hx, y, hexc("#1a1a1e"))
        for y in range(y0, y1 + 3):                              # shadow of the shutter on the wall
            cv.mul(sx + 9, y + 1, 0.78)
    # Frame of lime-washed stone, a deep reveal and the glass.
    for y in range(y0 - 2, y1 + 1):
        for x in range(x0 - 1, x1 + 2):
            cv.px(x, y, PLASTER[4] if x < x0 + 2 or y < y0 else PLASTER[3])
    for y in range(y0 + 1, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            cv.px(x, y, GLASS[1])
    for x in range(x0 + 2, x1 - 1):                              # the reveal's shadow at the top
        cv.px(x, y0 + 1, GLASS[0]); cv.px(x, y0 + 2, GLASS[0])
    for y in range(y0 + 1, y1 - 1):
        cv.px(x0 + 2, y, GLASS[0])
    # A warm glow low in the room and the sky's reflection high on the panes.
    for y in range(y1 - 8, y1 - 1):
        for x in range(x0 + 3, x1 - 1):
            if (x + y) % 2 == 0:
                cv.px(x, y, hexc("#4a3a2a"))
    for i in range(5):
        cv.px(x0 + 4 + i, y0 + 4 + i // 2, GLASS[3] if i < 2 else GLASS[2])
    cv.px(x0 + w - 7, y0 + 5, GLASS[3])
    mx, my = x0 + w // 2, y0 + h // 2 - 1                       # cross bars
    for y in range(y0 + 1, y1 - 1):
        cv.px(mx, y, WOOD[1])
    for x in range(x0 + 2, x1 - 1):
        cv.px(x, my, WOOD[1])
    for y in range(y0 - 3, y1 + 1):
        cv.px(x0 - 2, y, OUTLINE); cv.px(x1 + 2, y, OUTLINE)
    for x in range(x0 - 2, x1 + 3):
        cv.px(x, y0 - 3, OUTLINE)
    # Sill and flower box.
    for x in range(x0 - 3, x1 + 4):
        cv.px(x, y1 + 1, PLASTER[4]); cv.px(x, y1 + 2, PLASTER[2]); cv.px(x, y1 + 3, OUTLINE)
    bx0, bx1, by0, by1 = x0 - 1, x1 + 1, y1 + 4, y1 + 9
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            c = POT[3] if y == by0 else (POT[2] if x < bx1 - 2 else POT[1])
            if x in (bx0, bx1) or y == by1:
                c = POT[0]
            cv.px(x, y, c)
    for x in range(bx0, bx1 + 1):
        cv.mul(x, by1 + 1, 0.7); cv.mul(x, by1 + 2, 0.85)
    rng = np.random.default_rng(seed)
    for x in range(bx0 + 1, bx1):                                # leaves spilling over the box
        top = by0 - 2 - int(rng.integers(0, 4))
        for y in range(top, by0 + 1 + (1 if rng.random() < 0.3 else 0)):
            cv.px(x, y, LEAF[1 + int(rng.integers(0, 3))] if y > top else LEAF[3])
    for i in range(7):                                            # geraniums
        fx = bx0 + 2 + int(i * (bx1 - bx0 - 4) / 6) + int(rng.integers(-1, 2))
        fy = by0 - 3 - int(rng.integers(0, 3))
        for (dx, dy, k) in ((0, 0, 2), (-1, 0, 1), (1, 0, 2), (0, -1, 3), (0, 1, 1), (1, -1, 2)):
            cv.px(fx + dx, fy + dy, RED[k])


def draw_herbs(cv: Canvas) -> None:
    """Bundles of herbs hung under the eave to dry, tied with string."""
    y_top = WALL_TOP + 1
    for i, (x, length, kind) in enumerate(((54, 9, "sage"), (59, 11, "lav"), (95, 10, "sage"), (100, 8, "rose"))):
        for y in range(y_top, y_top + 3):
            cv.px(x, y, hexc("#d8c9a4"))
        for y in range(y_top + 3, y_top + 3 + length):
            t = (y - y_top - 3) / length
            half = 1 if t < 0.25 else 2
            for dx in range(-half, half + 1):
                if kind == "lav" and t > 0.55:
                    c = hexc("#8f76c4") if (dx + y) % 2 else hexc("#6a55a0")
                elif kind == "rose" and t > 0.6:
                    c = hexc("#c04a5a") if (dx + y) % 2 else hexc("#8f3040")
                else:
                    c = LEAF[2] if dx < 0 else (LEAF[3] if dx == 0 else LEAF[1])
                    if kind == "sage":
                        c = hexc("#8a9a78") if dx < 1 else hexc("#66765a")
                cv.px(x + dx, y, c)
        cv.px(x - 1, y_top + 3, hexc("#a8946c")); cv.px(x + 1, y_top + 3, hexc("#a8946c"))


def draw_bougainvillea(cv: Canvas) -> None:
    """A bougainvillea on the right-hand corner: a twisting stem from the ground, leaves, and
    magenta bracts spilling over the eave."""
    rng = np.random.default_rng(5)
    # The stem.
    x = 152.0
    for y in range(WALL_BOT + 4, ROOF_EAVE - 2, -1):
        x += float(rng.normal(0, 0.45))
        x = min(156, max(147, x))
        cv.px(int(x), y, WOOD[1]); cv.px(int(x) + 1, y, WOOD[0])
    # Foliage blobs along the corner and over the eave.
    blobs = [(150, 166, 6, 7), (147, 150, 7, 7), (151, 134, 7, 7), (146, 118, 8, 6), (150, 104, 9, 6),
             (138, 100, 8, 5), (126, 99, 6, 4)]
    for (bx, by, rx, ry) in blobs:
        for y in range(by - ry, by + ry + 1):
            for x in range(bx - rx, bx + rx + 1):
                if not (0 <= x < W):
                    continue
                d = ((x - bx) / rx) ** 2 + ((y - by) / ry) ** 2
                if d > 1 or rng.random() > 1.25 - d:
                    continue
                n = rng.random()
                if n < 0.42:
                    k = 3 if (y < by - ry / 3 and x < bx) else (1 if y > by + ry / 3 else 2)
                    c = MAGENTA[k + (1 if rng.random() < 0.25 else 0)]
                else:
                    k = 2 if y < by else 1
                    c = LEAF[k + (1 if rng.random() < 0.2 else 0)]
                cv.px(x, y, c)
    # A few bracts fallen at the foot of the wall.
    for (fx, fy) in ((141, 186), (145, 188), (136, 189)):
        cv.px(fx, fy, MAGENTA[2]); cv.px(fx + 1, fy, MAGENTA[1])


def draw_pot(cv: Canvas, cx: int, by: int, plant: str) -> None:
    """A terracotta pot whose foot stands on row `by`, with a plant."""
    rows = [(5, 0), (5, 1), (4, 1), (4, 2), (4, 2), (3, 2), (3, 2), (3, 3)]
    top = by - len(rows) + 1
    for i, (half, _) in enumerate(rows):
        y = top + i
        for x in range(cx - half, cx + half + 1):
            c = POT[3] if x < cx - 1 else (POT[2] if x < cx + half - 1 else POT[1])
            if i == 0:
                c = POT[4] if x < cx + 2 else POT[3]
            if i == 1:
                c = POT[1]
            cv.px(x, y, c)
        cv.px(cx - half - 1, y, OUTLINE); cv.px(cx + half + 1, y, OUTLINE)
    for x in range(cx - 3, cx + 4):
        cv.px(x, by + 1, OUTLINE)
    rng = np.random.default_rng(cx)
    if plant == "rosemary":
        for i in range(9):
            x = cx - 4 + i
            tall = 5 + int(rng.integers(0, 4)) - abs(x - cx) // 2
            for y in range(top - tall, top):
                cv.px(x, y, hexc("#7e9070") if (y + i) % 3 else hexc("#5a6b50"))
            cv.px(x, top - tall - 1, hexc("#a9b6cf") if i % 3 == 0 else hexc("#7e9070"))
    else:                                                         # a round basil bush
        for y in range(top - 8, top + 1):
            for x in range(cx - 6, cx + 7):
                d = ((x - cx) / 6.2) ** 2 + ((y - (top - 4)) / 4.6) ** 2
                if d <= 1:
                    k = 4 if (y < top - 5 and x < cx) else (3 if y < top - 2 else 2)
                    if rng.random() < 0.25:
                        k -= 1
                    cv.px(x, y, LEAF[k])
        cv.outline_mask(np.all(cv.a[..., :3] == np.array(LEAF[0][:3]), axis=-1) & False, OUTLINE)


def house() -> Image.Image:
    cv = Canvas(W, H)
    draw_wall(cv)
    draw_plinth(cv)
    draw_roof(cv)
    draw_chimney(cv)
    draw_window(cv, 24, 125, 3)
    draw_window(cv, 114, 125, 8)
    draw_door(cv)
    draw_herbs(cv)
    draw_pot(cv, 59, WALL_BOT + 4, "rosemary")
    draw_pot(cv, 101, WALL_BOT + 4, "basil")
    draw_bougainvillea(cv)
    return Image.fromarray(cv.a, "RGBA")


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).parent / "preview"
    out.mkdir(exist_ok=True)
    im = house()
    bg = Image.new("RGBA", im.size, (110, 122, 56, 255))
    bg.alpha_composite(im)
    bg.resize((W * 4, H * 4), Image.NEAREST).save(out / "house_x4.png")
    print("wrote", out / "house_x4.png")
