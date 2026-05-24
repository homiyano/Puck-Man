import os

# Grid and Screen dimensions
TILE_SIZE = 24  # Size of each grid square in pixels
COLS = 28
ROWS = 36
MAZE_ROW_OFFSET = 3  # Maze is shifted down by 3 tiles to make space for top UI
SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE
FPS = 60


# Colors (Vibrant Neon-Modern Palette)
BG_COLOR = (10, 10, 18)            # Deep velvet midnight black
WALL_COLOR_BASE = (0, 45, 115)     # Darker neon blue base
WALL_COLOR_GLOW = (0, 191, 255)    # Electric cyan glow highlight
PELLET_COLOR = (255, 191, 150)     # Warm glowing soft peach
POWER_PELLET_COLOR = (255, 120, 0) # Intense orange-red
TEXT_COLOR = (240, 240, 250)       # Soft off-white
SCORE_COLOR = (255, 215, 0)        # Bright gold
READY_COLOR = (255, 238, 0)        # Pulsing bright yellow

# Pacman Colors
PACMAN_COLOR = (255, 238, 0)

# Ghost Colors
GHOST_COLORS = {
    "Blinky": (255, 20, 50),     # Hot Crimson
    "Pinky": (255, 105, 180),    # Neon Pink
    "Inky": (0, 240, 240),       # Electric Cyan
    "Clyde": (255, 150, 0),      # Vivid Orange
    "Frightened": (30, 80, 255), # Deep Electric Blue
    "Frightened_Flash": (255, 255, 255), # Flash White
    "Eaten": (140, 160, 200)     # Dull Steel Blue for Eyes
}

# Speeds (pixels per frame, adjusted for 60fps and smooth movement)
# Grid-based movement will use smooth tile interpolation
PACMAN_SPEED = 2.8      # Base speed (in pixels per frame)
GHOST_SPEED = 2.5       # Base ghost speed
GHOST_FRIGHTENED_SPEED = 1.3
GHOST_EATEN_SPEED = 6.0  # High speed for eyes returning to base

# Game Timings (in seconds)
FRIGHTENED_DURATION = 7.0
FLASH_START_TIME = 2.0   # Start flashing 2 seconds before frightened mode ends
SCATTER_DURATION = 7.0
CHASE_DURATION = 20.0

# Sound Toggle
SOUND_ENABLED = True

# High score persistence file
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "highscore.txt")
