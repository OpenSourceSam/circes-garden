# Craft scorecard

For recruiters and hiring managers who want to know whether this was thought through or generated and
pushed. Each line names what to look at. Scores are self-assessed on 2026-10-26, out of 5, and the gaps are
listed too. Nothing scores 5: each row says what the last point would take or what is still missing.

| Area | Score | Evidence |
|---|---|---|
| Scope control | 4 | One island, one cove, five quests, 20 minutes. `CLAUDE.md` rule 1 ("30 min demo, not a full game") was held for eight months of on-and-off work. The last point would need a release that a stranger finished without help. |
| Architecture | 4 | Three autoloads (`game/autoload/`), one world scene, entities as small scripts. Story text and the map are data (`game/data/story_text.gd`, `game/data/world_map.gd`), generated from source files, never hand-edited. |
| Testing | 4 | Nine headless unit and checkpoint tests (`tests/run_all.gd`), run in CI on every push. A closed-loop browser playthrough (`tools/pixelart/playtest.py`) plays the whole quest chain against the exported build and waits on the game's own console lines before each step; it runs on the build machine, not in CI. Every change was gated on it. |
| Art pipeline | 4 | Open LPC assets composed and recoloured by code (`tools/pixelart/lpc_compose.py`, `lpc_tiles.py`), code-drawn pieces where no asset exists, a sheet checker (`check_sheets.py`), map previews, and a generated credits file (`docs/CREDITS.md`). The February image-model attempt is documented honestly in `docs/MAKING-OF.md`. |
| Writing | 4 | Every line was rewritten for voice and fidelity to Miller's *Circe*; Hermes is funny on purpose; the ending is the book's. See `game/data/story_text.gd`. |
| Build and release | 4 | One command (`tools/build_web.sh`) imports, tests, exports and screenshots. Web export tuned for GitHub Pages (threads off); Windows export; a debug-signed Android APK, not yet tried on a device (`PLATFORMS.md`). |
| Documentation | 4 | `README.md` (play, controls, how it was built), `PLATFORMS.md`, `docs/MAKING-OF.md`, `CLAUDE.md` (the spec the code was written against), this file. |
| Human-AI collaboration | 4 | The human chose the book, the ending, the scope, the art direction and the acceptance bar, reviewed screenshots and dialogue samples, and approved each phase. The AI wrote code, tools, text drafts and ran the verification loop. The division is recorded in `docs/MAKING-OF.md`. |
| Polish | 3 | Readable maps, consistent characters, a title subtitle, a herb lesson with real herb pictures. Still missing: sound design with known sources, touch controls, a settings screen. |

## Gaps I know about

- Audio tracks have no recorded source yet; they are placeholders until that is settled.
- No touch controls, so phones can only watch.
- Collision is tile-based; walking around the house and the pier is fine, but not pixel-tight.
- Scylla is the one character still drawn by code rather than from an open asset, because no six-headed
  monster exists in the LPC packs.

## How to check the claims in ten minutes

1. Open `docs/index.html` through a local web server, or the GitHub Pages link, and play to the credits.
2. Read `tools/pixelart/playtest.py` and then `build/screens/` after running `tools/build_web.sh --script full`.
3. Compare the February sprites (commit `0a4a36a`, `assets/image_pipeline/generated/raw/`) with the current ones.
4. Read `game/data/story_text.gd` and look for the two Hermes jokes.
