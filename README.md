# Circe's Garden

<p align="center">
  <img src="showcase/prologue_01.png" alt="Circe stands among ancient Greek ruins overlooking the sea at sunset" width="400">
</p>

<p align="center">
  <em>A narrative farming game based on Madeline Miller's <strong>Circe</strong>, built as a solo project using AI-assisted development.</em>
</p>

<p align="center">
  <strong>Godot 4.5</strong> &nbsp;|&nbsp; <strong>GDScript</strong> &nbsp;|&nbsp; <strong>Android Handheld</strong> &nbsp;|&nbsp; <strong>~30 min playtime</strong>
</p>

---

## The Game

Circe, the witch-goddess, lives in exile on the island of Aiaia. She cannot undo her greatest mistake: transforming Scylla into a monster out of jealousy. She tries anyway. The potion fails. She finds peace.

**Core loop:** Farm herbs &rarr; Craft potion &rarr; Sail to Scylla &rarr; Potion fails &rarr; Acceptance

<p align="center">
  <img src="showcase/prologue_03.png" alt="Circe, Glaucus, and Scylla" width="200">
  &nbsp;&nbsp;
  <img src="showcase/circe_idle.png" alt="Circe sprite sheet" width="140">
  &nbsp;&nbsp;
  <img src="showcase/boat.png" alt="Greek boat sprite" width="140">
  &nbsp;&nbsp;
  <img src="showcase/aiaia_tileset_32.png" alt="Aiaia tileset" width="200">
</p>

<p align="center"><em>Cutscene painting &bull; Character sprite sheet &bull; World asset &bull; Island tileset &mdash; all AI-generated via a structured pipeline</em></p>

---

## What I Learned

Building this game was a crash course in working with AI at scale. These lessons transfer directly to anyone building with AI agents, managing AI-assisted workflows, or compounding their growth in any field.

- **Discipline is the bottleneck, not capability.** AI agents are competent enough to make you lazy. Without rigorous review of every output, errors compound silently &mdash; one wrong assumption propagates through code, tests, and docs until the rot is everywhere.
- **Compound engineering: never make the same mistake twice.** Every failure gets root-caused, the system gets patched, and the fix gets documented. AI makes capture and analysis cheap enough to actually sustain this. Progress compounds exponentially instead of linearly.
- **Route tasks to the cheapest capable model.** Not every job needs the frontier model. Breaking work into subtasks and assigning each to the right level of capability saved thousands while improving output quality.
- **Benchmarks don't tell the real story.** Leaderboard rankings didn't predict which tool would produce consistent pixel art at scale. Evaluate models on your actual workload, not someone else's test suite.
- **The work shifts from producing to directing.** AI-assisted work inverts the traditional rhythm: intense preparation and spec writing, then monitoring and course-correction. More film director than assembly line.
- **AI eliminates friction; you still do the reflection.** The compound effect comes from the process around the tools &mdash; spec documents, QA checklists, post-mortems &mdash; not the tools themselves.

---

## How It Was Built &mdash; AI-Assisted Development

This project is a case study in **using AI tools to build something complete as a solo non-technical creator**. Every aspect &mdash; game architecture, visual assets, testing, deployment planning &mdash; was produced through deliberate AI collaboration.

### The Development Pipeline

| Layer | Tool | What It Did |
|-------|------|-------------|
| Game code & architecture | Claude Code (Anthropic) | Wrote all GDScript, designed systems, ran tests |
| Visual asset generation | Custom pipeline via Gemini API | Produced all sprites, tilesets, and cutscene paintings |
| Prompt engineering | Structured spec docs + JSON schemas | Ensured consistency across 40+ generated assets |
| Project management | AI agents + structured docs | Phase-based development with clear milestones |

### Building an Image Generation Pipeline

The biggest challenge wasn't writing code &mdash; it was **getting consistent, high-quality visual assets at scale from AI image generation.**

I created [`ASSET_GENERATION_V3.md`](game/ASSET_GENERATION_V3.md) as a comprehensive spec document that served as the single source of truth for all visual asset production. It includes:

- **Character briefs** with exact palette anchors, proportions, and direction rules
- **A Consistency Lock Protocol** (the FRAME method) to maintain character identity across frames:
  - **F**ocus: same character identity from prior frame
  - **R**adiance: flat consistent lighting
  - **A**ngle: fixed camera angle per direction
  - **M**atter: fixed facial traits, clothing, proportions
  - **E**xtras: only pose/action changes
- **Copy-paste prompt templates** for each asset type (characters, tilesets, cutscenes)
- **A QA checklist** for validating every generated asset

This approach produced **33 required asset files** across characters, props, tilesets, UI icons, and full-screen cutscene paintings &mdash; all with consistent style and identity.

**What failed first:** Early single-shot prompts produced wildly inconsistent sprites &mdash; Circe would have brown hair in one frame and black in another, or her outfit would change between directions. Treating image generation like a single API call doesn't work when you need identity consistency across a 4x4 sprite grid.

**What worked:** Treating prompts like QA specification documents. Each character prompt locked an exact hex palette, silhouette description, and the FRAME consistency method. Every sprite sheet required 3-5 regeneration passes before acceptance. Cutscene illustrations were more forgiving at 1-2 passes each. Total across the project: roughly 120-150 generation calls to produce the 33 final assets that shipped.

**How FRAME was born:** After generating a full Circe sprite sheet where the south-facing frame had brown hair and the east-facing frame had a completely different outfit, I needed a systematic fix. FRAME started as a checklist taped to a failed generation and evolved into the standard header prepended to every prompt. Each letter solved a specific failure mode: identity drift (Focus), random shadow artifacts (Radiance), perspective shifts (Angle), feature mutation (Matter), and unsolicited "improvements" (Extras). The key insight: consistency in AI image generation is a specification problem, not a model quality problem.

### Transferable Skills: Beyond Game Dev

The same structured approach to AI asset generation applies directly to other domains:

The core principle: **don't prompt for outputs, prompt for systems that produce outputs.** A spec doc beats a clever prompt every time.

The same pipeline &mdash; spec doc, structured prompts, consistency protocol, QA checklist &mdash; applies to:

- **Sales enablement:** Personalized pitch decks, one-pagers, and competitive battle cards with locked brand identity across every asset
- **Marketing campaigns:** Consistent ad creative at scale using the same spec-driven approach that kept 33 game assets visually unified
- **Product documentation:** Onboarding materials, feature walkthroughs, and help articles that follow a single style guide
- **Client-facing content:** Any domain where you need volume, speed, and brand consistency from AI generation tools

The meta-skill is directing AI the way a creative director manages a design team: set the standards, write the brief, review against the spec &mdash; not line-by-line production.

---

## Project Details

**Quest structure:** 6 quests spanning prologue, herb farming, potion crafting, a voyage to confront Scylla, and an acceptance ending. Book-accurate &mdash; the potion fails.

**Architecture:** Three global singletons (game state, scene transitions, audio), test-first development with headless unit tests and visual QA screenshots, dependency injection for testability.

**Target device:** [Retroid Pocket Classic](https://www.goretroid.com/) &mdash; a 3.92" portrait AMOLED handheld (Android 14, D-pad input). All UI and world design is portrait-first at 1080x1240.

**Status:** ~75% complete. Core gameplay loop functional, all quests playable. Final polish and Android export remaining.

---

## Built With

- **[Godot 4.5](https://godotengine.org/)** &mdash; Open-source game engine
- **[Claude Code](https://claude.ai/)** (Anthropic) &mdash; AI coding assistant
- **Gemini API** (Google) &mdash; AI image generation for visual assets
- **[Madeline Miller's *Circe*](https://madelinemiller.com/circe/)** &mdash; Source material and narrative foundation

---

<p align="center">
  <em>Made with pharmaka and persistence.</em>
</p>
