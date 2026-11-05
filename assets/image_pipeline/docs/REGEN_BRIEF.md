# Kimmy K / Gemini Asset Fix Brief (Visual Blockers)

## Purpose
This brief documents exactly why visuals still look broken in runtime and what to regenerate first.
Use this as the handoff to the Kimmy K multipart Gemini pipeline.

## Executive Summary
- Not every file is broken, but **all character sets have at least one directional/action sheet issue**.
- Main character issue: **row direction ordering is inconsistent across sheets** (left/right swapped or duplicated).
- Main world issues:
  - tile visuals were rendered behind background layers due z-order setup,
  - plus selected Scylla ground tile indices are transparent.
- Result in-game: inverted facing, odd animation transitions, and visually empty terrain.

## Why This Happened
1. Generation drift from the spec:
- expected strict row contract (`Down, Up, Left, Right`) and fixed sheet sizes.
- actual outputs are oversized and row direction contracts vary by sheet.
2. Runtime assumed one global row mapping; generated sheets are not consistent enough for that.
3. Tile index sampling in `game/scenes/world.gd` uses transparent tile cells in key areas.
4. Tile sprites are currently created at a deeper negative z-order than background gradients, so map visuals can be present but hidden.

## Visual Evidence (Screenshots)
Reference images in `assets/image_pipeline/qa/audit_screenshots/`:

1. Character row audits:
- `assets/image_pipeline/qa/audit_screenshots/circe_idle_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/circe_walk_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/hermes_idle_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/hermes_walk_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/scylla_idle_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/scylla_walk_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/pig_walk_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/pig_run_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/pig_idle_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/pig_eat_rows.png`
- `assets/image_pipeline/qa/audit_screenshots/pig_sleep_rows.png`

2. Direction spot-checks:
- `assets/image_pipeline/qa/audit_screenshots/hermes_walk_row2_f0.png`
- `assets/image_pipeline/qa/audit_screenshots/hermes_walk_row3_f0.png`
- `assets/image_pipeline/qa/audit_screenshots/scylla_walk_row2_f0.png`
- `assets/image_pipeline/qa/audit_screenshots/scylla_walk_row3_f0.png`

3. Tile usage audits:
- `assets/image_pipeline/qa/audit_screenshots/scylla_used_tiles.png`
- `assets/image_pipeline/qa/audit_screenshots/aiaia_used_tiles.png`
- `assets/image_pipeline/qa/audit_screenshots/decor_used_tiles.png`

4. Runtime screenshot (flat terrain symptom):
- `tests/visual/screenshots/world.png`

## What Is Broken (Concrete)

### Character Direction Consistency
1. Circe:
- idle/walk side rows are reversed relative to expected runtime mapping.
- symptom: left/right appears inverted in gameplay.

2. Hermes:
- idle row order differs from walk row order for side directions.
- symptom: direction pops/inverts between idle and walk.

3. Scylla:
- walk side rows are malformed (right-facing duplication detected in audit).
- symptom: missing proper opposite-side movement.

4. Pig:
- walk/run side direction row ordering is inconsistent.
- idle/eat/sleep sheets do not cleanly follow a usable 2-direction contract.
- symptom: non-deterministic or wrong lateral facing for ambient pig states.

### Terrain Visibility
1. Tile visual layer ordering issue:
- `TileVisualLayer` is `z_index = -20` and each placed tile sprite is also `z_index = -20`, making effective draw depth too far behind backgrounds.
- symptom: map can look unloaded even when sprites were spawned.

2. Scylla zone ground tiles currently sampled from transparent cells:
- used tile coords `(0..5, 0)` in scylla atlas have ~`0%` opaque pixels.
- symptom: flat background color instead of textured ground.

## Priority Regeneration List

### P0 (Regenerate First)
1. `assets/image_pipeline/generated/raw/sprites/characters/circe/circe_idle.png`
2. `assets/image_pipeline/generated/raw/sprites/characters/circe/circe_walk.png`
3. `assets/image_pipeline/generated/raw/sprites/characters/hermes/hermes_idle.png`
4. `assets/image_pipeline/generated/raw/sprites/characters/hermes/hermes_walk.png`
5. `assets/image_pipeline/generated/raw/sprites/characters/scylla/scylla_idle.png`
6. `assets/image_pipeline/generated/raw/sprites/characters/scylla/scylla_walk.png`
7. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_walk.png`
8. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_run.png`
9. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_idle.png`
10. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_eat.png`
11. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_sleep.png`

### P1 (After Characters)
1. Re-export terrain-friendly tile selections in:
- `assets/image_pipeline/generated/raw/tilesets/scylla_cove_tileset_32.png`
- optionally `aiaia_tileset_32.png` and `greek_decor_tileset_32.png` for stronger readability.

## Required Generation Contract (Must Follow Exactly)
1. Character sheets (Circe/Hermes/Scylla walk+idle):
- dimensions: `256x256`
- frame size: `64x64`
- grid: `4x4`
- row order (top->bottom): `Down, Up, Left, Right`
- col order: 4-frame loop

2. Pig walk/run:
- dimensions: `256x256`
- frame size: `64x64`
- grid: `4x4`
- row order: `Down, Up, Left, Right`

3. Pig idle/eat/sleep:
- dimensions: `256x128`
- frame size: `64x64`
- grid: `4x2`
- row order: `Left, Right`

4. Tilesets:
- `32x32` tile grid, no spacing bleed.
- include clearly opaque full-ground tiles for primary fill rows.

## Prompt Addendum for Gemini (Paste Into Every Regen Prompt)
`CRITICAL CONTRACT: Output exact canvas size and exact frame grid. Do not upscale canvas. Do not add extra rows/columns. Row order must be strictly Down, Up, Left, Right (or Left, Right for pig 2-row sheets). Preserve identity and baseline alignment across all frames.`

## QC Gate Before Accepting Regenerated Files
1. Run local preflight script:
- `python assets/image_pipeline/tools/preflight.py`
2. Confirm row-direction audit manually with generated row panels (same method as this brief).
3. Reject any sheet with:
- wrong dimensions,
- inconsistent side direction ordering between idle and walk,
- duplicate side rows where opposite direction is expected.
