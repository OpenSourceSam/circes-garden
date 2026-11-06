"""Authored tile maps for Aiaia and Scylla's cove, resolved against the LPC-based atlases.

Text maps below become two ground layers (base fills + autotiled overlays with LPC edge
sets), a decor list (props and small objects) and collision rectangles, written to
game/data/world_map.gd, which world.gd reads at runtime. A 1x preview of each map goes to
tools/pixelart/preview/map_<zone>.png.

Grid: 32-px tiles, 17 columns (544 px; the camera shows 540). Rows are world rows:
Aiaia rows 0-46 (y 0-1504), open sea 47-61, the cove rows 62-109.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image  # noqa: E402

import lpc_tiles as tiles  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT_GD = REPO / "game/data/world_map.gd"
PREVIEW = Path(__file__).parent / "preview"
T = 32
W = 17
ATLAS_INDEX = {"aiaia": 0, "cove": 1, "decor": 2}
COVE_ROW0 = 62

# ---------------------------------------------------------------------------
# Ground legend (island): base is always grass.
#   g grass   G grass with flowers   S sand (overlay)   ~ sea (overlay)   p dirt path (overlay)
#   m marble  M mosaic   s cobble floor   t tilled soil   P pier planks
# Ground legend (cove): base is always grey stone.
#   r stone   d dark stone   R gravel (overlay)   ~ dark sea (overlay)   v cave floor (overlay)   P planks
AIAIA = """
~~~~~~~~~~~~~~~~~
~ggggggggggggggg~
~ggggggggggggggg~
~ggggggggggggggg~
~ggggggmmmgggggg~
~gggggGmMmGggggg~
~ggggggmmmgggggg~
~gggggGmMmGggggg~
~ggggggmmmgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggttttppptttggg~
~ggttttppptttggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~ggggggpppgggggg~
~gSSSSSPPPSSSSSg~
~~~~~~~PPP~~~~~~~
~~~~~~~PPP~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
"""

# Decor layer (same grid). 'F' fence (shape from neighbours), 'b' flower bed, 'B' bush,
# 'O' olive bush, 'A' amphora, 'h' herb pot, 'k' crate, 'T' torch, 'n' sign, 'o' dock post,
# 'q' / 'Q' dock post against a pier on its right / left, 'u' stump, 'w' seaweed, 'x' bones, '.' nothing.  Multi-tile props go in the PROPS lists.
AIAIA_DECOR = """
.................
.................
.................
.................
.................
.................
.................
.................
......A..........
.................
.................
.................
.................
.................
.................
.................
..FFFFF...FFFFF..
..F...........F..
..F...........F..
..F...........F..
..F...........F..
..FFFFF...FFFFF..
.................
...........FFFFF.
...........F...F.
......k...TF...F.
...........FFFFF.
.................
.................
..........n......
.................
......q...Q......
.................
......q...Q......
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
"""

# Multi-tile props on Aiaia: (prop name, col, row of the TOP-LEFT tile)
AIAIA_PROPS = [
    # tools/pixelart/check_placement.py checks that no two footprints, shadows or trunks collide.
    ("house", 1, 1), ("cypress2", 12, 1),
    # Two whole columns stand at the back of Hermes' terrace (the broken stubs read as cropped).
    ("column2", 7, 1), ("column2", 9, 1),
    ("olive", 12, 6), ("olive2", 1, 8), ("round_tree", 13, 10),
    ("well", 11, 12), ("olive3", 1, 12), ("shrub", 14, 14), ("shrub2", 2, 22),
    ("big_rock", 4, 9), ("olive", 1, 25), ("olive2", 13, 27), ("rock_s", 5, 28),
]

# Scylla's strait. North to south: the cliff top (rows 62-64), the strait under the cliff face
# (cove_scene.py draws the face, the whirlpool and the mist over rows 64-73), open water, a
# point of rock where Circe faces Scylla (row 78), the shore, and the pier at the south end
# where the boat lands. Circe walks north to the point, so she is always in front of Scylla.
COVE = """
ddddddddddddddddd
ddddddddddddddddd
ddddddddddddddddd
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~rrr~~~~~~~
~~~~~rrrrrrr~~~~~
~~~rrrrrrrrrrr~~~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~~rrrrrrrrrrrrrr~
~~rrRRRRRRRRRrr~~
~~~RRRRRRRRRRR~~~
~~~~RRRPPPRRR~~~~
~~~~~~~PPP~~~~~~~
~~~~~~~PPP~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
"""

# 'w' seaweed, 'x' bones, 'o' dock post, 'T' torch
COVE_DECOR = """
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
....w............
...........w.....
.....x...........
............x....
..w..............
........x........
.................
.............w...
...x.............
.................
......o...o......
.................
......o...o......
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
.................
"""
# The low rock in the water right of the point is the one Scylla strikes (scylla.gd STRIKE_AT).
COVE_PROPS = [
    ("rock_sd", 10, 76), ("spire_d", 13, 78), ("spire_d", 2, 79),
    ("big_rock_d", 1, 82), ("dead_tree", 13, 81), ("wreck", 11, 85), ("rock_sd", 3, 86),
]

BLOCKING_GROUND = {"~"}
SLAB = {"m", "M"}
# Neighbours that count as the same terrain when choosing an overlay's edge: the dirt path runs
# straight onto the pier and the terrace (it passes between the two farm beds, each with its own edge); the beach runs into the sea and up to the
# pier; the sea runs on under the pier, so the pier stands in the water instead of on a spit of land.
JOINS = {"p": ("P", "m", "M"), "S": ("P",), "~": ("P",)}
# Joins that hold only toward the row below: the beach runs down into the sea, but its two ends keep
# a ragged edge against the side coasts (joined on all sides it ended in a straight vertical line).
JOINS_BELOW = {"S": ("~",)}
BLOCKING_DECOR = {"F", "b", "B", "O", "A", "h", "k", "T", "n", "o", "q", "Q", "u"}
# Props and small objects that get a soft ground shadow in the game (half width, half height in px);
# trees, rocks and the house have shadows in their own art.
SHADOWS = {"column2": (15, 4), "well": (26, 6), "amphora5": (9, 3), "amphora4": (10, 3), "crate": (14, 4),
           "torch": (7, 2), "sign": (10, 3), "herb_pot": (9, 3), "rock_s": (22, 5)}
TREE_PROPS = ("olive", "olive2", "olive3", "round_tree", "big_tree", "cypress", "cypress2", "dead_tree")

OVERLAYS = {"aiaia": {"S": "sand", "~": "sea", "p": "dirt", "t": "soil"}, "cove": {"R": "gravel", "~": "dsea", "v": "cave"}}
FILLS = {
    "aiaia": {"g": ["grass0", "grass1", "grass2", "grass3"], "G": ["grassf0", "grassf1", "grassf2", "grassf3"],
              "m": ["marble0", "marble1", "marble2", "marble3"], "M": ["mosaic0", "mosaic1", "mosaic2", "mosaic3"],
              "s": ["cobble_f0", "cobble_c"], "t": ["grass0", "grass1", "grass2", "grass3"], "P": ["plank_v"],
              "S": ["grass0", "grass1"], "~": ["grass0"], "p": ["grass0", "grass1", "grass2"]},
    "cove": {"r": ["rock0", "rock1", "rock2", "rock3"], "d": ["rockd0", "rockd1", "rockd2", "rockd3"],
             "R": ["rock0", "rock1"], "~": ["rock0"], "v": ["rock0"], "P": ["plank_v"]},
}


def encode(cell) -> int:
    """Cell value for world_map.gd: atlas_index * 10000 + ty * 100 + tx, or -1."""
    if cell is None:
        return -1
    ai, tx, ty = cell
    return ai * 10000 + ty * 100 + tx


def _rows(text: str) -> list[str]:
    rows = [r for r in text.strip("\n").split("\n")]
    for r in rows:
        assert len(r) == W, f"row has {len(r)} chars, want {W}: {r!r}"
    return rows


def _rng(col: int, row: int, salt: int = 0) -> random.Random:
    return random.Random(row * 1000 + col * 7 + salt)


def _code(cell: str, rows: list[str], c: int, r: int) -> str:
    """Autotile code for an overlay cell from its 8 neighbours (same character = same terrain)."""
    H = len(rows)

    def same(cc: int, rr: int) -> bool:
        if 0 <= rr < H and 0 <= cc < W:
            other = rows[rr][cc]
            return (other == cell or other in JOINS.get(cell, ())
                    or (rr > r and other in JOINS_BELOW.get(cell, ())))
        return True  # off-map counts as the same terrain so no edge shows at the map border
    n, s, w, e = same(c, r - 1), same(c, r + 1), same(c - 1, r), same(c + 1, r)
    if n and s and w and e:
        ne, nw, se, sw = same(c + 1, r - 1), same(c - 1, r - 1), same(c + 1, r + 1), same(c - 1, r + 1)
        if not se:
            return "ise"
        if not sw:
            return "isw"
        if not ne:
            return "ine"
        if not nw:
            return "inw"
        return "c"
    if not n and not w:
        return "nw"
    if not n and not e:
        return "ne"
    if not s and not w:
        return "sw"
    if not s and not e:
        return "se"
    if not n:
        return "n"
    if not s:
        return "s"
    if not w:
        return "w"
    if not e:
        return "e"
    return "c"


def resolve_ground(rows: list[str], zone: str, row0: int):
    """Return (base, overlay) per-cell lists of (atlas_index, tx, ty) or None."""
    names = tiles.TILES[zone]
    ai = ATLAS_INDEX[zone]
    base_rows, over_rows = [], []
    for r, line in enumerate(rows):
        base_line, over_line = [], []
        for c, k in enumerate(line):
            rng = _rng(c, r + row0)
            if zone == "aiaia" and k in SLAB:
                # Hermes' terrace: one raised stone platform cut from the sheet as a 3 x 3 set
                # (corners, edges, centre), drawn over grass so its rim and shadowed edge show.
                # Random marble pieces from two different floor patterns left broken lines.
                def inside(cc: int, rr: int) -> bool:
                    return 0 <= rr < len(rows) and 0 <= cc < len(rows[rr]) and rows[rr][cc] in SLAB
                v = "t" if not inside(c, r - 1) else ("b" if not inside(c, r + 1) else "m")
                h = "l" if not inside(c - 1, r) else ("r" if not inside(c + 1, r) else "c")
                base_line.append((ai, *names[FILLS[zone]["g"][rng.randrange(4)]]))
                over_line.append((ai, *names[f"slab_{v}{h}"]))
                continue
            fills = FILLS[zone].get(k)
            if fills is None:
                raise KeyError(f"no fill for {k!r} in {zone}")
            fname = fills[rng.randrange(len(fills))]
            if zone == "aiaia" and k == "~" and r > 0 and rows[r - 1][c] in ("S", "P"):
                fname = "sand_c"        # the shore just below the beach shows sand, not grass
            base_line.append((ai, *names[fname]))
            over = OVERLAYS[zone].get(k)
            if over:
                code = _code(k, rows, c, r)
                if code == "c":
                    variants = [f"{over}_c"] + [f"{over}_f{i}" for i in range(3) if f"{over}_f{i}" in names]
                    oname = variants[rng.randrange(len(variants))]
                elif code == "n" and f"{over}_nv0" in names:
                    oname = f"{over}_nv{rng.randrange(3)}"
                else:
                    oname = f"{over}_{code}"
                if oname not in names:
                    raise KeyError(f"no overlay tile {oname!r}")
                over_line.append((ai, *names[oname]))
            else:
                over_line.append(None)
        base_rows.append(base_line)
        over_rows.append(over_line)
    return base_rows, over_rows


def resolve_decor(rows: list[str], row0: int):
    names = tiles.TILES["decor"]
    ai = ATLAS_INDEX["decor"]
    H = len(rows)
    out = []

    def is_f(c: int, r: int) -> bool:
        return 0 <= r < H and 0 <= c < W and rows[r][c] == "F"

    single = {"b": ("bed0", "bed1"), "B": ("bush0",), "O": ("bush1",), "h": ("herb_pot",), "k": ("crate",),
              "T": ("torch",), "n": ("sign",), "o": ("dock_post",), "q": ("dock_post_r",), "Q": ("dock_post_l",), "u": ("stump",), "w": ("seaweed0", "seaweed1"),
              "x": ("bones",), "A": ("amphora5",)}   # amphora0-3 are the top halves of two-tile jars in the sheet; 4 stands by the door
    for r in range(H):
        for c in range(W):
            k = rows[r][c]
            if k == ".":
                continue
            if k == "F":
                l, rt, u, d = is_f(c - 1, r), is_f(c + 1, r), is_f(c, r - 1), is_f(c, r + 1)
                if l and rt:
                    name = "fence_h"
                elif u and d:
                    name = "fence_v"
                elif rt and d:
                    name = "fence_tl"
                elif l and d:
                    name = "fence_tr"
                elif rt and u:
                    name = "fence_bl"
                elif l and u:
                    name = "fence_br"
                elif u or d:
                    name = "fence_v"
                elif rt:
                    name = "fence_end_l"         # left end of a run: rails stop at its post
                elif l:
                    name = "fence_end_r"
                else:
                    name = "fence_post"
            else:
                opts = single[k]
                name = opts[_rng(c, r + row0, 3).randrange(len(opts))]
            tx, ty = names[name]
            out.append((ai, tx, ty, 1, 1, c, r + row0, *SHADOWS.get(name, (0, 0))))
    return out


def resolve_props(props):
    out = []
    for name, c, r in props:
        atlas, tx, ty, w, h = tiles.PROPS[name]
        out.append((ATLAS_INDEX[atlas], tx, ty, w, h, c, r, *SHADOWS.get(name, (0, 0))))
    return out


def blocked_rects(ground_rows, decor_rows, props, row0: int):
    H = len(ground_rows)
    blocked = [[False] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            if ground_rows[r][c] in BLOCKING_GROUND or decor_rows[r][c] in BLOCKING_DECOR:
                blocked[r][c] = True
    for name, c, r in props:
        _, _, _, w, h = tiles.PROPS[name]
        # Trees and columns block only their bottom row (the trunk); buildings block their
        # lower three rows (the walls); rocks and the rest block their whole footprint.
        if name in TREE_PROPS or name.startswith("column"):
            rows_blocked = range(r + h - 1, r + h)
        elif name in ("house", "shrine"):
            rows_blocked = range(r + max(0, h - 3), r + h)
        else:
            rows_blocked = range(r, r + h)
        for rr in rows_blocked:
            for cc in range(c, c + w):
                if 0 <= rr - row0 < H and 0 <= cc < W:
                    blocked[rr - row0][cc] = True
    rects = []
    for r in range(H):
        c = 0
        while c < W:
            if blocked[r][c]:
                start = c
                while c < W and blocked[r][c]:
                    c += 1
                rects.append((start * T, (r + row0) * T, (c - start) * T, T))
            else:
                c += 1
    return rects


def render_preview(base, over, decor, props, atlases, row0: int, name: str) -> None:
    H = len(base)
    img = Image.new("RGBA", (W * T, H * T), (0, 0, 0, 255))
    order = {v: k for k, v in ATLAS_INDEX.items()}
    for layer in (base, over):
        for r in range(H):
            for c in range(W):
                cell = layer[r][c]
                if cell is None:
                    continue
                ai, tx, ty = cell
                img.alpha_composite(atlases[order[ai]].crop((tx * T, ty * T, tx * T + T, ty * T + T)), (c * T, r * T))
    for ai, tx, ty, w, h, c, r, *_ in sorted(decor + props, key=lambda d: d[6] + d[4]):
        src = atlases[order[ai]].crop((tx * T, ty * T, (tx + w) * T, (ty + h) * T))
        img.alpha_composite(src, (c * T, (r - row0) * T))
    PREVIEW.mkdir(parents=True, exist_ok=True)
    img.save(PREVIEW / f"map_{name}.png")


def build(write_gd: bool = True) -> None:
    atlases = tiles.build()
    a_rows, a_dec = _rows(AIAIA), _rows(AIAIA_DECOR)
    c_rows, c_dec = _rows(COVE), _rows(COVE_DECOR)
    assert len(a_rows) == len(a_dec) == 47, (len(a_rows), len(a_dec))
    assert len(c_rows) == len(c_dec) == 48, (len(c_rows), len(c_dec))

    a_base, a_over = resolve_ground(a_rows, "aiaia", 0)
    c_base, c_over = resolve_ground(c_rows, "cove", COVE_ROW0)
    # Open sea between the zones (rows 47-61): dark sea from the cove atlas over stone.
    sea_names = tiles.TILES["cove"]
    sea_base, sea_over = [], []
    for r in range(47, COVE_ROW0):
        bl, ol = [], []
        for c in range(W):
            variants = ["dsea_c", "dsea_f0", "dsea_f1", "dsea_f2"]
            tx, ty = sea_names[variants[_rng(c, r).randrange(len(variants))]]
            bl.append((ATLAS_INDEX["cove"], *sea_names["rock0"]))
            ol.append((ATLAS_INDEX["cove"], tx, ty))
        sea_base.append(bl)
        sea_over.append(ol)
    base = a_base + sea_base + c_base
    over = a_over + sea_over + c_over

    a_decor, a_props = resolve_decor(a_dec, 0), resolve_props(AIAIA_PROPS)
    c_decor, c_props = resolve_decor(c_dec, COVE_ROW0), resolve_props(COVE_PROPS)
    decor = a_decor + a_props + c_decor + c_props
    blocked = blocked_rects(a_rows, a_dec, AIAIA_PROPS, 0) + \
        [(0, r * T, W * T, T) for r in range(47, COVE_ROW0)] + \
        blocked_rects(c_rows, c_dec, COVE_PROPS, COVE_ROW0)

    render_preview(a_base, a_over, a_decor, a_props, atlases, 0, "aiaia")
    render_preview(c_base, c_over, c_decor, c_props, atlases, COVE_ROW0, "cove")

    if not write_gd:
        return

    def rows_literal(layer):
        return ["\t[%s]," % ", ".join(str(encode(cell)) for cell in row) for row in layer]

    lines = [
        "## GENERATED by tools/pixelart/worldmap.py. Do not edit by hand; edit the text maps there.",
        "## Loaded by world.gd with preload(); no class_name on purpose (exports resolve preloads reliably).",
        "## Ground cells: atlas_index * 10000 + ty * 100 + tx, or -1 for no tile. Row r is world y = r * 32.",
        "## Plain nested arrays only: constructor calls are not constant expressions in exported builds.",
        "const TILE := 32",
        "const COLUMNS := %d" % W,
        'const ATLASES := ["res://assets/image_pipeline/generated/raw/tilesets/aiaia_tileset_32.png", '
        '"res://assets/image_pipeline/generated/raw/tilesets/scylla_cove_tileset_32.png", '
        '"res://assets/image_pipeline/generated/raw/tilesets/greek_decor_tileset_32.png"]',
        "const GROUND_ROWS: Array = [", *rows_literal(base), "]",
        "const OVERLAY_ROWS: Array = [", *rows_literal(over), "]",
        "## Decor: [atlas_index, tx, ty, width_tiles, height_tiles, col, row, shadow_rx, shadow_ry]",
        "const DECOR: Array = [", *("\t[%s]," % ", ".join(str(v) for v in d) for d in decor), "]",
        "## Blocked rectangles in pixels: [x, y, width, height]",
        "const BLOCKED: Array = [", *("\t[%s]," % ", ".join(str(v) for v in b) for b in blocked), "]",
    ]
    OUT_GD.parent.mkdir(parents=True, exist_ok=True)
    OUT_GD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_GD} ({len(base)} rows, {len(decor)} decor, {len(blocked)} blocked rects)")


if __name__ == "__main__":
    build(write_gd="--preview-only" not in sys.argv)
