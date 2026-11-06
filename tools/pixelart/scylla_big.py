"""Scylla as parts: dog heads, neck segments, the body she raises out of the strait, foam, a vial.

Godot draws her from these parts every frame (game/entities/npcs/scylla.gd): six necks are
chains of overlapping discs along curves with a head on each, at whole-pixel positions and 1:1
scale. This file draws the parts into one atlas and writes their regions, pivots and the neck
anchors to game/data/scylla_parts.gd. `neck_chain()` follows the same rule as scylla.gd so the
previews (cove_scene.py) show what the game shows.
"""
from __future__ import annotations

import math
from pathlib import Path

from px import Px, rgb
from shading import mask, autoshade, outline_mask, inner_edge

REPO = Path(__file__).resolve().parents[2]
OUT_GD = REPO / "game/data/scylla_parts.gd"
ATLAS_REL = "sprites/characters/scylla/scylla_parts.png"

# Slate hide, cold and wet, a shade darker than the cliff so she reads against it.
OUT = rgb("#0b0f12")
D2 = rgb("#1a2225")
DARK = rgb("#283336")
BODY = rgb("#3a4749")
MID = rgb("#4f5d5e")
LIGHT = rgb("#6d7b78")
HI = rgb("#98a39b")
BELLY = rgb("#8a8672")
BELLY_D = rgb("#635f50")
BELLY_DD = rgb("#4a4a40")
EYE = rgb("#ff9f2e")
EYE_HOT = rgb("#fff1a8")
EYE_D = rgb("#b8380c")
EYE_CALM = rgb("#6e5a44")
MOUTH = rgb("#5e1622")
MOUTH_D = rgb("#2a060c")
TONGUE = rgb("#9c3040")
TOOTH = rgb("#efe8d2")
TOOTH_D = rgb("#b0a68a")
FOAM = rgb("#e4f1f4")
FOAM_D = rgb("#9fc0c8")
GLASS = rgb("#7fd3e6")
GLASS_D = rgb("#3f93a8")
LIQUID = rgb("#c9f4ff")
CORK = rgb("#9c6b3c")

HIDE = [D2, DARK, BODY, MID, LIGHT, HI]
PALE = [DARK, BELLY_D, BELLY]


# ---------------------------------------------------------------------------
# Heads in profile, facing left (the right-facing ones are mirrors). The ruff of spines at the
# back of the skull is where the neck goes in.
SIDE_W, SIDE_H = 38, 27


def side_head(open_jaw: bool) -> Px:
    W, H = SIDE_W, SIDE_H
    p = Px(W, H)
    ruff = mask(W, H, lambda q: [q.poly([(22, 5), (35, 3), (29, 9)], OUT), q.poly([(25, 8), (37, 10), (29, 13)], OUT),
                                 q.poly([(25, 12), (36, 17), (28, 17)], OUT), q.poly([(23, 16), (32, 23), (24, 21)], OUT)])
    neck = mask(W, H, lambda q: q.ellipse(18, 11, 32, 26, OUT))
    skull = mask(W, H, lambda q: [q.ellipse(11, 2, 28, 18, OUT),
                                  q.poly([(1, 9), (2, 7), (13, 5), (17, 8), (17, 14), (1, 13)], OUT)])
    ear = mask(W, H, lambda q: q.poly([(18, 6), (24, 0), (26, 0), (28, 8), (23, 9)], OUT))
    if open_jaw:
        jaw = mask(W, H, lambda q: q.poly([(4, 20), (17, 15), (24, 17), (21, 21), (9, 23), (4, 22)], OUT))
        cavity = mask(W, H, lambda q: q.poly([(2, 13), (17, 13), (19, 16), (5, 20)], OUT))
    else:
        jaw = mask(W, H, lambda q: q.poly([(3, 14), (17, 13), (24, 16), (21, 19), (8, 18), (3, 16)], OUT))
        cavity = set()
    autoshade(p, ruff, [D2, DARK, BODY], depth=2, lift=-0.3)
    autoshade(p, neck, HIDE, depth=5, lift=-1.0)
    autoshade(p, jaw, PALE, depth=2)
    for (x, y) in cavity:
        p.dot(x, y, MOUTH)
    autoshade(p, skull, HIDE, depth=5)
    autoshade(p, ear, HIDE, depth=2, lift=0.3)
    for (x, y) in [(23, 3), (23, 4), (24, 4), (24, 5), (24, 6), (25, 6)]:
        p.dot(x, y, D2)
    outline_mask(p, ruff | neck | skull | ear | jaw | cavity, OUT)
    if open_jaw:
        for (x, y) in cavity:
            if y >= 16 and 7 <= x <= 15:
                p.dot(x, y, TONGUE)
            if x >= 16:
                p.dot(x, y, MOUTH_D)
        for x in (3, 6, 9, 12, 15):
            p.dot(x, 14, TOOTH)
        for x in (4, 11):
            p.dot(x, 15, TOOTH)
            p.dot(x, 16, TOOTH_D)
        for x in (7, 10, 13, 16):
            p.dot(x, 19 - (x - 7) // 4, TOOTH)
        p.dot(6, 18, TOOTH); p.dot(6, 19, TOOTH)
    else:
        for (x, y) in inner_edge(jaw, skull):
            if y >= 13 and x <= 17:
                p.dot(x, y, MOUTH_D)
        for x in (4, 7, 10, 13):
            p.dot(x, 14, TOOTH)
        for x in (5, 12):
            p.dot(x, 15, TOOTH)
        p.dot(16, 14, TOOTH_D)
    p.rect(0, 8, 2, 10, OUT); p.dot(1, 8, MID)                     # nose
    for (x, y) in [(6, 8), (7, 8), (9, 7), (10, 7), (8, 10), (9, 10)]:
        p.dot(x, y, DARK)                                          # snarl wrinkles
    for (x, y) in [(12, 6), (13, 6), (14, 6), (15, 7), (16, 7)]:
        p.dot(x, y, D2)                                            # brow
    p.dot(13, 7, EYE_D); p.dot(14, 7, EYE); p.dot(15, 8, EYE); p.dot(14, 8, EYE_HOT); p.dot(16, 8, EYE_D)
    return p


# Heads seen from the front, looking down at Circe: symmetric, so drawn from a left half.
FRONT_W, FRONT_H = 31, 29


def _sym(q: Px, pts: list[tuple[int, int]], c) -> None:
    q.poly(pts, c)
    q.poly([(FRONT_W - 1 - x, y) for x, y in pts], c)


def front_head(jaw_state: str) -> Px:
    """jaw_state: 'closed' (snarling), 'open' (biting, screaming) or 'calm' (eyes half shut)."""
    W, H = FRONT_W, FRONT_H
    p = Px(W, H)
    ears = mask(W, H, lambda q: _sym(q, [(6, 9), (4, 0), (6, 0), (12, 5)], OUT))
    tufts = mask(W, H, lambda q: _sym(q, [(7, 9), (0, 11), (5, 13), (1, 17), (8, 19)], OUT))
    skull = mask(W, H, lambda q: q.ellipse(5, 3, 25, 19, OUT))
    muzzle = mask(W, H, lambda q: [q.ellipse(10, 10, 20, 21, OUT), q.rect(11, 13, 19, 20, OUT)])
    open_ = jaw_state == "open"
    jaw = mask(W, H, lambda q: q.ellipse(9, 21, 21, 28, OUT) if open_ else q.ellipse(10, 18, 20, 25, OUT))
    cavity = mask(W, H, lambda q: q.ellipse(9, 18, 21, 25, OUT)) if open_ else set()
    autoshade(p, tufts, [D2, DARK, BODY], depth=2, lift=-0.3)
    autoshade(p, ears, HIDE, depth=2, lift=0.2)
    autoshade(p, jaw, PALE, depth=2)
    for (x, y) in cavity:
        p.dot(x, y, MOUTH_D if y < 20 else (TONGUE if 12 <= x <= 18 and y >= 22 else MOUTH))
    autoshade(p, skull, HIDE, depth=5)
    autoshade(p, muzzle, HIDE, depth=3, lift=0.6)
    for (x, y) in [(5, 3), (5, 4), (6, 5), (6, 6)]:
        p.dot(x, y, D2); p.dot(W - 1 - x, y, D2)                    # ear inner
    outline_mask(p, ears | tufts | skull | muzzle | jaw | cavity, OUT)
    p.rect(13, 18, 17, 20, OUT); p.dot(14, 18, MID)                  # nose
    # Brows slant down toward the nose; the eyes glow under them.
    for (x, y) in [(7, 8), (8, 8), (9, 9), (10, 9), (11, 10)]:
        p.dot(x, y, D2); p.dot(W - 1 - x, y, D2)
    if jaw_state == "calm":
        for x in (8, 9, 10):
            p.dot(x, 11, EYE_CALM); p.dot(W - 1 - x, 11, EYE_CALM)
            p.dot(x, 10, D2); p.dot(W - 1 - x, 10, D2)
    else:
        for (x, y, c) in [(8, 10, EYE_D), (9, 10, EYE), (10, 11, EYE), (9, 11, EYE_HOT), (8, 11, EYE_D), (11, 11, EYE_D)]:
            p.dot(x, y, c); p.dot(W - 1 - x, y, c)
    # Teeth: a snarl when shut, fangs top and bottom when open.
    if open_:
        for x in (10, 12, 14, 16, 18, 20):
            p.dot(x, 20, TOOTH)
        for x in (11, 19):
            p.dot(x, 21, TOOTH); p.dot(x, 22, TOOTH_D)
        for x in (12, 18):
            p.dot(x, 24, TOOTH); p.dot(x, 23, TOOTH)
        for x in (14, 16):
            p.dot(x, 24, TOOTH_D)
    else:
        p.hline(11, 19, 21, MOUTH_D)
        for x in (11, 13, 15, 17, 19):
            p.dot(x, 21, TOOTH)
        for x in (12, 18):
            p.dot(x, 22, TOOTH)
    return p


# Pivot: the point a head's position refers to (middle of the skull), in the sprite.
# Socket: where the neck enters, relative to the pivot. Neck: the direction the neck leaves the
# socket, used for the last control point of the neck curve.
SIDE_PIVOT, SIDE_SOCKET, SIDE_NECK = (15, 11), (12, 9), (0.55, 0.85)
FRONT_PIVOT, FRONT_SOCKET, FRONT_NECK = (15, 12), (0, -5), (0.0, -1.0)


def heads() -> dict[str, tuple[Px, tuple[int, int], tuple[int, int], tuple[float, float]]]:
    out = {}
    for jaw, open_ in (("closed", False), ("open", True)):
        img = side_head(open_)
        out[f"side_{jaw}_l"] = (img, SIDE_PIVOT, SIDE_SOCKET, SIDE_NECK)
        out[f"side_{jaw}_r"] = (img.mirrored(), (SIDE_W - 1 - SIDE_PIVOT[0], SIDE_PIVOT[1]),
                                (-SIDE_SOCKET[0], SIDE_SOCKET[1]), (-SIDE_NECK[0], SIDE_NECK[1]))
    for state in ("closed", "open", "calm"):
        out[f"front_{state}"] = (front_head(state), FRONT_PIVOT, FRONT_SOCKET, FRONT_NECK)
    return out


# ---------------------------------------------------------------------------
# Neck segments. Each radius has an outline disc (drawn first under a whole neck) and a shaded
# fill (drawn second), so a neck reads as one tube with an outline only on its silhouette.
SEG_RADII = list(range(4, 12))


def _disc_mask(r: int, grow: float) -> tuple[int, set]:
    size = 2 * r + 3
    c = r + 1
    return size, {(x, y) for y in range(size) for x in range(size) if (x - c) ** 2 + (y - c) ** 2 <= (r + grow) ** 2}


def segment(r: int, kind: str) -> Px:
    size, m = _disc_mask(r, 1.2 if kind == "outline" else 0.25)
    p = Px(size, size)
    if kind == "outline":
        for (x, y) in m:
            p.dot(x, y, OUT)
        return p
    autoshade(p, m, HIDE, depth=max(2.0, r * 0.9), gain=1.0, lift=0.7 if kind == "fill" else 0.1)
    if kind == "scaled":
        # A band of scale marks: small dark crescents with a pale point above each.
        c = r + 1
        for i in range(-r + 2, r - 1, 3):
            y = c + int(round(r * 0.2)) + (1 if i % 2 else 0)
            if (c + i, y) in m and (c + i + 1, y) in m:
                p.dot(c + i, y, D2)
                p.dot(c + i + 1, y, D2)
                p.dot(c + i, y - 1, LIGHT)
    return p


def belly_plate(r: int) -> Px:
    """A strip of the pale underside, drawn down the middle of a neck on every disc: a dull
    stripe with a faint lighter edge on each plate."""
    w = max(3, r - 2)
    h = 3
    p = Px(w, h)
    p.hline(1, w - 2, 0, BELLY_D)
    p.rect(0, 1, w - 1, 2, BELLY_DD)
    p.dot(0, 2, DARK); p.dot(w - 1, 2, DARK)
    return p


# ---------------------------------------------------------------------------
# The body: three humps of her back out of the water (the root of the necks, two shoulders),
# a ridge of spines, the dark of the rest of her under the surface, and foam around her.
BODY_W, BODY_H = 176, 74
BODY_ANCHOR = (88, 68)    # the waterline, centre: the node origin in the game
NECK_X = [-60, -36, -12, 12, 36, 60]
HUMPS = [(48, 4, 128, 100), (6, 26, 86, 104), (90, 26, 170, 104)]   # back to front


def _hump_masks() -> list[set]:
    out = []
    for (x0, y0, x1, y1) in HUMPS:
        m = mask(BODY_W, BODY_H, lambda q, b=(x0, y0, x1, y1): q.ellipse(*b, OUT))
        out.append({(x, y) for (x, y) in m if y <= BODY_ANCHOR[1] + 2})
    return out


def _body_mask() -> set:
    m: set = set()
    for h in _hump_masks():
        m |= h
    return m


def body_top(m: set, x: int) -> int:
    ys = [y for (xx, y) in m if xx == x]
    return min(ys) if ys else BODY_ANCHOR[1]


def neck_bases() -> list[tuple[int, int]]:
    m = _body_mask()
    ax, ay = BODY_ANCHOR
    return [(dx, body_top(m, ax + dx) + 10 - ay) for dx in NECK_X]


def body() -> Px:
    p = Px(BODY_W, BODY_H)
    ax, ay = BODY_ANCHOR
    humps = _hump_masks()
    for k, m in enumerate(humps):
        autoshade(p, m, HIDE, depth=12, gain=1.2, lift=0.4 if k == 0 else 0.0)
        # Scales scattered over the hide: small dark crescents with a pale point.
        seed = 7 + k * 31
        for row, y in enumerate(range(4, ay - 8, 6)):
            for x in range(4 + (row % 2) * 5, BODY_W - 4, 9):
                seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
                if seed % 3 == 0:
                    continue
                jx = x + (seed >> 8) % 4 - 2
                if all((jx + dx, y + dy) in m for dx, dy in ((-1, 0), (4, 0), (1, 3))):
                    p.hline(jx, jx + 2, y + 1, D2)
                    p.dot(jx + 1, y, LIGHT if jx < ax else MID)
        if k > 0:
            # A dark seam where a shoulder rises in front of the root of the necks.
            for (x, y) in m:
                if (x, y - 1) not in m and (x, y - 1) in humps[0]:
                    p.dot(x, y, OUT)
                    p.dot(x, y + 1, D2)
    m = _body_mask()
    # Wet and darker where she meets the water.
    for (x, y) in m:
        if y > ay - 9:
            c = p.im.getpixel((x, y))
            if c in HIDE:
                p.dot(x, y, HIDE[max(0, HIDE.index(c) - (2 if y > ay - 4 else 1))])
    # A ridge of spines along the tops of the humps, between and beside the necks.
    for sx in range(-80, 81, 7):
        if any(abs(sx - nx) < 7 for nx in NECK_X):
            continue
        top_y = body_top(m, ax + sx)
        if top_y > ay - 6:
            continue
        h = 8 if abs(sx) < 40 else 6
        p.poly([(ax + sx - 3, top_y + 4), (ax + sx + 1, top_y - h), (ax + sx + 3, top_y + 4)], D2)
        p.dot(ax + sx, top_y - h + 3, MID)
    p.outline(OUT)
    return p


SHADOW_W, SHADOW_H = 264, 40
SHADOW_ANCHOR = (132, 14)


def shadow() -> Px:
    """The rest of her, dark under the water: a broad shape with a dithered edge."""
    p = Px(SHADOW_W, SHADOW_H)
    ax, ay = SHADOW_ANCHOR
    deep = rgb("#040d19")
    for y in range(SHADOW_H):
        for x in range(SHADOW_W):
            d = ((x - ax) / (SHADOW_W / 2 - 1)) ** 2 + ((y - ay) / (SHADOW_H - ay - 1)) ** 2 if y >= ay else                 ((x - ax) / (SHADOW_W / 2 - 1)) ** 2 + ((y - ay) / (ay + 0.5)) ** 2
            if d < 0.6 or (d < 0.85 and (x + y) % 2 == 0) or (d < 1.0 and x % 2 == 0 and y % 2 == 0):
                p.dot(x, y, deep)
    return p


FOAM_W, FOAM_H = 216, 22
FOAM_ANCHOR = (108, 4)


def foam(f: int) -> Px:
    """Foam churning round her where she breaks the surface: the near half of a ring, so it
    bows toward the viewer, with spray and a broken outer ripple. Four frames."""
    p = Px(FOAM_W, FOAM_H)
    ax, ay = FOAM_ANCHOR
    for x in range(2, FOAM_W - 2):
        dx = (x - ax) / 92.0
        if abs(dx) <= 1:
            bow = math.sqrt(max(0.0, 1 - dx * dx)) * 7
            wave = math.sin(x * 0.45 + f * 1.57) + 0.6 * math.sin(x * 0.17 - f * 1.57)
            y = ay + int(round(bow + wave * 1.1))
            if not ((x * 7 + f * 3) % 9 == 0 and abs(dx) > 0.6):
                thick = 2 if abs(dx) < 0.85 else 1
                p.vline(x, y, y + thick, FOAM if (x + f) % 7 else FOAM_D)
            if (x * 3 + f * 5) % 11 == 0 and abs(dx) < 0.9:
                p.dot(x, y - 2, FOAM)
            if (x * 5 + f * 3) % 13 == 0:
                p.dot(x, y + 4, FOAM_D)
        # The ripple further out, in pieces that shift each frame.
        rx = (x - ax) / 104.0
        if abs(rx) <= 1 and (x // 6 + f) % 3 != 0:
            y = ay + int(round(math.sqrt(max(0.0, 1 - rx * rx)) * 13)) + (1 if (x + f) % 4 == 0 else 0)
            if 0 <= y < FOAM_H:
                p.dot(x, y, FOAM_D)
    return p


def vial() -> Px:
    p = Px(9, 13)
    p.rect(3, 0, 5, 2, CORK)
    p.rect(2, 3, 6, 4, GLASS_D)
    p.ellipse(0, 4, 8, 12, GLASS)
    p.ellipse(2, 7, 6, 11, LIQUID)
    p.dot(2, 6, rgb("#ffffff"))
    p.outline(OUT)
    return p


# ---------------------------------------------------------------------------
# The neck rule, shared with scylla.gd: a cubic curve from the base to the head's socket, discs
# placed every SPACING pixels along it, thick at the base and thinner toward the head.
SPACING = 3.0
R_BASE, R_HEAD = 9, 4


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1])


def neck_chain(base, socket, neck_dir, bulge: float) -> list[tuple[int, int, int]]:
    """[(x, y, radius)] from the base to the socket. `bulge` bends the neck sideways (px)."""
    dx, dy = socket[0] - base[0], socket[1] - base[1]
    length = math.hypot(dx, dy) or 1.0
    px_, py_ = -dy / length, dx / length          # perpendicular, for the S-bend
    lean = base[0] / 70.0
    p1 = (base[0] + lean * length * 0.25 + px_ * bulge, base[1] - length * 0.45 + py_ * bulge)
    p2 = (socket[0] + neck_dir[0] * length * 0.4 - px_ * bulge * 0.5,
          socket[1] + neck_dir[1] * length * 0.4 - py_ * bulge * 0.5)
    pts = [_bezier(base, p1, p2, socket, i / 40) for i in range(41)]
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = cum[-1]
    out = []
    s = 0.0
    j = 0
    while s <= total:
        while j < len(cum) - 2 and cum[j + 1] < s:
            j += 1
        seg = cum[j + 1] - cum[j] or 1.0
        f = (s - cum[j]) / seg
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f
        r = int(round(R_BASE + (R_HEAD - R_BASE) * (s / total)))
        out.append((int(round(x)), int(round(y)), r))
        s += SPACING
    return out


# ---------------------------------------------------------------------------
# Atlas packing and the GDScript data file.

def parts() -> dict[str, tuple[Px, tuple[int, int]]]:
    """name -> (image, pivot). The pivot is the point the game positions."""
    out: dict[str, tuple[Px, tuple[int, int]]] = {}
    for r in SEG_RADII:
        for kind, key in (("outline", "o"), ("fill", "f"), ("scaled", "s")):
            out[f"seg_{key}{r}"] = (segment(r, kind), (r + 1, r + 1))
        plate = belly_plate(r)
        out[f"seg_b{r}"] = (plate, (plate.w // 2, plate.h // 2))
    for name, (img, pivot, _s, _n) in heads().items():
        out[name] = (img, pivot)
    out["body"] = (body(), BODY_ANCHOR)
    out["shadow"] = (shadow(), SHADOW_ANCHOR)
    for f in range(4):
        out[f"foam{f}"] = (foam(f), FOAM_ANCHOR)
    out["vial"] = (vial(), (4, 6))
    return out


def pack(items: dict[str, tuple[Px, tuple[int, int]]], width: int = 256):
    """Shelf packing, tallest first. Returns (image, {name: (x, y, w, h, pivot_x, pivot_y)})."""
    from PIL import Image
    width = max(width, (max(img.w for img, _p in items.values()) + 31) // 32 * 32)
    order = sorted(items, key=lambda n: (-items[n][0].h, n))
    x = y = shelf = 0
    regions = {}
    for name in order:
        img, (pvx, pvy) = items[name]
        if x + img.w > width:
            x, y, shelf = 0, y + shelf + 1, 0
        regions[name] = (x, y, img.w, img.h, pvx, pvy)
        x += img.w + 1
        shelf = max(shelf, img.h)
    height = (y + shelf + 31) // 32 * 32
    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for name, (rx, ry, _w, _h, _px, _py) in regions.items():
        atlas.alpha_composite(items[name][0].im, (rx, ry))
    return atlas, regions


def atlas_and_data():
    items = parts()
    atlas, regions = pack(items)
    lines = [
        "## GENERATED by tools/pixelart/scylla_big.py. Do not edit by hand.",
        "## Regions in scylla_parts.png: name -> [x, y, w, h, pivot_x, pivot_y]. The game draws a part",
        "## with its pivot on the position it computes. Plain arrays only (constant in exports).",
        'const TEXTURE := "res://assets/image_pipeline/generated/raw/%s"' % ATLAS_REL,
        "const REGIONS := {",
        *("\t\"%s\": [%s]," % (n, ", ".join(str(v) for v in regions[n])) for n in sorted(regions)),
        "}",
        "## Heads: name -> [socket_x, socket_y, neck_dir_x, neck_dir_y]. The neck enters at the socket",
        "## (relative to the pivot) and leaves it along neck_dir.",
        "const HEADS := {",
        *("\t\"%s\": [%d, %d, %.2f, %.2f]," % (n, s[0], s[1], d[0], d[1])
          for n, (_i, _p, s, d) in sorted(heads().items())),
        "}",
        "## Neck discs: seg_o<r> outline, seg_f<r> fill, seg_s<r> fill with scales, seg_b<r> belly plate,",
        "## r from SEG_MIN to SEG_MAX.",
        "const SEG_MIN := %d" % SEG_RADII[0],
        "const SEG_MAX := %d" % SEG_RADII[-1],
        "const SPACING := %.1f" % SPACING,
        "const R_BASE := %d" % R_BASE,
        "const R_HEAD := %d" % R_HEAD,
        "## Where the six necks leave the body, relative to the waterline (the node origin), left to right.",
        "const NECK_BASES := [%s]" % ", ".join("[%d, %d]" % b for b in neck_bases()),
    ]
    return atlas, regions, "\n".join(lines) + "\n"


def write_data() -> None:
    _atlas, _regions, text = atlas_and_data()
    OUT_GD.parent.mkdir(parents=True, exist_ok=True)
    OUT_GD.write_text(text, encoding="utf-8")


def scylla_images():
    atlas, _regions, _text = atlas_and_data()
    return {ATLAS_REL: atlas}


if __name__ == "__main__":
    from px import preview, save
    out = Path(__file__).parent / "preview"
    atlas, regions, text = atlas_and_data()
    save(preview(atlas, 4, bg=(70, 80, 90, 255)), out / "scylla_parts_x4.png")
    print(text[:400])
