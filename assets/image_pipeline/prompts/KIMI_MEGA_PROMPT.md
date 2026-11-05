# Circe's Garden — Full Asset Generation Prompt

Generate ALL visual assets for a pixel art farming game set in Greek mythology.
Each numbered section below is ONE image. Generate them in order.
Save each image with the exact filename shown.

---

## MASTER RULES (apply to EVERY image)

- **Style:** High-quality pixel art. Cozy farming sim readability. Greek mythology aesthetic.
- **Motifs:** White marble architecture, bronze statuary, sacred island flora, coastal ruins.
- **No anti-aliasing.** Crisp pixel edges only. No blur, no smoothing.
- **Consistent outline thickness** within each asset family.
- **Flat/cluster shading.** No blurry gradients on gameplay sprites.
- **Transparent background** on all sprites (unless noted otherwise).
- **PNG format** for all outputs.

### Direction Rules for Spritesheets

For sheets with 4 direction rows (top to bottom): **Down, Up, Left, Right**
For sheets with 2 direction rows (top to bottom): **Left, Right**

- **LEFT** = the character's face and body point toward the LEFT side of the image.
- **RIGHT** = the character's face and body point toward the RIGHT side of the image.
- **DOWN** = the character faces the viewer (toward the bottom of the image).
- **UP** = the character faces away from the viewer (toward the top of the image).

### Grid Rules

- All spritesheet frames must be **exactly the same size** within one sheet.
- Frames must tile perfectly with **no gaps, no overlap, no partial frames**.
- All frames aligned on the **same baseline** (feet at same Y position).

---

## BATCH 1: CHARACTER SPRITESHEETS (6 images)

Each character sheet is:
- **1:1 square ratio** (Kimi will generate ~1024x1024)
- **Transparent background**
- **4 columns x 4 rows** = 16 frames total
- Row order top to bottom: **Down, Up, Left, Right**
- Each row: 4-frame animation cycle

---

### IMAGE 1 — circe_idle.png

Generate a pixel art spritesheet for **Circe** (idle animation).

**Character brief:**
- Exiled witch-goddess. Graceful, intelligent, emotionally heavy but not fragile.
- Long dark hair, flowing dress, subtle jewelry accents.
- Deep violet/purple dress with warm gold details (Greek-inspired trim, small circlet).
- Hair: dark brown/near-black with subtle warm highlights.
- Skin: Mediterranean olive range.
- Accents: muted gold (not neon yellow).
- Expression: calm/melancholic focus.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing idle (4 frames)
- Row 2: Up-facing idle (4 frames)
- Row 3: Left-facing idle (4 frames)
- Row 4 (bottom): Right-facing idle (4 frames)

**Action:** Subtle standing idle. Gentle breathing sway or slight arm movement. 4-frame loop.

**IMPORTANT:** This is the FIRST Circe image. The next image (circe_walk) must look like the exact same character.

**Save as:** `circe_idle.png`

---

### IMAGE 2 — circe_walk.png

Generate a pixel art spritesheet for **Circe** (walk animation).

**Character:** EXACTLY the same Circe from Image 1. Same face, same outfit, same proportions, same palette. Only the pose changes.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing walk (4 frames)
- Row 2: Up-facing walk (4 frames)
- Row 3: Left-facing walk (4 frames)
- Row 4 (bottom): Right-facing walk (4 frames)

**Action:** Walking cycle. Dress sways gently with each step. 4-frame loop.

Maintain character identity from circe_idle.png. Same face, same outfit, same proportions. Only pose/action changes.

**Save as:** `circe_walk.png`

---

### IMAGE 3 — hermes_idle.png

Generate a pixel art spritesheet for **Hermes** (idle animation).

**Character brief:**
- Messenger god. Youthful, quick, mischievous energy.
- Short tousled light hair, light tunic/cloak, messenger-like trim.
- Pale sky-blue/cream garments with gold accents. Optional small wing motifs on sandals.
- Hair: warm blond/gold.
- Skin: fair-light.
- Expression: alert/playful confidence.
- Keep narrower/lighter silhouette than Circe. No heavy armor.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing idle (4 frames)
- Row 2: Up-facing idle (4 frames)
- Row 3: Left-facing idle (4 frames)
- Row 4 (bottom): Right-facing idle (4 frames)

**Action:** Alert standing idle. Slight weight-shift animation. 4-frame loop.

**Save as:** `hermes_idle.png`

---

### IMAGE 4 — hermes_walk.png

Generate a pixel art spritesheet for **Hermes** (walk animation).

**Character:** EXACTLY the same Hermes from Image 3. Same face, outfit, proportions, palette.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing walk (4 frames)
- Row 2: Up-facing walk (4 frames)
- Row 3: Left-facing walk (4 frames)
- Row 4 (bottom): Right-facing walk (4 frames)

**Action:** Light, quick walking cycle. Energetic but not running. 4-frame loop.

**Save as:** `hermes_walk.png`

---

### IMAGE 5 — scylla_idle.png

Generate a pixel art spritesheet for **Scylla** in monster form (idle animation).

**Character brief:**
- Tragic transformed sea monster. Monstrous and dangerous, but clearly tragic — NOT generic evil.
- Broad distorted upper mass with multi-head suggestion. Unstable asymmetry is acceptable.
- Sea-monster anatomy with human-remnant cues. Simplify head count to readable grouped forms.
- Body: teal/sea-green + deep blue-gray shadows.
- Accents: bruised purple or cold cyan highlights.
- Eyes/mouth: restrained glow — avoid cartoon neon.
- Expression: suffering/rage hybrid.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing idle (4 frames)
- Row 2: Up-facing idle (4 frames)
- Row 3: Left-facing idle (4 frames)
- Row 4 (bottom): Right-facing idle (4 frames)

**Action:** Writhing idle pose. Multiple heads weave slowly. Menacing but tragic. 4-frame cycle.

Maintain same monster mass across all directions. Do not let side views collapse into a generic blob.

**Save as:** `scylla_idle.png`

---

### IMAGE 6 — scylla_walk.png

Generate a pixel art spritesheet for **Scylla** (walk/movement animation).

**Character:** EXACTLY the same Scylla monster from Image 5. Same form, palette, mass.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing walk (4 frames)
- Row 2: Up-facing walk (4 frames)
- Row 3: Left-facing walk (4 frames)
- Row 4 (bottom): Right-facing walk (4 frames)

**Action:** Lurching, dragging movement. Heavy and threatening. 4-frame loop.

**Save as:** `scylla_walk.png`

---

## BATCH 2: PIG SPRITESHEETS (5 images)

The pig is a cozy farm animal decoration. Same pig identity across ALL 5 sheets.

**Pig visual brief (use for ALL pig images):**
- Cozy domesticated farm pig. Rounded, friendly, readable at small scale.
- Warm pink/rose body tones with earthy shadow tones.
- Keep proportions and snout/ear shape identical across all sheets.

---

### IMAGE 7 — pig_walk.png (4-direction)

Generate a pixel art spritesheet for a **pig** (walk animation).

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing walk (4 frames)
- Row 2: Up-facing walk (4 frames)
- Row 3: Left-facing walk (4 frames)
- Row 4 (bottom): Right-facing walk (4 frames)

**Action:** Relaxed walking gait. Trotting along happily. 4-frame cycle.

**This is the FIRST pig image.** All other pig sheets must match this pig exactly.

**Save as:** `pig_walk.png`

---

### IMAGE 8 — pig_run.png (4-direction)

Same pig as Image 7. EXACTLY the same pig — same proportions, same colors.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 4 rows.
- Row 1 (top): Down-facing run (4 frames)
- Row 2: Up-facing run (4 frames)
- Row 3: Left-facing run (4 frames)
- Row 4 (bottom): Right-facing run (4 frames)

**Action:** Urgent running. Ears flopping, legs pumping. Still cute. 4-frame cycle.

**Save as:** `pig_run.png`

---

### IMAGE 9 — pig_idle.png (2-direction)

Same pig as Image 7. This sheet has only 2 directions.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 2 rows in the **TOP HALF** of the image.
- Bottom half of the image should be empty/transparent.
- Row 1 (top): Left-facing idle (4 frames)
- Row 2: Right-facing idle (4 frames)

**Action:** Standing relaxed. Subtle breathing or ear twitch. 4-frame cycle.

**Save as:** `pig_idle.png`

---

### IMAGE 10 — pig_eat.png (2-direction)

Same pig as Image 7. 2 directions only.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 2 rows in the **TOP HALF** of the image.
- Bottom half empty/transparent.
- Row 1 (top): Left-facing eat (4 frames)
- Row 2: Right-facing eat (4 frames)

**Action:** Head-down nibble posture. Snout to ground, chewing. 4-frame eating cycle.

**Save as:** `pig_eat.png`

---

### IMAGE 11 — pig_sleep.png (2-direction)

Same pig as Image 7. 2 directions only.

**Sheet layout:**
- 1:1 square image, transparent background.
- EXACTLY 4 columns x EXACTLY 2 rows in the **TOP HALF** of the image.
- Bottom half empty/transparent.
- Row 1 (top): Left-facing sleep (4 frames)
- Row 2: Right-facing sleep (4 frames)

**Action:** Curled up sleeping. Gentle breathing animation — body rises and falls slightly. 4-frame cycle.

**Save as:** `pig_sleep.png`

---

## BATCH 3: ENTITY SPRITES (8 images)

Each entity is a **single static sprite** (not animated, not a spritesheet).
All are 1:1 square, transparent background.
Top-down or slight ¾ top-down view, matching the game camera angle.

---

### IMAGE 12 — boat.png

A small wooden **Greek-style boat**. Weathered timber, simple sail or oars visible. Beached on a sandy shore. Slight top-down angle. Wider than tall (the boat is horizontal).

Pixel art, cozy style, Greek mythology aesthetic. Single sprite on transparent background.

**Save as:** `boat.png`

---

### IMAGE 13 — crafting_table.png

A stone-topped **crafting table** with mortar, pestle, and small vials. Ancient Greek / herbalist aesthetic. Slight top-down view. Should clearly read as "crafting station" even at small size.

Pixel art, transparent background.

**Save as:** `crafting_table.png`

---

### IMAGE 14 — farm_plot_stage_empty.png

An **empty tilled soil farm plot**. Dark rich earth in a rectangular garden bed shape. Top-down view. Just dirt — no plants.

**IMPORTANT:** This is the first of 5 farm plot stages. ALL 5 must use the EXACT SAME base soil/plot shape and color. Only the plant growth changes between stages.

Pixel art, transparent background.

**Save as:** `farm_plot_stage_empty.png`

---

### IMAGE 15 — farm_plot_stage_planted.png

Farm plot with a **tiny seed or just-breaking seedling**. Same soil base as Image 14. A tiny green dot or seedling barely visible.

Same plot shape and soil as Image 14.

**Save as:** `farm_plot_stage_planted.png`

---

### IMAGE 16 — farm_plot_stage_1.png

Farm plot with a **small growing plant**. Short green stem with 1-2 small leaves. Clearly growing but small — about 1/3 of final height.

Same plot shape and soil as Image 14.

**Save as:** `farm_plot_stage_1.png`

---

### IMAGE 17 — farm_plot_stage_2.png

Farm plot with a **medium plant**. Taller stem, several leaves, starting to show golden color (this is moly, a magical herb). About 2/3 of final height.

Same plot shape and soil as Image 14.

**Save as:** `farm_plot_stage_2.png`

---

### IMAGE 18 — farm_plot_stage_ready.png

Farm plot with **fully grown golden moly herb**. Bright golden flower/herb at full height. Should feel magical — slight glow or shimmer quality. Ready to harvest.

Same plot shape and soil as Image 14.

**Save as:** `farm_plot_stage_ready.png`

---

### IMAGE 19 — sleep_spot.png

A simple **bedroll or sleeping mat**. Greek/ancient style — woven fabric on the ground, maybe a small pillow. Cozy rest spot. Top-down view. Should read as "rest here."

Pixel art, transparent background.

**Save as:** `sleep_spot.png`

---

## BATCH 4: UI ICONS (3 images)

Each icon is a **single item icon** for the inventory display.
1:1 square, transparent background.
Must read clearly at very small display size (32x32 pixels final).
Bold, clean, high contrast. Item centered in frame.

---

### IMAGE 20 — icon_moly_seed.png

**Golden seed icon.** A small seed in warm amber/gold color. Simple teardrop or oval shape. Bold and clear.

**Save as:** `icon_moly_seed.png`

---

### IMAGE 21 — icon_moly.png

**Golden moly herb icon.** A bright gold flower with a short green stem. The harvested magical herb. Should match the golden plant from Image 18 (farm_plot_stage_ready).

**Save as:** `icon_moly.png`

---

### IMAGE 22 — icon_calming_draught.png

**Potion vial icon.** A small glass bottle with blue-tinted liquid inside. Cork stopper on top. Calming, serene color. This is the crafted potion item.

**Save as:** `icon_calming_draught.png`

---

## BATCH 5: TILESETS (3 images)

Each tileset is a **tile atlas** with 32x32 pixel tiles in a grid.
NOT transparent background (solid colors fill each tile) — EXCEPT the decor tileset which uses transparency.
Tiles must align perfectly to a 32-pixel grid with no gaps or bleed.
Each atlas: at least **16 columns x 8 rows** (= 128+ tiles).
Use 3:2 ratio if possible.

---

### IMAGE 23 — aiaia_tileset_32.png

**Aiaia Island tileset.** Warm, sunny, fertile garden island.

Tile categories (organize roughly by rows):
- **Rows 0-1:** Grass variants (5+ types), dirt path, path edge transitions
- **Rows 2-3:** Ground textures — flowers in grass, garden soil, stone path, mixed grass/dirt
- **Rows 4-5:** Garden features — hedges, flower beds, herb garden borders, small rocks
- **Rows 6-7:** Architecture — marble floor tiles, column bases, low walls, stone steps

**Palette:** Warm greens, golden yellows, warm browns, white marble accents. Cozy Greek island garden feeling.

32x32 pixel grid. At least 16 columns x 8 rows. No anti-aliasing. Tiles should connect seamlessly to their neighbors.

**Save as:** `aiaia_tileset_32.png`

---

### IMAGE 24 — scylla_cove_tileset_32.png

**Scylla's Cove tileset.** Dark, foreboding coastal rocks.

Tile categories:
- **Rows 0-1:** Dark shoreline — wet rocks, tide pools, dark sand transitions
- **Rows 2-3:** Dark ground — rocky surfaces, cracked stone, deep shadow ground variants
- **Rows 4-5:** Coastal features — barnacle rocks, seaweed patches, bone fragments, coral
- **Rows 6-7:** Cave/cliff elements — dark wall faces, cave mouth edges, dripping stone

**Palette:** Deep blue-grays, teal shadows, dark purple-blacks. Cold and menacing but not cartoonish.

32x32 pixel grid. At least 16 columns x 8 rows. No anti-aliasing.

**Save as:** `scylla_cove_tileset_32.png`

---

### IMAGE 25 — greek_decor_tileset_32.png

**Greek architectural decoration tileset.** Overlay props that work on both the warm Aiaia and dark Scylla tilesets.

**This tileset uses TRANSPARENT background** — tiles are individual decorative props placed over the ground tilesets.

Tile categories:
- **Rows 0-1:** Marble path tiles (4+ variants), stone borders, paving patterns
- **Rows 2-3:** Column pieces — base, shaft, capital, broken column, fallen column
- **Rows 4-5:** Ruins and statues — broken wall, archway pieces, rubble, bronze statue base, small statue
- **Rows 6-7:** Nature/sacred props — sacred grove tree, laurel bush, offering bowl, torch/brazier

**Palette:** White marble, warm bronze, aged stone. Must work when overlaid on either tileset.

32x32 pixel grid. At least 16 columns x 8 rows. Transparent background.

**Save as:** `greek_decor_tileset_32.png`

---

## BATCH 6: PROLOGUE CUTSCENES (7 images)

These are **painterly/illustrative** images — NOT pixel art.
Full-frame portrait artwork for narrative screens.
**2:3 ratio** (portrait orientation). High resolution.
No transparent background — full painted scenes.
Greek mythology atmosphere. Cohesive visual style across all 7.
Avoid modern objects, clothing, or settings.

---

### IMAGE 26 — prologue_01.png

**Circe on Aiaia.** A divine but isolated woman stands on a lush green Mediterranean island. Golden sunlight. She's among herbs and wild plants — beautiful but clearly alone. Goddess-like presence but with visible loneliness.

Portrait composition. Warm palette. Painterly style.

**Save as:** `prologue_01.png`

---

### IMAGE 27 — prologue_02.png

**The art of pharmaka.** Close-up of hands working with glowing herbs, mortar and pestle, mysterious plant essences. Magical green and gold light emanates from the herbs. The ancient craft of herbal magic.

Portrait composition. Intimate, magical atmosphere. Painterly.

**Save as:** `prologue_02.png`

---

### IMAGE 28 — prologue_03.png

**The love triangle.** Circe watches Glaucus (a sea-god with blue-green tones, handsome) who gazes at Scylla (a beautiful human woman with dark hair). Circe's jealousy is visible in her expression. Coastal setting with waves.

Portrait composition. Romantic tension. Warm vs cool color contrast. Painterly.

**Save as:** `prologue_03.png`

---

### IMAGE 29 — prologue_04.png

**The poisoning.** Circe pours dark liquid poison into a bathing pool at night. The ominous green-purple liquid spreads through the water. Her expression: guilty but determined. Dark, foreboding atmosphere.

Portrait composition. The poison should look viscerally wrong. Painterly.

**Save as:** `prologue_04.png`

---

### IMAGE 30 — prologue_05.png

**Scylla's transformation.** A beautiful woman mid-transformation into a horrific sea monster. Multiple heads beginning to emerge from her body. Her human form distorting and twisting. The moment of irreversible change.

Portrait composition. Body horror but tasteful — tragic, not gory. Should evoke pity. Painterly.

**Save as:** `prologue_05.png`

---

### IMAGE 31 — prologue_06.png

**Exile and guilt.** Circe alone on Aiaia, staring out at the sea toward the distant strait where Scylla now lives. Slumped, defeated posture. Sunset or overcast sky. The weight of what she's done. Empty island stretches behind her.

Portrait composition. Melancholic, lonely. Blue-gray mood. Painterly.

**Save as:** `prologue_06.png`

---

### IMAGE 32 — prologue_07.png

**Fragile hope.** Circe holds a single golden moly seedling, looking at it with careful, fragile hope. Warm dawn light breaks through clouds. Green growth beginning around her. The start of her attempt to make things right.

Portrait composition. Hopeful but delicate. Golden light, green growth. The emotional turn toward the game. Painterly.

**Save as:** `prologue_07.png`

---

## POST-GENERATION CHECKLIST

After generating all images, verify:

1. All spritesheets have the correct number of columns and rows
2. Direction rows are in the correct order (Down/Up/Left/Right for 4-dir, Left/Right for 2-dir)
3. Character identity is consistent between idle and walk sheets
4. Farm plot stages share the same base soil shape
5. Tilesets align to 32px grid
6. All prologue images are portrait orientation
7. All sprite backgrounds are transparent
8. No anti-aliasing or blur on pixel art sprites

### File Destination Map

After download, place files in these folders:

```
assets/image_pipeline/generated/raw/
  sprites/characters/circe/      <- circe_idle.png, circe_walk.png
  sprites/characters/hermes/     <- hermes_idle.png, hermes_walk.png
  sprites/characters/scylla/     <- scylla_idle.png, scylla_walk.png
  sprites/characters/pig/        <- pig_walk.png, pig_run.png, pig_idle.png, pig_eat.png, pig_sleep.png
  sprites/entities/              <- boat.png, crafting_table.png, farm_plot_stage_*.png, sleep_spot.png
  sprites/ui/                    <- icon_moly_seed.png, icon_moly.png, icon_calming_draught.png
  tilesets/                      <- aiaia_tileset_32.png, scylla_cove_tileset_32.png, greek_decor_tileset_32.png
  cutscenes/prologue/            <- prologue_01.png through prologue_07.png
```

### Normalize Pipeline

After placing files, run:

```bash
python assets/image_pipeline/tools/normalize_assets.py
python assets/image_pipeline/tools/preflight.py --root normalized
python assets/image_pipeline/tools/row_direction_qa.py --root normalized
```
