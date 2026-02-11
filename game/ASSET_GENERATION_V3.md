# Asset Generation Spec v3

**Project:** Circe's Garden v3  
**Purpose:** Source-of-truth spec for generating all visual assets needed through Phase 4 polish, including opening cutscene images.  
**Output consumer:** Another AI generation agent (copy-paste prompt ready).

---

## 1) Locked Decisions (From Chunk Plan)

- Scope: all assets needed for current v3 gameplay + opening cutscene images.
- Visual direction: cozy Stardew-like readability with Greek mythology aesthetics (white marble, bronze statuary, temple motifs).
- Gameplay character quality target: high-detail pixel art.
- Character frame size: `64x64`.
- Tile size: `32x32`.
- Animation baseline: `idle + walk` for gameplay characters.
- Pig scope: interactive pig set with `idle + walk + eat + sleep + run` (direction rules below).
- Spritesheet organization: separate sheet per action per character.
- Prologue image count: `7` (one per text screen).
- Prologue image style: painterly/illustrative.
- Prologue image resolution: `1080x1240` (match game viewport).
- File format: `PNG` for gameplay assets and cutscene images.
- Naming: strict deterministic names only.
- Doc output location selected by owner: `game/ASSET_GENERATION_V3.md`.

---

## 2) Style References

Use these as visual guidance only (not as dimension authority):

- `game/Concept Art/Circe-SpriteSheet-Gemini.jpg`
- `game/Concept Art/ConceptArt3.png`
- `game/Concept Art/ConceptArt4.png`
- `game/Concept Art/CutSceneHD-ConceptArt.jpg`
- `game/Concept Art/MapExample.png`

Lore references for character/cutscene accuracy:
- `game/LORE_SOURCES.md`
- `Circe - Madeline Miller.txt`
- https://circe.fandom.com/wiki/Circe_Wiki

Target tone:
- Cozy, readable, warm.
- Greek myth layer in architecture and props: marble columns, bronze statues, sacred groves, stonework, coastal ruins.
- Avoid modern/fantasy-tech motifs.

---

## 3) Global Technical Standards

### 3.1 Pixel Rules

- No anti-aliasing.
- Clean silhouettes at gameplay zoom.
- Consistent outline thickness per asset family.
- Flat/cluster shading (no blurry gradients for gameplay sprites).

### 3.2 Gameplay Sprite Rules

- Frame size: `64x64`.
- Direction row order: `Down, Up, Left, Right`.
- Per-action sheet layout: `4 columns x 4 rows`.
- Sheet size per action: `256x256`.
- Baseline alignment: all frames aligned to same foot baseline.

### 3.3 Tile Rules

- Tile size: `32x32`.
- Atlas sheets should align to 32-grid with no spacing bleed.

### 3.4 Cutscene Image Rules

- Size: `1080x1240`.
- Format: PNG.
- Full-frame artwork, composed for portrait viewport.

---

## 4) Consistency Lock Protocol (Use In Every Prompt)

Required consistency phrases:
- "Keep lighting consistent across all frames."
- "Match exact character proportions in every frame."
- "Align all frames on same baseline."
- "Same character identity in each frame."

FRAME lock method:
- **Focus:** same character identity from prior frame.
- **Radiance:** flat consistent lighting.
- **Angle:** fixed camera angle per direction.
- **Matter:** fixed facial traits, clothing, proportions.
- **Extras:** only pose/action changes.

Magic lock line:

`Maintain character identity from previous generation. Same face, same outfit, same proportions. Only [pose/action] changes.`

---

## 5) Required Asset Inventory (v3)

## 5.1 Characters (Gameplay)

### 5.1.1 Character Art Briefs (Required)

Use these briefs in every character prompt. Keep identity stable across idle/walk sheets.

#### Circe (Player)

- Role: exiled witch-goddess, central protagonist.
- Read: graceful, intelligent, emotionally heavy but not fragile.
- Silhouette: long dark hair, flowing dress shape, subtle jewelry accents.
- Outfit direction: deep violet/purple dress with warm gold details (Greek-inspired trim, small circlet or ornament).
- Palette anchors:
  - Dress: deep violet + shadow plum + muted highlight lavender.
  - Hair: dark brown/near-black with subtle warm highlights.
  - Skin: Mediterranean olive range.
  - Accents: muted gold, not neon yellow.
- Expression baseline: calm/melancholic focus.
- Direction notes:
  - Down: strongest facial read.
  - Up: maintain same hair mass and shoulder width.
  - Left/Right: dress flow and hair volume must remain consistent.

#### Hermes (NPC)

- Role: messenger god, witty guide, sarcastic but helpful.
- Read: youthful, quick, mischievous energy.
- Silhouette: short tousled light hair, light tunic/cloak, messenger-like trim.
- Outfit direction: pale sky-blue/cream garments with gold accents; optional small wing motifs on sandals.
- Palette anchors:
  - Clothing: sky-blue + cream + soft gold trim.
  - Hair: warm blond/gold.
  - Skin: fair-light.
- Expression baseline: alert/playful confidence.
- Direction notes:
  - Keep Hermes narrower/lighter than Circe in silhouette.
  - Avoid heavy armor or warrior reads.

#### Scylla (NPC - Monster Form)

- Role: tragic transformed figure, emotionally central to ending.
- Read: monstrous and dangerous, but clearly tragic rather than generic evil.
- Silhouette: broad distorted upper mass with multi-head suggestion; unstable asymmetry is acceptable.
- Form direction: sea-monster anatomy with human-remnant cues; simplify head count to readable grouped forms.
- Palette anchors:
  - Body: teal/sea-green + deep blue-gray shadows.
  - Accents: bruised purple or cold cyan highlights.
  - Eyes/mouth accents: restrained glow, avoid cartoon neon.
- Expression baseline: suffering/rage hybrid.
- Direction notes:
  - Maintain same monster mass across all directions.
  - Do not let side views collapse into a generic blob; preserve unique silhouette.

Generate these sheets:

- `assets/sprites/characters/circe/circe_idle.png` (`256x256`)
- `assets/sprites/characters/circe/circe_walk.png` (`256x256`)
- `assets/sprites/characters/hermes/hermes_idle.png` (`256x256`)
- `assets/sprites/characters/hermes/hermes_walk.png` (`256x256`)
- `assets/sprites/characters/scylla/scylla_idle.png` (`256x256`)
- `assets/sprites/characters/scylla/scylla_walk.png` (`256x256`)

Notes:
- These supersede low-res placeholders currently in `assets/sprites/characters/*.png`.
- Character descriptions above are mandatory, not optional flavor text.

## 5.2 Pig Set (New Gameplay Entity)

Required:

- `assets/sprites/characters/pig/pig_idle.png` (`256x128`, 2-direction rows only: Left, Right)
- `assets/sprites/characters/pig/pig_walk.png` (`256x256`, 4-direction)
- `assets/sprites/characters/pig/pig_run.png` (`256x256`, 4-direction)
- `assets/sprites/characters/pig/pig_eat.png` (`256x128`, 2-direction Left/Right)
- `assets/sprites/characters/pig/pig_sleep.png` (`256x128`, 2-direction Left/Right)

Pig visual brief:
- Read: cozy domesticated farm pig, stylized to match character world.
- Palette: warm pink/rose body tones with earthy shadow tones.
- Shape language: rounded, friendly, readable at gameplay scale.
- Behavior cues:
  - Walk: relaxed gait.
  - Run: urgent but still cute.
  - Eat: head-down nibble posture.
  - Sleep: curled or low-rest pose.
- Keep proportions and snout/ear shape identical across all pig sheets.

## 5.3 Interactables and Props

Replace or add:

- `assets/sprites/entities/boat.png` (high-detail remake, recommended `128x64`)
- `assets/sprites/entities/crafting_table.png` (high-detail remake, recommended `64x64`)
- `assets/sprites/entities/farm_plot.png` (high-detail remake, recommended `64x64`)
- `assets/sprites/entities/sleep_spot.png` (high-detail remake, recommended `64x64`)

Additional prop variants:

- `assets/sprites/entities/farm_plot_stage_empty.png`
- `assets/sprites/entities/farm_plot_stage_planted.png`
- `assets/sprites/entities/farm_plot_stage_1.png`
- `assets/sprites/entities/farm_plot_stage_2.png`
- `assets/sprites/entities/farm_plot_stage_ready.png`

## 5.4 Tilesets and Environment Pack (Core + Robust Decor)

Create:

- `assets/tilesets/aiaia_tileset_32.png`
- `assets/tilesets/scylla_cove_tileset_32.png`
- `assets/tilesets/greek_decor_tileset_32.png`

Minimum tile categories:
- Ground: grass variants, dirt, path transitions.
- Coast/water: shoreline edges, shallow/deep water tiles.
- Rock/cliff: dark coastal stone for Scylla zone.
- Greek architecture: white marble floor/walls, column bases/caps, broken ruins.
- Bronze decor: statue bases, full/partial statues, pedestals.
- Farm support: tilled soil variants, border tiles.

## 5.5 UI Visuals

Rebuild icons at higher quality:

- `assets/sprites/ui/icon_moly_seed.png` (recommended `32x32`)
- `assets/sprites/ui/icon_moly.png` (recommended `32x32`)
- `assets/sprites/ui/icon_calming_draught.png` (recommended `32x32`)

## 5.6 Opening Prologue Cutscene Images (Required)

Exactly one per prologue text screen:

- `assets/cutscenes/prologue/prologue_01.png` (`1080x1240`)
- `assets/cutscenes/prologue/prologue_02.png` (`1080x1240`)
- `assets/cutscenes/prologue/prologue_03.png` (`1080x1240`)
- `assets/cutscenes/prologue/prologue_04.png` (`1080x1240`)
- `assets/cutscenes/prologue/prologue_05.png` (`1080x1240`)
- `assets/cutscenes/prologue/prologue_06.png` (`1080x1240`)
- `assets/cutscenes/prologue/prologue_07.png` (`1080x1240`)

Suggested narrative mapping:
- 01: Circe on Aiaia, divine-but-isolated mood.
- 02: Pharmaka/herb craft visual language.
- 03: Circe, Glaucus, Scylla triangle setup.
- 04: Jealous poison in bathing pool.
- 05: Scylla transformation horror/tragedy.
- 06: Exile and guilt on Aiaia.
- 07: Final fragile hope to undo the past.

---

## 6) Copy-Paste Prompt Templates

## 6.1 Master Style Header (prepend to all prompts)

```
Style: high-quality pixel art, cozy farming sim readability, Greek mythology aesthetic.
Motifs: white marble architecture, bronze statuary, sacred island flora, coastal ruins.
No anti-aliasing. Crisp pixel edges. Consistent outline thickness.
Keep lighting consistent across all frames.
Match exact character proportions in every frame.
Align all frames on same baseline.
Same character identity in each frame.
Maintain character identity from previous generation. Same face, same outfit, same proportions. Only [pose/action] changes.
```

## 6.2 Character Action Sheet Prompt

```
Generate a pixel art spritesheet for [CHARACTER_NAME].
Character brief: [PASTE EXACT CHARACTER BRIEF FROM SECTION 5.1.1].
Canvas size: 256x256 PNG with transparency.
Frame size: 64x64.
Layout: 4 columns x 4 rows.
Rows (top to bottom): Down, Up, Left, Right.
Columns: 4-frame [ACTION_NAME] cycle.
Keep lighting consistent across all frames.
Match exact character proportions in every frame.
Align all frames on same baseline.
Same character identity in each frame.
No anti-aliasing.
Output filename: [character]_[action].png
```

## 6.3 Pig 2-Direction Sheet Prompt (idle/eat/sleep)

```
Generate a pixel art spritesheet for pig [ACTION_NAME].
Character brief: cozy farm pig, same identity/proportions as other pig sheets.
Canvas size: 256x128 PNG with transparency.
Frame size: 64x64.
Layout: 4 columns x 2 rows.
Rows: Left, Right.
Columns: 4-frame animation cycle.
Keep lighting/proportions consistent. Align baseline.
No anti-aliasing.
Output filename: pig_[action].png
```

## 6.4 Tileset Prompt

```
Generate a 32x32 tile atlas for [SET_NAME] with Greek-myth cozy farming style.
Include clean 32-grid alignment, no spacing bleed, no anti-aliasing.
Required categories: [LIST CATEGORIES].
Use coherent color language with warm highlights and readable contrast.
Output PNG with transparency where appropriate.
```

## 6.5 Prologue Image Prompt

```
Generate a painterly illustrative cutscene image.
Resolution: 1080x1240 PNG.
Mood: melancholic but hopeful, Greek mythology atmosphere, cohesive with cozy game tone.
Scene brief: [PROLOGUE_BEAT_DESCRIPTION].
Composition for portrait framing with clear focal subject.
Avoid modern objects/clothing.
Output filename: prologue_0X.png
```

## 6.6 Refinement / Fix Prompt

```
Previous generation had inconsistencies.
Regenerate with:
- exact same head/body proportions across frames
- exact same palette family
- exact same outline thickness
- baseline alignment maintained
- same character identity preserved
Only [specified action/pose] should change.
```

---

## 7) QA Checklist (Full)

- Correct filename and output folder.
- Correct canvas dimensions.
- Correct frame dimensions and row/column layout.
- Transparent background where required.
- No anti-aliasing blur.
- Consistent identity across frames (face/outfit/proportions).
- Direction rows correctly ordered (Down, Up, Left, Right).
- Baseline alignment maintained.
- Greek myth motifs present where relevant.
- Cutscene images exactly `1080x1240`.
- Style coherence with `game/Concept Art`.

Godot import checks:
- Gameplay pixel sprites: set nearest filtering in import settings.
- Tilesets: verify 32-grid slicing and no bleeding.
- Cutscene images: verify portrait fit and safe framing.

---

## 8) Strict Naming Policy

- No random suffixes.
- No model names in filenames.
- No spaces in generated asset filenames.
- Use lowercase snake_case only.
- If a file must be revised, overwrite same deterministic name.

---

## 9) Notes for Integration Agent

- Current v3 uses low-res placeholders; these assets are intended replacements/upgrades.
- Keep this file as the generation source-of-truth for visual asset production.
- If new actions are added later, preserve the same sizing/layout contracts.
