"""Build the game's three 32-px atlases from the LPC packs (terrain, trees, conifers,
rocks, Ancient Greek architecture) and register tile names for worldmap.py.

Sources (unpacked under build/lpc_downloads/x/, not in git; credits in docs/CREDITS.md):
  lpc-terrains/terrain-v7.png   blocks of 96x192: rows 0-1 inner corners, rows 2-4 the 3x3
                                edge block (centre = fill), row 5 alternate fills
  lpc-trees/trees-green.png, lpc-conifers/conifers.png, rocks/rocks.png: free-form sprites
  LPC_Ancient_Greece_Architecture.png: 32-px grid, columns, roofs, walls, pottery, mosaics

Atlas layout produced here (16 x 8 tiles of 32 px each):
  aiaia:  terrain for the island (grass fills, sand/sea/dirt overlays with edges, marble)
  cove:   terrain for the cove (stone fills, gravel and dark-sea overlays, cave floor)
  decor:  transparent props on a 32-px grid; multi-tile props registered in PROPS
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parents[2]
X = REPO / "build/lpc_downloads/x"
TERRAIN = X / "lpc-terrains/terrain-v7.png"
TREES = X / "lpc-trees/trees-green.png"
CONIFERS = X / "lpc-conifers/conifers.png"
ROCKS = X / "rocks/rocks.png"
GREEK = X / "LPC_Ancient_Greece_Architecture.png"

T = 32
COLS, ROWS = 16, 8

TILES: dict[str, dict[str, tuple[int, int]]] = {"aiaia": {}, "cove": {}, "decor": {}}
PROPS: dict[str, tuple[str, int, int, int, int]] = {}

# Edge codes for an overlay terrain, in the order they sit in an LPC block.
# Inner corners (concave): the missing diagonal. Outer: which sides are open.
EDGE_LOCAL = {
    # One terrain = a 96x224 block: rows 0-1 hold the 2x2 concave-corner set in columns 1-2
    # (column 0 has small islands), rows 2-4 the 3x3 edge block, row 5 three fill variants.
    "ise": (1, 0), "isw": (2, 0), "ine": (1, 1), "inw": (2, 1),
    "nw": (0, 2), "n": (1, 2), "ne": (2, 2),
    "w": (0, 3), "c": (1, 3), "e": (2, 3),
    "sw": (0, 4), "s": (1, 4), "se": (2, 4),
    "c1": (0, 5), "c2": (1, 5), "c3": (2, 5),
    "isle0": (0, 0), "isle1": (0, 1),
}
BLOCK_H = 224

_img_cache: dict[Path, Image.Image] = {}


def img(path: Path) -> Image.Image:
    if path not in _img_cache:
        _img_cache[path] = Image.open(path).convert("RGBA")
    return _img_cache[path]


def tile_at(sheet: Image.Image, px: int, py: int, w: int = T, h: int = T) -> Image.Image:
    return sheet.crop((px, py, px + w, py + h))


def terrain_block_tile(bc: int, k: int, code: str) -> Image.Image:
    """Tile `code` of terrain number `k` (top to bottom) in block column `bc`."""
    lx, ly = EDGE_LOCAL[code]
    return tile_at(img(TERRAIN), bc * 96 + lx * T, k * BLOCK_H + ly * T)


def mood(im: Image.Image, saturation: float = 0.9, contrast: float = 1.05, warmth: int = 3) -> Image.Image:
    rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(saturation)).enhance(contrast)
    arr = np.array(rgb).astype(int)
    arr[..., 0] = np.clip(arr[..., 0] + warmth, 0, 255)
    arr[..., 2] = np.clip(arr[..., 2] - warmth, 0, 255)
    out = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


ATLAS_SIZE = {"aiaia": (16, 8), "cove": (16, 8), "decor": (32, 32)}


class Atlas:
    def __init__(self, name: str):
        self.name = name
        self.cols, self.rows = ATLAS_SIZE[name]
        self.im = Image.new("RGBA", (self.cols * T, self.rows * T), (0, 0, 0, 0))
        self.next = 0

    def put(self, tile: Image.Image, tname: str) -> tuple[int, int]:
        w, h = tile.width // T, tile.height // T
        # First-fit on the grid for multi-tile images.
        for idx in range(self.next, self.cols * self.rows):
            cx, cy = idx % self.cols, idx // self.cols
            if cx + w <= self.cols and cy + h <= self.rows and self._free(cx, cy, w, h):
                self.im.alpha_composite(tile, (cx * T, cy * T))
                self._mark(cx, cy, w, h)
                TILES[self.name][tname] = (cx, cy)
                if w > 1 or h > 1:
                    PROPS[tname] = (self.name, cx, cy, w, h)
                return cx, cy
        raise RuntimeError(f"atlas {self.name} is full placing {tname}")

    def _free(self, cx, cy, w, h) -> bool:
        if not hasattr(self, "_used"):
            self._used = set()
        return all((x, y) not in self._used for x in range(cx, cx + w) for y in range(cy, cy + h))

    def _mark(self, cx, cy, w, h) -> None:
        for x in range(cx, cx + w):
            for y in range(cy, cy + h):
                self._used.add((x, y))


def add_overlay(atlas: Atlas, prefix: str, bc: int, br: int, fills: int = 3) -> None:
    for code in ("ise", "isw", "ine", "inw", "nw", "n", "ne", "w", "c", "e", "sw", "s", "se"):
        atlas.put(mood(terrain_block_tile(bc, br, code)), f"{prefix}_{code}")
    for i, code in enumerate(("c1", "c2", "c3")[:fills]):
        atlas.put(mood(terrain_block_tile(bc, br, code)), f"{prefix}_f{i}")


def add_fill(atlas: Atlas, prefix: str, bc: int, br: int, n: int = 4) -> None:
    codes = ["c", "c1", "c2", "c3"][:n]
    for i, code in enumerate(codes):
        atlas.put(mood(terrain_block_tile(bc, br, code)), f"{prefix}{i}")


# --- sprite extraction for trees, rocks (connected regions of opaque pixels) --------------
def components(sheet: Image.Image, min_size: int = 20, block: int = 4) -> list[tuple[int, int, int, int]]:
    """Bounding boxes of opaque regions, found on a coarse grid then refined."""
    a = np.array(sheet.getchannel("A")) > 0
    H, W = a.shape
    bh, bw = (H + block - 1) // block, (W + block - 1) // block
    grid = np.zeros((bh, bw), dtype=bool)
    for by in range(bh):
        for bx in range(bw):
            grid[by, bx] = a[by * block:(by + 1) * block, bx * block:(bx + 1) * block].any()
    seen = np.zeros_like(grid)
    boxes = []
    for sy in range(bh):
        for sx in range(bw):
            if not grid[sy, sx] or seen[sy, sx]:
                continue
            stack = [(sy, sx)]
            seen[sy, sx] = True
            cells = []
            while stack:
                y, x = stack.pop()
                cells.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < bh and 0 <= nx < bw and grid[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
            ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
            x0, y0 = min(xs) * block, min(ys) * block
            x1, y1 = min(W, (max(xs) + 1) * block), min(H, (max(ys) + 1) * block)
            sub = a[y0:y1, x0:x1]
            rows = np.where(sub.any(axis=1))[0]; cols = np.where(sub.any(axis=0))[0]
            if len(rows) == 0:
                continue
            bx0, by0, bx1, by1 = x0 + cols[0], y0 + rows[0], x0 + cols[-1] + 1, y0 + rows[-1] + 1
            if bx1 - bx0 >= min_size and by1 - by0 >= min_size:
                boxes.append((bx0, by0, bx1, by1))
    return sorted(boxes, key=lambda b: (b[1] // 64, b[0]))


def sprite_to_tiles(sprite: Image.Image, max_w_tiles: int = 6, max_h_tiles: int = 6) -> Image.Image:
    """Pad a sprite to whole tiles, anchored bottom-centre; downscale if it is too large."""
    w, h = sprite.size
    max_w, max_h = max_w_tiles * T, max_h_tiles * T
    if w > max_w or h > max_h:
        f = min(max_w / w, max_h / h)
        sprite = sprite.resize((max(1, int(w * f)), max(1, int(h * f))), Image.Resampling.NEAREST)
        w, h = sprite.size
    tw, th = (w + T - 1) // T, (h + T - 1) // T
    out = Image.new("RGBA", (tw * T, th * T), (0, 0, 0, 0))
    out.alpha_composite(sprite, ((tw * T - w) // 2, th * T - h))
    return out


def pick_box(sheet: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """Crop a region and keep only its largest opaque component (isolates one tree)."""
    region = sheet.crop(box)
    boxes = components(region, min_size=8, block=2)
    if not boxes:
        return region
    b = max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    return region.crop(b)


def pick_component(sheet: Image.Image, boxes, near: tuple[int, int]) -> Image.Image:
    """The component whose box contains or is closest to the point `near` (sheet pixels)."""
    x, y = near
    inside = [b for b in boxes if b[0] <= x < b[2] and b[1] <= y < b[3]]
    if inside:
        b = min(inside, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))   # the tightest, not a merged blob
    else:
        b = min(boxes, key=lambda b: (abs((b[0] + b[2]) / 2 - x) + abs((b[1] + b[3]) / 2 - y)))
    return sheet.crop(b)


def greek(px: int, py: int, w: int = 1, h: int = 1) -> Image.Image:
    return tile_at(img(GREEK), px * T, py * T, w * T, h * T)


def build() -> dict[str, Image.Image]:
    TILES["aiaia"].clear(); TILES["cove"].clear(); TILES["decor"].clear(); PROPS.clear()
    aiaia, cove, decor = Atlas("aiaia"), Atlas("cove"), Atlas("decor")

    # ---- island terrain ----
    add_fill(aiaia, "grass", 1, 1, 4)              # mid green grass fills
    import random as _random
    for i in range(4):                             # grass with small flowers drawn on
        t = mood(terrain_block_tile(1, 1, ["c", "c1", "c2", "c3"][i])).copy()
        rng = _random.Random(500 + i)
        for _ in range(rng.randrange(2, 4)):
            x, y = rng.randrange(2, T - 3), rng.randrange(2, T - 3)
            col = rng.choice([(246, 243, 231, 255), (242, 200, 75, 255), (224, 122, 168, 255)])
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                t.putpixel((x + dx, y + dy), col)
            t.putpixel((x + 1, y + 2), (47, 107, 38, 255))
        aiaia.put(t, f"grassf{i}")
    add_overlay(aiaia, "sand", 5, 1)               # beach sand over grass
    add_overlay(aiaia, "sea", 0, 2)                # water with sandy shore edge
    add_overlay(aiaia, "dirt", 3, 1)               # dirt path over grass
    add_overlay(aiaia, "cobble", 5, 3, fills=1)    # pale cobblestone (terrace surround)
    for i, (gx, gy) in enumerate(((8, 9), (9, 9), (8, 10), (9, 10))):
        aiaia.put(mood(greek(gx, gy)), f"marble{i}")
    for i, (gx, gy) in enumerate(((12, 11), (13, 11), (12, 12), (13, 12))):
        aiaia.put(mood(greek(gx, gy)), f"mosaic{i}")
    for i in range(4):
        t = mood(terrain_block_tile(3, 1, ["c", "c1", "c2", "c3"][i]), saturation=0.85, contrast=1.1, warmth=0)
        arr = np.array(t)
        for y in (6, 14, 22, 30):
            arr[y, :, :3] = (arr[y, :, :3] * 0.6).astype(np.uint8)
            arr[min(31, y + 1), :, :3] = np.clip(arr[min(31, y + 1), :, :3] * 1.15, 0, 255).astype(np.uint8)
        aiaia.put(Image.fromarray(arr, "RGBA"), f"soil{i}")
    import tiles as gen
    aiaia.put(gen.plank_tile(60, True).im, "plank_v")

    # ---- cove terrain ----
    add_fill(cove, "rock", 4, 0, 4)                # grey stone floor
    add_fill(cove, "rockd", 6, 0, 4)               # darker stone
    add_overlay(cove, "gravel", 8, 1)              # gravel landing over stone
    add_overlay(cove, "dsea", 6, 2)                # dark sea with dark edge
    add_overlay(cove, "cave", 8, 0, fills=1)       # near-black ground in front of the cave
    cove.put(gen.plank_tile(60, True).im, "plank_v")

    # ---- decor: props from LPC packs ----
    trees = img(TREES); conifers = img(CONIFERS); rocks = img(ROCKS)

    def prop(sheet, box, name, max_w=4, max_h=5):
        decor.put(mood(sprite_to_tiles(pick_box(sheet, box), max_w, max_h)), name)

    # Trees are cut along their own outline (canopy and shadow), found by components(), so no
    # tree is sliced by a hand-typed box. `near` is any point inside the tree on the sheet.
    tree_boxes = components(trees, min_size=8, block=2)

    def tree(near, name, max_w=4, max_h=4):
        decor.put(mood(sprite_to_tiles(pick_component(trees, tree_boxes, near), max_w, max_h)), name)

    tree((640, 290), "olive")          # dark gnarled tree with roots
    tree((370, 160), "olive2")         # dark round tree
    tree((770, 290), "olive3")         # bright round tree
    tree((175, 160), "round_tree", 3, 4)
    tree((590, 150), "big_tree", 3, 4)
    prop(trees, (0, 28, 64, 66), "shrub", 2, 2)
    prop(trees, (64, 0, 128, 64), "shrub2", 2, 2)
    prop(conifers, (225, 0, 300, 165), "cypress", 2, 6)
    prop(conifers, (440, 0, 560, 150), "cypress2", 3, 5)
    prop(rocks, (0, 0, 64, 64), "rock_s", 2, 2)
    prop(rocks, (290, 30, 380, 110), "big_rock", 3, 3)
    prop(rocks, (0, 512, 64, 576), "rock_sd", 2, 2)
    prop(rocks, (290, 540, 380, 620), "big_rock_d", 3, 3)
    prop(rocks, (640, 640, 768, 768), "boulder_d", 4, 4)
    prop(rocks, (384, 520, 520, 620), "arch_d", 4, 3)
    prop(rocks, (512, 610, 560, 700), "spire_d", 2, 3)
    # Greek architecture pieces.
    decor.put(mood(greek(0, 0, 1, 4)), "column")          # full Ionic column, 1x4
    decor.put(mood(greek(0, 9, 1, 4)), "column2")
    decor.put(mood(greek(0, 4, 1, 1)), "column_b")        # broken stub
    for i, gx in enumerate((0, 1, 2, 4, 6, 9)):
        decor.put(mood(greek(gx, 18)), f"amphora{i}")
    decor.put(mood(greek(12, 9, 2, 2)), "altar")          # round altar 2x2
    decor.put(mood(greek(14, 16, 3, 1)), "bench")
    decor.put(mood(greek(18, 16, 2, 1)), "doors")
    # The pediment roof region's top-left tile holds a stray piece of the next roof on the sheet;
    # it showed as a floating red square above the house, so it is cleared.
    def roof() -> Image.Image:
        r = greek(7, 1, 5, 4).copy()
        r.paste((0, 0, 0, 0), (0, 0, T, T))
        return r

    # Circe's house: tiled roof (4x4) over stone walls (4x2) with a door.
    house = Image.new("RGBA", (5 * T, 6 * T), (0, 0, 0, 0))
    house.alpha_composite(roof(), (0, 0))                        # pediment roof
    house.alpha_composite(greek(7, 6, 5, 2), (0, 4 * T))         # stone walls
    house.alpha_composite(greek(12, 6, 1, 2), (2 * T, 4 * T))    # door
    house.alpha_composite(greek(6, 18), (4 * T, 5 * T))          # pot by the door
    house.alpha_composite(greek(1, 18), (0, 5 * T))              # amphora by the door
    decor.put(mood(house), "house")
    # Small temple/shrine for the terrace: pediment roof over two columns.
    shrine = Image.new("RGBA", (5 * T, 6 * T), (0, 0, 0, 0))
    shrine.alpha_composite(roof(), (0, 0))
    shrine.alpha_composite(greek(0, 1, 1, 2), (0, 4 * T))
    shrine.alpha_composite(greek(0, 1, 1, 2), (4 * T, 4 * T))
    decor.put(mood(shrine), "shrine")

    # Small hand-made bits kept from the code generator (fences, beds, well, cave, torch...).
    gen_decor = gen.decor_atlas()
    for name in ("fence_h", "fence_v", "fence_post", "fence_tl", "fence_tr", "fence_bl", "fence_br",
                 "bed0", "bed1", "bush0", "bush1", "herb_pot", "crate", "torch", "sign", "dock_post",
                 "seaweed0", "seaweed1", "bones", "stump"):
        cx, cy = gen.TILES["decor"][name]
        decor.put(gen_decor.im.crop((cx * T, cy * T, (cx + 1) * T, (cy + 1) * T)), name)
    for name in ("well", "cave", "dead_tree", "wreck"):
        _, cx, cy, w, h = gen.PROPS[name]
        decor.put(gen_decor.im.crop((cx * T, cy * T, (cx + w) * T, (cy + h) * T)), name)

    return {"aiaia": aiaia.im, "cove": cove.im, "decor": decor.im}


def all_tiles():
    """Same shape as tiles.all_tiles(): {relative path: image} for build_all / worldmap."""
    from px import Px
    out = {}
    names = {"aiaia": "tilesets/aiaia_tileset_32.png", "cove": "tilesets/scylla_cove_tileset_32.png",
             "decor": "tilesets/greek_decor_tileset_32.png"}
    for key, im in build().items():
        p = Px(im.width, im.height); p.im = im
        out[names[key]] = p
    return out


if __name__ == "__main__":
    from px import preview, save
    out = Path(__file__).parent / "preview"
    for key, im in build().items():
        save(preview(im, 2, grid=32), out / f"lpc_atlas_{key}_x2.png")
    print({k: len(v) for k, v in TILES.items()}, "props:", list(PROPS)[:40])
