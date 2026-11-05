#!/usr/bin/env python3
"""Split composite spritesheets into individual action sheets.

Kimi K generates idle+walk as one stacked 1:1 image (4 cols x 8 rows)
to maintain character identity consistency. This tool splits them into
separate sheets before normalization.

Workflow
--------
1. Drop Kimi composite outputs into  assets/image_pipeline/generated/composites/
2. Run:   python assets/image_pipeline/tools/split_composites.py
3. Check: assets/image_pipeline/generated/raw/  (individual sheets)
4. Run:   python assets/image_pipeline/tools/normalize_assets.py
5. Run:   python assets/image_pipeline/tools/preflight.py

Composite naming convention
---------------------------
  circe_composite.png      -> circe_idle.png  + circe_walk.png
  hermes_composite.png     -> hermes_idle.png + hermes_walk.png
  scylla_composite.png     -> scylla_idle.png + scylla_walk.png
  pig_4dir_composite.png   -> pig_walk.png    + pig_run.png
  pig_2dir_composite.png   -> pig_idle.png    + pig_eat.png + pig_sleep.png

Flags
-----
  --dry-run    Report what would be done without writing anything
  --force      Overwrite existing output files (default: skip if exists)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class SplitSpec:
    """Defines how to split one composite image."""
    composite_name: str          # input filename in composites/
    output_dir: str              # subfolder under assets/sprites/characters/
    actions: list[str]           # action names, top to bottom
    rows_per_action: int         # how many rows each action occupies
    cols: int = 4                # columns (always 4 for our sheets)


SPLIT_SPECS: list[SplitSpec] = [
    # Characters: 1:1 square, 4 cols x 8 rows -> 2 actions x 4 rows each
    SplitSpec("circe_composite.png", "sprites/characters/circe",
              ["idle", "walk"], rows_per_action=4),
    SplitSpec("hermes_composite.png", "sprites/characters/hermes",
              ["idle", "walk"], rows_per_action=4),
    SplitSpec("scylla_composite.png", "sprites/characters/scylla",
              ["idle", "walk"], rows_per_action=4),

    # Pig 4-dir: 1:1 square, 4 cols x 8 rows -> 2 actions x 4 rows each
    SplitSpec("pig_4dir_composite.png", "sprites/characters/pig",
              ["walk", "run"], rows_per_action=4),

    # Pig 2-dir: tall image, 4 cols x 6 rows -> 3 actions x 2 rows each
    SplitSpec("pig_2dir_composite.png", "sprites/characters/pig",
              ["idle", "eat", "sleep"], rows_per_action=2),
]


ROOT = Path(__file__).resolve().parents[3]
COMPOSITE_ROOT = ROOT / "assets" / "image_pipeline" / "generated" / "composites"
OUTPUT_ROOT = ROOT / "assets" / "image_pipeline" / "generated" / "raw"


def get_character_name(spec: SplitSpec) -> str:
    """Extract character name from composite filename."""
    name = spec.composite_name.replace("_composite.png", "")
    name = name.replace("_4dir", "").replace("_2dir", "")
    return name


def split_one(spec: SplitSpec, composite_root: Path, output_root: Path,
              *, dry_run: bool = False, force: bool = False) -> list[str]:
    """Split one composite into individual sheets. Returns status lines."""
    src = composite_root / spec.composite_name
    results = []

    if not src.exists():
        results.append(f"SKIP     {spec.composite_name} (not found)")
        return results

    with Image.open(src) as img:
        w, h = img.size
        total_rows = spec.rows_per_action * len(spec.actions)
        row_height = h // total_rows

        # Validate dimensions
        col_width = w // spec.cols
        if w % spec.cols != 0:
            results.append(f"ERROR    {spec.composite_name}: width {w} not divisible by {spec.cols} cols")
            return results
        if h % total_rows != 0:
            results.append(f"ERROR    {spec.composite_name}: height {h} not divisible by {total_rows} rows")
            return results

        char_name = get_character_name(spec)
        frame_w = col_width
        frame_h = row_height

        results.append(f"SPLIT    {spec.composite_name} ({w}x{h}) -> "
                       f"{len(spec.actions)} sheets, {spec.cols}x{spec.rows_per_action} each, "
                       f"frame {frame_w}x{frame_h}")

        for i, action in enumerate(spec.actions):
            top = i * spec.rows_per_action * row_height
            bottom = top + spec.rows_per_action * row_height
            crop_box = (0, top, w, bottom)

            out_name = f"{char_name}_{action}.png"
            out_path = output_root / spec.output_dir / out_name

            if out_path.exists() and not force:
                results.append(f"  EXISTS {spec.output_dir}/{out_name} (use --force to overwrite)")
                continue

            if not dry_run:
                sheet = img.crop(crop_box)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                sheet.save(out_path)

            sheet_w = w
            sheet_h = spec.rows_per_action * row_height
            results.append(f"  WRITE  {spec.output_dir}/{out_name} ({sheet_w}x{sheet_h})")

    return results


def run(args: argparse.Namespace) -> int:
    if not COMPOSITE_ROOT.exists():
        print(f"Composites directory not found: {COMPOSITE_ROOT}")
        print("Creating it now. Drop your composite images there and re-run.")
        COMPOSITE_ROOT.mkdir(parents=True, exist_ok=True)
        return 1

    print(f"Input:  {COMPOSITE_ROOT}")
    print(f"Output: {OUTPUT_ROOT}")
    if args.dry_run:
        print("MODE:   dry-run (no files written)")
    print()

    found = 0
    split_count = 0
    errors = 0

    for spec in SPLIT_SPECS:
        src = COMPOSITE_ROOT / spec.composite_name
        if not src.exists():
            continue
        found += 1

        statuses = split_one(spec, COMPOSITE_ROOT, OUTPUT_ROOT,
                             dry_run=args.dry_run, force=args.force)
        for s in statuses:
            print(s)
            if s.startswith("  WRITE"):
                split_count += 1
            elif s.startswith("ERROR"):
                errors += 1
        print()

    if found == 0:
        print("No composite images found. Expected filenames:")
        for spec in SPLIT_SPECS:
            print(f"  {spec.composite_name}")
        return 1

    print(f"Summary: {found} composites found, {split_count} sheets written, {errors} errors")
    if errors > 0:
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split composite spritesheets into individual action sheets.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done without writing files")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing output files")
    sys.exit(run(parser.parse_args()))


if __name__ == "__main__":
    main()
