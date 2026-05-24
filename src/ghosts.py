import pygame
import math
import random
from src.settings import TILE_SIZE, COLS, ROWS, GHOST_SPEED, GHOST_FRIGHTENED_SPEED, GHOST_EATEN_SPEED, GHOST_COLORS, MAZE_ROW_OFFSET

class Ghost(pygame.sprite.Sprite):
    def __init__(self, name, start_col, start_row, scatter_col, scatter_row):
        super().__init__()
        self.name = name
        self.start_col = start_col
        self.start_row = start_row
        
        self.col = start_col
        self.row = start_row
        self.target_col = start_col
        self.target_row = start_row
        self.progress = 0.0
        
        self.scatter_col = scatter_col
        self.scatter_row = scatter_row
        
        self.direction = "UP"
        self.next_direction = "UP"
        
        self.speed = GHOST_SPEED
        self.state = "SCATTER"  # SCATTER, CHASE, FRIGHTENED, EATEN, HOUSE
        
        self.base_color = GHOST_COLORS[name]
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = (start_row + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2
        self.is_moving = False
        
        # Ghost house containment rules
        self.in_house = True
        self.house_exit_timer = 0
        
        # Bobbing floating effect
        self.float_tick = random.randint(0, 100)

    def reset_position(self):
        self.col = self.start_col
        self.row = self.start_row
        self.target_col = self.start_col
        self.target_row = self.start_row
        self.progress = 0.0
        self.direction = "UP"
        self.speed = GHOST_SPEED
        self.state = "SCATTER"
        self.in_house = True
        self.is_moving = False
        self.x = self.start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = (self.start_row + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2

    def update_position(self, game_map, pacman=None, blinky_pos=None):
        """Standard grid-based smooth movement logic with tile interpolation."""
        if not self.is_moving:
            return

        # Adjust progress speed based on current state
        if self.state == "FRIGHTENED":
            self.speed = GHOST_FRIGHTENED_SPEED
        elif self.state == "EATEN":
            self.speed = GHOST_EATEN_SPEED
        else:
            self.speed = GHOST_SPEED

        # Progress increment
        progress_inc = self.speed / TILE_SIZE
        self.progress += progress_inc

        # Wrapping logic check
        is_wrap_right = (self.col == COLS - 1 and self.target_col == 0)
        is_wrap_left = (self.col == 0 and self.target_col == COLS - 1)

        if self.progress >= 1.0:
            self.col = self.target_col
            self.row = self.target_row
            self.progress = 0.0
            self.is_moving = False
            self.on_reach_target(game_map, pacman, blinky_pos)
        else:
            r_offset = MAZE_ROW_OFFSET
            if is_wrap_right:
                current_x = self.col * TILE_SIZE + TILE_SIZE // 2
                target_x = COLS * TILE_SIZE + TILE_SIZE // 2
                self.x = current_x + (target_x - current_x) * self.progress
                if self.x > COLS * TILE_SIZE:
                    self.x -= COLS * TILE_SIZE
                self.y = (self.row + r_offset) * TILE_SIZE + TILE_SIZE // 2
            elif is_wrap_left:
                current_x = self.col * TILE_SIZE + TILE_SIZE // 2
                target_x = -1 * TILE_SIZE + TILE_SIZE // 2
                self.x = current_x + (target_x - current_x) * self.progress
                if self.x < 0:
                    self.x += COLS * TILE_SIZE
                self.y = (self.row + r_offset) * TILE_SIZE + TILE_SIZE // 2
            else:
                c_x = self.col * TILE_SIZE + TILE_SIZE // 2
                t_x = self.target_col * TILE_SIZE + TILE_SIZE // 2
                c_y = (self.row + r_offset) * TILE_SIZE + TILE_SIZE // 2
                t_y = (self.target_row + r_offset) * TILE_SIZE + TILE_SIZE // 2
                
                self.x = c_x + (t_x - c_x) * self.progress
                self.y = c_y + (t_y - c_y) * self.progress

    def get_dir_vector(self, direction):
        vectors = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        return vectors.get(direction, (0, 0))

    def update(self, game_map, pacman, blinky_pos, frightened_timer):
        """Update loop called each frame."""
        self.float_tick += 1

        # Frightened state check
        if frightened_timer > 0 and self.state not in ["EATEN", "HOUSE"]:
            self.state = "FRIGHTENED"
        elif frightened_timer <= 0 and self.state == "FRIGHTENED":
            # Return to normal (chase or scatter - main will coordinate, but scatter is safe default)
            self.state = "SCATTER"

        # House exit delay logic
        if self.in_house:
            self._handle_house_logic(game_map)
            return

        # Start moving if idle
        if not self.is_moving:
            self.on_reach_target(game_map, pacman, blinky_pos)

        # Move smoothly
        self.update_position(game_map, pacman, blinky_pos)

    def _handle_house_logic(self, game_map):
        """Gradually float ghosts out of the ghost house based on their timers."""
        exit_delays = {"Blinky": 0, "Pinky": 60, "Inky": 180, "Clyde": 300}
        self.house_exit_timer += 1
        
        # Float bobbing up and down inside the house
        bob = math.sin(self.float_tick * 0.1) * 3
        self.y = (self.row + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2 + bob
        self.x = self.col * TILE_SIZE + TILE_SIZE // 2
        
        if self.house_exit_timer >= exit_delays.get(self.name, 0):
            # Target is the gate exit tile (col 13/14, row 11)
            # Standard ghost house center: col 13/14, row 14
            # We animate the ghost rising up through the gate:
            # Shift grid position to gate exit
            self.in_house = False
            self.col = 14
            self.row = 11
            self.target_col = 14
            self.target_row = 11
            self.x = 14 * TILE_SIZE + TILE_SIZE // 2
            self.y = (11 + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2
            self.direction = "LEFT"
            self.progress = 0.0

    def on_reach_target(self, game_map, pacman=None, blinky_pos=None):
        """At each grid tile, determine path decision to reach target."""
        # 1. Determine Target Tile based on AI state
        target_col, target_row = self.get_current_target(pacman, blinky_pos)

        # 2. Check valid directions (excluding reverse)
        valid_dirs = game_map.get_valid_directions(self.col, self.row, self.direction, allow_ghost_gate=(self.state == "EATEN"))
        
        if not valid_dirs:
            # Fallback
            self.is_moving = False
            return

        # 3. Pathfinding Decision
        chosen_dir = None
        if self.state == "FRIGHTENED":
            # Frightened ghosts make random turns
            chosen_dir = random.choice(valid_dirs)
        else:
            # Standard AI: pick the valid tile that is geometrically closest to target tile
            min_dist = float('inf')
            for d in valid_dirs:
                dx, dy = self.get_dir_vector(d)
                next_c = (self.col + dx) % COLS
                next_r = self.row + dy
                
                # Calculate straight-line Euclidean distance
                dist = (next_c - target_col)**2 + (next_r - target_row)**2
                if dist < min_dist:
                    min_dist = dist
                    chosen_dir = d
                    
        # Apply move
        if chosen_dir:
            self.direction = chosen_dir
            dx, dy = self.get_dir_vector(chosen_dir)
            self.target_col = (self.col + dx) % COLS
            self.target_row = self.row + dy
            self.is_moving = True
        else:
            self.is_moving = False

    def get_current_target(self, pacman, blinky_pos):
        """Overridden by ghost subclasses. Default is scatter corner."""
        if self.state == "EATEN":
            # Eaten ghosts target the house center to respawn
            if self.col == 14 and self.row == 11:
                # Arrived back home! Revive ghost.
                self.state = "SCATTER"
                self.in_house = True
                self.house_exit_timer = 0
                return 14, 14
            return 14, 11
            
        if self.state == "SCATTER":
            return self.scatter_col, self.scatter_row
            
        # Chase state overridden in individual ghost classes
        return self.scatter_col, self.scatter_row

    def draw(self, surface, flash_white=False):
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Floating bobbing animation
        y_bob = int(math.sin(self.float_tick * 0.15) * 2)
        draw_y = center_y + y_bob
        
        radius = TILE_SIZE // 2 - 1
        
        # 1. Draw Body
        if self.state == "EATEN":
            # Draw eyes only, no body
            self._draw_eyes(surface, draw_y)
            return

        # Choose body color
        if self.state == "FRIGHTENED":
            body_color = GHOST_COLORS["Frightened_Flash"] if flash_white else GHOST_COLORS["Frightened"]
        else:
            body_color = self.base_color
            
        # Draw classic ghost body polygon: Dome top, straight sides, wavy bottom
        # Upper dome
        points = []
        # Draw semicircle for dome
        for deg in range(180, 360 + 10, 10):
            rad = math.radians(deg)
            px = center_x + math.cos(rad) * radius
            py = draw_y + math.sin(rad) * radius
            points.append((px, py))
            
        # Right wall bottom corner
        right_corner_x = center_x + radius
        right_corner_y = draw_y + radius
        points.append((right_corner_x, right_corner_y))
        
        # Bottom wavy tentacles (oscillating based on ticks)
        tentacle_phase = (self.float_tick // 4) % 2
        num_peaks = 3
        for i in range(num_peaks + 1):
            px = right_corner_x - (i * (2 * radius) / num_peaks)
            # Tentacle wave offset
            wave = 3 if (i % 2 == tentacle_phase) else 0
            py = draw_y + radius - wave
            points.append((px, py))
            
        # Left wall bottom corner
        left_corner_x = center_x - radius
        left_corner_y = draw_y + radius
        points.append((left_corner_x, left_corner_y))
        
        pygame.draw.polygon(surface, body_color, points)
        
        # 2. Draw Face details
        if self.state == "FRIGHTENED":
            # Vulnerable face: sad mouth and small orange/white eyes
            # Eye dots
            eye_color = (255, 184, 151) if not flash_white else (255, 50, 50)
            pygame.draw.circle(surface, eye_color, (center_x - 3, draw_y - 2), 2)
            pygame.draw.circle(surface, eye_color, (center_x + 3, draw_y - 2), 2)
            
            # Wavy sad mouth
            mouth_rect = pygame.Rect(center_x - 5, draw_y + 3, 10, 3)
            # Quick draw squiggle
            pygame.draw.line(surface, eye_color, (center_x - 5, draw_y + 4), (center_x - 3, draw_y + 2), 1)
            pygame.draw.line(surface, eye_color, (center_x - 3, draw_y + 2), (center_x - 1, draw_y + 4), 1)
            pygame.draw.line(surface, eye_color, (center_x - 1, draw_y + 4), (center_x + 1, draw_y + 2), 1)
            pygame.draw.line(surface, eye_color, (center_x + 1, draw_y + 2), (center_x + 3, draw_y + 4), 1)
            pygame.draw.line(surface, eye_color, (center_x + 3, draw_y + 4), (center_x + 5, draw_y + 2), 1)
        else:
            self._draw_eyes(surface, draw_y)

    def _draw_eyes(self, surface, draw_y):
        """Draws ghost eyes looking in their travel direction."""
        center_x = int(self.x)
        
        # Eye sclera offsets depending on travel direction
        eye_offsets = {
            "UP": (0, -2),
            "DOWN": (0, 2),
            "LEFT": (-2, 0),
            "RIGHT": (2, 0)
        }
        dx, dy = eye_offsets.get(self.direction, (0, 0))
        
        # White scleras (oval-like circles)
        eye_left_x, eye_left_y = center_x - 4 + dx//2, draw_y - 2 + dy//2
        eye_right_x, eye_right_y = center_x + 4 + dx//2, draw_y - 2 + dy//2
        
        pygame.draw.circle(surface, (255, 255, 255), (eye_left_x, eye_left_y), 3.5)
        pygame.draw.circle(surface, (255, 255, 255), (eye_right_x, eye_right_y), 3.5)
        
        # Blue pupils
        pupil_color = (10, 40, 220)
        pygame.draw.circle(surface, pupil_color, (eye_left_x + dx, eye_left_y + dy), 1.5)
        pygame.draw.circle(surface, pupil_color, (eye_right_x + dx, eye_right_y + dy), 1.5)


# ------------------ GHOST SUBCLASSES ------------------

class Blinky(Ghost):
    def __init__(self, start_col=13, start_row=11):
        # Blinky spawns directly outside the ghost house
        super().__init__("Blinky", start_col, start_row, COLS - 1, -2)
        # Blinky is already active
        self.in_house = False
        self.direction = "LEFT"

    def get_current_target(self, pacman, blinky_pos):
        if self.state == "EATEN":
            return super().get_current_target(pacman, blinky_pos)
            
        if self.state == "SCATTER":
            return self.scatter_col, self.scatter_row
            
        # Blinky directly targets Pacman
        return pacman.col, pacman.row


class Pinky(Ghost):
    def __init__(self, start_col=13, start_row=14):
        super().__init__("Pinky", start_col, start_row, 0, -2)

    def get_current_target(self, pacman, blinky_pos):
        if self.state == "EATEN":
            return super().get_current_target(pacman, blinky_pos)
            
        if self.state == "SCATTER":
            return self.scatter_col, self.scatter_row
            
        # Pinky targets 4 tiles ahead of Pacman's current direction
        dx, dy = self.get_dir_vector(pacman.direction)
        target_col = (pacman.col + 4 * dx) % COLS
        target_row = pacman.row + 4 * dy
        
        # Recreate classic UP-direction offset bug if Pacman is moving UP
        if pacman.direction == "UP":
            target_col = (target_col - 4) % COLS
            
        return target_col, target_row


class Inky(Ghost):
    def __init__(self, start_col=11, start_row=14):
        super().__init__("Inky", start_col, start_row, COLS - 1, ROWS + 1)

    def get_current_target(self, pacman, blinky_pos):
        if self.state == "EATEN":
            return super().get_current_target(pacman, blinky_pos)
            
        if self.state == "SCATTER":
            return self.scatter_col, self.scatter_row
            
        # Inky's target uses a vector from Blinky to Pacman offset tile
        # 1. Tile 2 spaces in front of Pacman
        dx, dy = self.get_dir_vector(pacman.direction)
        pac_offset_col = (pacman.col + 2 * dx) % COLS
        pac_offset_row = pacman.row + 2 * dy
        if pacman.direction == "UP":
            pac_offset_col = (pac_offset_col - 2) % COLS
            
        # 2. Vector from Blinky to Pac_offset
        vector_col = pac_offset_col - blinky_pos[0]
        vector_row = pac_offset_row - blinky_pos[1]
        
        # 3. Double the vector and add to Blinky's position
        target_col = (blinky_pos[0] + 2 * vector_col) % COLS
        target_row = blinky_pos[1] + 2 * vector_row
        
        return target_col, target_row


class Clyde(Ghost):
    def __init__(self, start_col=15, start_row=14):
        super().__init__("Clyde", start_col, start_row, 0, ROWS + 1)

    def get_current_target(self, pacman, blinky_pos):
        if self.state == "EATEN":
            return super().get_current_target(pacman, blinky_pos)
            
        if self.state == "SCATTER":
            return self.scatter_col, self.scatter_row
            
        # Calculate straight tile-distance to Pacman
        dist_sq = (self.col - pacman.col)**2 + (self.row - pacman.row)**2
        
        # 8 tiles distance squared = 64
        if dist_sq > 64:
            # Clyde targets Pacman directly when far away
            return pacman.col, pacman.row
        else:
            # Clyde runs to scatter corner when too close
            return self.scatter_col, self.scatter_row
