"""Herb portraits for the herb lesson, drawn like small plates from an old herbal.

Each card is 64x64 with a transparent background (the game puts it on a cream card):
- moly: black bulb root showing at the soil, slender leaves, a milk-white six-petal star flower
  (black root and white flower, as in the Odyssey and in Miller's Circe);
- nightshade: branching stem, broad leaves, drooping purple bells and glossy black berries;
- hemlock: tall stem blotched with purple, feathery leaves, umbrellas of tiny white flowers.

Two harmless look-alikes, the pairs foragers really learn, for Hermes' flash cards:
- wild carrot: like hemlock, but a plain green, hairy stem and one dense lacy dome of flowers;
- bilberry: a low shrub with small oval leaves, pink urn-shaped flowers and dusty blue berries.
"""
from __future__ import annotations

import math

from px import Px, rgb, darken, lighten

OUTLINE = rgb("#2a1d14")
SOIL = rgb("#6b4a2f")
SOIL_D = rgb("#4a3220")
SOIL_L = rgb("#8a6240")
STEM = rgb("#5f8a35")
STEM_D = rgb("#3f6524")
LEAF = rgb("#5e9c3e")
LEAF_L = rgb("#86c25a")
LEAF_D = rgb("#3b6e2a")
WHITE = rgb("#f6f1e2")
WHITE_S = rgb("#d6cfbd")
POLLEN = rgb("#f0c64a")
ROOT = rgb("#1c1512")
ROOT_L = rgb("#3a2d26")
BELL = rgb("#7d4fa8")
BELL_L = rgb("#a57ad0")
BELL_D = rgb("#55317a")
BERRY = rgb("#1d1626")
BERRY_L = rgb("#6c5a86")
SPOT = rgb("#7a2a5c")
PINK = rgb("#e2a0b2")
PINK_L = rgb("#f3c8d2")
PINK_D = rgb("#b06e86")
BLUE = rgb("#3a4c8c")
BLUE_L = rgb("#93a4d2")
BLUE_D = rgb("#26315e")


def _soil(p: Px) -> None:
    p.ellipse(12, 52, 51, 60, SOIL)
    p.ellipse(14, 52, 49, 56, SOIL_L)
    p.hline(16, 47, 58, SOIL_D)
    p.dot(20, 55, SOIL_D); p.dot(43, 54, SOIL_D); p.dot(37, 57, SOIL_L)


def _stem(p: Px, pts: list[tuple[int, int]], c=STEM, shade=STEM_D) -> None:
    """A 2-pixel stem along a polyline, with a darker right edge."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            p.dot(x, y, c)
            p.dot(x + 1, y, shade)


def _leaf(p: Px, x: float, y: float, angle_deg: float, length: float, width: float,
          base=LEAF, light=LEAF_L, dark=LEAF_D) -> None:
    """A pointed leaf from (x, y) along angle; upper half lit, lower half shaded, pale midrib."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)          # along the leaf
    nx, ny = -uy, ux                           # across it
    for i in range(int(length * 4)):
        t = i / (length * 4)
        half = width * math.sin(math.pi * min(1.0, t * 1.05)) * (1.0 - 0.25 * t)
        cx, cy = x + ux * length * t, y + uy * length * t
        for j in range(-int(half * 3), int(half * 3) + 1):
            s = j / 3.0
            px_, py_ = cx + nx * s, cy + ny * s
            colour = light if s < -half * 0.35 else (dark if s > half * 0.4 else base)
            p.dot(round(px_), round(py_), colour)
        if t < 0.85:
            p.dot(round(cx), round(cy), light)    # midrib


def moly() -> Px:
    p = Px(64, 64)
    _soil(p)
    # The black bulb, half out of the soil, with a few root threads.
    p.ellipse(25, 45, 38, 56, ROOT)
    p.ellipse(27, 46, 31, 50, ROOT_L)
    for (x0, y0, x1, y1) in ((27, 55, 24, 58), (36, 55, 39, 58)):
        _stem(p, [(x0, y0), (x1, y1)], ROOT_L, ROOT_L)
    _stem(p, [(31, 46), (31, 34), (32, 22), (32, 14)])
    _leaf(p, 31, 44, -150, 15, 2.6)
    _leaf(p, 32, 42, -30, 15, 2.6)
    _leaf(p, 31, 34, -125, 11, 2.0)
    _leaf(p, 32, 31, -55, 10, 2.0)
    # Six-petal star flower, petals lit on top and shaded underneath.
    cx, cy = 32, 12
    for k in range(6):
        a = math.radians(k * 60 - 90)
        for r in range(2, 9):
            w = 2.2 * math.sin(math.pi * r / 9)
            for s in (-w, -w / 2, 0, w / 2, w):
                x = cx + math.cos(a) * r - math.sin(a) * s
                y = cy + math.sin(a) * r + math.cos(a) * s
                p.dot(round(x), round(y), WHITE if s <= 0 else WHITE_S)
    p.ellipse(30, 10, 34, 14, POLLEN)
    p.dot(31, 11, lighten(POLLEN))
    # A closed bud on a side stem.
    _stem(p, [(32, 26), (40, 21), (43, 18)])
    p.ellipse(42, 14, 46, 19, WHITE_S)
    p.dot(43, 15, WHITE)
    p.outline(OUTLINE)
    return p


def nightshade() -> Px:
    p = Px(64, 64)
    _soil(p)
    _stem(p, [(31, 54), (31, 40), (29, 28), (26, 18)])
    _stem(p, [(31, 40), (38, 32), (42, 22)])
    _leaf(p, 31, 48, -160, 13, 4.2)
    _leaf(p, 32, 45, -20, 13, 4.2)
    _leaf(p, 30, 33, -150, 10, 3.4)
    _leaf(p, 37, 33, -10, 9, 3.0)
    # Drooping purple bells: a rounded top, a flared mouth, a lighter lit side.
    for (x, y) in ((24, 18), (42, 22), (19, 27)):
        _stem(p, [(x + 1, y - 5), (x, y - 2)])
        p.ellipse(x - 3, y - 2, x + 3, y + 4, BELL)
        p.rect(x - 4, y + 4, x + 4, y + 5, BELL_D)
        p.dot(x - 2, y, BELL_L); p.dot(x - 1, y - 1, BELL_L)
        p.dot(x, y + 6, POLLEN)
    # Glossy black berries, each on a green star of sepals, with one bright highlight.
    _stem(p, [(33, 46), (41, 44), (47, 40)])
    for (x, y) in ((41, 47), (48, 43), (54, 38)):
        _stem(p, [(x, y - 5), (x, y - 3)])
        p.poly([(x - 3, y - 2), (x, y - 4), (x + 3, y - 2)], LEAF_D)
        p.ellipse(x - 2, y - 2, x + 2, y + 2, BERRY)
        p.dot(x - 1, y - 1, BERRY_L)
    p.outline(OUTLINE)
    return p


def hemlock() -> Px:
    p = Px(64, 64)
    _soil(p)
    _stem(p, [(32, 54), (32, 30), (31, 14)])
    for y in (51, 47, 43, 38, 33, 28, 23, 18):
        p.dot(32, y, SPOT); p.dot(32, y + 1, SPOT)
        p.dot(33, y, darken(SPOT)); p.dot(33, y + 1, darken(SPOT))
    # Feathery leaves: a rachis with small paired leaflets.
    for (x, y, ang, n) in ((31, 46, -160, 6), (33, 42, -20, 6), (31, 34, -145, 4), (33, 31, -35, 4)):
        a = math.radians(ang)
        for i in range(n):
            bx = x + math.cos(a) * i * 2.4
            by = y + math.sin(a) * i * 2.4
            p.dot(round(bx), round(by), STEM_D)
            for side in (-1, 1):
                lx = bx - math.sin(a) * side * 2.2
                ly = by + math.cos(a) * side * 2.2
                p.dot(round(lx), round(ly), LEAF)
                p.dot(round(lx + math.cos(a)), round(ly + math.sin(a)), LEAF_L if side < 0 else LEAF_D)
    # A compound umbel: spokes from one point to small domed clusters of white florets.
    hub = (31, 16)
    for (x, y) in ((20, 9), (26, 5), (33, 4), (40, 6), (45, 11)):
        _stem(p, [hub, (x, y + 2)], STEM, STEM)
        for (dx, dy) in ((-2, 0), (0, -1), (2, 0), (-1, 1), (1, 1), (0, 1)):
            p.dot(x + dx, y + dy, WHITE)
        p.dot(x + 1, y + 1, WHITE_S); p.dot(x - 1, y + 2, WHITE_S)
    p.outline(OUTLINE)
    return p


def _feathery_leaves(p: Px, sprigs) -> None:
    """Hemlock-type leaves: a rachis with small paired leaflets."""
    for (x, y, ang, n) in sprigs:
        a = math.radians(ang)
        for i in range(n):
            bx = x + math.cos(a) * i * 2.4
            by = y + math.sin(a) * i * 2.4
            p.dot(round(bx), round(by), STEM_D)
            for side in (-1, 1):
                lx = bx - math.sin(a) * side * 2.2
                ly = by + math.cos(a) * side * 2.2
                p.dot(round(lx), round(ly), LEAF)
                p.dot(round(lx + math.cos(a)), round(ly + math.sin(a)), LEAF_L if side < 0 else LEAF_D)


def wild_carrot() -> Px:
    p = Px(64, 64)
    _soil(p)
    _stem(p, [(32, 54), (32, 30), (31, 15)])
    # Fine hairs along a plain green stem: no purple anywhere.
    for y in (50, 44, 38, 32, 26, 20):
        p.dot(31, y, LEAF_L); p.dot(34, y + 3, LEAF_L)
    _feathery_leaves(p, ((31, 47, -165, 6), (33, 43, -15, 6), (31, 35, -140, 4), (33, 32, -40, 4)))
    # One dense, flat-topped lacy dome on many spokes, not hemlock's separate small umbrellas.
    hub = (31, 16)
    for x in range(20, 45, 3):
        _stem(p, [hub, (x, 10)], STEM, STEM)
    # Hundreds of tiny florets: small clusters packed into a dome, with dark gaps between them.
    cx, cy, rx, ry = 31.5, 9.0, 13.5, 5.5
    for y in range(3, 14):
        for x in range(17, 47):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1.0:
                continue
            if (x % 3 == 0 and y % 3 == 1) or (x % 3 == 2 and y % 3 == 2 and x % 2):
                continue
            p.dot(x, y, WHITE_S if y >= 11 or (x + 2 * y) % 7 == 0 else WHITE)
    p.outline(OUTLINE)
    return p


def bilberry() -> Px:
    p = Px(64, 64)
    _soil(p)
    # A low, bushy shrub: angular green stems that branch near the ground.
    for pts in (
        [(31, 54), (29, 46), (24, 40), (20, 32)],
        [(32, 54), (33, 45), (31, 37), (33, 28)],
        [(33, 54), (37, 47), (42, 41), (45, 33)],
        [(29, 46), (36, 41)],
    ):
        _stem(p, pts)
    # Small oval leaves along the stems.
    for (x, y, ang) in ((24, 40, -150), (20, 33, -110), (26, 44, 170), (31, 37, -160), (33, 29, -70),
                        (34, 41, -20), (42, 41, -30), (45, 34, -70), (39, 46, 10), (30, 47, -175)):
        _leaf(p, x, y, ang, 6, 2.0)
    # Pink urn-shaped flowers, hanging.
    for (x, y) in ((19, 36), (35, 31), (46, 37)):
        p.ellipse(x - 2, y - 2, x + 2, y + 3, PINK)
        p.dot(x - 1, y - 1, PINK_L)
        p.dot(x + 1, y + 2, PINK_D); p.dot(x, y + 3, PINK_D)
    # Round blue berries with a dusty bloom and a small crown underneath.
    for (x, y) in ((24, 46), (29, 41), (38, 45), (43, 47), (27, 50)):
        p.ellipse(x - 2, y - 2, x + 2, y + 2, BLUE)
        p.dot(x - 1, y - 1, BLUE_L); p.dot(x, y - 1, BLUE_L)
        p.dot(x + 1, y + 1, BLUE_D); p.dot(x, y + 2, BLUE_D)
    p.outline(OUTLINE)
    return p


def card_back_flower() -> Px:
    """The small white flower in the middle of a face-down flash card."""
    p = Px(11, 11)
    for (x, y) in ((5, 1), (5, 9), (1, 3), (9, 3), (1, 7), (9, 7)):
        p.ellipse(x - 1, y - 1, x + 1, y + 1, WHITE)
    p.ellipse(3, 3, 7, 7, WHITE)
    p.dot(5, 5, POLLEN)
    return p


def herb_card(kind: str) -> Px:
    return {"moly": moly, "nightshade": nightshade, "hemlock": hemlock,
            "wild_carrot": wild_carrot, "bilberry": bilberry}[kind]()


if __name__ == "__main__":
    from pathlib import Path
    from PIL import Image
    kinds = ("moly", "nightshade", "bilberry", "hemlock", "wild_carrot")
    out = Image.new("RGBA", (len(kinds) * 266 + 10, 64 * 4 + 20), (237, 222, 184, 255))
    for i, k in enumerate(kinds):
        im = herb_card(k).im.resize((256, 256), Image.Resampling.NEAREST)
        out.alpha_composite(im, (10 + i * 266, 10))
    dest = Path(__file__).parent / "preview" / "herbs_x4.png"
    dest.parent.mkdir(exist_ok=True)
    out.save(dest)
    print(dest)
