import pygame
import sys
import os
import math
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR, TEXT_COLOR,
    PACMAN_SPEED, GHOST_SPEED, HIGHSCORE_FILE, TILE_SIZE, COLS, ROWS, MAZE_ROW_OFFSET
)
from src.map import Map
from src.sound import SoundEngine
from src.entities import Pacman
from src.ghosts import Blinky, Pinky, Inky, Clyde
from src.particles import ParticleSystem
from src.ui import UIManager

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Puc-Man (Retro-Modern Python)")
        self.clock = pygame.time.Clock()
        
        # Load assets/modules
        self.map = Map()
        self.sound = SoundEngine()
        self.ui = UIManager()
        self.particles = ParticleSystem()
        
        # Entities setup
        self.pacman = Pacman(14, 23)
        self.ghosts = pygame.sprite.Group()
        self.blinky = Blinky(13, 11)
        self.pinky = Pinky(13, 14)
        self.inky = Inky(11, 14)
        self.clyde = Clyde(15, 14)
        
        self.ghosts.add(self.blinky)
        self.ghosts.add(self.pinky)
        self.ghosts.add(self.inky)
        self.ghosts.add(self.clyde)
        
        # Core Game Variables
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.state = "START_SCREEN"  # START_SCREEN, READY_PROMPT, PLAYING, PAUSED, GAME_OVER, VICTORY
        
        # Power Pellet timing
        self.frightened_timer = 0
        self.ghost_eat_multiplier = 1  # 1=200, 2=400, 3=800, 4=1600
        
        # Timers and counters
        self.ready_timer = 0
        self.victory_timer = 0
        self.hit_freeze_timer = 0
        self.record_beaten = False
        self.sound_muted = False

    def load_high_score(self):
        """Loads high score from local text file."""
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    return int(f.read().strip())
            except Exception:
                return 10000 # Default arcade threshold
        return 10000

    def save_high_score(self):
        """Saves high score to local text file if current score exceeds it."""
        if self.score > self.high_score:
            self.high_score = self.score
            self.record_beaten = True
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except Exception as e:
            print(f"Error saving high score: {e}")

    def reset_game(self):
        """Prepares a completely fresh game run."""
        self.score = 0
        self.level = 1
        self.pacman.lives = 3
        self.record_beaten = False
        self.map.reset()
        self.reset_round()

    def reset_round(self):
        """Resets entity positions for a new life or round."""
        self.pacman.reset_position(14, 23)
        self.blinky.reset_position()
        self.pinky.reset_position()
        self.inky.reset_position()
        self.clyde.reset_position()
        self.frightened_timer = 0
        self.ghost_eat_multiplier = 1
        self.ready_timer = 120  # 2 seconds pre-round freeze
        self.hit_freeze_timer = 0
        self.particles.clear()
        self.sound.stop_siren()

    def run(self):
        """Main gameplay execution loop."""
        running = True
        while running:
            # Dispatch ticks and cap FPS
            dt = self.clock.tick(FPS)
            
            # 1. Event Dispatcher
            running = self.handle_events()
            if not running:
                break
                
            # 2. State Controller Logic Update
            self.update()
            
            # 3. Double-Buffer Rendering Dispatcher
            self.draw()
            
        self.save_high_score()
        self.sound.stop_all()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Processes low-level user events (keyboard clicks, window quit)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                # Toggle Mute globally
                if event.key == pygame.K_m:
                    self.sound_muted = not self.sound_muted
                    self.sound.enabled = not self.sound_muted
                    if self.sound_muted:
                        self.sound.stop_all()
                    else:
                        if self.state == "PLAYING":
                            self.sound.play("siren")
                            
                # State transitions
                if self.state == "START_SCREEN":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = "READY_PROMPT"
                        self.sound.play("intro")
                    elif event.key == pygame.K_ESCAPE:
                        return False
                        
                elif self.state == "PLAYING":
                    if event.key == pygame.K_p:
                        self.state = "PAUSED"
                        self.sound.stop_siren()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "START_SCREEN"
                        self.sound.stop_siren()
                        
                elif self.state == "PAUSED":
                    if event.key == pygame.K_p:
                        self.state = "PLAYING"
                        if self.frightened_timer <= 0:
                            self.sound.play("siren")
                    elif event.key == pygame.K_ESCAPE:
                        self.save_high_score()
                        self.state = "START_SCREEN"
                        
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = "READY_PROMPT"
                        self.sound.play("intro")
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "START_SCREEN"
                        
        return True

    def update(self):
        """Updates game state logic based on active state."""
        # Handle Hit Freeze (Arcade screen lag on eating a ghost for impact feedback)
        if self.hit_freeze_timer > 0:
            self.hit_freeze_timer -= 1
            self.particles.update() # Keep particles floating
            return

        if self.state == "READY_PROMPT":
            self.ready_timer -= 1
            if self.ready_timer <= 0:
                self.state = "PLAYING"
                self.sound.play("siren")
            # Update particles even if paused
            self.particles.update()
            
        elif self.state == "PLAYING":
            self.update_gameplay()
            
        elif self.state == "VICTORY":
            self.victory_timer -= 1
            self.particles.update()
            if self.victory_timer <= 0:
                # Move to next stage
                self.level += 1
                self.map.reset()
                self.reset_round()
                self.state = "READY_PROMPT"
                self.sound.play("intro")

    def update_gameplay(self):
        """Standard active game mechanics update."""
        # 1. Update Pacman
        self.pacman.update(self.map, self.sound)
        
        # If Pacman is dead, process death animation and holds
        if self.pacman.is_dead:
            if self.pacman.death_timer == 10:
                # Trigger massive particle explosion at death start frame
                px = self.pacman.x
                py = self.pacman.y
                self.particles.create_death_burst(px, py, PACMAN_SPEED)
                self.particles.trigger_shake(8, 25) # Heavy screen shake
            
            if self.pacman.death_timer > 55:
                # Animation finished: decrement life
                self.pacman.lives -= 1
                self.save_high_score()
                if self.pacman.lives > 0:
                    self.reset_round()
                    self.state = "READY_PROMPT"
                    self.sound.play("intro")
                else:
                    self.state = "GAME_OVER"
            self.particles.update()
            return

        # 2. Update Frightened Vulnerability Timers
        if self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer == 0:
                self.ghost_eat_multiplier = 1
                # Resume normal siren sound
                self.sound.stop_siren()
                self.sound.play("siren")

        # 3. Update Ghosts
        blinky_pos = (self.blinky.col, self.blinky.row)
        for ghost in self.ghosts:
            ghost.update(self.map, self.pacman, blinky_pos, self.frightened_timer)

        # 4. Check Collisions: Pacman vs Pellets
        self.check_pellet_collisions()

        # 5. Check Collisions: Pacman vs Ghosts
        self.check_ghost_collisions()

        # 6. Update Particle & float text effects
        self.particles.update()

    def check_pellet_collisions(self):
        """Handles Pacman eating items on map."""
        # Check current Pacman center tile
        col, row = self.pacman.col, self.pacman.row
        points, pellet_type = self.map.eat_pellet(col, row)
        
        if points > 0:
            self.score += points
            
            # Visual sparkle particles at tile center
            px = col * TILE_SIZE + TILE_SIZE // 2
            py = (row + MAZE_ROW_OFFSET) * TILE_SIZE + TILE_SIZE // 2
            self.particles.create_eating_burst(px, py, (255, 238, 0))
            
            if pellet_type == "pellet":
                # Play alternating chewing waka
                waka_sfx = "waka1" if self.pacman.last_waka_sound == "waka2" else "waka2"
                self.sound.play(waka_sfx)
                self.pacman.last_waka_sound = waka_sfx
                
            elif pellet_type == "power_pellet":
                self.sound.play("eat_power")
                self.frightened_timer = 420  # 7 seconds at 60fps
                self.ghost_eat_multiplier = 1
                # Trigger vulnerable state on ghosts immediately
                for ghost in self.ghosts:
                    if ghost.state not in ["EATEN", "HOUSE"]:
                        ghost.state = "FRIGHTENED"
                # Stop normal siren
                self.sound.stop_siren()
                
            # Score scaling check
            if self.score > self.high_score:
                self.high_score = self.score
                
            # Victory check
            if self.map.pellets_left <= 0:
                self.state = "VICTORY"
                self.victory_timer = 150  # 2.5 seconds victory freeze
                self.sound.stop_siren()
                self.sound.play("clear")

    def check_ghost_collisions(self):
        """Handles collision between Pacman and Ghosts."""
        # Standard collision radius
        collision_dist = (TILE_SIZE // 1.5) ** 2
        
        for ghost in self.ghosts:
            if ghost.state == "HOUSE":
                continue
                
            # Calculate distance squared to avoid square roots
            dist_sq = (self.pacman.x - ghost.x)**2 + (self.pacman.y - ghost.y)**2
            
            if dist_sq < collision_dist:
                if ghost.state == "FRIGHTENED":
                    # Eat Ghost!
                    ghost.state = "EATEN"
                    self.sound.play("eat_ghost")
                    
                    # Score reward details
                    pts = 200 * self.ghost_eat_multiplier
                    self.score += pts
                    self.ghost_eat_multiplier = min(8, self.ghost_eat_multiplier * 2) # max multiplier is 8 (1600 pts)
                    
                    # Pop scores on screen
                    self.particles.add_floating_text(ghost.x, ghost.y, f"+{pts}", (0, 255, 200), font_size=18)
                    
                    # Colorful burst at impact
                    self.particles.create_ghost_burst(ghost.x, ghost.y, ghost.base_color)
                    
                    # Set Hit Freeze to give high punch feedback (arcade frame lag)
                    self.hit_freeze_timer = 20
                    break
                    
                elif ghost.state in ["CHASE", "SCATTER"]:
                    # Pacman Dies!
                    self.pacman.is_dead = True
                    self.pacman.is_moving = False
                    self.sound.stop_siren()
                    self.sound.play("death")
                    break

    def draw(self):
        """Orchestrates all state drawing onto back-buffer."""
        # Master screen shake displacement offset
        offset_x, offset_y = self.particles.get_shake_offset()
        
        # Double-buffer drawing canvas
        canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        canvas.fill(BG_COLOR)
        
        # 1. State machine drawing
        if self.state == "START_SCREEN":
            self.ui.draw_start_screen(canvas, self.high_score)
        else:
            # Active board drawing
            # Map pre-rendered walls and dynamic pellets
            self.map.draw(canvas)
            
            # Pacman
            self.pacman.draw(canvas)
            
            # Ghosts
            # Flash frightened ghosts in red/white near the end of vulnerable state
            flash_white = False
            if self.frightened_timer > 0 and self.frightened_timer < 120:  # Under 2 seconds left
                flash_white = (self.frightened_timer // 8) % 2 == 0
                
            for ghost in self.ghosts:
                ghost.draw(canvas, flash_white=flash_white)
                
            # Floating particles & scores
            self.particles.draw(canvas, self.ui.normal_font)
            
            # HUD overlay
            self.ui.draw_hud(canvas, self.score, self.high_score, self.pacman.lives, self.level)
            
            # Overlay Prompts
            if self.state == "READY_PROMPT":
                self.ui.draw_ready_prompt(canvas)
            elif self.state == "PAUSED":
                self.ui.draw_pause_screen(canvas)
            elif self.state == "GAME_OVER":
                self.ui.draw_game_over(canvas, self.score, self.record_beaten)
                
        # Draw canvas onto screen with screen shake offsets applied
        self.screen.blit(canvas, (offset_x, offset_y))
        pygame.display.flip()


if __name__ == "__main__":
    game = GameController()
    game.run()
