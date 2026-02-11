# Android Deployment Guide - Retroid Pocket Classic

**Target Device:** Retroid Pocket Classic (Android 14, 1240×1080 portrait display)

---

## Critical Analysis: Current vs Target

### Current Game Configuration
```
Resolution: 1280×720 (landscape, 16:9)
Input: Keyboard (WASD, E key)
Platform: Windows/Linux/Mac desktop
```

### Target Device Specs
```
Resolution: 1240×1080 (portrait, ~1.15:1)
Input: D-pad, face buttons, touchscreen
Platform: Android 14 handheld
```

### Compatibility Assessment ✓
**Good news:** Most of the work is compatible!
- ✅ GL Compatibility renderer already set
- ✅ Input actions (ui_up, ui_down, etc.) automatically map to D-pad
- ✅ Godot 4.5 has mature Android export
- ⚠️ Resolution/orientation needs decision
- ⚠️ Input mapping needs gamepad fallback testing

---

## Screen Orientation Decision

### Option 1: Landscape with Pillarboxing (RECOMMENDED)
**What happens:** Game displays 1280×720 in landscape, black bars on sides

**Pros:**
- ✅ Zero redesign needed - use existing scenes/UI as-is
- ✅ Faster to deploy - just export settings
- ✅ Landscape feels natural for side-scrolling movement
- ✅ UI elements (dialogue, inventory) already laid out horizontally

**Cons:**
- ⚠️ Reduced play area (~720×720 effective after pillarboxing)
- ⚠️ Player must hold device sideways (not natural for vertical device)

**Implementation:**
```gdscript
# project.godot changes needed:
[display]
window/size/viewport_width=1280
window/size/viewport_height=720
window/stretch/mode="viewport"
window/stretch/aspect="keep"  # Add this - maintains aspect, adds black bars
window/handheld/orientation="landscape"  # Force landscape
```

---

### Option 2: Portrait Native (FULL REDESIGN)
**What happens:** Redesign game for 1080×1240 portrait layout

**Pros:**
- ✅ Uses full screen, no wasted space
- ✅ Natural device orientation (hold vertically)
- ✅ Higher effective resolution

**Cons:**
- ❌ Requires redesigning every scene (world, UI, levels)
- ❌ Camera system needs rework (vertical follow vs horizontal)
- ❌ All UI elements need repositioning
- ❌ 2-4 weeks additional development time
- ❌ Testing/validation all over again

**Recommendation:** **NOT WORTH IT** for a 30-minute gift game

---

### Option 3: Hybrid Pillarbox Portrait
**What happens:** Rotate game 90° clockwise, display as portrait with horizontal black bars

**Pros:**
- ✅ Device held vertically (natural)
- ✅ Minimal code changes

**Cons:**
- ⚠️ Even smaller play area (~720×540 after bars)
- ⚠️ Input feels awkward (D-pad up = game right)

**Recommendation:** Confusing for players

---

## Recommended Approach: Landscape Pillarbox

**Keep the game landscape (1280×720), force landscape orientation on Android.**

### Why This Works
1. **Retroid is gaming-focused** - Users expect to rotate for games (like emulators)
2. **D-pad positioned for landscape** - Horizontal layout is primary use case
3. **Zero redesign** - Export and test immediately
4. **Side-scrolling feels better horizontal** - Natural movement direction

---

## Deployment Methods (Best to Easiest)

### Method 1: Official APK Build (RECOMMENDED)
**What:** Export game as signed APK, install directly via USB/file manager

**Steps:**
1. Install Godot Android Export Templates
2. Configure Android build settings in Godot
3. Create debug keystore (or use Godot's default)
4. Export as APK
5. Transfer to Retroid via USB or cloud storage
6. Enable "Install from Unknown Sources" in Android settings
7. Install APK via file manager

**Pros:**
- ✅ Standalone app with icon
- ✅ Runs natively (best performance)
- ✅ No dependencies required
- ✅ Can launch from app drawer
- ✅ Proper Android lifecycle (pause/resume)

**Cons:**
- ⚠️ Requires initial setup (export templates, ~300MB download)
- ⚠️ Must sign APK (auto-handled by Godot)

**Time to Deploy:** ~1 hour setup, then 5 minutes per build

---

### Method 2: HTML5 + Browser (NOT RECOMMENDED)
**What:** Export as web game, open in Chrome/Firefox

**Pros:**
- ✅ No installation needed
- ✅ Quick iteration for testing

**Cons:**
- ❌ Slower performance (WebGL overhead)
- ❌ No fullscreen without user gesture
- ❌ Input mapping issues (browser captures some keys)
- ❌ Audio latency/permission issues
- ❌ Must stay in browser (no app icon)
- ❌ Godot 4.5 web export can be buggy

**Recommendation:** Only use for early prototyping, not final delivery

---

### Method 3: Remote Desktop/Streaming (TERRIBLE)
**What:** Stream game from PC to Android via Steam Link, Moonlight, etc.

**Cons:**
- ❌ Requires PC running constantly
- ❌ Input lag over network
- ❌ Not portable (needs Wi-Fi)
- ❌ Defeats purpose of handheld

**Recommendation:** Don't do this

---

## Recommended Implementation Plan

### Step 1: Configure Android Export (30 min)
1. Download Godot Android Export Templates (4.5 stable)
2. Open Project → Export → Add Android preset
3. Set minimum SDK to 21 (Android 5.0+)
4. Keep default debug keystore
5. Configure orientation: Landscape

### Step 2: Adjust Project Settings (10 min)
```gdscript
[display]
window/stretch/aspect="keep"  # Add black bars instead of stretching
window/handheld/orientation="landscape"  # Force landscape

[input_devices]
pointing/emulate_touch_from_mouse=true  # For desktop testing
pointing/emulate_mouse_from_touch=true  # Enable touchscreen as backup input
```

### Step 3: Test Input Mapping (15 min)
1. Add gamepad button debug overlay
2. Verify D-pad → ui_left/ui_right/ui_up/ui_down
3. Verify face buttons → ui_accept/ui_cancel/interact
4. Add fallback for touchscreen "virtual buttons" if needed

### Step 4: Build & Transfer (10 min)
1. Export → Android → Export Project (APK)
2. Copy APK to Retroid via USB or cloud
3. Install on device
4. Test on actual hardware

### Step 5: Performance Validation (30 min)
1. Check FPS (should be stable 60fps)
2. Test fade transitions (SceneManager)
3. Verify audio playback
4. Test save/load (Android file permissions)

**Total Time:** ~2 hours for first deployment

---

## Input Mapping Strategy

### Current Input Actions (from project.godot)
```
ui_left = Arrow Left, A key
ui_right = Arrow Right, D key
ui_up = Arrow Up, W key
ui_down = Arrow Down, S key
interact = E key
ui_accept = Enter, Space, E key
ui_cancel = Escape
```

### Godot Auto-Mapping (Built-in) ✓
Godot automatically maps these to gamepad:
- **D-pad directions** → ui_left/right/up/down
- **Face buttons** (typically):
  - A button → ui_accept
  - B button → ui_cancel
  - X/Y buttons → (unmapped by default)

### Recommended Additions
Add explicit gamepad mappings for clarity:

```gdscript
# Add to project.godot [input] section
interact={
"deadzone": 0.5,
"events": [
    Object(InputEventKey, ..., "keycode": 69),  # E key (existing)
    Object(InputEventJoypadButton, "button_index": JOY_BUTTON_A)  # A button
]
}
```

**Testing Plan:**
1. Connect Xbox/PlayStation controller to PC
2. Test all actions work with controller
3. If works on PC → will work on Retroid (uses SDL gamepad database)

---

## File Size Considerations

### Expected APK Size
- **Godot Engine:** ~25-35 MB (baseline)
- **Game Assets:** Current placeholder assets (~5 MB)
- **Total Estimated:** ~40-50 MB final APK

**Retroid Storage:** 64GB/128GB → plenty of room ✓

---

## Performance Expectations

### Snapdragon G1 Gen 2 Capabilities
- **CPU:** Octa-core up to 2.2 GHz
- **GPU:** Adreno (entry-level gaming)
- **Target:** 2D games, emulators up to PS1/N64

### Circe's Garden Performance
- **Rendering:** 2D sprites, simple shaders
- **Physics:** Light (few collision objects)
- **Expected FPS:** 60fps stable ✓
- **Load Times:** <2 seconds per scene ✓

**Assessment:** Should run perfectly - game is less demanding than N64 emulation

---

## Testing Checklist

### Pre-Export Testing (Desktop)
- [ ] Connect gamepad, test all inputs
- [ ] Test at 1280×720 with black bars (aspect="keep")
- [ ] Verify no hardcoded keyboard references in code
- [ ] Check touch input works for menus

### Post-Export Testing (Retroid)
- [ ] APK installs successfully
- [ ] App icon appears in launcher
- [ ] Game launches without crashes
- [ ] D-pad controls work
- [ ] Face buttons work (A=accept, B=cancel)
- [ ] Audio plays correctly
- [ ] All scenes load (main menu → world → minigames)
- [ ] Fade transitions smooth
- [ ] Game save/load works (Android permissions)
- [ ] Boat travel works
- [ ] All NPCs interactable
- [ ] Minigames playable with D-pad
- [ ] Can complete full quest chain
- [ ] Performance stable (no slowdowns)

---

## Alternative: Test Before Full Commit

### Quick Validation Strategy
1. **Export current build to APK** (don't modify anything yet)
2. **Test on Retroid as-is** (see what works/breaks)
3. **Make decisions based on real device feedback**

**Why:** Avoid premature optimization. Test actual issues vs theoretical ones.

---

## Sources
- [Godot Android Export Docs](https://docs.godotengine.org/en/4.5/tutorials/export/exporting_for_android.html)
- [Godot Controller Support](https://docs.godotengine.org/en/stable/tutorials/inputs/controllers_gamepads_joysticks.html)
- [Android Game Controllers Best Practices](https://developer.android.com/training/game-controllers/controller-input)
