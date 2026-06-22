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
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -3)
        self.gravity = 0.2
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.color = random.choice([
            (255, 192, 72),   # Orange
            (46, 213, 115),   # Green
            (84, 160, 255),   # Blue
            (255, 107, 129),  # Pink
            (255, 234, 167),  # Yellow
        ])
        self.size = random.randint(4, 8)
        self.max_lifetime = 60

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
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class StarParticle(ParticleEffect):
    """Twinkling star particles"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.scale = 0
        self.max_scale = random.uniform(0.5, 1.5)
        self.max_lifetime = 40
        self.color = (255, 255, 0)  # Yellow

    def update(self, dt=0.016):
        super().update(dt)
        # Scale up then down
        progress = self.lifetime / self.max_lifetime
        if progress < 0.5:
            self.scale = progress * 2 * self.max_scale
        else:
            self.scale = (1 - progress) * 2 * self.max_scale

    def draw(self, surface):
        if self.is_alive() and self.scale > 0:
            size = int(self.scale * 8)
            if size > 0:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class GlowEffect:
    """Button glow effect"""
    def __init__(self, rect, intensity=0):
        self.rect = rect
        self.intensity = intensity
        self.target_intensity = 0
        self.speed = 0.15

    def update(self):
        if self.intensity < self.target_intensity:
            self.intensity = min(self.intensity + self.speed, self.target_intensity)
        elif self.intensity > self.target_intensity:
            self.intensity = max(self.intensity - self.speed, self.target_intensity)

    def set_hover(self, is_hovering):
        self.target_intensity = 255 if is_hovering else 0

    def draw(self, surface):
        if self.intensity > 0:
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            glow_rect = pygame.Rect(10, 10, self.rect.width, self.rect.height)
            
            # Draw glow with decreasing opacity
            for i in range(10, 0, -1):
                alpha = int(self.intensity * (1 - i / 10) * 0.5)
                glow_circle_surf = pygame.Surface((self.rect.width + i * 2, self.rect.height + i * 2), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_circle_surf,
                    (255, 255, 255, alpha),
                    glow_circle_surf.get_rect(),
                    border_radius=30
                )
                glow_surface.blit(glow_circle_surf, (10 - i, 10 - i))
            
            surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))


class ShakeEffect:
    """Screen shake effect"""
    def __init__(self, intensity=10, duration=10):
        self.intensity = intensity
        self.duration = duration
        self.elapsed = 0
        self.offset_x = 0
        self.offset_y = 0

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
    def __init__(self, start, end, duration=60):
        self.start = start
        self.end = end
        self.current = float(start)
        self.duration = duration
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
    def __init__(self, scale_min=0.95, scale_max=1.05, speed=0.1):
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


class ButtonScaleEffect:
    """Button press scale animation"""
    def __init__(self, duration=5):
        self.duration = duration
        self.elapsed = 0
        self.pressed = False

    def press(self):
        self.pressed = True
        self.elapsed = 0

    def update(self):
        if self.pressed and self.elapsed < self.duration:
            self.elapsed += 1
        elif self.elapsed >= self.duration:
            self.pressed = False

    def get_scale(self):
        if not self.pressed:
            return 1.0
        progress = self.elapsed / self.duration
        # Quick shrink then expand
        if progress < 0.5:
            return 1.0 - progress * 0.15
        else:
            return 0.85 + (progress - 0.5) * 0.3
