import pygame
import math
import random


class ParticleEffect:
    """Base class for particle effects"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.lifetime = 0
        self.max_lifetime = 0

    def update(self, dt=0.016):
        self.lifetime += 1

    def draw(self, surface):
        pass

    def is_alive(self):
        return self.alive and self.lifetime < self.max_lifetime


class ConfettiParticle(ParticleEffect):
    """Confetti animation particles"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-12, -4)
        self.gravity = 0.25
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.color = random.choice([
            (255, 192, 72),   # Orange
            (46, 213, 115),   # Green
            (84, 160, 255),   # Blue
            (255, 107, 129),  # Pink
            (255, 234, 167),  # Yellow
        ])
        self.size = random.randint(5, 10)
        self.max_lifetime = 90

    def update(self, dt=0.016):
        super().update(dt)
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
        if self.y > 700:  # Off screen
            self.alive = False

    def draw(self, surface):
        if self.is_alive():
            # Draw as a small rectangle or circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class StarParticle(ParticleEffect):
    """Twinkling star particles"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.scale = 0
        self.max_scale = random.uniform(0.6, 1.4)
        self.max_lifetime = 50
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, 1)
        self.color = (255, 234, 0)  # Yellow star

    def update(self, dt=0.016):
        super().update(dt)
        self.x += self.vx
        self.y += self.vy
        # Scale up then down
        progress = self.lifetime / self.max_lifetime
        if progress < 0.3:
            self.scale = (progress / 0.3) * self.max_scale
        else:
            self.scale = ((1 - progress) / 0.7) * self.max_scale

    def draw(self, surface):
        if self.is_alive() and self.scale > 0:
            size = int(self.scale * 12)
            if size > 0:
                # Draw a simple star shape (cross + circle)
                px, py = int(self.x), int(self.y)
                pygame.draw.circle(surface, self.color, (px, py), size // 2)
                pygame.draw.line(surface, self.color, (px - size, py), (px + size, py), 2)
                pygame.draw.line(surface, self.color, (px, py - size), (px, py + size), 2)


class GlowEffect:
    """Button glow effect"""
    def __init__(self, rect, intensity=0):
        self.rect = rect
        self.intensity = intensity
        self.target_intensity = 0
        self.speed = 20  # Fast transition

    def update(self):
        if self.intensity < self.target_intensity:
            self.intensity = min(self.intensity + self.speed, self.target_intensity)
        elif self.intensity > self.target_intensity:
            self.intensity = max(self.intensity - self.speed, self.target_intensity)

    def set_hover(self, is_hovering):
        self.target_intensity = 180 if is_hovering else 0

    def draw(self, surface, color=(255, 255, 255)):
        if self.intensity > 0:
            glow_surf = pygame.Surface((self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA)
            # Draw layers of smooth transparent rounded rectangles for blur effect
            for i in range(8, 0, -1):
                alpha = int(self.intensity * (1 - i / 9) * 0.3)
                layer_rect = pygame.Rect(8 - i, 8 - i, self.rect.width + i * 2, self.rect.height + i * 2)
                pygame.draw.rect(glow_surf, color + (alpha,), layer_rect, border_radius=30)
            surface.blit(glow_surf, (self.rect.x - 8, self.rect.y - 8))


class ShakeEffect:
    """Screen shake effect"""
    def __init__(self, intensity=8, duration=15):
        self.intensity = intensity
        self.duration = duration
        self.elapsed = duration  # Start inactive
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self):
        self.elapsed = 0

    def update(self):
        if self.elapsed < self.duration:
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
            self.elapsed += 1
        else:
            self.offset_x = 0
            self.offset_y = 0

    def is_active(self):
        return self.elapsed < self.duration


class AnimatedCounter:
    """Animates counting from one number to another"""
    def __init__(self, start, end, duration=30):
        self.start = start
        self.end = end
        self.current = float(start)
        self.duration = duration
        self.elapsed = 0

    def reset(self, start, end):
        self.start = start
        self.end = end
        self.current = float(start)
        self.elapsed = 0

    def update(self):
        if self.elapsed < self.duration:
            progress = self.elapsed / self.duration
            # Ease-out cubic for smooth animation
            progress = 1 - (1 - progress) ** 3
            self.current = self.start + (self.end - self.start) * progress
            self.elapsed += 1
        else:
            self.current = self.end

    def get_value(self):
        return int(self.current)

    def is_animating(self):
        return self.elapsed < self.duration


class PulseEffect:
    """Pulsing/bouncing effect"""
    def __init__(self, scale_min=0.96, scale_max=1.04, speed=0.08):
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.speed = speed
        self.phase = 0

    def update(self):
        self.phase += self.speed
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi

    def get_scale(self):
        # Sine wave between min and max
        normalized = (math.sin(self.phase) + 1) / 2
        return self.scale_min + normalized * (self.scale_max - self.scale_min)
