"""Scylla's strait: the cliff face, the whirlpool across the water, and banks of mist.

    python tools/pixelart/cove_scene.py     # previews, including the scene as the game frames it

The cliff is one image laid over the north of the cove (rows 64-73): rock slabs shaded from the
upper left, a cave at the waterline, wet rock and foam at its foot. The whirlpool is an 8-frame
loop; the mist banks are pale dithered shapes the game draws half-transparent and drifts.
`scene_preview()` composes the cove the way world.gd and scylla.gd do, for checking art here.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image

from px import Px, rgb
from shading import mask, autoshade

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "assets/image_pipeline/generated/raw"
PREVIEW = Path(__file__).parent / "preview"

CLIFF_REL = "sprites/entities/cove_cliff.png"
WHIRLPOOL_REL = "sprites/entities/whirlpool.png"
MIST_REL = "sprites/entities/mist_banks.png"

# World placement (world.gd reads the same numbers from its constants).
CLIFF_POS = (0, 2056)          # top-left of the cliff image in the world
CLIFF_W, CLIFF_H = 544, 292
WHIRL_W, WHIRL_H, WHIRL_FRAMES = 150, 60, 8
WHIRL_CENTER = (96, 2404)

# Warm grey stone, a step lighter than Scylla's slate so she stands out against it.
CLIFF = [rgb(h) for h in ("#120f11", "#1e1a1c", "#2b2628", "#3a3436", "#4c4545", "#605756", "#776c67", "#918479")]
CAVE = rgb("#060507")
CAVE_D = rgb("#0d0b0d")
WEED = rgb("#1b2b22")
WEED_L = rgb("#2b4232")
GRASS = rgb("#6a6640")
GRASS_D = rgb("#48462c")
GUANO = rgb("#a39a8c")
FOAM = rgb("#e4f1f4")
FOAM_D = rgb("#9fc0c8")
SEA = [rgb(h) for h in ("#02060c", "#051427", "#0a2440", "#103a5e", "#1b5e86")]
MIST = rgb("#d6dee3")


def _noise(seed: int, n: int = 64):
    rng = random.Random(seed)
    vals = [rng.random() for _ in range(n + 1)]

    def f(x: float) -> float:
        i = int(math.floor(x)) % n
        t = x - math.floor(x)
        t = t * t * (3 - 2 * t)
        return vals[i] * (1 - t) + vals[i + 1] * t
    return f


def _cells(W: int, H: int, rng: random.Random, sx: int = 26, sy: int = 46):
    """Rock slabs as stretched Voronoi cells: each pixel belongs to the nearest seed, measured
    with vertical distance counted less, so the slabs come out tall like sea-cliff columns."""
    seeds = {}
    for gy in range(-1, H // sy + 2):
        for gx in range(-1, W // sx + 2):
            seeds[(gx, gy)] = (gx * sx + rng.uniform(0, sx), gy * sy + rng.uniform(0, sy))
    owner = {}
    for y in range(H):
        gy = int(y // sy)
        for x in range(W):
            gx = int(x // sx)
            best, bd = None, 1e9
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    k = (gx + dx, gy + dy)
                    if k not in seeds:
                        continue
                    px_, py_ = seeds[k]
                    d = (x - px_) ** 2 + ((y - py_) * 0.42) ** 2
                    if d < bd:
                        best, bd = k, d
            owner[(x, y)] = best
    cells: dict = {}
    for xy, k in owner.items():
        cells.setdefault(k, set()).add(xy)
    return cells, seeds


def cliff() -> Px:
    W, H = CLIFF_W, CLIFF_H
    p = Px(W, H)
    rng = random.Random(41)
    n1, n2, n3 = _noise(3), _noise(9), _noise(17)
    lip = [int(12 + 7 * n1(x / 23.0) + 3 * n2(x / 7.0)) for x in range(W)]
    base = [int(H - 6 + 2 * n2(x / 11.0)) for x in range(W)]
    face = {(x, y) for x in range(W) for y in range(lip[x], base[x])}

    # Slabs, each shaded on its own; the pixels between them stay dark as cracks. Light falls
    # from above, so the face darkens toward the sea, and a slow noise pushes whole buttresses
    # forward (lighter) or back into shadow.
    cells, seeds = _cells(W, H, rng, sx=42, sy=64)
    cracked = {k: rng.random() < 0.55 for k in cells}
    for k, m in cells.items():
        # Only some slabs are split from their neighbours by a crack; the rest just change tone.
        if cracked[k]:
            m = {(x, y) for (x, y) in m if all((x + dx, y + dy) in m for dx, dy in ((1, 0), (0, 1)))}
        m &= face
        if len(m) < 6:
            continue
        cx_, cy_ = seeds[k]
        lift = 1.4 - 2.6 * (cy_ / H) + 1.8 * (n3(cx_ / 80.0) - 0.5) + rng.uniform(-0.3, 0.3)
        autoshade(p, m, CLIFF, depth=12, lift=lift, gain=0.8)
    for (x, y) in face:
        if p.im.getpixel((x, y))[3] == 0:
            p.dot(x, y, CLIFF[1] if n2(x / 5.0 + y / 9.0) > 0.4 else CLIFF[2])

    # Short ledges: a lit edge with a shadow under it, each at its own slight slant.
    ledges = []
    for _ in range(22):
        lx, ly = rng.randint(0, W - 20), rng.randint(46, 236)
        length, slope = rng.randint(14, 48), rng.uniform(-0.18, 0.18)
        ledges.append((lx, ly))
        for i in range(length):
            x, y = lx + i, ly + int(round(i * slope))
            if (x, y) in face and (x, y + 2) in face:
                p.dot(x, y, CLIFF[6])
                p.dot(x, y + 1, CLIFF[1])
                p.dot(x, y + 2, CLIFF[2])

    # The lip catches the light; dry grass hangs over it here and there.
    for x in range(W):
        p.dot(x, lip[x], CLIFF[7])
        p.dot(x, lip[x] + 1, CLIFF[6])
        if n2(x / 3.0) > 0.78:
            p.vline(x, lip[x] - 2, lip[x], GRASS)
            p.dot(x, lip[x] + 2, GRASS_D)

    # White streaks under some ledges, where birds that do not know better roost.
    for _ in range(12):
        lx, ly = rng.choice(ledges)
        gx, gy = lx + rng.randint(2, 12), ly + 3
        if (gx, gy) in face:
            for k in range(rng.randint(5, 14)):
                if (gx, gy + k) in face and k % 4 != 3:
                    p.dot(gx, gy + k, GUANO)

    # The cave she came out of: a ragged black arch at the waterline behind her.
    cx, top, bot = 272, 168, H
    cave = set()
    for y in range(top, bot):
        t = (y - top) / (bot - top)
        half = int(8 + 64 * math.sqrt(t) + 4 * n1(y / 5.0))
        for x in range(cx - half, cx + half + 1):
            cave.add((x, y))
    cave &= face
    rim = {(x, y) for (x, y) in cave if any((x + dx, y + dy) not in cave for dx, dy in ((2, 0), (-2, 0), (0, -2)))}
    for (x, y) in cave:
        p.dot(x, y, CAVE_D if (x, y) in rim else CAVE)
    for i in range(-5, 6):                                  # teeth of rock along the arch
        sx = cx + i * 11
        sy = top + int(max(0.0, (abs(i * 11) - 8) / 64.0) ** 2 * (bot - top)) + 3
        p.poly([(sx - 3, sy - 2), (sx + 3, sy - 2), (sx + rng.randint(-1, 1), sy + rng.randint(5, 9))], CLIFF[2])

    # Wet foot of the cliff: darker, weed hanging in strands, foam where the sea hits it.
    for (x, y) in face:
        d = base[x] - y
        if d <= 18 and (x, y) not in cave:
            c = p.im.getpixel((x, y))
            if c in CLIFF:
                p.dot(x, y, CLIFF[max(0, CLIFF.index(c) - (3 if d < 8 else 2))])
    for x in range(0, W, 3):
        if n1(x / 4.0) > 0.45 and not (cx - 70 < x < cx + 70):
            ln = int(4 + 9 * n2(x / 2.0))
            for k in range(ln):
                p.dot(x + (k // 4) % 2, base[x] - 18 + k + 6, WEED if k % 3 else WEED_L)
    for x in range(W):
        y = base[x] - 1
        p.dot(x, y, FOAM if (x * 7) % 5 else FOAM_D)
        if (x * 13) % 7 < 3:
            p.dot(x, y - 1, FOAM)
        if (x * 11) % 9 == 0:
            p.dot(x, y + 1, FOAM_D)
    return p


def whirlpool(f: int) -> Px:
    """Charybdis: a spiral of foam turning into a black hole in the water, frame f of 8."""
    W, H = WHIRL_W, WHIRL_H
    p = Px(W, H)
    cx, cy = W / 2 - 0.5, H / 2 - 0.5
    a, b = W / 2 - 1, H / 2 - 1
    phase = f / WHIRL_FRAMES * 2 * math.pi / 3
    for y in range(H):
        for x in range(W):
            ex, ey = (x - cx) / a, (y - cy) / b
            r = math.hypot(ex, ey)
            if r > 1.0:
                continue
            th = math.atan2(ey, ex)
            s = math.sin(3 * th + 5.5 * math.log(r + 0.04) + phase * 3)
            # Rings of water, darker toward the throat; the near side of the funnel falls away.
            ring = 4 if r > 0.82 else 3 if r > 0.6 else 2 if r > 0.38 else 1 if r > 0.17 else 0
            if ey > 0 and r < 0.5:
                ring = max(0, ring - 1)
            if r > 0.9 and s < 0.5:
                continue                                    # ragged outer edge melts into the sea
            col = SEA[ring]
            if 0.15 < r < 0.95 and s > 0.62:
                col = FOAM if s > 0.86 and r > 0.3 else FOAM_D
            elif 0.2 < r < 0.9 and s > 0.35:
                col = SEA[min(4, ring + 1)]
            p.dot(x, y, col)
    return p


MIST_SIZES = [(420, 30), (300, 22), (480, 40)]


def mist_bank(i: int) -> Px:
    """A long wisp of fog with a dithered edge; the game draws it at about a quarter opacity."""
    W, H = MIST_SIZES[i]
    p = Px(W, H)
    na, nb, nc = _noise(200 + i), _noise(300 + i), _noise(400 + i)
    for x in range(W):
        u = x / (W - 1)
        taper = min(1.0, u / 0.25, (1 - u) / 0.25)
        centre = H / 2 + (H * 0.22) * (na(x / 50.0) - 0.5) * 2
        half = (H / 2 - 1) * taper * (0.35 + 0.65 * nb(x / 38.0))
        for y in range(H):
            if half <= 0:
                continue
            d = 1 - abs(y - centre) / half
            d += 0.25 * (nc(x / 9.0 + y / 4.0) - 0.5)
            if d > 0.55 or (d > 0.3 and (x + y) % 2 == 0) or (d > 0.08 and x % 2 == 0 and y % 2 == 0):
                p.dot(x, y, MIST)
    return p


def mist_sheet() -> Image.Image:
    w = max(s[0] for s in MIST_SIZES)
    h = sum(s[1] for s in MIST_SIZES)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for i, (_w, mh) in enumerate(MIST_SIZES):
        out.alpha_composite(mist_bank(i).im, (0, y))
        y += mh
    return out


def whirlpool_sheet() -> Image.Image:
    out = Image.new("RGBA", (WHIRL_W * WHIRL_FRAMES, WHIRL_H), (0, 0, 0, 0))
    for f in range(WHIRL_FRAMES):
        out.alpha_composite(whirlpool(f).im, (f * WHIRL_W, 0))
    return out


def cove_images() -> dict[str, Image.Image]:
    return {CLIFF_REL: cliff().im, WHIRLPOOL_REL: whirlpool_sheet(), MIST_REL: mist_sheet()}


# ---------------------------------------------------------------------------
# Preview of the scene as the game frames it at the point (for tuning art and poses here).

def scene_preview(pose: str = "idle", t: float = 0.0) -> Image.Image:
    import scylla_big as S
    import scylla_pose as P
    view_top = 2048
    view = Image.new("RGBA", (544, 620), (0, 0, 0, 255))
    ground = Image.open(PREVIEW / "map_cove.png").convert("RGBA")
    view.alpha_composite(ground.crop((0, view_top - 1984, 544, view_top - 1984 + 620)))

    def put(img: Image.Image, x: int, y: int, alpha: float = 1.0) -> None:
        if alpha < 1.0:
            img = img.copy()
            a = img.getchannel("A").point(lambda v: int(v * alpha))
            img.putalpha(a)
        view.alpha_composite(img, (x, y - view_top)) if 0 <= y - view_top < 620 and x >= 0 else \
            _paste_clipped(view, img, x, y - view_top)

    banks = mist_sheet()
    def bank(i):
        y0 = sum(s[1] for s in MIST_SIZES[:i])
        return banks.crop((0, y0, MIST_SIZES[i][0], y0 + MIST_SIZES[i][1]))
    put(bank(2), 120, 2060, 0.30)
    put(cliff().im, *CLIFF_POS)
    put(bank(0), 300, 2300, 0.25)
    w = whirlpool(0).im
    put(w, WHIRL_CENTER[0] - WHIRL_W // 2, WHIRL_CENTER[1] - WHIRL_H // 2)

    atlas, regions, _ = S.atlas_and_data()
    origin = P.ORIGIN
    for name, x, y in P.draw_list(pose, t):
        rx, ry, rw, rh, pvx, pvy = regions[name]
        put(atlas.crop((rx, ry, rx + rw, ry + rh)), origin[0] + x - pvx, origin[1] + y - pvy)

    circe = Image.open(RAW / "sprites/characters/circe/circe_idle.png").convert("RGBA").crop((0, 64, 64, 128))
    cx, cy = 272, 2508
    put(circe, cx - 32, cy - 12 - 32)
    put(bank(1), 40, 2150, 0.32)
    put(bank(0), 280, 2110, 0.28)
    return view


def _paste_clipped(dst: Image.Image, img: Image.Image, x: int, y: int) -> None:
    sx, sy = max(0, -x), max(0, -y)
    crop = img.crop((sx, sy, img.width, img.height))
    if crop.width and crop.height:
        dst.alpha_composite(crop, (max(0, x), max(0, y)))


if __name__ == "__main__":
    from px import preview, save
    save(preview(cliff().im, 2, bg=(20, 30, 50, 255)), PREVIEW / "cove_cliff_x2.png")
    save(preview(whirlpool_sheet(), 3, bg=(7, 30, 55, 255)), PREVIEW / "whirlpool_x3.png")
    save(preview(mist_sheet(), 2, bg=(30, 40, 60, 255)), PREVIEW / "mist_banks_x2.png")
    for pose in ("idle", "descend", "strike"):
        img = scene_preview(pose)
        save(img.resize((img.width * 2, img.height * 2), Image.Resampling.NEAREST), PREVIEW / f"scene_{pose}_x2.png")
    print("ok")
