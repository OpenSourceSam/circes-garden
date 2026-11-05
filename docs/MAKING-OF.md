# How Circe's Garden was made, and what was hard

Written 2026-10-25 by Sam Cloutier with Claude. This is the honest log of a one-person, AI-assisted game,
kept so that someone else can repeat the parts that worked and skip the parts that did not.

## The short version

- The game logic (quests, farming, crafting, dialogue, tests) was written with Claude Code in February 2026
  against a spec-first `CLAUDE.md` and a phased plan. That part went fast and worked.
- The art did not. Getting sprite sheets that an engine can slice (exact frame grid, consistent directions,
  transparent background, stable character design) was the single hardest problem of the project.
- What finally worked: open pixel-art assets composed by code, plus code-drawn pieces where no asset existed,
  all checked by scripts and by an automated browser playthrough that screenshots the real game.

## Timeline

1. **February 2026, image-model sprite sheets (failed).** Prompts asked Kimi K2.5 for 256x256 sheets with a
   4x4 grid of 64-px frames. The images came back at 1024 px or larger, frames drifted across the grid,
   left and right rows were swapped or duplicated, characters changed between frames, and backgrounds were
   not transparent. A pipeline of normalisers and QA scripts (`assets/image_pipeline/`) shrank and checked
   them, but shrinking a painting does not make pixel art, and a frame that spills into its neighbour cannot
   be fixed after the fact. The sheets loaded, and the game looked broken.
2. **2026-10-25 morning, code-drawn pixel art (worked, but plain).** Every sprite, prop and tile was generated
   by Python with Pillow: parametric characters, right rows mirrored from left rows so directions could never
   be wrong, and a checker for sizes, alpha, baselines and cell bounds. It fixed every structural problem at
   once and ran in seconds. The result was clean and readable, and it looked like what it was: programmer art.
3. **2026-10-25 afternoon, the world as data.** The island and the cove became text maps resolved by a script
   into tile coordinates, props and collision rectangles. Changing the map became a text edit followed by a
   preview render, with no editor work.
4. **2026-10-25 evening, open assets composed by code (worked).** Characters were built from the Universal LPC
   Spritesheet Character Generator layers (body, head, eyes, hair, dress or tunic, sandals, cloak, winged cap),
   recoloured with its palette files, and converted to this game's sheet format. Terrain came from the LPC
   terrain, trees, conifers, rocks and Ancient Greek architecture packs, with an autotiler for the LPC edge
   sets. Scylla, who has no open asset, stayed code-drawn at a larger frame size. The dialogue was rewritten in
   the same pass. Credits for every author are in `docs/CREDITS.md`.

## Why sprite sheets are hard for image models, and when they still make sense

- A sprite sheet is not a picture; it is a table. Each cell must contain one pose, aligned to the same
  baseline, with the same character, and nothing crossing the cell border. Image models optimise the look of
  the whole image, not the geometry of a grid. Every model tested kept drifting on exactly those constraints.
- Low resolution makes it worse. A 64-px character is about 40 px tall. Models draw at 1024 px and higher;
  shrinking by 16x turns clean lines into mush, and pixel-art "style" at high resolution is not pixel art.
- Newer models with tighter prompt control may close the gap for single images (one turnaround, one portrait).
  For animation frames the practical route today is still: generate or pick a design once, then let code
  produce the frames (mirroring, offsets, palette swaps), and verify every cell with a script.
- Open assets are on-brand for this kind of game. The LPC packs were made for exactly this grid, so the
  problem becomes composition and recolouring, which code is good at.

## The verification loop

- `tools/pixelart/check_sheets.py`: sizes, binary alpha, every frame inside its cell, steady baseline.
- `tools/pixelart/worldmap.py`: renders a 1x preview of each map so a human can look before building.
- `tools/pixelart/playtest.py`: serves the exported web build, drives it in headless Chromium, and waits on
  console lines the game prints (`[Dialogue] start hermes_intro`, `[GameState] Planted moly`, player
  positions) so every step is confirmed, not assumed. It plays the whole quest chain and saves 21 screenshots.
- `tools/build_web.sh`: import, unit and checkpoint tests, Web export, playtest, in one command.

## What I would tell someone starting this

1. Decide the sprite format first (frame size, rows, columns, baseline) and write the checker before any art.
2. Do not ask an image model for a grid. Ask it for one design, or use open assets, and generate the grid in code.
3. Put the map in data and render previews; the editor is slow for iteration when an agent does the work.
4. Make the game print its state. A test that reads those lines beats a test that presses keys and hopes.
5. Keep an automated playthrough. It caught every regression in this project within minutes.
