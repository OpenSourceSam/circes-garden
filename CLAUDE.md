# Circe's Garden v3 - Claude Instructions

**Project:** Narrative farming game (~20 min) | **Engine:** Godot 4.5 | **For:** Portfolio demo

**Target Platform:** Retroid Pocket Classic (Android handheld, 1240×1080 portrait, D-pad input)

**See [PLATFORMS.md](PLATFORMS.md) for the browser, Windows and Android builds.**

---

## The Game

Circe, exiled to Aiaia, learns she cannot undo her greatest mistake - transforming Scylla into a monster. She tries anyway. The potion fails. She finds peace.

**Core loop:** Farm herbs → Craft potion → Sail to Scylla → Potion fails → Acceptance

---

## Story (5 Quests)

| Quest | What Happens | Flag |
|-------|--------------|------|
| 0 | Prologue: Flashback (Scylla transformation), arrive on Aiaia | `prologue_complete` |
| 1 | Meet Hermes, learn pharmaka, herb minigame | `quest_1_complete` |
| 2 | Farm moly (the cure herb) | `quest_2_complete` |
| 3 | Craft Calming Draught | `quest_3_complete` |
| 4 | Sail to Scylla, potion fails | `quest_4_complete` |
| 5 | Epilogue: Return, acceptance | `game_complete` |

---

## Map Design

**Single map (`world.tscn`) with 2 zones:**

```
AIAIA GARDEN          |    SCYLLA'S COVE
(warm, sunny)         |    (dark, rocky)
                      |
  house  farm         |      monster
  Hermes              |      (Scylla)
                      |
  ~~~~ boat ~~~~      |
```

Travel = fade out → teleport → fade in (same map, different coordinates)

The map is data: text maps in `tools/pixelart/worldmap.py` become `game/data/world_map.gd`
(ground tiles, props, collision rectangles). `world.gd` only reads that file. Edit the text
maps and rerun the script; never edit `world_map.gd` by hand. [2026-10-25]

---

## Project Structure

```
circes_garden_v3/
├── project.godot
├── CLAUDE.md
├── game/
│   ├── autoload/           # GameState, SceneManager, AudioController
│   ├── scenes/             # main_menu, world, herb_minigame
│   ├── entities/
│   │   ├── player/         # player.tscn
│   │   ├── npcs/           # hermes, scylla
│   │   └── interactables/  # boat, farm_plot, crafting_table, sleep_spot
│   ├── ui/                 # dialogue_box, inventory_display, quest_display
│   ├── resources/          # dialogue_data
│   └── util/               # texture_loader, sprite_sheet
├── tests/
│   ├── run_all.gd          # Headless test runner
│   ├── unit/               # Logic tests
│   ├── checkpoints/        # Quest milestone tests
│   └── visual/             # Screenshot + playthrough tests
└── assets/
    ├── audio/
    ├── sprites/
    └── tiles/
```

---

## Core Systems (3 Autoloads Only)

1. **GameState** - Inventory, quest flags, farm plots
2. **SceneManager** - Transitions with fade
3. **AudioController** - Music + SFX

---

## GDScript Patterns

```gdscript
# Type hints always
@export var speed: float = 200.0
@onready var sprite: Sprite2D = $Sprite2D

# Signals for decoupling
signal dialogue_ended(dialogue_id: String)

# Cache node refs
@onready var player: CharacterBody2D = $Player  # GOOD
# $Player in _process()  # BAD
```

---

## Characters

- **Circe** - Player, guilty, seeking redemption
- **Hermes** - Trickster, teacher, sarcastic
- **Scylla** - Monster, cannot speak, only screams

---

## Key Rules

1. **Keep it simple** - 30 min demo, not a full game
2. **No addons** - Vanilla Godot only (add back if truly needed)
3. **Test often** - `Godot*.exe --headless --script tests/run_all.gd`
4. **Book-accurate ending** - Potion fails, Scylla lives as monster
5. **Subagents** - Always use sonnet (never haiku). Log the model in your message when launching each agent so there's a visible record.
6. **NEVER import from v2** - The v2 project (`v2_heras_garden`, `OlD heras garden`) is contaminated. Do not copy code, assets, docs, or patterns from it. Everything in v3 is built from scratch.
7. **Image metadata checks** - For dimensions/alpha/frame-grid validation, use local scripted inspection (Pillow/CLI), not model-based image recognition.

---

## Lore Sources [2026-02-10]

- Primary canon: the novel itself (copyrighted; not in the repo)
- Secondary detailed reference: https://circe.fandom.com/wiki/Circe_Wiki
- Project lore usage guide: `assets/image_pipeline/reference/LORE_SOURCES.md`

When lore conflicts exist, use the novel text as source-of-truth.

---

## Art Pipeline [2026-10-25]

Sprites, props and tiles are composed by code in `tools/pixelart/` from Liberated Pixel Cup assets, or drawn
in code (Scylla, icons, farm plots). The seven prologue paintings are the one exception: they were made with
an image model in February 2026 and are kept as they are. Pipeline:
- `build_all.py` writes every sheet, prop, icon and tileset to `assets/image_pipeline/generated/raw/`
  (same file names the scripts load) and 4x previews to `tools/pixelart/preview/`.
- `check_sheets.py` verifies exact sizes, binary alpha, frames inside cells, steady baseline, left/right mirrors.
- `playtest.py` drives the exported web build in headless Chromium and screenshots it; `tools/build_web.sh` runs
  import, tests, export and playtest in one go.
- Sheet spec stays as in `assets/image_pipeline/docs/ASSET_SPEC.md` (64x64 frames, 4 columns, rows Down/Up/Left/Right).
- The February 2026 Kimi-generated art is in git history (commit `0a4a36a`); a local gitignored copy sits in
  `assets/image_pipeline/generated/kimi_2026-02/`.

---

## Platform: Android Handheld [2026-02-05]

**Target:** Retroid Pocket Classic (3.92" portrait AMOLED, D-pad input, Android 14)

**Strategy:** Full portrait conversion (1080x1240 viewport, vertical world layout)
Done:
- Portrait conversion (Phase 3.2, commit 09e3ff6)
- World uses vertical layout: Aiaia (top) → Boat → Scylla (bottom)
- Controller A, B and d-pad are bound at runtime in `game/autoload/game_state.gd`
  (the project input map lists keyboard keys only) [2026-10-26]
- Camera zoom 2x, visible area 540x620 world units
- Export as APK, sideload via USB

**See [PLATFORMS.md](PLATFORMS.md), section 3, for the Android export**

**Development:** Keep building on desktop, test final APK on device before polish phase

---

## Document Hygiene Rules

**Problem:** Stale docs cause compounding errors when AI agents pick up outdated approaches.

### Single Source of Truth (SSOT)

| Document | Purpose | Lifespan |
|----------|---------|----------|
| `CLAUDE.md` | Project truth, always current | Permanent |
| `STATE.md` | Current work state (GSD) | Session |
| `PROJECT.md` | Milestone roadmap (GSD) | Per-milestone |
| `PLAN.md` | Phase execution plan | Per-phase |

### Hygiene Rules

1. **No orphan docs** - Every `.md` must be referenced from CLAUDE.md or deleted
2. **Delete after use** - Temp files (PLAN.md, research notes) deleted when phase completes
3. **Update, don't append** - Fix outdated sections instead of adding "UPDATE:" notes
4. **Timestamp changes** - Major CLAUDE.md changes get date comment: `[2026-02-05]`
5. **One approach** - If approach changes, DELETE old approach text entirely

### What Lives Where

```
CLAUDE.md (this file)
├── Project overview
├── Story / quests
├── Technical patterns
├── Key rules
└── Testing approach

STATE.md (GSD creates)
├── Current phase
├── What's blocked
└── Next actions

PLAN.md (GSD creates, then DELETES)
├── Phase tasks
├── Acceptance criteria
└── Implementation steps
```

### Red Flags (Stop & Clean)

- Multiple `.md` files describing same system
- "See also" links to files that don't exist
- Comments like "OLD:" or "DEPRECATED:" still in docs
- Plan files from completed phases still present

---

## Testing [2026-02-05]

**Goal:** Verify state changes actually happened, not just "code ran without error"

### Test Levels

| Level | What | When | How |
|-------|------|------|-----|
| **Logic** | State changes work | After any system code | Headless |
| **Integration** | Systems interact | After connecting systems | Headless |
| **Checkpoint** | Game milestones | After quest/feature done | Headless |
| **Visual** | Scenes render correctly | After UI/scene changes | Headed (screenshots) |

### Test Pattern (Important)

Tests use `RefCounted` with dependency injection — NOT autoload globals. Autoload names like `GameState` are not available in scripts loaded via `load().new()`.

```gdscript
# tests/unit/test_inventory.gd
extends RefCounted

var gs: Node

func run(game_state: Node) -> bool:
    gs = game_state
    gs.new_game()

    gs.add_item("moly", 3)
    if gs.get_item_count("moly") != 3:
        push_error("Should have 3 moly")
        return false

    print("  └─ Inventory works")
    return true
```

The runner instantiates GameState and passes it in:

```gdscript
# In run_all.gd
var game_state = load("res://game/autoload/game_state.gd").new()
var test = load("res://tests/unit/test_inventory.gd").new()
var passed: bool = test.run(game_state)
```

### Visual Screenshot Test

Captures screenshots of each game scene for verification. Runs headed (not headless).

**How it works:**
1. Launches as a `.tscn` scene (so autoloads like SceneManager are available)
2. Reparents itself to `/root` to survive SceneManager scene changes
3. Loads each scene via `SceneManager.change_scene()`
4. Waits for `transition_finished` signal + 30 render frames
5. Captures viewport to PNG in `tests/visual/screenshots/`

**Run:**
```bash
Godot*.exe --path . res://tests/visual/test_screenshot.tscn
```

**Output:** PNG screenshots in `tests/visual/screenshots/` (gitignored)

**To add new scenes:** Edit `_scenes_to_test` array in `test_screenshot.gd`

### Running Tests

```bash
# All headless tests (unit + checkpoint)
Godot*.exe --headless --script tests/run_all.gd

# Visual screenshot test (headed, opens window)
Godot*.exe --path . res://tests/visual/test_screenshot.tscn
```

### Test File Structure

```
tests/
├── run_all.gd              # Runner: instantiates GameState, runs all tests
├── unit/                   # Logic tests (RefCounted, headless)
│   ├── test_inventory.gd
│   ├── test_flags.gd
│   └── test_farming.gd
├── checkpoints/            # Quest milestone tests (RefCounted, headless)
│   ├── test_quest_0_prologue.gd
│   ├── test_quest_1_pharmaka.gd
│   ├── test_quest_2_farming.gd
│   ├── test_quest_3_crafting.gd
│   ├── test_quest_4_scylla.gd
│   └── test_quest_5_epilogue.gd
└── visual/                 # Headed tests (screenshot capture)
    ├── test_screenshot.tscn    # Launch this scene
    ├── test_screenshot.gd      # Screenshot logic
    └── screenshots/            # Output PNGs (gitignored)
```

### Test-First Rule

Before marking any feature complete:
1. Write checkpoint test that would pass if feature works
2. Run test (should fail)
3. Implement feature
4. Run test (should pass)
5. THEN mark complete
