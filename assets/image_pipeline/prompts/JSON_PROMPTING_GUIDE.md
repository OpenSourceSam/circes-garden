# JSON Prompting Guide for Game Asset Generation

Adapted from the [JSON Prompt Translator](JSON%20Prompt%20Translator_%20A%20Unified%20Schema%20for%20UI%2C%20Diagrams%2C%20and%20Marketing%20Images.pdf) methodology for pixel art spritesheets and game assets.

---

## Why JSON Instead of Prose?

Models can't reliably follow vibes. A paragraph like "make a pixel art character facing four directions with idle animation" mixes layout, subject, style, and rules into one blob. The model picks up some parts and drops others — especially spatial/grid rules.

**JSON fixes this** by giving every rendering attribute its own discrete key-value field:

| Prose prompt | JSON prompt |
|---|---|
| "4x4 grid, 256px cells" | `"grid": { "columns": 4, "rows": 4, "cell_width_px": 256 }` |
| "facing toward the viewer" | `"facing": "front-facing (straight toward viewer, 6 o'clock)"` |
| "pixel art style like Stardew Valley" | `"style": { "aesthetic": "pixel art, Stardew Valley / 16-bit RPG" }` |

Each field is unambiguous. The model processes them independently instead of trying to parse a run-on sentence.

---

## The Spritesheet Schema

For game spritesheets, we use a custom `spritesheet` root key (adapted from the PDF's `marketing_image` pattern). Required sections:

```
{
  "spritesheet": {
    "canvas":            // image dimensions, background, format
    "grid":              // columns, rows, cell sizes, spacing
    "alignment_guides":  // guide lines for consistent character height
    "rows" or "cell_assignments":  // what goes in each cell
    "subject":           // character identity (hair, outfit, skin, etc.)
    "style":             // pixel art style, outline, shading rules
    "rules":             // hard constraints the model must follow
  }
}
```

### Section Breakdown

**canvas** — The output image itself
```json
"canvas": {
  "width_px": 1024,
  "height_px": 1024,
  "aspect_ratio": "1:1",
  "background": "transparent"
}
```
Why: Models default to arbitrary sizes. Explicit dimensions prevent this.

**grid** — How the image is divided
```json
"grid": {
  "columns": 4,
  "rows": 4,
  "cell_width_px": 256,
  "cell_height_px": 256,
  "total_cells": 16,
  "gaps_between_cells": "none",
  "borders": "none",
  "margins": "none",
  "labels_or_text_anywhere": "none"
}
```
Why: Models love adding borders, margins, labels, and decorative elements. Explicitly saying "none" for each prevents this.

**alignment_guides** — Guide lines baked into the reference image
```json
"alignment_guides": {
  "grid_dividers": {
    "color": "#000000 black",
    "positions": "y=256, y=512, y=768 and x=256, x=512, x=768"
  },
  "character_guides": {
    "color": "#FF00FF magenta",
    "lines": [
      {"y_px": 38, "role": "row 1 — top of head"},
      {"y_px": 218, "role": "row 1 — bottom of feet"}
    ]
  }
}
```
Why: Without visual guides, character heights drift between cells. Magenta lines are easy to strip in post-processing.

**rows** (Version A) or **cell_assignments** (Version B) — Content per cell

Version A describes 4 rows, each with a facing direction + 4 column poses:
```json
"rows": [{
  "row_number": 1,
  "facing": "front-facing — character looks straight toward the viewer",
  "clock_direction": "6 o'clock",
  "what_viewer_sees": "the character's face, chest, and front of body",
  "column_1": "idle frame 1 — neutral standing pose"
}]
```

Version B describes all 16 cells individually:
```json
"cell_assignments": [{
  "cell": "row1_col1",
  "x": "0-255", "y": "0-255",
  "facing": "front-facing (straight toward viewer, 6 o'clock)",
  "pose": "idle frame 1 — neutral stand"
}]
```

**subject** — Character identity (locked across all cells)
```json
"subject": {
  "name": "Circe",
  "hair": "long dark brown hair past shoulders",
  "outfit": "deep violet/purple Greek dress with small gold trim accents",
  "skin": "Mediterranean olive tone",
  "expression": "calm and focused"
}
```

**style** — Art style constraints
```json
"style": {
  "aesthetic": "pixel art, Stardew Valley or classic 16-bit RPG style",
  "outline": "dark 1-pixel outline around the entire character",
  "shading": "flat cluster shading, no smooth gradients",
  "antialiasing": "none — crisp pixel edges only, no blur",
  "character_height": "70% of cell height (approximately 180 pixels)"
}
```

**rules** — Hard constraints as an array of strings
```json
"rules": [
  "this is ONE image containing 16 small characters in a grid — NOT 16 separate images",
  "identical character identity across all 16 cells",
  "no character may cross a cell boundary into a neighboring cell",
  "consistent top-left lighting across all 16 cells"
]
```
Why: Rules prevent the most common failure modes (model generates 16 separate images, characters bleed across cells, lighting changes per cell).

---

## Key Techniques

### 1. Viewer-Relative Facing Terms

Never say "left" or "right" alone — models interpret these inconsistently.

| Bad | Good |
|---|---|
| "facing left" | "profile-left — looks toward 9 o'clock (left edge), viewer sees right side of body" |
| "facing right" | "profile-right — looks toward 3 o'clock (right edge), viewer sees left side of body" |
| "facing forward" | "front-facing — looks straight toward the viewer, 6 o'clock" |
| "facing away" | "back-facing — faces away from viewer, 12 o'clock" |

The clock-position reinforcement (6/12/9/3 o'clock) gives the model a second spatial anchor.

### 2. Reference Grid Template

Generate a pixel-perfect PNG grid template with Python/Pillow and upload it alongside the JSON prompt. The template contains:

- **Black (#000000) lines** — cell boundaries (3px wide)
- **Magenta (#FF00FF) lines** — character head/feet alignment guides (2px wide)
- **Transparent background**

The model draws characters between the guide lines, then you strip all magenta pixels in post-processing.

Grid math for a 4x4 sheet at 1024x1024:
```
Cell size:      256 x 256 px
Character:      180px tall (70% of cell)
Padding:        38px top + 38px bottom = (256 - 180) / 2
Head guides:    y = 38, 294, 550, 806
Feet guides:    y = 218, 474, 730, 986
Grid dividers:  y = 256, 512, 768  and  x = 256, 512, 768
```

### 3. Explicit Negation

Models add things you didn't ask for. Prevent this with explicit "none" fields:

```json
"gaps_between_cells": "none — cells touch edge to edge",
"borders": "none",
"margins": "none",
"labels_or_text_anywhere": "none",
"antialiasing": "none — crisp pixel edges only, no blur"
```

### 4. Redundant Anchoring

State the same constraint multiple ways. If it matters, say it in:
- The grid section (structural)
- The alignment_guides section (visual)
- The rules array (imperative)

Example — keeping characters inside cells:
- grid: `"gaps_between_cells": "none — cells touch edge to edge"`
- alignment_guides: `"rule": "no character part may cross a black grid line"`
- rules: `"no character may cross a cell boundary into a neighboring cell"`

### 5. Identity Locking

For multi-cell spritesheets, the model tends to drift character appearance. Lock it:

```json
"rules": [
  "identical character identity across all 16 cells — same face, outfit, proportions, palette"
]
```

For walk sheets generated separately from idle sheets, add to your prompt:
```json
"identity_reference": "match the character from the previously generated idle sheet"
```

---

## Row Direction Contract

All spritesheets in this project follow this row order (top to bottom):

| Row | Direction | Clock |
|-----|-----------|-------|
| 1 | Front-facing (toward viewer) | 6 o'clock |
| 2 | Back-facing (away from viewer) | 12 o'clock |
| 3 | Profile-left (looks left) | 9 o'clock |
| 4 | Profile-right (looks right) | 3 o'clock |

This matches the Godot spritesheet import order used in our game code.

---

## Version A vs Version B

| | Version A (Row-based) | Version B (Cell-based) |
|---|---|---|
| Structure | 4 rows, each with direction + columns | All 16 cells listed individually |
| Detail level | Row-level (model infers per-cell) | Explicit per cell |
| Best for | Models that handle hierarchy well | Models that need hand-holding |
| Verbosity | Medium | High |
| File | `circe_idle_v1_rows.json` | `circe_idle_v2_cells.json` |

Start with Version A. If the model produces wrong cells, try Version B.

---

## Workflow

1. **Write JSON prompt** for the asset (use existing ones as templates)
2. **Generate grid template** with Python if needed (or reuse `spritesheet_grid_1024.png`)
3. **Upload both** to Kimi K (grid image + JSON pasted as text)
4. **Evaluate output** — check grid alignment, directions, identity consistency
5. **Post-process** — strip guide lines, convert white bg to transparent, normalize

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `circe_idle_v1_rows.json` | Circe idle sheet — row-based prompt (tested, works) |
| `circe_idle_v2_cells.json` | Circe idle sheet — cell-based prompt (backup) |
| `spritesheet_grid_1024.png` | 1024x1024 grid template (upload with prompt) |
| `asset_prompts.json` | Internal pipeline metadata catalog (NOT for Kimi) |
| `KIMI_MEGA_PROMPT.md` | Legacy prose prompts (deprecated, use JSON instead) |
| `JSON_PROMPTING_GUIDE.md` | This file |
