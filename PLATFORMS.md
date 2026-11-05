# Where Circe's Garden can run, and what each target needs

Written 2026-10-25 and updated 2026-10-26 (Godot 4.5.1; Web, Windows and Android presets in `export_presets.cfg`).

## 1. Browser build on GitHub Pages (ready now)

What exists: `docs/index.html` plus the `.wasm`, `.pck` and `.js` files, exported with threads off so GitHub Pages
can serve it without special headers. About 60 MB download; Pages compresses the wasm on the fly.

Publishing steps:
1. Make the repository public (GitHub Pages on a free account needs that) or create a public copy.
2. Repository settings, Pages, source "Deploy from a branch", branch `main`, folder `/docs`.
3. Wait up to ten minutes; the site appears at `https://<account>.github.io/<repository>/`.

Limits: keyboard only, so phones cannot play it; Safari is weaker with WebGL 2 than Chrome and Firefox;
audio starts after the first click.

Rebuild: `tools/build_web.sh --out docs` then commit `docs/`.

## 2. Windows download (ready now, untested on a real desktop)

`build/windows/CircesGarden.exe` is a single file with the game data embedded. Zip it and attach it to a GitHub
Release (`gh release create v0.1.0 build/CircesGarden-windows-x86_64.zip`). Windows SmartScreen warns because the
file is not signed; the README tells players what to click. Rebuild with
`Godot_v4.5.1-stable_win64.exe --headless --path . --export-release "Windows Desktop" build/windows/CircesGarden.exe`.

## 3. Android, sideloaded on the Retroid Pocket Classic (the original target)

Status 2026-10-26: a debug-signed arm64 APK builds headlessly with the Android preset in `export_presets.cfg`
(`build/android/CircesGarden.apk`, about 48 MB). It has not yet been installed on the device.

The Retroid Pocket Classic is an Android 14 handheld with a portrait 1240x1080 screen and a D-pad. It runs
emulators, but this game is not a Game Boy ROM: Godot cannot produce one. The right path is a native Android
app (APK) installed over USB or from a file manager, which the Retroid runs like any Android game.

What is already done for it: the project is portrait (1080x1240 viewport), and the controller's A, B and
d-pad buttons are bound at runtime in `game/autoload/game_state.gd` (the input map in `project.godot` lists
keyboard keys only). The Android SDK, a Java runtime and a debug keystore are set up on the build machine, and
the "Android" preset in `export_presets.cfg` (package `com.samcloutier.circesgarden`, version 0.1.0, arm64,
"Use Gradle Build" off) exports with
`--headless --path . --export-debug "Android" build/android/CircesGarden.apk`.

What is still needed, in order:
1. Copy the APK to the Retroid (USB cable, or a cloud drive) and open it with the file manager; allow
   "install unknown apps" once.
2. Test with the D-pad: movement, talking, the herb lesson (left/right and A), menus, the boat, the ending.
   Font sizes and the dialogue box should be checked on the 3.92-inch screen; they were sized for a desktop window.
3. Optional later: touch controls (an on-screen D-pad and A button) so the same APK works on phones.

## 4. What "finished" would add after that

- A short settings screen (volume, controller test) and a pause menu.
- Save and continue (the game is short, so this is optional).
- Replace the placeholder music and effects with tracks whose source is recorded.
- Hand-polish the generated sprites where it matters most: Circe's walk cycle and Scylla's idle.
