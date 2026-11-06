"""Scylla's poses for the previews: the same head targets and draw order as scylla.gd.

A pose gives each of the six heads a target (x, y relative to the waterline) and a sprite.
draw_list() returns the parts to draw, back to front, as (part name, x, y) relative to ORIGIN.
"""
from __future__ import annotations

import math

import scylla_big as S

ORIGIN = (272, 2430)
DRAW_ORDER = [0, 5, 1, 4, 2, 3]   # outer necks first, so the middle ones overlap them
BULGE = [-26, -18, -8, 8, 18, 26]

POSES = {
    # High in the mist, looking out to sea for ships.
    "idle": [(-158, -238, "side_closed_l"), (-104, -292, "side_closed_l"), (-40, -318, "side_open_l"),
             (36, -306, "side_closed_r"), (100, -276, "side_closed_r"), (156, -226, "side_open_r")],
    # Down out of the fog, all twelve eyes on Circe.
    "descend": [(-150, -150, "front_closed"), (-98, -196, "front_closed"), (-36, -222, "front_open"),
                (30, -214, "front_closed"), (90, -184, "front_closed"), (146, -146, "front_closed")],
    # One head drives down onto the rock beside her; the rest scream.
    "strike": [(-156, -160, "front_open"), (-104, -214, "front_open"), (-40, -240, "front_open"),
               (28, -232, "front_open"), (80, 14, "front_open"), (150, -156, "front_open")],
}


def draw_list(pose: str, t: float = 0.0) -> list[tuple[str, int, int]]:
    heads = S.heads()
    bases = S.neck_bases()
    out = [("shadow", 0, 0), ("body", 0, 0)]
    chains = []
    for i in range(6):
        hx, hy, hname = POSES[pose][i]
        hx += int(round(3 * math.sin(t * 1.3 + i)))
        hy += int(round(2 * math.sin(t * 1.7 + i * 2)))
        _img, _pv, (sx, sy), ndir = heads[hname]
        if hname.startswith("front"):
            side = 1 if bases[i][0] > hx + sx else -1 if bases[i][0] < hx + sx else 0
            ndir = (side * 0.55, -0.85)
        chains.append((S.neck_chain(bases[i], (hx + sx, hy + sy), ndir, BULGE[i]), hname, hx, hy))
    for i in DRAW_ORDER:
        chain, hname, hx, hy = chains[i]
        for (x, y, r) in chain:
            out.append((f"seg_o{r}", x, y))
        for k, (x, y, r) in enumerate(chain):
            out.append((f"seg_{'s' if k % 3 == 0 else 'f'}{r}", x, y))
        for k, (x, y, r) in enumerate(chain[:int(len(chain) * 0.85)]):
            out.append((f"seg_b{r}", x, y + 1))
        out.append((hname, hx, hy))
    out.append(("foam0", 0, 0))
    return out
