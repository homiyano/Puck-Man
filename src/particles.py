import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Random directions and velocities
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1.0, 4.0)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        
        self.size = random.uniform(2.0, 4.0)
        self.alpha = 255
        self.decay = random.uniform(5.0, 10.0) # Opacity decay per frame
        self.gravity = 0.05

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Add a tiny bit of gravity drop
        self.vx *= 0.98          # Slight air resistance
        self.alpha = max(0, self.alpha - self.decay)
        self.size = max(0.5, self.size - 0.05)

    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Draw anti-aliased alpha circle
        s = pygame.Surface((self.size * 2 + 2, self.size * 2 + 2), pygame.SRCALPHA)
        # Apply glowing white centers to particles
        glow_color = (
            min(255, self.color[0] + 50),
            min(255, self.color[1] + 50),
            min(255, self.color[2] + 50),
            int(self.alpha)
        )
        pygame.draw.circle(s, glow_color, (int(self.size + 1), int(self.size + 1)), self.size)
        surface.blit(s, (int(self.x - self.size - 1), int(self.y - self.size - 1)))


class FloatingText:
    def __init__(self, x, y, text, color, font_size=16):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.font_size = font_size
        self.vy = -1.2 # Slow rise
        self.life = 45 # Frames to live

    def update(self):
        self.y += self.vy
        self.life -= 1
        self.alpha = max(0, int((self.life / 45.0) * 255))

    def draw(self, surface, font):
        if self.alpha <= 0 or self.life <= 0:
            return
            
        text_surf = font.render(self.text, True, self.color)
        
        # Apply alpha blending
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, self.alpha))
        alpha_surf.blit(text_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Center horizontally
        draw_x = self.x - text_surf.get_width() // 2
        draw_y = self.y - text_surf.get_height() // 2
        
        surface.blit(alpha_surf, (draw_x, draw_y))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        
        # Screen shake parameters
        self.shake_intensity = 0
        self.shake_duration = 0

    def trigger_shake(self, intensity=8, duration=15):
        """Triggers a mechanical camera shake effect."""
        self.shake_intensity = intensity
        self.shake_duration = duration

    def get_shake_offset(self):
        """Returns the current screen offset displacement."""
        if self.shake_duration > 0:
            self.shake_duration -= 1
            dx = random.randint(-self.shake_intensity, self.shake_intensity)
            dy = random.randint(-self.shake_intensity, self.shake_intensity)
            # Dampen intensity gradually
            if self.shake_duration == 0:
                self.shake_intensity = 0
            return dx, dy
        return 0, 0

    def create_eating_burst(self, x, y, color):
        """Burst of particles when eating a pellet."""
        for _ in range(5):
            self.particles.append(Particle(x, y, color))

    def create_death_burst(self, x, y, color):
        """Massive explosion when Pacman dies."""
        for _ in range(25):
            p = Particle(x, y, color)
            p.speed = random.uniform(2.0, 7.0)
            p.vx = math.cos(p.angle) * p.speed
            p.vy = math.sin(p.angle) * p.speed
            p.decay = random.uniform(2.0, 5.0)
            self.particles.append(p)

    def create_ghost_burst(self, x, y, color):
        """Visual burst when a ghost is eaten."""
        for _ in range(15):
            p = Particle(x, y, color)
            p.speed = random.uniform(1.5, 5.0)
            p.vx = math.cos(p.angle) * p.speed
            p.vy = math.sin(p.angle) * p.speed
            self.particles.append(p)

    def add_floating_text(self, x, y, text, color, font_size=16):
        """Spawns fading floating score indicators."""
        self.floating_texts.append(FloatingText(x, y, text, color, font_size))

    def update(self):
        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0:
                self.particles.remove(p)
                
        # Update texts
        for ft in self.floating_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.floating_texts.remove(ft)

    def draw(self, surface, font):
        # Draw particles
        for p in self.particles:
            p.draw(surface)
            
        # Draw texts
        for ft in self.floating_texts:
            ft.draw(surface, font)
            
    def clear(self):
        """Clears all particles and texts."""
        self.particles.clear()
        self.floating_texts.clear()
        self.shake_duration = 0
        self.shake_intensity = 0
