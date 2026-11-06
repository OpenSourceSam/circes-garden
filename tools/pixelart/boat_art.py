"""Circe's boat, drawn in code: a small ancient Greek sailing boat seen from the side and above.

176 x 104 px, bow to the right. A dark tarred hull with an ochre band along the gunwale and a
painted eye on the bow, a stern post that curls back over like a swan's neck, a steering oar
over the stern quarter, the inside of the boat with its benches, an oar, a coil of rope and two
amphorae, a mast with a square linen sail on its yard (two purple bands, Circe's colour), stays
to the bow and stern, a pennant, and the hull's shadow and ripples on the water.

The same picture is used at both piers (boat.gd); boat.gd bobs it on the swell.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from paint import hexc

W, H = 176, 104
WATERLINE = 88

TAR = [hexc("#1c1512"), hexc("#2a201a"), hexc("#382b22"), hexc("#47372b"), hexc("#5a4636")]
OCHRE = [hexc("#7a2f20"), hexc("#a3442c"), hexc("#c45c3a"), hexc("#d97a50")]
DECK = [hexc("#4e3622"), hexc("#6b4b2f"), hexc("#86603c"), hexc("#a07649"), hexc("#b88c58")]
LINEN = [hexc("#a8957a"), hexc("#c4b291"), hexc("#dccdab"), hexc("#ebe0c3"), hexc("#f6eedb")]
PURPLE = [hexc("#3c1c5c"), hexc("#55297e"), hexc("#6d3a9c"), hexc("#8a55b8")]
ROPE = hexc("#3b2e22")
ROPE_LIGHT = hexc("#c9b27a")
OUTLINE = hexc("#140f0c")


class C:
    def __init__(self):
        self.a = np.zeros((H, W, 4), dtype=np.uint8)

    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            self.a[y, x] = c

    def line(self, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            self.px(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)


def _t(x: float) -> float:
    return (x - 90) / 76


def sheer(x: float) -> float:
    """Top of the near side of the hull: low amidships, sweeping up to the stern and the bow."""
    t = _t(x)
    return 68 - 16 * max(0, -t) ** 2.0 - 12 * max(0, t) ** 2.2


def waterline(x: float) -> float:
    """The hull's lower edge where it meets the water: a crescent, rising to meet the sheer at
    both ends, so the boat has a pointed bow and stern instead of square ends."""
    t = _t(x)
    end = sheer(x) + 6
    return WATERLINE - 2 - (WATERLINE - 2 - end) * abs(t) ** 2.6


def far_rail(x: float) -> float:
    """The far gunwale, seen over the near one: the boat's width, foreshortened."""
    t = _t(x)
    return sheer(x) - 14 * max(0, 1 - t * t) ** 0.8


X0, X1 = 14, 165            # stern and bow ends of the hull


def boat() -> Image.Image:
    c = C()
    # ---- shadow and ripples on the water (semi-transparent, so they work on both seas) ----
    for x in range(X0 - 4, X1 + 8):
        wl = waterline(min(max(x, X0), X1))
        for y in range(int(wl), int(wl) + 6):
            a = 120 - (y - int(wl)) * 18
            if 0 <= y < H:
                c.a[y, x] = (8, 22, 30, max(0, a))
    rng = np.random.default_rng(9)
    for x in range(X0 - 2, X1 + 10, 1):
        if rng.random() < 0.35:
            wl = waterline(min(max(x, X0), X1))
            yy = int(wl) + int(rng.integers(1, 5))
            c.px(x, yy, (226, 238, 228, 200))
    bw = waterline(X1 - 6)
    for i in range(7):                                     # the bow wave, folding back along the hull
        c.px(X1 - 8 - i * 2, bw + 2 + i // 3, (232, 242, 232, 220))
        c.px(X1 - 7 - i * 2, bw + 3 + i // 3, (200, 222, 214, 150))

    # ---- steering oar over the stern quarter, its blade under water ----------------------
    c.line(32, 58, 12, 90, DECK[3]); c.line(33, 58, 13, 90, DECK[1]); c.line(31, 58, 11, 90, OUTLINE)
    for i in range(7):                                     # its blade, dim under the water
        c.line(9 + i * 0.5, 86 + i, 15 + i * 0.5, 87 + i, (70, 60, 44, 120))

    # ---- inside of the hull: floor boards, benches, cargo -----------------------------------
    for x in range(X0 + 3, X1 - 2):
        top, bot = far_rail(x), sheer(x)
        for y in range(int(np.ceil(top)) + 2, int(bot)):
            k = 2 if (y - int(top)) % 4 else 1
            if x % 23 == 0:
                k = 1
            c.px(x, y, DECK[k + (1 if y < top + 5 else 0)])
    for bx in (48, 72, 116, 138):                          # benches across the boat
        top, bot = far_rail(bx), sheer(bx)
        for y in range(int(top) + 2, int(bot)):
            c.px(bx, y, DECK[4]); c.px(bx + 1, y, DECK[3]); c.px(bx + 2, y, DECK[1])
            c.px(bx + 3, y, DECK[0])
    # An oar laid along the boat.
    c.line(44, sheer(44) - 6, 132, sheer(132) - 7, DECK[4])
    c.line(44, sheer(44) - 5, 132, sheer(132) - 6, DECK[2])
    for i in range(5):
        c.px(130 + i, sheer(132) - 8, DECK[4]); c.px(130 + i, sheer(132) - 5, DECK[1])
    # Two amphorae and a coil of rope in the bow.
    for (ax, lean) in ((124, 0), (131, 1)):
        ay = sheer(ax) - 3
        for dy in range(-9, 1):
            half = [1, 1, 2, 3, 3, 4, 4, 3, 3, 2][dy + 9]
            for dx in range(-half, half + 1):
                col = hexc("#b9673f") if dx < 0 else (hexc("#9a5233") if dx < half - 1 else hexc("#6f3a22"))
                c.px(ax + dx + (lean if dy < -5 else 0), ay + dy, col)
        c.px(ax - 1, ay - 9, hexc("#d98a5c"))
    cx, cy = 60, sheer(60) - 8
    for a in range(0, 360, 15):
        for rr in (2, 4):
            c.px(cx + np.cos(np.radians(a)) * rr, cy + np.sin(np.radians(a)) * rr * 0.6,
                 ROPE_LIGHT if a < 200 else hexc("#8f7a4c"))
    # The far gunwale rail.
    for x in range(X0 + 2, X1 - 1):
        y = far_rail(x)
        c.px(x, y, DECK[4]); c.px(x, y + 1, DECK[2]); c.px(x, y - 1, OUTLINE)

    # ---- the near side of the hull ---------------------------------------------------------
    for x in range(X0, X1 + 1):
        top, bot = sheer(x), waterline(x)
        for y in range(int(top), int(bot) + 1):
            d = y - top
            if d < 2:
                col = DECK[4] if d < 1 else DECK[3]            # the gunwale rail, lit
            elif d < 5:
                col = OCHRE[2] if d < 4 else OCHRE[1]          # painted band
            else:
                f = (y - top - 5) / max(1.0, bot - top - 5)
                strake = int(f * 4)
                seam = abs(f * 4 - round(f * 4)) < 0.12 and 0 < round(f * 4) < 4
                col = TAR[0] if seam else TAR[[4, 3, 2, 1][min(3, strake)]]
                if abs(_t(x)) > 0.85:
                    col = TAR[max(0, [3, 2, 1, 1][min(3, strake)] - (0 if seam else 0))]
            c.px(x, y, col)
        c.px(x, int(top) - 1, OUTLINE)
        c.px(x, int(bot) + 1, OUTLINE)
    # Light glancing off the hull's curve near the waterline, a row of tholes on the rail.
    for x in range(X0 + 24, X1 - 22):
        c.px(x, sheer(x) + 7, TAR[4] if x % 3 else TAR[3])
    for tx in (40, 64, 88, 112, 136):
        c.px(tx, sheer(tx) - 1, DECK[4]); c.px(tx, sheer(tx) - 2, DECK[2])
    # The eye on the bow.
    ex, ey = 150, sheer(150) + 8
    for (dx, dy, col) in ((-3, 0, OCHRE[0]), (-2, -1, OCHRE[0]), (-1, -1, LINEN[4]), (0, -1, LINEN[4]),
                          (1, -1, LINEN[4]), (2, -1, OCHRE[0]), (3, 0, OCHRE[0]), (-2, 0, LINEN[4]),
                          (-1, 0, hexc("#101418")), (0, 0, hexc("#101418")), (1, 0, LINEN[3]),
                          (2, 0, LINEN[3]), (-2, 1, OCHRE[0]), (-1, 1, LINEN[3]), (0, 1, LINEN[3]),
                          (1, 1, LINEN[3]), (2, 1, OCHRE[0])):
        c.px(ex + dx, ey + dy, col)
    c.px(ex - 1, ey - 2, OCHRE[1]); c.px(ex, ey - 2, OCHRE[1]); c.px(ex + 1, ey - 2, OCHRE[1])

    # ---- stern post curling back like a swan's neck; the bow's stem and cutwater ----------
    pts = [(X0 + 2, sheer(X0 + 2)), (X0 - 1, 46), (X0 - 1, 39), (X0 + 2, 33), (X0 + 7, 31), (X0 + 11, 33),
           (X0 + 12, 37), (X0 + 10, 39)]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        c.line(xa, ya, xb, yb, TAR[3]); c.line(xa + 1, ya, xb + 1, yb, TAR[2])
        c.line(xa - 1, ya, xb - 1, yb, OUTLINE)
    c.px(X0 + 9, 41, OCHRE[2]); c.px(X0 + 8, 41, OCHRE[1])
    for i in range(8):                                    # the band runs up the stern post
        c.px(X0 + 1 - i * 0.3, sheer(X0 + 2) - i * 1.2, OCHRE[2])
    stem = [(X1 - 1, sheer(X1 - 1)), (X1 + 2, 50), (X1 + 3, 45)]
    for (xa, ya), (xb, yb) in zip(stem, stem[1:]):
        c.line(xa, ya, xb, yb, TAR[3]); c.line(xa + 1, ya, xb + 1, yb, OUTLINE)
    c.px(X1 + 4, 46, OCHRE[2]); c.px(X1 + 3, 46, OCHRE[2])
    c.line(X1 - 4, waterline(X1 - 4) + 1, X1 + 5, waterline(X1 - 4) + 3, TAR[2])     # cutwater
    c.line(X1 - 4, waterline(X1 - 4) + 2, X1 + 5, waterline(X1 - 4) + 4, OUTLINE)

    # ---- mast, yard and sail ---------------------------------------------------------------
    mx = 92
    for y in range(6, int(far_rail(mx)) + 6):
        c.px(mx, y, DECK[4]); c.px(mx + 1, y, DECK[2]); c.px(mx + 2, y, DECK[0])
    sx0, sx1, sy0, sy1 = 58, 128, 13, 52
    for x in range(sx0, sx1 + 1):
        t = (x - sx0) / (sx1 - sx0)
        belly = 3 * np.sin(np.pi * t)                       # the bottom edge sags in a curve
        bottom = sy1 + belly
        for y in range(sy0, int(bottom) + 1):
            # Light from the left; the cloth bellies, lighter in the middle of each panel.
            k = 4 if t < 0.25 else (3 if t < 0.6 else (2 if t < 0.88 else 1))
            panel = (x - sx0) % 10
            if panel == 0:
                k -= 2                                          # a brail line (seam)
            elif panel in (1, 2) and k < 4:
                k += 1
            v = (y - sy0) / (bottom - sy0)
            col = LINEN[max(0, min(4, k))]
            if 0.2 < v < 0.3 or 0.7 < v < 0.8:
                col = PURPLE[max(0, min(3, k - 1))]
            if y == int(bottom):
                col = LINEN[0]
            c.px(x, y, col)
        c.px(x, sy0 - 1, OUTLINE)
        c.px(x, int(bottom) + 1, OUTLINE)
    for y in range(sy0, sy1 + 2):
        c.px(sx0 - 1, y, OUTLINE); c.px(sx1 + 1, y + (2 if y > sy1 - 2 else 0), OUTLINE)
    for x in range(sx0 - 6, sx1 + 7):                       # the yard
        droop = ((x - mx) / 40) ** 2 * 1.5
        c.px(x, sy0 - 2 + droop, DECK[3]); c.px(x, sy0 - 1 + droop, DECK[1])
    c.px(sx0 - 7, sy0 - 1, OUTLINE); c.px(sx1 + 7, sy0 - 1, OUTLINE)
    # Stays from the masthead to the bow and the stern, and the brails hanging to the deck.
    c.line(mx + 1, 6, X1 + 3, 49, ROPE)
    c.line(mx, 6, X0 + 5, 33, ROPE)
    for bx in (68, 98, 118):
        c.line(bx, sy1 + 3, bx + 2, sheer(bx) - 4, (59, 46, 34, 200))
    # The mooring line, from the stern post up to the pier's end post (top left of the picture).
    for i in range(29):
        t = i / 28
        x = 19 + 3 * t
        y = 6 + 28 * t + 4 * np.sin(np.pi * t)
        c.px(x, y, ROPE_LIGHT if i % 3 else hexc("#9b8456"))
        c.px(x + 1, y, (40, 32, 24, 160))
    # Pennant at the masthead.
    for i in range(9):
        for j in range(3 - i // 3):
            c.px(mx + 2 + i, 3 + j + i // 4, PURPLE[2] if j == 0 else PURPLE[1])
    c.px(mx, 4, OUTLINE); c.px(mx + 1, 4, DECK[4])
    return Image.fromarray(c.a, "RGBA")


if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).parent / "preview"
    im = boat()
    bg = Image.new("RGBA", im.size, (52, 122, 140, 255))
    bg.alpha_composite(im)
    bg.resize((W * 4, H * 4), Image.NEAREST).save(out / "boat_x4.png")
    print("wrote", out / "boat_x4.png")
