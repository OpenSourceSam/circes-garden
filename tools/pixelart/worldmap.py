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
~ggtttttttttttgg~
~ggtttttttttttgg~
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
~SSSSSSPPPSSSSSS~
~SSSSSSPPPSSSSSS~
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
# 'u' stump, 'w' seaweed, 'x' bones, '.' nothing.  Multi-tile props go in the PROPS lists.
AIAIA_DECOR = """
.................
.................
.................
.................
.................
..hh.............
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
..Fb.........bF..
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
"""

# Multi-tile props on Aiaia: (prop name, col, row of the TOP-LEFT tile)
AIAIA_PROPS = [
    ("house", 1, 1), ("cypress", 5, 0), ("cypress2", 12, 1),
    ("column", 5, 2), ("column2", 11, 2),
    ("olive", 12, 5), ("olive2", 1, 9), ("round_tree", 13, 9),
    ("well", 11, 12), ("olive3", 1, 13), ("shrub", 14, 14), ("shrub2", 2, 22),
    ("big_rock", 13, 11), ("olive", 1, 25), ("olive2", 13, 27),
    ("shrub", 1, 20), ("shrub2", 15, 21), ("rock_s", 3, 28),
]

COVE = """
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~
~~~~~~~PPP~~~~~~~
~~RRRRRPPPRRRRR~~
~~RRRRRRRRRRRRR~~
~~rrrRRRRRRRrrr~~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrr~~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrvvvrrr~
~rrrrrrrrvvvvvrr~
~rrrrrrrrrvvvrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~rrrrrrrrrrrrrrr~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrr~~
~~rrrrrrrrrrrrr~~
~~~rrrrrrrrrrr~~~
~~~rrrrrrrrrrr~~~
~~~~rrrrrrrrr~~~~
~~~~~rrrrrrr~~~~~
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
......o...o......
.................
...w.........w...
......w..........
.................
.................
...........x.....
.................
.................
.....x...........
.................
.................
.................
.................
.................
.................
.............x...
.....x...........
.................
.................
.................
.................
.........x.......
.................
.................
.................
.................
.................
.....x...........
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
COVE_PROPS = [
    ("wreck", 12, 72), ("boulder_d", 1, 73), ("big_rock_d", 13, 76),
    ("spire_d", 3, 78), ("arch_d", 11, 80), ("big_rock_d", 2, 82),
    ("cave", 10, 85), ("dead_tree", 3, 88), ("boulder_d", 13, 89),
    ("spire_d", 13, 93), ("big_rock_d", 3, 94), ("boulder_d", 11, 96),
    ("dead_tree", 12, 99), ("rock_sd", 4, 100), ("big_rock_d", 6, 102), ("spire_d", 9, 102),
]

BLOCKING_GROUND = {"~"}
BLOCKING_DECOR = {"F", "b", "B", "O", "A", "h", "k", "T", "n", "o", "u"}
TREE_PROPS = ("olive", "olive2", "olive3", "round_tree", "big_tree", "cypress", "cypress2", "dead_tree")

OVERLAYS = {"aiaia": {"S": "sand", "~": "sea", "p": "dirt"}, "cove": {"R": "gravel", "~": "dsea", "v": "cave"}}
FILLS = {
    "aiaia": {"g": ["grass0", "grass1", "grass2", "grass3"], "G": ["grassf0", "grassf1", "grassf2", "grassf3"],
              "m": ["marble0", "marble1", "marble2", "marble3"], "M": ["mosaic0", "mosaic1", "mosaic2", "mosaic3"],
              "s": ["cobble_f0", "cobble_c"], "t": ["soil0", "soil1", "soil2", "soil3"], "P": ["plank_v"],
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
            return rows[rr][cc] == cell
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
            fills = FILLS[zone].get(k)
            if fills is None:
                raise KeyError(f"no fill for {k!r} in {zone}")
            fname = fills[rng.randrange(len(fills))]
            base_line.append((ai, *names[fname]))
            over = OVERLAYS[zone].get(k)
            if over:
                code = _code(k, rows, c, r)
                if code == "c":
                    variants = [f"{over}_c"] + [f"{over}_f{i}" for i in range(3) if f"{over}_f{i}" in names]
                    oname = variants[rng.randrange(len(variants))]
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
              "T": ("torch",), "n": ("sign",), "o": ("dock_post",), "u": ("stump",), "w": ("seaweed0", "seaweed1"),
              "x": ("bones",), "A": tuple(n for n in names if n.startswith("amphora"))}
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
                elif l or rt:
                    name = "fence_h"
                else:
                    name = "fence_post"
            else:
                opts = single[k]
                name = opts[_rng(c, r + row0, 3).randrange(len(opts))]
            tx, ty = names[name]
            out.append((ai, tx, ty, 1, 1, c, r + row0))
    return out


def resolve_props(props):
    out = []
    for name, c, r in props:
        atlas, tx, ty, w, h = tiles.PROPS[name]
        out.append((ATLAS_INDEX[atlas], tx, ty, w, h, c, r))
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
    for ai, tx, ty, w, h, c, r in sorted(decor + props, key=lambda d: d[6] + d[4]):
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
        "## Decor: [atlas_index, tx, ty, width_tiles, height_tiles, col, row]",
        "const DECOR: Array = [", *("\t[%s]," % ", ".join(str(v) for v in d) for d in decor), "]",
        "## Blocked rectangles in pixels: [x, y, width, height]",
        "const BLOCKED: Array = [", *("\t[%s]," % ", ".join(str(v) for v in b) for b in blocked), "]",
    ]
    OUT_GD.parent.mkdir(parents=True, exist_ok=True)
    OUT_GD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_GD} ({len(base)} rows, {len(decor)} decor, {len(blocked)} blocked rects)")


if __name__ == "__main__":
    build(write_gd="--preview-only" not in sys.argv)
