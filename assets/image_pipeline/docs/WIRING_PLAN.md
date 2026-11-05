# Asset Wiring Execution Plan (Fresh-Start Handoff)

## Goal

Wire all generated visual assets into the playable game so v3 looks production-ready before export work.

## Source Inputs

- Generated assets: `assets/image_pipeline/generated/raw/`
- Runtime asset root: `assets/`
- Asset spec: `assets/image_pipeline/docs/ASSET_SPEC.md`
- Tooling policy: `assets/image_pipeline/learnings/image_tool_reliability.md`

## Constraints

- Do not rely on model-based image recognition for technical metadata.
- Use local scripted checks for dimensions/alpha/frame layout.
- Keep gameplay logic stable while replacing visuals.

## Phase A - Intake + Normalization

1. Build asset mapping table:
   - Input file (generated path) -> output file (`assets/...`) -> target format/size/layout.
2. Run deterministic metadata scan (Pillow):
   - width, height, alpha min/max, transparency coverage.
3. Normalize oversized sheets/images:
   - Character sheets: enforce expected frame math and final runtime dimensions.
   - Pig sheets: enforce 4-dir/2-dir variants as specified.
   - Props/icons: downscale to target gameplay dimensions with nearest-neighbor.
   - Prologue images: resize/crop to `1080x1240` while preserving composition.
4. Write normalized outputs to final runtime paths in `assets/`.

Acceptance for Phase A:
- Every required file in `assets/image_pipeline/docs/ASSET_SPEC.md` exists in runtime `assets/`.
- All outputs match expected dimensions and transparency requirements.

## Phase B - Scene/Script Wiring

1. Player/NPC animation integration:
   - Replace static character sprites with animated idle/walk sheet usage.
   - Ensure direction mapping (Down/Up/Left/Right) is correct.
2. Pig integration:
   - Add pig entity scene/script using generated pig animations.
   - Place pig(s) in world with simple idle/walk behavior.
3. Farm plot stage visuals:
   - Wire stage textures (`empty/planted/1/2/ready`) into plot display updates.
4. Prop/UI updates:
   - Replace boat/crafting/farm/sleep textures.
   - Replace inventory icon textures.
5. Prologue art integration:
   - Show `prologue_01` ... `prologue_07` with existing text screens.

Acceptance for Phase B:
- Visual assets appear in-game in expected places.
- No missing texture errors in output log.

## Phase C - Visual Polish Pass

1. Remove placeholder-looking labels where no longer needed.
2. Adjust sprite scaling/offsets for consistent world readability.
3. Tune layering/z-index so characters, props, and UI don’t overlap incorrectly.
4. Ensure credits + prologue visual style feels coherent.

Acceptance for Phase C:
- Game looks like a cohesive playable build, not prototype placeholders.

## Phase D - Regression + Validation

1. Run headless tests:
   - `Godot_v4.5.1-stable_win64.exe --headless --path . --script tests/run_all.gd`
2. Run the integration playthrough (the scene-based test_playthrough.tscn was replaced in October 2026):
   - `python tools/pixelart/playtest.py --script full`
3. Run visual screenshot capture pass (if headed session available):
   - `Godot_v4.5.1-stable_win64.exe --path . res://tests/visual/test_screenshot.tscn`
4. Fix regressions until stable.

Acceptance for Phase D:
- Headless suite passes.
- Playthrough completes without blockers.
- Visual screenshots reflect new assets.

## Deliverables

- Updated runtime assets under `assets/`.
- Wired gameplay scenes/scripts using new visuals.
- Updated screenshots in `tests/visual/screenshots/` (if generated this run).
- Short completion summary (what wired, what deferred, known issues).

## Suggested Execution Order (Single Session)

1. A1-A4
2. B1-B5
3. C1-C4
4. D1-D4
5. Final summary

## Defer Until After This Plan

- Android hardware validation on device.
- Additional optional VFX/juice not required for base asset wiring completion.
