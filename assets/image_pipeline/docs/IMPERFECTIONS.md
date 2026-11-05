# Asset Imperfections / Regen Candidates

This file tracks visual issues discovered during runtime wiring and playtest.
These are non-blocking for Phase 4 wiring and can be regenerated later.

## Status
- Last updated: 2026-02-10
- Policy: continue wiring, log issues for later regeneration pass.

## Observed so far
1. `assets/image_pipeline/generated/raw/sprites/characters/circe/circe_idle.png`
- Issue: Sheet dimensions are `1024x1024` instead of spec `256x256`.
- Impact: Runtime uses 256-cell slicing + scale compensation; works but indicates generation drift.

2. `assets/image_pipeline/generated/raw/sprites/characters/circe/circe_walk.png`
- Issue: `1024x1024` instead of `256x256`.
- Impact: Same as above.

3. `assets/image_pipeline/generated/raw/sprites/characters/hermes/hermes_idle.png`
- Issue: `1024x1024` instead of `256x256`.
- Impact: Same as above.

4. `assets/image_pipeline/generated/raw/sprites/characters/hermes/hermes_walk.png`
- Issue: `1024x1024` instead of `256x256`.
- Impact: Same as above.

5. `assets/image_pipeline/generated/raw/sprites/characters/scylla/scylla_idle.png`
- Issue: `1024x1024` instead of `256x256`.
- Impact: Same as above.

6. `assets/image_pipeline/generated/raw/sprites/characters/scylla/scylla_walk.png`
- Issue: `1024x1024` instead of `256x256`.
- Impact: Same as above.

7. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_idle.png`
- Issue: `1536x1024` instead of spec `256x128`.
- Impact: Runtime uses constrained 2-row directional extraction; works but indicates major sheet contract drift.

8. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_eat.png`
- Issue: `1536x1024` instead of `256x128`.
- Impact: Same as above.

9. `assets/image_pipeline/generated/raw/sprites/characters/pig/pig_sleep.png`
- Issue: `1536x1024` instead of `256x128`.
- Impact: Same as above.

10. `assets/image_pipeline/generated/raw/sprites/entities/boat.png`
- Issue: `1536x1024` instead of recommended prop-scale dimensions.
- Impact: Runtime compensates with scale tuning.

11. `assets/image_pipeline/generated/raw/sprites/entities/crafting_table.png`
- Issue: `1024x1024` instead of recommended `64x64` target-like art bounds.
- Impact: Runtime compensates with scale tuning.

12. `assets/image_pipeline/generated/raw/sprites/entities/farm_plot.png` and stage variants
- Issue: `1024x1024` each, significant transparent padding.
- Impact: Runtime compensates with scale tuning and stage-specific texture assignment.

13. `assets/image_pipeline/generated/raw/sprites/entities/sleep_spot.png`
- Issue: `1024x1024` instead of recommended `64x64`-scale prop output.
- Impact: Runtime compensates with scale tuning.

14. `assets/image_pipeline/generated/raw/sprites/ui/icon_moly_seed.png`
- Issue: `1024x1024` instead of recommended `32x32`.
- Impact: Runtime crops transparent bounds and scales for inventory readability.

15. `assets/image_pipeline/generated/raw/sprites/ui/icon_moly.png`
- Issue: `1024x1024` instead of recommended `32x32`.
- Impact: Same as above.

16. `assets/image_pipeline/generated/raw/sprites/ui/icon_calming_draught.png`
- Issue: `1024x1024` instead of recommended `32x32`.
- Impact: Same as above.

## Notes
- Prologue images are correctly `864x1184` per locked decision.
- All 33 required files exist and pass deterministic local preflight checks.
- `project.godot` icon warning was resolved by pointing `config/icon` to an existing PNG.

## Residual Warnings (Accepted for This Block)
1. Godot shutdown reports:
- `ObjectDB instances leaked at exit`
- `resources still in use at exit`
- Context: appears during automated test process shutdown and did not block gameplay flow, asset loading, or screenshots in this pass.

2. Headless playthrough reports:
- `WARN: credits transition not observed in headless run`
- Context: headed screenshot validation confirms credits scene capture and is the authoritative transition check for this block.
