"""32-px tile atlases, 16 columns x 8 rows (512x256 each).

Three atlases, all generated here. `worldmap.py` turns a text map into
tile coordinates using the names in TILES, so the game never hard-codes them.

  aiaia_tileset_32.png        opaque terrain for the island
  scylla_cove_tileset_32.png  opaque terrain for the cove
  greek_decor_tileset_32.png  transparent props (fences, trees, house, well, cave, ...)
"""
from __future__ import annotations

import random

from px import OUTLINE, Px, rgb, darken, lighten

T = 32
COLS, ROWS = 16, 8

# --- palette ------------------------------------------------------------
GRASS = rgb("#6aa84f"); GRASS_L = rgb("#86c45f"); GRASS_D = rgb("#528f3d"); GRASS_DD = rgb("#3f7430")
FLOWER = [rgb("#f6f3e7"), rgb("#f2c84b"), rgb("#e07aa8"), rgb("#8fb3ff")]
DIRT = rgb("#a67c52"); DIRT_D = rgb("#7d5a3a"); DIRT_L = rgb("#c49a6c")
SOIL = rgb("#5c3a21"); SOIL_D = rgb("#3e2715"); SOIL_L = rgb("#7a5230")
SAND = rgb("#e2cf9a"); SAND_D = rgb("#c9b27c")
SEA = rgb("#3f7fb5"); SEA_D = rgb("#2f6594"); SEA_L = rgb("#6aa6d6"); FOAM = rgb("#dff1ff")
ROCK = rgb("#4a5461"); ROCK_D = rgb("#333a45"); ROCK_L = rgb("#64707f")
GRAVEL = rgb("#5b5f66"); GRAVEL_D = rgb("#44474d"); GRAVEL_L = rgb("#737881")
DARKSEA = rgb("#1e3550"); DARKSEA_L = rgb("#2d4a6c")
CLIFF = rgb("#8a7a5c"); CLIFF_D = rgb("#5e5240"); CLIFF_L = rgb("#a89a78")
MARBLE = rgb("#d9d6cc"); MARBLE_D = rgb("#b5b1a6"); MARBLE_L = rgb("#f0eee8")
STONE = rgb("#9a9aa6"); STONE_D = rgb("#6c6c78"); STONE_L = rgb("#b9b9c4")
BONE = rgb("#e9e2cf")
WOOD = rgb("#9c6b3c"); WOOD_D = rgb("#5a3d22"); WOOD_L = rgb("#c08a52")
LEAF = rgb("#4f9a3a"); LEAF_D = rgb("#2f6b26"); LEAF_L = rgb("#8ccf5a")
OLIVE = rgb("#6f8f4a"); OLIVE_D = rgb("#4a6a30"); OLIVE_L = rgb("#9bb86a")
CYPRESS = rgb("#2f5d3a"); CYPRESS_D = rgb("#1f4228"); CYPRESS_L = rgb("#4a7d4f")
CLAY = rgb("#b5603a"); CLAY_D = rgb("#7e3f25")
ROOF = rgb("#b5563a"); ROOF_D = rgb("#7d3a26"); ROOF_L = rgb("#d07a5a")
WALL = rgb("#e8dcc4"); WALL_D = rgb("#c4b596"); WALL_L = rgb("#f5efe0")
DOOR = rgb("#5a3d22")
FIRE = rgb("#f2a33a"); FIRE_L = rgb("#ffe08a")
CAVE = rgb("#141820"); CAVE_L = rgb("#232a36")
WEED = rgb("#2e5f4a"); WEED_L = rgb("#3f8362")

# Named tile coordinates (column, row) per atlas. worldmap.py imports this.
TILES: dict[str, dict[str, tuple[int, int]]] = {"aiaia": {}, "cove": {}, "decor": {}}
# Multi-tile props: name -> (atlas, col, row, width_tiles, height_tiles)
PROPS: dict[str, tuple[str, int, int, int, int]] = {}


def _put(atlas: Px, tile: Px, cx: int, cy: int, atlas_name: str | None = None, name: str | None = None) -> None:
    atlas.paste(tile, cx * T, cy * T)
    if atlas_name and name:
        TILES[atlas_name][name] = (cx, cy)


def _speckle(t: Px, rng: random.Random, colors, n: int, base) -> None:
    t.rect(0, 0, T - 1, T - 1, base)
    for _ in range(n):
        x, y = rng.randrange(T), rng.randrange(T)
        c = rng.choice(colors)
        t.rect(x, y, min(T - 1, x + rng.choice((0, 1, 2))), y, c)


# --- ground tiles ---------------------------------------------------------
def grass_tile(seed: int, flowers: int = 0, dark: bool = False) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    base, light, darkc = (GRASS_D, GRASS, GRASS_DD) if dark else (GRASS, GRASS_L, GRASS_D)
    _speckle(t, rng, [light, darkc, light], 26, base)
    for _ in range(rng.randrange(2, 5)):
        x, y = rng.randrange(1, T - 1), rng.randrange(2, T - 1)
        t.vline(x, y - 2, y, darkc); t.dot(x + 1, y - 1, light)
    for _ in range(flowers):
        x, y = rng.randrange(2, T - 3), rng.randrange(2, T - 3)
        c = rng.choice(FLOWER)
        t.dot(x, y, c); t.dot(x + 1, y, c); t.dot(x, y + 1, c); t.dot(x + 1, y + 1, c)
        t.dot(x + 1, y + 2, LEAF_D)
    return t


def dirt_tile(seed: int, furrows: bool = False) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    if furrows:
        _speckle(t, rng, [SOIL_L, SOIL_D], 16, SOIL)
        for y in (6, 14, 22, 30):
            t.hline(0, T - 1, y, SOIL_D); t.hline(0, T - 1, y + 1, SOIL_L)
    else:
        _speckle(t, rng, [DIRT_L, DIRT_D], 20, DIRT)
    return t


def path_edge_tile(seed: int, side: str) -> Px:
    """Dirt path with a grassy edge on one side."""
    t = dirt_tile(seed)
    g = grass_tile(seed + 50)
    if side == "left":
        t.im.paste(g.im.crop((0, 0, 6, T)), (0, 0))
        for y in range(0, T, 2):
            t.dot(6 + (y % 3), y, GRASS_D)
    elif side == "right":
        t.im.paste(g.im.crop((T - 6, 0, T, T)), (T - 6, 0))
        for y in range(0, T, 2):
            t.dot(T - 7 - (y % 3), y, GRASS_D)
    return t


def sand_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    _speckle(t, rng, [SAND_D, lighten(SAND, 1.05)], 18, SAND)
    return t


def sea_tile(seed: int, base=SEA, light=SEA_L, dark=SEA_D) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    t.rect(0, 0, T - 1, T - 1, base)
    for i in range(4):
        y = 4 + i * 8 + rng.randrange(0, 3)
        x = rng.randrange(0, 12)
        t.hline(x, x + 8 + rng.randrange(0, 8), y, light)
        t.hline(x + 3, x + 6, y + 1, dark)
    return t


def foam_tile(seed: int, side: str, base=SEA, light=SEA_L, dark=SEA_D, land=SAND) -> Px:
    """Water tile with a foam line on the side that touches land."""
    rng = random.Random(seed)
    t = sea_tile(seed, base, light, dark)
    for i in range(T):
        f = rng.random()
        if side == "top":
            t.dot(i, 0, land if f < 0.25 else FOAM); t.dot(i, 1, FOAM if f < 0.7 else light)
            if f < 0.3: t.dot(i, 2, FOAM)
        elif side == "bottom":
            t.dot(i, T - 1, land if f < 0.25 else FOAM); t.dot(i, T - 2, FOAM if f < 0.7 else light)
            if f < 0.3: t.dot(i, T - 3, FOAM)
        elif side == "left":
            t.dot(0, i, land if f < 0.25 else FOAM); t.dot(1, i, FOAM if f < 0.7 else light)
            if f < 0.3: t.dot(2, i, FOAM)
        elif side == "right":
            t.dot(T - 1, i, land if f < 0.25 else FOAM); t.dot(T - 2, i, FOAM if f < 0.7 else light)
            if f < 0.3: t.dot(T - 3, i, FOAM)
    return t


def rock_tile(seed: int, base=ROCK, light=ROCK_L, dark=ROCK_D) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    _speckle(t, rng, [light, dark], 22, base)
    for _ in range(rng.randrange(2, 4)):
        x, y = rng.randrange(2, T - 6), rng.randrange(2, T - 6)
        for i in range(rng.randrange(3, 7)):
            t.dot(x + i, y + (i // 2), dark)
    if rng.random() < 0.5:
        x, y = rng.randrange(2, T - 5), rng.randrange(2, T - 5)
        t.rect(x, y, x + 3, y + 2, light); t.hline(x, x + 3, y + 2, dark)
    return t


def cliff_top_tile(seed: int, grass_above: bool = True) -> Px:
    """Top half grass (or rock), bottom half the lit lip of a cliff."""
    t = grass_tile(seed) if grass_above else rock_tile(seed)
    t.rect(0, 18, T - 1, T - 1, CLIFF)
    t.hline(0, T - 1, 18, CLIFF_L); t.hline(0, T - 1, 19, CLIFF_L)
    rng = random.Random(seed)
    for x in range(0, T, 4):
        t.vline(x + rng.randrange(0, 3), 21, 21 + rng.randrange(3, 9), CLIFF_D)
    t.hline(0, T - 1, T - 1, CLIFF_D)
    return t


def cliff_face_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    _speckle(t, rng, [CLIFF_L, CLIFF_D], 14, CLIFF)
    for y in range(3, T, 9):
        t.hline(0, T - 1, y + rng.randrange(0, 2), CLIFF_D)
        for x in range(rng.randrange(0, 8), T, 9):
            t.vline(x, y, y + 6, CLIFF_D)
    return t


def marble_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    t.rect(0, 0, T - 1, T - 1, MARBLE)
    t.hline(0, T - 1, 0, MARBLE_L); t.vline(0, 0, T - 1, MARBLE_L)
    t.hline(0, T - 1, T - 1, MARBLE_D); t.vline(T - 1, 0, T - 1, MARBLE_D)
    t.hline(0, T - 1, 15, MARBLE_D); t.hline(0, T - 1, 16, MARBLE_L)
    off = rng.randrange(4, 28)
    t.vline(off, 0, 15, MARBLE_D); t.vline((off + 14) % 30 + 1, 17, T - 1, MARBLE_D)
    for _ in range(4):
        t.dot(rng.randrange(T), rng.randrange(T), MARBLE_D)
    return t


def stone_floor_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    t.rect(0, 0, T - 1, T - 1, STONE)
    for (x0, y0, x1, y1) in ((0, 0, 14, 10), (16, 0, 31, 10), (0, 12, 9, 20), (11, 12, 31, 20), (0, 22, 20, 31), (22, 22, 31, 31)):
        t.rect(x0, y0, x1, y1, STONE if rng.random() < 0.7 else STONE_L)
        t.hline(x0, x1, y1, STONE_D); t.vline(x1, y0, y1, STONE_D)
    return t


def gravel_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    _speckle(t, rng, [GRAVEL_L, GRAVEL_D, GRAVEL_L], 30, GRAVEL)
    return t


def cave_floor_tile(seed: int) -> Px:
    """Scorched, darker rock in front of the cave mouth (not pitch black)."""
    return rock_tile(seed, base=darken(ROCK, 0.72), light=darken(ROCK_L, 0.72), dark=darken(ROCK_D, 0.72))


def plank_tile(seed: int, vertical: bool = True) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    t.rect(0, 0, T - 1, T - 1, WOOD)
    step = 8
    for i in range(0, T, step):
        if vertical:
            t.vline(i, 0, T - 1, WOOD_D); t.vline(i + 1, 0, T - 1, WOOD_L)
        else:
            t.hline(0, T - 1, i, WOOD_D); t.hline(0, T - 1, i + 1, WOOD_L)
    for _ in range(3):
        t.dot(rng.randrange(T), rng.randrange(T), WOOD_D)
    return t


# --- props (transparent) ----------------------------------------------------
def fence_tile(kind: str) -> Px:
    """One fence tile. 'h' and 'v' are runs, 'tl'..'br' corners, 'end_l' / 'end_r' the last tile of
    a horizontal run (rails stop at the post instead of running on into the grass)."""
    t = Px(T, T)
    if kind in ("h", "tl", "tr", "bl", "br", "end_l", "end_r"):
        x0 = 14 if kind in ("tl", "bl", "end_l") else 0
        x1 = 17 if kind in ("tr", "br", "end_r") else T - 1
        t.rect(x0, 10, x1, 12, WOOD_L); t.rect(x0, 20, x1, 22, WOOD_L)
    if kind in ("v", "tl", "tr", "bl", "br"):
        y0 = 10 if kind in ("tl", "tr") else 0
        y1 = 22 if kind in ("bl", "br") else T - 1
        t.rect(14, y0, 17, y1, WOOD)
    # Every tile has a post, the side runs included, so a side fence reads as posts and a rail.
    if kind in ("post", "tl", "tr", "bl", "br", "h", "v", "end_l", "end_r"):
        t.rect(13, 6, 18, 27, WOOD); t.rect(13, 6, 18, 8, WOOD_L)
    t.outline(OUTLINE)
    return t


def flower_bed_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    t.rect(3, 6, 28, 28, SOIL)
    t.rect(3, 6, 28, 8, SOIL_L)
    for _ in range(9):
        x, y = rng.randrange(5, 25), rng.randrange(9, 25)
        c = rng.choice(FLOWER)
        t.rect(x, y, x + 2, y + 2, c); t.dot(x + 1, y + 1, lighten(c, 1.15)); t.dot(x + 1, y + 3, LEAF_D)
    t.outline(OUTLINE)
    return t


def bush_tile(seed: int, olive: bool = False) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    t.ellipse(4, 10, 27, 29, LEAF_D)
    t.ellipse(7, 6, 24, 24, LEAF)
    for _ in range(8):
        t.dot(rng.randrange(8, 23), rng.randrange(8, 22), LEAF_L)
    if olive:
        for _ in range(3):
            t.dot(rng.randrange(8, 23), rng.randrange(10, 24), rgb("#2b2b2b"))
    t.outline(OUTLINE)
    return t


def rock_prop_tile(dark: bool = False) -> Px:
    t = Px(T, T)
    base, light, darkc = (ROCK_D, ROCK, darken(ROCK_D, 0.7)) if dark else (STONE, STONE_L, STONE_D)
    t.ellipse(4, 12, 27, 29, darkc)
    t.ellipse(6, 9, 25, 25, base)
    t.ellipse(9, 11, 16, 16, light)
    t.outline(OUTLINE)
    return t


def amphora_tile() -> Px:
    t = Px(T, T)
    t.ellipse(9, 8, 22, 26, CLAY)
    t.rect(12, 3, 19, 8, CLAY); t.rect(11, 2, 20, 3, CLAY_D)
    t.rect(8, 10, 9, 16, CLAY_D); t.rect(22, 10, 23, 16, CLAY_D)
    t.rect(12, 26, 19, 29, CLAY_D)
    t.hline(11, 20, 15, CLAY_D); t.hline(11, 20, 12, lighten(CLAY, 1.15))
    t.outline(OUTLINE)
    return t


def column_tile(broken: bool) -> Px:
    t = Px(T, T)
    top = 10 if broken else 2
    t.rect(11, top, 20, 29, MARBLE)
    t.vline(12, top, 29, MARBLE_L); t.vline(19, top, 29, MARBLE_D); t.vline(16, top, 29, MARBLE_D)
    t.rect(8, 27, 23, 30, MARBLE_D); t.hline(8, 23, 27, MARBLE_L)
    if broken:
        t.poly([(11, top), (14, top - 4), (17, top + 2), (20, top - 2), (20, top)], MARBLE)
    else:
        t.rect(8, 2, 23, 5, MARBLE_L); t.hline(8, 23, 5, MARBLE_D)
    t.outline(OUTLINE)
    return t


def herb_pot_tile() -> Px:
    t = Px(T, T)
    t.rect(10, 18, 21, 28, CLAY); t.rect(9, 16, 22, 18, CLAY_D)
    t.rect(14, 8, 16, 17, LEAF_D)
    t.rect(10, 10, 13, 12, LEAF); t.rect(17, 7, 21, 9, LEAF); t.rect(12, 5, 15, 7, LEAF_L)
    t.outline(OUTLINE)
    return t


def crate_tile() -> Px:
    t = Px(T, T)
    t.rect(6, 8, 25, 27, WOOD)
    t.rect(6, 8, 25, 10, WOOD_L); t.rect(6, 25, 25, 27, WOOD_D)
    t.vline(6, 8, 27, WOOD_D); t.vline(25, 8, 27, WOOD_D)
    t.hline(6, 25, 17, WOOD_D)
    t.outline(OUTLINE)
    return t


def torch_tile() -> Px:
    t = Px(T, T)
    t.rect(14, 12, 17, 29, WOOD_D)
    t.rect(12, 10, 19, 13, WOOD)
    t.ellipse(11, 2, 20, 11, FIRE); t.ellipse(13, 4, 18, 9, FIRE_L)
    t.outline(OUTLINE)
    return t


def signpost_tile() -> Px:
    t = Px(T, T)
    t.rect(14, 6, 17, 29, WOOD_D)
    t.rect(6, 7, 25, 15, WOOD_L); t.hline(6, 25, 15, WOOD_D)
    t.hline(9, 22, 10, WOOD_D); t.hline(9, 18, 12, WOOD_D)
    t.outline(OUTLINE)
    return t


def dock_post_tile() -> Px:
    t = Px(T, T)
    t.rect(13, 4, 18, 29, WOOD_D); t.rect(13, 4, 18, 6, WOOD_L)
    t.rect(12, 26, 19, 29, darken(WOOD_D, 0.8))
    t.outline(OUTLINE)
    return t


def seaweed_tile(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T)
    for x in (8, 14, 20, 25):
        h = rng.randrange(8, 18)
        for i in range(h):
            t.dot(x + (1 if (i // 3) % 2 else 0), 29 - i, WEED if i % 4 else WEED_L)
    t.outline(OUTLINE)
    return t


def bones_tile() -> Px:
    t = Px(T, T)
    t.ellipse(8, 8, 21, 20, BONE)
    t.rect(11, 20, 18, 24, BONE)
    t.rect(11, 13, 13, 15, OUTLINE); t.rect(16, 13, 18, 15, OUTLINE)
    t.dot(14, 17, OUTLINE); t.dot(15, 17, OUTLINE)
    t.rect(2, 26, 29, 28, BONE); t.rect(1, 25, 4, 29, BONE); t.rect(27, 25, 30, 29, BONE)
    t.outline(OUTLINE)
    return t


def stump_tile() -> Px:
    t = Px(T, T)
    t.rect(10, 6, 21, 27, WOOD_D)
    t.rect(6, 24, 25, 29, WOOD_D)
    t.rect(10, 6, 21, 9, rgb("#8a6238"))
    t.rect(14, 0, 17, 8, WOOD_D); t.rect(19, 2, 24, 4, WOOD_D)
    t.outline(OUTLINE)
    return t


def wreck_prop(w: int = 2) -> Px:
    t = Px(T * w, T)
    t.poly([(4, 28), (14, 8), (19, 10), (10, 29)], WOOD_D)
    t.poly([(16, 29), (40, 12), (45, 16), (26, 30)], rgb("#8a6238"))
    t.rect(22, 4, 24, 18, WOOD_D)
    t.rect(46, 20, 60, 29, WOOD_D); t.hline(46, 60, 22, rgb("#8a6238"))
    t.outline(OUTLINE)
    return t


def big_rock_prop(seed: int, dark: bool = False) -> Px:
    rng = random.Random(seed)
    t = Px(T * 2, T)
    base, light, darkc = (ROCK_D, ROCK, darken(ROCK_D, 0.7)) if dark else (STONE, STONE_L, STONE_D)
    t.ellipse(2, 10, 61, 30, darkc)
    t.ellipse(4, 4, 58, 26, base)
    t.ellipse(10, 7, 26, 15, light)
    for _ in range(5):
        t.dot(rng.randrange(8, 56), rng.randrange(8, 26), darkc)
    t.outline(OUTLINE)
    return t


def house_prop() -> Px:
    """Circe's house, 4 x 3 tiles (128 x 96): tiled roof, cream stone walls, door, window, ivy."""
    t = Px(T * 4, T * 3)
    # Walls
    t.rect(10, 44, 117, 92, WALL)
    t.rect(10, 44, 117, 46, WALL_L)
    for y in range(50, 92, 10):
        t.hline(12, 115, y, WALL_D)
        for x in range(12 + (y // 10 % 2) * 8, 115, 16):
            t.vline(x, y - 9, y - 1, WALL_D)
    # Roof
    t.poly([(2, 46), (64, 6), (125, 46)], ROOF)
    t.poly([(2, 46), (64, 6), (125, 46), (125, 50), (2, 50)], ROOF)
    for y in range(14, 50, 7):
        t.hline(2 + max(0, int((46 - y) * 1.55)), 125 - max(0, int((46 - y) * 1.55)), y, ROOF_D)
        for x in range(6 + (y % 14 == 0) * 6, 122, 12):
            if 2 + (46 - y) * 1.55 < x < 125 - (46 - y) * 1.55:
                t.vline(x, y - 6, y - 1, ROOF_D)
    t.hline(2, 125, 50, ROOF_D)
    t.rect(0, 48, 127, 51, ROOF_D)
    # Door and step
    t.rect(54, 66, 73, 92, DOOR); t.rect(56, 68, 71, 90, lighten(DOOR, 1.25)); t.dot(69, 80, FIRE_L)
    t.rect(50, 92, 77, 95, STONE_D)
    # Windows
    for x in (22, 94):
        t.rect(x, 60, x + 13, 73, SEA_D); t.rect(x + 1, 61, x + 12, 72, SEA_L)
        t.hline(x, x + 13, 66, WOOD_D); t.vline(x + 6, 60, 73, WOOD_D)
        t.rect(x - 1, 74, x + 14, 76, WOOD)
    # Ivy on the left wall, herb pots by the door
    for (x, y) in ((12, 52), (14, 58), (11, 64), (15, 70), (13, 78), (12, 86)):
        t.rect(x, y, x + 3, y + 3, LEAF); t.dot(x + 1, y + 1, LEAF_L)
    t.rect(40, 84, 47, 92, CLAY); t.rect(41, 78, 46, 84, LEAF)
    t.rect(80, 84, 87, 92, CLAY); t.rect(81, 78, 86, 84, LEAF)
    t.outline(OUTLINE)
    return t


def olive_tree_prop(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T * 2, T * 2)
    t.rect(28, 40, 35, 60, WOOD_D); t.rect(24, 52, 39, 60, WOOD_D)
    t.rect(30, 40, 31, 58, WOOD)
    t.ellipse(4, 6, 59, 46, OLIVE_D)
    t.ellipse(8, 2, 55, 38, OLIVE)
    t.ellipse(14, 4, 40, 24, OLIVE_L)
    for _ in range(18):
        t.dot(rng.randrange(8, 56), rng.randrange(6, 42), OLIVE_D if rng.random() < 0.6 else OLIVE_L)
    for _ in range(6):
        t.dot(rng.randrange(10, 52), rng.randrange(10, 40), rgb("#2b2b2b"))
    t.outline(OUTLINE)
    return t


def cypress_prop(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T, T * 3)
    t.rect(14, 80, 17, 94, WOOD_D)
    t.poly([(15, 2), (28, 60), (26, 84), (5, 84), (3, 60)], CYPRESS_D)
    t.poly([(15, 6), (24, 58), (22, 80), (8, 80), (7, 58)], CYPRESS)
    for _ in range(14):
        t.dot(rng.randrange(8, 23), rng.randrange(10, 78), CYPRESS_L)
    t.outline(OUTLINE)
    return t


def dead_tree_prop() -> Px:
    t = Px(T * 2, T * 3)
    t.rect(28, 40, 35, 92, WOOD_D); t.rect(24, 86, 39, 92, WOOD_D)
    t.poly([(30, 44), (12, 20), (16, 18), (32, 38)], WOOD_D)
    t.poly([(33, 50), (54, 26), (57, 29), (35, 54)], WOOD_D)
    t.poly([(31, 36), (24, 6), (28, 5), (34, 34)], WOOD_D)
    t.rect(10, 16, 13, 20, WOOD_D); t.rect(54, 22, 58, 26, WOOD_D)
    t.outline(OUTLINE)
    return t


def well_prop() -> Px:
    t = Px(T * 2, T * 2)
    t.ellipse(10, 34, 53, 60, STONE_D)
    t.ellipse(12, 30, 51, 54, STONE)
    t.ellipse(20, 36, 43, 50, CAVE)
    t.ellipse(24, 40, 39, 48, SEA_D)
    t.rect(14, 10, 17, 40, WOOD_D); t.rect(46, 10, 49, 40, WOOD_D)
    t.poly([(10, 14), (32, 2), (54, 14), (54, 18), (10, 18)], ROOF); t.hline(10, 54, 18, ROOF_D)
    t.rect(17, 22, 46, 24, WOOD); t.rect(28, 24, 35, 30, WOOD_D)
    for x in range(12, 52, 8):
        t.vline(x, 32, 52, STONE_D)
    t.outline(OUTLINE)
    return t


def cave_prop() -> Px:
    """Cave mouth in dark rock, 3 x 2 tiles."""
    t = Px(T * 3, T * 2)
    t.ellipse(2, 6, 93, 70, ROCK_D)
    t.ellipse(6, 2, 89, 62, ROCK)
    t.ellipse(14, 10, 40, 30, ROCK_L)
    t.ellipse(26, 22, 69, 76, CAVE)
    t.ellipse(30, 26, 65, 64, CAVE_L) if False else None
    t.rect(26, 50, 69, 63, CAVE)
    for x in range(30, 66, 6):
        t.poly([(x, 24), (x + 2, 34), (x + 4, 24)], ROCK_D)
    t.dot(44, 52, FIRE); t.dot(52, 52, FIRE)
    t.outline(OUTLINE)
    return t


def dark_boulder_prop(seed: int) -> Px:
    rng = random.Random(seed)
    t = Px(T * 2, T * 2)
    t.ellipse(2, 14, 61, 62, darken(ROCK_D, 0.7))
    t.ellipse(4, 6, 59, 56, ROCK_D)
    t.ellipse(12, 10, 36, 30, ROCK)
    for _ in range(6):
        t.dot(rng.randrange(8, 56), rng.randrange(12, 54), darken(ROCK_D, 0.7))
    t.outline(OUTLINE)
    return t


# --- atlases ----------------------------------------------------------------
def aiaia_atlas() -> Px:
    a = Px(COLS * T, ROWS * T)
    n = "aiaia"
    for cy in range(ROWS):
        for cx in range(COLS):
            _put(a, grass_tile(cy * 100 + cx), cx, cy)
    # row 0: sea and foam edges
    for i in range(4):
        _put(a, sea_tile(i), i, 0, n, f"sea{i}")
    _put(a, foam_tile(10, "top"), 4, 0, n, "foam_top")
    _put(a, foam_tile(11, "bottom"), 5, 0, n, "foam_bottom")
    _put(a, foam_tile(12, "left"), 6, 0, n, "foam_left")
    _put(a, foam_tile(13, "right"), 7, 0, n, "foam_right")
    for i in range(4):
        _put(a, sand_tile(20 + i), 8 + i, 0, n, f"sand{i}")
    # row 1: dirt paths and edges, stone floor
    for i in range(4):
        _put(a, dirt_tile(30 + i), i, 1, n, f"dirt{i}")
    _put(a, path_edge_tile(34, "left"), 4, 1, n, "path_l")
    _put(a, path_edge_tile(35, "right"), 5, 1, n, "path_r")
    for i in range(4):
        _put(a, stone_floor_tile(40 + i), 6 + i, 1, n, f"stone{i}")
    for i in range(4):
        _put(a, marble_tile(50 + i), 10 + i, 1, n, f"marble{i}")
    _put(a, plank_tile(60, True), 14, 1, n, "plank_v")
    _put(a, plank_tile(61, False), 15, 1, n, "plank_h")
    # row 2: grass variants, flowers, dark grass
    _put(a, grass_tile(200), 0, 2, n, "grass0")
    _put(a, grass_tile(201), 1, 2, n, "grass1")
    _put(a, grass_tile(202, flowers=1), 2, 2, n, "grass_f1")
    _put(a, grass_tile(203), 3, 2, n, "grass2")
    _put(a, grass_tile(204, flowers=2), 4, 2, n, "grass_f2")
    _put(a, grass_tile(205, flowers=1), 5, 2, n, "grass_f3")
    _put(a, grass_tile(206, dark=True), 6, 2, n, "dgrass0")
    _put(a, grass_tile(207, dark=True), 7, 2, n, "dgrass1")
    for i in range(4):
        _put(a, dirt_tile(300 + i, furrows=True), 8 + i, 2, n, f"soil{i}")
    # row 3: cliffs
    for i in range(4):
        _put(a, cliff_top_tile(400 + i), i, 3, n, f"cliff_top{i}")
        _put(a, cliff_face_tile(410 + i), 4 + i, 3, n, f"cliff_face{i}")
    return a


def cove_atlas() -> Px:
    a = Px(COLS * T, ROWS * T)
    n = "cove"
    dk = (DARKSEA, DARKSEA_L, darken(DARKSEA, 0.8))
    for cy in range(ROWS):
        for cx in range(COLS):
            _put(a, rock_tile(cy * 100 + cx + 7), cx, cy)
    for i in range(4):
        _put(a, sea_tile(40 + i, *dk), i, 0, n, f"sea{i}")
    _put(a, foam_tile(44, "top", *dk, land=GRAVEL), 4, 0, n, "foam_top")
    _put(a, foam_tile(45, "bottom", *dk, land=GRAVEL), 5, 0, n, "foam_bottom")
    _put(a, foam_tile(46, "left", *dk, land=GRAVEL), 6, 0, n, "foam_left")
    _put(a, foam_tile(47, "right", *dk, land=GRAVEL), 7, 0, n, "foam_right")
    for i in range(4):
        _put(a, gravel_tile(50 + i), 8 + i, 0, n, f"gravel{i}")
    for i in range(4):
        _put(a, cave_floor_tile(60 + i), 12 + i, 0, n, f"cave{i}")
    for i in range(8):
        _put(a, rock_tile(70 + i), i, 1, n, f"rock{i}")
    for i in range(4):
        _put(a, cliff_top_tile(80 + i, grass_above=False), 8 + i, 1, n, f"cliff_top{i}")
        _put(a, cliff_face_tile(90 + i), 12 + i, 1, n, f"cliff_face{i}")
    _put(a, plank_tile(62, True), 0, 2, n, "plank_v")
    _put(a, plank_tile(63, False), 1, 2, n, "plank_h")
    return a


def decor_atlas() -> Px:
    a = Px(COLS * T, ROWS * T)
    n = "decor"
    # row 0: fences, beds, small props
    for i, kind in enumerate(("h", "v", "post", "tl", "tr", "bl", "br")):
        _put(a, fence_tile(kind), i, 0, n, f"fence_{kind}")
    _put(a, flower_bed_tile(1), 7, 0, n, "bed0")
    _put(a, flower_bed_tile(2), 8, 0, n, "bed1")
    _put(a, bush_tile(3), 9, 0, n, "bush0")
    _put(a, bush_tile(4, olive=True), 10, 0, n, "bush1")
    _put(a, rock_prop_tile(), 11, 0, n, "rock_s")
    _put(a, rock_prop_tile(dark=True), 12, 0, n, "rock_sd")
    _put(a, amphora_tile(), 13, 0, n, "amphora")
    _put(a, column_tile(False), 14, 0, n, "column")
    _put(a, column_tile(True), 15, 0, n, "column_b")
    # row 1
    _put(a, herb_pot_tile(), 0, 1, n, "herb_pot")
    _put(a, crate_tile(), 1, 1, n, "crate")
    _put(a, torch_tile(), 2, 1, n, "torch")
    _put(a, signpost_tile(), 3, 1, n, "sign")
    _put(a, dock_post_tile(), 4, 1, n, "dock_post")
    _put(a, seaweed_tile(7), 5, 1, n, "seaweed0")
    _put(a, seaweed_tile(8), 6, 1, n, "seaweed1")
    _put(a, bones_tile(), 7, 1, n, "bones")
    _put(a, stump_tile(), 8, 1, n, "stump")
    # multi-tile props
    def prop(px: Px, name: str, cx: int, cy: int) -> None:
        a.paste(px, cx * T, cy * T)
        PROPS[name] = ("decor", cx, cy, px.w // T, px.h // T)

    prop(wreck_prop(), "wreck", 9, 1)
    prop(big_rock_prop(9), "big_rock", 11, 1)
    prop(big_rock_prop(10, dark=True), "big_rock_d", 13, 1)
    prop(house_prop(), "house", 0, 2)
    prop(olive_tree_prop(11), "olive", 4, 2)
    prop(olive_tree_prop(12), "olive2", 4, 4)
    prop(cypress_prop(13), "cypress", 6, 2)
    prop(well_prop(), "well", 7, 2)
    prop(cave_prop(), "cave", 9, 2)
    prop(dark_boulder_prop(14), "boulder_d", 12, 2)
    prop(dead_tree_prop(), "dead_tree", 14, 2)
    prop(cypress_prop(15), "cypress2", 6, 5)
    return a


def all_tiles() -> dict[str, Px]:
    return {
        "tilesets/aiaia_tileset_32.png": aiaia_atlas(),
        "tilesets/scylla_cove_tileset_32.png": cove_atlas(),
        "tilesets/greek_decor_tileset_32.png": decor_atlas(),
    }
