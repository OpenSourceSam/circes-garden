#!/usr/bin/env python3
"""Normalize oversized AI-generated assets to exact runtime dimensions.

Converts Kimi/Gemini outputs (which enforce a ~1K floor) to the exact pixel
sizes required by the Godot runtime.  Uses nearest-neighbor resampling to
preserve pixel-art crispness.

Workflow
--------
1. Drop Kimi outputs into  assets/image_pipeline/generated/raw/
2. Run:   python assets/image_pipeline/tools/normalize_assets.py
3. Check: assets/image_pipeline/generated/normalized/  (exact-spec copies)
4. Run:   python assets/image_pipeline/tools/preflight.py --root normalized
5. If preflight passes, copy normalized/ → assets/ when ready.

Flags
-----
  --in-place   Overwrite originals in assets/ instead of writing to normalized/
  --dry-run    Report what would be done without writing anything
  --force      Resize even if already at target (default: skip correct files)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


# ---------------------------------------------------------------------------
# Spec definitions — single source of truth for every asset's target size
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AssetSpec:
    path: str
    kind: str
    target_w: int
    target_h: int


# Character 4-dir:  256×256,  64×64 frames,  4×4 grid
# Pig 4-dir:        256×256,  64×64 frames,  4×4 grid
# Pig 2-dir:        256×128,  64×64 frames,  4×2 grid
# Entity:           per-asset recommended sizes
# Icon:             32×32
# Prologue:         864×1184
# Tileset:          keep original (just verify 32-grid)

ASSET_SPECS: list[AssetSpec] = [
    # --- Prologue (already correct at 864×1184, normalize if needed) ---
    AssetSpec("cutscenes/prologue/prologue_01.png", "prologue", 864, 1184),
    AssetSpec("cutscenes/prologue/prologue_02.png", "prologue", 864, 1184),
    AssetSpec("cutscenes/prologue/prologue_03.png", "prologue", 864, 1184),
    AssetSpec("cutscenes/prologue/prologue_04.png", "prologue", 864, 1184),
    AssetSpec("cutscenes/prologue/prologue_05.png", "prologue", 864, 1184),
    AssetSpec("cutscenes/prologue/prologue_06.png", "prologue", 864, 1184),
    AssetSpec("cutscenes/prologue/prologue_07.png", "prologue", 864, 1184),

    # --- Characters (4-direction sheets) ---
    AssetSpec("sprites/characters/circe/circe_idle.png", "character_4dir", 256, 256),
    AssetSpec("sprites/characters/circe/circe_walk.png", "character_4dir", 256, 256),
    AssetSpec("sprites/characters/hermes/hermes_idle.png", "character_4dir", 256, 256),
    AssetSpec("sprites/characters/hermes/hermes_walk.png", "character_4dir", 256, 256),
    AssetSpec("sprites/characters/scylla/scylla_idle.png", "character_4dir", 256, 256),
    AssetSpec("sprites/characters/scylla/scylla_walk.png", "character_4dir", 256, 256),

    # --- Pig 4-direction ---
    AssetSpec("sprites/characters/pig/pig_walk.png", "pig_4dir", 256, 256),
    AssetSpec("sprites/characters/pig/pig_run.png", "pig_4dir", 256, 256),

    # --- Pig 2-direction ---
    AssetSpec("sprites/characters/pig/pig_idle.png", "pig_2dir", 256, 128),
    AssetSpec("sprites/characters/pig/pig_eat.png", "pig_2dir", 256, 128),
    AssetSpec("sprites/characters/pig/pig_sleep.png", "pig_2dir", 256, 128),

    # --- Entities (recommended sizes from spec) ---
    AssetSpec("sprites/entities/boat.png", "entity", 128, 64),
    AssetSpec("sprites/entities/crafting_table.png", "entity", 64, 64),
    AssetSpec("sprites/entities/farm_plot.png", "entity", 64, 64),
    AssetSpec("sprites/entities/farm_plot_stage_empty.png", "entity", 64, 64),
    AssetSpec("sprites/entities/farm_plot_stage_planted.png", "entity", 64, 64),
    AssetSpec("sprites/entities/farm_plot_stage_1.png", "entity", 64, 64),
    AssetSpec("sprites/entities/farm_plot_stage_2.png", "entity", 64, 64),
    AssetSpec("sprites/entities/farm_plot_stage_ready.png", "entity", 64, 64),
    AssetSpec("sprites/entities/sleep_spot.png", "entity", 64, 64),

    # --- UI Icons ---
    AssetSpec("sprites/ui/icon_moly_seed.png", "icon", 32, 32),
    AssetSpec("sprites/ui/icon_moly.png", "icon", 32, 32),
    AssetSpec("sprites/ui/icon_calming_draught.png", "icon", 32, 32),

    # --- Tilesets (keep original size, just pass through) ---
    AssetSpec("tilesets/aiaia_tileset_32.png", "tileset", 0, 0),
    AssetSpec("tilesets/scylla_cove_tileset_32.png", "tileset", 0, 0),
    AssetSpec("tilesets/greek_decor_tileset_32.png", "tileset", 0, 0),
]


ROOT = Path(__file__).resolve().parents[3]
INPUT_ROOT = ROOT / "assets" / "image_pipeline" / "generated" / "raw"
OUTPUT_ROOT = ROOT / "assets" / "image_pipeline" / "generated" / "normalized"


def normalize_one(spec: AssetSpec, input_root: Path, output_root: Path,
                   *, dry_run: bool = False, force: bool = False) -> str:
    """Normalize a single asset. Returns a status string."""
    src = input_root / spec.path
    dst = output_root / spec.path

    if not src.exists():
        return f"MISSING  {spec.path}"

    with Image.open(src) as img:
        cur_w, cur_h = img.size

        # Tilesets: copy through without resize (just verify 32-grid)
        if spec.kind == "tileset":
            if cur_w % 32 != 0 or cur_h % 32 != 0:
                return f"WARN     {spec.path}: {cur_w}x{cur_h} not 32-grid aligned"
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                img.save(dst)
            return f"COPY     {spec.path} ({cur_w}x{cur_h}, tileset pass-through)"

        target_w, target_h = spec.target_w, spec.target_h

        # Already correct?
        if (cur_w, cur_h) == (target_w, target_h) and not force:
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                img.save(dst)
            return f"OK       {spec.path} (already {cur_w}x{cur_h})"

        # Ensure RGBA for sprites (not prologue which may be RGB)
        if spec.kind != "prologue" and img.mode != "RGBA":
            img = img.convert("RGBA")

        # Crop to target aspect ratio if source aspect differs (e.g. Kimi
        # outputs 1:1 squares but pig_2dir/boat targets are 2:1).
        src_ratio = cur_w / cur_h
        tgt_ratio = target_w / target_h
        if abs(src_ratio - tgt_ratio) > 0.01:
            crop_h = int(cur_w / tgt_ratio)
            if crop_h < cur_h:
                img = img.crop((0, 0, cur_w, crop_h))
            else:
                crop_w = int(cur_h * tgt_ratio)
                img = img.crop((0, 0, crop_w, cur_h))

        # Nearest-neighbor resize — preserves pixel art
        resized = img.resize((target_w, target_h), Image.NEAREST)

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            resized.save(dst)

        return f"RESIZE   {spec.path}: {cur_w}x{cur_h} -> {target_w}x{target_h}"


def run(args: argparse.Namespace) -> int:
    input_root = INPUT_ROOT
    output_root = INPUT_ROOT if args.in_place else OUTPUT_ROOT

    if not input_root.exists():
        print(f"ERROR: Input directory not found: {input_root}")
        return 1

    print(f"Input:  {input_root}")
    print(f"Output: {output_root}")
    if args.dry_run:
        print("MODE:   dry-run (no files written)")
    elif args.in_place:
        print("MODE:   in-place (overwriting originals)")
    print()

    results = {"ok": 0, "resized": 0, "copied": 0, "missing": 0, "warn": 0}

    for spec in ASSET_SPECS:
        status = normalize_one(spec, input_root, output_root,
                               dry_run=args.dry_run, force=args.force)
        print(status)

        tag = status.split()[0]
        if tag == "OK":
            results["ok"] += 1
        elif tag == "RESIZE":
            results["resized"] += 1
        elif tag == "COPY":
            results["copied"] += 1
        elif tag == "MISSING":
            results["missing"] += 1
        elif tag == "WARN":
            results["warn"] += 1

    print()
    print(f"Summary: {results['resized']} resized, {results['ok']} already correct, "
          f"{results['copied']} copied, {results['missing']} missing, {results['warn']} warnings")

    if results["missing"] > 0:
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize oversized AI-generated assets to exact runtime dimensions.")
    parser.add_argument("--in-place", action="store_true",
                        help="Overwrite originals instead of writing to normalized/")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done without writing files")
    parser.add_argument("--force", action="store_true",
                        help="Resize even if already at target dimensions")
    sys.exit(run(parser.parse_args()))


if __name__ == "__main__":
    main()
