# Asset Pipeline Workflow

How to go from Kimi K outputs to game-ready assets.

## The Problem

Kimi enforces a ~1K minimum resolution. Our runtime needs exact sizes (256x256, 256x128, 64x64, 32x32, etc). The pipeline below normalizes oversized outputs to exact spec.

## Quick Reference (Copy-Paste Commands)

```bash
# Step 0: Split composite images (if Kimi generated idle+walk as one image)
python assets/image_pipeline/tools/split_composites.py

# Step 1: Normalize oversized Kimi outputs
python assets/image_pipeline/tools/normalize_assets.py

# Step 2: Check dimensions pass strict validation
python assets/image_pipeline/tools/preflight.py --root normalized

# Step 3: Generate row-direction contact sheets for manual QA
python assets/image_pipeline/tools/row_direction_qa.py --root normalized

# Step 4: Review contact sheets in assets/image_pipeline/qa/row_qa/
#   - Open each *_rows.png and verify direction labels match the art
#   - Check QA_SUMMARY.txt for automated warnings

# Step 5: When satisfied, overwrite originals
python assets/image_pipeline/tools/normalize_assets.py --in-place
```

## Detailed Steps

### 0. Split composites (if applicable)

If Kimi generated idle+walk as stacked composite images for identity consistency,
drop them in `assets/image_pipeline/generated/composites/` with these names:

```
composites/
  circe_composite.png       -> splits into circe_idle.png + circe_walk.png
  hermes_composite.png      -> splits into hermes_idle.png + hermes_walk.png
  scylla_composite.png      -> splits into scylla_idle.png + scylla_walk.png
  pig_4dir_composite.png    -> splits into pig_walk.png + pig_run.png
  pig_2dir_composite.png    -> splits into pig_idle.png + pig_eat.png + pig_sleep.png
```

Run: `python assets/image_pipeline/tools/split_composites.py`

This cuts composites into individual sheets and places them in `raw/`.
If you got individual sheets directly from Kimi, skip this step.

### 1. Drop Kimi outputs

Place generated files in (or confirm split tool placed them):
```
assets/image_pipeline/generated/raw/
  cutscenes/prologue/prologue_01.png  ... prologue_07.png
  sprites/characters/circe/circe_idle.png, circe_walk.png
  sprites/characters/hermes/hermes_idle.png, hermes_walk.png
  sprites/characters/scylla/scylla_idle.png, scylla_walk.png
  sprites/characters/pig/pig_idle.png, pig_walk.png, pig_run.png, pig_eat.png, pig_sleep.png
  sprites/entities/boat.png, crafting_table.png, farm_plot.png, etc.
  sprites/ui/icon_moly_seed.png, icon_moly.png, icon_calming_draught.png
  tilesets/aiaia_tileset_32.png, scylla_cove_tileset_32.png, greek_decor_tileset_32.png
```

### 2. Run normalize

```bash
python assets/image_pipeline/tools/normalize_assets.py
```

This reads from `raw/` and writes exact-size copies to `normalized/`.

**Expected output:**
```
RESIZE   sprites/characters/circe/circe_idle.png: 1024x1024 -> 256x256
RESIZE   sprites/characters/pig/pig_idle.png: 1536x1024 -> 256x128
OK       cutscenes/prologue/prologue_01.png (already 864x1184)
COPY     tilesets/aiaia_tileset_32.png (1024x1024, tileset pass-through)
...
Summary: 23 resized, 7 already correct, 3 copied, 0 missing, 0 warnings
```

### 3. Run strict preflight

```bash
python assets/image_pipeline/tools/preflight.py --root normalized
```

**Expected output (passing):**
```
Errors: 0
Warnings: 0
  All checks passed.
```

If errors appear, the normalize step missed something or files are missing.

### 4. Run row QA

```bash
python assets/image_pipeline/tools/row_direction_qa.py --root normalized
```

Output goes to `assets/image_pipeline/qa/row_qa/`:
- `circe_idle_rows.png` - labeled 4x upscaled row strips
- `pig_eat_rows.png` - etc.
- `QA_SUMMARY.txt` - all warnings

**What to look for in contact sheets:**
- Row labeled "Down" should show character facing toward viewer
- Row labeled "Up" should show character's back
- Row labeled "Left" should show character facing left
- Row labeled "Right" should show character facing right
- Pig 2-dir sheets only have Left and Right rows

**Red flags:**
- "DUPLICATE" warning = two rows are pixel-identical (wrong)
- Left/Right look identical without flip = same direction drawn twice
- Directions look shuffled compared to labels

### 5. Accept and overwrite

When everything looks good:

```bash
python assets/image_pipeline/tools/normalize_assets.py --in-place
```

This overwrites the originals in `raw/` with the normalized versions.

## Exact Size Contracts

| Kind | Target Size | Grid | Frame Size |
|------|------------|------|------------|
| character_4dir | 256x256 | 4x4 | 64x64 |
| pig_4dir | 256x256 | 4x4 | 64x64 |
| pig_2dir | 256x128 | 4x2 | 64x64 |
| entity (boat) | 128x64 | - | - |
| entity (others) | 64x64 | - | - |
| icon | 32x32 | - | - |
| prologue | 864x1184 | - | - |
| tileset | 32-grid aligned | 32x32 tiles | - |

## If Row Directions Are Wrong

The normalize pipeline only resizes - it does NOT reorder rows. If Kimi generated rows in the wrong order, you need to either:

1. Re-prompt Kimi with stricter direction instructions
2. Manually reorder rows in an image editor
3. (Future) Add a `--swap-rows 2,3` flag to normalize_assets.py

The row contract is always: **Down, Up, Left, Right** (top to bottom) for 4-dir sheets, and **Left, Right** for 2-dir sheets.
