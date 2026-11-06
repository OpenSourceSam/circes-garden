"""The three moly beds in Circe's garden, one 64x64 image per growth stage.

The bed itself (tilled earth inside a border of fieldstones) is painted into the island ground
(yard.py); each plot only draws its three planting spots and what grows in them: hoed soil,
seeds in their holes, two-leaf sprouts, young plants with closed white buds, then the milk-white
star flowers of the herb lesson. Three variants (0, 1, 2) give the plots their own spacing.
"""
from __future__ import annotations

import math
import random

from px import Px, rgb

OUTLINE = rgb("#2a1d14")
EARTH = rgb("#5a3b24")
EARTH_D = rgb("#3e2817")
EARTH_L = rgb("#7a5233")
EARTH_HI = rgb("#936746")
SEED = rgb("#24170f")
STEM = rgb("#5f8a35")
LEAF = rgb("#5e9c3e")
LEAF_L = rgb("#86c25a")
LEAF_D = rgb("#3b6e2a")
WHITE = rgb("#f6f1e2")
WHITE_S = rgb("#d6cfbd")
POLLEN = rgb("#f0c64a")
GLINT = rgb("#fff6c8")

XS = (21, 32, 43)        # the three plants
BASE_Y = 44              # where their stems meet the soil


def _spots(p: Px, xs) -> None:
    """Three hoed spots of loose, darker earth where the moly goes, no outline (the bed's earth
    is painted under them)."""
    for x in xs:
        for dy in range(-2, 3):
            half = [2, 4, 5, 4, 2][dy + 2]
            for dx in range(-half, half + 1):
                p.dot(x + dx, BASE_Y + dy, EARTH_D if dy > -1 else EARTH)
        p.dot(x - 2, BASE_Y - 2, EARTH_HI); p.dot(x + 1, BASE_Y - 2, EARTH_L); p.dot(x + 3, BASE_Y - 1, EARTH_L)


def _bed(p: Px, variant: int = 0) -> None:
    """The old free-standing mound (before the beds were painted into the ground); unused."""
    rng = random.Random(41 + variant * 13)
    # Ragged mound: an ellipse with a wobbling edge.
    cx, cy, rx, ry = 32, 44, 23, 10
    for y in range(cy - ry - 2, cy + ry + 2):
        for x in range(cx - rx - 2, cx + rx + 3):
            a = math.atan2((y - cy) / ry, (x - cx) / rx)
            wobble = 1.0 + 0.06 * math.sin(a * 7 + variant * 2.1) + 0.04 * math.sin(a * 13 + 1 + variant * 1.3)
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d <= wobble:
                top = (y - cy) / ry
                colour = EARTH_L if top < -0.45 else (EARTH_D if top > 0.55 else EARTH)
                p.dot(x, y, colour)
    # A furrow along the row of plants, and scattered clods.
    for x in range(13, 52):
        p.dot(x, BASE_Y + 1 + (1 if (x // 6) % 2 else 0), EARTH_D)
    for _ in range(26):
        x, y = rng.randrange(12, 53), rng.randrange(37, 52)
        if p.im.getpixel((x, y))[3]:
            p.dot(x, y, EARTH_HI if rng.random() < 0.5 else EARTH_D)


def _sprout(p: Px, x: int, size: int) -> None:
    top = BASE_Y - 3 - size * 5
    for y in range(top, BASE_Y + 1):
        p.dot(x, y, STEM)
    p.dot(x + 1, BASE_Y, LEAF_D)
    # Paired leaves as small rounded blades, bigger and more of them as the plant grows.
    for i in range(min(size, 3)):
        ly = BASE_Y - 2 - i * 5
        length = 3 + size - i
        for side in (-1, 1):
            for k in range(1, length + 1):
                lx = x + side * k
                lift = (k * k) // (length + 3)
                thick = 1 if k in (1, length) else 2
                for t in range(thick):
                    shade = LEAF_L if (side > 0 and t == 0) else (LEAF_D if t == 1 else LEAF)
                    p.dot(lx, ly - lift - t, shade)


def _bud(p: Px, x: int, y: int) -> None:
    p.ellipse(x - 2, y - 3, x + 1, y + 1, WHITE_S)
    p.dot(x - 1, y - 2, WHITE)
    p.dot(x, y + 2, LEAF_D)


def _star(p: Px, x: int, y: int) -> None:
    for k in range(6):
        a = math.radians(k * 60 - 90)
        for r in range(1, 6):
            for s in (-0.7, 0.0, 0.7):
                if r == 5 and s:
                    continue
                px_ = x + math.cos(a) * r - math.sin(a) * s
                py_ = y + math.sin(a) * r + math.cos(a) * s
                p.dot(round(px_), round(py_), WHITE if s <= 0 else WHITE_S)
    p.rect(x - 1, y - 1, x, y, POLLEN)


def plot(stage: str, variant: int = 0) -> Px:
    p = Px(64, 64)
    XS = tuple(x + d for x, d in zip(globals()["XS"], ((0, 0, 0), (-1, 1, 2), (1, -1, -2))[variant % 3]))
    _spots(p, XS)
    plants = Px(64, 64)
    if stage == "planted":
        for x in XS:
            plants.ellipse(x - 2, BASE_Y - 1, x + 2, BASE_Y + 2, EARTH_D)
            plants.dot(x, BASE_Y, SEED)
            plants.dot(x, BASE_Y - 2, LEAF_L)          # the first green tip, so planting shows
    elif stage == "stage_1":
        for x in XS:
            _sprout(plants, x, 1)
    elif stage == "stage_2":
        for x in XS:
            _sprout(plants, x, 2)
            _bud(plants, x, BASE_Y - 14)
    elif stage == "ready":
        for x in XS:
            _sprout(plants, x, 3)
            _star(plants, x, BASE_Y - 21)
        for (gx, gy) in ((12, 18), (52, 20), (26, 14), (40, 12)):
            plants.dot(gx, gy, GLINT)                  # a few motes of light: the moly is ready
    plants.outline(OUTLINE)
    p.paste(plants, 0, 0)
    return p


if __name__ == "__main__":
    from pathlib import Path
    from PIL import Image
    stages = ("empty", "planted", "stage_1", "stage_2", "ready")
    out = Image.new("RGBA", (len(stages) * 64, 64), (70, 110, 40, 255))
    for i, s in enumerate(stages):
        out.alpha_composite(plot(s).im, (i * 64, 0))
    dest = Path(__file__).parent / "preview" / "garden_beds_x3.png"
    out.resize((out.width * 3, out.height * 3), Image.Resampling.NEAREST).save(dest)
    print(dest)
