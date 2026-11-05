#!/usr/bin/env python3
"""Deterministic preflight checks for generated visual assets.

Enforces EXACT target dimensions for all asset kinds.
Previous version only checked divisibility — this version fails on any
size that doesn't match the runtime contract.

Usage:
  python assets/image_pipeline/tools/preflight.py                 # check raw/
  python assets/image_pipeline/tools/preflight.py --root normalized  # check normalized/
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass(frozen=True)
class AssetRule:
    path: str
    kind: str
    # Exact target dimensions (0 = don't enforce, e.g. tilesets)
    target_w: int = 0
    target_h: int = 0


# ── Exact dimension contracts ──────────────────────────────────────────
# character_4dir:  256×256   (4×4 grid of 64×64 frames)
# pig_4dir:        256×256   (4×4 grid of 64×64 frames)
# pig_2dir:        256×128   (4×2 grid of 64×64 frames)
# entity:          per-asset (see below)
# icon:            32×32
# prologue:        864×1184
# tileset:         32-grid aligned (no fixed size)

REQUIRED_ASSETS: list[AssetRule] = [
    # Prologue
    AssetRule("cutscenes/prologue/prologue_01.png", "prologue", 864, 1184),
    AssetRule("cutscenes/prologue/prologue_02.png", "prologue", 864, 1184),
    AssetRule("cutscenes/prologue/prologue_03.png", "prologue", 864, 1184),
    AssetRule("cutscenes/prologue/prologue_04.png", "prologue", 864, 1184),
    AssetRule("cutscenes/prologue/prologue_05.png", "prologue", 864, 1184),
    AssetRule("cutscenes/prologue/prologue_06.png", "prologue", 864, 1184),
    AssetRule("cutscenes/prologue/prologue_07.png", "prologue", 864, 1184),

    # Characters (4-direction)
    AssetRule("sprites/characters/circe/circe_idle.png", "character_4dir", 256, 256),
    AssetRule("sprites/characters/circe/circe_walk.png", "character_4dir", 256, 256),
    AssetRule("sprites/characters/hermes/hermes_idle.png", "character_4dir", 256, 256),
    AssetRule("sprites/characters/hermes/hermes_walk.png", "character_4dir", 256, 256),
    AssetRule("sprites/characters/scylla/scylla_idle.png", "character_4dir", 256, 256),
    AssetRule("sprites/characters/scylla/scylla_walk.png", "character_4dir", 256, 256),

    # Pig (4-direction)
    AssetRule("sprites/characters/pig/pig_walk.png", "pig_4dir", 256, 256),
    AssetRule("sprites/characters/pig/pig_run.png", "pig_4dir", 256, 256),

    # Pig (2-direction)
    AssetRule("sprites/characters/pig/pig_idle.png", "pig_2dir", 256, 128),
    AssetRule("sprites/characters/pig/pig_eat.png", "pig_2dir", 256, 128),
    AssetRule("sprites/characters/pig/pig_sleep.png", "pig_2dir", 256, 128),

    # Entities (exact recommended sizes)
    AssetRule("sprites/entities/boat.png", "entity", 128, 64),
    AssetRule("sprites/entities/crafting_table.png", "entity", 64, 64),
    AssetRule("sprites/entities/farm_plot.png", "entity", 64, 64),
    AssetRule("sprites/entities/farm_plot_stage_empty.png", "entity", 64, 64),
    AssetRule("sprites/entities/farm_plot_stage_planted.png", "entity", 64, 64),
    AssetRule("sprites/entities/farm_plot_stage_1.png", "entity", 64, 64),
    AssetRule("sprites/entities/farm_plot_stage_2.png", "entity", 64, 64),
    AssetRule("sprites/entities/farm_plot_stage_ready.png", "entity", 64, 64),
    AssetRule("sprites/entities/sleep_spot.png", "entity", 64, 64),

    # UI Icons
    AssetRule("sprites/ui/icon_moly_seed.png", "icon", 32, 32),
    AssetRule("sprites/ui/icon_moly.png", "icon", 32, 32),
    AssetRule("sprites/ui/icon_calming_draught.png", "icon", 32, 32),

    # Tilesets (32-grid only, no fixed total size)
    AssetRule("tilesets/aiaia_tileset_32.png", "tileset"),
    AssetRule("tilesets/scylla_cove_tileset_32.png", "tileset"),
    AssetRule("tilesets/greek_decor_tileset_32.png", "tileset"),
]


ROOT = Path(__file__).resolve().parents[3]


def resolve_paths(root_name: str) -> tuple[Path, Path]:
    """Return (asset_root, report_path) based on --root flag."""
    base = ROOT / "assets" / "image_pipeline" / "generated"
    asset_root = base / root_name
    report_path = base / f"preflight_report_{root_name}.json"
    return asset_root, report_path


def alpha_stats(image: Image.Image) -> dict[str, Any]:
    if "A" not in image.getbands():
        return {
            "has_alpha": False,
            "alpha_min": None,
            "alpha_max": None,
            "transparent_pixels": 0,
            "transparent_pct": 0.0,
        }

    alpha = image.getchannel("A")
    alpha_min, alpha_max = alpha.getextrema()
    histogram = alpha.histogram()
    transparent = histogram[0]
    total_pixels = image.width * image.height
    transparent_pct = round((transparent / total_pixels) * 100.0, 3)
    return {
        "has_alpha": True,
        "alpha_min": int(alpha_min),
        "alpha_max": int(alpha_max),
        "transparent_pixels": int(transparent),
        "transparent_pct": transparent_pct,
    }


def validate_dimensions(asset: AssetRule, width: int, height: int) -> list[str]:
    """Strict exact-size validation. Returns list of error strings."""
    errors: list[str] = []
    relative = asset.path

    if asset.kind == "tileset":
        # Tilesets: 32-grid alignment only
        if width % 32 != 0 or height % 32 != 0:
            errors.append(f"{relative}: expected 32-grid alignment, got {width}x{height}")
        return errors

    # Everything else: exact dimensions required
    if asset.target_w > 0 and asset.target_h > 0:
        if (width, height) != (asset.target_w, asset.target_h):
            errors.append(
                f"{relative}: expected EXACT {asset.target_w}x{asset.target_h}, "
                f"got {width}x{height}"
            )

    # Additional grid sanity for sprite sheets
    if asset.kind in {"character_4dir", "pig_4dir"}:
        if width % 4 != 0 or height % 4 != 0:
            errors.append(f"{relative}: dimensions not divisible by 4 (grid check)")

    if asset.kind == "pig_2dir":
        if width % 4 != 0 or height % 2 != 0:
            errors.append(f"{relative}: width not /4 or height not /2 (grid check)")

    return errors


def run(args: argparse.Namespace) -> int:
    asset_root, report_path = resolve_paths(args.root)

    report: dict[str, Any] = {
        "asset_root": asset_root.relative_to(ROOT).as_posix(),
        "required_count": len(REQUIRED_ASSETS),
        "mode": "STRICT (exact dimensions enforced)",
        "checks": {
            "prologue_exact_size": [864, 1184],
            "character_4dir_exact": [256, 256],
            "pig_4dir_exact": [256, 256],
            "pig_2dir_exact": [256, 128],
            "entity_exact": "per-asset (boat=128x64, others=64x64)",
            "icon_exact": [32, 32],
            "tileset_grid": "32x32 aligned",
            "alpha_policy": "sprites/tilesets require alpha, prologue may be RGB",
        },
        "assets": [],
        "errors": [],
        "warnings": [],
    }

    if not asset_root.exists():
        report["errors"].append(f"Missing asset root: {asset_root}")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote report: {report_path.as_posix()}")
        return 1

    for asset in REQUIRED_ASSETS:
        relative = asset.path
        file_path = asset_root / relative

        if not file_path.exists():
            report["errors"].append(f"Missing required asset: {relative}")
            continue

        with Image.open(file_path) as image:
            width, height = image.size
            bands = list(image.getbands())
            metadata: dict[str, Any] = {
                "path": relative,
                "kind": asset.kind,
                "width": width,
                "height": height,
                "target": f"{asset.target_w}x{asset.target_h}" if asset.target_w else "32-grid",
                "bands": bands,
            }
            metadata.update(alpha_stats(image))
            report["assets"].append(metadata)

            # Strict dimension check
            report["errors"].extend(validate_dimensions(asset, width, height))

            # Alpha channel check
            if asset.kind in {"character_4dir", "pig_4dir", "pig_2dir", "entity", "icon", "tileset"}:
                if not metadata["has_alpha"]:
                    report["errors"].append(f"{relative}: expected alpha channel")
                elif metadata["alpha_min"] == metadata["alpha_max"] == 255:
                    report["warnings"].append(f"{relative}: fully opaque alpha channel")

    # Extra files
    all_png = sorted(path.relative_to(asset_root).as_posix() for path in asset_root.rglob("*.png"))
    required_set = {asset.path for asset in REQUIRED_ASSETS}
    extras = [path for path in all_png if path not in required_set]
    report["extras"] = extras

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report: {report_path.as_posix()}")
    print(f"Required assets: {len(REQUIRED_ASSETS)}")
    print(f"Errors: {len(report['errors'])}")
    print(f"Warnings: {len(report['warnings'])}")

    if report["errors"]:
        for error in report["errors"]:
            print(f"  ERROR: {error}")
        return 1

    print("  All checks passed.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Strict preflight checks for generated visual assets.")
    parser.add_argument("--root", default="raw",
                        help="Subdirectory under assets/image_pipeline/generated/ to check "
                             "(default: raw, use 'normalized' after running normalize)")
    sys.exit(run(parser.parse_args()))


if __name__ == "__main__":
    main()
