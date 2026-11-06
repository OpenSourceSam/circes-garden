"""Write docs/CREDITS.md for the open art used in the game.

Pulls the exact author/licence rows from the Universal LPC Spritesheet Character Generator's
CREDITS.csv for the layers lpc_compose.py uses, and copies each OpenGameArt pack's own
credits file. Run after changing the character layers or adding a pack.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lpc_compose  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DL = REPO / "build/lpc_downloads"
ULPC = lpc_compose.ULPC
OUT = REPO / "docs/CREDITS.md"

PACKS = [
    ("[LPC] Terrains", "https://opengameart.org/content/lpc-terrains", "CC-BY-SA 3.0 / CC-BY-SA 4.0",
     DL / "x/lpc-terrains/CREDITS-terrain.txt", "ground tiles: grass, sand, sea, dirt, cobblestone, stone, gravel"),
    ("[LPC] Trees", "https://opengameart.org/content/lpc-trees", "CC-BY-SA 3.0",
     DL / "x/lpc-trees/CREDITS-trees.txt", "olive-like and round trees, shrubs"),
    ("[LPC] Conifers", "https://opengameart.org/content/lpc-conifers", "CC-BY-SA 3.0 / GPL 2.0 / GPL 3.0",
     DL / "x/lpc-conifers/CREDITS-conifers.txt", "cypress-like trees"),
    ("[LPC] Rocks", "https://opengameart.org/content/lpc-rocks", "CC-BY-SA 3.0 / CC-BY-SA 4.0",
     DL / "x/rocks/CREDITS-rocks.txt", "rocks, boulders, the dolmen and spires in the cove"),
    ("LPC compatible Ancient Greek Architecture", "https://opengameart.org/content/lpc-compatible-ancient-greek-architecture",
     "CC-BY-SA 3.0 / GPL 3.0 / OGA-BY 3.0", None,
     "columns, the tiled roofs, stone walls, door, marble floor, mosaics, altar, bench, amphorae; "
     "by TheraHedwig (Wolthera van Hovell tot Westerflier)"),
    ("LPC style farm animals", "https://opengameart.org/content/lpc-style-farm-animals", "CC-BY 3.0 / GPL 2.0",
     None, "the pig; by Daniel Eddeland (daneeklu)"),
]


def used_layer_dirs() -> list[str]:
    dirs = []
    for char in (lpc_compose.CIRCE, lpc_compose.HERMES):
        for layer in char.layers:
            dirs.append(layer.rel_dir)
    return sorted(set(dirs))


def main() -> int:
    rows = list(csv.DictReader((ULPC / "CREDITS.csv").open(encoding="utf-8")))
    dirs = used_layer_dirs()
    lines = ["# Art credits", "",
             "Circe's Garden uses open pixel art from the Liberated Pixel Cup (LPC) community, composed and",
             "recoloured by scripts in `tools/pixelart/`. The art keeps its own licences (listed below); the",
             "game code is separate. Every author below must be credited when this art is redistributed.", "",
             "## Characters (Universal LPC Spritesheet Character Generator)", "",
             "Generator: https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator",
             "(per-file credits from its CREDITS.csv). Layers used: " + ", ".join(dirs) + ".", ""]
    seen = set()
    for row in rows:
        fn = row["filename"]
        if not any(fn.startswith(d.rstrip("/") + "/") or fn == d for d in dirs):
            continue
        key = (row["authors"], row["licenses"], row["urls"])
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- `{fn.rsplit('/', 1)[0]}`: {row['authors']} — {row['licenses']} — {row['urls']}")
    lines += ["", "## Tiles and props (OpenGameArt packs)", ""]
    for name, url, lic, credits_file, what in PACKS:
        lines += [f"### {name}", f"- Used for: {what}.", f"- Licence: {lic}.", f"- Page: {url}", ""]
        if credits_file and credits_file.exists():
            text = credits_file.read_text(encoding="utf-8", errors="replace").strip()
            lines += ["```", text, "```", ""]
    lines += ["## Fonts", "",
              "- EB Garamond, by The EB Garamond Project Authors (Octavio Pardo, after Georg Duffner) — SIL Open",
              "  Font License 1.1 — https://github.com/octaviopardo/EBGaramond12 (licence: `assets/fonts/EBGaramond-OFL.txt`)",
              "- Cinzel, by The Cinzel Project Authors (Natanael Gama) — SIL Open Font License 1.1 —",
              "  https://github.com/NDISCOVER/Cinzel (licence: `assets/fonts/Cinzel-OFL.txt`)", ""]
    lines += ["## Everything else", "",
              "Scylla, the cliff, whirlpool and mist of her strait, the farm beds, icons, herb cards, butterflies,",
              "fences, the well, the crafting table and the boat are drawn by code in `tools/pixelart/` for this game.",
              "The seven prologue paintings were made",
              "in February 2026 with an image model for this project. Story and characters after Madeline",
              "Miller's novel *Circe*; this is a fan project.", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(seen)} character layer credit lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
