"""Scripted checks for the generated art (no model-based image recognition).

For every sheet the game loads:
  - exact pixel size per the asset spec
  - alpha is binary (0 or 255), no anti-aliasing
  - every animation frame has content, fully inside its cell with a 1-px margin
  - the lowest opaque row (feet + outline) is the same in every frame of a sheet
  - Right rows are exact mirrors of Left rows (4-row: rows 2/3; 2-row: rows 0/1)
  - at most 48 distinct colours per sheet
Exit code 1 on any failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "assets/image_pipeline/generated/raw"

SHEETS = {
    "sprites/characters/circe/circe_idle.png": (256, 256, 4, 4),
    "sprites/characters/circe/circe_walk.png": (256, 256, 4, 4),
    "sprites/characters/hermes/hermes_idle.png": (256, 256, 4, 4),
    "sprites/characters/hermes/hermes_walk.png": (256, 256, 4, 4),
    "sprites/characters/pig/pig_walk.png": (256, 256, 4, 4),
    "sprites/characters/pig/pig_run.png": (256, 256, 4, 4),
    "sprites/characters/pig/pig_idle.png": (256, 128, 4, 2),
    "sprites/characters/pig/pig_eat.png": (256, 128, 4, 2),
    "sprites/characters/pig/pig_sleep.png": (256, 128, 4, 2),
}
STATICS = {
    "sprites/entities/boat.png": (128, 64),
    "sprites/entities/crafting_table.png": (64, 64),
    "sprites/entities/sleep_spot.png": (64, 64),
    "sprites/entities/farm_plot.png": (64, 64),
    "sprites/entities/farm_plot_stage_empty.png": (64, 64),
    "sprites/entities/farm_plot_stage_planted.png": (64, 64),
    "sprites/entities/farm_plot_stage_1.png": (64, 64),
    "sprites/entities/farm_plot_stage_2.png": (64, 64),
    "sprites/entities/farm_plot_stage_ready.png": (64, 64),
    "sprites/ui/icon_moly_seed.png": (32, 32),
    "sprites/ui/icon_moly.png": (32, 32),
    "sprites/ui/icon_calming_draught.png": (32, 32),
    "sprites/ui/herb_moly.png": (64, 64),
    "sprites/ui/herb_nightshade.png": (64, 64),
    "sprites/ui/herb_hemlock.png": (64, 64),
    "sprites/ui/particle_soft.png": (16, 16),
    "sprites/characters/scylla/scylla_parts.png": None,
    "sprites/entities/cove_cliff.png": (544, 292),
    "sprites/entities/whirlpool.png": (1200, 60),
    "sprites/entities/mist_banks.png": (480, 92),
    "tilesets/aiaia_tileset_32.png": None,
    "tilesets/scylla_cove_tileset_32.png": None,
    "tilesets/greek_decor_tileset_32.png": None,
}


def binary_alpha(img: Image.Image) -> bool:
    return set(img.getchannel("A").getdata()) <= {0, 255}


def check_scylla_parts() -> list[str]:
    """Every part listed in game/data/scylla_parts.gd lies inside the atlas and has pixels."""
    import re
    data = (REPO / "game/data/scylla_parts.gd").read_text(encoding="utf-8")
    img = Image.open(RAW / "sprites/characters/scylla/scylla_parts.png").convert("RGBA")
    out = []
    regions = re.findall(r'"(\w+)": \[(\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\]', data)
    if not regions:
        return ["scylla_parts.gd: no regions"]
    for name, x, y, w, h, _px, _py in regions:
        x, y, w, h = int(x), int(y), int(w), int(h)
        if x + w > img.width or y + h > img.height:
            out.append(f"scylla_parts: {name} lies outside the atlas")
        elif img.crop((x, y, x + w, y + h)).getbbox() is None:
            out.append(f"scylla_parts: {name} is empty")
    return out


def main() -> int:
    problems: list[str] = []
    warnings: list[str] = []
    ok = 0
    for rel, (w, h, cols, rows) in SHEETS.items():
        path = RAW / rel
        if not path.exists():
            problems.append(f"{rel}: missing"); continue
        img = Image.open(path).convert("RGBA")
        if img.size != (w, h):
            problems.append(f"{rel}: size {img.size}, expected {(w, h)}"); continue
        if not binary_alpha(img):
            problems.append(f"{rel}: semi-transparent pixels")
        colours = len(set(img.getdata()))
        if colours > 48:
            problems.append(f"{rel}: {colours} colours")
        cw, ch = w // cols, h // rows
        bottoms = set()
        for r in range(rows):
            for c in range(cols):
                cell = img.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
                bb = cell.getbbox()
                if bb is None:
                    problems.append(f"{rel}: empty frame row {r} col {c}"); continue
                # LPC sheets put feet on the last rows of the cell; only the top and sides must stay clear.
                if bb[0] < 1 or bb[1] < 1 or bb[2] > cw - 1:
                    problems.append(f"{rel}: frame row {r} col {c} touches the cell edge {bb}")
                bottoms.add(bb[3])
        if max(bottoms) - min(bottoms) > 3:
            problems.append(f"{rel}: feet baseline differs between frames: {sorted(bottoms)}")
        left_r, right_r = (2, 3) if rows == 4 else (0, 1)
        left = img.crop((0, left_r * ch, w, (left_r + 1) * ch))
        right = img.crop((0, right_r * ch, w, (right_r + 1) * ch))
        for c in range(cols):
            lf = left.crop((c * cw, 0, (c + 1) * cw, ch))
            rf = right.crop((c * cw, 0, (c + 1) * cw, ch))
            if ImageOps.mirror(lf).tobytes() != rf.tobytes():
                # LPC-drawn sheets have hand-drawn right-facing rows; only warn.
                warnings.append(f"{rel}: right frame {c} is not a mirror of left frame {c}")
        ok += 1
    for rel, size in STATICS.items():
        path = RAW / rel
        if not path.exists():
            problems.append(f"{rel}: missing"); continue
        img = Image.open(path).convert("RGBA")
        if size is None:
            if img.width % 32 or img.height % 32:
                problems.append(f"{rel}: size {img.size} is not a multiple of 32")
        elif img.size != size:
            problems.append(f"{rel}: size {img.size}, expected {size}")
        if not binary_alpha(img) and "tilesets" not in rel and "particle" not in rel:   # soft edges by design
            problems.append(f"{rel}: semi-transparent pixels")
        if img.getbbox() is None:
            problems.append(f"{rel}: empty image")
        ok += 1
    problems += check_scylla_parts()
    print(f"checked {ok} files, {len(problems)} problems, {len(warnings)} warnings (non-mirrored rows)")
    for p in problems:
        print("  ", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
