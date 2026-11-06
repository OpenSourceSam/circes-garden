"""Headless browser playtest of the exported web build.

Serves a web export folder over HTTP, opens it in headless Chromium (software
WebGL), drives the game with keyboard steps and saves screenshots so a person
or an agent can look at how the game renders. The game prints its state
changes (GameState flags, minigame rounds) to the browser console, and the
script waits on those lines, so the run is a closed loop rather than blind
key presses.

Usage:
    python tools/pixelart/playtest.py [--build build/web] [--out build/screens]
                                      [--script default|full] [--scale 0.75]
                                      [--frames-dir build/frames]

Exit code 1 when the page logs a loader error, a failed resource, or a
step does not reach its goal.
"""
from __future__ import annotations

import argparse
import functools
import re
import http.server
import socketserver
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BAD_CONSOLE = ("No loader found", "Failed to load resource", "Uncaught", "ERROR:")

# Step tuples: (action, value, wait_seconds, screenshot_label_or_None)
#   key <name>            press once, then wait
#   hold <name>           hold for `wait` seconds
#   walk <key cond>       hold a key until the player reports a position meeting cond, e.g. 'ArrowDown y>=600'
#   enter <n>             press Enter n times, 0.5 s apart (advance dialogue), then wait
#   wait                  just wait
#   wait_for <substring>  wait until a console line contains it (wait = timeout)
#   interact <substring>  press E; if no console line with substring appears, nudge and retry
#   minigame              press Enter on the focused answer until "[Minigame] complete"
SCRIPTS = {
    "default": [
        ("wait", 0, 2.0, "00_menu"),
        ("key", "Enter", 1.5, None),
        ("wait", 0, 1.0, "01_prologue"),
        ("enter", 7, 2.5, None),
        ("wait", 0, 1.0, "02_world_spawn"),
        ("walk", "ArrowUp y<=282", 8.0, None),
        ("interact", "start hermes_intro", 15.0, "03_hermes_talk"),
        ("enter", 12, 1.0, "04_minigame"),  # hermes_intro has 12 lines
        ("wait_for", "[Minigame] round", 15.0, "04b_herb_lesson"),
        ("wait", 0, 2.0, "04c_herb_lesson"),
        ("minigame", "", 150.0, "05_minigame_done"),
        ("hold", "ArrowDown", 3.6, "06_farm"),
        ("hold", "ArrowLeft", 1.0, None),
        ("hold", "ArrowRight", 1.0, "07_walk_right"),
        ("hold", "ArrowDown", 2.0, "08_sleep_spot"),
    ],
    # Short clip for the README GIF: run with --frames-dir and --scale 0.5. Walks here are timed
    # holds, not closed-loop, because screenshots slow the game down.
    "gif": [
        ("wait", 0, 1.5, "g00_menu"),
        ("key", "Enter", 1.5, None),
        ("wait", 0, 2.0, "g01_prologue"),
        ("enter", 1, 2.0, None),
        ("enter", 6, 2.5, None),
        ("wait", 0, 1.0, "g02_world"),
        ("walk", "ArrowUp y<=282", 12.0, None),
        ("interact", "start hermes_intro", 15.0, "g03_hermes"),
        ("enter", 3, 1.0, None),
        ("enter", 3, 1.5, "g04_minigame"),
        ("minigame", "", 150.0, None),
        ("wait_for", "quest_2_active = true", 20.0, None),
        ("walk", "ArrowDown y>=600", 15.0, None),
        ("walk", "ArrowLeft x<=196", 10.0, None),
        ("interact", "Planted moly", 6.0, "g05_plant"),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowLeft x<=134", 10.0, None),
        ("interact", "Planted moly", 6.0, None),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowRight x>=368", 10.0, None),
        ("interact", "Planted moly", 6.0, None),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowLeft x<=272", 10.0, None),
        ("walk", "ArrowDown y>=800", 10.0, None),
        ("interact", "start sleep_day_1", 6.0, "g06_sleep"),
        ("enter", 3, 1.0, None),
        ("walk", "ArrowDown y>=1000", 10.0, "g07_beach"),
    ],
    "full": [
        ("wait", 0, 2.0, "00_menu"),
        ("key", "Enter", 1.5, None),
        ("wait", 0, 1.0, "01_prologue"),
        ("enter", 7, 2.5, None),
        ("wait", 0, 1.0, "02_world_spawn"),
        ("walk", "ArrowUp y<=282", 8.0, None),
        ("interact", "start hermes_intro", 15.0, "03_hermes_talk"),
        ("enter", 6, 1.0, "04_minigame"),
        ("minigame", "", 150.0, None),
        ("wait_for", "quest_2_active = true", 20.0, "05_seeds_given"),
        ("walk", "ArrowDown y>=600", 12.0, None),
        ("walk", "ArrowLeft x<=196", 8.0, None),
        ("interact", "Planted moly", 6.0, "06_plant_middle"),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowLeft x<=134", 8.0, None),
        ("interact", "Planted moly", 6.0, None),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowRight x>=368", 8.0, None),
        ("interact", "Planted moly", 6.0, "07_plant_right"),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowLeft x<=272", 8.0, None),
        ("walk", "ArrowDown y>=800", 8.0, "08_sleep_spot"),
        ("interact", "start sleep_day_1", 6.0, None),
        ("enter", 3, 0.5, None),
        ("wait_for", "Day 2", 4.0, None),
        ("interact", "start sleep_day_2", 6.0, None),
        ("enter", 4, 0.5, None),
        ("wait_for", "Day 3", 4.0, None),
        ("interact", "start sleep_day_3", 6.0, None),
        ("enter", 3, 0.5, None),
        ("wait_for", "Day 4", 4.0, "09_day_4"),
        ("walk", "ArrowUp y<=600", 8.0, "10_crops_ready"),
        ("walk", "ArrowLeft x<=196", 8.0, None),
        ("interact", "Harvested moly", 6.0, None),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowLeft x<=134", 8.0, None),
        ("interact", "Harvested moly", 6.0, None),
        ("enter", 2, 0.5, None),
        ("walk", "ArrowRight x>=368", 8.0, None),
        ("interact", "Harvested moly", 6.0, "11_harvest"),
        ("enter", 2, 0.5, None),
        ("wait_for", "quest_3_active = true", 4.0, None),
        ("walk", "ArrowLeft x<=272", 8.0, None),
        ("walk", "ArrowUp y<=400", 8.0, None),
        ("interact", "can_sail_to_scylla = true", 6.0, "12_craft"),
        ("enter", 4, 0.5, None),
        ("walk", "ArrowDown y>=1100", 40.0, "13_boat"),
        ("interact", "teleported player to (272.0, 2800.0)", 20.0, None),
        ("wait", 0, 1.5, "14_cove_arrival"),
        # North from the pier to the point of rock that faces Scylla across the strait.
        ("walk", "ArrowUp y<=2510", 30.0, "15_scylla"),
        ("interact", "potion_failed = true", 15.0, "16_potion_fails"),
        ("enter_until", "[Scylla] cue descend", 20.0, None),
        ("wait", 0, 1.8, "16b_heads_down"),
        ("enter_until", "[Scylla] cue strike", 40.0, None),
        ("wait", 0, 0.3, "16c_strike_rear"),
        ("wait", 0, 0.3, "16d_strike_hit"),
        ("enter", 6, 0.5, "17_after_scylla"),
        ("walk", "ArrowDown y>=2880", 30.0, None),
        ("interact", "teleported player to (270.0, 500.0)", 20.0, None),
        ("wait", 0, 1.5, "18_back_home"),
        ("enter", 2, 0.3, None),
        ("walk", "ArrowUp y<=282", 20.0, None),
        ("interact", "start hermes_epilogue", 15.0, "19_epilogue"),
        ("enter", 24, 0.6, None),  # 11 lines; the first press of each only finishes the typing
        ("wait_for", "game_complete = true", 10.0, None),
        ("wait", 0, 6.0, "20_credits"),  # the credits fade in; the headless browser runs slowly
    ],
}


def serve(folder: Path, port: int) -> socketserver.TCPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(folder))
    handler.log_message = lambda *a, **k: None  # type: ignore[attr-defined]
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


class Runner:
    def __init__(self, page, out: Path, frames_dir: Path | None = None, frame_every: float = 0.4):
        self.page, self.out = page, out
        self.console: list[str] = []
        self.bad: list[str] = []
        self.failures: list[str] = []
        self.frames_dir = frames_dir
        self.frame_every = frame_every
        self._last_frame = 0.0
        self._frame_n = 0

    def shoot(self, name: str) -> None:
        self.page.screenshot(path=str(self.out / f"{name}.png"))
        print("  shot", name)

    def tick(self) -> None:
        """Save a GIF frame if enough wall time passed. Runs on the driver thread (Playwright is not thread-safe)."""
        if not self.frames_dir:
            return
        now = time.time()
        if now - self._last_frame < self.frame_every:
            return
        self._last_frame = now
        try:
            self.page.screenshot(path=str(self.frames_dir / f"f{self._frame_n:05d}.png"), timeout=5000)
            self._frame_n += 1
        except Exception:
            pass

    def pause(self, seconds: float) -> None:
        """Wait while letting Playwright deliver console events (time.sleep would not)."""
        end = time.time() + seconds
        while True:
            self.tick()
            left = end - time.time()
            if left <= 0:
                return
            self.page.wait_for_timeout(min(100, int(left * 1000)) or 1)

    def seen_since(self, idx: int, needles: str) -> bool:
        parts = [n for n in needles.split("|") if n]
        if not parts:
            return True
        return any(any(n in line for n in parts) for line in self.console[idx:])

    def wait_for(self, needles: str, timeout: float) -> bool:
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.seen_since(0, needles):
                return True
            self.pause(0.2)
        return False

    def hold(self, key: str, seconds: float) -> None:
        self.page.keyboard.down(key)
        self.pause(seconds)
        self.page.keyboard.up(key)
        self.pause(0.25)

    _POS_RE = re.compile(r"\[Player\] at (-?\d+),(-?\d+)")

    def player_pos(self):
        # Godot can batch several print() lines into one console message; take the last match.
        for line in reversed(self.console):
            found = self._POS_RE.findall(line)
            if found:
                x, y = found[-1]
                return int(x), int(y)
        return None

    def walk(self, spec: str, timeout: float) -> bool:
        """spec: '<key> <axis><op><value>' e.g. 'ArrowDown y>=600'. Holds the key until the game
        reports a player position that satisfies the condition (closed loop, immune to stalls)."""
        key, cond = spec.split(" ", 1)
        axis = cond[0]
        op = ">=" if ">=" in cond else "<="
        target = int(cond.split(op)[1])
        # Console latency means we learn the position ~20 px late; stop a little early.
        margin = 24
        goal = target - margin if op == ">=" else target + margin
        # Headless Chromium renders in software, several times slower than a real browser, so a
        # fixed time limit fails on slow runs. The walk keeps going while the player keeps moving;
        # `timeout` is the allowance without progress, with an overall cap of four times it.
        start = time.time()
        deadline = start + timeout
        cap = start + timeout * 4
        last_pos = self.player_pos()
        ok = False
        self.page.keyboard.down(key)
        try:
            while time.time() < min(deadline, cap):
                self.page.wait_for_timeout(50)
                self.tick()  # GIF frames; the closed loop below tolerates the stall
                pos = self.player_pos()
                if pos is not None:
                    if pos != last_pos:
                        last_pos = pos
                        deadline = time.time() + min(timeout, 4.0)
                    v = pos[0] if axis == "x" else pos[1]
                    if (op == ">=" and v >= goal) or (op == "<=" and v <= goal):
                        ok = True
                        break
        finally:
            self.page.keyboard.up(key)
        self.pause(0.3)
        if not ok:
            print(f"  note: walk {spec!r} timed out at {self.player_pos()}")
        return True  # soft: the next interact step decides

    def interact(self, needles: str, timeout: float) -> bool:
        """Press E; if the expected console line does not show, nudge around and retry."""
        nudges = [("ArrowUp", 0.3), ("ArrowLeft", 0.3), ("ArrowDown", 0.6), ("ArrowRight", 0.6),
                  ("ArrowUp", 0.6), ("ArrowLeft", 0.3), ("ArrowDown", 0.3), ("ArrowRight", 0.3)]
        start = len(self.console)
        deadline = time.time() + timeout
        n = 0
        while True:
            self.page.keyboard.press("KeyE")
            # Software rendering is slow: poll for up to 2.5 s before nudging.
            for _ in range(25):
                self.pause(0.1)
                if self.seen_since(start, needles):
                    self.pause(0.4)
                    return True
            if time.time() > deadline:
                return False
            key, secs = nudges[n % len(nudges)]
            n += 1
            self.hold(key, secs)

    def dialogue_open(self) -> bool:
        """True when the last [Dialogue] start line has no end line after it."""
        last_start = last_end = -1
        for i, line in enumerate(self.console):
            if "[Dialogue] start" in line:
                last_start = i
            elif "[Dialogue] end" in line:
                last_end = i
        return last_start > last_end

    def press_through(self, n: int) -> None:
        """With a dialogue open: press Enter until it ends (typewriter lines take two presses),
        at most 3n times. Otherwise (prologue screens, menus): press exactly n times."""
        if not self.dialogue_open():
            for _ in range(n):
                self.page.keyboard.press("Enter")
                self.pause(0.5)
            return
        for _ in range(max(1, 3 * n)):
            self.page.keyboard.press("Enter")
            self.pause(0.45)
            if not self.dialogue_open():
                return

    def enter_until(self, needles: str, timeout: float) -> bool:
        """Inside a dialogue: press Enter, one press at a time, until a console line shows."""
        start = len(self.console)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.seen_since(start, needles):
                return True
            self.page.keyboard.press("Enter")
            self.pause(0.5)
        return self.seen_since(start, needles)

    def minigame(self, timeout: float) -> bool:
        start = len(self.console)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.seen_since(start, "[Minigame] complete"):
                return True
            self.page.keyboard.press("Enter")
            self.pause(1.5)
        return self.seen_since(start, "[Minigame] complete")

    def run(self, steps) -> None:
        for action, value, wait, label in steps:
            ok = True
            if action == "key":
                self.page.keyboard.press(value)
                self.pause(wait)
            elif action == "hold":
                self.hold(value, float(wait))
            elif action == "walk":
                ok = self.walk(value, float(wait))
            elif action == "enter":
                self.press_through(int(value))
                self.pause(wait)
            elif action == "enter_until":
                ok = self.enter_until(value, float(wait))
            elif action == "wait":
                self.pause(wait)
            elif action == "wait_for":
                ok = self.wait_for(value, float(wait))
            elif action == "interact":
                ok = self.interact(value, float(wait))
            elif action == "minigame":
                ok = self.minigame(float(wait))
            if not ok:
                msg = f"step {action} {value!r} did not reach its goal"
                print("  FAIL:", msg)
                self.failures.append(msg)
                if label:
                    self.shoot(label + "_FAILED")
                continue
            if label:
                self.shoot(label)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default="build/web")
    ap.add_argument("--out", default="build/screens")
    ap.add_argument("--script", default="default")
    ap.add_argument("--scale", type=float, default=0.75)
    ap.add_argument("--port", type=int, default=8060)
    ap.add_argument("--boot-wait", type=float, default=25.0)
    ap.add_argument("--frames-dir", default=None, help="also save a frame about every 0.4 s here (for a GIF)")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    build = (REPO / args.build).resolve()
    out = (REPO / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    frames_dir = (REPO / args.frames_dir).resolve() if args.frames_dir else None
    if frames_dir:
        frames_dir.mkdir(parents=True, exist_ok=True)
        for old in frames_dir.glob("*.png"):
            old.unlink()
    if not (build / "index.html").exists():
        print(f"no index.html in {build}")
        return 2

    httpd = serve(build, args.port)
    width, height = int(1080 * args.scale), int(1240 * args.scale)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                  "--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"],
        )
        page = browser.new_page(viewport={"width": width, "height": height})
        runner = Runner(page, out, frames_dir)

        def on_console(msg):
            text = f"[{msg.type}] {msg.text}"
            runner.console.append(text)
            if any(b in msg.text for b in BAD_CONSOLE):
                runner.bad.append(text)

        page.on("console", on_console)
        page.on("pageerror", lambda e: runner.bad.append(f"[pageerror] {e}"))
        page.on("requestfailed", lambda r: runner.bad.append(f"[requestfailed] {r.url}"))
        page.on("response", lambda r: runner.bad.append(f"[http {r.status}] {r.url}") if r.status >= 400 else None)

        page.goto(f"http://127.0.0.1:{args.port}/index.html")
        t0 = time.time()
        while time.time() - t0 < args.boot_wait:
            try:
                hidden = page.evaluate(
                    "(() => { const s = document.getElementById('status'); "
                    "return !s || s.style.visibility === 'hidden' || s.style.display === 'none'; })()")
            except Exception:
                hidden = False
            if hidden and time.time() - t0 > 4:
                break
            time.sleep(0.5)
        print(f"boot wait {time.time() - t0:.1f}s")
        page.mouse.click(width // 2, height // 2)
        time.sleep(1.0)

        runner.run(SCRIPTS[args.script])
        if frames_dir:
            print(f"  {runner._frame_n} frames saved to {frames_dir}")
        browser.close()

    httpd.shutdown()
    (out / "console.log").write_text("\n".join(runner.console), encoding="utf-8")
    rc = 0
    if runner.bad:
        rc = 1
        print("PROBLEMS:")
        for b in runner.bad[:40]:
            print("  ", b)
    if runner.failures:
        rc = 1
        print("UNREACHED STEPS:", len(runner.failures))
    print(f"{len(runner.console)} console lines, {len(runner.bad)} problems, "
          f"{len(runner.failures)} unreached steps, screenshots in {out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
