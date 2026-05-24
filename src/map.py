import pygame
from src.settings import TILE_SIZE, COLS, ROWS, WALL_COLOR_BASE, WALL_COLOR_GLOW, PELLET_COLOR, POWER_PELLET_COLOR, MAZE_ROW_OFFSET

# The classic maze structure (31 rows, 28 columns)
# '#' = Wall
# '.' = Pellet
# 'o' = Power Pellet
# ' ' = Empty space / Path
# 'G' = Ghost Gate (can be crossed by ghosts, not Pacman)
# 'H' = Ghost House interior
MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##    GG    ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## # HHHH # ##.######",
    "T     .   # HHHH #   .     T",
    "######.## # HHHH # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]



class Map:
    def __init__(self):
        self.layout = [list(row) for row in MAZE_LAYOUT]
        self.cols = COLS
        self.rows = len(MAZE_LAYOUT)
        self.height = self.rows
        
        # Static surface for rendering walls once to save processing power
        self.wall_surface = None
        
        # Initial pellet count
        self.initial_pellets = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] in ['.', 'o']:
                    self.initial_pellets += 1
        self.pellets_left = self.initial_pellets

    def reset(self):
        """Resets all pellets and layout to initial state."""
        self.layout = [list(row) for row in MAZE_LAYOUT]
        self.pellets_left = self.initial_pellets

    def is_wall(self, col, row, allow_ghost_gate=False):
        """Checks if a cell in grid coordinates is a wall."""
        # Wrap horizontal tunnels
        if col < 0 or col >= self.cols:
            return False
            
        # Outside vertical bounds
        if row < 0 or row >= self.rows:
            return True
            
        cell = self.layout[row][col]
        if cell == '#':
            return True
        if cell == '-' and not allow_ghost_gate:
            return True
        return False

    def is_ghost_house(self, col, row):
        """Checks if a tile is inside the ghost house or gate."""
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return False
        return self.layout[row][col] in ['H', '-', 'G']

    def is_tunnel(self, col, row):
        """Checks if a tile is part of the side tunnels."""
        if row + MAZE_ROW_OFFSET == 17: # Row 14 in MAZE_LAYOUT + offset 3 = Row 17
            if col < 3 or col >= self.cols - 3:
                return True
        return False

    def get_valid_directions(self, col, row, current_dir, allow_ghost_gate=False):
        """Returns a list of all valid directions from the given tile."""
        valid = []
        # Directions: (dx, dy), Name
        directions = [
            ((0, -1), "UP"),
            ((0, 1), "DOWN"),
            ((-1, 0), "LEFT"),
            ((1, 0), "RIGHT")
        ]
        
        for (dx, dy), name in directions:
            # Prevent reversing direction immediately unless necessary (standard ghost AI behavior)
            if current_dir == "UP" and name == "DOWN": continue
            if current_dir == "DOWN" and name == "UP": continue
            if current_dir == "LEFT" and name == "RIGHT": continue
            if current_dir == "RIGHT" and name == "LEFT": continue
            
            # Check target tile
            tc, tr = (col + dx) % self.cols, row + dy
            if not self.is_wall(tc, tr, allow_ghost_gate):
                # Standard arcade ghost restriction: cannot turn UP at certain intersections near the ghost house
                if name == "UP" and not allow_ghost_gate:
                    # Specific traditional restrictions can go here if needed
                    pass
                valid.append(name)
                
        # Fallback in case ghost gets stuck: allow reversing
        if not valid:
            opp = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            valid.append(opp.get(current_dir, "UP"))
            
        return valid

    def eat_pellet(self, col, row):
        """Attempts to eat a pellet at a tile. Returns score increase and pellet type."""
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return 0, None
            
        cell = self.layout[row][col]
        if cell == '.':
            self.layout[row][col] = ' '
            self.pellets_left -= 1
            return 10, "pellet"
        elif cell == 'o':
            self.layout[row][col] = ' '
            self.pellets_left -= 1
            return 50, "power_pellet"
        return 0, None

    def pre_render_walls(self, screen):
        """Pre-renders walls on a static surface to save CPU load."""
        width = self.cols * TILE_SIZE
        height = self.rows * TILE_SIZE
        self.wall_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.wall_surface.fill((0, 0, 0, 0))  # Transparent background
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == '#':
                    # Draw neon glowing boxes / lines
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE
                    
                    # Compute borders by checking neighbors
                    up = r > 0 and self.layout[r-1][c] == '#'
                    down = r < self.rows - 1 and self.layout[r+1][c] == '#'
                    left = c > 0 and self.layout[r][c-1] == '#'
                    right = c < self.cols - 1 and self.layout[r][c+1] == '#'
                    
                    # Neon Double-Line Draw:
                    # 1. Base glowing blue block or thicker lines
                    base_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    
                    # Fill walls slightly to avoid empty black patches, giving solid grid feel
                    pygame.draw.rect(self.wall_surface, (5, 5, 20), base_rect)
                    
                    # Draw outer thick outline
                    if not up:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_BASE, (x, y + 2), (x + TILE_SIZE, y + 2), 4)
                    if not down:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_BASE, (x, y + TILE_SIZE - 2), (x + TILE_SIZE, y + TILE_SIZE - 2), 4)
                    if not left:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_BASE, (x + 2, y), (x + 2, y + TILE_SIZE), 4)
                    if not right:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_BASE, (x + TILE_SIZE - 2, y), (x + TILE_SIZE - 2, y + TILE_SIZE), 4)
                        
                    # 2. Add electric cyan glowing highlights inside the border to simulate neon lights
                    glow_offset = 2
                    if not up:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_GLOW, (x, y + glow_offset), (x + TILE_SIZE, y + glow_offset), 1)
                    if not down:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_GLOW, (x, y + TILE_SIZE - glow_offset), (x + TILE_SIZE, y + TILE_SIZE - glow_offset), 1)
                    if not left:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_GLOW, (x + glow_offset, y), (x + glow_offset, y + TILE_SIZE), 1)
                    if not right:
                        pygame.draw.line(self.wall_surface, WALL_COLOR_GLOW, (x + TILE_SIZE - glow_offset, y), (x + TILE_SIZE - glow_offset, y + TILE_SIZE), 1)
                        
                elif self.layout[r][c] == '-':
                    # Ghost gate / barrier
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE
                    # Draw a glowing pink barrier
                    pygame.draw.line(self.wall_surface, (255, 105, 180), (x, y + TILE_SIZE//2), (x + TILE_SIZE, y + TILE_SIZE//2), 4)
                    pygame.draw.line(self.wall_surface, (255, 200, 220), (x, y + TILE_SIZE//2), (x + TILE_SIZE, y + TILE_SIZE//2), 1)

    def draw(self, surface):
        """Draws pre-rendered walls and dynamic pellets onto the provided surface."""
        # Draw pre-rendered walls
        if self.wall_surface is None:
            self.pre_render_walls(surface)
            
        surface.blit(self.wall_surface, (0, MAZE_ROW_OFFSET * TILE_SIZE))
        
        # Draw active pellets
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.layout[r][c]
                px = c * TILE_SIZE + TILE_SIZE // 2
                py = (r + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2
                
                if cell == '.':
                    # Standard pellet: a small round circle
                    pygame.draw.circle(surface, PELLET_COLOR, (px, py), 3)
                elif cell == 'o':
                    # Power Pellet: a pulsing large orange circle
                    # Pulse is driven by game ticks (done inside main, but let's draw standard for now)
                    pulse_radius = 6
                    pygame.draw.circle(surface, POWER_PELLET_COLOR, (px, py), pulse_radius)
                    # Outer glow ring
                    pygame.draw.circle(surface, (255, 200, 0), (px, py), pulse_radius + 2, 1)
