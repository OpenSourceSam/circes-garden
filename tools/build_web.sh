#!/usr/bin/env bash
# Headless: placement check, import, (optionally) tests, export the Web preset, then screenshot it in a
# headless browser.
# Usage: tools/build_web.sh [--no-test] [--out build/web] [--script default]
set -u
# Godot 4.5.1 binary: set GODOT_BIN, or have `godot` on PATH; the last line is the author's local install.
GODOT="${GODOT_BIN:-$(command -v godot || true)}"
[ -n "$GODOT" ] || GODOT="/c/Users/$USER/Documents/heras-garden/Godot_v4.5.1-stable_win64.exe"
[ -x "$GODOT" ] || { echo "Godot binary not found; set GODOT_BIN"; exit 1; }
cd "$(dirname "$0")/.."
RUN_TESTS=1; OUT=build/web; SCRIPT=default; EXTRA=""
while [ $# -gt 0 ]; do case "$1" in
  --no-test) RUN_TESTS=0;; --out) OUT="$2"; shift;; --script) SCRIPT="$2"; shift;; --frames) EXTRA="--frames-dir $2"; shift;; esac; shift; done
mkdir -p build/logs "$OUT"; touch build/.gdignore
# Placement check: stop if two objects stand on the same ground, a shadow lies across something, or a
# picture is cut by its box. It rebuilds the atlases from the LPC packs, so it runs where those are.
if [ -d build/lpc_downloads ]; then
  python tools/pixelart/check_placement.py > build/logs/placement.txt 2>&1 || { echo "placement check failed:"; cat build/logs/placement.txt; exit 1; }
  echo "placement check: $(tail -1 build/logs/placement.txt | cut -d';' -f1)"
fi
"$GODOT" --headless --path . --import > build/logs/import.txt 2>&1; echo "import exit $?"
if [ $RUN_TESTS = 1 ]; then "$GODOT" --headless --path . --script tests/run_all.gd > build/logs/tests.txt 2>&1; echo "tests exit $? : $(grep RESULTS build/logs/tests.txt)"; fi
"$GODOT" --headless --path . --export-release "Web" "$OUT/index.html" > build/logs/export_web.txt 2>&1; rc=$?
echo "export exit $rc"; grep -iE "Template file not found|No export template|failed|Invalid export" build/logs/export_web.txt | head -5
ls -la "$OUT" | grep -E "index\.(pck|wasm)"
python tools/pixelart/playtest.py --build "$OUT" --out build/screens --script "$SCRIPT" $EXTRA 2>&1 | grep -vE "^127\.0\.0\.1"
