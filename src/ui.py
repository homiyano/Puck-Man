import pygame
import math
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_COLOR, SCORE_COLOR, READY_COLOR, GHOST_COLORS, TILE_SIZE, PACMAN_COLOR, MAZE_ROW_OFFSET

class UIManager:
    def __init__(self):
        # Initialize default Pygame fonts
        pygame.font.init()
        # Fallback order of premium fonts, or standard monospace/sans
        try:
            self.title_font = pygame.font.SysFont("Courier New", 38, bold=True)
            self.large_font = pygame.font.SysFont("Courier New", 26, bold=True)
            self.normal_font = pygame.font.SysFont("Courier New", 16, bold=True)
            self.small_font = pygame.font.SysFont("Courier New", 12, bold=True)
        except Exception:
            self.title_font = pygame.font.Font(None, 48)
            self.large_font = pygame.font.Font(None, 36)
            self.normal_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)
            
        self.tick = 0
        self.intro_pacman_x = -50
        self.intro_ghosts = [
            {"name": "Blinky", "color": GHOST_COLORS["Blinky"], "offset": 40},
            {"name": "Pinky", "color": GHOST_COLORS["Pinky"], "offset": 75},
            {"name": "Inky", "color": GHOST_COLORS["Inky"], "offset": 110},
            {"name": "Clyde", "color": GHOST_COLORS["Clyde"], "offset": 145}
        ]

    def draw_hud(self, surface, score, high_score, lives, level):
        """Draws classic arcade HUD header and footer."""
        self.tick += 1
        
        # 1. Header (Scores)
        # Score Column
        score_title = self.normal_font.render("SCORE", True, TEXT_COLOR)
        score_val = self.large_font.render(f"{score:06d}", True, SCORE_COLOR)
        surface.blit(score_title, (40, 10))
        surface.blit(score_val, (40, 28))
        
        # High Score Column
        hi_title = self.normal_font.render("HIGH SCORE", True, TEXT_COLOR)
        hi_val = self.large_font.render(f"{high_score:06d}", True, SCORE_COLOR)
        surface.blit(hi_title, (SCREEN_WIDTH - hi_title.get_width() - 40, 10))
        surface.blit(hi_val, (SCREEN_WIDTH - hi_val.get_width() - 40, 28))
        
        # Level column (centered)
        level_lbl = self.normal_font.render(f"STAGE {level}", True, (0, 255, 100))
        surface.blit(level_lbl, (SCREEN_WIDTH // 2 - level_lbl.get_width() // 2, 20))
        
        # 2. Footer (Lives and Fruits status)
        footer_y = SCREEN_HEIGHT - 35
        # Draw Lives as cute mini-Pacmans
        lives_lbl = self.normal_font.render("LIVES:", True, TEXT_COLOR)
        surface.blit(lives_lbl, (20, footer_y))
        
        icon_x = 20 + lives_lbl.get_width() + 10
        for i in range(lives):
            # Draw mini solid Pacman wedge
            cx = icon_x + i * 22
            cy = footer_y + lives_lbl.get_height() // 2
            r = 8
            pygame.draw.circle(surface, PACMAN_COLOR, (cx, cy), r)
            # Bite cut-out pointing right
            points = [(cx, cy), (cx + r, cy - r//2), (cx + r, cy + r//2)]
            pygame.draw.polygon(surface, (10, 10, 18), points) # Background color overlay

        # Audio mute indicator
        audio_lbl = self.small_font.render("Press 'M' to Mute", True, (100, 100, 120))
        surface.blit(audio_lbl, (SCREEN_WIDTH - audio_lbl.get_width() - 20, footer_y + 4))

    def draw_start_screen(self, surface, high_score):
        """Arcade title dashboard with moving entities and character listings."""
        self.tick += 1
        
        # Background dark glow overlay
        surface.fill((8, 8, 14))
        
        # 1. Pulsing Game Title
        glow_val = abs(math.sin(self.tick * 0.05))
        title_glow_color = (
            int(0 + glow_val * 50),
            int(150 + glow_val * 105),
            255
        )
        title_shadow = self.title_font.render("NEON PUC-MAN", True, (0, 40, 100))
        title_text = self.title_font.render("NEON PUC-MAN", True, title_glow_color)
        surface.blit(title_shadow, (SCREEN_WIDTH//2 - title_text.get_width()//2 + 2, 62))
        surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 60))
        
        # High Score indicator
        hi_score_lbl = self.normal_font.render(f"ALL-TIME RECORD: {high_score:06d}", True, SCORE_COLOR)
        surface.blit(hi_score_lbl, (SCREEN_WIDTH//2 - hi_score_lbl.get_width()//2, 115))

        # 2. Animated Character Showcase Table (Beautiful retro card look)
        panel_rect = pygame.Rect(30, 160, SCREEN_WIDTH - 60, 390)
        pygame.draw.rect(surface, (18, 18, 30), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (0, 191, 255), panel_rect, 1, border_radius=12) # glowing cyan frame
        
        headers = ["GHOST", "CHARACTER", "AI METHOD"]
        hx_offsets = [60, 160, 310]
        for idx, header in enumerate(headers):
            h_text = self.small_font.render(header, True, (0, 191, 255))
            surface.blit(h_text, (hx_offsets[idx], 175))
        pygame.draw.line(surface, (0, 45, 115), (45, 195), (SCREEN_WIDTH - 45, 195), 1)

        # Characters data
        ghosts_showcase = [
            ("Blinky", "Shadow", "Direct Chaser", GHOST_COLORS["Blinky"]),
            ("Pinky", "Speedy", "Ambusher (4-Ahead)", GHOST_COLORS["Pinky"]),
            ("Inky", "Bashful", "Flank-Vector", GHOST_COLORS["Inky"]),
            ("Clyde", "Pokey", "Proximity Coward", GHOST_COLORS["Clyde"])
        ]
        
        for idx, (name, nickname, behaviour, color) in enumerate(ghosts_showcase):
            ry = 220 + idx * 80
            
            # Draw actual ghost sprite dynamically
            self._draw_showcase_ghost(surface, 75, ry, color)
            
            # Name and info text
            name_text = self.normal_font.render(name, True, color)
            nick_text = self.normal_font.render(f'"{nickname}"', True, color)
            beh_text = self.normal_font.render(behaviour, True, TEXT_COLOR)
            
            surface.blit(name_text, (160, ry - 18))
            surface.blit(nick_text, (160, ry + 2))
            surface.blit(beh_text, (310, ry - 8))
            
            # Subtle division line
            if idx < len(ghosts_showcase) - 1:
                pygame.draw.line(surface, (20, 20, 35), (45, ry + 38), (SCREEN_WIDTH - 45, ry + 38), 1)

        # 3. Floating Marching Intro Showcase (Pacman chasing ghosts across the bottom)
        self.intro_pacman_x += 1.8
        if self.intro_pacman_x > SCREEN_WIDTH + 200:
            self.intro_pacman_x = -200
            
        march_y = SCREEN_HEIGHT - 130
        
        # Draw marching Pacman
        px = int(self.intro_pacman_x)
        # Animated chewing
        chew = abs(math.sin(self.tick * 0.2)) * 40
        pygame.draw.circle(surface, PACMAN_COLOR, (px, march_y), 15)
        # Bite overlay
        points = [(px, march_y), (px + 16, march_y - int(chew//3)), (px + 16, march_y + int(chew//3))]
        pygame.draw.polygon(surface, (8, 8, 14), points)

        # Draw marching ghosts
        for g in self.intro_ghosts:
            gx = px - g["offset"]
            self._draw_showcase_ghost(surface, gx, march_y, g["color"], scale=1.2)

        # 4. Pulsing "PRESS SPACE"
        blink = (self.tick // 25) % 2
        if blink == 0:
            prompt = self.large_font.render("PRESS SPACE TO PLAY", True, READY_COLOR)
            surface.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 65))
        
        instructions = self.small_font.render("Use Arrow Keys/WASD to steer • 'P' to pause", True, (100, 100, 120))
        surface.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, SCREEN_HEIGHT - 35))

    def _draw_showcase_ghost(self, surface, cx, cy, color, scale=1.0):
        """Draws a beautiful standalone static ghost body for UI."""
        r = int(12 * scale)
        # Dome semicircle
        points = []
        for deg in range(180, 360 + 10, 10):
            rad = math.radians(deg)
            px = cx + math.cos(rad) * r
            py = cy + math.sin(rad) * r
            points.append((px, py))
        points.append((cx + r, cy + r))
        
        # Wavy bottom
        tentacle_phase = (self.tick // 8) % 2
        num_peaks = 3
        for i in range(num_peaks + 1):
            px = cx + r - (i * (2 * r) / num_peaks)
            wave = int(3 * scale) if (i % 2 == tentacle_phase) else 0
            py = cy + r - wave
            points.append((px, py))
        points.append((cx - r, cy + r))
        
        pygame.draw.polygon(surface, color, points)
        
        # Draw eyes looking right
        ex_l, ey_l = cx - int(4 * scale) + 1, cy - int(2 * scale)
        ex_r, ey_r = cx + int(4 * scale) + 1, cy - int(2 * scale)
        pygame.draw.circle(surface, (255, 255, 255), (ex_l, ey_l), int(3.5 * scale))
        pygame.draw.circle(surface, (255, 255, 255), (ex_r, ey_r), int(3.5 * scale))
        # Pupils
        pygame.draw.circle(surface, (10, 40, 220), (ex_l + 1, ey_l), int(1.5 * scale))
        pygame.draw.circle(surface, (10, 40, 220), (ex_r + 1, ey_r), int(1.5 * scale))

    def draw_ready_prompt(self, surface):
        """Classic pre-round READY! text."""
        txt = self.large_font.render("READY!", True, READY_COLOR)
        # Center in the gap below ghost house
        rx = SCREEN_WIDTH // 2 - txt.get_width() // 2
        ry = (19 + MAZE_ROW_OFFSET) * TILE_SIZE + 2  # Row 22 in grid coordinates
        
        # Soft dark container backplate
        plate = pygame.Rect(rx - 15, ry - 5, txt.get_width() + 30, txt.get_height() + 10)
        pygame.draw.rect(surface, (10, 10, 18), plate)
        surface.blit(txt, (rx, ry))

    def draw_pause_screen(self, surface):
        """Frosted dim overlay screen with key bindings info."""
        # Create translucent black canvas
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((5, 5, 12, 180)) # Glass dark-tint overlay
        surface.blit(dim_surf, (0, 0))
        
        box_width, box_height = 360, 240
        bx = SCREEN_WIDTH//2 - box_width//2
        by = SCREEN_HEIGHT//2 - box_height//2
        
        # Elegant panel
        pygame.draw.rect(surface, (18, 18, 30), (bx, by, box_width, box_height), border_radius=15)
        pygame.draw.rect(surface, WALL_COLOR_GLOW, (bx, by, box_width, box_height), 2, border_radius=15)
        
        title = self.large_font.render("GAME PAUSED", True, READY_COLOR)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, by + 25))
        
        # Mappings list
        controls = [
            "Arrow Keys / WASD - Move Pacman",
            "P Key             - Resume Game",
            "M Key             - Mute Audio",
            "Escape            - Return to Menu"
        ]
        
        for idx, ctrl in enumerate(controls):
            txt = self.normal_font.render(ctrl, True, TEXT_COLOR)
            surface.blit(txt, (bx + 30, by + 80 + idx * 32))

    def draw_game_over(self, surface, final_score, record_beaten):
        """Dramatic retro arcade game over overlay."""
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((5, 5, 12, 210))
        surface.blit(dim_surf, (0, 0))
        
        # Red warning block
        go_txt = self.title_font.render("GAME OVER", True, (255, 30, 60))
        surface.blit(go_txt, (SCREEN_WIDTH//2 - go_txt.get_width()//2, SCREEN_HEIGHT // 2 - 120))
        
        score_lbl = self.large_font.render(f"FINAL SCORE: {final_score:06d}", True, SCORE_COLOR)
        surface.blit(score_lbl, (SCREEN_WIDTH//2 - score_lbl.get_width()//2, SCREEN_HEIGHT // 2 - 50))
        
        if record_beaten:
            record_txt = self.large_font.render("★ NEW ALL-TIME RECORD! ★", True, (0, 255, 128))
            surface.blit(record_txt, (SCREEN_WIDTH//2 - record_txt.get_width()//2, SCREEN_HEIGHT // 2 - 10))
            
        retry_blink = (self.tick // 25) % 2
        if retry_blink == 0:
            retry_lbl = self.normal_font.render("PRESS SPACE TO TRY AGAIN", True, TEXT_COLOR)
            surface.blit(retry_lbl, (SCREEN_WIDTH//2 - retry_lbl.get_width()//2, SCREEN_HEIGHT // 2 + 70))
            
        esc_lbl = self.normal_font.render("PRESS ESC TO EXIT TO MENU", True, (120, 120, 140))
        surface.blit(esc_lbl, (SCREEN_WIDTH//2 - esc_lbl.get_width()//2, SCREEN_HEIGHT // 2 + 105))
