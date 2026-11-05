# Learning Note: Prologue Image Options in Godot

## Why This Came Up

While planning the new asset generation document for `circes_garden_v3`, we needed to decide how prologue cutscene images should be organized for Godot.

Your game already has a 7-screen prologue flow in `game/scenes/prologue.gd` (text advances screen by screen).  
The question was: how should image files map to those 7 screens?

## The Three Options

### Option 1: One Image Per Screen (Recommended)

Example files:
- `prologue_01.png`
- `prologue_02.png`
- ...
- `prologue_07.png`

How it works in Godot:
- Screen 1 text shows with `prologue_01`
- Screen 2 text shows with `prologue_02`
- etc.

Pros:
- Easiest to implement and debug
- Easiest to replace one bad image without touching others
- Clean for non-technical iteration with AI-generated art

Cons:
- No built-in alternates unless you create extra files manually

---

### Option 2: Variants Per Screen

Example files:
- `prologue_01_a.png`, `prologue_01_b.png`
- ...

How it works in Godot:
- You choose one variant in code or switch based on conditions.

Pros:
- Creative flexibility
- Backup versions for each beat

Cons:
- More file management overhead
- More decision complexity when integrating

---

### Option 3: One Big Storyboard Strip

Example:
- One large image containing all 7 panels, cropped in code.

How it works in Godot:
- Code manually selects sub-regions (rectangles) for each prologue step.

Pros:
- Single file

Cons:
- Hardest to maintain
- One panel change requires re-exporting the full strip
- More fragile implementation for simple narrative cutscenes

## Why Option 1 Fits This Project Best

For `circes_garden_v3`:
- The prologue is already linear and screen-based.
- You want to generate many assets quickly and swap them often.
- You are optimizing for clarity and reliability before export.

So Option 1 gives the best balance of:
- simplicity
- maintainability
- fast iteration

## Extra Context for Future You

- We also locked prologue image output to match game aspect/runtime: `1080x1240`.
- This keeps cutscene framing aligned with the portrait viewport and Retroid target.
- Concept art in `game/Concept Art` is style reference, not final sizing authority.

## Practical Godot Tip

When unsure, choose the most explicit file-to-screen mapping first (Option 1).  
You can always add variants later without rewriting the whole cutscene system.
