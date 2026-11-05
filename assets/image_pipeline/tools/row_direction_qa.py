#!/usr/bin/env python3
"""Row-direction QA tool for sprite sheet validation.

Generates labeled contact sheets for every sprite sheet, splitting each row
into a clearly marked strip.  Also runs heuristic checks for:
  - Row duplication (two rows that are pixel-identical)
  - Missing mirror (left-facing row should be horizontally-flipped right-facing)

Output goes to  assets/image_pipeline/qa/row_qa/  for manual review.

Usage:
  python assets/image_pipeline/tools/row_direction_qa.py                      # check raw/
  python assets/image_pipeline/tools/row_direction_qa.py --root normalized     # check normalized/
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


# ---------------------------------------------------------------------------
# Sheet definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SheetSpec:
    path: str
    kind: str            # character_4dir, pig_4dir, pig_2dir
    cols: int
    rows: int
    row_labels: list[str]   # top-to-bottom


SHEETS: list[SheetSpec] = [
    # Characters
    SheetSpec("sprites/characters/circe/circe_idle.png", "character_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    SheetSpec("sprites/characters/circe/circe_walk.png", "character_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    SheetSpec("sprites/characters/hermes/hermes_idle.png", "character_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    SheetSpec("sprites/characters/hermes/hermes_walk.png", "character_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    SheetSpec("sprites/characters/scylla/scylla_idle.png", "character_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    SheetSpec("sprites/characters/scylla/scylla_walk.png", "character_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    # Pig 4-dir
    SheetSpec("sprites/characters/pig/pig_walk.png", "pig_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    SheetSpec("sprites/characters/pig/pig_run.png", "pig_4dir",
              4, 4, ["Down", "Up", "Left", "Right"]),
    # Pig 2-dir
    SheetSpec("sprites/characters/pig/pig_idle.png", "pig_2dir",
              4, 2, ["Left", "Right"]),
    SheetSpec("sprites/characters/pig/pig_eat.png", "pig_2dir",
              4, 2, ["Left", "Right"]),
    SheetSpec("sprites/characters/pig/pig_sleep.png", "pig_2dir",
              4, 2, ["Left", "Right"]),
]

ROOT = Path(__file__).resolve().parents[3]

# Scaling factor for contact sheet previews (4x upscale for readability)
PREVIEW_SCALE = 4

# Label area width (pixels at preview scale)
LABEL_WIDTH = 120

# Colors
BG_COLOR = (40, 40, 40, 255)
LABEL_COLOR = (255, 255, 255, 255)
WARN_COLOR = (255, 80, 80, 255)
OK_COLOR = (80, 255, 80, 255)
GRID_COLOR = (100, 100, 100, 255)


def pixel_similarity(arr_a: np.ndarray, arr_b: np.ndarray) -> float:
    """Return fraction of pixels that are identical between two arrays."""
    if arr_a.shape != arr_b.shape:
        return 0.0
    match = np.all(arr_a == arr_b, axis=-1)
    return float(np.mean(match))


def check_row_duplication(rows: list[np.ndarray]) -> list[str]:
    """Check if any two rows are pixel-identical."""
    warnings = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            sim = pixel_similarity(rows[i], rows[j])
            if sim > 0.95:
                warnings.append(f"Row {i} and Row {j} are {sim:.0%} identical (DUPLICATE?)")
    return warnings


def check_mirror_pair(rows: list[np.ndarray], labels: list[str]) -> list[str]:
    """For 4-dir sheets, check if Left/Right rows are proper mirrors."""
    warnings = []

    # Find Left and Right row indices
    left_idx = next((i for i, l in enumerate(labels) if l == "Left"), None)
    right_idx = next((i for i, l in enumerate(labels) if l == "Right"), None)

    if left_idx is None or right_idx is None:
        return warnings

    left_row = rows[left_idx]
    right_row = rows[right_idx]

    # Check direct similarity (should be low unless duplicated)
    direct_sim = pixel_similarity(left_row, right_row)
    if direct_sim > 0.95:
        warnings.append(
            f"Left/Right rows are {direct_sim:.0%} identical WITHOUT flip - "
            "likely duplicated instead of mirrored"
        )

    # Check mirror similarity (flip right horizontally, compare to left)
    right_flipped = np.flip(right_row, axis=1)
    mirror_sim = pixel_similarity(left_row, right_flipped)
    if mirror_sim > 0.90:
        # This is normal — Left is often a mirror of Right
        pass
    elif mirror_sim < 0.30 and direct_sim < 0.30:
        warnings.append(
            f"Left/Right rows have low mirror similarity ({mirror_sim:.0%}) - "
            "rows may be misassigned"
        )

    return warnings


def generate_contact_sheet(
    spec: SheetSpec,
    src_path: Path,
    out_path: Path,
) -> list[str]:
    """Generate a labeled contact sheet and return QA warnings."""
    warnings: list[str] = []

    with Image.open(src_path) as img:
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        src_w, src_h = img.size
        frame_w = src_w // spec.cols
        frame_h = src_h // spec.rows
        src_arr = np.array(img)

    # Extract rows as numpy arrays
    row_arrays: list[np.ndarray] = []
    for r in range(spec.rows):
        y0 = r * frame_h
        y1 = (r + 1) * frame_h
        row_arrays.append(src_arr[y0:y1, :, :])

    # Run heuristic checks
    warnings.extend(check_row_duplication(row_arrays))
    warnings.extend(check_mirror_pair(row_arrays, spec.row_labels))

    # Build contact sheet with labels
    preview_frame_w = frame_w * PREVIEW_SCALE
    preview_frame_h = frame_h * PREVIEW_SCALE
    preview_row_w = src_w * PREVIEW_SCALE

    sheet_w = LABEL_WIDTH + preview_row_w + 10
    sheet_h = spec.rows * (preview_frame_h + 4) + 30  # +30 for title

    sheet = Image.new("RGBA", (sheet_w, sheet_h), BG_COLOR)
    draw = ImageDraw.Draw(sheet)

    # Title
    title = Path(spec.path).stem
    draw.text((10, 4), title, fill=LABEL_COLOR)

    y_offset = 26
    for r in range(spec.rows):
        label = spec.row_labels[r] if r < len(spec.row_labels) else f"Row {r}"

        # Draw label
        draw.text((8, y_offset + preview_frame_h // 2 - 6), label, fill=LABEL_COLOR)

        # Draw upscaled row
        row_img = Image.fromarray(row_arrays[r])
        row_upscaled = row_img.resize(
            (preview_row_w, preview_frame_h), Image.NEAREST
        )
        sheet.paste(row_upscaled, (LABEL_WIDTH, y_offset))

        # Draw frame grid lines
        for c in range(1, spec.cols):
            x = LABEL_WIDTH + c * preview_frame_w
            draw.line([(x, y_offset), (x, y_offset + preview_frame_h)],
                      fill=GRID_COLOR, width=1)

        y_offset += preview_frame_h + 4

    # Draw warnings on sheet
    if warnings:
        for i, warn in enumerate(warnings):
            draw.text((8, y_offset + i * 14), f"! {warn}", fill=WARN_COLOR)
    else:
        draw.text((8, y_offset), "No issues detected", fill=OK_COLOR)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return warnings


def run(args: argparse.Namespace) -> int:
    base = ROOT / "assets" / "image_pipeline" / "generated"
    asset_root = base / args.root
    output_dir = ROOT / "assets" / "image_pipeline" / "qa" / "row_qa"

    if not asset_root.exists():
        print(f"ERROR: Asset directory not found: {asset_root}")
        return 1

    print(f"Input:  {asset_root}")
    print(f"Output: {output_dir}")
    print()

    total_warnings: list[str] = []
    processed = 0
    skipped = 0

    for spec in SHEETS:
        src_path = asset_root / spec.path
        if not src_path.exists():
            print(f"SKIP     {spec.path} (not found)")
            skipped += 1
            continue

        out_name = Path(spec.path).stem + "_rows.png"
        out_path = output_dir / out_name

        warnings = generate_contact_sheet(spec, src_path, out_path)
        processed += 1

        status = "WARN" if warnings else "OK"
        print(f"{status:8s} {spec.path}")
        for w in warnings:
            print(f"         ! {w}")
            total_warnings.append(f"{spec.path}: {w}")

    print()
    print(f"Processed: {processed}, Skipped: {skipped}, Warnings: {len(total_warnings)}")

    if total_warnings:
        print()
        print("=== ALL WARNINGS ===")
        for w in total_warnings:
            print(f"  {w}")

    # Write summary
    summary_path = output_dir / "QA_SUMMARY.txt"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        f.write("Row Direction QA Summary\n")
        f.write(f"Source: {asset_root.relative_to(ROOT).as_posix()}\n")
        f.write(f"Processed: {processed}, Skipped: {skipped}\n")
        f.write(f"Warnings: {len(total_warnings)}\n\n")
        if total_warnings:
            for w in total_warnings:
                f.write(f"  {w}\n")
        else:
            f.write("  No issues detected.\n")
    print(f"\nSummary: {summary_path}")

    return 1 if total_warnings else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Row-direction QA for sprite sheets.")
    parser.add_argument("--root", default="raw",
                        help="Subdirectory under assets/image_pipeline/generated/ to check")
    sys.exit(run(parser.parse_args()))


if __name__ == "__main__":
    main()
