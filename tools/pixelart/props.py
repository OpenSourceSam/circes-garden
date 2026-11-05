"""Static props (64x64, boat 128x64) and 32x32 inventory icons."""
from __future__ import annotations

from px import OUTLINE, WHITE, Px, rgb, darken, lighten

WOOD = rgb("#9c6b3c")
WOOD_DARK = rgb("#6e4826")
WOOD_LIGHT = rgb("#c08a52")
SOIL = rgb("#5c3a21")
SOIL_DARK = rgb("#3e2715")
SOIL_LIGHT = rgb("#7a5230")
LEAF = rgb("#4f9a3a")
LEAF_DARK = rgb("#2f6b26")
LEAF_LIGHT = rgb("#8ccf5a")
PETAL = rgb("#f6f3e7")
POLLEN = rgb("#f2c84b")
CREAM = rgb("#efe3c6")
PURPLE = rgb("#5b2a86")
GOLD = rgb("#e3b341")
STONE = rgb("#9a9aa6")
STONE_DARK = rgb("#6c6c78")
GLASS = rgb("#7fd3e6")
GLASS_DARK = rgb("#3f93a8")
LIQUID = rgb("#b8f0ff")
SEED = rgb("#3a2518")
SEED_LIGHT = rgb("#6b4a2e")


def boat() -> Px:
    p = Px(128, 64)
    # Hull
    p.trapezoid(64, 38, 100, 54, 70, WOOD)
    p.hline(14, 113, 38, WOOD_LIGHT)
    p.hline(20, 108, 44, WOOD_DARK)
    p.hline(26, 102, 50, WOOD_DARK)
    # Prow curl
    p.rect(12, 32, 15, 38, WOOD)
    p.rect(112, 32, 115, 38, WOOD)
    # Mast and sail
    p.rect(63, 6, 65, 38, WOOD_DARK)
    p.poly([(66, 8), (100, 30), (66, 32)], CREAM)
    p.poly([(62, 10), (36, 30), (62, 32)], darken(CREAM, 0.9))
    p.hline(66, 96, 30, darken(CREAM, 0.8))
    p.rect(60, 3, 68, 6, PURPLE)  # pennant
    p.outline(OUTLINE)
    return p


def crafting_table() -> Px:
    p = Px(64, 64)
    # Legs
    p.rect(12, 40, 15, 56, WOOD_DARK)
    p.rect(48, 40, 51, 56, WOOD_DARK)
    p.rect(14, 46, 49, 48, WOOD_DARK)
    # Table top (slight perspective)
    p.rect(8, 34, 55, 41, WOOD)
    p.hline(8, 55, 34, WOOD_LIGHT)
    p.hline(8, 55, 41, WOOD_DARK)
    # Mortar and pestle
    p.ellipse(14, 24, 26, 34, STONE)
    p.rect(14, 24, 26, 26, STONE_DARK)
    p.rect(19, 16, 21, 27, WOOD_LIGHT)
    # Bottles
    p.rect(32, 22, 36, 33, GLASS); p.rect(33, 19, 35, 22, WOOD_DARK); p.rect(33, 27, 35, 32, LIQUID)
    p.rect(40, 25, 44, 33, PURPLE); p.rect(41, 22, 43, 25, WOOD_DARK)
    # Herb bundle
    p.rect(46, 29, 52, 33, LEAF); p.dot(47, 28, LEAF_LIGHT); p.dot(50, 27, LEAF_LIGHT); p.dot(52, 28, LEAF_DARK)
    p.outline(OUTLINE)
    return p


def sleep_spot() -> Px:
    p = Px(64, 64)
    # Bedroll seen from above-front
    p.rect(16, 18, 47, 56, CREAM)
    p.rect(16, 30, 47, 56, PURPLE)
    p.hline(16, 47, 30, GOLD)
    p.hline(16, 47, 48, darken(PURPLE, 0.8))
    p.rect(20, 20, 43, 27, lighten(CREAM, 1.05))   # pillow
    p.hline(20, 43, 27, darken(CREAM, 0.85))
    p.rect(14, 54, 49, 57, WOOD_DARK)               # mat edge
    p.outline(OUTLINE)
    return p


def _soil(p: Px) -> None:
    p.rect(8, 26, 55, 55, SOIL)
    for y in (31, 37, 43, 49):
        p.hline(10, 53, y, SOIL_DARK)
        p.hline(10, 53, y + 1, SOIL_LIGHT)
    p.hline(8, 55, 26, SOIL_LIGHT)
    p.hline(8, 55, 55, SOIL_DARK)


def _plant(p: Px, x: int, y: int, size: int, flower: bool) -> None:
    """Moly: a small plant with a white flower at full size."""
    p.rect(x, y - size * 3, x + 1, y, LEAF_DARK)
    for i in range(size):
        ly = y - 2 - i * 3
        p.rect(x - 2 - i, ly, x - 1, ly + 1, LEAF)
        p.rect(x + 2, ly, x + 3 + i, ly + 1, LEAF)
        p.dot(x - 2 - i, ly, LEAF_LIGHT)
    if flower:
        fy = y - size * 3 - 3
        p.rect(x - 2, fy - 1, x + 3, fy + 2, PETAL)
        p.dot(x - 3, fy, PETAL); p.dot(x + 4, fy, PETAL); p.dot(x, fy - 2, PETAL); p.dot(x + 1, fy + 3, PETAL)
        p.rect(x, fy, x + 1, fy + 1, POLLEN)


def farm_plot(stage: str) -> Px:
    p = Px(64, 64)
    _soil(p)
    xs = (18, 32, 46)
    if stage == "planted":
        for x in xs:
            p.rect(x - 1, 38, x + 1, 40, SEED); p.dot(x - 1, 38, SEED_LIGHT)
    elif stage == "stage_1":
        for x in xs:
            _plant(p, x, 44, 1, False)
    elif stage == "stage_2":
        for x in xs:
            _plant(p, x, 46, 2, False)
    elif stage == "ready":
        for x in xs:
            _plant(p, x, 48, 3, True)
    p.outline(OUTLINE)
    return p


def icon_moly_seed() -> Px:
    p = Px(32, 32)
    p.ellipse(9, 10, 22, 23, SEED)
    p.ellipse(11, 12, 16, 16, SEED_LIGHT)
    p.rect(16, 6, 17, 11, LEAF_DARK)
    p.rect(18, 7, 21, 9, LEAF)
    p.outline(OUTLINE)
    return p


def icon_moly() -> Px:
    p = Px(32, 32)
    p.rect(15, 16, 16, 27, LEAF_DARK)
    p.rect(10, 22, 14, 24, LEAF); p.rect(17, 19, 21, 21, LEAF)
    p.ellipse(9, 5, 22, 18, PETAL)
    p.dot(15, 3, PETAL); p.dot(16, 3, PETAL); p.dot(7, 11, PETAL); p.dot(24, 11, PETAL)
    p.rect(14, 10, 17, 13, POLLEN)
    p.outline(OUTLINE)
    return p


def icon_calming_draught() -> Px:
    p = Px(32, 32)
    p.rect(13, 4, 18, 9, WOOD_DARK)          # cork
    p.rect(12, 9, 19, 12, GLASS_DARK)        # neck
    p.ellipse(7, 11, 24, 28, GLASS)          # bottle
    p.ellipse(9, 17, 22, 27, LIQUID)         # liquid
    p.dot(10, 14, WHITE); p.dot(11, 13, WHITE)
    p.outline(OUTLINE)
    return p


BERRY = rgb("#3b1f5e")
BERRY_L = rgb("#6a3fa0")
STEM = rgb("#5f8f3a")
SPOT = rgb("#7a2a6a")
BELL = rgb("#b8a0e0")


def herb_card(kind: str) -> Px:
    """64x64 herb portrait for the identification minigame."""
    p = Px(64, 64)
    p.rect(14, 54, 49, 57, SOIL)
    p.hline(14, 49, 54, SOIL_LIGHT)
    if kind == "moly":
        # Black root, milk-white flower (as in Homer and in Miller).
        p.rect(30, 44, 33, 54, SEED)
        p.rect(27, 50, 29, 53, SEED); p.rect(34, 49, 36, 52, SEED)
        p.rect(31, 24, 32, 44, LEAF_DARK)
        p.poly([(31, 38), (20, 34), (22, 40)], LEAF); p.poly([(32, 34), (43, 30), (41, 36)], LEAF)
        p.ellipse(22, 10, 41, 29, PETAL)
        p.dot(31, 7, PETAL); p.dot(32, 7, PETAL); p.dot(19, 19, PETAL); p.dot(44, 19, PETAL)
        p.rect(29, 17, 34, 22, POLLEN)
    elif kind == "nightshade":
        p.rect(31, 20, 32, 54, STEM)
        p.poly([(31, 30), (18, 24), (22, 34)], LEAF_DARK); p.poly([(32, 38), (46, 32), (42, 44)], LEAF_DARK)
        p.poly([(31, 46), (20, 44), (24, 52)], LEAF)
        for (x, y) in ((26, 16), (34, 12), (38, 20), (28, 24), (36, 28)):
            p.ellipse(x - 3, y - 3, x + 3, y + 3, BERRY)
            p.dot(x - 1, y - 1, BERRY_L)
        p.ellipse(22, 6, 30, 12, BELL)
        p.rect(24, 12, 28, 14, BELL)
    elif kind == "hemlock":
        p.rect(31, 14, 32, 54, STEM)
        for y in range(18, 52, 6):
            p.dot(31, y, SPOT)
        p.poly([(31, 40), (16, 36), (20, 46)], LEAF); p.poly([(32, 32), (48, 28), (44, 38)], LEAF)
        for (x, y) in ((22, 12), (31, 8), (40, 12), (26, 18), (36, 18)):
            p.rect(x - 2, y - 1, x + 2, y + 1, PETAL)
            p.dot(x, y - 2, PETAL); p.dot(x, y + 2, PETAL)
            p.vline(x, y + 2, 20, STEM)
        p.rect(28, 20, 35, 22, STEM)
    p.outline(OUTLINE)
    return p


def particle_soft() -> Px:
    """16x16 soft white circle used by the particle emitters (an untextured quad renders black on web)."""
    p = Px(16, 16)
    cx, cy = 7.5, 7.5
    for y in range(16):
        for x in range(16):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / 7.5
            a = max(0.0, 1.0 - d)
            a = a * a
            if a > 0.03:
                p.dot(x, y, (255, 255, 255, int(255 * a)))
    return p


def all_props() -> dict[str, Px]:
    return {
        "sprites/ui/particle_soft.png": particle_soft(),
        "sprites/ui/herb_moly.png": herb_card("moly"),
        "sprites/ui/herb_nightshade.png": herb_card("nightshade"),
        "sprites/ui/herb_hemlock.png": herb_card("hemlock"),
        "sprites/entities/boat.png": boat(),
        "sprites/entities/crafting_table.png": crafting_table(),
        "sprites/entities/sleep_spot.png": sleep_spot(),
        "sprites/entities/farm_plot.png": farm_plot("empty"),
        "sprites/entities/farm_plot_stage_empty.png": farm_plot("empty"),
        "sprites/entities/farm_plot_stage_planted.png": farm_plot("planted"),
        "sprites/entities/farm_plot_stage_1.png": farm_plot("stage_1"),
        "sprites/entities/farm_plot_stage_2.png": farm_plot("stage_2"),
        "sprites/entities/farm_plot_stage_ready.png": farm_plot("ready"),
        "sprites/ui/icon_moly_seed.png": icon_moly_seed(),
        "sprites/ui/icon_moly.png": icon_moly(),
        "sprites/ui/icon_calming_draught.png": icon_calming_draught(),
    }
