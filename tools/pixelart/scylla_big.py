"""Scylla as a 96x96-frame monster: six dog-headed necks, twelve legs, sea-green hide.

Sheets are 384x384 (4 frames x rows Down, Up, Left, Right). scylla.gd slices by
texture width / 4, so the bigger cell needs no code change; the scene offset moves.
"""
from __future__ import annotations

import math

from px import Px, rgb, darken

CELL = 96
CX = 48
BASE = 90

OUT = rgb("#0f2628")
BODY = rgb("#2f6f6a")
DARK = rgb("#1d4a49")
LIGHT = rgb("#4f9a92")
BELLY = rgb("#8fb8ad")
EYE = rgb("#ffd34d")
PUPIL = rgb("#5a1a0a")
TOOTH = rgb("#f2f2e6")
MOUTH = rgb("#4a1020")
FOAM = rgb("#dff1ff")
WATER = rgb("#2f6594")


def _neck(p: Px, x0: float, y0: float, x1: float, y1: float, bulge: float, thick: int = 3) -> None:
    steps = int(max(abs(y1 - y0), abs(x1 - x0), 1))
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t + bulge * math.sin(t * math.pi)
        y = y0 + (y1 - y0) * t
        xi, yi = int(round(x)), int(round(y))
        p.rect(xi - thick // 2, yi, xi - thick // 2 + thick - 1, yi + 1, BODY)
        p.dot(xi - thick // 2, yi, LIGHT)


def _head(p: Px, x: int, y: int, facing: int, eyes: bool, open_jaw: bool) -> None:
    """Dog head about 12x9 centred at (x, y). facing: -1 left, 1 right, 0 toward the camera."""
    if facing == 0:
        p.ellipse(x - 5, y - 4, x + 5, y + 4, BODY)
        p.rect(x - 3, y + 1, x + 3, y + 4, DARK)            # muzzle
        p.poly([(x - 5, y - 3), (x - 7, y - 8), (x - 2, y - 4)], DARK)   # ears
        p.poly([(x + 5, y - 3), (x + 7, y - 8), (x + 2, y - 4)], DARK)
        if eyes:
            p.rect(x - 3, y - 2, x - 2, y - 1, EYE); p.rect(x + 2, y - 2, x + 3, y - 1, EYE)
            p.dot(x - 2, y - 1, PUPIL); p.dot(x + 2, y - 1, PUPIL)
        if open_jaw:
            p.rect(x - 2, y + 3, x + 2, y + 5, MOUTH)
            p.dot(x - 2, y + 3, TOOTH); p.dot(x + 2, y + 3, TOOTH); p.dot(x, y + 5, TOOTH)
        p.hline(x - 3, x, y - 4, LIGHT)
    else:
        f = facing
        p.ellipse(x - 5, y - 4, x + 5, y + 4, BODY)
        p.rect(min(x + f * 4, x + f * 9), y - 1, max(x + f * 4, x + f * 9), y + 2, BODY)   # snout
        p.rect(min(x + f * 5, x + f * 9), y + 2, max(x + f * 5, x + f * 9), y + 3, DARK)
        p.poly([(x - f * 2, y - 4), (x - f * 4, y - 9), (x + f * 1, y - 4)], DARK)          # ear
        if eyes:
            p.rect(x + f * 1, y - 2, x + f * 2, y - 1, EYE); p.dot(x + f * 2, y - 1, PUPIL)
        if open_jaw:
            p.rect(min(x + f * 5, x + f * 9), y + 3, max(x + f * 5, x + f * 9), y + 4, MOUTH)
            p.dot(x + f * 6, y + 3, TOOTH); p.dot(x + f * 9, y + 3, TOOTH)
        p.hline(min(x - 3, x + f * 2), max(x - 3, x + f * 2), y - 4, LIGHT)


def _legs(p: Px, xs: list[int], top: int, phase: int, side: bool) -> None:
    for i, x in enumerate(xs):
        lift = 1 if (phase != 0 and (i + (phase > 0)) % 2 == 0) else 0
        shade = DARK if i % 2 else BODY
        p.rect(x, top, x + 2, BASE - lift, shade)
        p.rect(x - 1, BASE - 2 - lift, x + 3, BASE - lift, darken(shade, 0.8))   # paw
        if side:
            p.dot(x + 3, BASE - lift, darken(shade, 0.8))


def frame(view: str, action: str, f: int) -> Px:
    p = Px(CELL, CELL)
    sway = [0, 1, 0, -1][f]
    phase = [1, 0, -1, 0][f] if action == "walk" else 0
    bob = -1 if (action == "walk" and f % 2 == 1) else 0
    jaw = (f == 2) if action == "idle" else (f % 2 == 0)
    # Shallow water and foam under her: she stands in the strait.
    p.ellipse(CX - 30, BASE - 5, CX + 30, BASE + 3, WATER)
    for i in range(-30, 31, 6):
        p.dot(CX + i + (f % 2), BASE - 5 + ((i // 6) % 2), FOAM)

    if view in ("down", "up"):
        back = view == "up"
        _legs(p, list(range(CX - 27, CX + 28, 6)), 70 + bob, phase, False)
        # body mass
        p.ellipse(CX - 28, 44 + bob, CX + 28, 86 + bob, BODY)
        p.ellipse(CX - 24, 36 + bob, CX + 24, 60 + bob, BODY)
        if not back:
            p.ellipse(CX - 16, 54 + bob, CX + 16, 82 + bob, BELLY)
            p.hline(CX - 18, CX + 18, 83 + bob, DARK)
        else:
            p.ellipse(CX - 20, 50 + bob, CX + 20, 80 + bob, DARK)
            p.vline(CX, 48 + bob, 80 + bob, darken(DARK, 0.85))
        p.hline(CX - 20, CX - 6, 40 + bob, LIGHT); p.hline(CX - 24, CX - 16, 48 + bob, LIGHT)
        # six necks and heads in a fan
        anchors = [(-20, 44), (-12, 40), (-4, 38), (4, 38), (12, 40), (20, 44)]
        heads = [(-33, 30), (-22, 17), (-9, 11), (9, 11), (22, 17), (33, 30)]
        facings = [-1, -1, 0, 0, 1, 1] if not back else [1, 1, 0, 0, -1, -1]
        order = [0, 5, 1, 4, 2, 3]  # outer first so the centre heads draw on top
        for i in order:
            ax, ay = anchors[i]; hx, hy = heads[i]
            wig = sway * (1 if i % 2 else -1) + (sway if i in (2, 3) else 0)
            hx += wig; hy += abs(wig) // 2
            _neck(p, CX + ax, ay + bob, CX + hx, hy + 4 + bob, -6 if hx < 0 else 6)
            _head(p, CX + hx, hy + bob, facings[i], not back, jaw and i in (1, 2, 4))
    else:
        # Facing LEFT: body in profile, necks reaching forward and up.
        _legs(p, [CX - 22, CX - 16, CX - 10, CX - 4, CX + 2, CX + 8, CX + 14, CX + 20], 70 + bob, phase, True)
        p.ellipse(CX - 26, 46 + bob, CX + 30, 86 + bob, BODY)
        p.ellipse(CX - 14, 38 + bob, CX + 26, 62 + bob, BODY)
        p.ellipse(CX - 16, 60 + bob, CX + 20, 82 + bob, darken(BELLY, 0.9))
        p.hline(CX - 10, CX + 14, 42 + bob, LIGHT)
        # tail curling behind (right side)
        p.rect(CX + 26, 62 + bob, CX + 34, 66 + bob, BODY); p.rect(CX + 32, 56 + bob, CX + 36, 64 + bob, BODY)
        p.rect(CX + 34, 52 + bob, CX + 38, 56 + bob, DARK)
        anchors = [(-8, 44), (-4, 40), (0, 40), (6, 40), (12, 42), (18, 46)]
        heads = [(-34, 40), (-32, 26), (-24, 15), (-8, 13), (10, 15), (26, 22)]
        facings = [-1, -1, -1, -1, 1, 1]
        for i in (5, 4, 3, 0, 1, 2):
            ax, ay = anchors[i]; hx, hy = heads[i]
            wig = sway * (1 if i % 2 else -1)
            _neck(p, CX + ax, ay + bob, CX + hx + (2 if hx < 0 else -2), hy + 4 + bob + wig, -5 if hx < -10 else 3)
            _head(p, CX + hx, hy + bob + wig, facings[i], True, jaw and i in (0, 2, 4))
    p.outline(OUT)
    return p


def scylla_sheets() -> dict[str, list[list[Px]]]:
    out = {}
    for action in ("idle", "walk"):
        left = [frame("side", action, f) for f in range(4)]
        out[action] = [
            [frame("down", action, f) for f in range(4)],
            [frame("up", action, f) for f in range(4)],
            left,
            [fr.mirrored() for fr in left],
        ]
    return out


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from px import sheet, preview, save
    out = Path(__file__).parent / "preview"
    for action, rows in scylla_sheets().items():
        img = sheet(rows, CELL, CELL)
        save(preview(img, 3, grid=CELL), out / f"scylla_big_{action}_x3.png")
    print("ok")
