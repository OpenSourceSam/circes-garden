"""The island's small objects, redrawn in code with one light direction (upper left), one wood
ramp and the house's terracotta: fence pieces, a crate, a lantern on a post, a signpost, the
well and Circe's worktable. The first versions (tiles.py, props.py) were flat shapes in one or
two colours; a review against a well-made cozy farming game ranked them among the weakest
things on screen.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from paint import hexc

WOOD = [hexc("#2e1f14"), hexc("#4f3622"), hexc("#6d4c30"), hexc("#8b643f"), hexc("#a97d51"), hexc("#c49a68")]
IRON = [hexc("#1e1d20"), hexc("#3a383c"), hexc("#5d5a5e")]
BRONZE = [hexc("#5a3a1a"), hexc("#8a5a26"), hexc("#b5843b"), hexc("#d9ae5c")]
STONE = [hexc("#4f4a42"), hexc("#6e675c"), hexc("#8d8577"), hexc("#aaa293"), hexc("#c5bdaf"), hexc("#d9d2c4")]
ROOF = [hexc("#45201a"), hexc("#622e20"), hexc("#7f3b27"), hexc("#9b4a2f"), hexc("#b35c39"), hexc("#c87449")]
WATER = [hexc("#0f1e26"), hexc("#1d3a46"), hexc("#3c6b78"), hexc("#8fc9c4")]
GLOW = [hexc("#c8742a"), hexc("#f0a43c"), hexc("#ffd77a"), hexc("#fff3c4")]
GLASS = [hexc("#2d5d6a"), hexc("#4f9aa8"), hexc("#9fd8de")]
LEAF = [hexc("#2c3a1a"), hexc("#475a26"), hexc("#647a33"), hexc("#86994a")]
OUTLINE = hexc("#21160f")


class Canvas:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)

    def px(self, x, y, c) -> None:
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c) -> None:
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = c

    def outline(self, c=OUTLINE) -> None:
        m = self.a[..., 3] > 0
        out = np.zeros_like(m)
        out[:, 1:] |= m[:, :-1] & ~m[:, 1:]
        out[:, :-1] |= m[:, 1:] & ~m[:, :-1]
        out[1:, :] |= m[:-1, :] & ~m[1:, :]
        out[:-1, :] |= m[1:, :] & ~m[:-1, :]
        self.a[out] = c

    def image(self) -> Image.Image:
        return Image.fromarray(self.a, "RGBA")


def _post(c: Canvas, x0: int, y0: int, y1: int, w: int = 5) -> None:
    """A squared post, lit on the left, with a pyramid cap and a darker, weathered foot."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x0 + w):
            k = 4 if x == x0 else (3 if x < x0 + w - 1 else 1)
            if y > y1 - 3:
                k = max(1, k - 1)
            if (x * 5 + y * 3) % 11 == 0 and x not in (x0, x0 + w - 1):
                k -= 1                                      # grain
            c.px(x, y, WOOD[k])
    for x in range(x0, x0 + w):                             # the cap
        c.px(x, y0, WOOD[5] if x < x0 + w // 2 + 1 else WOOD[3])
    c.px(x0 + w // 2, y0 - 1, WOOD[5])


def _rail(c: Canvas, x0: int, x1: int, y: int) -> None:
    """A horizontal rail 3 px tall: lit top, body, shadowed underside."""
    for x in range(x0, x1 + 1):
        c.px(x, y, WOOD[5] if (x // 9) % 4 else WOOD[4])
        c.px(x, y + 1, WOOD[3] if (x * 7) % 13 else WOOD[2])
        c.px(x, y + 2, WOOD[1])


def fence(kind: str, variant: int = 0) -> Image.Image:
    """One 32 px fence tile ('h', 'v', 'tl', 'tr', 'bl', 'br', 'post', 'end_l', 'end_r'), the
    same layout as before: posts centred at x 13-18, rails at y 10 and 19. Variants 1 and 2 give
    a post that stands a pixel lower or carries a knot and a tuft of moss at its foot."""
    c = Canvas(32, 32)
    if kind in ("h", "tl", "tr", "bl", "br", "end_l", "end_r"):
        x0 = 15 if kind in ("tl", "bl", "end_l") else 0
        x1 = 17 if kind in ("tr", "br", "end_r") else 31
        _rail(c, x0, x1, 10)
        _rail(c, x0, x1, 19)
    if kind in ("v", "tl", "tr", "bl", "br"):
        y0 = 10 if kind in ("tl", "tr") else 0
        y1 = 22 if kind in ("bl", "br") else 31
        for y in range(y0, y1 + 1):                         # the side rail, seen from above
            c.px(14, y, WOOD[4]); c.px(15, y, WOOD[3]); c.px(16, y, WOOD[3]); c.px(17, y, WOOD[1])
    if kind in ("post", "tl", "tr", "bl", "br", "h", "v", "end_l", "end_r"):
        corner = kind in ("tl", "tr", "bl", "br", "end_l", "end_r")
        top = (6 if not corner else 4) + (1 if variant == 1 else 0)
        _post(c, 13 if not corner else 12, top, 27, 6 if not corner else 7)
        if variant == 2:
            c.px(15, 15, WOOD[1]); c.px(16, 16, WOOD[2])                       # a knot
            for (x, y, k) in ((13, 27, 1), (14, 26, 2), (17, 27, 1), (18, 26, 2)):
                c.px(x, y, LEAF[k])                                         # moss at the foot
        if variant == 1:
            c.px(14, 18, WOOD[1]); c.px(14, 19, WOOD[1])                     # a split in the grain
    c.outline()
    return c.image()


def crate() -> Image.Image:
    c = Canvas(32, 32)
    x0, x1, top, front, bot = 6, 25, 8, 13, 27
    for y in range(top, front):                             # the lid, seen from above
        for x in range(x0 + 1, x1):
            k = 5 if y == top else (4 if (x - x0) % 6 else 3)
            c.px(x, y, WOOD[k])
    for y in range(front, bot + 1):                         # the front: planks and a brace
        for x in range(x0, x1 + 1):
            k = 3 if (y - front) % 5 else 1
            if x in (x0, x0 + 1):
                k = 4
            if x in (x1 - 1, x1):
                k = 2
            c.px(x, y, WOOD[k])
    for i in range(x1 - x0 - 3):                            # diagonal brace
        c.px(x0 + 2 + i, bot - 1 - i * (bot - front - 2) / (x1 - x0 - 4), WOOD[5])
        c.px(x0 + 2 + i, bot - i * (bot - front - 2) / (x1 - x0 - 4), WOOD[1])
    for (x, y) in ((x0 + 1, front + 1), (x1 - 1, front + 1), (x0 + 1, bot - 1), (x1 - 1, bot - 1)):
        c.px(x, y, IRON[2])
    for x in range(x0, x1 + 1):
        c.px(x, front, WOOD[1])
    c.outline()
    return c.image()


def lantern_post() -> Image.Image:
    """A post with an arm and a bronze lantern hanging from it, its glass lit warm."""
    c = Canvas(32, 32)
    _post(c, 9, 4, 29, 4)
    for x in range(12, 24):                                 # the arm
        c.px(x, 6, WOOD[4]); c.px(x, 7, WOOD[1])
    c.px(20, 8, IRON[1]); c.px(20, 9, IRON[1])              # hook
    lx = 20
    for y in range(10, 20):                                 # lantern body
        half = 3 if 11 <= y <= 18 else 2
        for dx in range(-half, half + 1):
            if y in (10, 19):
                col = BRONZE[2] if dx < 1 else BRONZE[1]
            elif abs(dx) == half:
                col = BRONZE[1] if dx > 0 else BRONZE[2]
            else:
                col = GLOW[3] if (dx < 0 and y < 15) else (GLOW[2] if y < 17 else GLOW[1])
            c.px(lx + dx, y, col)
    c.px(lx, 9, BRONZE[3])
    for y in range(11, 19):
        c.px(lx, y, BRONZE[1] if y % 3 == 0 else c.a[y, lx])
    c.outline()
    return c.image()


def signpost() -> Image.Image:
    c = Canvas(32, 32)
    _post(c, 14, 12, 29, 4)
    x0, x1, y0, y1 = 5, 26, 6, 15
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = 4 if y == y0 else (3 if y < y1 - 1 else 2)
            if (y - y0) == 4:
                k = 2                                       # the seam between two boards
            if x == x1:
                k = 1
            c.px(x, y, WOOD[k])
    for x in range(x0 - 1, x0 + 2):                         # a pointed end, toward the shore
        pass
    c.px(x1 + 1, y0 + 2, WOOD[2]); c.px(x1 + 1, y0 + 6, WOOD[2])
    for x in range(x1 + 1, x1 + 4):
        for y in range(y0 + 2 + (x - x1 - 1), y1 - 1 - (x - x1 - 1)):
            c.px(x, y, WOOD[3] if y < (y0 + y1) / 2 else WOOD[2])
    # Carved marks: a little boat and a wave, burnt dark.
    for x in range(9, 18):
        c.px(x, 11, WOOD[0] if 10 <= x <= 16 else WOOD[1])
    c.px(10, 10, WOOD[1]); c.px(16, 10, WOOD[1])
    for y in range(7, 11):
        c.px(13, y, WOOD[1])
    c.px(14, 8, WOOD[1]); c.px(15, 9, WOOD[1])
    for x in range(19, 24):
        c.px(x, 10 + (x % 2), WOOD[1])
    for (x, y) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        c.px(x, y, IRON[1])
    c.outline()
    return c.image()


def well() -> Image.Image:
    """A round stone well with a small terracotta roof on two posts, a windlass, a rope and a
    bucket on its rim."""
    c = Canvas(64, 64)
    cx = 31.5
    # Stone ring: the far rim (top of the ellipse), the water inside, the near wall below.
    rx, ry, rim_y = 21, 8, 38
    for y in range(rim_y - ry - 2, 61):
        for x in range(64):
            dx = (x - cx) / rx
            top_d = dx * dx + ((y - rim_y) / ry) ** 2
            if y <= rim_y:
                inside = top_d <= 1.0
                inner = (x - cx) ** 2 / (rx - 5) ** 2 + ((y - rim_y) / (ry - 3)) ** 2 <= 1.0
                if inner:
                    t = (y - (rim_y - ry + 3)) / (2 * (ry - 3))
                    c.px(x, y, WATER[0] if t < 0.35 else (WATER[1] if t < 0.8 else WATER[2]))
                elif inside:
                    c.px(x, y, STONE[5] if y < rim_y - ry + 3 else (STONE[4] if x < cx else STONE[3]))
            else:
                if abs(dx) <= 1.0 and y <= rim_y + 16 + 3 * np.sqrt(max(0, 1 - dx * dx)):
                    course = (y - rim_y) // 5
                    off = 0 if course % 2 == 0 else 4
                    joint = (y - rim_y) % 5 == 0 or (int((x + off) / 8) != int((x + off - 1) / 8))
                    k = 3 if dx < -0.45 else (2 if dx < 0.5 else 1)
                    if joint:
                        k = 0
                    if y > rim_y + 14:
                        k = max(0, k - 1)
                    c.px(x, y, STONE[k + 1 if not joint else 1])
    for x in range(int(cx - rx), int(cx + rx) + 1):          # lit near rim
        dx = (x - cx) / rx
        if abs(dx) <= 1:
            y = rim_y + ry * np.sqrt(max(0, 1 - dx * dx))
            c.px(x, y, STONE[5] if dx < 0.3 else STONE[4]); c.px(x, y + 1, STONE[3])
    # A glint on the water.
    c.px(cx - 4, rim_y - 1, WATER[3]); c.px(cx - 3, rim_y - 1, WATER[3]); c.px(cx + 2, rim_y, WATER[2])
    # Posts and windlass.
    for px_ in (12, 48):
        for y in range(9, rim_y + 4):
            c.px(px_, y, WOOD[4]); c.px(px_ + 1, y, WOOD[3]); c.px(px_ + 2, y, WOOD[1])
    for x in range(15, 48):
        c.px(x, 20, WOOD[4]); c.px(x, 21, WOOD[2]); c.px(x, 22, WOOD[1])
    for y in range(23, 33):                                  # rope down to the bucket
        c.px(31, y, hexc("#c9b27a") if y % 2 else hexc("#9b8456"))
    for y in range(33, 40):                                  # bucket on the rim
        half = 4 if y > 34 else 5
        for dx in range(-half, half + 1):
            col = WOOD[4] if dx < -1 else (WOOD[3] if dx < 2 else WOOD[2])
            if y in (35, 38):
                col = IRON[2] if dx < 1 else IRON[1]
            c.px(31 + dx, y, col)
    c.px(48 + 4, 19, WOOD[4]); c.px(48 + 5, 19, WOOD[3]); c.px(48 + 5, 20, WOOD[2]); c.px(48 + 5, 21, WOOD[2])   # crank
    # Roof: terracotta barrel tiles like the house, seen from above, with a ridge.
    for y in range(2, 13):
        span = 6 + (y - 2) * 2.2
        for x in range(int(cx - span), int(cx + span) + 1):
            f = (x - (cx - span)) % 6
            k = 4 if f < 2 else (3 if f < 4 else 2)
            if y >= 11:
                k = 1 if y == 12 else 2
            c.px(x, y, ROOF[k])
    for x in range(int(cx - 6), int(cx + 7)):
        c.px(x, 2, ROOF[5]); c.px(x, 1, OUTLINE)
    c.outline()
    c.a = np.roll(c.a, 2, axis=0)              # clear of the top of its box (it read as cut off)
    return c.image()


def worktable() -> Image.Image:
    """Circe's worktable, 64 x 64: a heavy olive-wood table seen from above and in front, with a
    stone mortar and pestle, glass bottles of coloured tinctures, a bundle of herbs, a clay jar
    and a scroll."""
    c = Canvas(64, 64)
    x0, x1, top0, top1 = 6, 57, 30, 41
    for y in range(top1 + 1, 57):                            # legs
        for (lx, w) in ((9, 4), (51, 4)):
            for x in range(lx, lx + w):
                c.px(x, y, WOOD[3] if x == lx else (WOOD[2] if x < lx + w - 1 else WOOD[1]))
    for x in range(12, 52):                                  # a stretcher between the legs
        c.px(x, 50, WOOD[2]); c.px(x, 51, WOOD[1])
    for y in range(top0, top1 + 1):                          # the top, lit, with board seams
        for x in range(x0, x1 + 1):
            k = 5 if y == top0 else 4
            if (y - top0) in (4, 8):
                k = 3
            if x == x1:
                k = 2
            c.px(x, y, WOOD[k])
    for x in range(x0, x1 + 1):                              # its front edge
        c.px(x, top1 + 1, WOOD[2]); c.px(x, top1 + 2, WOOD[1])
    # Mortar and pestle.
    for y in range(24, 33):
        half = [3, 4, 5, 5, 5, 4, 4, 3, 3][y - 24]
        for dx in range(-half, half + 1):
            col = STONE[4] if dx < -1 else (STONE[3] if dx < 2 else STONE[2])
            if y == 24:
                col = STONE[1]
            c.px(15 + dx, y, col)
    for i in range(9):
        c.px(17 + i * 0.35, 23 - i, WOOD[4] if i < 7 else WOOD[5])
    # Three bottles: green, violet (Circe's draught) and amber.
    for (bx, liquid, tall) in ((27, [hexc("#2f6b4a"), hexc("#4f9a6a"), hexc("#9fd8b0")], 12),
                               (34, [hexc("#4a2a7a"), hexc("#7046a8"), hexc("#b494e0")], 15),
                               (41, [hexc("#8a4f1a"), hexc("#c58232"), hexc("#f0c070")], 10)):
        base = top0 + 3
        for y in range(base - tall, base):
            neck = y < base - tall + 4
            half = 1 if neck else 3
            for dx in range(-half, half + 1):
                if neck:
                    col = GLASS[1] if dx < 1 else GLASS[0]
                else:
                    col = liquid[2] if dx == -half + 1 and y < base - 4 else (liquid[1] if dx < 1 else liquid[0])
                c.px(bx + dx, y, col)
        c.px(bx, base - tall - 1, WOOD[3]); c.px(bx + 1, base - tall - 1, WOOD[2])     # cork
    # A bundle of herbs lying on the table, and a small clay jar.
    for i in range(10):
        c.px(46 + i, 35 - (i % 3 == 0), LEAF[2 + (i % 2)])
        c.px(46 + i, 36, LEAF[1])
    c.px(49, 34, hexc("#a08ad6")); c.px(52, 33, hexc("#a08ad6")); c.px(54, 34, hexc("#c4b3ee"))
    for y in range(27, 33):
        half = 2 if y in (27, 28) else 3
        for dx in range(-half, half + 1):
            c.px(52 + dx, y, ROOF[4] if dx < 0 else ROOF[3])
    # A scroll at the front corner.
    for x in range(10, 22):
        c.px(x, 38, hexc("#efe3c2")); c.px(x, 39, hexc("#d6c59e"))
    c.px(9, 38, hexc("#b8a47a")); c.px(22, 39, hexc("#b8a47a"))
    c.outline()
    return c.image()


if __name__ == "__main__":
    from pathlib import Path
    tiles = [fence(k) for k in ("tl", "h", "end_r", "v", "bl", "post")] + [crate(), lantern_post(), signpost()]
    big = [well(), worktable()]
    out = Image.new("RGBA", (32 * len(tiles) + 64 * len(big) + 20, 64), (110, 122, 56, 255))
    for i, t in enumerate(tiles):
        out.alpha_composite(t, (i * 32, 32))
    for i, t in enumerate(big):
        out.alpha_composite(t, (32 * len(tiles) + 20 + i * 64, 0))
    out.resize((out.width * 4, out.height * 4), Image.NEAREST).save(Path(__file__).parent / "preview" / "smallprops_x4.png")
    print("ok")
