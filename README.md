# ⚡ Neon Puc-Man (Retro-Modern Python Edition) ⚡

A premium, high-fidelity Pac-Man (Pucman) clone written in Python using **Pygame** (optimized for Pygame-CE). This edition combines the classic 1980s arcade mechanics with a sleek, glowing neon-modern visual aesthetic, advanced ghost AI, and programmatic 8-bit chiptune sound synthesis.

---

## 🕹️ Features

### 1. Retro-Modern Aesthetics & Micro-Animations
* **Double-Tube Neon Walls**: Pre-rendered glowing blue maze paths with cyan highlighted glows, avoiding typical blocky/pixelated edges.
* **Liquid Movement & Turns**: Standard tile-locked linear interpolation ensures Pac-Man and the ghosts glide smoothly between junctions without glitchy corner clipping.
* **Animated Elements**: 
  * Pac-Man features smooth sine-driven "waka-waka" chomping animations.
  * Ghosts feature bobbing floating animations and animated eyes that look in their direction of movement.
* **Satisfying Visual Feedback**:
  * **Eating sparkles**: Floating glowing particles spawn when Pac-Man eats pellets.
  * **Screen Shake**: High-impact rumble displacement when Pac-Man is caught.
  * **Hit Freeze**: Instant 20-frame freeze-frame lag when Pac-Man eats a ghost, creating an arcade "crunch" effect.
  * **Score Popups**: Floating score values (`+200`, `+400`, etc.) float upwards and fade on eat.

### 2. Programmatic 8-Bit Synthesizer
The game programmatically generates classic 8-bit sound effects at runtime using standard sound-wave algorithms! **No external `.wav` or `.mp3` assets are required**, making the game completely self-contained.
* Alternating chewing chomp sounds (`waka1`, `waka2`).
* Rhythmic alert tones for frightened ghosts.
* High-pitch upward slide for eating ghosts.
* Bubbling descending arpeggio for death.
* Built-in dynamic opening arcade startup melody and clear level fanfare!

### 3. Faithful Ghost AI Profiles
Ghosts follow exact, classic pathfinding rules at junctions (choosing the tile closest to their current target, without turning backwards).
* **🔴 Blinky (Red)**: The direct shadow. Directly tracks Pac-Man's exact tile.
* **💗 Pinky (Pink)**: The ambusher. Targets 4 tiles ahead of Pac-Man's direction (including replicating the original UP-direction offset bug!).
* **🔷 Inky (Cyan)**: The tactician. Uses a doubled offset vector drawn from Blinky to Pac-Man's front tiles, making his movements unpredictable.
* **🍊 Clyde (Orange)**: The coward. Direct-tracks Pac-Man when far away (> 8 tiles), but flees to his home corner when Pac-Man approaches.

---

## ⌨️ Controls

* **Steer Pac-Man**: `Arrow Keys` or `W, A, S, D` keys.
* **Pause / Resume**: `P` key.
* **Toggle Audio**: `M` key (toggles mute).
* **Return to Menu / Quit**: `Escape` key.

---

## 🚀 How to Run

For the absolute easiest setup, a launcher script `run.sh` is provided. Open your terminal, navigate to the game directory, and run:

```bash
chmod +x run.sh
./run.sh
```

### Manual Installation & Run:
If you prefer to run it manually step-by-step:

1. **Navigate** to the game folder:
   ```bash
   cd "/Users/homi/Documents/Vibe coding/pacman"
   ```
2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   ```
3. **Activate it**:
   ```bash
   source .venv/bin/activate
   ```
4. **Install Pygame**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Launch the game**:
   ```bash
   python -m src.main
   ```

Enjoy playing Neon Puc-Man! 🎮
