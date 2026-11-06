"""Generate every sprite sheet, prop, icon and tileset the game loads.

Usage:
    python tools/pixelart/build_all.py                # write into the game's asset folder
    python tools/pixelart/build_all.py --preview-only # only write tools/pixelart/preview/

The first real run copies the previous (Kimi-generated, Feb 2026) files to
assets/image_pipeline/generated/kimi_2026-02/ so nothing is lost.
Prologue cutscene paintings are never touched.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from px import preview, save  # noqa: E402
import scylla_big  # noqa: E402
import cove_scene  # noqa: E402
from props import all_props  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "assets/image_pipeline/generated/raw"
BACKUP = REPO / "assets/image_pipeline/generated/kimi_2026-02"
PREVIEW = Path(__file__).parent / "preview"


def build() -> dict[str, Image.Image]:
    """Characters and the pig come from LPC layers (lpc_compose); Scylla's parts, her strait
    (cliff, whirlpool, mist), props, icons and the herb cards are drawn in code; the tilesets
    are assembled from LPC packs (lpc_tiles)."""
    import lpc_compose
    import lpc_tiles
    out = {}
    for char in (lpc_compose.CIRCE, lpc_compose.HERMES):
        for action, img in lpc_compose.game_sheets(char).items():
            out[f"sprites/characters/{char.name}/{char.name}_{action}.png"] = img
    for action, img in lpc_compose.pig_sheets().items():
        out[f"sprites/characters/pig/pig_{action}.png"] = img
    out.update(scylla_big.scylla_images())
    out.update(cove_scene.cove_images())
    for rel, px in all_props().items():
        out[rel] = px.im
    for rel, px in lpc_tiles.all_tiles().items():
        out[rel] = px.im
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview-only", action="store_true")
    args = ap.parse_args()

    images = build()
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for rel, img in images.items():
        name = Path(rel).stem
        grid = (None if "scylla" in rel else 64) if "characters" in rel else (32 if "tilesets" in rel else None)
        scale = 2 if "tilesets" in rel else 4
        save(preview(img, scale, grid=grid), PREVIEW / f"{name}_x{scale}.png")
    print(f"{len(images)} images, previews in {PREVIEW}")

    if args.preview_only:
        return 0

    if not BACKUP.exists():
        shutil.copytree(RAW, BACKUP, ignore=shutil.ignore_patterns("*.import"))
        print(f"backed up previous art to {BACKUP}")
    for rel, img in images.items():
        save(img, RAW / rel)
    scylla_big.write_data()
    print(f"wrote {len(images)} files under {RAW} and {scylla_big.OUT_GD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
