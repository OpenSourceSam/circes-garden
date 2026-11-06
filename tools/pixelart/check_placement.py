"""Placement check for the island: finds objects that stand on, in or under each other.

Reads the text maps and prop list in worldmap.py, the prop pictures from lpc_tiles.build(), and the
entity positions in game/scenes/world.tscn, then reports:
  BASE     two objects' footprints (trunks, column bases, walls, fences) share ground;
  COVERED  an object's footprint is hidden behind another object drawn in front of it;
  SHADOW   one object's see-through shadow lies across another object;
  FEET     a character or animal stands on a fence, wall, trunk or rock;
  EDGE     a prop picture touches the edge of its own box along a straight line (looks cropped);
  STRADDLE a prop's footprint sits half on one kind of ground and half on another.
It also writes build/qa/placement_aiaia.png with every finding boxed and numbered.

Run after worldmap.py: python tools/pixelart/check_placement.py   (exit code 1 if anything found)
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw  # noqa: E402

import lpc_tiles as tiles  # noqa: E402
import worldmap as wm  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
T = wm.T
OUT = REPO / "build/qa/placement_aiaia.png"
SHADOW_ALPHA = 200          # pixels below this alpha (and above 0) count as shadow or haze
EDGE_RUN = 10               # opaque pixels in a straight line along a box edge = looks cropped
COVER_SHARE = 0.30          # share of a footprint hidden before it counts as COVERED
# Straight edges checked by eye and meant to be there (2026-11-05): a house has straight walls and
# a flat roof ridge, a freestanding column has a flat top, and the standing stones' left side is
# their natural outline. A new straight edge anywhere else is still reported.
EDGE_OK = {("house", "top"), ("house", "left"), ("house", "right"), ("column2", "top"),
           ("column", "top"), ("big_rock", "left")}
# Entities in world.tscn on the island, with an approximate footprint (feet) box: half width, height.
ENTITY_FEET = {"hermes": (10, 8), "pig": (12, 8), "crafting_table": (30, 14), "sleep_spot": (24, 12),
               "farm_plot": (30, 16), "boat": (40, 20), "player": (10, 8)}


@dataclass
class Obj:
    name: str
    x: int                  # top-left of the picture in world pixels
    y: int
    img: Image.Image | None
    sort_y: int             # world y used by the y-sort (bottom of the prop)
    base: tuple[int, int, int, int]   # footprint rect x0, y0, x1, y1 (exclusive)
    kind: str               # prop, decor or entity


def _props(atlases: dict[int, Image.Image]) -> list[Obj]:
    out = []
    for name, c, r in wm.AIAIA_PROPS:
        atlas, tx, ty, w, h = tiles.PROPS[name]
        img = atlases[wm.ATLAS_INDEX[atlas]].crop((tx * T, ty * T, (tx + w) * T, (ty + h) * T))
        x, y = c * T, r * T
        if name in wm.TREE_PROPS or name.startswith("column"):
            base = (x, y + (h - 1) * T, x + w * T, y + h * T)
        elif name in ("house", "shrine"):
            base = (x, y + max(0, h - 3) * T, x + w * T, y + h * T)
        else:
            base = (x, y, x + w * T, y + h * T)
        base = _shrink_to_pixels(img, x, y, base)
        out.append(Obj(f"{name}@{c},{r}", x, y, img, y + h * T, base, "prop"))
    return out


def _shrink_to_pixels(img: Image.Image, x: int, y: int, rect):
    """Tighten a footprint to the opaque pixels inside it (a trunk is narrower than its tile)."""
    x0, y0, x1, y1 = rect
    sub = img.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    alpha = sub.getchannel("A").point(lambda a: 255 if a >= SHADOW_ALPHA else 0)
    box = alpha.getbbox()
    if not box:
        return rect
    return (x0 + box[0], y0 + box[1], x0 + box[2], y0 + box[3])


def _decor(atlases: dict[int, Image.Image]) -> list[Obj]:
    rows = wm._rows(wm.AIAIA_DECOR)
    out = []
    for ai, tx, ty, w, h, c, r, *_ in wm.resolve_decor(rows, 0):
        img = atlases[ai].crop((tx * T, ty * T, (tx + w) * T, (ty + h) * T))
        x, y = c * T, r * T
        char = rows[r][c]
        name = {"F": "fence", "h": "urn", "A": "amphora", "k": "crate", "T": "torch", "n": "sign",
                "o": "dock_post", "b": "flower_bed", "B": "bush", "O": "olive_bush", "u": "stump"}.get(char, char)
        base = _shrink_to_pixels(img, x, y, (x, y, x + w * T, y + h * T))
        out.append(Obj(f"{name}@{c},{r}", x, y, img, y + h * T, base, "decor"))
    return out


def _entities() -> list[Obj]:
    text = (REPO / "game/scenes/world.tscn").read_text(encoding="utf-8")
    ext = dict(re.findall(r'\[ext_resource [^\]]*path="([^"]+)" id="([^"]+)"\]', text))
    ext = {v: k for k, v in ext.items()}
    out = []
    for block in text.split("\n[node ")[1:]:
        m = re.match(r'name="([^"]+)"[^\]]*instance=ExtResource\("([^"]+)"\)', block)
        pos = re.search(r"position = Vector2\(([-\d.]+), ([-\d.]+)\)", block)
        if not m or not pos:
            continue
        path = ext.get(m.group(2), "")
        stem = Path(path).stem
        if stem not in ENTITY_FEET:
            continue
        x, y = int(float(pos.group(1))), int(float(pos.group(2)))
        if y > 47 * T:
            continue                                  # the cove is checked separately
        hw, hh = ENTITY_FEET[stem]
        out.append(Obj(f"{stem}:{m.group(1)}@{x},{y}", x - hw, y - hh, None, y, (x - hw, y - hh, x + hw, y + 2), "entity"))
    spawn = (270, 350)
    out.append(Obj("player:spawn", spawn[0] - 10, spawn[1] - 8, None, spawn[1], (260, 342, 280, 352), "entity"))
    return out


def _overlap(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    return (x0, y0, x1, y1) if x0 < x1 and y0 < y1 else None


def _alpha_at(o: Obj, px: int, py: int) -> int:
    if o.img is None:
        return 0
    lx, ly = px - o.x, py - o.y
    if 0 <= lx < o.img.width and 0 <= ly < o.img.height:
        return o.img.getpixel((lx, ly))[3]
    return 0


def _box(o: Obj):
    if o.img is None:
        return o.base
    return (o.x, o.y, o.x + o.img.width, o.y + o.img.height)


def _same_group(a: Obj, b: Obj) -> bool:
    # Neighbouring fence pieces are meant to touch.
    return a.name.startswith("fence") and b.name.startswith("fence")


def check() -> list[tuple[str, str, tuple[int, int, int, int]]]:
    built = tiles.build()                     # also fills tiles.PROPS and tiles.TILES
    atlases = {wm.ATLAS_INDEX[k]: im.convert("RGBA") for k, im in built.items()}
    objs = _props(atlases) + _decor(atlases) + _entities()
    findings = []
    ground = wm._rows(wm.AIAIA)
    for i, a in enumerate(objs):
        for b in objs[i + 1:]:
            if _same_group(a, b):
                continue
            ov = _overlap(a.base, b.base)
            if ov and (ov[2] - ov[0]) * (ov[3] - ov[1]) >= 16:
                kind = "FEET" if "entity" in (a.kind, b.kind) else "BASE"
                findings.append((kind, f"{a.name} and {b.name} share ground", ov))
    for a in objs:
        # COVERED: a's footprint hidden by any object drawn after it.
        bx0, by0, bx1, by1 = a.base
        area = max(1, (bx1 - bx0) * (by1 - by0))
        for b in objs:
            if b is a or b.img is None or b.sort_y <= a.sort_y or _same_group(a, b):
                continue
            ov = _overlap(a.base, _box(b))
            if not ov:
                continue
            hidden = sum(1 for py in range(ov[1], ov[3]) for px in range(ov[0], ov[2])
                         if _alpha_at(b, px, py) >= SHADOW_ALPHA)
            if hidden / area >= COVER_SHARE:
                findings.append(("COVERED", f"{a.name} is {100 * hidden // area}% hidden behind {b.name}", ov))
        # SHADOW: a's see-through pixels over another object's solid pixels.
        if a.img is None:
            continue
        for b in objs:
            if b is a or b.img is None or _same_group(a, b):
                continue
            ov = _overlap(_box(a), _box(b))
            if not ov:
                continue
            n = 0
            for py in range(ov[1], ov[3]):
                for px in range(ov[0], ov[2]):
                    aa = _alpha_at(a, px, py)
                    if 0 < aa < SHADOW_ALPHA and _alpha_at(b, px, py) >= SHADOW_ALPHA:
                        n += 1
            if n >= 24:
                findings.append(("SHADOW", f"shadow or haze of {a.name} lies over {b.name} ({n} px)", ov))
        # EDGE: straight opaque runs along the left, right or top edge of a prop's own box.
        if a.kind == "prop":
            w, h = a.img.size
            alpha = a.img.getchannel("A")
            edges = {"top": [(x, 0) for x in range(w)], "left": [(0, y) for y in range(h)],
                     "right": [(w - 1, y) for y in range(h)]}
            for side, pts in edges.items():
                run = best = 0
                for p in pts:
                    run = run + 1 if alpha.getpixel(p) >= SHADOW_ALPHA else 0
                    best = max(best, run)
                if best >= EDGE_RUN and (a.name.split("@")[0], side) not in EDGE_OK:
                    findings.append(("EDGE", f"{a.name} picture is cut by its box on the {side} ({best} px straight)",
                                     _box(a)))
            # STRADDLE: footprint tiles on different ground letters.
            cols = range(a.base[0] // T, (a.base[2] - 1) // T + 1)
            row = (a.base[3] - 1) // T
            letters = {ground[row][c] for c in cols if 0 <= row < len(ground) and 0 <= c < wm.W}
            if len({{"G": "g", "S": "g"}.get(ch, ch) for ch in letters}) > 1:
                findings.append(("STRADDLE", f"{a.name} stands on mixed ground {sorted(letters)}", a.base))
    return findings


def draw(findings) -> None:
    preview = wm.PREVIEW / "map_aiaia.png"
    if not preview.exists():
        return
    img = Image.open(preview).convert("RGBA").resize((wm.W * T * 2, 47 * T * 2), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(img)
    colours = {"BASE": "#ff3030", "FEET": "#ff3030", "COVERED": "#ff9a1a", "SHADOW": "#3aa0ff",
               "EDGE": "#ffe23a", "STRADDLE": "#c060ff"}
    for i, (kind, _, (x0, y0, x1, y1)) in enumerate(findings, 1):
        d.rectangle((x0 * 2, y0 * 2, x1 * 2 - 1, y1 * 2 - 1), outline=colours[kind], width=2)
        d.text((x0 * 2 + 3, y0 * 2 + 2), str(i), fill=colours[kind])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)


def main() -> int:
    findings = check()
    for i, (kind, text, rect) in enumerate(findings, 1):
        print(f"{i:3d}. {kind:8s} {text}  at x {rect[0]}-{rect[2]}, y {rect[1]}-{rect[3]}")
    draw(findings)
    print(f"{len(findings)} placement findings; picture: {OUT}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
