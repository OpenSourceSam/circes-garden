# Spritesheet Generation Pipeline

Step-by-step workflow for generating pixel art character spritesheets. Follow this document top to bottom, completing one spritesheet at a time.

---

## What You're Making

Each spritesheet is a single 1024x1024 PNG containing character frames in a grid of 256x256 cells.

**4-direction sheets** (4x4 grid, 16 cells): front, back, left, right — 4 animation frames each.
**2-direction sheets** (4x2 grid, 8 cells): left, right only — 4 animation frames each. Content in top half, bottom half empty.

Output format: `{character}_{action}.png` (e.g. `circe_idle.png`)

---

## Inputs (Provided to You)

For each spritesheet you will receive:

1. **This pipeline doc** (read once, follow for every sheet)
2. **Grid template image** — `spritesheet_grid_1024.png` — a 1024x1024 PNG with:
   - Black (#000000) lines at cell boundaries (x/y = 256, 512, 768)
   - Magenta (#FF00FF) lines for character head/feet alignment guides
3. **JSON prompt file** — one per spritesheet, containing exact character description, grid layout, facing directions, and animation frame descriptions

---

## Step 1: Generate the Spritesheet

1. Read the JSON prompt file for the current asset
2. Use the grid template as a visual reference for alignment
3. Generate a 1024x1024 pixel art spritesheet following the JSON spec exactly:
   - **4-dir sheets**: 4x4 grid, 256px cells. Row 1: front (6 o'clock), Row 2: back (12 o'clock), Row 3: left (9 o'clock), Row 4: right (3 o'clock)
   - **2-dir sheets**: 4x2 grid in top half only. Row 1: left (9 o'clock), Row 2: right (3 o'clock). Bottom half empty.
   - 4 animation frames per row (columns 1-4)
4. Character should be ~180px tall (70% of 256px cell), centered in each cell

---

## Step 2: Clean Up the Output

After generation, verify and fix:

1. **Grid/guide lines** — Remove any visible black grid lines or magenta guide lines from the final image. These are scaffolding only.
2. **Background** — Should be fully transparent (alpha = 0). If the generator added a colored background, extract the characters using color-based masking (detect character colors: skin, hair, outfit, outline — not background).
3. **Cell boundaries** — No character part should bleed across cell boundaries. If any frames overlap into adjacent cells, crop them to stay within their 256x256 cell.

---

## Step 3: Save the Output

Save the clean 1024x1024 PNG with transparent background.

Filename: Use the `id` from the JSON prompt (e.g. `circe_idle`, `hermes_walk`).

---

## Step 4: Quality Checklist

Before moving to the next spritesheet, verify all of these:

- [ ] Image is exactly 1024x1024 pixels
- [ ] Grid matches JSON spec (4x4 for 4-dir, 4x2 for 2-dir) with 256x256 cells
- [ ] Directions match JSON row assignments (check clock positions)
- [ ] For 2-dir sheets: bottom half is completely empty/transparent
- [ ] Character identity is consistent across all cells (same face, outfit, proportions, colors)
- [ ] No cell bleeding (characters stay within their cell boundaries)
- [ ] Transparent background (no colored bg)
- [ ] Pixel art style (crisp edges, no blur, no anti-aliasing)
- [ ] Animation frames show subtle differences (not 4 identical copies)

---

## Step 5: Identity Chaining

When generating a walk sheet after an idle sheet for the same character:
- The walk sheet character MUST look identical to the idle sheet character
- Same face, same outfit, same proportions, same color palette
- Only the pose/action changes

The JSON prompt for walk sheets will include an identity reference rule reminding you of this.

---

## Asset Queue

Generate in this order. Complete each fully before starting the next.

| # | Asset ID | JSON Prompt File | Character | Action | Status |
|---|----------|-----------------|-----------|--------|--------|
| 1 | `circe_idle` | `circe_idle_v1_rows.json` | Circe | Idle breathing | DONE |
| 2 | `circe_walk` | `circe_walk.json` | Circe | Walking cycle | TODO |
| 3 | `hermes_idle` | `hermes_idle.json` | Hermes | Idle standing | TODO |
| 4 | `hermes_walk` | `hermes_walk.json` | Hermes | Walking cycle | TODO |
| 5 | `scylla_idle` | `scylla_idle.json` | Scylla | Idle writhing | TODO |
| 6 | `scylla_walk` | `scylla_walk.json` | Scylla | Lurching movement | TODO |
| 7 | `pig_walk` | `pig_walk.json` | Pig | Walking trot (4-dir) | TODO |
| 8 | `pig_run` | `pig_run.json` | Pig | Running (4-dir) | TODO |
| 9 | `pig_idle` | `pig_idle.json` | Pig | Idle standing (2-dir) | TODO |
| 10 | `pig_eat` | `pig_eat.json` | Pig | Eating (2-dir) | TODO |
| 11 | `pig_sleep` | `pig_sleep.json` | Pig | Sleeping (2-dir) | TODO |

---

## Common Issues and Fixes

**Model generates 16 separate images instead of one grid:**
Re-emphasize in the prompt: "ONE image containing 16 small characters in a grid."

**Characters bleed across cell boundaries:**
Add explicit cell coordinate ranges. Use the grid template as visual reference.

**Directions are wrong (e.g. profile views swapped):**
Use clock position anchoring: "profile-left looks toward 9 o'clock (left edge of image)."

**Character identity drifts between cells:**
Lock identity explicitly: "identical character identity across all 16 cells — same face, outfit, proportions, palette."

**Background is not transparent:**
Use color-based character extraction in post-processing. Detect character colors (outfit, skin, hair) rather than trying to detect "background."

**Grid lines remain in final output:**
Strip all pixels matching #000000 (pure black grid lines) and #FF00FF (magenta guide lines) that fall on known grid/guide line positions.

---

## Alternative Approach: Direction-by-Direction Generation

The current approach (generate all 16 cells in one shot) maximizes consistency but can reduce quality — the model spreads its detail budget across 16 small figures.

A possible alternative for higher quality:

1. **Generate the front-facing character first** as a standalone high-quality image (single figure, full detail)
2. **Get approval** on the front-facing design before proceeding
3. **Generate each remaining direction as a variation** — feed the approved front-facing image back to the model and ask for back, left, right views that match it exactly
4. **Composite all directions onto the grid** — stitch the individual direction images into the final 4x4 spritesheet programmatically

Trade-offs:
- **Pro**: Higher per-cell quality since the model focuses on one figure at a time
- **Pro**: Approval checkpoint before committing to all 16 cells
- **Con**: More generation steps (4-5 per sheet instead of 1)
- **Con**: Requires a stitching/compositing step
- **Con**: Identity drift risk between separate generations (mitigated by feeding reference image)

This has not been tested yet. Try the current single-shot approach first and fall back to this if quality is insufficient.
