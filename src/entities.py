import pygame
import math
from src.settings import TILE_SIZE, COLS, ROWS, PACMAN_SPEED, PACMAN_COLOR, MAZE_ROW_OFFSET

class BaseEntity:
    def __init__(self, col, row, speed):
        self.col = col
        self.row = row
        self.target_col = col
        self.target_row = row
        self.progress = 0.0
        self.speed = speed
        self.direction = "LEFT"
        self.next_direction = None
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = (row + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2
        self.is_moving = False

    def update_position(self, game_map):
        """Standard grid-based smooth movement logic with tile interpolation."""
        if not self.is_moving:
            return

        # Increment progress based on speed
        # Progress ranges from 0.0 (current tile) to 1.0 (target tile)
        progress_inc = self.speed / TILE_SIZE
        self.progress += progress_inc

        # Wrap tunnels interpolation calculations
        # Check if wrapping from right (COLS-1) to left (0)
        is_wrap_right = (self.col == COLS - 1 and self.target_col == 0)
        # Check if wrapping from left (0) to right (COLS-1)
        is_wrap_left = (self.col == 0 and self.target_col == COLS - 1)

        if self.progress >= 1.0:
            # Snap to target tile
            self.col = self.target_col
            self.row = self.target_row
            self.progress = 0.0
            self.is_moving = False
            self.on_reach_target(game_map)
        else:
            # Smooth position interpolation
            r_offset = MAZE_ROW_OFFSET
            if is_wrap_right:
                # Interpolate off screen to the right, then wrap
                current_x = self.col * TILE_SIZE + TILE_SIZE // 2
                target_x = COLS * TILE_SIZE + TILE_SIZE // 2
                self.x = current_x + (target_x - current_x) * self.progress
                # Wrap visual coordinates if halfway through
                if self.x > COLS * TILE_SIZE:
                    self.x -= COLS * TILE_SIZE
                self.y = (self.row + r_offset) * TILE_SIZE + TILE_SIZE // 2
            elif is_wrap_left:
                # Interpolate off screen to the left, then wrap
                current_x = self.col * TILE_SIZE + TILE_SIZE // 2
                target_x = -1 * TILE_SIZE + TILE_SIZE // 2
                self.x = current_x + (target_x - current_x) * self.progress
                # Wrap visual coordinates if halfway through
                if self.x < 0:
                    self.x += COLS * TILE_SIZE
                self.y = (self.row + r_offset) * TILE_SIZE + TILE_SIZE // 2
            else:
                # Standard smooth linear interpolation (lerp)
                c_x = self.col * TILE_SIZE + TILE_SIZE // 2
                t_x = self.target_col * TILE_SIZE + TILE_SIZE // 2
                c_y = (self.row + r_offset) * TILE_SIZE + TILE_SIZE // 2
                t_y = (self.target_row + r_offset) * TILE_SIZE + TILE_SIZE // 2
                
                self.x = c_x + (t_x - c_x) * self.progress
                self.y = c_y + (t_y - c_y) * self.progress

    def get_dir_vector(self, direction):
        """Returns the grid delta (dx, dy) for a given direction name."""
        vectors = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0)
        }
        return vectors.get(direction, (0, 0))

    def on_reach_target(self, game_map):
        """Fires when entity completes movement from col, row to target_col, target_row."""
        pass


class Pacman(BaseEntity):
    def __init__(self, col, row):
        super().__init__(col, row, PACMAN_SPEED)
        self.direction = "LEFT"
        self.next_direction = "LEFT"
        self.waka_tick = 0
        self.lives = 3
        self.is_dead = False
        self.death_timer = 0
        self.mouth_angle = 45 # current opening size

        # For alternating waka audio
        self.last_waka_sound = "waka1"

    def reset_position(self, col=14, row=23):
        """Resets Pacman coordinates for a new life or round."""
        self.col = col
        self.row = row
        self.target_col = col
        self.target_row = row
        self.progress = 0.0
        self.direction = "LEFT"
        self.next_direction = "LEFT"
        self.is_moving = False
        self.is_dead = False
        self.death_timer = 0
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = (row + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2

    def handle_input(self):
        """Checks keyboard states and buffers requested moves."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_direction = "LEFT"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_direction = "RIGHT"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_direction = "UP"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_direction = "DOWN"

    def update(self, game_map, sound_engine):
        if self.is_dead:
            self.death_timer += 1
            return

        self.handle_input()
        
        # If not moving, try to trigger movement
        if not self.is_moving:
            self.on_reach_target(game_map)

        # Move smoothly
        self.update_position(game_map)
        
        # Update waka animation ticks
        if self.is_moving:
            self.waka_tick += 1
            # Mouth swings dynamically open and closed using a sine wave
            self.mouth_angle = abs(math.sin(self.waka_tick * 0.25)) * 45
            
            # Periodically request chomp sounds when eating pellets (done in main, but siren is continuous)
        else:
            self.mouth_angle = 15 # slightly open when stationary

    def on_reach_target(self, game_map):
        """Attempts to turn in buffered direction or continue straight."""
        # 1. First attempt to turn in the buffered next direction
        dx, dy = self.get_dir_vector(self.next_direction)
        next_col = (self.col + dx) % COLS
        next_row = self.row + dy
        
        if not game_map.is_wall(next_col, next_row):
            self.direction = self.next_direction
            self.target_col = next_col
            self.target_row = next_row
            self.is_moving = True
            return

        # 2. Otherwise, attempt to continue in the current direction
        dx, dy = self.get_dir_vector(self.direction)
        next_col = (self.col + dx) % COLS
        next_row = self.row + dy
        
        if not game_map.is_wall(next_col, next_row):
            self.target_col = next_col
            self.target_row = next_row
            self.is_moving = True
        else:
            self.is_moving = False

    def draw(self, surface):
        if self.is_dead:
            # Draw death shrinking circle animation
            self._draw_death_animation(surface)
            return

        # Pacman mouth angle and rotation
        angle_offsets = {
            "RIGHT": 0,
            "UP": 90,
            "LEFT": 180,
            "DOWN": 270
        }
        base_angle = angle_offsets.get(self.direction, 0)
        
        center_x = int(self.x)
        center_y = int(self.y)
        radius = TILE_SIZE // 2 - 1
        
        # Draw a beautiful, anti-aliased solid Pacman polygon
        # If mouth is closed (0 deg), draw full circle
        if self.mouth_angle < 3:
            pygame.draw.circle(surface, PACMAN_COLOR, (center_x, center_y), radius)
        else:
            # Build list of points for Pacman wedge
            points = [(center_x, center_y)]
            # We draw a fan of points spanning the non-mouth section
            start_deg = base_angle + self.mouth_angle
            end_deg = base_angle + 360 - self.mouth_angle
            
            # Step in degrees to draw smooth arc
            step = 10
            for deg in range(int(start_deg), int(end_deg) + step, step):
                # Clamp end point
                if deg > end_deg:
                    deg = end_deg
                rad = math.radians(deg)
                px = center_x + math.cos(rad) * radius
                py = center_y - math.sin(rad) * radius  # Subtracted since pygame Y is down
                points.append((px, py))
                
            points.append((center_x, center_y))
            
            # Avoid crash if there are too few points
            if len(points) >= 3:
                pygame.draw.polygon(surface, PACMAN_COLOR, points)
            else:
                pygame.draw.circle(surface, PACMAN_COLOR, (center_x, center_y), radius)

    def _draw_death_animation(self, surface):
        """Draws the 12-frame classic animation where Pacman opens wide and collapses."""
        center_x = int(self.x)
        center_y = int(self.y)
        radius = TILE_SIZE // 2 - 1
        
        # Death animation lasts about 45 frames (0.75 seconds)
        # First 10 frames: hold. Then collapse.
        progress = max(0, self.death_timer - 10) / 35.0
        if progress >= 1.0:
            return  # Completely disappeared
            
        # Mouth opening grows from normal to a full 180 degrees (straight line) and radius shrinks
        max_mouth = 45 + progress * 135
        curr_radius = max(1, radius * (1.0 - progress))
        
        angle_offsets = {"RIGHT": 0, "UP": 90, "LEFT": 180, "DOWN": 270}
        base_angle = angle_offsets.get(self.direction, 0)
        
        # Draw the collapsing wedge
        points = [(center_x, center_y)]
        start_deg = base_angle + max_mouth
        end_deg = base_angle + 360 - max_mouth
        
        step = 12
        for deg in range(int(start_deg), int(end_deg) + step, step):
            if deg > end_deg:
                deg = end_deg
            rad = math.radians(deg)
            px = center_x + math.cos(rad) * curr_radius
            py = center_y - math.sin(rad) * curr_radius
            points.append((px, py))
            
        points.append((center_x, center_y))
        
        if len(points) >= 3 and curr_radius > 1:
            pygame.draw.polygon(surface, PACMAN_COLOR, points)
