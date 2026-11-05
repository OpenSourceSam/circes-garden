# Image Generation Pipeline (February 2026, archived)

The February 2026 image-model pipeline, kept as a record of what was tried. The game's current art is
built by `tools/pixelart/` instead; `docs/MAKING-OF.md` explains why. Only the seven prologue paintings
in `generated/raw/cutscenes/prologue/` still come from this pipeline.

## Quick Start

```bash
# 0. Split composites (if Kimi gave you stacked idle+walk images)
python assets/image_pipeline/tools/split_composites.py

# 1. Normalize oversized Kimi outputs to exact spec sizes
python assets/image_pipeline/tools/normalize_assets.py

# 2. Validate dimensions
python assets/image_pipeline/tools/preflight.py --root normalized

# 3. Generate row-direction QA contact sheets
python assets/image_pipeline/tools/row_direction_qa.py --root normalized

# 4. Review contact sheets in qa/row_qa/

# 5. When satisfied, overwrite originals
python assets/image_pipeline/tools/normalize_assets.py --in-place
```

## Folder Map

```
image_pipeline/
  README.md              <- You are here

  docs/
    ASSET_SPEC.md         Master spec: dimensions, character briefs, prompt templates
    WORKFLOW.md           Step-by-step operator guide
    REGEN_BRIEF.md        Known issues + regen handoff for Kimi K
    IMPERFECTIONS.md      Non-blocking issue tracker
    WIRING_PLAN.md        Integration plan (assets -> game)

  learnings/
    image_tool_reliability.md   Policy: use Pillow, not AI, for metadata
    file_formats.md             PNG vs JPG vs WebP decision
    prologue_options.md         Why "one image per screen"

  tools/
    normalize_assets.py    Resize oversized outputs to exact spec
    preflight.py           Strict dimension validation
    row_direction_qa.py    Visual QA contact sheets
    split_composites.py    Split idle+walk composites

  reference/
    concept_art/           Style reference images (kept locally, not published)
    LORE_SOURCES.md        Canon hierarchy for character accuracy

  generated/
    composites/            Drop Kimi composite images here
    raw/                   Drop individual Kimi outputs here
    normalized/            Pipeline output (exact spec sizes)
    reports/               Preflight JSON reports

  qa/
    row_qa/                Labeled row contact sheets for direction QA
    audit_screenshots/     Historical validation captures
```

## Pending Re-generations [2026-02-12]

| Asset | Issue | JSON Fix Needed? |
|-------|-------|-----------------|
| `pig_eat.png` | Pigs pushed to bottom of cells, not centered on alignment guides | Yes — `pig_eat.json` says "ONLY draw in TOP 2 ROWS" which confuses Kimi. Remove that constraint and use standard 2-row grid instructions instead. |
| `pig_sleep.png` | Pigs straddle cell boundaries, content in all 4 rows | Yes — `pig_sleep.json` has same "TOP 2 ROWS" language. Same fix needed. |

**Current state:** pig_eat and pig_sleep still use Phase 3.1 placeholders in `generated/raw/`. All other character sprites have real Kimi art wired in.

## Key Documents

| What you need | Where to look |
|---------------|---------------|
| Asset dimensions and grid specs | [docs/ASSET_SPEC.md](docs/ASSET_SPEC.md) |
| How to run the pipeline | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| What's broken in current assets | [docs/REGEN_BRIEF.md](docs/REGEN_BRIEF.md) |
| Character/story lore for accuracy | [reference/LORE_SOURCES.md](reference/LORE_SOURCES.md) |
