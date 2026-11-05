"""Compose characters from the Universal LPC Spritesheet Character Generator layers.

Input: the generator repository unpacked under build/lpc_downloads/ulpc/ (not in git).
Output: 256x256 game sheets (4 frames x rows Down, Up, Left, Right; 64x64 frames) for
idle and walk, written where the game loads them, plus 4x previews.

LPC layer sheets: walk.png is 9 columns x 4 rows (rows: up, left, down, right; column 0
is the standing pose, columns 1-8 the cycle). idle.png is 2 columns x 4 rows.
Colours: palette recolouring per the generator's PALETTE_RECOLOR_GUIDE.md (exact colour
replacement with a tolerance of 1 per channel).

Usage:
    python tools/pixelart/lpc_compose.py [--preview-only]
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from px import preview, save  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
ULPC = REPO / "build/lpc_downloads/ulpc/Universal-LPC-Spritesheet-Character-Generator-master"
SS = ULPC / "spritesheets"
PAL = ULPC / "palette_definitions"
RAW = REPO / "assets/image_pipeline/generated/raw/sprites/characters"
PREVIEW = Path(__file__).parent / "preview"

LPC_ROWS = {"up": 0, "left": 1, "down": 2, "right": 3}
GAME_ROWS = ["down", "up", "left", "right"]
WALK_COLS = [1, 3, 5, 7]
CELL = 64


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


_palette_cache: dict[str, dict] = {}


def load_palette(material: str) -> dict[str, list[tuple[int, int, int]]]:
    if material not in _palette_cache:
        data = json.loads((PAL / material / f"{material}_ulpc.json").read_text(encoding="utf-8"))
        _palette_cache[material] = {k: [hex_to_rgb(c) for c in v] for k, v in data.items()}
    return _palette_cache[material]


def detect_source(arr: np.ndarray, palette: dict) -> str:
    """The palette variant whose colours cover the most opaque pixels is the source."""
    rgb = arr[..., :3][arr[..., 3] > 0]
    best, best_n = None, -1
    for name, colors in palette.items():
        n = 0
        for c in colors:
            n += int(np.all(np.abs(rgb.astype(int) - np.array(c)) <= 1, axis=1).sum())
        if n > best_n:
            best, best_n = name, n
    return best


def recolor(img: Image.Image, material: str, variant: str) -> Image.Image:
    palette = load_palette(material)
    if variant not in palette:
        raise KeyError(f"{material} palette has no variant {variant!r}; options: {list(palette)[:12]}")
    arr = np.array(img.convert("RGBA"))
    src = detect_source(arr, palette)
    out = arr.copy()
    for c_from, c_to in zip(palette[src], palette[variant]):
        mask = np.all(np.abs(arr[..., :3].astype(int) - np.array(c_from)) <= 1, axis=2) & (arr[..., 3] > 0)
        out[mask, :3] = c_to
    return Image.fromarray(out, "RGBA")


def find_layer(rel_dir: str, anim: str, color: str | None) -> Path:
    base = SS / rel_dir
    candidates = []
    if color:
        candidates += [base / anim / f"{color}.png", base / color / f"{anim}.png"]
    candidates += [base / f"{anim}.png", base / anim / "base.png"]
    for c in candidates:
        if c.exists():
            return c
    tried = "\n  ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"no layer for {rel_dir} {anim} {color}:\n  {tried}")


@dataclass
class Layer:
    rel_dir: str
    z: int
    color: str | None = None          # explicit colour file name (e.g. dress/slit colours)
    recolor: tuple[str, str] | None = None  # (material, variant) palette recolour
    optional: bool = False


@dataclass
class Character:
    name: str
    layers: list[Layer] = field(default_factory=list)
    mood: dict = field(default_factory=dict)


def compose(char: Character, anim: str) -> Image.Image:
    layers = sorted(char.layers, key=lambda l: l.z)
    canvas = None
    for layer in layers:
        try:
            path = find_layer(layer.rel_dir, anim, layer.color)
        except FileNotFoundError:
            if layer.optional:
                continue
            raise
        img = Image.open(path).convert("RGBA")
        if layer.recolor:
            img = recolor(img, *layer.recolor)
        if canvas is None:
            canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
        if img.size != canvas.size:
            # Some layers are taller (big hats); crop or pad to the body sheet size.
            fixed = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            fixed.alpha_composite(img.crop((0, 0, canvas.width, canvas.height)))
            img = fixed
        canvas.alpha_composite(img)
    return canvas


def frame(sheet: Image.Image, col: int, row: int) -> Image.Image:
    return sheet.crop((col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL))


def mirror_check(img: Image.Image) -> None:
    pass


def tone(img: Image.Image, saturation: float = 1.0, contrast: float = 1.0, warmth: int = 0) -> Image.Image:
    """Mood pass: scale saturation and contrast, shift warmth, keep alpha binary."""
    from PIL import ImageEnhance
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    arr = np.array(rgb).astype(int)
    arr[..., 0] = np.clip(arr[..., 0] + warmth, 0, 255)
    arr[..., 2] = np.clip(arr[..., 2] - warmth, 0, 255)
    out = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    out.putalpha(img.getchannel("A").point(lambda a: 255 if a > 96 else 0))
    return out


def game_sheets(char: Character) -> dict[str, Image.Image]:
    """Walk from LPC walk columns 1,3,5,7; idle from the standing pose (column 0) with a
    one-pixel breath on frame 3, so every layer only needs a walk sheet."""
    walk = compose(char, "walk")
    out = {}
    sheet_w = Image.new("RGBA", (4 * CELL, 4 * CELL), (0, 0, 0, 0))
    sheet_i = Image.new("RGBA", (4 * CELL, 4 * CELL), (0, 0, 0, 0))
    for r, direction in enumerate(GAME_ROWS):
        lr = LPC_ROWS[direction]
        for c, col in enumerate(WALK_COLS):
            sheet_w.alpha_composite(frame(walk, col, lr), (c * CELL, r * CELL))
        stand = frame(walk, 0, lr)
        breath = Image.new("RGBA", stand.size, (0, 0, 0, 0))
        breath.alpha_composite(stand.crop((0, 1, CELL, CELL)), (0, 0))      # body up 1 px
        breath.alpha_composite(stand.crop((0, 52, CELL, CELL)), (0, 52))    # feet stay put
        for c, img in enumerate((stand, stand, breath, stand)):
            sheet_i.alpha_composite(img, (c * CELL, r * CELL))
    for name, sheet in (("walk", sheet_w), ("idle", sheet_i)):
        out[name] = tone(sheet, **char.mood) if char.mood else sheet
    return out


MOOD = {"saturation": 0.92, "contrast": 1.06, "warmth": 4}

CIRCE = Character("circe", [
    Layer("cape/solid/bg", 5, recolor=("cloth", "navy")),
    Layer("body/bodies/female", 10, recolor=("body", "olive")),
    Layer("feet/sandals/thin", 15, recolor=("cloth", "leather")),
    Layer("dress/slit/female", 30, color="white"),
    Layer("cape/solid/fg", 85, recolor=("cloth", "navy")),
    Layer("head/heads/human/female", 100, recolor=("body", "olive")),
    Layer("eyes/human/adult/default", 110, color="yellow", optional=True),
    Layer("hair/long/adult", 120, recolor=("hair", "dark_brown")),
], MOOD)

HERMES = Character("hermes", [
    Layer("cape/solid/bg", 5, recolor=("cloth", "sky")),
    Layer("body/bodies/male", 10, recolor=("body", "amber")),
    Layer("feet/sandals/male", 15, recolor=("cloth", "walnut")),
    Layer("legs/skirts/plain/male", 25, color="white", optional=True),
    Layer("torso/clothes/sleeveless/sleeveless/male", 35, color="white"),
    Layer("cape/solid/fg", 85, recolor=("cloth", "sky")),
    Layer("hat/accessory/wings/bg/adult", 95, recolor=("cloth", "white"), optional=True),
    Layer("head/heads/human/male", 100, recolor=("body", "amber")),
    Layer("eyes/human/adult/default", 110, color="blue", optional=True),
    Layer("hair/parted/adult", 120, recolor=("hair", "blonde")),
    Layer("hat/accessory/wings/fg/adult", 145, recolor=("cloth", "white"), optional=True),
], MOOD)


# --- Pig from "LPC style farm animals" (Daniel Eddeland, CC-BY 3.0 / GPL 2.0) ----------
PIG_WALK = REPO / "build/lpc_downloads/pig_walk.png"
PIG_EAT = REPO / "build/lpc_downloads/pig_eat.png"
PIG_LPC_ROWS = {"up": 0, "left": 1, "down": 2, "right": 3}


def pig_frame(sheet: Image.Image, col: int, row: int, cell: int = 128) -> Image.Image:
    """Crop a 128-px LPC animal cell to a 64x64 game frame, feet on row 58."""
    big = sheet.crop((col * cell, row * cell, (col + 1) * cell, (row + 1) * cell))
    bb = big.getbbox()
    out = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if bb is None:
        return out
    sprite = big.crop(bb)
    x = (CELL - sprite.width) // 2
    y = 58 - sprite.height + 1
    out.alpha_composite(sprite, (max(0, x), max(0, y)))
    return out


def pig_sheets() -> dict[str, Image.Image]:
    walk = Image.open(PIG_WALK).convert("RGBA")
    eat = Image.open(PIG_EAT).convert("RGBA")
    cols = walk.width // 128
    out = {}
    for action in ("walk", "run"):
        sheet = Image.new("RGBA", (4 * CELL, 4 * CELL), (0, 0, 0, 0))
        for r, direction in enumerate(GAME_ROWS):
            for c in range(4):
                sheet.alpha_composite(pig_frame(walk, c % cols, PIG_LPC_ROWS[direction]), (c * CELL, r * CELL))
        out[action] = sheet
    for action, src, frames in (("idle", walk, [0, 0, 0, 0]), ("eat", eat, [0, 1, 2, 3]), ("sleep", eat, [3, 3, 3, 3])):
        sheet = Image.new("RGBA", (4 * CELL, 2 * CELL), (0, 0, 0, 0))
        for r, direction in enumerate(("left", "right")):
            for c, col in enumerate(frames):
                fr = pig_frame(src, col % cols, PIG_LPC_ROWS[direction])
                if action == "idle" and c == 2:
                    fr = fr.transform(fr.size, Image.Transform.AFFINE, (1, 0, 0, 0, 1, 1))  # 1-px breath
                if action == "sleep" and c != 3:
                    zx = 44 if direction == "left" else 14
                    zy = 26 - c * 3
                    for dx, dy in ((0, 0), (1, 0), (2, 0), (2, 1), (1, 2), (0, 3), (1, 3), (2, 3)):
                        fr.putpixel((zx + dx, zy + dy), (255, 255, 255, 255))
                sheet.alpha_composite(fr, (c * CELL, r * CELL))
        out[action] = sheet
    return {k: tone(v, **MOOD) for k, v in out.items()}


def build(preview_only: bool) -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for anim, img in pig_sheets().items():
        save(preview(img, 4, grid=64), PREVIEW / f"lpc_pig_{anim}_x4.png")
        if not preview_only:
            save(img, RAW / "pig" / f"pig_{anim}.png")
    print("pig: 5 sheets", "previewed" if preview_only else "written")
    for char in (CIRCE, HERMES):
        sheets = game_sheets(char)
        for anim, img in sheets.items():
            assert img.size == (256, 256), img.size
            save(preview(img, 4, grid=64), PREVIEW / f"lpc_{char.name}_{anim}_x4.png")
            if not preview_only:
                save(img, RAW / char.name / f"{char.name}_{anim}.png")
        print(f"{char.name}: idle and walk sheets {'previewed' if preview_only else 'written'}")


if __name__ == "__main__":
    build("--preview-only" in sys.argv)
