"""Static props (64x64, boat 128x64) and 32x32 inventory icons."""
from __future__ import annotations

from px import OUTLINE, WHITE, Px, rgb, darken, lighten
import herbs
import garden

WOOD = rgb("#9c6b3c")
WOOD_DARK = rgb("#6e4826")
WOOD_LIGHT = rgb("#c08a52")
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
        "sprites/ui/herb_moly.png": herbs.herb_card("moly"),
        "sprites/ui/herb_nightshade.png": herbs.herb_card("nightshade"),
        "sprites/ui/herb_hemlock.png": herbs.herb_card("hemlock"),
        "sprites/entities/boat.png": boat(),
        "sprites/entities/crafting_table.png": crafting_table(),
        "sprites/entities/sleep_spot.png": sleep_spot(),
        "sprites/entities/farm_plot.png": garden.plot("empty"),
        "sprites/entities/farm_plot_stage_empty.png": garden.plot("empty"),
        "sprites/entities/farm_plot_stage_planted.png": garden.plot("planted"),
        "sprites/entities/farm_plot_stage_1.png": garden.plot("stage_1"),
        "sprites/entities/farm_plot_stage_2.png": garden.plot("stage_2"),
        "sprites/entities/farm_plot_stage_ready.png": garden.plot("ready"),
        "sprites/ui/icon_moly_seed.png": icon_moly_seed(),
        "sprites/ui/icon_moly.png": icon_moly(),
        "sprites/ui/icon_calming_draught.png": icon_calming_draught(),
    }
