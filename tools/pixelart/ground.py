"""Aiaia's ground, painted as one picture and cut into unique 32-px tiles.

The island used to be laid from four LPC grass tiles, which are 97 % one flat lime green, so the
whole island read as one bright field. Here the ground is painted the way the title painting
(prologue_07) looks: olive and sage grass in soft patches with blades and tufts, a path of pale
flagstones with grass in the joints, and clumps of lavender, white and yellow flowers along
the path and the fences. The LPC overlays (beach, sea, farm beds, Hermes' terrace) are laid on
top as before, and any LPC grass pixels left on their edges are recoloured to the painted grass.

Called by worldmap.py, which writes the tiles to tilesets/aiaia_ground_32.png and the cell
references to game/data/world_map.gd.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

import paint
import coast
import yard
from paint import hexc

T = 32

# Grass, dark to light: olive in the shade, sage and warm olive in the sun (chosen to sit with
# the title painting's warm light, not copied from it, since the painting is tinted lilac).
OLIVE = [hexc("#46511f"), hexc("#56632a"), hexc("#677534"), hexc("#7a873e"), hexc("#8e994b"), hexc("#a5aa5c")]
SAGE = [hexc("#475236"), hexc("#57643f"), hexc("#69774b"), hexc("#7c8a57"), hexc("#909c66"), hexc("#a7ae78")]
# LPC grass colours that may be left on overlay edges -> ramp step to use instead.
LPC_GREENS = {(61, 123, 1): 2, (133, 161, 5): 3, (133, 161, 6): 3, (191, 218, 63): 4, (19, 87, 40): 0}

STONE_BASES = [hexc("#b3a68c"), hexc("#a89b82"), hexc("#bcae93"), hexc("#a3967d"), hexc("#b0a48f"), hexc("#b9a585"),
               hexc("#9f9686")]
STONE_DARK = hexc("#7a705f")
STONE_LIGHT = hexc("#cbc1ab")
STONE_HI = hexc("#dcd2bc")
LEAF = [hexc("#3c4719"), hexc("#4d5a22"), hexc("#5d6b2b"), hexc("#728036")]
LAVENDER_LEAF = [hexc("#46503a"), hexc("#5f6c4f"), hexc("#76856a"), hexc("#94a389")]


class Ground:
    def __init__(self, w: int, h: int, seed: int = 7):
        self.w, self.h = w, h
        self.rng = np.random.default_rng(seed)
        # Fields 0..1: how sunlit the grass is (picks its tone) and where it turns sage.
        self.light = paint.fractal_noise(w, h, (150, 60, 22), (0.55, 0.3, 0.15), seed=seed)
        self.sage = paint.fractal_noise(w, h, (190, 70), (0.7, 0.3), seed=seed + 5)
        self.img = np.zeros((h, w, 4), dtype=np.uint8)
        self.grass_ok = np.ones((h, w), dtype=bool)    # where flowers and tufts may grow

    # ---- grass ---------------------------------------------------------------------------
    def grass_colour(self, step, ys, xs) -> np.ndarray:
        olive = np.array(OLIVE, dtype=float)
        sage = np.array(SAGE, dtype=float)
        step = np.asarray(step, dtype=float)
        lo = np.clip(np.floor(step), 0, len(OLIVE) - 1).astype(int)
        hi = np.clip(lo + 1, 0, len(OLIVE) - 1)
        fr = np.clip(step - np.floor(step), 0, 1)[..., None]
        # Sage patches with crisp edges (dithered borders read as smudges), mixed in lightly.
        mix = (self.sage[ys, xs] > 0.6).astype(float) * 0.45
        o = olive[lo] * (1 - fr) + olive[hi] * fr
        g = sage[lo] * (1 - fr) + sage[hi] * fr
        c = o * (1 - mix[..., None]) + g * mix[..., None]
        return c[..., :3]

    def _colour_at(self, step: float, x: int, y: int) -> np.ndarray:
        y = min(self.h - 1, max(0, y)); x = min(self.w - 1, max(0, x))
        return self.grass_colour(np.array(step), np.array(y), np.array(x)).astype(np.uint8)

    # Grass tufts as small shapes ('d' dark, 'm' mid-dark, 'l' lit), drawn with their root on the
    # bottom row. Distinct shapes a few pixels wide read as grass at game scale; single pixels
    # read as noise.
    TUFTS = [
        ["..l..", "d.m.d", ".ddd."],
        ["l...", "m.d.", ".dd."],
        ["...l", ".d.m", ".dd."],
        ["m.d", ".d."],
        [".l.", "d.d", ".d."],
        ["d..m", ".dd."],
        [".l..l.", "m.dd.d", ".dddd."],
    ]
    TALL = [
        ["..l...", "..m.l.", "d.m.d.", ".dmd..", "..d..."],
        ["l....", "m..l.", "m.dm.", "dd.d.", ".ddd."],
        [".l.l.", ".m.m.", "dm.md", ".ddd."],
    ]

    def stamp(self, x: int, y: int, shape: list[str], base: float) -> None:
        h = len(shape)
        cols = {"d": self._colour_at(base - 1.9, x, y), "m": self._colour_at(base - 1.0, x, y),
                "l": self._colour_at(base + 1.6, x, y)}
        for j, row in enumerate(shape):
            for i, ch in enumerate(row):
                if ch != ".":
                    self._px(x + i - len(row) // 2, y - (h - 1 - j), cols[ch])

    def paint_grass(self) -> None:
        h, w = self.h, self.w
        ys, xs = np.mgrid[0:h, 0:w]
        # Three tones of grass in broad patches of sun and shade. Where two tones meet they are
        # dithered across a narrow band, as a pixel artist would blend them.
        f = self.light * 2.0                        # 0..2: shade, grass, sun
        lo = np.floor(np.clip(f, 0, 1.999))
        frac = f - lo
        blend = np.clip((frac - 0.5) * 5 + 0.5, 0, 1)
        tone = lo + (blend > paint.bayer(w, h)).astype(float)
        step = np.choose(tone.astype(int), [2.3, 3.0, 3.7])
        self.step = step
        self.img[..., :3] = self.grass_colour(step, ys, xs).astype(np.uint8)
        self.img[..., 3] = 255
        rng = self.rng
        # Patches of taller, denser grass.
        clump = paint.fractal_noise(w, h, (34, 14), (0.7, 0.3), seed=97)
        self.clump = clump
        # A close, even texture of small tufts everywhere...
        for gy in range(0, h, 6):
            off = (gy // 6) % 2 * 4
            for gx in range(off, w, 8):
                dense = clump[min(h - 1, gy), min(w - 1, gx)] > 0.72
                if rng.random() > (0.95 if dense else 0.78):
                    continue
                x = gx + int(rng.integers(0, 5))
                y = gy + int(rng.integers(0, 4))
                if not (3 <= x < w - 4 and 5 <= y < h):
                    continue
                pool = self.TALL if (dense and rng.random() < 0.6) else self.TUFTS
                shape = pool[int(rng.integers(0, len(pool)))]
                self.stamp(x, y, shape, float(step[y, x]) - (0.3 if dense else 0.0))
        # ...and sun-flecks: a lit pixel pair here and there.
        for _ in range(w * h // 260):
            x, y = int(rng.integers(2, w - 2)), int(rng.integers(2, h - 2))
            c = self._colour_at(float(step[y, x]) + 1.4, x, y)
            self._px(x, y, c); self._px(x + 1, y, self._colour_at(float(step[y, x]) + 0.7, x, y))

    def _px(self, x: int, y: int, c) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img[y, x, :3] = np.asarray(c)[:3]
            self.img[y, x, 3] = 255

    def _blend(self, x: int, y: int, c, a: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            d = self.img[y, x, :3].astype(float)
            self.img[y, x, :3] = np.clip(d * (1 - a) + np.asarray(c[:3], dtype=float) * a, 0, 255).astype(np.uint8)

    def _darken(self, x: int, y: int, f: float) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img[y, x, :3] = (self.img[y, x, :3].astype(float) * f).astype(np.uint8)

    def tuft(self, x: int, y: int, tall: int = 4) -> None:
        """A taller clump of three blades rooted at (x, y), for breaking hard edges."""
        s = float(self.step[min(self.h - 1, max(0, y)), min(self.w - 1, max(0, x))])
        dark, mid, light = self._colour_at(s - 1.5, x, y), self._colour_at(s - 0.5, x, y), self._colour_at(s + 1.2, x, y)
        for i in range(tall):
            self._px(x, y - i, dark if i < 2 else mid)
        for i in range(tall - 1):
            self._px(x - 1 - i // 2, y - i, dark if i < 1 else mid)
            self._px(x + 1 + i // 2, y - i, dark if i < 1 else mid)
        self._px(x, y - tall, light)
        self._px(x + 1 + (tall - 2) // 2, y - tall + 1, light)

    # ---- recolour what the LPC overlays left -----------------------------------------------
    def recolour_lpc_greens(self, region: np.ndarray) -> None:
        ys, xs = np.nonzero(region)
        if len(ys) == 0:
            return
        rgb = self.img[ys, xs, :3]
        for col, step in LPC_GREENS.items():
            m = np.all(rgb == np.array(col, dtype=np.uint8), axis=-1)
            if m.any():
                c = self.grass_colour(np.full(m.sum(), step), ys[m], xs[m])
                self.img[ys[m], xs[m], :3] = c.astype(np.uint8)

    # ---- flagstone path --------------------------------------------------------------------
    def flagstones(self, left, right, y0: int, y1: int, fade_from: int | None = None) -> None:
        """Lay pale flagstones between left(y) and right(y): rows of irregular slabs with grass
        in the joints. Near the edges they thin out, so the path has a soft, broken edge; below
        `fade_from` they thin out towards y1, where the path runs into the beach."""
        rng = self.rng
        y = y0
        while y < y1:
            rh = int(rng.integers(10, 20))
            x = int(left(y)) - int(rng.integers(2, 14))
            while x < right(y) + 6:
                sw = int(rng.choice([15, 17, 20, 23, 26, 30, 34]))
                cx, cy = x + sw / 2, y + rh / 2
                L, R = left(cy), right(cy)
                inset = min(cx - L, R - cx)
                keep = 0.97 if inset > 10 else (0.7 if inset > 4 else (0.3 if inset > 0 else 0.0))
                if getattr(self, "hard_edge", None) and self.hard_edge(cy) and (x < L - 1 or x + sw > R + 1):
                    keep = 0.0                              # never under a fence post at the gap
                if fade_from is not None and cy > fade_from:
                    keep *= max(0.0, 1 - (cy - fade_from) / max(1, y1 - fade_from)) * 0.9
                if rng.random() < keep:
                    dy = int(rng.integers(-1, 2))
                    self.stone(x, y + dy, sw - 2, rh - 2 - abs(dy))
                x += sw
            y += rh

    def stone(self, x0: int, y0: int, w: int, h: int) -> None:
        rng = self.rng
        if w < 6 or h < 6:
            return
        m = np.ones((h, w), dtype=bool)
        # Each corner cut by its own amount, so the slabs are irregular, not pills.
        for (cx, cy, sx, sy) in ((0, 0, 1, 1), (w - 1, 0, -1, 1), (0, h - 1, 1, -1), (w - 1, h - 1, -1, -1)):
            r = int(rng.integers(1, 4))
            for dy in range(r):
                for dx in range(r - dy):
                    m[cy + sy * dy, cx + sx * dx] = False
        for _ in range(int(rng.integers(0, 3))):          # a chip out of one edge
            if rng.random() < 0.5:
                yy = 0 if rng.random() < 0.5 else h - 1
                x = int(rng.integers(2, w - 3))
                m[yy, x:x + int(rng.integers(1, 4))] = False
            else:
                xx = 0 if rng.random() < 0.5 else w - 1
                y = int(rng.integers(2, h - 3))
                m[y:y + int(rng.integers(1, 3)), xx] = False
        base = np.array(STONE_BASES[int(rng.integers(0, len(STONE_BASES)))][:3], dtype=float)
        base = base * (0.95 + rng.random() * 0.08)
        # Shadow on the turf under the slab's bottom and right edge (it sits sunk in the grass).
        for yy in range(h):
            for xx in range(w):
                if m[yy, xx]:
                    if yy + 1 >= h or not m[yy + 1, xx]:
                        self._darken(x0 + xx, y0 + yy + 1, 0.5)
                    if xx + 1 >= w or not m[yy, xx + 1]:
                        self._darken(x0 + xx + 1, y0 + yy, 0.64)
        tex = paint.value_noise(w, h, 5, int(rng.integers(0, 1 << 30)))
        for yy in range(h):
            for xx in range(w):
                if not m[yy, xx]:
                    continue
                top = yy == 0 or not m[yy - 1, xx]
                lft = xx == 0 or not m[yy, xx - 1]
                bot = yy == h - 1 or not m[yy + 1, xx]
                rgt = xx == w - 1 or not m[yy, xx + 1]
                if bot or rgt:
                    c = np.array(STONE_DARK[:3], dtype=float)
                elif top or lft:
                    c = np.array(STONE_LIGHT[:3], dtype=float)
                else:
                    t = tex[yy, xx]
                    c = base * (0.9 if t < 0.3 else (1.0 if t < 0.75 else 1.06))
                self._px(x0 + xx, y0 + yy, np.clip(c, 0, 255).astype(np.uint8))
        # Wear: a few pits, a sunlit corner, sometimes a hairline crack or moss at a corner.
        for _ in range(int(rng.integers(1, 4))):
            px, py = x0 + int(rng.integers(2, w - 2)), y0 + int(rng.integers(2, h - 2))
            self._blend(px, py, STONE_DARK, 0.5)
            self._blend(px - 1, py - 1, STONE_LIGHT, 0.4)
        for i in range(2):
            self._px(x0 + 2 + i, y0 + 1, np.array(STONE_HI[:3], dtype=np.uint8))
        if w > 16 and rng.random() < 0.3:
            cx = x0 + int(rng.integers(5, w - 5))
            for i in range(int(rng.integers(3, h - 1))):
                self._blend(cx + (i // 3), y0 + 1 + i, STONE_DARK, 0.75)
        if rng.random() < 0.3:
            mx = x0 + (1 if rng.random() < 0.5 else w - 3)
            for i in range(int(rng.integers(2, 5))):
                self._px(mx + (i % 2), y0 + h - 2 - i // 2, np.array(OLIVE[2 + i % 2][:3], dtype=np.uint8))
        self.grass_ok[max(0, y0 - 1):y0 + h + 1, max(0, x0 - 1):x0 + w + 1] = False

    # ---- flowers ---------------------------------------------------------------------------
    def flower(self, x: int, y: int, kind: str) -> None:
        """One bloom centred at (x, y): a cross of petals round a centre, the lower petal in
        shade; some open wider. Every bloom is at least 3 px across, so none reads as a stray
        pixel at game scale."""
        petal, shade, centre = {
            "white": (hexc("#f6f2e4"), hexc("#cdc6b2"), hexc("#e9b941")),
            "yellow": (hexc("#f5d250"), hexc("#c69b2c"), hexc("#d27a2a")),
            "pink": (hexc("#eda7c4"), hexc("#b96f93"), hexc("#f8e6a8")),
            "lilac": (hexc("#c0abe8"), hexc("#8f78bf"), hexc("#f4e6a4")),
        }[kind]
        self._px(x, y - 1, petal); self._px(x - 1, y, petal); self._px(x + 1, y, petal)
        self._px(x, y, centre)
        self._px(x, y + 1, shade)
        if self.rng.random() < 0.45:
            self._px(x - 1, y - 1, petal); self._px(x + 1, y + 1, shade)

    def spike(self, x: int, y: int, tall: int, lean: int = 0) -> None:
        """A lavender stem rooted at (x, y): grey-green stalk, then purple florets to a pale tip."""
        ramp = [hexc("#5a4790"), hexc("#7c64b8"), hexc("#9d86d4"), hexc("#c4b3ee")]
        stem = hexc("#6f7d58")
        self._px(x, y, stem); self._px(x, y - 1, stem)
        for i in range(tall):
            xx = x + (lean if i >= tall // 2 else 0)
            self._px(xx, y - 2 - i, ramp[2] if i % 2 else ramp[1])
            if 0 < i < tall - 1:
                self._px(xx + 1, y - 2 - i, ramp[0])
        self._px(x + lean, y - 2 - tall, ramp[3])

    def mound(self, cx: int, cy: int, rx: int, ry: int, ramp: list) -> None:
        """A low leafy mound (the plant under a clump of flowers): dark at its foot, lit on top."""
        for yy in range(-ry, ry + 1):
            for xx in range(-rx, rx + 1):
                d = (xx / (rx + 0.5)) ** 2 + (yy / (ry + 0.5)) ** 2
                if d > 1:
                    continue
                if yy >= ry - 1 or (d > 0.8 and yy > 0):
                    k = 0
                elif yy < -ry + 2 and (xx + yy) % 2 == 0:
                    k = 3
                else:
                    k = 1 if (xx * 3 + yy * 5) % 4 else 2
                self._px(cx + xx, cy + yy, ramp[k])
        for xx in range(-rx + 1, rx):                     # its shadow on the grass
            self._darken(cx + xx, cy + ry + 1, 0.66)

    def free(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        if x0 < 0 or y0 < 0 or x1 > self.w or y1 > self.h:
            return False
        return bool(self.grass_ok[y0:y1, x0:x1].all())

    def claim(self, x0: int, y0: int, x1: int, y1: int) -> None:
        self.grass_ok[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = False

    def flower_clump(self, cx: int, cy: int, kind: str, blooms: int) -> bool:
        """A clump of one kind of flower on a leafy mound, 9-15 px across."""
        rng = self.rng
        rx, ry = int(rng.integers(5, 9)), int(rng.integers(3, 5))
        if not self.free(cx - rx - 1, cy - ry - 4, cx + rx + 2, cy + ry + 3):
            return False
        self.mound(cx, cy, rx, ry, LEAF)
        for _ in range(blooms):
            x = cx + int(rng.integers(-rx + 1, rx))
            y = cy + int(rng.integers(-ry - 1, ry))
            self.flower(x, y, kind)
        self.claim(cx - rx - 1, cy - ry - 4, cx + rx + 2, cy + ry + 3)
        return True

    def lavender_bush(self, cx: int, cy: int, spikes: int = 8) -> bool:
        """A clump of lavender: a silvery grey-green base with purple spikes standing out of it."""
        rng = self.rng
        rx, ry = int(rng.integers(6, 10)), 3
        if not self.free(cx - rx - 1, cy - 12, cx + rx + 2, cy + ry + 3):
            return False
        self.mound(cx, cy, rx, ry, LAVENDER_LEAF)
        for i in range(spikes):
            x = cx - rx + 1 + int(round(i * (2 * rx - 2) / max(1, spikes - 1))) + int(rng.integers(-1, 2))
            tall = int(rng.integers(4, 7)) + (2 if abs(x - cx) < rx / 2 else 0)
            lean = -1 if x < cx - 2 else (1 if x > cx + 2 else 0)
            self.spike(x, cy - 1 + int(rng.integers(0, 2)), tall, lean if rng.random() < 0.6 else 0)
        self.claim(cx - rx - 1, cy - 12, cx + rx + 2, cy + ry + 3)
        return True

    def daisies(self, cx: int, cy: int, n: int, kinds: list[str], spread: int = 7) -> None:
        """Loose wildflowers in the grass, each on a short dark stem."""
        rng = self.rng
        for _ in range(n * 3):
            if n <= 0:
                break
            x = cx + int(rng.normal(0, spread * 0.6))
            y = cy + int(rng.normal(0, spread * 0.4))
            if not self.free(x - 2, y - 2, x + 3, y + 4):
                continue
            stem = self._colour_at(0, x, y)
            self._px(x, y + 2, stem); self._px(x - 1, y + 2, stem)
            self.flower(x, y, kinds[int(rng.integers(0, len(kinds)))])
            self.claim(x - 1, y - 1, x + 2, y + 3)
            n -= 1

    def clover(self, cx: int, cy: int, n: int) -> None:
        """A patch of clover: small three-leaf sprigs, brighter than the grass, in a loose cluster."""
        rng = self.rng
        for _ in range(n):
            x = cx + int(rng.normal(0, 5)); y = cy + int(rng.normal(0, 3))
            if not self.free(x - 2, y - 2, x + 3, y + 2):
                continue
            hi, mid, lo = hexc("#9fb257"), hexc("#80963f"), hexc("#55682a")
            self._px(x, y - 1, hi); self._px(x - 1, y, mid); self._px(x + 1, y, mid); self._px(x, y, lo)
            self._px(x, y + 1, lo)
        self.claim(cx - 8, cy - 5, cx + 9, cy + 5)

    def worn(self, cx: int, cy: int, rx: int, ry: int) -> None:
        """A worn spot of bare earth where feet have rubbed the grass away."""
        rng = self.rng
        dirt = [hexc("#5f4c36"), hexc("#7a6448"), hexc("#8f7757"), hexc("#a38b68")]
        for y in range(cy - ry - 1, cy + ry + 2):
            for x in range(cx - rx - 1, cx + rx + 2):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + rng.uniform(-0.25, 0.25)
                if d <= 1.0 and 0 <= x < self.w and 0 <= y < self.h:
                    k = 2 if d < 0.5 else 1
                    if y < cy - ry * 0.4 and rng.random() < 0.4:
                        k = 3
                    if rng.random() < 0.1:
                        k = 0
                    self._px(x, y, dirt[k])

    def planting(self, cx: int, cy: int, kind: str | None = None) -> bool:
        """One planting: lavender, a clump of one flower, or loose daisies."""
        rng = self.rng
        kind = kind or str(rng.choice(["lavender", "lavender", "white", "white", "yellow", "lilac", "pink", "daisies"]))
        if kind == "tufts":                              # grass growing up round a stone's foot
            for i in range(5):
                self.tuft(cx - 12 + i * 6 + int(rng.integers(-1, 2)), cy + int(rng.integers(-1, 2)), int(rng.integers(3, 6)))
            return True
        if kind == "lavender":
            return self.lavender_bush(cx, cy, int(rng.integers(8, 13)))
        if kind == "daisies":
            self.daisies(cx, cy, int(rng.integers(5, 9)), ["white", "white", "yellow"], 10)
            return True
        return self.flower_clump(cx, cy, kind, int(rng.integers(8, 14)))


SHADOW_CORE = np.array([0.6, 0.64, 0.76])     # shade multiplies the ground, a little blue
SHADOW_EDGE = np.array([0.8, 0.82, 0.88])


def cast_shadows(g: "Ground", casters, sx: float = 0.3, sy: float = 0.11) -> None:
    """Shadows of objects on the ground, the light coming from the upper left: every opaque pixel
    of an object, at height h above its foot, throws shade h * sx to the right and h * sy down
    from the foot. So a tall tree lays a long flat shadow to its lower right."""
    m = np.zeros((g.h, g.w), dtype=bool)
    for caster in casters:
        arr, x0, y0, base = caster[:4]
        csx, csy = (caster[4], caster[5]) if len(caster) > 5 else (sx, sy)
        a = arr[..., 3] >= 200
        ys, xs = np.nonzero(a)
        if len(ys) == 0:
            continue
        hh = base - (y0 + ys)
        ok = hh >= 0
        X = np.round(x0 + xs[ok] + hh[ok] * csx).astype(int)
        Y = np.round(base + hh[ok] * csy - 1).astype(int)
        inb = (X >= 0) & (X < g.w) & (Y >= 0) & (Y < g.h)
        m[Y[inb], X[inb]] = True
        # Fill the gaps the squashing leaves between rows.
        m[np.clip(Y[inb] + 1, 0, g.h - 1), X[inb]] = True
    if getattr(g, "water", None) is not None:
        m &= ~g.water                                  # shade falls on the island, not on the sea
    edge = (coast.grow(m, 1) == 1)
    if getattr(g, "water", None) is not None:
        edge &= ~g.water
    img = g.img
    img[m, :3] = np.clip(img[m, :3].astype(float) * SHADOW_CORE, 0, 255).astype(np.uint8)
    img[edge, :3] = np.clip(img[edge, :3].astype(float) * SHADOW_EDGE, 0, 255).astype(np.uint8)


def bake(rows: list[str], decor_rows: list[str], base_cells, over_cells, atlases: dict, order: dict,
         avoid_boxes: list[tuple[int, int, int, int]], plantings: list[tuple[int, int, str]] = (),
         side_path: list[tuple[int, int]] = (), casters=(), pen=None) -> Image.Image:
    """Paint the island's ground. `rows` are the AIAIA text rows; base/over cells as resolved by
    worldmap.resolve_ground (the dirt path overlay is replaced by flagstones here). `plantings`
    are hand-placed flowers: (x, y, kind)."""
    H, W = len(rows), len(rows[0])
    g = Ground(W * T, H * T)
    g.paint_grass()
    img = g.img

    def cell_img(cell):
        ai, tx, ty = cell
        return np.asarray(atlases[order[ai]].crop((tx * T, ty * T, tx * T + T, ty * T + T)))

    # Sea, banks and beach (coast.py), Hermes' terrace and the garden beds (yard.py) are all
    # painted; no LPC overlay tiles are used on the island any more.
    shore = coast.paint_coast(g, rows)
    g.water = shore["water"]
    lpc_region = np.zeros((H * T, W * T), dtype=bool)

    def runs(chars):
        """Bounding boxes (c0, r0, c1, r1) of each horizontal run of `chars`, merged down rows."""
        boxes = []
        for r, line in enumerate(rows):
            c = 0
            while c < W:
                if line[c] in chars:
                    c0 = c
                    while c < W and line[c] in chars:
                        c += 1
                    for b in boxes:
                        if b[0] == c0 and b[2] == c - 1 and b[3] == r - 1:
                            b[3] = r
                            break
                    else:
                        boxes.append([c0, r, c - 1, r])
                else:
                    c += 1
        return boxes
    for (c0, r0_, c1, r1_) in runs("mM"):
        sx0, sx1 = c0 * T, (c1 + 1) * T - 1
        yard.paint_terrace(g, sx0 + 1, r0_ * T + 1, sx1 - 2, (r1_ + 1) * T - 2,
                           sx0 + (sx1 - sx0) // 2 - 22, sx0 + (sx1 - sx0) // 2 + 22)
    for i, (c0, r0_, c1, r1_) in enumerate(runs("t")):
        yard.paint_bed(g, c0 * T + 2, r0_ * T + 4, (c1 + 1) * T - 3, (r1_ + 1) * T - 3, 300 + i)
    if pen:
        yard.paint_pen(g, pen[0], pen[1], 401)
    for r, line in enumerate(rows):
        for c, k in enumerate(line):
            y, x = r * T, c * T
            if k not in ("g", "G", "p", "~", "S", "P"):
                g.grass_ok[max(0, y - 4):y + T + 4, max(0, x - 3):x + T + 3] = False
    g.recolour_lpc_greens(lpc_region)
    for (x0, y0, x1, y1) in avoid_boxes:
        g.grass_ok[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = False

    # ---- the path ----------------------------------------------------------------------
    prow = [r for r, line in enumerate(rows) if "p" in line]
    r0, r1 = min(prow), max(prow)
    cols = [c for c, k in enumerate(rows[r0]) if k == "p"]
    lx, rx = cols[0] * T, (cols[-1] + 1) * T
    wob_l = paint.value_noise(4, H * T, 70, 11)[:, 0]
    wob_r = paint.value_noise(4, H * T, 70, 12)[:, 0]
    fence_rows = [r for r, line in enumerate(decor_rows) if "F" in line[cols[0] - 1:cols[-1] + 2]]

    def near_fence(y: float) -> bool:
        return any(fr * T - 8 <= y <= fr * T + T + 8 for fr in fence_rows)
    g.hard_edge = near_fence

    def left(y: float) -> float:
        yi = int(np.clip(y, 0, H * T - 1))
        return lx + 3 + (0 if near_fence(y) else (wob_l[yi] - 0.5) * 6)

    def right(y: float) -> float:
        yi = int(np.clip(y, 0, H * T - 1))
        return rx - 3 + (0 if near_fence(y) else (wob_r[yi] - 0.5) * 6)

    y_top, y_bot = r0 * T, (r1 + 1) * T
    # The flagstones run on into the sand, thinning out, right up to the pier.
    g.flagstones(left, right, y_top + 9, y_bot + 12, fade_from=y_bot - 8)     # starts below the terrace's steps
    g.grass_ok[y_top:y_bot, lx - 4:rx + 4] = False
    pier_rows = [r for r, line in enumerate(rows) if "P" in line]
    if pier_rows:
        pc = [c for c, k in enumerate(rows[pier_rows[0]]) if k == "P"]
        coast.paint_pier(g, pc[0] * T + 4, (pc[-1] + 1) * T - 5, pier_rows[0] * T + 6,
                         (pier_rows[-1] + 1) * T - 6, shore["water"])
    # A few rocks out in the sea, so the water south of the island is not empty.
    for i, (x, y, rx, ry) in enumerate(((74, 1238, 9, 6), (88, 1252, 5, 3), (478, 1166, 7, 5),
                                        (432, 1372, 11, 7), (452, 1384, 5, 3))):
        coast.sea_rock(g, x, y, rx, ry, 700 + i, shore["water"])

    rng = g.rng
    # Stepping stones from the main path to the front door.
    for (x0, y0), (x1, y1) in zip(side_path, side_path[1:]):
        n = max(1, int(np.hypot(x1 - x0, y1 - y0) // 15))
        for i in range(n):
            t = i / n
            x, y = int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)
            w, h = int(rng.integers(12, 16)), int(rng.integers(8, 11))
            g.stone(x - w // 2 + int(rng.integers(-1, 2)), y - h // 2, w, h)
    # Hand-placed plantings first (by the house, the terrace), so the scatter fills round them.
    for (x, y, kind) in plantings:
        g.grass_ok[y - 13:y + 5, x - 12:x + 13] = True
        g.planting(x, y, kind)
    # Along both edges of the path: a planting every so often, tufts in between.
    for y in range(y_top + 12, y_bot - 24, 13):
        for side in (0, 1):
            if rng.random() < 0.85:
                yy = y + int(rng.integers(-4, 5))
                gap = int(rng.integers(14, 26))
                kind = str(rng.choice(["lavender", "lavender", "white", "white", "yellow", "lilac", "pink"]))
                for attempt in range(4):              # step out past stones that overhang the edge
                    cx = int(left(yy)) - gap if side == 0 else int(right(yy)) + gap
                    if g.planting(cx, yy, kind):
                        break
                    gap += 7
    for y in range(y_top + 4, y_bot - 6, 5):
        for side in (0, 1):
            if rng.random() < 0.4:
                x = int(left(y)) - int(rng.integers(-1, 4)) if side == 0 else int(right(y)) + int(rng.integers(-1, 4))
                g.tuft(x, y, int(rng.integers(3, 6)))
    # Along the foot of each horizontal fence run.
    for r, line in enumerate(decor_rows):
        for c in range(W):
            if line[c] != "F":
                continue
            horizontal = (c + 1 < W and line[c + 1] == "F") or (c > 0 and line[c - 1] == "F")
            if horizontal and rng.random() < 0.6:
                g.grass_ok[r * T + T - 2:r * T + T + 10, c * T:c * T + T] |= False
                g.planting(c * T + int(rng.integers(6, 26)), r * T + T + 6)
    # Worn earth where the path meets the grass, and at the front door and the garden gaps.
    for y in range(y_top + 30, y_bot - 30, 70):
        for side in (0, 1):
            if rng.random() < 0.6:
                yy = y + int(rng.integers(-15, 16))
                x = int(left(yy)) - 2 if side == 0 else int(right(yy)) + 2
                if g.free(x - 8, yy - 4, x + 9, yy + 5) or True:
                    g.worn(x, yy, int(rng.integers(5, 9)), int(rng.integers(3, 5)))
    # Clover in the open grass.
    for _ in range(40):
        x, y = int(rng.integers(40, W * T - 40)), int(rng.integers(40, H * T - 40))
        if g.free(x - 8, y - 5, x + 9, y + 5):
            g.clover(x, y, int(rng.integers(5, 11)))
    # Meadow: loose wildflowers and the odd clump in the open grass.
    for _ in range(170):
        x, y = int(rng.integers(40, W * T - 40)), int(rng.integers(40, H * T - 40))
        if g.grass_ok[y, x]:
            if rng.random() < 0.8:
                g.daisies(x, y, int(rng.integers(2, 5)), ["white", "white", "yellow", "lilac"])
            else:
                g.planting(x, y)
    for _ in range(320):
        x, y = int(rng.integers(8, W * T - 8)), int(rng.integers(8, H * T - 8))
        if g.free(x - 2, y - 5, x + 3, y + 1):
            g.tuft(x, y, int(rng.integers(3, 5)))
    cast_shadows(g, casters)
    return Image.fromarray(img, "RGBA")


def slice_tiles(im: Image.Image, cols: int = 32):
    """Cut the baked picture into 32-px tiles, sharing identical ones. Returns (atlas image,
    cell grid of (tx, ty))."""
    arr = np.asarray(im)
    H, W = arr.shape[0] // T, arr.shape[1] // T
    seen: dict[bytes, int] = {}
    tiles_list: list[np.ndarray] = []
    grid = []
    for r in range(H):
        row = []
        for c in range(W):
            t = arr[r * T:(r + 1) * T, c * T:(c + 1) * T]
            key = t.tobytes()
            if key not in seen:
                seen[key] = len(tiles_list)
                tiles_list.append(t)
            i = seen[key]
            row.append((i % cols, i // cols))
        grid.append(row)
    rows_n = (len(tiles_list) + cols - 1) // cols
    atlas = np.zeros((rows_n * T, cols * T, 4), dtype=np.uint8)
    for i, t in enumerate(tiles_list):
        atlas[(i // cols) * T:(i // cols + 1) * T, (i % cols) * T:(i % cols + 1) * T] = t
    return Image.fromarray(atlas, "RGBA"), grid
