# Learning Note: PNG vs JPG vs WebP for Godot Assets

## Why This Came Up

During asset planning for `circes_garden_v3`, we needed to pick file formats for:
- gameplay sprites/tiles/UI
- prologue cutscene images

In Godot, format choice affects:
- transparency support
- visual quality
- file size
- edit/iteration workflow

## Option A: Gameplay PNG + Cutscene PNG

### What it means
- Everything uses PNG.

### Pros
- Supports transparency (critical for sprites, tiles overlays, UI icons).
- Lossless quality (good for pixel art edges and text clarity).
- Stable and predictable in Godot pipelines.
- Easy to re-edit repeatedly without quality decay.

### Cons
- Larger files than JPG/WebP in many cases.

### Best for
- Projects where quality and clean iteration matter more than smallest size.

---

## Option B: Gameplay PNG + Cutscene JPG

### What it means
- Sprites/UI stay PNG.
- Prologue images use JPG.

### Pros
- Smaller file size for large painted cutscene images.
- Faster transfer/storage in some cases.

### Cons
- JPG is lossy (compression artifacts, especially around edges/text).
- No alpha transparency.
- Re-exporting multiple times can compound quality loss.

### Best for
- Photo-like backgrounds where slight compression is acceptable.

---

## Option C: Gameplay WebP + Cutscene PNG

### What it means
- Gameplay assets use WebP.
- Cutscene images stay PNG.

### Pros
- WebP can reduce file size while keeping good visual quality.
- Can support alpha (depending on export settings and pipeline use).

### Cons
- More pipeline complexity for AI generation + cleanup tools.
- Easier to accidentally introduce inconsistent compression settings.
- Less straightforward than PNG for pixel-perfect iteration.

### Best for
- Teams intentionally optimizing package size with a controlled pipeline.

## Practical Recommendation for Circe's Garden v3

Use **Gameplay PNG + Cutscene PNG** for now.

Why:
- You are still iterating quickly.
- You need clean pixel edges for gameplay assets.
- You want minimal technical friction while generating many assets with AI.

After asset lock, you can selectively convert some large cutscene PNGs if APK size needs optimization.

## Quick Rule of Thumb

- If it needs transparency or crisp pixel edges: **PNG**
- If it's a big painted image and size is critical: **consider JPG/WebP later**
- If you are still iterating heavily: **prefer PNG everywhere first**
